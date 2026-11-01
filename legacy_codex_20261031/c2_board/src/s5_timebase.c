/*
 * s5_timebase.c —— 全局定时器 64 位读取 + 宏括号坑的编译期断言
 *
 * 见 s5_timebase.h 顶部说明。这里额外做两件事：
 *   1) 用带括号的 (uint64_t)(COUNTS_PER_SECOND) 与自带常量 S5_GT_HZ 对齐，
 *      一旦 BSP 的 CPU 频率或 xtimer 宏写法变化，编译期直接失败（而不是静默算错 4 倍）；
 *   2) hi-lo-hi 双读，保证低位 32 位回绕时不会把 (hi,lo) 拼错。
 */
#include "s5_timebase.h"

#include "xil_io.h"
#include "xiltimer.h" /* COUNTS_PER_SECOND（BSP include/xtimer_config.h，宏无括号） */

/* BSP 的 COUNTS_PER_SECOND 展开为 XPAR_CPU_CORE_CLOCK_FREQ_HZ/2 = 666666687/2。
 * 这里用**带括号**的写法（先算除法再转 64 位），与 S5_GT_HZ 比较。
 * 注意：若写成 (uint64_t)COUNTS_PER_SECOND / 2，或把 COUNTS_PER_SECOND 直接放进
 *       “先乘后除”的表达式，分母会被放大到 1,333,333,374 —— 阶段4 的历史坑。 */
_Static_assert(((uint64_t)(COUNTS_PER_SECOND)) == S5_GT_HZ,
               "COUNTS_PER_SECOND 与 S5_GT_HZ 不一致：请核对 BSP CPU 频率/xtimer 宏写法");
_Static_assert(S5_GT_HZ == 333333343ULL, "S5_GT_HZ 应为 666666687/2");

uint64_t S5Ticks_Now(void)
{
    uint32_t hi1;
    uint32_t lo;
    uint32_t hi2;

    do {
        hi1 = Xil_In32(S5_GT_HIGH_REG);
        lo = Xil_In32(S5_GT_LOW_REG);
        hi2 = Xil_In32(S5_GT_HIGH_REG);
    } while (hi1 != hi2);

    return ((uint64_t)hi1 << 32) | (uint64_t)lo;
}