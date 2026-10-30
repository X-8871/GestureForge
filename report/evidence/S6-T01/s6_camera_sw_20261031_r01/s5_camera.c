/*
 * s5_camera.c —— R-07 / P3r：OV5640 640×480 SCCB 配置 + S2MM VDMA 控制（可选 S5_CAMERA=1）
 * 详见 s5_camera.h 顶部数据宽度结论。所有 MMIO 走 S5CamBus 函数指针，主机可注入假寄存器堆。
 */
#include "s5_camera.h"

#ifndef S5_HOST_TEST
#include "xil_io.h"
#endif

#define S5_CAM_POLL_LIMIT 2000000u /* 轮询上限（CPU 侧，非墙钟保证） */

static uint32_t cam_rd(const S5CamBus *b, uint32_t addr)
{
    return b->rd(b->ctx, addr);
}

static void cam_wr(const S5CamBus *b, uint32_t addr, uint32_t val)
{
    b->wr(b->ctx, addr, val);
}

/* ---------------- PS I2C0（polled master，Cadence 寄存器） ---------------- */

static int i2c_wait_txdv(const S5CamBus *b, uint32_t base)
{
    uint32_t n;

    for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
        if ((cam_rd(b, base + S5_I2C_SR) & S5_I2C_SR_TXDV) != 0u) {
            return 0;
        }
    }
    return -1;
}

/* 等 COMPLETE；返回 0=成功，-1=硬件错误/NACK/超时（把 ISR 读到并清掉） */
static int i2c_wait_complete(const S5CamBus *b, uint32_t base)
{
    uint32_t n;

    for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
        uint32_t isr = cam_rd(b, base + S5_I2C_ISR);

        if ((isr & (S5_I2C_ISR_ERROR | S5_I2C_ISR_NACK | S5_I2C_ISR_ARB | S5_I2C_ISR_TO)) != 0u) {
            cam_wr(b, base + S5_I2C_ISR, isr);
            return -1;
        }
        if ((isr & S5_I2C_ISR_COMP) != 0u) {
            cam_wr(b, base + S5_I2C_ISR, isr);
            return 0;
        }
    }
    return -1;
}

int S5Cam_I2cInit(const S5CamBus *bus, uint32_t cpu_hz)
{
    uint32_t base = S5_CAM_I2C_BASE;
    uint32_t div;
    uint32_t cr;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0) || (cpu_hz == 0u)) {
        return -1;
    }
    /* 100 kHz：div_a=0、div_b≈cpu/100k-1（与驱动同义）；仅作可用初值，板上按波形再调 */
    div = (cpu_hz / 100000u);
    div = (div < 2u) ? 2u : (div - 1u);
    if (div > 0x3Fu) {
        div = 0x3Fu;
    }
    cr = (S5_I2C_CR_EN | S5_I2C_CR_MS | S5_I2C_CR_NEA | (div << 8));
    cam_wr(bus, base + S5_I2C_CR, cr);
    cam_wr(bus, base + S5_I2C_TIME_OUT, 0xFFu);
    cam_wr(bus, base + S5_I2C_ISR, 0x7FFu);
    if (cam_rd(bus, base + S5_I2C_CR) != cr) {
        return -2; /* 回读不一致：I2C 控制器未响应 */
    }
    return 0;
}

int S5Cam_WriteReg(const S5CamBus *bus, uint16_t reg, uint8_t val)
{
    uint32_t base = S5_CAM_I2C_BASE;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0)) {
        return -1;
    }
    cam_wr(bus, base + S5_I2C_CR, S5_I2C_CR_EN | S5_I2C_CR_MS | S5_I2C_CR_NEA | S5_I2C_CR_CLR_FIFO);
    cam_wr(bus, base + S5_I2C_ADDR, (uint32_t)S5_CAM_SCCB_ADDR << 1);
    if (i2c_wait_txdv(bus, base) != 0) {
        return -2;
    }
    cam_wr(bus, base + S5_I2C_DATA, (reg >> 8) & 0xFFu);
    if (i2c_wait_txdv(bus, base) != 0) {
        return -2;
    }
    cam_wr(bus, base + S5_I2C_DATA, reg & 0xFFu);
    if (i2c_wait_txdv(bus, base) != 0) {
        return -2;
    }
    cam_wr(bus, base + S5_I2C_DATA, val);
    return (i2c_wait_complete(bus, base) == 0) ? 0 : -3;
}

int S5Cam_ReadReg(const S5CamBus *bus, uint16_t reg, uint8_t *val)
{
    uint32_t base = S5_CAM_I2C_BASE;

    if ((bus == 0) || (bus->rd == 0) || (bus->wr == 0) || (val == 0)) {
        return -1;
    }
    /* 写寄存器地址（HOLD 保持总线）→ 重复起始读 1 字节（SCCB 读） */
    cam_wr(bus, base + S5_I2C_CR, S5_I2C_CR_EN | S5_I2C_CR_MS | S5_I2C_CR_NEA | S5_I2C_CR_HOLD);
    cam_wr(bus, base + S5_I2C_ADDR, (uint32_t)S5_CAM_SCCB_ADDR << 1);
    if (i2c_wait_txdv(bus, base) != 0) {
        return -2;
    }
    cam_wr(bus, base + S5_I2C_DATA, (reg >> 8) & 0xFFu);
    if (i2c_wait_txdv(bus, base) != 0) {
        return -2;
    }
    cam_wr(bus, base + S5_I2C_DATA, reg & 0xFFu);
    if (i2c_wait_complete(bus, base) != 0) {
        return -3;
    }
    cam_wr(bus, base + S5_I2C_ADDR, ((uint32_t)S5_CAM_SCCB_ADDR << 1) | 1u);
    cam_wr(bus, base + S5_I2C_TRANS_SIZE, 1u);
    {
        uint32_t n;

        for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
            if ((cam_rd(bus, base + S5_I2C_SR) & S5_I2C_SR_RXDV) != 0u) {
                break;
            }
        }
        if (n >= S5_CAM_POLL_LIMIT) {
            return -4;
        }
    }
    *val = (uint8_t)(cam_rd(bus, base + S5_I2C_DATA) & 0xFFu);
    if (i2c_wait_complete(bus, base) != 0) {
        return -3;
    }
    cam_wr(bus, base + S5_I2C_CR, S5_I2C_CR_EN | S5_I2C_CR_MS | S5_I2C_CR_NEA);
    return 0;
}

/* ---------------- OV5640：CHIPID / 640×480 覆盖 / 回读 ---------------- */

int S5Cam_Probe(const S5CamBus *bus, uint16_t *chip_id)
{
    uint8_t hi = 0u;
    uint8_t lo = 0u;

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

/* 640×480 覆盖表（在阶段3 基线 720p 初始化之后写）：PCLK 84 MHz / HTS 1892 保持，
 * VTS=1480 ⇒ 30 fps；窗口 640×480；AEC 上限同步到新 VTS。 */
static const S5CamReg s5_cam_vga_tbl[] = {
    {0x3035u, 0x21u}, /* PLL：PCLK=84MHz（保持阶段3 值） */
    {0x3036u, 0x69u},
    {0x3808u, 0x02u}, /* DVPHO[15:8] */
    {0x3809u, 0x80u}, /* DVPHO[7:0] = 640 */
    {0x380Au, 0x01u}, /* DVPVO[15:8] */
    {0x380Bu, 0xE0u}, /* DVPVO[7:0] = 480 */
    {0x380Cu, 0x07u}, /* HTS[15:8] */
    {0x380Du, 0x64u}, /* HTS = 1892 */
    {0x380Eu, 0x05u}, /* VTS[15:8] */
    {0x380Fu, 0xC8u}, /* VTS = 1480 (0x05C8) */
    {0x3810u, 0x00u}, /* X offset[15:8] */
    {0x3811u, 0x00u},
    {0x3812u, 0x00u}, /* Y offset[15:8] */
    {0x3813u, 0x00u},
    {0x3814u, 0x31u}, /* X inc：保持 2x 子采样（阶段3 值） */
    {0x3815u, 0x31u}, /* Y inc */
    {0x3824u, 0x04u}, /* PCLK 手动分频（保持） */
    {0x4300u, 0x60u}, /* RGB565（保持；PL 由 16→24 converter 展开） */
    {0x3A02u, 0x05u}, /* 60Hz max exposure ≈ VTS-4 */
    {0x3A03u, 0xC4u},
    {0x3A14u, 0x05u}, /* 50Hz max exposure */
    {0x3A15u, 0xC4u},
};

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
    uint8_t h = 0u;
    uint8_t l = 0u;

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
        if ((rd.dvpho == (uint16_t)S5_CAM_W) && (rd.dvpvo == (uint16_t)S5_CAM_H) &&
            (rd.hts == 1892u) && (rd.vts == (uint16_t)S5_CAM_VTS)) {
            info->dvpho = rd.dvpho;
            info->dvpvo = rd.dvpvo;
            info->hts = rd.hts;
            info->vts = rd.vts;
            return 0;
        }
        (void)S5Cam_ApplyVga(bus); /* 回读不符：重写覆盖表后再试 */
    }
    return -2;
}

/* ---------------- S2MM VDMA（非 SG、24bpp、循环） ---------------- */

static int camv_wait_halted_clear(const S5CamBus *bus)
{
    uint32_t n;

    for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
        if ((cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR) & S5_CAM_SR_HALTED) == 0u) {
            return 0;
        }
    }
    return -1;
}

int S5CamVdma_Init(const S5CamBus *bus, S5CamInfo *info)
{
    uint32_t sr;

    if ((bus == 0) || (info == 0)) {
        return -1;
    }
    /* 复位 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, S5_CAM_CR_RESET);
    {
        uint32_t n;

        for (n = 0u; n < S5_CAM_POLL_LIMIT; n++) {
            if ((cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR) & S5_CAM_CR_RESET) == 0u) {
                break;
            }
        }
    }
    /* 地址（单帧 raw；ABI 固定 0x12000000） */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0, S5_CAM_RAW_BASE);
    /* 尺寸：24bpp → HSIZE=1920、STRIDE=1920、VSIZE=480 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE, (uint32_t)S5_CAM_STRIDE);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE, (uint32_t)S5_CAM_STRIDE);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, (uint32_t)S5_CAM_H);
    /* 回读几何（防宏/BD 不一致） */
    if (cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_HSIZE) != (uint32_t)S5_CAM_STRIDE) {
        return -4;
    }
    if (cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_STRIDE) != (uint32_t)S5_CAM_STRIDE) {
        return -4;
    }
    if (cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_ADDR0) != S5_CAM_RAW_BASE) {
        return -4;
    }
    info->vdma_sr = cam_rd(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_SR);
    (void)sr;
    return 0;
}

int S5CamVdma_Start(const S5CamBus *bus)
{
    if (bus == 0) {
        return -1;
    }
    /* 循环模式：RUNSTOP|TAIL_EN；写 VSIZE 触发搬运 */
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_CR, S5_CAM_CR_RUNSTOP | S5_CAM_CR_TAIL_EN);
    cam_wr(bus, S5_CAM_VDMA_BASE + S5_CAM_S2MM_VSIZE, (uint32_t)S5_CAM_H);
    return (camv_wait_halted_clear(bus) == 0) ? 0 : -3;
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

int S5Cam_Init(const S5CamBus *bus, uint32_t cpu_hz, S5CamInfo *info)
{
    int rc;

    if ((bus == 0) || (info == 0)) {
        return -1;
    }
    info->chip_id = 0u;
    info->frames = 0u;
    rc = S5Cam_I2cInit(bus, cpu_hz);
    if (rc != 0) {
        return rc; /* -1 参数 / -2 控制器回读失败 */
    }
    rc = S5Cam_Probe(bus, &info->chip_id);
    if (rc != 0) {
        return (rc == -3) ? -10 : -11; /* -10 CHIPID 不符 / -11 SCCB 读失败 */
    }
    rc = S5Cam_ApplyVga(bus);
    if (rc != 0) {
        return -12;
    }
    rc = S5Cam_VerifyVga(bus, info);
    if (rc != 0) {
        return -13; /* 回读校验失败（3 次） */
    }
    rc = S5CamVdma_Init(bus, info);
    if (rc != 0) {
        return -14;
    }
    rc = S5CamVdma_Start(bus);
    if (rc != 0) {
        return -15; /* S2MM 未退出 HALTED：无像素时钟/BD 地址错 */
    }
    return 0;
}