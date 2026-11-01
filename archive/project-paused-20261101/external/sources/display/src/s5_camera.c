/*
 * s5_camera.c —— R-07 / P3r：OV5640(双目模组 J11) 640×480 SCCB 配置 + S2MM VDMA 控制
 * 后端：S5_CAM_I2C_BACKEND = GPIO(1, 默认, 0x43C80000/08 bit-bang) | PS(0, PS I2C0)
 * 数据宽度：ov5640_ip 16b RGB565 → axis_subset_converter 16→24 → S2MM 24bpp → DDR BGR888
 *           640 宽 ⇒ stride 1920、帧 921,600 B（与阶段5 冻结 raw ABI 一致）。
 *
 * r14–r22 修复记录：
 *  - PS 后端：CR 读改写保留分频位；Fscl=Fpclk/(22*(a+1)*(b+1))；ISR 掩码按 xiicps_hw.h；
 *    setup_role 按读写角色置/清 RD_WR；写首字节前不等 TXDV；40 kHz（div_a=1/div_b=62）。
 *  - GPIO 后端：读字节第 9 拍先拉低 SCL 再改 SDA（防被当 START），中间字节 ACK、末字节 NACK，
 *    字节间释放 SDA；SCL 高后额外采样延时；半周期 40 µs。
 */
#include "s5_camera.h"
#include "s5_ov5640_init_table.h"

#ifndef S5_HOST_TEST
#include "xil_io.h"
#endif

#define S5_CAM_POLL_LIMIT 2000000u

uint32_t S5Cam_StreamOnMs;
uint32_t S5Cam_WarmupMs;

#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_PS
static uint32_t s5_cam_div_bits; /* PS 后端 CR 分频位 */
#endif
#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_GPIO
static uint32_t s5_gpio_ctrl;    /* GPIO 后端 ctrl 影子（低 3 位） */
#endif
static uint32_t s5_last_err_isr; /* 最近一次错误 ISR（trace 用） */

static uint32_t cam_rd(const S5CamBus *b, uint32_t addr) { return b->rd(b->ctx, addr); }
static void cam_wr(const S5CamBus *b, uint32_t addr, uint32_t v) { b->wr(b->ctx, addr, v); }

static void cam_delay_us(const S5CamBus *b, uint32_t us)
{
    if ((b != 0) && (b->delay_us != 0)) {
        b->delay_us(b->ctx, us);
    }
}

/* ================= 复位（cmos_rst，低有效） ================= */

int S5Cam_ResetSeq(const S5CamBus *bus, uint32_t *pin_before, uint32_t *pin_after)
{
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    if (pin_before != 0) {
        *pin_before = cam_rd(bus, S5_CAM_RST_REG);
    }
    cam_wr(bus, S5_CAM_RST_REG, (S5_CAM_RST_ACTIVE_LOW != 0u) ? 1u : 0u);
    cam_delay_us(bus, S5_CAM_RST_HOLD_MS * 1000u);
    cam_wr(bus, S5_CAM_RST_REG, (S5_CAM_RST_ACTIVE_LOW != 0u) ? 0u : 1u);
    cam_delay_us(bus, S5_CAM_RST_HOLD_MS * 1000u);
    cam_wr(bus, S5_CAM_RST_REG, (S5_CAM_RST_ACTIVE_LOW != 0u) ? 1u : 0u);
    cam_delay_us(bus, S5_CAM_RST_HOLD_MS * 1000u);
    if (pin_after != 0) {
        *pin_after = cam_rd(bus, S5_CAM_RST_REG);
    }
    return 0;
}

/* ================= SLCR（PS I2C0 复位语义排查） ================= */

uint32_t S5Cam_SlcrRead(const S5CamBus *bus, uint32_t reg)
{
    uint32_t v;

    cam_wr(bus, S5_CAM_SLCR_UNLOCK, S5_CAM_SLCR_UNLOCK_VAL);
    v = cam_rd(bus, reg);
    cam_wr(bus, S5_CAM_SLCR_LOCK, S5_CAM_SLCR_LOCK_VAL);
    return v;
}

void S5Cam_SlcrWrite(const S5CamBus *bus, uint32_t reg, uint32_t val)
{
    cam_wr(bus, S5_CAM_SLCR_UNLOCK, S5_CAM_SLCR_UNLOCK_VAL);
    cam_wr(bus, reg, val);
    cam_wr(bus, S5_CAM_SLCR_LOCK, S5_CAM_SLCR_LOCK_VAL);
}

int S5Cam_I2cRstPulse(const S5CamBus *bus, uint32_t force, uint32_t *before, uint32_t *after)
{
    uint32_t v;

    cam_wr(bus, S5_CAM_SLCR_UNLOCK, S5_CAM_SLCR_UNLOCK_VAL);
    v = cam_rd(bus, S5_CAM_SLCR_I2C_RST);
    if (before != 0) {
        *before = v;
    }
    if (((v & 1u) != 0u) || (force != 0u)) {
        cam_wr(bus, S5_CAM_SLCR_I2C_RST, v | 1u);
        cam_delay_us(bus, 1000u);
        cam_wr(bus, S5_CAM_SLCR_I2C_RST, v & ~1u);
        cam_delay_us(bus, 10000u);
    }
    v = cam_rd(bus, S5_CAM_SLCR_I2C_RST);
    cam_wr(bus, S5_CAM_SLCR_LOCK, S5_CAM_SLCR_LOCK_VAL);
    if (after != 0) {
        *after = v;
    }
    return ((v & 1u) == 0u) ? 0 : -1;
}

/* ================= PS I2C0 后端 ================= */
#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_PS

static void i2c_cr_write(const S5CamBus *b, uint32_t ctl)
{
    uint32_t cr = cam_rd(b, S5_CAM_I2C_BASE + S5_I2C_CR);

    cr &= (S5_I2C_CR_DIV_A_MASK | S5_I2C_CR_DIV_B_MASK);
    cr = (cr & ~(S5_I2C_CR_DIV_A_MASK | S5_I2C_CR_DIV_B_MASK)) | s5_cam_div_bits;
    cr |= ctl;
    cam_wr(b, S5_CAM_I2C_BASE + S5_I2C_CR, cr);
}

static void i2c_setup_role(const S5CamBus *b, int is_read, uint32_t extra)
{
    uint32_t ctl = S5_I2C_CR_MS | S5_I2C_CR_NEA | S5_I2C_CR_ACKEN | extra;

    if (is_read != 0) {
        ctl |= S5_I2C_CR_RD_WR;
    } else {
        ctl &= ~S5_I2C_CR_RD_WR;
    }
    i2c_cr_write(b, ctl);
}

/* 等传输结束：0=COMP；-1=NACK；-2=TO；-3=ARB/溢出；-4=超时 */
static int i2c_wait_complete(const S5CamBus *b, uint32_t *isr_out)
{
    uint32_t n;

    for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
        uint32_t isr = cam_rd(b, S5_CAM_I2C_BASE + S5_I2C_ISR);

        if ((isr & (S5_I2C_ISR_NACK | S5_I2C_ISR_TO | S5_I2C_ISR_ARB | S5_I2C_ISR_TX_OVR |
                    S5_I2C_ISR_RX_OVR | S5_I2C_ISR_RX_UNF)) != 0u) {
            cam_wr(b, S5_CAM_I2C_BASE + S5_I2C_ISR, isr);
            if (isr_out != 0) {
                *isr_out = isr;
            }
            if ((isr & S5_I2C_ISR_NACK) != 0u) {
                return -1;
            }
            return ((isr & S5_I2C_ISR_TO) != 0u) ? -2 : -3;
        }
        if ((isr & S5_I2C_ISR_COMP) != 0u) {
            cam_wr(b, S5_CAM_I2C_BASE + S5_I2C_ISR, isr);
            if (isr_out != 0) {
                *isr_out = isr;
            }
            return 0;
        }
    }
    return -4;
}

static uint32_t i2c_calc_div(uint32_t fpclk, uint32_t fscl, uint32_t *fa, uint32_t *fb)
{
    uint32_t best_a = 0u, best_b = 0u, best_err = 0xFFFFFFFFu, a, b;

    for (a = 0u; a < 4u; a++) {
        for (b = 0u; b < 64u; b++) {
            uint32_t f = fpclk / (22u * (a + 1u) * (b + 1u));
            uint32_t err;

            if (f < fscl) {
                continue;
            }
            err = f - fscl;
            if (err < best_err) {
                best_err = err;
                best_a = a;
                best_b = b;
            } else if (err == best_err) {
                if ((a == 1u) && (best_a != 1u)) {
                    best_a = a;
                    best_b = b;
                } else if ((a != 1u) && (best_a != 1u) && (b > best_b)) {
                    best_a = a;
                    best_b = b;
                }
            }
        }
    }
    *fa = best_a;
    *fb = best_b;
    return (best_a << 14) | (best_b << 8);
}

int S5Cam_I2cInitEx(const S5CamBus *bus, uint32_t cpu_hz, uint32_t *cr_out, uint32_t *sr_out,
                    uint32_t *div_out)
{
    uint32_t div_a = 0u, div_b = 0u, cr;
    int rc;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0) || (cpu_hz == 0u)) {
        return -1;
    }
    s5_cam_div_bits = i2c_calc_div(cpu_hz, S5_CAM_I2C_TARGET_HZ, &div_a, &div_b);
    cr = s5_cam_div_bits | S5_I2C_CR_MS | S5_I2C_CR_NEA;
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_CR, cr);
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_TIME_OUT, 0xFFu);
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_ISR, 0x2FFu);
    if (cr_out != 0) {
        *cr_out = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_CR);
    }
    if (sr_out != 0) {
        *sr_out = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_SR);
    }
    if (div_out != 0) {
        *div_out = (div_a << 8) | div_b;
    }
    rc = (cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_CR) == cr) ? 0 : -2;
    return rc;
}

int S5Cam_WriteReg(const S5CamBus *bus, uint16_t reg, uint8_t val)
{
    int rc;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    i2c_setup_role(bus, 0, S5_I2C_CR_CLR_FIFO);
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_DATA, (reg >> 8) & 0xFFu);
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_DATA, reg & 0xFFu);
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_DATA, val);
    cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_ADDR, (uint32_t)S5_CAM_SCCB_ADDR << 1);
    rc = i2c_wait_complete(bus, 0);
    if (rc == 0) {
        return 0;
    }
    return (rc == -1) ? -3 : ((rc == -2) ? -5 : -4);
}

#endif /* PS 后端 */

/* ================= gpio_sccb 后端 ================= */
#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_GPIO

static void gpio_wr_raw(const S5CamBus *b, uint32_t v)
{
    s5_gpio_ctrl = S5_CAM_GPIO_MODE | (v & (S5_CAM_GPIO_SCL_LOW | S5_CAM_GPIO_SDA_LOW));
    cam_wr(b, S5_CAM_GPIO_CTRL, s5_gpio_ctrl);
}

static uint32_t gpio_levels(const S5CamBus *b) { return cam_rd(b, S5_CAM_GPIO_STAT) & 0x3u; }
static void gpio_dly(const S5CamBus *b) { cam_delay_us(b, S5_CAM_GPIO_HALF_US); }

static void gpio_scl(const S5CamBus *b, int low)
{
    if (low != 0) {
        gpio_wr_raw(b, s5_gpio_ctrl | S5_CAM_GPIO_SCL_LOW);
    } else {
        gpio_wr_raw(b, s5_gpio_ctrl & ~S5_CAM_GPIO_SCL_LOW);
    }
}

static void gpio_sda(const S5CamBus *b, int low)
{
    if (low != 0) {
        gpio_wr_raw(b, s5_gpio_ctrl | S5_CAM_GPIO_SDA_LOW);
    } else {
        gpio_wr_raw(b, s5_gpio_ctrl & ~S5_CAM_GPIO_SDA_LOW);
    }
}

static void gpio_start(const S5CamBus *b)
{
    gpio_sda(b, 0);
    gpio_scl(b, 0);
    gpio_dly(b);
    gpio_sda(b, 1);
    gpio_dly(b);
    gpio_scl(b, 1);
    gpio_dly(b);
}

static void gpio_stop(const S5CamBus *b)
{
    gpio_scl(b, 1);
    gpio_sda(b, 1);
    gpio_dly(b);
    gpio_scl(b, 0);
    gpio_dly(b);
    gpio_sda(b, 0);
    gpio_dly(b);
}

static void gpio_recover(const S5CamBus *b)
{
    uint32_t i;

    gpio_sda(b, 0);
    for (i = 0u; i < 9u; i++) {
        gpio_scl(b, 0);
        gpio_dly(b);
        gpio_scl(b, 1);
        gpio_dly(b);
    }
}

static int gpio_write_byte(const S5CamBus *b, uint8_t v)
{
    uint32_t i;

    for (i = 0u; i < 8u; i++) {
        gpio_sda(b, ((v & (uint8_t)(0x80u >> i)) != 0u) ? 0 : 1);
        gpio_dly(b);
        gpio_scl(b, 0);
        gpio_dly(b);
        gpio_scl(b, 1);
        gpio_dly(b);
    }
    gpio_sda(b, 0);
    gpio_dly(b);
    gpio_scl(b, 0);
    gpio_dly(b);
    i = gpio_levels(b);
    gpio_scl(b, 1);
    gpio_dly(b);
    return ((i & 0x2u) == 0u) ? 0 : -1;
}

static int gpio_read_byte(const S5CamBus *b, uint8_t *val, int ack, uint8_t *bits_out)
{
    uint32_t i;
    uint8_t v = 0u, bits = 0u;

    gpio_sda(b, 0);
    gpio_dly(b);
    for (i = 0u; i < 8u; i++) {
        gpio_scl(b, 1);
        gpio_dly(b);
        gpio_scl(b, 0);
        gpio_dly(b);
        cam_delay_us(b, S5_CAM_GPIO_SAMPLE_US);
        if ((gpio_levels(b) & 0x2u) != 0u) {
            v |= (uint8_t)(0x80u >> i);
            bits |= (uint8_t)(0x80u >> i);
        }
        gpio_dly(b);
    }
    /* 第 9 拍：先拉低 SCL 再改 SDA；ack=1 拉低(ACK)，ack=0 保持高(NACK) */
    gpio_scl(b, 1);
    gpio_dly(b);
    gpio_sda(b, (ack != 0) ? 1 : 0);
    gpio_dly(b);
    gpio_scl(b, 0);
    gpio_dly(b);
    gpio_scl(b, 1);
    gpio_dly(b);
    gpio_sda(b, 0);
    gpio_dly(b);
    *val = v;
    if (bits_out != 0) {
        *bits_out = bits;
    }
    return 0;
}

static int gpio_write_reg(const S5CamBus *b, uint16_t reg, uint8_t val)
{
    gpio_start(b);
    if (gpio_write_byte(b, (uint8_t)(S5_CAM_SCCB_ADDR << 1)) != 0) {
        gpio_stop(b);
        return -3;
    }
    if (gpio_write_byte(b, (uint8_t)(reg >> 8)) != 0) {
        gpio_stop(b);
        return -3;
    }
    if (gpio_write_byte(b, (uint8_t)(reg & 0xFFu)) != 0) {
        gpio_stop(b);
        return -3;
    }
    if (gpio_write_byte(b, val) != 0) {
        gpio_stop(b);
        return -3;
    }
    gpio_stop(b);
    return 0;
}

int S5Cam_I2cInitEx(const S5CamBus *bus, uint32_t cpu_hz, uint32_t *cr_out, uint32_t *sr_out,
                    uint32_t *div_out)
{
    uint32_t lv;

    (void)cpu_hz;
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    s5_gpio_ctrl = S5_CAM_GPIO_MODE;
    cam_wr(bus, S5_CAM_GPIO_CTRL, S5_CAM_GPIO_MODE);
    cam_delay_us(bus, 1000u);
    lv = gpio_levels(bus);
    if ((lv & 0x3u) != 0x3u) {
        gpio_recover(bus);
        gpio_wr_raw(bus, S5_CAM_GPIO_MODE);
        cam_delay_us(bus, 1000u);
        lv = gpio_levels(bus);
    }
    if (cr_out != 0) {
        *cr_out = s5_gpio_ctrl;
    }
    if (sr_out != 0) {
        *sr_out = lv;
    }
    if (div_out != 0) {
        *div_out = S5_CAM_GPIO_HALF_US;
    }
    return ((lv & 0x3u) == 0x3u) ? 0 : -2;
}

int S5Cam_WriteReg(const S5CamBus *bus, uint16_t reg, uint8_t val)
{
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    return gpio_write_reg(bus, reg, val);
}

#endif /* GPIO 后端 */

int S5Cam_I2cInit(const S5CamBus *bus, uint32_t cpu_hz)
{
    return S5Cam_I2cInitEx(bus, cpu_hz, 0, 0, 0);
}

/* ================= 寄存器 dump / trace ================= */

void S5Cam_RegDump(const S5CamBus *bus, S5CamRegDump *d)
{
    if ((bus == 0) || (d == 0)) {
        return;
    }
#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_GPIO
    d->cr = cam_rd(bus, S5_CAM_GPIO_CTRL);
    d->sr = cam_rd(bus, S5_CAM_GPIO_STAT) & 0x3u;
    d->isr = 0u;
    d->addr = 0u;
    d->trsz = 0u;
    d->busy = 0u;
    d->impr = 0u;
#else
    d->cr = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_CR);
    d->sr = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_SR);
    d->isr = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_ISR);
    d->addr = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_ADDR);
    d->trsz = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_TRANS_SIZE);
    d->busy = (d->sr & S5_I2C_SR_BUSY) ? 1u : 0u;
    d->impr = cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_IMPR);
#endif
}

static void trace_add(const S5CamBus *bus, S5CamTrace *tr, uint8_t kind, uint8_t byte,
                      uint8_t have_byte)
{
    S5CamTraceStep *st;
    S5CamRegDump d;

    if (tr->n >= S5_CAM_TRACE_MAX) {
        return;
    }
    S5Cam_RegDump(bus, &d);
    st = &tr->step[tr->n++];
    st->kind = kind;
    st->byte = byte;
    st->have_byte = have_byte;
    st->bits = 0u;
    st->isr = d.isr;
    st->sr = d.sr;
    st->cr = d.cr;
    st->addr = d.addr;
    st->trsz = d.trsz;
}

int S5Cam_ReadRegTrace(const S5CamBus *bus, uint8_t addr7, uint16_t reg, uint8_t *val,
                       uint32_t nbytes, S5CamTrace *tr)
{
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0) || (val == 0) || (tr == 0)) {
        return -1;
    }
    if ((nbytes == 0u) || (nbytes > 4u)) {
        nbytes = 1u;
    }
    tr->n = 0u;
    tr->rc = 0;
    tr->acks = 0u;

#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_GPIO
    {
        uint32_t k;

        gpio_start(bus);
        trace_add(bus, tr, S5_CAM_TR_START, (uint8_t)(addr7 << 1), 1u);
        if (gpio_write_byte(bus, (uint8_t)(addr7 << 1)) != 0) {
            tr->rc = -3;
            goto done;
        }
        tr->acks |= 1u;
        if (gpio_write_byte(bus, (uint8_t)(reg >> 8)) != 0) {
            tr->rc = -3;
            goto done;
        }
        tr->acks |= 2u;
        trace_add(bus, tr, S5_CAM_TR_REG_HI, (uint8_t)(reg >> 8), 1u);
        if (gpio_write_byte(bus, (uint8_t)(reg & 0xFFu)) != 0) {
            tr->rc = -3;
            goto done;
        }
        tr->acks |= 4u;
        trace_add(bus, tr, S5_CAM_TR_REG_LO, (uint8_t)(reg & 0xFFu), 1u);
        /* 重复起始 */
        gpio_sda(bus, 0);
        gpio_scl(bus, 0);
        gpio_dly(bus);
        gpio_sda(bus, 1);
        gpio_dly(bus);
        gpio_scl(bus, 1);
        gpio_dly(bus);
        trace_add(bus, tr, S5_CAM_TR_RSTART, (uint8_t)(((uint32_t)addr7 << 1) | 1u), 1u);
        if (gpio_write_byte(bus, (uint8_t)(((uint32_t)addr7 << 1) | 1u)) != 0) {
            tr->rc = -3;
            goto done;
        }
        tr->acks |= 8u;
        for (k = 0u; k < nbytes; k++) {
            uint8_t v = 0u, bits = 0u;

            (void)gpio_read_byte(bus, &v, (k + 1u < nbytes) ? 1 : 0, &bits);
            val[k] = v;
            trace_add(bus, tr, S5_CAM_TR_DATA, v, 1u);
            if (tr->n > 0u) {
                tr->step[tr->n - 1u].bits = bits;
            }
        }
        gpio_stop(bus);
        trace_add(bus, tr, S5_CAM_TR_STOP, 0u, 0u);
        tr->rc = 0;
    }
done:
#else
    {
        uint32_t i, isr = 0u;

        i2c_setup_role(bus, 0, S5_I2C_CR_HOLD);
        cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_DATA, (reg >> 8) & 0xFFu);
        trace_add(bus, tr, S5_CAM_TR_REG_HI, (uint8_t)(reg >> 8), 1u);
        cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_DATA, reg & 0xFFu);
        trace_add(bus, tr, S5_CAM_TR_REG_LO, (uint8_t)(reg & 0xFFu), 1u);
        cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_ADDR, (uint32_t)addr7 << 1);
        trace_add(bus, tr, S5_CAM_TR_START, (uint8_t)(addr7 << 1), 1u);
        {
            int rc = i2c_wait_complete(bus, &isr);

            if (rc != 0) {
                s5_last_err_isr = isr;
                tr->rc = (rc == -1) ? -3 : ((rc == -2) ? -5 : -4);
                goto done;
            }
        }
        i2c_setup_role(bus, 1, S5_I2C_CR_HOLD);
        cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_ADDR, ((uint32_t)addr7 << 1) | 1u);
        cam_wr(bus, S5_CAM_I2C_BASE + S5_I2C_TRANS_SIZE, nbytes);
        trace_add(bus, tr, S5_CAM_TR_RSTART, (uint8_t)(((uint32_t)addr7 << 1) | 1u), 1u);
        for (i = 0u; i < nbytes; i++) {
            uint32_t n;

            if (i == (nbytes - 1u)) {
                i2c_cr_write(bus, S5_I2C_CR_MS | S5_I2C_CR_NEA | S5_I2C_CR_HOLD);
            }
            for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
                if ((cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_SR) & S5_I2C_SR_RXDV) != 0u) {
                    break;
                }
            }
            if (n >= S5_CAM_POLL_LIMIT) {
                tr->rc = -5;
                goto done;
            }
            val[i] = (uint8_t)(cam_rd(bus, S5_CAM_I2C_BASE + S5_I2C_DATA) & 0xFFu);
            trace_add(bus, tr, S5_CAM_TR_DATA, val[i], 1u);
        }
        {
            int rc = i2c_wait_complete(bus, &isr);

            if (rc != 0) {
                s5_last_err_isr = isr;
                tr->rc = (rc == -1) ? -3 : ((rc == -2) ? -5 : -4);
                goto done;
            }
        }
        i2c_setup_role(bus, 0, 0u);
        trace_add(bus, tr, S5_CAM_TR_STOP, 0u, 0u);
        tr->rc = 0;
    }
done:
#endif
    {
        S5CamRegDump d;

        S5Cam_RegDump(bus, &d);
        tr->final_isr = (tr->rc != 0 && s5_last_err_isr != 0u) ? s5_last_err_isr : d.isr;
        tr->final_sr = d.sr;
        tr->final_cr = d.cr;
        tr->final_addr = d.addr;
        tr->final_trsz = d.trsz;
    }
    return tr->rc;
}

int S5Cam_ReadRegEx(const S5CamBus *bus, uint16_t reg, uint8_t *val, uint32_t *isr_addr,
                    uint32_t *isr_data)
{
    S5CamTrace tr;

    (void)isr_addr;
    (void)isr_data;
    return S5Cam_ReadRegTrace(bus, S5_CAM_SCCB_ADDR, reg, val, 1u, &tr);
}

int S5Cam_ReadReg(const S5CamBus *bus, uint16_t reg, uint8_t *val)
{
    return S5Cam_ReadRegEx(bus, reg, val, 0, 0);
}

int S5Cam_ScanAddr(const S5CamBus *bus, uint8_t addr7, uint8_t *id, S5CamTrace *tr)
{
    uint32_t i;
    uint8_t v = 0u;
    int ack;

    if (S5Cam_ReadRegTrace(bus, addr7, 0x300Au, &v, 1u, tr) != 0) {
        ack = 0;
        for (i = 0u; i < tr->n; i++) {
            if (tr->step[i].kind == S5_CAM_TR_RSTART) {
                ack = 1;
                break;
            }
            if ((tr->step[i].kind == S5_CAM_TR_REG_LO) &&
                ((tr->step[i].isr & S5_I2C_ISR_NACK) != 0u)) {
                ack = 1;
                break;
            }
        }
    } else {
        ack = ((addr7 == S5_CAM_SCCB_ADDR) || (v != 0u)) ? 1 : 0;
    }
    if (id != 0) {
        *id = v;
    }
    return ack;
}

/* 阶段3 冻结件完整初始化表（见 s5_ov5640_init_table.h；302 项，顺序照抄） */
uint32_t S5Cam_InitTableCount(void)
{
    return (uint32_t)S5_OV5640_INIT_TBL_N;
}

/* 0x3008 每次写后延时 5ms（software reset / power down / stream on 需要） */
int S5Cam_ApplyInitTable(const S5CamBus *bus)
{
    uint32_t i;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    for (i = 0u; i < (uint32_t)S5_OV5640_INIT_TBL_N; i++) {
        if (S5Cam_WriteReg(bus, s5_ov5640_init_tbl[i].reg, s5_ov5640_init_tbl[i].val) != 0) {
            return -(int)(i + 1u);
        }
        if (s5_ov5640_init_tbl[i].reg == 0x3008u) {
            cam_delay_us(bus, 5000u);
        }
    }
    cam_delay_us(bus, 20000u);
    return 0;
}

/* 理论 PCLK = HTS(0x380C/0D) × VTS(0x380E/0F) × fps（用于与实测 PCLK 对照） */
uint32_t S5Cam_TheoryPclk(uint32_t hts, uint32_t vts, uint32_t fps)
{
    return hts * vts * fps;
}

/* v15：改时序寄存器前必须显式停流（0x3008=0x42），否则 sensor 停流不再出 HREF/VSYNC */
int S5Cam_StreamOff(const S5CamBus *bus)
{
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    if (S5Cam_WriteReg(bus, 0x3008u, 0x42u) != 0) {
        return -1;
    }
    cam_delay_us(bus, 10000u);
    return 0;
}

/* 时序敏感覆盖（顺序敏感）：子采样 → 偏移 → HTS/VTS → 窗口 → PLL */
int S5Cam_SetPolarity(const S5CamBus *bus, uint8_t val)
{
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    return S5Cam_WriteReg(bus, 0x4740u, val);
}

/* v21：0x4740 极性实验的最小安全序列：停流 → 写极性 → 开流（含 10/20ms 延时与回读） */
int S5Cam_StreamWithPolarity(const S5CamBus *bus, uint8_t pol4740)
{
    int rc = S5Cam_StreamOff(bus);

    if (rc != 0) {
        return rc;
    }
    if (S5Cam_SetPolarity(bus, pol4740) != 0) {
        return -2;
    }
    return S5Cam_StreamOn(bus);
}

int S5Cam_ApplyTiming(const S5CamBus *bus)
{
    typedef struct { uint16_t reg; uint8_t val; } S5CamTLocal;
    static const S5CamTLocal tbl[] = {
        {0x3814u, 0x31u}, {0x3815u, 0x31u},
        {0x3810u, 0x00u}, {0x3811u, 0x00u}, {0x3812u, 0x00u}, {0x3813u, 0x00u},
        {0x380Cu, 0x07u}, {0x380Du, 0x64u},
        {0x380Eu, 0x02u}, {0x380Fu, 0xE4u},
        {0x3808u, 0x05u}, {0x3809u, 0x00u},
        {0x380Au, 0x02u}, {0x380Bu, 0xD0u},
        {0x3035u, 0x21u}, {0x3036u, 0x69u}, {0x3037u, 0x13u}, {0x3108u, 0x01u},
    };
    uint32_t i;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    for (i = 0u; i < (uint32_t)(sizeof(tbl) / sizeof(tbl[0])); i++) {
        if (S5Cam_WriteReg(bus, tbl[i].reg, tbl[i].val) != 0) {
            return -(int)(i + 1u);
        }
    }
    cam_delay_us(bus, 10000u);
    return 0;
}

int S5Cam_StreamOn(const S5CamBus *bus)
{
    uint8_t v = 0u;

    if (S5Cam_WriteReg(bus, 0x3008u, 0x02u) != 0) {
        return -1;
    }
    cam_delay_us(bus, 20000u);
    if (S5Cam_ReadReg(bus, 0x3008u, &v) != 0) {
        return -2;
    }
    return ((v & 0x02u) != 0u) ? 0 : -3;
}

/* ================= OV5640 配置 ================= */

int S5Cam_Probe(const S5CamBus *bus, uint16_t *chip_id)
{
    uint8_t hi = 0u, lo = 0u;

    if (chip_id == 0) {
        return -1;
    }
    if (S5Cam_ReadReg(bus, 0x300Au, &hi) != 0) {
        return -2;
    }
    if (S5Cam_ReadReg(bus, 0x300Bu, &lo) != 0) {
        return -2;
    }
    *chip_id = (uint16_t)(((uint16_t)hi << 8) | lo);
    return (*chip_id == 0x5640u) ? 0 : -3;
}

typedef struct S5CamReg {
    uint16_t reg;
    uint8_t val;
} S5CamReg;

static const S5CamReg s5_cam_vga_tbl[] = {
    {0x3035u, 0x21u}, {0x3036u, 0x69u}, {0x3034u, 0x1Au}, {0x3808u, 0x05u},
    {0x3809u, 0x00u}, {0x380Au, 0x02u}, {0x380Bu, 0xD0u}, {0x380Cu, 0x07u},
    {0x380Du, 0x64u}, {0x380Eu, 0x02u}, {0x380Fu, 0xE4u}, {0x501Fu, 0x01u},
    {0x3810u, 0x00u}, {0x3811u, 0x00u},
    {0x3812u, 0x00u}, {0x3813u, 0x00u}, {0x3814u, 0x31u}, {0x3815u, 0x31u},
    {0x3824u, 0x04u}, {0x4300u, 0x60u}, {0x3A02u, 0x05u}, {0x3A03u, 0xC4u},
    {0x3A14u, 0x05u}, {0x3A15u, 0xC4u},
};

/* v12：关键寄存器（系统/PLL/PAD 使能/格式/JPEG/stream） */
static const uint16_t s5_key_regs[] = {
    0x300Eu, 0x3103u, 0x3017u, 0x3018u, 0x3034u, 0x3035u, 0x3036u, 0x3037u,
    0x3108u, 0x4300u, 0x501Fu, 0x440Eu, 0x460Cu,
    0x3814u, 0x3815u, 0x380Cu, 0x380Du, 0x380Eu, 0x380Fu, 0x3008u,
};

uint32_t S5Cam_KeyRegList(uint16_t *regs, uint32_t max)
{
    uint32_t n = (uint32_t)(sizeof(s5_key_regs) / sizeof(s5_key_regs[0]));
    uint32_t i;

    if ((regs == 0) || (max == 0u)) {
        return 0u;
    }
    if (n > max) {
        n = max;
    }
    for (i = 0u; i < n; i++) {
        regs[i] = s5_key_regs[i];
    }
    return n;
}

int S5Cam_LastWritten(uint16_t reg, uint8_t *val)
{
    uint32_t i;

    if (val == 0) {
        return -1;
    }
    if (reg == 0x3008u) {
        *val = 0x02u; /* stream on 最后写 */
        return 0;
    }
    /* 覆盖表在完整表之后写 ⇒ 先查覆盖表（后者优先），再查完整表 */
    for (i = (uint32_t)(sizeof(s5_cam_vga_tbl) / sizeof(s5_cam_vga_tbl[0])); i > 0u; i--) {
        if (s5_cam_vga_tbl[i - 1u].reg == reg) {
            *val = s5_cam_vga_tbl[i - 1u].val;
            return 0;
        }
    }
    for (i = (uint32_t)S5_OV5640_INIT_TBL_N; i > 0u; i--) {
        if (s5_ov5640_init_tbl[i - 1u].reg == reg) {
            *val = s5_ov5640_init_tbl[i - 1u].val;
            return 0;
        }
    }
    return -2;
}

int S5Cam_CheckKeyRegs(const S5CamBus *bus, S5CamRegCheck *out, uint32_t max,
                       uint32_t *n, uint32_t *mismatch)
{
    uint16_t regs[16];
    uint32_t got;
    uint32_t k;
    uint32_t cnt = 0u;
    uint32_t bad = 0u;

    if ((bus == 0) || (out == 0) || (n == 0) || (mismatch == 0)) {
        return -1;
    }
    got = S5Cam_KeyRegList(regs, 16u);
    for (k = 0u; (k < got) && (cnt < max); k++) {
        uint8_t exp = 0u;
        uint8_t rd = 0u;

        if (S5Cam_LastWritten(regs[k], &exp) != 0) {
            continue;
        }
        if (S5Cam_ReadReg(bus, regs[k], &rd) != 0) {
            rd = 0xFFu;
        }
        out[cnt].reg = regs[k];
        out[cnt].expect = exp;
        out[cnt].read = rd;
        out[cnt].ok = (uint8_t)((rd == exp) ? 1 : 0);
        if (rd != exp) {
            bad++;
        }
        cnt++;
    }
    *n = cnt;
    *mismatch = bad;
    return (int)bad;
}

int S5Cam_ApplyVga(const S5CamBus *bus)
{
    uint32_t i;

    for (i = 0u; i < (uint32_t)(sizeof(s5_cam_vga_tbl) / sizeof(s5_cam_vga_tbl[0])); i++) {
        if (S5Cam_WriteReg(bus, s5_cam_vga_tbl[i].reg, s5_cam_vga_tbl[i].val) != 0) {
            return -(int)(i + 1u);
        }
    }
    return 0;
}

static int cam_read_u16(const S5CamBus *bus, uint16_t hi_reg, uint16_t *out)
{
    uint8_t h = 0u, l = 0u;

    if (S5Cam_ReadReg(bus, hi_reg, &h) != 0) {
        return -1;
    }
    if (S5Cam_ReadReg(bus, (uint16_t)(hi_reg + 1u), &l) != 0) {
        return -1;
    }
    *out = (uint16_t)(((uint16_t)h << 8) | l);
    return 0;
}

int S5Cam_VerifyVga(const S5CamBus *bus, S5CamInfo *info)
{
    uint32_t attempt;

    if (info == 0) {
        return -1;
    }
    for (attempt = 0u; attempt < 3u; attempt++) {
        S5CamInfo rd;

        if (cam_read_u16(bus, 0x3808u, &rd.dvpho) != 0) {
            continue;
        }
        if (cam_read_u16(bus, 0x380Au, &rd.dvpvo) != 0) {
            continue;
        }
        if (cam_read_u16(bus, 0x380Cu, &rd.hts) != 0) {
            continue;
        }
        if (cam_read_u16(bus, 0x380Eu, &rd.vts) != 0) {
            continue;
        }


        if ((rd.dvpho == (uint16_t)S5_CAM_CAP_W) && (rd.dvpvo == (uint16_t)S5_CAM_VSIZE) &&
            (rd.hts == 1892u) && (rd.vts == (uint16_t)S5_CAM_VTS)) {
            info->dvpho = rd.dvpho;
            info->dvpvo = rd.dvpvo;
            info->hts = rd.hts;
            info->vts = rd.vts;
            return 0;
        }
        (void)S5Cam_ApplyVga(bus);
    }
    return -2;
}

/* ================= S2MM VDMA（axi_vdma 直接模式，固定偏移） ================= */

void S5Cam_SrDecode(uint32_t sr, int *halted, uint32_t *err, uint32_t *frmcnt)
{
    if (halted != 0) {
        *halted = (sr & S5_CAM_SR_HALTED) ? 1 : 0;
    }
    if (err != 0) {
        *err = sr & S5_CAM_SR_ERR_ALL;
    }
    if (frmcnt != 0) {
        *frmcnt = (sr & S5_CAM_SR_FRMCNT_MASK) >> S5_CAM_SR_FRMCNT_SHIFT;
    }
}

static void vdstep(S5CamVdmaTrace *tr, const char *name, uint32_t off, uint32_t wval,
                   uint32_t rval, uint32_t expect, int has_expect)
{
    S5CamVdmaStep *st;

    if ((tr == 0) || (tr->n >= S5_CAM_VDMA_TRACE_MAX)) {
        return;
    }
    st = &tr->step[tr->n++];
    st->name = name;
    st->off = off;
    st->wval = wval;
    st->rval = rval;
    st->expect = expect;
    st->has_expect = (uint8_t)(has_expect ? 1 : 0);
    st->ok = (uint8_t)((has_expect == 0) || (rval == expect));
    if ((st->ok == 0u) && (tr->first_bad < 0)) {
        tr->first_bad = (int)(tr->n - 1u);
    }
}

/* 轮询 SR 直到 (sr & mask)==want（want=1 表示置位，0 表示清零）；
 * 判据用掩码：HALTED=bit0、ERR_ALL=0x0FF0（bit[23:16]=FRMCNT 不参与判错）。 */
static int camv_poll_sr(const S5CamBus *bus, uint32_t mask, int want_set, uint32_t *last)
{
    uint32_t n;

    for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
        uint32_t sr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);

        if (last != 0) {
            *last = sr;
        }
        if (want_set != 0) {
            if ((sr & mask) == mask) {
                return 0;
            }
        } else if ((sr & mask) == 0u) {
            return 0;
        }
    }
    return -1;
}

int S5CamVdma_Config(const S5CamBus *bus, S5CamInfo *info, S5CamVdmaTrace *tr)
{
    uint32_t sr = 0u, ver, rv;

    if ((bus == 0) || (info == 0)) {
        return -1;
    }
    if (tr != 0) {
        tr->n = 0u;
        tr->first_bad = -1;
        tr->cand = 0xFFFFFFFFu;
        tr->base = S5_CAM_VDMA_BASE;
    }

    ver = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VER);
    vdstep(tr, "VER(0x2C)", S5_CAM_S2MM_VER, 0u, ver, 0u, 0);
    if ((ver == 0u) || (ver == 0xFFFFFFFFu)) {
        return -4; /* IP 不在/基址不对 */
    }

    /* 1) 复位：CR.RESET(0x4)=1；SR 判据用掩码（ERR_ALL + HALTED），FRMCNT 忽略 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, S5_CAM_CR_RESET);
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);
    vdstep(tr, "CR(0x30)<=RESET", S5_CAM_S2MM_CR, S5_CAM_CR_RESET, rv, 0u, 0);
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 1, &sr) != 0) {
        vdstep(tr, "SR(0x34)", S5_CAM_S2MM_SR, 0u, sr, 0u, 0);
        vdstep(tr, "SR.HALTED==1", S5_CAM_S2MM_SR, 0u, (sr & S5_CAM_SR_HALTED), S5_CAM_SR_HALTED, 1);
        return -4;
    }
    vdstep(tr, "SR(0x34)", S5_CAM_S2MM_SR, 0u, sr, 0u, 0);
    vdstep(tr, "SR.HALTED==1", S5_CAM_S2MM_SR, 0u, (sr & S5_CAM_SR_HALTED), S5_CAM_SR_HALTED, 1);

    /* 2) 配置（S2MM 固定偏移：VSIZE=0xA0 / HSIZE=0xA4 / STRIDE=0xA8 / FRMPTR1=0xAC） */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, (uint32_t)S5_CAM_VSIZE);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE, (uint32_t)S5_CAM_STRIDE);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE, (uint32_t)S5_CAM_STRIDE);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE);
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE);
    vdstep(tr, "VSIZE(0xA0)", S5_CAM_S2MM_VSIZE, S5_CAM_VSIZE, rv, S5_CAM_VSIZE, 1);
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE);
    vdstep(tr, "HSIZE(0xA4)", S5_CAM_S2MM_HSIZE, S5_CAM_STRIDE, rv, S5_CAM_STRIDE, 1);
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE);
    vdstep(tr, "STRIDE(0xA8)", S5_CAM_S2MM_STRIDE, S5_CAM_STRIDE, rv, S5_CAM_STRIDE, 1);
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0);
    vdstep(tr, "FRMPTR1(0xAC)", S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE, rv, S5_CAM_RAW_BASE, 1);

    /* 3) 启动：CR = RUNSTOP(0x1)（写 CR=0 是保持 halted，不能当启动！）
     *    然后轮询 SR.HALTED==0（超时 100 ms 量纲）；错误位必须为 0。 */
    /* v25 kick-off：CR 清控制位并置 RS，然后**再写一次 VSIZE**（驱动 direct 模式语义） */
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);
    rv &= ~S5_CAM_CR_CLEAR_START_MASK;
    rv |= S5_CAM_CR_RUNSTOP;
    vdstep(tr, "CR(0x30)<=(RS=1|clear tail/sync/frmcnt/rdptr)", S5_CAM_S2MM_CR, rv,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR), 0u, 0);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, rv);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, (uint32_t)S5_CAM_VSIZE); /* kick off */
    vdstep(tr, "VSIZE(0xA0) kick-off", S5_CAM_S2MM_VSIZE, (uint32_t)S5_CAM_VSIZE,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE), (uint32_t)S5_CAM_VSIZE, 1);
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 0, &sr) != 0) {
        vdstep(tr, "SR(0x34)", S5_CAM_S2MM_SR, 0u, sr, 0u, 0);
        vdstep(tr, "SR.HALTED==0", S5_CAM_S2MM_SR, 0u, (sr & S5_CAM_SR_HALTED), 0u, 1);
        return -4;
    }
    vdstep(tr, "SR(0x34) after RUNSTOP", S5_CAM_S2MM_SR, 0u, sr, 0u, 0);
    vdstep(tr, "SR.HALTED==0", S5_CAM_S2MM_SR, 0u, (sr & S5_CAM_SR_HALTED), 0u, 1);
    vdstep(tr, "SR.ERR_ALL==0", S5_CAM_S2MM_SR, 0u, (sr & S5_CAM_SR_ERR_ALL), 0u, 1);
    if ((sr & S5_CAM_SR_ERR_ALL) != 0u) {
        /* 错误位展开打印：0x10 internal / 0x20 slave / 0x40 decode /
         * 0x80 FSizeLess / 0x100 LSizeLess / 0x800 FSizeMore */
        vdstep(tr, "SR.ERR_INTERNAL(0x10)", S5_CAM_S2MM_SR, 0u, (sr & 0x10u), 0u, 1);
        vdstep(tr, "SR.ERR_SLAVE(0x20)", S5_CAM_S2MM_SR, 0u, (sr & 0x20u), 0u, 1);
        vdstep(tr, "SR.ERR_DECODE(0x40)", S5_CAM_S2MM_SR, 0u, (sr & 0x40u), 0u, 1);
        vdstep(tr, "SR.ERR_FSIZE_LESS(0x80)", S5_CAM_S2MM_SR, 0u, (sr & 0x80u), 0u, 1);
        vdstep(tr, "SR.ERR_LSIZE_LESS(0x100)", S5_CAM_S2MM_SR, 0u, (sr & 0x100u), 0u, 1);
        vdstep(tr, "SR.ERR_FSIZE_MORE(0x800)", S5_CAM_S2MM_SR, 0u, (sr & 0x800u), 0u, 1);
        return -4;
    }

    info->vsreg = S5_CAM_S2MM_VSIZE;
    info->hsreg = S5_CAM_S2MM_HSIZE;
    info->strreg = S5_CAM_S2MM_STRIDE;
    info->vdma_sr = sr;
    return 0;
}

int S5CamVdma_Init(const S5CamBus *bus, S5CamInfo *info)
{
    return S5CamVdma_Config(bus, info, 0);
}

uint32_t S5Cam_SrErrors(uint32_t sr)
{
    return sr & S5_CAM_SR_ERR_ALL;
}

/* 换一套几何重配：reset → 等 HALTED=1 → 写 VSIZE/HSIZE/STRIDE/FRMPTR1 → RUNSTOP → 等 HALTED=0
 * （诊断用；返回 0 且 sr_out=最新 SR，超时返回 -4 并给出 SR） */
/* 配置一组几何并启动，保持运行（供观察循环使用；结束不要写 CR=0） */
int S5CamVdma_StartGeometry(const S5CamBus *bus, uint32_t vsize, uint32_t hsize, uint32_t stride,
                            uint32_t *sr_out)
{
    uint32_t sr = 0u;

    if ((bus == 0) || (sr_out == 0)) {
        return -1;
    }
    /* reset 流程：RESET=1 → 等 HALTED=1 → 配几何 → RUNSTOP → 等 HALTED=0 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, S5_CAM_CR_RESET);
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 1, &sr) != 0) {
        *sr_out = sr;
        return -4;
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vsize);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE, hsize);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE, stride);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE);
    {
        uint32_t cr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);

        cr &= ~S5_CAM_CR_CLEAR_START_MASK;
        cr |= S5_CAM_CR_RUNSTOP;
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, cr);
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vsize); /* kick off */
    }
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 0, &sr) != 0) {
        *sr_out = sr;
        return -4;
    }
    *sr_out = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    return 0;
}

int S5CamVdma_Probe(const S5CamBus *bus, uint32_t vsize, uint32_t hsize, uint32_t stride,
                    uint32_t *sr_out, S5CamVdmaTrace *tr)
{
    uint32_t sr = 0u, rv;

    if ((bus == 0) || (sr_out == 0)) {
        return -1;
    }
    if (tr != 0) {
        tr->n = 0u;
        tr->first_bad = -1;
        tr->cand = 0xFFFFFFFFu;
        tr->base = S5_CAM_VDMA_BASE;
    }

    /* 1) 停 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0u);
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 1, &sr) != 0) {
        vdstep(tr, "CR=0 -> HALTED=1 timeout", S5_CAM_S2MM_CR, 0u, sr, 0u, 0);
        *sr_out = sr;
        return -4;
    }
    vdstep(tr, "CR(0x30)=0", S5_CAM_S2MM_CR, 0u, cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR), 0u, 0);

    /* 2) W1C 清 SR 并确认残留 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR, 0xFFFFFFFFu);
    rv = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    vdstep(tr, "SR W1C 0xFFFFFFFF", S5_CAM_S2MM_SR, 0xFFFFFFFFu, rv, 0u, 0);

    /* 3) 配几何 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vsize);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE, hsize);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE, stride);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE);
    vdstep(tr, "VSIZE", S5_CAM_S2MM_VSIZE, vsize,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE), vsize, 1);
    vdstep(tr, "HSIZE", S5_CAM_S2MM_HSIZE, hsize,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE), hsize, 1);
    vdstep(tr, "STRIDE", S5_CAM_S2MM_STRIDE, stride,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE), stride, 1);
    vdstep(tr, "FRMPTR1", S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0), S5_CAM_RAW_BASE, 1);

    /* 4) 启动并等 HALTED=0 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_FRMSTORE, 1u);
    {
        uint32_t cr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);

        cr &= ~S5_CAM_CR_CLEAR_START_MASK;
        cr |= S5_CAM_CR_RUNSTOP;
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, cr);
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vsize);
    }
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 0, &sr) != 0) {
        vdstep(tr, "CR=1 -> HALTED=0 timeout", S5_CAM_S2MM_CR, S5_CAM_CR_RUNSTOP, sr, 0u, 0);
        *sr_out = sr;
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0u);
        return -4;
    }

    /* 5) 等 250ms 后读 SR/FRMCNT */
    cam_delay_us(bus, 250000u);
    *sr_out = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);

    /* 6) 结束前停 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0u);
    (void)camv_poll_sr(bus, S5_CAM_SR_HALTED, 1, &sr);
    return 0;
}

int S5CamVdma_Reconfig(const S5CamBus *bus, uint32_t vsize, uint32_t hsize, uint32_t stride,
                       S5CamVdmaTrace *tr, uint32_t *sr_out)
{
    uint32_t sr = 0u;
    int rc;

    if ((bus == 0) || (sr_out == 0)) {
        return -1;
    }
    if (tr != 0) {
        tr->n = 0u;
        tr->first_bad = -1;
        tr->cand = 0xFFFFFFFFu;
        tr->base = S5_CAM_VDMA_BASE;
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, S5_CAM_CR_RESET);
    if (camv_poll_sr(bus, S5_CAM_SR_HALTED, 1, &sr) != 0) {
        vdstep(tr, "CR.RESET -> HALTED=1 timeout", S5_CAM_S2MM_CR, S5_CAM_CR_RESET, sr, 0u, 0);
        *sr_out = sr;
        return -4;
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vsize);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE, hsize);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE, stride);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE);
    vdstep(tr, "VSIZE", S5_CAM_S2MM_VSIZE, vsize,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE), vsize, 1);
    vdstep(tr, "HSIZE", S5_CAM_S2MM_HSIZE, hsize,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE), hsize, 1);
    vdstep(tr, "STRIDE", S5_CAM_S2MM_STRIDE, stride,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE), stride, 1);
    vdstep(tr, "FRMPTR1", S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE,
           cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0), S5_CAM_RAW_BASE, 1);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_FRMSTORE, 1u);
    {
        uint32_t cr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);

        cr &= ~S5_CAM_CR_CLEAR_START_MASK;
        cr |= S5_CAM_CR_RUNSTOP;
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, cr);
        cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vsize);
    }
    rc = camv_poll_sr(bus, S5_CAM_SR_HALTED, 0, &sr);
    *sr_out = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0u); /* 停 */
    return (rc == 0) ? 0 : -4;
}

int S5CamVdma_Start(const S5CamBus *bus)
{
    if (bus == 0) {
        return -1;
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_FRMSTORE, 1u);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, S5_CAM_S2MM_CR_START);
    return 0;
}

int S5CamVdma_Stop(const S5CamBus *bus)
{
    if (bus == 0) {
        return -1;
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0u);
    return 0;
}

int S5CamVdma_Status(const S5CamBus *bus, uint32_t *sr)
{
    uint32_t v;

    if ((bus == 0) || (sr == 0)) {
        return -1;
    }
    v = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    *sr = v;
    return (((v & S5_CAM_SR_ERR_ALL) != 0u) ? -2 : 0);
}

/* v33：清 S2MM SR（W1C 0x7F0），返回清前/清后值 */
int S5Cam_VdmaClearSr(const S5CamBus *bus, uint32_t *sr_before, uint32_t *sr_after)
{
    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0) || (sr_before == 0) || (sr_after == 0)) {
        return -1;
    }
    *sr_before = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR, 0x7F0u);
    cam_delay_us(bus, 1000u);
    *sr_after = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    return 0;
}

/* v31：无 RESET 的 VDMA 启动（b11h 几何 1280x720/3840）
 * 1) CR=0 清 RESET，读回要求 (cr&4)==0
 * 2) 配 VSIZE/HSIZE/STRIDE/FRMPTR1
 * 3) CR=1（只 RS），读回要求 (cr&1)==1 且 (cr&4)==0
 * 4) kick：再写 VSIZE —— 全程不写 RESET、不调用 StartGeometry */
static int s5_vdma_start_nors(const S5CamBus *bus, uint32_t vs, uint32_t hs, uint32_t st)
{
    uint32_t cr;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0u);
    cam_delay_us(bus, 1000u);
    cr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);
    if ((cr & 0x4u) != 0u) {
        return -21; /* RESET 清不掉 */
    }
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, vs);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE, hs);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE, st);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, 0x1u);
    cam_delay_us(bus, 10000u); /* v33：RS 后等 10 ms，只读回读，不再写 VSIZE */
    cr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR);
    if (((cr & 0x1u) == 0u) || ((cr & 0x4u) != 0u)) {
        return -22; /* RS 未置或 RESET 被重新置位 */
    }
    return 0;
}

int S5Cam_Init(const S5CamBus *bus, uint32_t cpu_hz, S5CamInfo *info)
{
    int rc;

    if ((bus == 0) || (info == 0)) {
        return -1;
    }
    info->chip_id = 0u;
    info->frames = 0u;
    rc = S5Cam_ResetSeq(bus, 0, 0);
    if (rc != 0) {
        return -16;
    }
    rc = S5Cam_I2cInit(bus, cpu_hz);
    if (rc != 0) {
        return rc;
    }
    rc = S5Cam_Probe(bus, &info->chip_id);
    if (rc != 0) {
        return (rc == -3) ? -10 : -11;
    }
    rc = S5Cam_ApplyInitTable(bus); /* 阶段3 完整表 */
    if (rc != 0) {
        return -17;
    }
    rc = S5Cam_ApplyVga(bus);
    if (rc != 0) {
        return -12;
    }
    rc = S5Cam_VerifyVga(bus, info);
    if (rc != 0) {
        return -13;
    }
    rc = S5Cam_StreamOff(bus); /* v15：改时序前先停流 */
    if (rc != 0) {
        return -19;
    }
    rc = S5Cam_ApplyTiming(bus); /* 时序敏感覆盖重写（顺序敏感） */
    if (rc != 0) {
        return -20;
    }
    rc = S5Cam_StreamOn(bus);
    if (rc != 0) {
        return -18;
    }
    /* v18：厂商 IP 上电等待（reset_cnt 200M + fifo_ready_cnt 100M PCLK ≈ 3.6 s@84MHz）
     * 必须等够再配/启 VDMA，否则 FIFO 未就绪、无 wr_en、S2MM 无数据。 */
    S5Cam_StreamOnMs = (bus->now_ms != 0) ? bus->now_ms() : 0u;
    cam_delay_us(bus, (uint32_t)S5_CAM_IP_WARMUP_MS * 1000u);
    S5Cam_WarmupMs = (bus->now_ms != 0) ? (bus->now_ms() - S5Cam_StreamOnMs)
                                        : (uint32_t)S5_CAM_IP_WARMUP_MS;
    info->vdma_sr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    rc = s5_vdma_start_nors(bus, (uint32_t)S5_CAM_VDMA_VSIZE, (uint32_t)S5_CAM_HSIZE,
                            (uint32_t)S5_CAM_STRIDE);
    if (rc != 0) {
        return rc; /* -21 清 RESET 失败 / -22 RS 未置 */
    }
    info->vsreg = S5_CAM_S2MM_VSIZE;
    info->hsreg = S5_CAM_S2MM_HSIZE;
    info->strreg = S5_CAM_S2MM_STRIDE;
    return 0;
}