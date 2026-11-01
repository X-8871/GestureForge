/*
 * s5_timebase.h —— 阶段5 PS 侧时间基座（P3b-sw）
 *
 * 为什么不用 BSP 的 COUNTS_PER_SECOND 直接算：
 *   BSP `include/xtimer_config.h` 里
 *       #define XSLEEPTIMER_FREQ   XPAR_CPU_CORE_CLOCK_FREQ_HZ/2
 *       #define COUNTS_PER_SECOND  XSLEEPTIMER_FREQ
 *   两个宏都**没有括号**。`xparameters.h` 中 XPAR_CPU_CORE_CLOCK_FREQ_HZ = 666666687。
 *   若写成 `ticks * 1000 / COUNTS_PER_SECOND`，预处理后是
 *       ticks * 1000 / 666666687 / 2
 *   实际分母变成 1,333,333,374（= GT 频率的 4 倍），所有 ms 值被压小 4 倍。
 *   （同一坑在阶段4 已发生，见 S4-T34/s4d_time_basis_20261029_r01/ERRATUM_ROOT_CAUSE.md）
 *
 * 本模块的做法：
 *   · 计数直接读 Zynq 全局定时器（0xF8F00200 低 32 位 / 0xF8F00204 高 32 位），
 *     读法为 hi-lo-hi 双读（低位回绕期间高 32 位可能进位，必须复核）；
 *   · 频率用**自带显式常量** S5_GT_HZ = 333333343（= 666666687 / 2，向下取整），
 *     并在编译期用带括号的 (uint64_t)(COUNTS_PER_SECOND) 做一次断言，宏一改就编译失败；
 *   · 所有换算用 64 位整数，先乘后除，避免中间截断。
 */
#ifndef S5_TIMEBASE_H
#define S5_TIMEBASE_H

#include <stdint.h>

/* Zynq-7000 全局定时器计数频率：
 * CPU_3x2x = 666666687 Hz（PS_CLK 33.333333 MHz × 40 / 2），GT = CPU_3x2x/2 = 333333343.5 → 取整 333333343。 */
#define S5_GT_HZ 333333343ULL

/* 全局定时器寄存器（Zynq-7000 TRM ug585 表 8-1：私有定时器/全局定时器位于 0xF8F00200 起） */
#define S5_GT_LOW_REG  0xF8F00200u
#define S5_GT_HIGH_REG 0xF8F00204u

/* 当前 64 位计数（hi-lo-hi 双读，规避低位回绕）。 */
uint64_t S5Ticks_Now(void);

/* 计数差 → 微秒 / 毫秒（先乘后除，64 位）。 */
static inline uint64_t S5Ticks_ToUs(uint64_t delta)
{
    return (delta * 1000000ULL) / S5_GT_HZ;
}

static inline uint64_t S5Ticks_ToMs(uint64_t delta)
{
    return (delta * 1000ULL) / S5_GT_HZ;
}

/* 轮询超时的“自旋预算”：把 us 换成定时器计数（不睡眠，离线/裸机均可）。 */
static inline uint64_t S5Ticks_FromUs(uint64_t us)
{
    return (us * S5_GT_HZ) / 1000000ULL;
}

/* 由计数差判断是否超时。 */
static inline int S5Ticks_Elapsed(uint64_t start, uint64_t budget)
{
    return (S5Ticks_Now() - start) >= budget;
}

#endif /* S5_TIMEBASE_H */