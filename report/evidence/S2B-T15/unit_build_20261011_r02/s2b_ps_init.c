/* 只调用同一固定XSA的PS初始化；所有对象和模式栈必须属于OCM。 */
#include "ps7_init.h"
#include "xil_cache.h"
#include "xil_types.h"
#include "xpseudo_asm.h"
#ifndef SDT
#error "初始化壳要求实际SDT CPU0 BSP"
#endif
#ifdef USE_AMP
#error "初始化壳不支持AMP"
#endif
_Static_assert(sizeof(u32) == 4, "u32 must be 32 bit");
volatile u32 s2b_ps_init_result __attribute__((aligned(64))) = 0U;
volatile int s2b_ps_init_return __attribute__((aligned(64))) = -1;

__attribute__((used, noinline, noreturn)) void s2b_ps_init_ready(void)
{
    /* 独有成功停止点；不加载启动镜像、不配置PL、不释放CPU1。 */
    for (;;) { __asm__ volatile("wfe" ::: "memory"); }
}

__attribute__((used, noinline, noreturn)) void s2b_ps_init_fail(void)
{
    /* 原ps7_init返回码供调试器读取；失败不进入成功停止点。 */
    for (;;) { __asm__ volatile("wfe" ::: "memory"); }
}

int main(void)
{
    u32 mpidr;
    __asm__ volatile("mrc p15, 0, %0, c0, c0, 5" : "=r"(mpidr));
    /* BSP启动只使用OCM；在调用初始化前把OCM脏数据写回并关闭DCache。 */
    Xil_DCacheFlush();
    Xil_DCacheDisable();
    if ((mpidr & 0xFFU) != 0U) {
        s2b_ps_init_result = 0x81U;
        dsb();
        s2b_ps_init_fail();
    }
    s2b_ps_init_result = 1U;
    dsb();
    s2b_ps_init_return = ps7_init();
    if (s2b_ps_init_return != PS7_INIT_SUCCESS) {
        s2b_ps_init_result = 0x82U;
        dsb();
        s2b_ps_init_fail();
    }
    s2b_ps_init_result = 2U;
    dsb();
    s2b_ps_init_ready();
}
