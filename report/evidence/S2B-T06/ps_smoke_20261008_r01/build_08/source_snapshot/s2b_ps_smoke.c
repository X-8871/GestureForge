/* 阶段2B的PS前置检查：只使用链接器独占的DDR对象，不扫描整个DDR。 */
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include "xil_cache.h"
#include "xil_types.h"
#include "xparameters.h"
#include "xstatus.h"
#include "xuartps.h"
#include "s2b_smoke_platform.h"

#ifndef SDT
#error "本程序只接受已核验的Vitis 2026.1 SDT BSP"
#endif
#ifdef USE_AMP
#error "本程序要求CPU0独占且BSP同时维护L1和L2缓存"
#endif

#define SMOKE_VERSION "S2B-T06-1"
#define SMOKE_BYTES (1024U * 1024U)
#define SMOKE_WORDS (SMOKE_BYTES / sizeof(u32))
#define SMOKE_PASSES 2U
#define SMOKE_PATTERNS 8U
#define UART_POLL_LIMIT 10000000U

_Static_assert(sizeof(u32) == 4U, "检查要求32位word");
_Static_assert(sizeof(UINTPTR) == 4U, "检查要求32位Cortex-A9地址");
_Static_assert(S2B_BSP_CACHELINE_BYTES == 32U, "BSP缓存行必须由实际源码确认");
_Static_assert((SMOKE_BYTES % 64U) == 0U, "缓存维护范围必须完整对齐");
_Static_assert(S2B_BUFFER_END - S2B_BUFFER_BEGIN == SMOKE_BYTES, "链接窗口大小不符");
_Static_assert(S2B_UART1_BASE == 0xE0001000U, "实际BSP必须指向PS UART1");
_Static_assert(sizeof(S2B_C_SOURCE_SHA256) == 65U, "构建必须绑定实际C源码SHA-256");
_Static_assert(sizeof(S2B_XSA_SHA256) == 65U, "构建必须绑定固定XSA SHA-256");

/* 自定义NOLOAD节不属于启动代码清零的.bss；首次模式完整覆盖整个对象。 */
static u32 s2b_smoke_buffer[SMOKE_WORDS]
    __attribute__((section(".s2b_smoke_buffer"), aligned(64), used));
extern u8 __s2b_smoke_buffer_start[];
extern u8 __s2b_smoke_buffer_end[];
static XUartPs uart;

/* 状态独立对齐；每次发布均写回DDR，UART不可用时可据此核对物理读结果。 */
volatile u32 s2b_smoke_result __attribute__((aligned(64))) = 0U;

static void memory_barrier(void)
{
    __asm__ __volatile__("dsb sy" ::: "memory");
}

static void publish_result(u32 value)
{
    /* volatile不提供DAP/DDR一致性；明确写回状态所在缓存行后再返回。 */
    s2b_smoke_result = value;
    memory_barrier();
    Xil_DCacheFlushRange((INTPTR)(UINTPTR)&s2b_smoke_result, (u32)sizeof(s2b_smoke_result));
    memory_barrier();
}

static int send_text(const char *text)
{
    while (*text != '\0') {
        u32 tries;
        u8 byte = (u8)*text;
        /* 每次只交付一个字节，避免重设驱动的未完成发送缓冲。 */
        for (tries = 0U; tries < UART_POLL_LIMIT; ++tries) {
            if (XUartPs_Send(&uart, &byte, 1U) == 1U) {
                break;
            }
        }
        if (tries == UART_POLL_LIMIT) {
            return XST_FAILURE;
        }
        for (tries = 0U; tries < UART_POLL_LIMIT; ++tries) {
            if (XUartPs_IsSending(&uart) == 0U) {
                break;
            }
        }
        if (tries == UART_POLL_LIMIT) {
            return XST_FAILURE;
        }
        ++text;
    }
    return XST_SUCCESS;
}

static int send_line(const char *format, ...)
{
    char text[256];
    va_list args;
    int count;
    va_start(args, format);
    count = vsnprintf(text, sizeof(text), format, args);
    va_end(args);
    if ((count < 0) || ((unsigned int)count >= sizeof(text))) {
        return XST_FAILURE;
    }
    return send_text(text);
}

static int init_uart(void)
{
    XUartPs_Config *config = XUartPs_LookupConfig((UINTPTR)S2B_UART1_BASE);
    XUartPsFormat wanted = {115200U, XUARTPS_FORMAT_8_BITS,
                           XUARTPS_FORMAT_NO_PARITY, XUARTPS_FORMAT_1_STOP_BIT};
    XUartPsFormat actual;
    if ((config == NULL) || (config->BaseAddress != S2B_UART1_BASE) ||
        (config->InputClockHz == 0U)) {
        return XST_FAILURE;
    }
    if (XUartPs_CfgInitialize(&uart, config, (u32)config->BaseAddress) != XST_SUCCESS) {
        return XST_FAILURE;
    }
    XUartPs_SetInterruptMask(&uart, 0U);
    XUartPs_SetOptions(&uart, 0U);
    XUartPs_SetOperMode(&uart, XUARTPS_OPER_MODE_NORMAL);
    if (XUartPs_SetDataFormat(&uart, &wanted) != XST_SUCCESS) {
        return XST_FAILURE;
    }
    XUartPs_GetDataFormat(&uart, &actual);
    if ((actual.BaudRate != wanted.BaudRate) || (actual.DataBits != wanted.DataBits) ||
        (actual.Parity != wanted.Parity) || (actual.StopBits != wanted.StopBits) ||
        ((XUartPs_GetOptions(&uart) & XUARTPS_OPTION_SET_FCM) != 0U) ||
        (XUartPs_GetOperMode(&uart) != XUARTPS_OPER_MODE_NORMAL)) {
        return XST_FAILURE;
    }
    return XST_SUCCESS;
}

static u32 pattern_word(u32 pattern, u32 word)
{
    switch (pattern) {
    case 0U: return 0x00000000U;
    case 1U: return 0xFFFFFFFFU;
    case 2U: return 0xAAAAAAAAU;
    case 3U: return 0x55555555U;
    case 4U: return word;
    case 5U: return ~word;
    case 6U: return 1U << (word & 31U);
    default: return ~(1U << (word & 31U));
    }
}

static int fail_after_uart(const char *reason, u32 result)
{
    publish_result(result);
    if (send_line("FAIL reason=%s\r\nEND %s\r\n", reason, SMOKE_VERSION) != XST_SUCCESS) {
        publish_result(0x83U);
    }
    return XST_FAILURE;
}

int main(void)
{
    const UINTPTR begin = (UINTPTR)s2b_smoke_buffer;
    const UINTPTR end = begin + (UINTPTR)sizeof(s2b_smoke_buffer);
    volatile u32 *const words = s2b_smoke_buffer;
    u32 core;
    u32 pass;
    u32 pattern;
    u32 verified_words = 0U;
    publish_result(1U);
    if (init_uart() != XST_SUCCESS) {
        publish_result(0x81U);
        return XST_FAILURE;
    }
    if (send_line("BEGIN %s\r\nBUILD c_sha256=%s xsa_sha256=%s\r\n",
                  SMOKE_VERSION, S2B_C_SOURCE_SHA256, S2B_XSA_SHA256) != XST_SUCCESS) {
        publish_result(0x83U);
        return XST_FAILURE;
    }
    if (send_line("UART base=0x%08lX baud=115200 data=8 parity=N stop=1 flow=NONE clock_hz=%lu\r\n",
                  (unsigned long)uart.Config.BaseAddress,
                  (unsigned long)uart.InputClockHz) != XST_SUCCESS) {
        publish_result(0x83U);
        return XST_FAILURE;
    }
    if (send_line("BUFFER begin=0x%08lX end_exclusive=0x%08lX bytes=%lu words=%lu align=64 cacheline=32\r\n",
                  (unsigned long)begin, (unsigned long)end,
                  (unsigned long)sizeof(s2b_smoke_buffer), (unsigned long)SMOKE_WORDS) != XST_SUCCESS) {
        publish_result(0x83U);
        return XST_FAILURE;
    }
    /* 地址检查先于第一次写入；实际地址来自链接结果和构建时生成的绑定。 */
    if ((begin != S2B_BUFFER_BEGIN) || (end != S2B_BUFFER_END) || (end <= begin) ||
        ((begin & 63U) != 0U) || ((end & 63U) != 0U) ||
        (begin != (UINTPTR)__s2b_smoke_buffer_start) ||
        (end != (UINTPTR)__s2b_smoke_buffer_end)) {
        return fail_after_uart("BUFFER_LAYOUT", 0x82U);
    }
    __asm__ __volatile__("mrc p15, 0, %0, c0, c0, 5" : "=r"(core));
    if ((core & 3U) != 0U) {
        return fail_after_uart("CPU_NOT_ZERO", 0x84U);
    }
    /* 部署前仍须确认CPU1停驻、所有DMA及PL写入方静止；这里只屏蔽CPU0中断。 */
    __asm__ __volatile__("cpsid if" ::: "memory");
    Xil_DCacheEnable();
    memory_barrier();
    if (send_line("CONFIG cpu=0 passes=%lu patterns=%lu words_per_pattern=%lu order=WRITE_DSB_FLUSH_DSB_INVALIDATE_DSB_READ\r\n",
                  (unsigned long)SMOKE_PASSES, (unsigned long)SMOKE_PATTERNS,
                  (unsigned long)SMOKE_WORDS) != XST_SUCCESS) {
        publish_result(0x83U);
        return XST_FAILURE;
    }
    for (pass = 0U; pass < SMOKE_PASSES; ++pass) {
        for (pattern = 0U; pattern < SMOKE_PATTERNS; ++pattern) {
            u32 word;
            u32 mismatches = 0U;
            u32 first_word = 0U;
            u32 first_expected = 0U;
            u32 first_actual = 0U;
            for (word = 0U; word < SMOKE_WORDS; ++word) {
                words[word] = pattern_word(pattern, word);
            }
            /* 两级缓存范围维护后读回，避免仅命中本核先前写入的缓存行。 */
            memory_barrier();
            Xil_DCacheFlushRange((INTPTR)begin, SMOKE_BYTES);
            memory_barrier();
            Xil_DCacheInvalidateRange((INTPTR)begin, SMOKE_BYTES);
            memory_barrier();
            for (word = 0U; word < SMOKE_WORDS; ++word) {
                const u32 expected = pattern_word(pattern, word);
                const u32 actual = words[word];
                if (actual != expected) {
                    if (mismatches == 0U) {
                        first_word = word;
                        first_expected = expected;
                        first_actual = actual;
                    }
                    ++mismatches;
                }
            }
            verified_words += SMOKE_WORDS;
            if (mismatches != 0U) {
                publish_result(0x85U);
                if (send_line("FAIL pass=%lu pattern=%lu first_offset=0x%08lX expected=0x%08lX actual=0x%08lX mismatches=%lu verified_words=%lu\r\nEND %s\r\n",
                              (unsigned long)pass, (unsigned long)pattern,
                              (unsigned long)(first_word * sizeof(u32)),
                              (unsigned long)first_expected, (unsigned long)first_actual,
                              (unsigned long)mismatches, (unsigned long)verified_words,
                              SMOKE_VERSION) != XST_SUCCESS) {
                    publish_result(0x83U);
                }
                return XST_FAILURE;
            }
            if (send_line("PATTERN_PASS pass=%lu pattern=%lu words=%lu mismatches=0\r\n",
                          (unsigned long)pass, (unsigned long)pattern,
                          (unsigned long)SMOKE_WORDS) != XST_SUCCESS) {
                publish_result(0x83U);
                return XST_FAILURE;
            }
        }
    }
    if (send_line("PASS passes=2 patterns=8 verified_words=%lu mismatches=0\r\nEND %s\r\n",
                  (unsigned long)verified_words, SMOKE_VERSION) != XST_SUCCESS) {
        publish_result(0x83U);
        return XST_FAILURE;
    }
    publish_result(2U);
    return XST_SUCCESS;
}
