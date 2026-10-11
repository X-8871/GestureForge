/* 阶段2B候选CPU0驱动：只有完整有效传输和外层安全状态才允许访问任务arena。 */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <limits.h>
#include "s2a_ps_decode_nms_reference.h"

#ifdef S2B_HOST_MOCK
#include "s2b_host_mock.h"
#else
#include "xil_cache.h"
#include "xil_io.h"
#include "xil_mmu.h"
#include "xil_types.h"
#include "xuartps.h"
#include "xstatus.h"
#include "xiltimer.h"
#include "sleep.h"
#include "s2b_inference_platform.h"
#ifndef SDT
#error "本程序要求实际Vitis2026.1 SDT CPU0 BSP"
#endif
#ifdef USE_AMP
#error "本程序禁止USE_AMP，缓存维护必须覆盖实际L1/L2"
#endif
#endif

#define INPUT_BYTES 519168U
#define WEIGHT_BYTES 5903100U
#define HEAD13_BYTES 5070U
#define HEAD26_BYTES 20280U
#define ARENA_BYTES 0x02000000U
#define FEATURE_OFFSET 0x01000000U
#define FEATURE_END 0x01ADADB8U
#define CSR_BASE 0x43C00000U
#define HEADER_BYTES 40U
#define META_BYTES 40U
#define MAX_REPEAT 1000U
#define MAX_RESPONSE (META_BYTES + HEAD13_BYTES + HEAD26_BYTES + 15U * 48U)
#define OWNER_PL (1U << 8)
#define HEAD_VALID (1U << 9)
#define SAFE_REUSE (1U << 10)
#define TERMINAL (1U << 11)
#define AXI_PENDING (1U << 12)
#define FIRST_PENDING (1U << 13)
#define IDLE_PS 0U
#define DONE_SAFE 4U
#define ERROR_SAFE 5U
#define FAULT_ISOLATED 6U
#define OP_WEIGHTS 1U
#define OP_RUN 2U
#define OP_DIAG 3U
#define OP_CACHE_PROBE 4U
#define RESPONSE_OK 0U
#define BAD_HEADER 1U
#define BAD_CRC 2U
#define BAD_SEQUENCE 3U
#define BAD_LENGTH 4U
#define BAD_STATE 5U
#define BAD_PARAMETERS 6U
#define BOARD_ERROR 7U
#define OBSERVE_TIMEOUT 8U
#define DECODE_ERROR 9U

_Static_assert(CHAR_BIT == 8 && sizeof(double) == 8U, "传输要求八位字节和IEEE binary64");
_Static_assert(sizeof(int32_t) == 4U && sizeof(uint64_t) == 8U, "传输整数宽度不符");
#ifndef S2B_HOST_MOCK
_Static_assert(sizeof(UINTPTR) == 4U, "目标必须为Cortex-A9 AArch32");
_Static_assert(S2B_UART1_BASE == 0xE0001000U && S2B_BSP_CACHELINE_BYTES == 32U, "BSP必须绑定实际UART1和缓存行");
_Static_assert(COUNTS_PER_SECOND > 0U, "真实SDT global timer频率必须非零");
#endif

/* NOLOAD arena的空洞从不由业务写入；缓存维护可覆盖其专属行padding。 */
static uint8_t arena[ARENA_BYTES] __attribute__((section(".s2b_tensor_ddr"), aligned(64), used));
static uint8_t staging[WEIGHT_BYTES] __attribute__((aligned(64)));
static uint8_t response[MAX_RESPONSE];
static double logits13[HEAD13_BYTES], logits26[HEAD26_BYTES];
static s2a_t62_detection boxes[15];
static uint32_t next_sequence = 1U;
static int weights_loaded, input_loaded;
static int cache_probe_wait;
static uint32_t cache_cpu_seed, cache_dap_seed;
volatile uint32_t s2b_inference_result __attribute__((aligned(64))) = 0U;

typedef struct {
    uint16_t op;
    uint32_t sequence, frame, width, height, repeat, length, payload_crc;
} wire_header;
typedef struct {
    uint64_t epoch;
    uint32_t status, frame, error, reject;
} terminal_snapshot;

#ifndef S2B_HOST_MOCK
static XUartPs uart;
static void barrier(void) { __asm__ volatile("dsb sy" ::: "memory"); }
static uint32_t csr_read(uint32_t offset) { return Xil_In32(CSR_BASE + offset); }
static void csr_write(uint32_t offset, uint32_t value) { Xil_Out32(CSR_BASE + offset, value); barrier(); }
static uint64_t ticks(void) { XTime value; XTime_GetTime(&value); return (uint64_t)value; }
static uint64_t seconds_ticks(uint32_t seconds) { return (uint64_t)COUNTS_PER_SECOND * seconds; }
static void flush_range(uint32_t offset, uint32_t length)
{
    Xil_DCacheFlushRange((INTPTR)(UINTPTR)(arena + offset), length);
}
static void invalidate_range(uint32_t offset, uint32_t length)
{
    Xil_DCacheInvalidateRange((INTPTR)(UINTPTR)(arena + offset), length);
}
static int uart_read_one(uint8_t *byte)
{
    return XUartPs_Recv(&uart, byte, 1U) == 1U;
}
static int uart_write_one(uint8_t byte)
{
    return XUartPs_Send(&uart, &byte, 1U) == 1U;
}
static int uart_drain_done(void) { return XUartPs_IsSending(&uart) == 0U; }
static void publish(uint32_t code)
{
    s2b_inference_result = code;
    barrier();
    Xil_DCacheFlushRange((INTPTR)(UINTPTR)&s2b_inference_result, 64U);
    barrier();
}
#endif

static uint32_t get32(const uint8_t *bytes)
{
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8) |
           ((uint32_t)bytes[2] << 16) | ((uint32_t)bytes[3] << 24);
}
static void put32(uint8_t *bytes, uint32_t value)
{
    unsigned int index;
    for (index = 0U; index < 4U; ++index) bytes[index] = (uint8_t)(value >> (8U * index));
}
static void put64(uint8_t *bytes, uint64_t value)
{
    put32(bytes, (uint32_t)value); put32(bytes + 4U, (uint32_t)(value >> 32));
}
static void put_double(uint8_t *bytes, double value)
{
    uint64_t bits;
    memcpy(&bits, &value, 8U); put64(bytes, bits);
}
static uint32_t crc32_ieee(const uint8_t *bytes, uint32_t length)
{
    uint32_t crc = UINT32_MAX, index;
    unsigned int bit;
    for (index = 0U; index < length; ++index) {
        crc ^= bytes[index];
        for (bit = 0U; bit < 8U; ++bit) crc = (crc >> 1) ^ ((0U - (crc & 1U)) & 0xEDB88320U);
    }
    return ~crc;
}
static int expired(uint64_t started, uint32_t seconds)
{
    return ticks() - started >= seconds_ticks(seconds);
}
static int receive_bytes(uint8_t *bytes, uint32_t length, uint32_t seconds)
{
    uint32_t index = 0U;
    uint64_t started = ticks();
    while (index < length) {
        if (uart_read_one(bytes + index)) ++index;
        if (expired(started, seconds)) return 0;
    }
    return 1;
}
static int send_bytes(const uint8_t *bytes, uint32_t length, uint64_t started)
{
    uint32_t index = 0U;
    while (index < length) {
        if (uart_write_one(bytes[index])) ++index;
        if (expired(started, 10U)) return 0;
    }
    return 1;
}
static int read_epoch(uint64_t *epoch)
{
    unsigned int retry;
    for (retry = 0U; retry < 8U; ++retry) {
        uint32_t high = csr_read(0x054U), low = csr_read(0x050U);
        if (high == csr_read(0x054U)) { *epoch = ((uint64_t)high << 32) | low; return 1; }
    }
    return 0;
}
static int is_idle(void)
{
    uint32_t status = csr_read(0x00CU);
    return (status & 7U) == IDLE_PS && (status & SAFE_REUSE) != 0U &&
           (status & (OWNER_PL | AXI_PENDING | HEAD_VALID | TERMINAL | FIRST_PENDING)) == 0U;
}
static int safe_snapshot(terminal_snapshot *snap)
{
    uint32_t first = csr_read(0x00CU), state = first & 7U;
    if ((state != DONE_SAFE && state != ERROR_SAFE) ||
        (first & (SAFE_REUSE | TERMINAL)) != (SAFE_REUSE | TERMINAL) ||
        (first & (OWNER_PL | AXI_PENDING | FIRST_PENDING)) != 0U) return 0;
    if (!read_epoch(&snap->epoch)) return 0;
    snap->frame = csr_read(0x058U); snap->error = csr_read(0x010U); snap->reject = csr_read(0x064U);
    snap->status = csr_read(0x00CU);
    if (first != snap->status) return 0;
    return state == DONE_SAFE ? ((first & HEAD_VALID) != 0U && snap->error == 0U) :
                              ((first & HEAD_VALID) == 0U && snap->error != 0U);
}
static void feature_invalidate(void)
{
    barrier(); invalidate_range(FEATURE_OFFSET, (FEATURE_END - FEATURE_OFFSET + 63U) & ~63U); barrier();
}
static void prepare_cache(void)
{
    barrier(); flush_range(0U, INPUT_BYTES); flush_range(0x00100000U, (WEIGHT_BYTES + 63U) & ~63U); barrier();
    flush_range(FEATURE_OFFSET, (FEATURE_END - FEATURE_OFFSET + 63U) & ~63U);
    invalidate_range(FEATURE_OFFSET, (FEATURE_END - FEATURE_OFFSET + 63U) & ~63U); barrier();
}
static int encode_header(const uint8_t *raw, wire_header *head)
{
    if (memcmp(raw, "S2BU", 4U) != 0 || raw[4] != 1U || raw[5] != 0U ||
        crc32_ieee(raw, 36U) != get32(raw + 36U)) return BAD_HEADER;
    head->op = (uint16_t)((uint16_t)raw[6] | ((uint16_t)raw[7] << 8));
    head->sequence = get32(raw + 8U); head->frame = get32(raw + 12U);
    head->width = get32(raw + 16U); head->height = get32(raw + 20U);
    head->repeat = get32(raw + 24U); head->length = get32(raw + 28U); head->payload_crc = get32(raw + 32U);
    if (head->sequence != next_sequence || next_sequence == UINT32_MAX) return BAD_SEQUENCE;
    if ((head->op == OP_WEIGHTS && head->length != WEIGHT_BYTES) ||
        (head->op == OP_RUN && head->length != INPUT_BYTES + 8U) ||
        (head->op == OP_DIAG && head->length != 12U) ||
        (head->op == OP_CACHE_PROBE && head->length != 12U) ||
        (head->op != OP_WEIGHTS && head->op != OP_RUN && head->op != OP_DIAG && head->op != OP_CACHE_PROBE)) return BAD_LENGTH;
    if (head->op == OP_RUN) {
        if (head->width == 0U || head->height == 0U || head->width > 65535U || head->height > 65535U ||
            head->repeat == 0U || head->repeat > MAX_REPEAT || head->frame > UINT32_MAX - (head->repeat - 1U)) return BAD_PARAMETERS;
    } else if (head->width != 0U || head->height != 0U || head->repeat != 1U) return BAD_PARAMETERS;
    return RESPONSE_OK;
}
static int send_response(const wire_header *request, terminal_snapshot *snap, uint32_t index,
                         uint32_t code, uint32_t count, uint32_t raw_count, int include_heads)
{
    uint8_t header[HEADER_BYTES] = {'S','2','B','U',1U,0U,0U,0U};
    uint32_t length = META_BYTES, box_index;
    uint64_t started = ticks();
    memset(response, 0, META_BYTES);
    put64(response, snap->epoch); put32(response + 8U, snap->status); put32(response + 12U, snap->error);
    put32(response + 16U, snap->reject); put32(response + 20U, raw_count); put32(response + 24U, count);
    put32(response + 28U, index); put32(response + 32U, request->repeat); put32(response + 36U, code);
    if (include_heads == 2) {
        memcpy(response + length, arena, 256U); length += 256U;
    } else if (include_heads == 1) {
        memcpy(response + length, arena + 0x01A46100U, HEAD13_BYTES); length += HEAD13_BYTES;
        memcpy(response + length, arena + 0x01AD5E80U, HEAD26_BYTES); length += HEAD26_BYTES;
        for (box_index = 0U; box_index < count; ++box_index) {
            const s2a_t62_detection *box = boxes + box_index;
            put32(response + length, (uint32_t)box->class_id); put32(response + length + 4U, (uint32_t)box->source_order);
            put_double(response + length + 8U, box->score); put_double(response + length + 16U, box->x1);
            put_double(response + length + 24U, box->y1); put_double(response + length + 32U, box->x2);
            put_double(response + length + 40U, box->y2); length += 48U;
        }
    }
    header[6] = (uint8_t)request->op; header[7] = 0x80U;
    put32(header + 8U, request->sequence); put32(header + 12U, request->frame + index);
    put32(header + 16U, request->width); put32(header + 20U, request->height); put32(header + 24U, request->repeat);
    put32(header + 28U, length); put32(header + 32U, crc32_ieee(response, length)); put32(header + 36U, crc32_ieee(header, 36U));
    if (!send_bytes(header, HEADER_BYTES, started) || !send_bytes(response, length, started)) return 0;
    while (!uart_drain_done()) if (expired(started, 10U)) return 0;
    return 1;
}
static int acknowledge(const terminal_snapshot *expected)
{
    terminal_snapshot actual;
    if (!safe_snapshot(&actual) || actual.epoch != expected->epoch || actual.frame != expected->frame || actual.status != expected->status) return 0;
    csr_write(0x05CU, (uint32_t)expected->epoch); csr_write(0x060U, (uint32_t)(expected->epoch >> 32));
    csr_write(0x008U, 4U);
    return is_idle();
}
static int configure_start(uint32_t frame, uint32_t core_timeout, uint32_t drain_timeout, uint32_t input_bytes, uint64_t *expected)
{
    uint64_t before;
    if (!is_idle() || !read_epoch(&before) || before == UINT64_MAX) return 0;
    csr_write(0x014U, frame); csr_write(0x018U, 0U); csr_write(0x01CU, input_bytes);
    csr_write(0x020U, 0x00100000U); csr_write(0x024U, WEIGHT_BYTES);
    csr_write(0x028U, core_timeout); csr_write(0x02CU, drain_timeout); barrier(); csr_write(0x008U, 1U);
    *expected = before + 1U;
    return 1;
}
static int wait_safe(terminal_snapshot *snap, uint64_t expected, uint32_t frame)
{
    uint64_t started = ticks();
    while (!safe_snapshot(snap)) {
        uint32_t status = csr_read(0x00CU);
        if ((status & 7U) == FAULT_ISOLATED || expired(started, 400U)) {
            snap->status = status; snap->error = csr_read(0x010U); snap->reject = csr_read(0x064U);
            (void)read_epoch(&snap->epoch);
            return 0;
        }
    }
    return snap->epoch == expected && snap->frame == frame;
}
static int infer_one(const wire_header *request, uint32_t index, uint32_t core_timeout, uint32_t drain_timeout)
{
    terminal_snapshot snap = {0U,0U,0U,0U,0U};
    uint64_t epoch;
    size_t count = 0U, raw_count = 0U;
    uint32_t offset;
    int decoded;
    if (!is_idle()) return 0;
    prepare_cache();
    if (!configure_start(request->frame + index, core_timeout, drain_timeout, INPUT_BYTES, &epoch)) return 0;
    if (!wait_safe(&snap, epoch, request->frame + index)) {
        (void)send_response(request, &snap, index, OBSERVE_TIMEOUT, 0U, 0U, 0); return 0;
    }
    feature_invalidate();
    if ((snap.status & 7U) != DONE_SAFE) {
        if (send_response(request, &snap, index, BOARD_ERROR, 0U, 0U, 0)) (void)acknowledge(&snap);
        return 0;
    }
    for (offset = 0U; offset < HEAD13_BYTES; ++offset) logits13[offset] = (double)(int8_t)arena[0x01A46100U + offset] * S2B_HEAD13_SCALE;
    for (offset = 0U; offset < HEAD26_BYTES; ++offset) logits26[offset] = (double)(int8_t)arena[0x01AD5E80U + offset] * S2B_HEAD26_SCALE;
    decoded = s2a_t62_decode_nms(logits13, HEAD13_BYTES, logits26, HEAD26_BYTES,
                                request->width, request->height, 0.25, boxes, 15U, &count, &raw_count);
    if (decoded != S2A_T62_OK) {
        (void)send_response(request, &snap, index, DECODE_ERROR, 0U, 0U, 0); return 0;
    }
    if (!send_response(request, &snap, index, RESPONSE_OK, (uint32_t)count, (uint32_t)raw_count, 1)) return 0;
    return acknowledge(&snap);
}
static int diagnostic(const wire_header *request)
{
    uint32_t mode = get32(staging), core = get32(staging + 4U), drain = get32(staging + 8U);
    terminal_snapshot snap = {0U,0U,0U,0U,0U};
    uint64_t epoch;
    if (mode == 0U) {
        snap.status = csr_read(0x00CU); snap.error = csr_read(0x010U); snap.reject = csr_read(0x064U);
        if (!read_epoch(&snap.epoch)) return 0;
        return send_response(request, &snap, 0U, RESPONSE_OK, 0U, 0U, 0);
    }
    if (mode > 2U || core == 0U || drain == 0U || (mode == 2U && (!weights_loaded || !input_loaded))) return 0;
    if (mode == 2U) prepare_cache();
    if (!configure_start(request->frame, core, drain, mode == 1U ? INPUT_BYTES - 1U : INPUT_BYTES, &epoch)) return 0;
    /* ABORT只在真正ARMING/RUN状态发出；不对已终态执行会产生SLVERR的命令。 */
    if (mode == 2U) {
        uint32_t state = csr_read(0x00CU) & 7U;
        if (state == 1U || state == 2U) csr_write(0x008U, 2U);
        else return 0;
    }
    if (!wait_safe(&snap, epoch, request->frame)) {
        (void)send_response(request, &snap, 0U, OBSERVE_TIMEOUT, 0U, 0U, 0); return 0;
    }
    feature_invalidate();
    if ((snap.status & 7U) != ERROR_SAFE || snap.error != (mode == 1U ? 3U : 8U)) {
        (void)send_response(request, &snap, 0U, BOARD_ERROR, 0U, 0U, 0); return 0;
    }
    if (!send_response(request, &snap, 0U, RESPONSE_OK, 0U, 0U, 0)) return 0;
    return acknowledge(&snap);
}
static int cache_probe(const wire_header *request)
{
    uint32_t phase = get32(staging), cpu_seed = get32(staging + 4U), dap_seed = get32(staging + 8U), index;
    terminal_snapshot snap = {0U,0U,0U,0U,0U};
    uint64_t epoch;
    if (!is_idle() || !read_epoch(&epoch) || epoch != 0U || weights_loaded || input_loaded || request->frame != 0U) return 0;
    snap.status = csr_read(0x00CU);
    if (phase == 0U && !cache_probe_wait && cpu_seed != dap_seed) {
        cache_cpu_seed = cpu_seed; cache_dap_seed = dap_seed; cache_probe_wait = 1;
        for (index = 0U; index < 64U; ++index) put32(arena + index * 4U, cpu_seed ^ (0x9E3779B9U * index));
        barrier(); flush_range(0U, 256U); barrier();
        return send_response(request, &snap, 0U, RESPONSE_OK, 0U, 0U, 2);
    }
    if (phase != 1U || !cache_probe_wait || cpu_seed != cache_cpu_seed || dap_seed != cache_dap_seed) {
        /* 顺序/身份失败也保留真实256B，随后永久停止；不进入LOAD或RUN。 */
        (void)send_response(request, &snap, 0U, BOARD_ERROR, 0U, 0U, 2); return 0;
    }
    barrier(); invalidate_range(0U, 256U); barrier();
    for (index = 0U; index < 64U; ++index) {
        if (get32(arena + index * 4U) != (dap_seed ^ (0x9E3779B9U * index))) {
            (void)send_response(request, &snap, 0U, BOARD_ERROR, 0U, 0U, 2); return 0;
        }
    }
    if (!is_idle() || !read_epoch(&epoch) || epoch != 0U) return 0;
    if (!send_response(request, &snap, 0U, RESPONSE_OK, 0U, 0U, 2)) return 0;
    cache_probe_wait = 0;
    return 1;
}
static int service_request(void)
{
    uint8_t header[HEADER_BYTES];
    wire_header request = {0U,0U,0U,0U,0U,1U,0U,0U};
    terminal_snapshot snap = {0U,0U,0U,0U,0U};
    uint32_t index, core, drain;
    int code;
    if (!receive_bytes(header, HEADER_BYTES, 1800U)) return 0;
    request.op = (uint16_t)header[6]; request.sequence = get32(header + 8U); request.frame = get32(header + 12U);
    code = encode_header(header, &request);
    if (code != 0) { (void)send_response(&request, &snap, 0U, (uint32_t)code, 0U, 0U, 0); return 0; }
    if (!is_idle()) { (void)send_response(&request, &snap, 0U, BAD_STATE, 0U, 0U, 0); return 0; }
    if (cache_probe_wait && request.op != OP_CACHE_PROBE) {
        (void)send_response(&request, &snap, 0U, BAD_STATE, 0U, 0U, 0); return 0;
    }
    if (!receive_bytes(staging, request.length, request.op == OP_WEIGHTS ? 900U : 120U)) return 0;
    if (crc32_ieee(staging, request.length) != request.payload_crc) {
        (void)send_response(&request, &snap, 0U, BAD_CRC, 0U, 0U, 0); return 0;
    }
    ++next_sequence;
    if (request.op == OP_CACHE_PROBE) return cache_probe(&request);
    if (request.op == OP_WEIGHTS) {
        if (memcmp(staging, "GFINT8W1", 8U) != 0) return 0;
        memcpy(arena + 0x00100000U, staging, WEIGHT_BYTES); weights_loaded = 1;
        snap.status = csr_read(0x00CU); (void)read_epoch(&snap.epoch);
        return send_response(&request, &snap, 0U, RESPONSE_OK, 0U, 0U, 0);
    }
    if (request.op == OP_DIAG) return diagnostic(&request);
    core = get32(staging); drain = get32(staging + 4U);
    if (!weights_loaded || core == 0U || drain == 0U) {
        (void)send_response(&request, &snap, 0U, BAD_PARAMETERS, 0U, 0U, 0); return 0;
    }
    memcpy(arena, staging + 8U, INPUT_BYTES); input_loaded = 1;
    for (index = 0U; index < request.repeat; ++index) if (!infer_one(&request, index, core, drain)) return 0;
    return 1;
}

#ifndef S2B_HOST_MOCK
static int initialise(void)
{
    XUartPs_Config *config = XUartPs_LookupConfig((UINTPTR)S2B_UART1_BASE);
    XUartPsFormat wanted = {115200U, XUARTPS_FORMAT_8_BITS, XUARTPS_FORMAT_NO_PARITY, XUARTPS_FORMAT_1_STOP_BIT}, actual;
    uint32_t control;
    if ((UINTPTR)arena != 0x10000000U || config == NULL || config->InputClockHz != 100000000U) return 0;
    /* 设置1MiB Device MMIO section；arena保持BSP唯一cacheable映射。 */
    Xil_SetTlbAttributes((INTPTR)CSR_BASE, DEVICE_MEMORY);
    Xil_DCacheEnable();
    __asm__ volatile("mrc p15, 0, %0, c1, c0, 0" : "=r"(control));
    if ((control & 4U) == 0U) return 0;
    /* SDT xiltimer第一次sleep实际启动global timer；CPU1必须已由总控停核。 */
    usleep(1U);
    if (XUartPs_CfgInitialize(&uart, config, (uint32_t)config->BaseAddress) != XST_SUCCESS) return 0;
    XUartPs_SetInterruptMask(&uart, 0U); XUartPs_SetOptions(&uart, 0U); XUartPs_SetOperMode(&uart, XUARTPS_OPER_MODE_NORMAL);
    if (XUartPs_SetDataFormat(&uart, &wanted) != XST_SUCCESS) return 0;
    XUartPs_GetDataFormat(&uart, &actual);
    if (actual.BaudRate != 115200U || actual.DataBits != wanted.DataBits || actual.Parity != wanted.Parity ||
        actual.StopBits != wanted.StopBits || (XUartPs_GetOptions(&uart) & XUARTPS_OPTION_SET_FCM) != 0U) return 0;
    if (csr_read(0U) != 0x53324250U || csr_read(4U) != 0x100U ||
        csr_read(0x030U) != 0x10000000U || csr_read(0x034U) != ARENA_BYTES ||
        csr_read(0x038U) != FEATURE_OFFSET || csr_read(0x03CU) != FEATURE_END ||
        csr_read(0x040U) != 0x01A46100U || csr_read(0x044U) != HEAD13_BYTES ||
        csr_read(0x048U) != 0x01AD5E80U || csr_read(0x04CU) != HEAD26_BYTES || !is_idle()) return 0;
    return 1;
}
int main(void)
{
    char banner[320];
    int length;
    uint64_t started;
    if (!initialise()) { publish(0xE001U); return 1; }
    length = snprintf(banner, sizeof(banner), "S2B-INFERENCE/1 READY SOURCE=%s XSA=%s MODEL=%s\r\n",
                      S2B_C_SOURCE_SHA256, S2B_XSA_SHA256, S2B_MODEL_SHA256);
    started = ticks();
    if (length <= 0 || (size_t)length >= sizeof(banner) || !send_bytes((const uint8_t *)banner, (uint32_t)length, started)) {
        publish(0xE002U); return 1;
    }
    publish(1U);
    while (service_request()) publish(2U);
    /* 失败保留所有权、账本和未ACK终态；不会复位PL或自动重新准入。 */
    publish(0xE003U);
    for (;;) __asm__ volatile("wfe" ::: "memory");
}
#endif
