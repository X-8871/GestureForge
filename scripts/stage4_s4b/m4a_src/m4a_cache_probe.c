/*
 * m4a_cache_probe.c —— 阶段4 S4-T31 M4-a 最小测量程序（**只做 cache 维护/可见性**，无任何业务功能）
 *
 * 用途（严格限定）：
 *   · 只在候选区 [0x12000000, 0x12C08000) 内读写；任何越界请求一律拒绝并报错；
 *   · 提供四条只读/受限命令：R 读+CRC、I invalidate+CRC、F flush+invalidate+CRC、W 写图案+flush+CRC；
 *   · 通过 UART 输出 `M4A ...` 行（115200 8N1），由主机侧驱动解析。
 *
 * 明确**不做**：不初始化/不驱动 DMA、不访问 PL、不做推理、不解析张量、不写候选区外任何地址。
 * cache 维护按 **64 B 向外取整**（起始向下对齐、结束向上对齐），与地址图 cache_maintenance 口径一致。
 *
 * 构建：见 scripts/stage4_s4b/build_m4a_measurement_elf.py（离线；Vitis 2026.1 arm-none-eabi-gcc，cortex-a9）。
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "xil_cache.h"
#include "xil_printf.h"
#include "sleep.h"

#define CAND_BASE 0x12000000u
#define CAND_END  0x12C08000u            /* 半开区间 */
#define CAND_BYTES (CAND_END - CAND_BASE) /* 12,615,680 */
#define CACHE_ALIGN 64u                   /* 维护对齐：64 B 向外取整 */

static const char *kPrompt = "M4A> ";

/* 位wise CRC-32（IEEE 802.3），用于区间内容摘要；不依赖查表，代码量最小 */
static uint32_t crc32_range(uint32_t addr, uint32_t len)
{
    uint32_t crc = 0xFFFFFFFFu;
    const volatile uint8_t *p = (const volatile uint8_t *)(uintptr_t)addr;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= (uint32_t)p[i];
        for (int b = 0; b < 8; b++) {
            uint32_t mask = (uint32_t)(-(int32_t)(crc & 1u));
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

static uint32_t align_down(uint32_t v, uint32_t a) { return v & ~(a - 1u); }
static uint32_t align_up(uint32_t v, uint32_t a) { return (v + a - 1u) & ~(a - 1u); }

/* 解析 0x 前缀或十进制无符号数；成功返回 1 */
static int parse_u32(const char *s, uint32_t *out)
{
    uint32_t value = 0;
    int base = 10;
    if (s == 0 || *s == '\0') {
        return 0;
    }
    if (s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) {
        base = 16;
        s += 2;
        if (*s == '\0') {
            return 0;
        }
    }
    for (; *s != '\0'; s++) {
        uint32_t digit;
        if (*s >= '0' && *s <= '9') {
            digit = (uint32_t)(*s - '0');
        } else if (base == 16 && *s >= 'a' && *s <= 'f') {
            digit = (uint32_t)(*s - 'a' + 10);
        } else if (base == 16 && *s >= 'A' && *s <= 'F') {
            digit = (uint32_t)(*s - 'A' + 10);
        } else {
            return 0;
        }
        value = value * (uint32_t)base + digit;
    }
    *out = value;
    return 1;
}

/* 读一行（回显不处理；最长 96 字符） */
static int read_line(char *buf, int cap)
{
    int n = 0;
    for (;;) {
        char c = (char)inbyte();
        if (c == '\r' || c == '\n') {
            if (n > 0) {
                buf[n] = '\0';
                xil_printf("\r\n");
                return n;
            }
            continue;
        }
        if (n + 1 < cap) {
            buf[n++] = c;
        }
    }
}

static int in_candidate(uint32_t addr, uint32_t len)
{
    if (len == 0) {
        return 0;
    }
    if (addr < CAND_BASE) {
        return 0;
    }
    if (addr >= CAND_END) {
        return 0;
    }
    if (len > CAND_BYTES - (addr - CAND_BASE)) {
        return 0;
    }
    return 1;
}

static void do_write_pattern(uint32_t addr, uint32_t len, uint32_t pattern)
{
    volatile uint32_t *p = (volatile uint32_t *)(uintptr_t)addr;
    uint32_t words = len / 4u;
    for (uint32_t i = 0; i < words; i++) {
        p[i] = pattern;
    }
}

int main(void)
{
    char line[96];
    xil_printf("\r\nM4A READY base=0x%08x end=0x%08x bytes=%u align=%u\r\n",
               (unsigned)CAND_BASE, (unsigned)CAND_END, (unsigned)CAND_BYTES, (unsigned)CACHE_ALIGN);

    for (;;) {
        xil_printf("%s", kPrompt);
        if (read_line(line, (int)sizeof(line)) <= 0) {
            continue;
        }
        char cmd = line[0];
        if (cmd == 'Q' || cmd == 'q') {
            xil_printf("M4A BYE\r\n");
            return 0;
        }
        /* 解析 addr len [pat] */
        char *save = line + 1;
        char *tok1 = save;
        while (*save == ' ') { save++; }
        tok1 = save;
        char *tok2 = 0, *tok3 = 0;
        char *sp = strchr(save, ' ');
        if (sp != 0) {
            *sp = '\0';
            tok2 = sp + 1;
            while (*tok2 == ' ') { tok2++; }
            char *sp2 = strchr(tok2, ' ');
            if (sp2 != 0) {
                *sp2 = '\0';
                tok3 = sp2 + 1;
                while (*tok3 == ' ') { tok3++; }
            }
        }
        uint32_t addr = 0, len = 0, pat = 0;
        if (tok1 == 0 || tok2 == 0 || !parse_u32(tok1, &addr) || !parse_u32(tok2, &len)) {
            xil_printf("M4A ERR ARGS\r\n");
            continue;
        }
        if (!in_candidate(addr, len)) {
            xil_printf("M4A ERR RANGE addr=0x%08x len=%u\r\n", (unsigned)addr, (unsigned)len);
            continue;
        }
        uint32_t a0 = align_down(addr, CACHE_ALIGN);
        uint32_t a1 = align_up(addr + len, CACHE_ALIGN);
        uint32_t alen = a1 - a0;

        switch (cmd) {
        case 'R': /* 只读 + CRC（不碰 cache） */
            xil_printf("M4A OK R addr=0x%08x len=%u crc=0x%08x\r\n",
                       (unsigned)addr, (unsigned)len, (unsigned)crc32_range(addr, len));
            break;
        case 'I': /* invalidate（64 B 向外取整）后 CRC */
            Xil_DCacheInvalidateRange((INTPTR)a0, (UINTPTR)alen);
            xil_printf("M4A OK I addr=0x%08x len=%u aligned=[0x%08x,%u) crc=0x%08x\r\n",
                       (unsigned)addr, (unsigned)len, (unsigned)a0, (unsigned)alen,
                       (unsigned)crc32_range(addr, len));
            break;
        case 'F': /* flush + invalidate 后 CRC */
            Xil_DCacheFlushRange((INTPTR)a0, (UINTPTR)alen);
            Xil_DCacheInvalidateRange((INTPTR)a0, (UINTPTR)alen);
            xil_printf("M4A OK F addr=0x%08x len=%u aligned=[0x%08x,%u) crc=0x%08x\r\n",
                       (unsigned)addr, (unsigned)len, (unsigned)a0, (unsigned)alen,
                       (unsigned)crc32_range(addr, len));
            break;
        case 'W': /* CPU 写图案 → flush+invalidate → CRC（行内可见） */
            if (tok3 == 0 || !parse_u32(tok3, &pat)) {
                xil_printf("M4A ERR ARGS pat\r\n");
                break;
            }
            do_write_pattern(addr, len, pat);
            Xil_DCacheFlushRange((INTPTR)a0, (UINTPTR)alen);
            Xil_DCacheInvalidateRange((INTPTR)a0, (UINTPTR)alen);
            xil_printf("M4A OK W addr=0x%08x len=%u pat=0x%08x crc=0x%08x\r\n",
                       (unsigned)addr, (unsigned)len, (unsigned)pat,
                       (unsigned)crc32_range(addr, len));
            break;
        default:
            xil_printf("M4A ERR CMD %c\r\n", cmd);
            break;
        }
    }
}