/*
 * vtc_ctrl.h —— 阶段5 P3b-sw：v_tc 6.2 生成器（generation-only）寄存器级初始化 + 回读校验
 *
 * 依据（本机可复核，不是猜的）：
 *   1) 寄存器偏移：D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\vtc_v8_8\src\xvtc_hw.h
 *        XVTC_CTL_OFFSET 0x000、XVTC_ISR_OFFSET 0x004、XVTC_ERROR_OFFSET 0x008、
 *        XVTC_IER_OFFSET 0x00C、XVTC_VER_OFFSET 0x010、
 *        XVTC_GASIZE_OFFSET 0x060、XVTC_GFENC_OFFSET 0x068、XVTC_GPOL_OFFSET 0x06C、
 *        XVTC_GHSIZE_OFFSET 0x070、XVTC_GVSIZE_OFFSET 0x074、XVTC_GHSYNC_OFFSET 0x078、
 *        XVTC_GVBHOFF_OFFSET 0x07C、XVTC_GVSYNC_OFFSET 0x080、XVTC_GVSHOFF_OFFSET 0x084、
 *        XVTC_GVSYNC_F1_OFFSET 0x08C、XVTC_GASIZE_F1_OFFSET 0x094
 *      字段位域：SB_START 0x3FFF / SB_END 0x3FFF0000(<<16)（同步 start/end）、
 *                ASIZE_HORI 0x3FFF / ASIZE_VERT 0x3FFF0000(<<16)（有效尺寸）、
 *                VSIZE_F0 0x3FFF / VSIZE_F1 0x3FFF0000(<<16)（场总行数）、
 *                POL_*（FIP/ACP/AVP/HSP/VSP/HBP/VBP）、ENC_PROG(bit6，1=隔行)、
 *                CTL：bit0 SW(VTC 使能)、bit1 RU、bit2 GE(生成器使能)、bit31 RESET
 *   2) 写序列：同目录 xvtc.c 的 XVtc_SetGenerator() / XVtc_SetPolarity() /
 *      XVtc_SetSkipLine() / XVtc_Reset() / XVtc_Enable() / XVtc_EnableGenerator()
 *   3) 720p60 几何：lead 2026-10-30 给定
 *        H: total 1650 / sync 40 / back 220 / active 1280（→ 前肩 110，同步 1390..1430）
 *        V: total 750  / sync 5  / back 20  / active 720 （→ 前肩 5，同步 725..730）
 *   4) 与 P3a BD 预设对照：bd_p3a.bd 的 vtc_0 参数
 *        GEN_HACTIVE_SIZE=1280、GEN_HFRAME_SIZE=1650、GEN_HSYNC_START/END=1390/1430、
 *        GEN_VACTIVE_SIZE=720、GEN_F0_VFRAME_SIZE=750、GEN_F0_VSYNC_VSTART/VEND=724/729
 *      **垂直同步端比几何值小 1**，原因是 v_tc 驱动的寄存器编码是
 *      `GVSYNC = (V0SyncStart + vactive - 1)`（见 XVtc_SetGenerator 源码），
 *      水平侧则是 `HSyncStart + hactive`（无 -1）。默认按 IP 预设编码（有 BD 证据），
 *      用 S5_VTC_VSYNC_USE_IP_PRESET 宏可切回几何原值，上板差 1 行时改这里。
 *
 * 边界：本模块只写生成器时序/极性/编码 + 使能，不碰检测器（enable_detection=false）、
 *       不碰中断（HAS_INTC_IF=false），也**不假设**已综合实现行为 —— 全部离线推导，
 *       未上板验证（见报告 §6）。
 */
#ifndef VTC_CTRL_H
#define VTC_CTRL_H

#include <stdint.h>

/* P3a/P3b 冻结地址：VTC AXI-Lite 基址 */
#define S5_VTC_BASE 0x43C30000u

/* v_tc 寄存器偏移（相对基址），来源见文件头 */
#define S5_VTC_CTL        0x000u
#define S5_VTC_ISR        0x004u
#define S5_VTC_ERROR      0x008u
#define S5_VTC_IER        0x00Cu
#define S5_VTC_VER        0x010u
#define S5_VTC_GASIZE     0x060u /* [13:0] 行有效像素, [29:16] 场有效行 */
#define S5_VTC_GFENC      0x068u /* bit6 PROG(1=隔行), bit0/8/9 chroma 跳过位 */
#define S5_VTC_GPOL       0x06Cu /* 极性：FIP/ACP/AVP/HSP/VSP/HBP/VBP */
#define S5_VTC_GHSIZE     0x070u /* [13:0] 行总周期 */
#define S5_VTC_GVSIZE     0x074u /* [13:0] 场 0 总行数, [29:16] 场 1 总行数 */
#define S5_VTC_GHSYNC     0x078u /* [13:0] 行同步起点, [29:16] 行同步终点 */
#define S5_VTC_GVBHOFF    0x07Cu /* 场消隐的水平起/止 */
#define S5_VTC_GVSYNC     0x080u /* [13:0] 场同步起点, [29:16] 场同步终点 */
#define S5_VTC_GVSHOFF    0x084u /* 场同步的水平起/止 */
#define S5_VTC_GVSYNC_F1  0x08Cu /* 场 1 场同步（逐行扫描填同值） */
#define S5_VTC_GASIZE_F1  0x094u /* 场 1 有效尺寸 */

#define S5_VTC_CTL_SW     0x00000001u /* VTC 核使能 */
#define S5_VTC_CTL_RU     0x00000002u /* 寄存器更新 */
#define S5_VTC_CTL_GE     0x00000004u /* 生成器使能 */
#define S5_VTC_CTL_RESET  0x80000000u /* 软复位（自清） */

#define S5_VTC_SB_START_MASK 0x00003FFFu
#define S5_VTC_SB_END_MASK   0x3FFF0000u
#define S5_VTC_SB_END_SHIFT  16u
#define S5_VTC_ASIZE_HORI_MASK 0x00003FFFu
#define S5_VTC_ASIZE_VERT_MASK 0x3FFF0000u
#define S5_VTC_ASIZE_VERT_SHIFT 16u
#define S5_VTC_VSIZE_F0_MASK 0x00003FFFu
#define S5_VTC_VSIZE_F1_MASK 0x3FFF0000u
#define S5_VTC_VSIZE_F1_SHIFT 16u

#define S5_VTC_POL_ACP 0x00000020u
#define S5_VTC_POL_AVP 0x00000010u
#define S5_VTC_POL_HSP 0x00000008u
#define S5_VTC_POL_VSP 0x00000004u
#define S5_VTC_POL_HBP 0x00000002u
#define S5_VTC_POL_VBP 0x00000001u
#define S5_VTC_POL_ALL_HIGH (S5_VTC_POL_ACP | S5_VTC_POL_AVP | S5_VTC_POL_HSP | \
                             S5_VTC_POL_VSP | S5_VTC_POL_HBP | S5_VTC_POL_VBP)

#define S5_VTC_ENC_PROG_MASK  0x00000040u
#define S5_VTC_ENC_PROG_SHIFT 6u

/* v_tc 的 GVSYNC 是否按 IP 预设编码（= 几何值 - 1，见文件头 §4）。
 * 默认 1：与 P3a BD 的 GEN_F0_VSYNC_VSTART/VEND=724/729 一致；上板差 1 行时改 0。 */
#ifndef S5_VTC_VSYNC_USE_IP_PRESET
#define S5_VTC_VSYNC_USE_IP_PRESET 1
#endif

/* 校验项上限：11 个时序/极性寄存器 + 1 个 CTL */
#define S5_VTC_MAX_CHK 12u

/* 720p60 几何参数（lead 2026-10-30 给定；前肩由 total 反算） */
typedef struct S5VtcTiming {
    uint32_t h_active;
    uint32_t h_total;
    uint32_t h_sync_width;
    uint32_t h_back_porch;
    uint32_t v_active;
    uint32_t v_total;
    uint32_t v_sync_width;
    uint32_t v_back_porch;
} S5VtcTiming;

/* 一项回读校验 */
typedef struct S5VtcChk {
    const char *name; /* 寄存器名 */
    uint32_t off;     /* 偏移 */
    uint32_t want;    /* 写入值 */
    uint32_t got;     /* 回读值 */
    int ok;           /* 1=一致 */
} S5VtcChk;

typedef struct S5Vtc {
    uint32_t base;
    uint32_t version;      /* 0x010 回读（判 AXI-Lite 通路） */
    uint32_t ctl_want;     /* 期望 CTL（SW|GE） */
    uint32_t ctl_got;      /* CTL 回读 */
    S5VtcChk chk[S5_VTC_MAX_CHK];
    uint32_t n_chk;
    uint32_t fail_count;
} S5Vtc;

/* 720p60 默认几何（H 1650/40/220/1280；V 750/5/20/720） */
void S5Vtc_Default720p60(S5VtcTiming *t);

uint32_t S5Vtc_Read(const S5Vtc *vtc, uint32_t off);
void S5Vtc_Write(S5Vtc *vtc, uint32_t off, uint32_t val);

/* 软复位：CTL.RESET=1 → 轮询自清；0=成功，-1=超时。 */
int S5Vtc_Reset(S5Vtc *vtc, uint32_t timeout_us);

/* 只写生成器寄存器（不使能），并把期望值记进 chk[]。 */
int S5Vtc_Program(S5Vtc *vtc, const S5VtcTiming *t);

/* 只回读校验（可单独调用，用于上板运行时再验一次）。返回失败项数（0=全通过）。 */
uint32_t S5Vtc_Verify(S5Vtc *vtc);

/* 一步到位：判活 → 复位 → 编程 → 使能(SW|GE) → 回读校验。
 * 返回 0=成功；-1=复位超时；-2=版本寄存器无效（AXI-Lite 不通/IP 未出复位）；
 *      -3=回读校验失败（fail_count>0，不静默）。 */
int S5Vtc_Init(S5Vtc *vtc, const S5VtcTiming *t, uint32_t timeout_us);

/* 人可读文本（不依赖 printf；返回写入长度，含结尾 0）。
 * 例："GHSIZE   @43C30070 want=00000672 got=00000672 OK" */
uint32_t S5Vtc_FormatCheck(const S5Vtc *vtc, uint32_t idx, char *buf, uint32_t cap);
/* 例："VTC verify: 12/12 OK" 或 "VTC verify: 11/12 FAIL(1)" */
uint32_t S5Vtc_FormatSummary(const S5Vtc *vtc, char *buf, uint32_t cap);
/* 例："VTC timing 1280x720@60 Htotal=1650 Hsync=1390..1430 Vtotal=750 Vsync=724..729" */
uint32_t S5Vtc_FormatTiming(const S5Vtc *vtc, char *buf, uint32_t cap);

#endif /* VTC_CTRL_H */