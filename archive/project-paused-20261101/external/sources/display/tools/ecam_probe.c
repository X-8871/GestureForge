/*
 * ecam_probe.c —— OCM 最小探针（R-07/相机排查用；也作长期"平台自检"）
 *
 * 设计约束（按 lead 2026-10-31 需求）：
 *  - 链接到 OCM（0x00000000 起 256 KB）：详见 tools/lscript_probe_ocm.ld，向量表在 0x0；
 *  - 运行时**不访问 DDR**（不碰 0x100000 / 0x12000000 / 0x20000000 / 0x20800000）；
 *  - 不初始化 I2C0、不碰帧存、不开中断、不用 Xilinx 驱动（仅裸 MMIO + xil_printf）；
 *  - 输出：PROBE: main / 关键地址原始值 / UART1 CR+SR / VBAR / 每 500 ms 心跳。
 *
 * 判读：
 *  - 能打印 ⇒ CPU/UART/启动流程/OCM 都正常，问题域缩到 DDR 配置或 DDR 上地址；
 *  - 静默 ⇒ 问题在 PS7/入口/时钟层面，与 DDR 无关。
 */
#include <stdint.h>

#include "xil_printf.h"
#include "xil_io.h"

/* ---- 只读探针地址（全部裸 MMIO） ---- */
#define PROBE_CAM_RST 0x41200000u  /* cmos_rst (AXI GPIO ch1 data；低有效) */
#define PROBE_GT_LO 0xF8F00200u    /* 全局定时器低 32 位 */
#define PROBE_GT_HI 0xF8F00204u    /* 全局定时器高 32 位 */
#define PROBE_2B_CSR 0x43C00000u   /* 2B CSR */
#define PROBE_DISP_VDMA 0x43C40000u /* 显示 VDMA CR */
#define PROBE_UART1 0xE0001000u    /* PS UART1：CR/SR */

static uint64_t probe_gt_now(void)
{
    uint32_t hi;
    uint32_t lo;
    uint32_t hi2;

    do {
        hi = Xil_In32(PROBE_GT_HI);
        lo = Xil_In32(PROBE_GT_LO);
        hi2 = Xil_In32(PROBE_GT_HI);
    } while (hi != hi2);
    return ((uint64_t)hi2 << 32) | (uint64_t)lo;
}

static uint32_t probe_vbar(void)
{
    uint32_t v;
#if defined(__arm__)
    __asm__ volatile("mrc p15, 0, %0, c12, c0, 0" : "=r"(v));
#else
    v = 0u;
#endif
    return v;
}

static void probe_delay_ms(uint32_t ms)
{
    uint64_t t0 = probe_gt_now();
    uint64_t ticks = (uint64_t)ms * 333333u; /* 333,333,343 Hz ≈ 333,333 ticks/ms */

    while ((probe_gt_now() - t0) < ticks) {
        /* busy wait */
    }
}

int main(void)
{
    uint32_t tick = 0u;
    uint32_t vbar;
    uint32_t gt_lo0;

    /* 第一行：证明 main 被执行（此前的所有初始化都已通过） */
    xil_printf("\r\nPROBE: main\r\n");

    vbar = probe_vbar();
    gt_lo0 = Xil_In32(PROBE_GT_LO);
    xil_printf("PROBE: vbar=0x%x vec@0x0=0x%x\r\n", (unsigned)vbar,
               (unsigned)Xil_In32(vbar)); /* 读向量表首字（OCM） */

    xil_printf("PROBE: cam_rst(0x41200000)=0x%x\r\n", (unsigned)Xil_In32(PROBE_CAM_RST));
    xil_printf("PROBE: gt_lo(0xF8F00200)=0x%x gt_hi=0x%x\r\n",
               (unsigned)gt_lo0, (unsigned)Xil_In32(PROBE_GT_HI));
    xil_printf("PROBE: 2b_csr(0x43C00000)=0x%x\r\n", (unsigned)Xil_In32(PROBE_2B_CSR));
    xil_printf("PROBE: disp_vdma_cr(0x43C40000)=0x%x\r\n", (unsigned)Xil_In32(PROBE_DISP_VDMA));
    xil_printf("PROBE: uart1 cr(0xE0001000)=0x%x sr=0x%x\r\n",
               (unsigned)Xil_In32(PROBE_UART1),
               (unsigned)Xil_In32(PROBE_UART1 + 0x04u));
    xil_printf("PROBE: links=OCM only (no DDR access), no I2C, no IRQ, no driver\r\n");

    for (;;) {
        probe_delay_ms(500u);
        tick++;
        xil_printf("PROBE: tick %d gt_lo=0x%x\r\n", (int)tick,
                   (unsigned)Xil_In32(PROBE_GT_LO));
    }
}