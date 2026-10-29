/*
 * vdma_ctrl.c —— axi_vdma 6.3（仅 MM2S、非 SG）寄存器级初始化/启动/状态查询
 *
 * 依据全部来自本机可查的官方源码，不猜寄存器：
 *   D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_17\src\
 *     · xaxivdma_hw.h      —— 偏移/位域常量
 *     · xaxivdma_channel.c —— 非 SG 写序列（SetBufferAddr / DmaSetup / ChannelStart / ChannelReset）
 * 逐条映射见 vdma_ctrl.h 文件头。
 *
 * 说明：本文件**不使用** axivdma 驱动库，也不依赖 BSP 里是否存在该驱动
 *       （当前 BSP 的 DRVLIST 未包含 axivdma），因此全部用 Xil_In32/Xil_Out32 直写。
 */
#include "vdma_ctrl.h"

#include "s5_timebase.h"
#include "xil_io.h"

/* 内存序：AXI-Lite 写后需要保证后续读/写不被编译器/Cortex-A9 重排。
 * Cortex-A9 的 Device 属性对同一外设保序，但编译器可能重排 MMIO 访问，故加编译器屏障。 */
static inline void s5_mb(void)
{
#if defined(__GNUC__) && !defined(S5_HOST_TEST)
    __asm__ __volatile__("dsb" ::: "memory");
#endif
}

uint32_t S5Vdma_Read(const S5Vdma *dma, uint32_t off)
{
    return Xil_In32(dma->base + off);
}

void S5Vdma_Write(S5Vdma *dma, uint32_t off, uint32_t val)
{
    Xil_Out32(dma->base + off, val);
    s5_mb();
}

int S5Vdma_Reset(S5Vdma *dma, uint32_t timeout_us)
{
    uint64_t t0;
    uint32_t cr;

    /* XAxiVdma_ChannelReset()：读 CR → 置 RESET → 写回 → 等待硬件自清 */
    cr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMACR);
    S5Vdma_Write(dma, S5_VDMA_MM2S_VDMACR, cr | S5_VDMA_CR_RESET);

    t0 = S5Ticks_Now();
    for (;;) {
        cr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMACR);
        if ((cr & S5_VDMA_CR_RESET) == 0u) {
            dma->cr_last = cr;
            return 0;
        }
        if (S5Ticks_Elapsed(t0, S5Ticks_FromUs(timeout_us))) {
            dma->cr_last = cr;
            return -1; /* 复位超时：多半是 AXI-Lite 地址错误 / IP 未复位 */
        }
    }
}

int S5Vdma_ProgramAddresses(S5Vdma *dma, const uint32_t *addrs, uint32_t n)
{
    uint32_t i;

    if ((addrs == 0) || (n == 0u)) {
        return -2;
    }
    if (n > S5_VDMA_FS_MAX) {
        return -2;
    }

    for (i = 0; i < n; i++) {
        dma->fb_addr[i] = addrs[i];
        S5Vdma_Write(dma, S5_VDMA_MM2S_START_ADDR(i), addrs[i]);
    }
    dma->fs_prog = n;
    return 0;
}

int S5Vdma_Configure(S5Vdma *dma, uint32_t hsize_bytes, uint32_t vsize_lines,
                     uint32_t stride_bytes, uint32_t frame_delay)
{
    if ((hsize_bytes == 0u) || (vsize_lines == 0u) || (stride_bytes == 0u)) {
        return -2;
    }
    if (vsize_lines > 0x1FFFu) {          /* XAXIVDMA_MAX_VSIZE */
        return -2;
    }
    if (hsize_bytes > 0xFFFFu) {          /* XAXIVDMA_MAX_HSIZE */
        return -2;
    }
    if (stride_bytes > 0xFFFFu) {         /* XAXIVDMA_MAX_STRIDE */
        return -2;
    }
    if (frame_delay > 0xFu) {             /* XAXIVDMA_FRMDLY_MAX */
        return -2;
    }

    dma->hsize_bytes = hsize_bytes;
    dma->vsize_lines = vsize_lines;
    dma->stride_bytes = stride_bytes;
    dma->frame_delay = frame_delay;

    /* XAxiVdma_ChannelDmaSetup() 非 SG 分支：
     *   HSIZE(0x54) = 每行字节数
     *   STRD_FRMDLY(0x58) = (FrameDelay << 24) | Stride                                */
    S5Vdma_Write(dma, S5_VDMA_MM2S_HSIZE, hsize_bytes);
    S5Vdma_Write(dma, S5_VDMA_MM2S_STRD_FRMDLY,
                 ((frame_delay & 0xFu) << 24) | (stride_bytes & 0xFFFFu));
    return 0;
}

int S5Vdma_Start(S5Vdma *dma)
{
    uint32_t cr;
    uint32_t sr;

    /* 1) 重建 CR：只保留 RUNSTOP，清掉 TAIL_EN/SYNC/FRMCNT/RD_PTR，再按需置循环位。
     *    与 XAxiVdma_ChannelDmaSetup() 的 CR 处理一致。 */
    cr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMACR);
    cr &= S5_VDMA_CR_RUNSTOP;
    /* 循环缓冲（circular）：等价于驱动的 EnableCircularBuf=1 → CR.TAIL_EN=1，
     * 帧存按 0..N-1 自动轮转，显示侧持续有数据。 */
    cr |= S5_VDMA_CR_TAIL_EN;
    cr |= S5_VDMA_CR_RUNSTOP;
    S5Vdma_Write(dma, S5_VDMA_MM2S_VDMACR, cr);

    /* 2) 写 VSIZE 触发（非 SG 模式下这一步才真正开始搬数）。 */
    S5Vdma_Write(dma, S5_VDMA_MM2S_VSIZE, dma->vsize_lines);

    /* 3) 等 HALTED 清掉（写 VSIZE 后硬件需要几个 aclk 才退出 halted；立即读会假失败）。
     *    依据：XAXIVDMA_SR_HALTED_MASK 是状态位 bit0，驱动用 CR.RUNSTOP 判断是否在跑。 */
    {
        uint64_t t0 = S5Ticks_Now();
        uint64_t budget = S5Ticks_FromUs(5000u);

        for (;;) {
            sr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMASR);
            if ((sr & S5_VDMA_SR_HALTED) == 0u) {
                break;
            }
            if ((S5Ticks_Now() - t0) >= budget) {
                dma->cr_last = cr;
                dma->sr_last = sr;
                return -3; /* 一直 halted：IP 未出复位 / 像素时钟未到 / AXI-Lite 地址错 */
            }
        }
    }

    dma->cr_last = cr;
    dma->sr_last = sr;
    return 0;
}

int S5Vdma_Stop(S5Vdma *dma)
{
    uint64_t t0;
    uint32_t cr;

    cr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMACR);
    S5Vdma_Write(dma, S5_VDMA_MM2S_VDMACR, cr & ~S5_VDMA_CR_RUNSTOP);

    t0 = S5Ticks_Now();
    for (;;) {
        cr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMACR);
        if ((cr & S5_VDMA_CR_RUNSTOP) == 0u) {
            dma->cr_last = cr;
            return 0;
        }
        if (S5Ticks_Elapsed(t0, S5Ticks_FromUs(10000u))) {
            return -1;
        }
    }
}

int S5Vdma_Init(S5Vdma *dma, const uint32_t *addrs, uint32_t n,
                uint32_t hsize_bytes, uint32_t vsize_lines)
{
    int rc;

    if (dma == 0) {
        return -9;
    }

    dma->base = S5_VDMA_BASE;
    dma->fs_prog = 0;
    dma->version = 0;
    dma->cr_last = 0;
    dma->sr_last = 0;

    /* 0) 先读版本，确认 AXI-Lite 通路活着（全 1/全 0 基本可判为无 IP）。 */
    dma->version = S5Vdma_Read(dma, S5_VDMA_VERSION);
    if ((dma->version == 0u) || (dma->version == 0xFFFFFFFFu)) {
        return -4;
    }

    /* 1) 复位 */
    rc = S5Vdma_Reset(dma, 10000u);
    if (rc != 0) {
        return -1;
    }

    /* 2) 帧存地址（先写地址，再配尺寸，最后启动） */
    rc = S5Vdma_ProgramAddresses(dma, addrs, n);
    if (rc != 0) {
        return -2;
    }

    /* 3) 尺寸：stride 与 hsize 相同（画布无补边） */
    rc = S5Vdma_Configure(dma, hsize_bytes, vsize_lines, hsize_bytes, 0u);
    if (rc != 0) {
        return -2;
    }

    /* 4) 记录 0x18 FRMSTORE 读回（**只读**，见头文件说明） */
    dma->fs_hw_readback = S5Vdma_Read(dma, S5_VDMA_MM2S_FRMSTORE) & 0x3Fu;

    /* 5) 循环模式启动 */
    rc = S5Vdma_Start(dma);
    if (rc != 0) {
        return rc;
    }
    return 0;
}

uint32_t S5Vdma_Status(S5Vdma *dma)
{
    dma->sr_last = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMASR);
    return dma->sr_last;
}

uint32_t S5Vdma_Version(S5Vdma *dma)
{
    return S5Vdma_Read(dma, S5_VDMA_VERSION);
}

uint32_t S5Vdma_CurrentReadStore(S5Vdma *dma)
{
    uint32_t park = S5Vdma_Read(dma, S5_VDMA_PARKPTR);
    return (park & S5_VDMA_PARK_READSTR_MASK) >> S5_VDMA_PARK_READSTR_SHIFT;
}

uint32_t S5Vdma_CurrentReadAddr(S5Vdma *dma)
{
    uint32_t idx;

    if (dma->fs_prog == 0u) {
        return 0u;
    }
    idx = S5Vdma_CurrentReadStore(dma);
    if (idx >= dma->fs_prog) {
        return 0u; /* 索引超出 SW 已知表：无法判定，交由调用方按“不安全”处理 */
    }
    return dma->fb_addr[idx];
}

int S5Vdma_WaitNotReading(S5Vdma *dma, uint32_t addr, uint32_t timeout_us)
{
    uint64_t t0 = S5Ticks_Now();
    uint64_t budget = S5Ticks_FromUs(timeout_us);

    for (;;) {
        uint32_t sr = S5Vdma_Read(dma, S5_VDMA_MM2S_VDMASR);

        /* 没在跑（复位后/停住）就没有读写冲突 */
        if ((sr & S5_VDMA_SR_HALTED) != 0u) {
            return 0;
        }

        if (S5Vdma_CurrentReadAddr(dma) != addr) {
            return 0;
        }

        if ((S5Ticks_Now() - t0) >= budget) {
            return -1; /* 超时：VDMA 一直在读这个缓冲，继续写会撕裂 */
        }
    }
}

void S5Vdma_DecodeVersion(uint32_t ver, uint32_t *major, uint32_t *minor, uint32_t *rev)
{
    if (major != 0) {
        *major = (ver >> S5_VDMA_VER_MAJOR_SHIFT) & 0xFu;
    }
    if (minor != 0) {
        *minor = (ver >> S5_VDMA_VER_MINOR_SHIFT) & 0xFFu;
    }
    if (rev != 0) {
        *rev = (ver >> S5_VDMA_VER_REV_SHIFT) & 0xFu;
    }
}