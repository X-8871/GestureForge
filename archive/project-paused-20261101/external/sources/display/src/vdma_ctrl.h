/*
 * vdma_ctrl.h —— 阶段5 P3b-sw：axi_vdma 6.3（仅 MM2S、非 SG）寄存器级控制
 *
 * 只做显示读通路（MM2S：DDR → AXI4-Stream → v_axi4s_vid_out），不碰 S2MM，不用驱动库。
 *
 * 寄存器偏移的**依据**（不是猜的，见 S5_P3B_SW_REPORT.md §2）：
 *   1) AMD 随 Vitis 2026.1 提供的驱动源码
 *      D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\axivdma_v6_17\src\xaxivdma_hw.h
 *      —— 该驱动支持 axi_vdma 6.x，头文件即官方寄存器映射：
 *          XAXIVDMA_TX_OFFSET         0x00   ← MM2S 通道基址（相对 IP 基址）
 *          XAXIVDMA_CR_OFFSET         0x00   XAXIVDMA_SR_OFFSET        0x04
 *          XAXIVDMA_CDESC_OFFSET      0x08   XAXIVDMA_TDESC_OFFSET     0x10
 *          XAXIVDMA_HI_FRMBUF_OFFSET  0x14   XAXIVDMA_FRMSTORE_OFFSET  0x18
 *          XAXIVDMA_PARKPTR_OFFSET    0x28   XAXIVDMA_VERSION_OFFSET   0x2C
 *          XAXIVDMA_MM2S_ADDR_OFFSET  0x50   ← 非 SG（direct register）帧存寄存器块
 *          XAXIVDMA_VSIZE_OFFSET      0x00（相对 0x50 → 0x50）
 *          XAXIVDMA_HSIZE_OFFSET      0x04（→ 0x54）
 *          XAXIVDMA_STRD_FRMDLY_OFFSET 0x08（→ 0x58，FRMDLY 在 bit[27:24]，STRIDE 在 bit[15:0]）
 *          XAXIVDMA_START_ADDR_OFFSET 0x0C（→ 0x5C，每帧存 +4 字节，32 位地址）
 *   2) 同一驱动的**非 SG 写序列**实现：
 *      xaxivdma_channel.c: XAxiVdma_ChannelSetBufferAddr()（写 0x5C+4*i）
 *                          XAxiVdma_ChannelDmaSetup()    （写 0x54/0x58，重建 CR）
 *                          XAxiVdma_ChannelStart()       （CR.RUNSTOP=1，随后写 0x50 VSIZE 启动）
 *   3) P3a BD 实参（report/evidence/S5-T01/s5_p3a_video_bd_20261030_r01/bd_p3a.bd）：
 *      c_include_sg=0、c_m_axi_mm2s_data_width=64、c_m_axis_mm2s_tdata_width=32、c_addr_width=32。
 *
 * 与题面里待核对的写法对照（题面自己标注了“不确定”）：
 *   · 题面猜 “MM2S_SA=0x5C / MM2S_LENGTH=0x58” —— **0x58 不是 LENGTH**，
 *     而是 STRIDE/FRMDLY；非 SG 模式没有 LENGTH 寄存器（那是 AXI DMA 的语义）。
 *     长度由 VSIZE(0x50) × HSIZE(0x54) 隐式给出，写 VSIZE 即启动一帧序列。
 *   · 题面猜 “MM2S_VDMACR 在 0x30、SR 在 0x34” —— 那是 **S2MM** 通道；
 *     MM2S 的 CR/SR 在 0x00/0x04（本设计只开 MM2S）。
 *
 * 未验证项（务必看报告 §6）：0x18 FRMSTORE 是否可写取决于 IP 的调试参数
 * （驱动里由 XAXIVDMA_ENABLE_DBG_FRMSTORE_REG 把关）；P3a BD 未显式设置 c_num_fstores，
 * IP 目录默认 3 帧存。本模块**不写** 0x18，只读回记录，并把所有帧存地址都填成有效值。
 */
#ifndef VDMA_CTRL_H
#define VDMA_CTRL_H

#include <stdint.h>

/* VDMA AXI-Lite 基址（编译期可配）：
 *   P3q（集成体，默认；P2d 计算占 0x43C00000/0x43C10000/0x43C20000）= 0x43C40000
 *   P3n（显示独立体）= 0x43C00000 → -DS5_VDMA_BASE=0x43C00000u
 *   P3b（旧架构）    = 0x43C40000（+ -DS5_NO_VTC=0） */
#ifndef S5_VDMA_BASE
#define S5_VDMA_BASE 0x43C40000u
#endif

/* P3p：fsync 从模式（axis_to_video.vs 驱动 mm2s_fsync）。
 * S5_VDMA_FSYNC=1 → CR 置 SYNC_EN(bit3)、FSYNC_SRC=0（外部 fsync）、GENLCK_RPT(bit15)，
 * 等价于驱动 XAxiVdma_DmaSetup(EnableSync=1, GenLock=XAXIVDMA_SLAVE, GenLockRepeat=1)
 * + XAxiVdma_FsyncSrcSelect(XAXIVDMA_CHAN_FSYNC, XAXIVDMA_MM2S)（本 BSP 无 axivdma 驱动库，
 * 故用寄存器级等价写法）。默认 0 = P3n 自由运行。 */
#ifndef S5_VDMA_FSYNC
#define S5_VDMA_FSYNC 0
#endif
#ifndef S5_VDMA_GENLOCK_REPEAT
#define S5_VDMA_GENLOCK_REPEAT 1
#endif

/* 32 位地址宽度下，一个 bank 最多 16 个帧存（0x5C..0x98，每 4 字节一个） */
#define S5_VDMA_FS_MAX 16u

/* ---- MM2S 寄存器偏移（相对 S5_VDMA_BASE），来源见文件头 ---- */
#define S5_VDMA_MM2S_VDMACR      0x00u /* 控制：bit0 RUNSTOP, bit1 TAIL_EN, bit2 RESET,
                                        * bit3 SYNC_EN, bit4 FRMCNT_EN, bit[11:8] RD_PTR */
#define S5_VDMA_MM2S_VDMASR      0x04u /* 状态：bit0 HALTED, bit1 IDLE, bit[11:4] 错误, bit[14:12] 中断 */
#define S5_VDMA_MM2S_CDESC       0x08u /* 当前描述符（SG 模式用；非 SG 保留） */
#define S5_VDMA_MM2S_TDESC       0x10u /* 尾描述符（SG 模式用） */
#define S5_VDMA_MM2S_HI_FRMBUF   0x14u /* 帧存 bank 选择（>16 帧存时才需要） */
#define S5_VDMA_MM2S_FRMSTORE    0x18u /* 帧存个数（**只在 IP 打开调试寄存器时可写**） */
#define S5_VDMA_MM2S_BUFTHRES    0x1Cu /* 行缓冲阈值（动态行缓冲配置） */
#define S5_VDMA_PARKPTR          0x28u /* Park 指针：bit[4:0] READREF, bit[12:8] WRTREF,
                                        * bit[20:16] READSTR(当前读帧存), bit[28:24] WRTSTR */
#define S5_VDMA_VERSION          0x2Cu /* 版本：bit[31:28] major, bit[27:20] minor, bit[19:16] rev */
/* 非 SG 帧存寄存器块（MM2S，相对基址 0x50） */
#define S5_VDMA_MM2S_VSIZE       0x50u /* 帧行数（写此寄存器 = 启动/重启一帧） */
#define S5_VDMA_MM2S_HSIZE       0x54u /* 每行字节数 */
#define S5_VDMA_MM2S_STRD_FRMDLY 0x58u /* bit[15:0] STRIDE 字节, bit[27:24] FRMDLY 帧 */
#define S5_VDMA_MM2S_START_ADDR(i) (0x5Cu + 4u * (uint32_t)(i)) /* 帧存 i 起始地址 */
#define S5_VDMA_VFLIP            0xECu /* 垂直翻转（S2MM 用，本设计不用） */

/* ---- 控制位 ---- */
#define S5_VDMA_CR_RUNSTOP  0x00000001u
#define S5_VDMA_CR_TAIL_EN  0x00000002u /* 循环缓冲（SG 用尾指针；非 SG 置位表示 Circular 模式） */
#define S5_VDMA_CR_RESET    0x00000004u
/* P3p fsync 位（axivdma_v6_17/src/xaxivdma_hw.h）：
 *   CR_SYNC_EN 0x8、CR_FSYNC_SRC 0x60（bit[6:5]，0=channel fsync/外部 vs）、CR_GENLCK_RPT 0x8000 */
#define S5_VDMA_CR_SYNC_EN      0x00000008u
#define S5_VDMA_CR_FSYNC_SRC_MASK 0x00000060u
#define S5_VDMA_CR_GENLCK_RPT   0x00008000u
#define S5_VDMA_CR_RD_PTR_MASK 0x00000F00u
#define S5_VDMA_CR_RD_PTR_SHIFT 8u

/* ⚠ 关于“帧计数”（r05 结论，**不要再用 SR[23:16]**）：
 *   查本机 axivdma_v6_17 驱动源码后确认：
 *     · SR（0x04）只定义到 bit14（HALTED/IDLE/ERR[11:4]/IXR[14:12]），**没有帧计数字段**；
 *     · 驱动里的 XAXIVDMA_FRMCNT_MASK(0x00FF0000) 是 **CR（0x00）的 bit[23:16]**，
 *       且仅在 IP 打开调试特性时有效（XAxiVdma_ChannelGetFrmCnt 用 XAXIVDMA_ENABLE_DBG_FRM_CNTR 把关，
 *       读的也是 CR 而不是 SR）；
 *     · 那是“帧计数/延时计数”调试寄存器（配 genlock 用），**不是** MM2S 每帧递增的进度计数。
 *   因此本模块不提供硬件帧计数：`vcnt` 由上层用软件观测（PARKPTR.READSTR 变化次数）统计。
 *   板上 r04 曾读到 vcnt=1 —— 即 SR 保留位/未定义位被误当计数，现已删除该读法。 */

/* ---- 状态位 ---- */
#define S5_VDMA_SR_HALTED      0x00000001u
#define S5_VDMA_SR_IDLE        0x00000002u
#define S5_VDMA_SR_ERR_ALL     0x00000FF0u
#define S5_VDMA_SR_ERR_INTERNAL 0x00000010u
#define S5_VDMA_SR_ERR_SLAVE   0x00000020u
#define S5_VDMA_SR_ERR_DECODE  0x00000040u

/* ---- PARKPTR 字段 ---- */
#define S5_VDMA_PARK_READREF_MASK 0x0000001Fu
#define S5_VDMA_PARK_READSTR_MASK 0x001F0000u
#define S5_VDMA_PARK_READSTR_SHIFT 16u
#define S5_VDMA_PARK_WRTSTR_MASK  0x1F000000u
#define S5_VDMA_PARK_WRTSTR_SHIFT 24u

/* ---- 版本字段 ---- */
#define S5_VDMA_VER_MAJOR_SHIFT 28u
#define S5_VDMA_VER_MINOR_SHIFT 20u
#define S5_VDMA_VER_REV_SHIFT   16u

/* 控制器实例（不含任何地址空间分配，帧缓冲由调用方以物理地址给出） */
typedef struct S5Vdma {
    uint32_t base;                        /* AXI-Lite 基址，通常 S5_VDMA_BASE */
    uint32_t hsize_bytes;                 /* 每行字节数 = 宽 × 4 */
    uint32_t vsize_lines;                 /* 每帧行数 */
    uint32_t stride_bytes;                /* 行跨距（本设计 = hsize_bytes，无补边） */
    uint32_t frame_delay;                 /* FRMDLY，非 genlock 模式取 0 */
    uint32_t fb_addr[S5_VDMA_FS_MAX];     /* 已编程的帧存地址 */
    uint32_t fs_prog;                     /* 软件编程的帧存个数 */
    uint32_t fs_hw_readback;              /* 0x18 读回值（调试寄存器未开时无意义，仅记录） */
    uint32_t version;                     /* 0x2C 版本寄存器 */
    uint32_t cr_last;                     /* 最近一次写/读的 CR */
    uint32_t sr_last;                     /* 最近一次读的 SR */
} S5Vdma;

/* 寄存器读写（带内存屏障语义，见 .c） */
uint32_t S5Vdma_Read(const S5Vdma *dma, uint32_t off);
void S5Vdma_Write(S5Vdma *dma, uint32_t off, uint32_t val);

/* 复位：CR.RESET=1 → 轮询到自清；超时返回 -1。
 * 依据：XAxiVdma_ChannelReset()（xaxivdma_channel.c）写 CR.RESET 后轮询。 */
int S5Vdma_Reset(S5Vdma *dma, uint32_t timeout_us);

/* 编程帧存起始地址（0x5C + 4*i）。n 超过 S5_VDMA_FS_MAX 时返回 -2。 */
int S5Vdma_ProgramAddresses(S5Vdma *dma, const uint32_t *addrs, uint32_t n);

/* 编程 HSIZE/STRIDE/FRMDLY（非 SG 直写寄存器模式）。 */
int S5Vdma_Configure(S5Vdma *dma, uint32_t hsize_bytes, uint32_t vsize_lines,
                     uint32_t stride_bytes, uint32_t frame_delay);

/* 启动：CR 置 RUNSTOP（可选 TAIL_EN=循环），随后写 VSIZE 触发。
 * 依据：XAxiVdma_ChannelStart()（非 SG 分支注释 “Update vsize to start the channel”）。 */
int S5Vdma_Start(S5Vdma *dma);

/* 停止：CR 清 RUNSTOP。 */
int S5Vdma_Stop(S5Vdma *dma);

/* 一步到位：复位 + 配置 + 地址 + 启动。返回 0 成功，负值见 .c 注释。 */
int S5Vdma_Init(S5Vdma *dma, const uint32_t *addrs, uint32_t n,
                uint32_t hsize_bytes, uint32_t vsize_lines);

/* 状态/版本/当前读帧存查询 */
uint32_t S5Vdma_Status(S5Vdma *dma);
uint32_t S5Vdma_Version(S5Vdma *dma);
uint32_t S5Vdma_CurrentReadStore(S5Vdma *dma);

/* 当前正在被读出的 DDR 地址（由 READSTR 索引到地址表；索引越界返回 0）。 */
uint32_t S5Vdma_CurrentReadAddr(S5Vdma *dma);

/* 等待 VDMA 不再读 addr 这个缓冲（写侧安全窗口）。0=安全，-1=超时（可能撕裂）。 */
int S5Vdma_WaitNotReading(S5Vdma *dma, uint32_t addr, uint32_t timeout_us);

/* 版本寄存器解码（major/minor/rev） */
void S5Vdma_DecodeVersion(uint32_t ver, uint32_t *major, uint32_t *minor, uint32_t *rev);

/* 测量 VDMA 读帧存的切换周期 = **显示帧周期**（fps_dis 的依据）。
 * 原理：circular 模式下 VDMA 每输出一帧就切一次 READSTR；本函数轮询 READSTR，
 * 取 `edges` 个切换边沿，用相邻边沿平均间隔作为周期（ticks，S5_GT_HZ 换算成 fps）。
 * 返回 0=成功（*period_ticks > 0），-1=超时（timeout_us 内没凑够边沿/边沿不动）。 */
int S5Vdma_MeasureReadPeriod(S5Vdma *dma, uint32_t edges, uint32_t timeout_us,
                            uint64_t *period_ticks);

/* ---- 帧计数说明（r05）----
 * 本驱动不提供“每帧递增”的硬件帧计数（见文件头 ⚠ 段）：SR 无该字段，CR[23:16] 是调试用帧计数
 * （需 IP 调试特性 + genlock 语义），不能当进度计数用。
 * 上层 `vcnt` 一律用软件观测：主循环每帧读 PARKPTR.READSTR（当前读帧存号），变化次数即“VDMA 消耗帧数”
 * 的代理指标（2 帧存时每个显示帧切换一次）。 */

#endif /* VDMA_CTRL_H */