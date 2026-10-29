/*
 * vtc_vdma_selftest.c —— 主机端离线自检：VTC 生成器初始化 + VDMA 双缓冲
 *
 * 为什么要做这个：VTC/VDMA 两块都是**寄存器序列**，离线最容易出错的是位域、
 * 写顺序、回读校验和双缓冲选择逻辑。这里用一块假寄存器堆（Xil_In32/Xil_Out32 替身）
 * 让 **真正上板的两个源文件**（src/vtc_ctrl.c、src/vdma_ctrl.c）原样跑一遍：
 *
 *   1) VTC：720p60 编程 → 回读校验（逐寄存器打印 want/got）→ 负例（人为破坏一个
 *      寄存器，确认校验会报 MISMATCH，不是静默通过）；
 *   2) VDMA：2 帧存（与 BD 的 c_num_fstores=2 一致）初始化 → 启动；
 *   3) 双缓冲：模拟 VDMA 读帧存轮转，验证“永远画不被读的那块”，并打印每帧决策。
 *
 * 假硬件的“行为”只在客户端：RESET 位自清、写 VSIZE 后清 HALTED、PARKPTR.READSTR
 * 随帧推进 —— 这些都是 pg020/xaxivdma_hw.h 里定义的寄存器语义，用来驱动被测代码的分支。
 *
 * 编译（MinGW gcc）：
 *   gcc -std=gnu11 -O2 -Wall -Wextra -DS5_HOST_TEST \
 *       -Itools/host_xil_shim -Isrc \
 *       tools/vtc_vdma_selftest.c src/vtc_ctrl.c src/vdma_ctrl.c \
 *       -o build/host_vtc_vdma_selftest.exe
 */
#define S5_HOST_TEST 1

#include <stdio.h>
#include <string.h>

#include "vdma_ctrl.h"
#include "vtc_ctrl.h"

/* 假时间基：每次调用 +1000 tick（约 3 us），保证轮询循环能推进而不是死等 */
uint64_t S5Ticks_Now(void)
{
    static uint64_t t = 1000000ULL;

    t += 1000ULL;
    return t;
}

/* ---------------- 假寄存器堆 ---------------- */

static uint32_t g_mm[0x00050000u / 4u]; /* 0x43C00000 .. 0x43C4FFFF */
static uint32_t g_frame_ticks;          /* 每次读 VDMA SR 推进一格 */

static inline uint32_t mm_idx(uint32_t addr)
{
    uint32_t off = addr - 0x43C00000u;

    return (off >> 2) & ((0x00050000u / 4u) - 1u);
}

static inline uint32_t mm_addr_of(uint32_t off) { return 0x43C00000u + off; }

static void fake_init(void)
{
    memset(g_mm, 0, sizeof(g_mm));
    g_frame_ticks = 0;

    /* VTC 版本寄存器：非 0/非全 1 即视为“IP 在” */
    g_mm[mm_idx(mm_addr_of(0x30000u + S5_VTC_VER))] = 0x00060000u;
    /* VDMA 版本寄存器：axi_vdma 6.3（驱动 XAXIVDMA_VERSION_* 编码：major<<28 | minor<<20 | rev<<16） */
    g_mm[mm_idx(mm_addr_of(0x40000u + S5_VDMA_VERSION))] = 0x60300000u;
    /* VDMA 0x18 FRMSTORE 回读：BD 已设 c_num_fstores=2 */
    g_mm[mm_idx(mm_addr_of(0x40000u + S5_VDMA_MM2S_FRMSTORE))] = 2u;
    /* VDMA SR 初值：HALTED=1 / IDLE=0 */
    g_mm[mm_idx(mm_addr_of(0x40000u + S5_VDMA_MM2S_VDMASR))] = S5_VDMA_SR_HALTED;
}

uint32_t Xil_In32(uint32_t addr)
{
    uint32_t idx = mm_idx(addr);

    /* ---- VTC ---- */
    if (addr == mm_addr_of(0x30000u + S5_VTC_CTL)) {
        /* RESET 位“自清”：读到的永远是已清掉 RESET 的值 */
        g_mm[idx] &= ~S5_VTC_CTL_RESET;
        return g_mm[idx];
    }
    /* ---- VDMA ---- */
    if (addr == mm_addr_of(0x40000u + S5_VDMA_MM2S_VDMASR)) {
        /* 每读一次 SR 推进一个“帧” */
        g_frame_ticks++;
        return g_mm[idx];
    }
    if (addr == mm_addr_of(0x40000u + S5_VDMA_PARKPTR)) {
        /* READSTR = 当前读帧存，2 帧存轮转（每 2 个 tick 换一次，帧周期 ~2 tick） */
        uint32_t store = (g_frame_ticks / 2u) % 2u;
        uint32_t park = g_mm[idx] & ~S5_VDMA_PARK_READSTR_MASK;

        park |= (store << S5_VDMA_PARK_READSTR_SHIFT) & S5_VDMA_PARK_READSTR_MASK;
        return park;
    }
    return g_mm[idx];
}

void Xil_Out32(uint32_t addr, uint32_t val)
{
    uint32_t idx = mm_idx(addr);

    /* ---- VTC ---- */
    if (addr == mm_addr_of(0x30000u + S5_VTC_CTL)) {
        /* 写 RESET 立即完成（自清） */
        g_mm[idx] = val & ~S5_VTC_CTL_RESET;
        return;
    }
    /* ---- VDMA ---- */
    if (addr == mm_addr_of(0x40000u + S5_VDMA_MM2S_VDMACR)) {
        g_mm[idx] = val & ~S5_VDMA_CR_RESET;
        return;
    }
    if (addr == mm_addr_of(0x40000u + S5_VDMA_MM2S_VSIZE)) {
        g_mm[idx] = val;
        /* 写 VSIZE 后硬件退出 halted */
        g_mm[mm_idx(mm_addr_of(0x40000u + S5_VDMA_MM2S_VDMASR))] = S5_VDMA_SR_IDLE;
        return;
    }
    g_mm[idx] = val;
}

/* ---------------- 自检主体 ---------------- */

static int g_fail;

static void print_vtc(const S5Vtc *vtc)
{
    char line[96];
    uint32_t i;

    printf("VTC: version=0x%08X\n", (unsigned)vtc->version);
    for (i = 0; i < vtc->n_chk; i++) {
        S5Vtc_FormatCheck(vtc, i, line, (uint32_t)sizeof(line));
        printf("  %s\n", line);
    }
    S5Vtc_FormatCheck(vtc, vtc->n_chk, line, (uint32_t)sizeof(line)); /* CTL */
    printf("  %s\n", line);
    S5Vtc_FormatSummary(vtc, line, (uint32_t)sizeof(line));
    printf("  %s\n", line);
    S5Vtc_FormatTiming(vtc, line, (uint32_t)sizeof(line));
    printf("  %s\n", line);
}

int main(void)
{
    static S5Vtc vtc;
    static S5Vdma dma;
    S5VtcTiming timing;
    uint32_t addrs[2];
    uint32_t major, minor, rev;
    uint32_t i;
    uint32_t back;
    int rc;

    printf("==== S5 P3b-sw 离线自检：VTC 初始化 + VDMA 双缓冲 ====\n");
    fake_init();

    /* ---------- 1) VTC 720p60 初始化 + 回读校验 ---------- */
    S5Vtc_Default720p60(&timing);
    rc = S5Vtc_Init(&vtc, &timing, 10000u);
    print_vtc(&vtc);
    if (rc == 0) {
        printf("VTC: init OK (SW|GE enabled, 720p60 generator)\n");
    } else {
        printf("VTC: init FAILED rc=%d\n", rc);
        g_fail = 1;
    }

    /* 负例：人为破坏 GHSIZE，确认校验会显式报 MISMATCH（不静默） */
    Xil_Out32(S5_VTC_BASE + S5_VTC_GHSIZE, 0x1234u);
    if (S5Vtc_Verify(&vtc) == 0u) {
        printf("VTC negative test: FAIL（破坏寄存器后仍报全通过）\n");
        g_fail = 1;
    } else {
        printf("VTC negative test: OK（检测到 %u 项不一致）\n", (unsigned)vtc.fail_count);
        {
            char line[96];
            uint32_t k;

            for (k = 0; k < vtc.n_chk; k++) {
                S5Vtc_FormatCheck(&vtc, k, line, (uint32_t)sizeof(line));
                if (strstr(line, "MISMATCH") != NULL) {
                    printf("  %s\n", line);
                }
            }
        }
        /* 恢复正确时序，便于后续状态干净 */
        rc = S5Vtc_Init(&vtc, &timing, 10000u);
        printf("VTC: re-init after negative test -> %s\n", (rc == 0) ? "OK" : "FAILED");
        if (rc != 0) {
            g_fail = 1;
        }
    }

    /* ---------- 2) VDMA 初始化（2 帧存，非 SG） ---------- */
    addrs[0] = 0x13000000u;
    addrs[1] = 0x13384000u;
    rc = S5Vdma_Init(&dma, addrs, 2u, 1280u * 4u, 720u);
    if (rc == 0) {
        S5Vdma_DecodeVersion(dma.version, &major, &minor, &rev);
        printf("VDMA: init OK, version=0x%08X (major %u minor %u rev %u), FRMSTORE readback=%u (expect 2)\n",
               (unsigned)dma.version, (unsigned)major, (unsigned)minor, (unsigned)rev,
               (unsigned)dma.fs_hw_readback);
        printf("VDMA: CR=0x%08X SR=0x%08X HSIZE=%u VSIZE=%u STRIDE=%u\n",
               (unsigned)dma.cr_last, (unsigned)dma.sr_last,
               (unsigned)dma.hsize_bytes, (unsigned)dma.vsize_lines,
               (unsigned)dma.stride_bytes);
        printf("VDMA: store0=0x%08X store1=0x%08X\n",
               (unsigned)dma.fb_addr[0], (unsigned)dma.fb_addr[1]);
    } else {
        printf("VDMA: init FAILED rc=%d\n", rc);
        g_fail = 1;
    }

    /* ---------- 3) 双缓冲选择：永远画“当前不被读”的那块 ---------- */
    back = 0;
    for (i = 0; i < 6u; i++) {
        uint32_t target = addrs[back];
        uint32_t reading;
        int w;

        w = S5Vdma_WaitNotReading(&dma, target, 100000u);
        reading = S5Vdma_CurrentReadAddr(&dma);
        printf("frame %u: VDMA reads %c(0x%08X) -> draw into %c(0x%08X) wait=%s %s\n",
               (unsigned)i,
               (reading == addrs[0]) ? 'A' : ((reading == addrs[1]) ? 'B' : '?'),
               (unsigned)reading,
               (target == addrs[0]) ? 'A' : 'B',
               (unsigned)target,
               (w == 0) ? "ok" : "TIMEOUT",
               (w == 0 && reading != target) ? "PASS" : "FAIL");
        if (!(w == 0 && reading != target)) {
            g_fail = 1;
        }
        back ^= 1u;
    }

    printf("==== selftest: %s ====\n", (g_fail == 0) ? "PASS" : "FAIL");
    return (g_fail == 0) ? 0 : 1;
}