/*
 * s4d_ps_app.c —— 阶段4 4-D PS 应用（S4-T32 范围扩展；离线可编译骨架）
 *
 * 职责（严格按 ADR §8.3/§8.4 冻结的 ABI）：
 *   · mailbox ABI：HOST_REQ / PS_ACK / PS_GEOM / PS_RESULT + X/Y 几何表 + JTAG_RAW_RESULT 结果区；
 *   · 预处理来源编译期开关：PREPROC_SRC=1 → PL（新块 CSR 0x43C00200..0x43C0027c）；=0 → PS 软件兜底；
 *   · infer_one_from_pl_tensor()：复用冻结网络入口，**跳过** CPU tensor memcpy 与输入 cache 写回；
 *   · 缓存语义：weights clean、feature flush+invalidate、head 输出 invalidate + DSB，64 B 外对齐；
 *   · pixel_format_code=1 → BGR888 必须经**显式映射表**，禁止直接 cast 到 s4_inject_pixel_format。
 *
 * 诚实边界（不得夸大）：
 *   · 解码入口：强实现，直调 r13 冻结参考 s2a_t62_decode_nms（head13/head26 取 arena 固定偏移）；
 *   · 网络启动入口：强实现，按冻结 2B CSR 语义写影子寄存器 + START 并轮询 TERMINAL/FAULT；
 *   · 仍未上板（板卡归阶段5）；不属于 G3。
 */

#include <stdint.h>
#include <string.h>

#include "xil_cache.h"
#include "xil_io.h"
#include "xil_printf.h"
#include "xparameters.h"

#include "s4d_geometry.h"   /* 唯一几何参数表 + 最近邻 letterbox（PL/SW 共用，禁止另写字面量） */
#include "s2a_ps_decode_nms_reference.h"   /* r13 冻结解码参考：强符号 s2a_t62_decode_nms */

/* ---------------- 地址与 ABI 常量（冻结，ADR §8.2/§8.4） ---------------- */
static const void *const s4d_keep_strong_symbols[3];

#define S4D_RAW_BASE      0x12000000u
#define S4D_RAW_BYTES     12582912u
#define S4D_META_BASE     0x12C00000u
#define S4D_META_BYTES    32768u
#define S4D_TENSOR_BASE   0x10000000u
#define S4D_TENSOR_BYTES  519168u
#define S4D_CSR_BASE      0x43C00000u

#define S4D_META_HOST_REQ    (S4D_META_BASE + 0x0000u)
#define S4D_META_PS_ACK      (S4D_META_BASE + 0x0080u)
#define S4D_META_PS_GEOM     (S4D_META_BASE + 0x00C0u)
#define S4D_META_PS_RESULT   (S4D_META_BASE + 0x0100u)
#define S4D_META_X_TABLE     (S4D_META_BASE + 0x0140u)
#define S4D_META_Y_TABLE     (S4D_META_BASE + 0x2840u)
#define S4D_META_JTAG_RESULT (S4D_META_BASE + 0x4F40u)

#define S4D_MAGIC_REQ    0x52423453u  /* S4BR */
#define S4D_MAGIC_ACK    0x41423453u  /* S4BA */
#define S4D_MAGIC_GEOM   0x47423453u  /* S4BG */
#define S4D_MAGIC_RESULT 0x53423453u  /* S4BS */
#define S4D_ABI_VERSION  1u

/* 新 AXI4-Lite 块（相对 0x43C00000） */
#define S4D_REG_ID           (S4D_CSR_BASE + 0x200u)
#define S4D_REG_VERSION      (S4D_CSR_BASE + 0x204u)
#define S4D_REG_STATUS       (S4D_CSR_BASE + 0x208u)
#define S4D_REG_COMMAND      (S4D_CSR_BASE + 0x20Cu)
#define S4D_REG_SESSION_ID   (S4D_CSR_BASE + 0x210u)
#define S4D_REG_FRAME_ID     (S4D_CSR_BASE + 0x214u)
#define S4D_REG_WIDTH        (S4D_CSR_BASE + 0x218u)
#define S4D_REG_HEIGHT       (S4D_CSR_BASE + 0x21Cu)
#define S4D_REG_STRIDE       (S4D_CSR_BASE + 0x220u)
#define S4D_REG_PIXFMT_CODE  (S4D_CSR_BASE + 0x224u)
#define S4D_REG_LOGICAL      (S4D_CSR_BASE + 0x228u)
#define S4D_REG_STORAGE      (S4D_CSR_BASE + 0x22Cu)
#define S4D_REG_RAW_CRC      (S4D_CSR_BASE + 0x230u)
#define S4D_REG_GEOM_VER     (S4D_CSR_BASE + 0x234u)
#define S4D_REG_GEOM_BYTES   (S4D_CSR_BASE + 0x238u)
#define S4D_REG_GEOM_CRC     (S4D_CSR_BASE + 0x23Cu)
#define S4D_REG_NEW_W        (S4D_CSR_BASE + 0x240u)
#define S4D_REG_NEW_H        (S4D_CSR_BASE + 0x244u)
#define S4D_REG_PAD_L        (S4D_CSR_BASE + 0x248u)
#define S4D_REG_PAD_T        (S4D_CSR_BASE + 0x24Cu)
#define S4D_REG_TIMER_FREQ   (S4D_CSR_BASE + 0x250u)
#define S4D_REG_BEGIN_LO     (S4D_CSR_BASE + 0x254u)
#define S4D_REG_BEGIN_HI     (S4D_CSR_BASE + 0x258u)
#define S4D_REG_RAW_BASE     (S4D_CSR_BASE + 0x25Cu)
#define S4D_REG_RAW_CAP      (S4D_CSR_BASE + 0x260u)
#define S4D_REG_META_BASE    (S4D_CSR_BASE + 0x264u)
#define S4D_REG_GEOM_BASE    (S4D_CSR_BASE + 0x268u)
#define S4D_REG_TENSOR_BASE  (S4D_CSR_BASE + 0x26Cu)
#define S4D_REG_TENSOR_BYTES (S4D_CSR_BASE + 0x270u)
#define S4D_REG_RESULT_SEQ   (S4D_CSR_BASE + 0x274u)

#define S4D_CMD_START_PREPROC        1u
#define S4D_CMD_CANCEL_AND_DRAIN     2u
#define S4D_CMD_ACK_SAFE_ERROR       4u
#define S4D_CMD_START_NET_FROM_TOKEN 8u

#define S4D_ST_TENSOR_VALID  (1u << 8)
#define S4D_ST_DESC_VALID    (1u << 9)
#define S4D_ST_ERROR         (1u << 10)
#define S4D_ST_ISOLATED      (1u << 11)
#define S4D_ST_LEDGER_EMPTY  (1u << 12)
#define S4D_ST_BOTH_EMPTY    (1u << 13)

#ifndef PREPROC_SRC
#define PREPROC_SRC 0   /* 0 = PS 软件预处理（兜底）；1 = PL 新块 */
#endif

/* ---------------- mailbox record（小端、固定宽度；packed） ---------------- */
typedef struct __attribute__((packed)) {
    uint32_t magic, version, session_id, frame_id;
    uint32_t width, height, stride_bytes, pixfmt_code;
    uint32_t logical_bytes, storage_bytes, raw_crc32;
    uint32_t geom_version, geom_bytes, geom_crc32;
    uint32_t new_width, new_height, pad_left, pad_top;
    uint32_t timer_freq_hz, begin_tick_lo, begin_tick_hi;
    uint32_t reserved[10];
    uint32_t crc32;
} s4d_host_req_t;   /* 128 B（32 字） */

typedef struct __attribute__((packed)) {
    uint32_t magic, version, session_id, frame_id, ack_code, reserved[10], crc32;
} s4d_ack_t;        /* 64 B（16 字） */

typedef struct __attribute__((packed)) {
    uint32_t magic, version, session_id, frame_id;
    uint32_t new_width, new_height, pad_left, pad_top;
    uint32_t geometry_version, geometry_bytes, geometry_crc32;
    uint32_t tensor_base, tensor_bytes;
    uint32_t reserved[2], crc32;
} s4d_geom_t;       /* 64 B（16 字） */

typedef struct __attribute__((packed)) {
    uint32_t magic, version, session_id, frame_id, result_seq;
    uint32_t phys_status, error_code, last_reject;
    uint32_t raw_candidate_count, box_count;
    uint64_t tensor_sha_prefix[2];
    uint32_t reserved[1], crc32;
} s4d_result_t;     /* 64 B */

_Static_assert(sizeof(s4d_host_req_t) == 128, "HOST_REQ must be 128 B");
_Static_assert(sizeof(s4d_ack_t) == 64, "PS_ACK must be 64 B");
_Static_assert(sizeof(s4d_geom_t) == 64, "PS_GEOM must be 64 B");
_Static_assert(sizeof(s4d_result_t) == 64, "PS_RESULT must be 64 B");

/* ---------------- 像素格式显式映射（禁止 cast） ---------------- */
typedef enum { S4D_PIXFMT_UNKNOWN = 0, S4D_PIXFMT_BGR888 = 1 } s4d_pixfmt_t;

static s4d_pixfmt_t s4d_pixfmt_from_code(uint32_t code)
{
    switch (code) {
    case 1u: return S4D_PIXFMT_BGR888;   /* mailbox 编码 1 = BGR888 */
    default: return S4D_PIXFMT_UNKNOWN;
    }
}

/* ---------------- CRC-32/ISO-HDLC（= zlib.crc32） ---------------- */
uint32_t s4d_crc32(const void *data, uint32_t len)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFu;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= p[i];
        for (int b = 0; b < 8; b++) {
            crc = (crc >> 1) ^ (0xEDB88320u & (uint32_t)(-(int32_t)(crc & 1u)));
        }
    }
    return ~crc;
}

/* ---------------- 缓存维护（64 B 外对齐 + DSB） ---------------- */
static void s4d_align64(uint32_t addr, uint32_t len, uint32_t *a0, uint32_t *alen)
{
    *a0 = addr & ~63u;
    *alen = ((addr + len + 63u) & ~63u) - *a0;
}

void s4d_region_flush(uint32_t addr, uint32_t len)
{
    uint32_t a0, alen;
    s4d_align64(addr, len, &a0, &alen);
    Xil_DCacheFlushRange((INTPTR)a0, (UINTPTR)alen);
    __asm__ volatile("dsb sy" ::: "memory");
}

void s4d_region_invalidate(uint32_t addr, uint32_t len)
{
    uint32_t a0, alen;
    s4d_align64(addr, len, &a0, &alen);
    Xil_DCacheInvalidateRange((INTPTR)a0, (UINTPTR)alen);
    __asm__ volatile("dsb sy" ::: "memory");
}

void s4d_region_flush_invalidate(uint32_t addr, uint32_t len)
{
    uint32_t a0, alen;
    s4d_align64(addr, len, &a0, &alen);
    Xil_DCacheFlushRange((INTPTR)a0, (UINTPTR)alen);
    Xil_DCacheInvalidateRange((INTPTR)a0, (UINTPTR)alen);
    __asm__ volatile("dsb sy" ::: "memory");
}


/* ---------------- 预处理 ---------------- */
#if PREPROC_SRC
/* PL 路径：写 CSR shadows 并触发 START_PREPROC，等待 tensor-valid（不见高端"HP0 安静"） */
static int s4d_preproc_pl(const s4d_host_req_t *req)
{
    Xil_Out32(S4D_REG_SESSION_ID, req->session_id);
    Xil_Out32(S4D_REG_FRAME_ID, req->frame_id);
    Xil_Out32(S4D_REG_WIDTH, req->width);
    Xil_Out32(S4D_REG_HEIGHT, req->height);
    Xil_Out32(S4D_REG_STRIDE, req->stride_bytes);
    Xil_Out32(S4D_REG_PIXFMT_CODE, req->pixfmt_code);
    Xil_Out32(S4D_REG_LOGICAL, req->logical_bytes);
    Xil_Out32(S4D_REG_STORAGE, req->storage_bytes);
    Xil_Out32(S4D_REG_RAW_CRC, req->raw_crc32);
    Xil_Out32(S4D_REG_GEOM_VER, req->geom_version);
    Xil_Out32(S4D_REG_GEOM_BYTES, req->geom_bytes);
    Xil_Out32(S4D_REG_GEOM_CRC, req->geom_crc32);
    Xil_Out32(S4D_REG_NEW_W, req->new_width);
    Xil_Out32(S4D_REG_NEW_H, req->new_height);
    Xil_Out32(S4D_REG_PAD_L, req->pad_left);
    Xil_Out32(S4D_REG_PAD_T, req->pad_top);
    Xil_Out32(S4D_REG_TIMER_FREQ, req->timer_freq_hz);
    Xil_Out32(S4D_REG_BEGIN_LO, req->begin_tick_lo);
    Xil_Out32(S4D_REG_BEGIN_HI, req->begin_tick_hi);
    Xil_Out32(S4D_REG_COMMAND, S4D_CMD_START_PREPROC);
    for (uint32_t spin = 0; spin < 2000000u; spin++) {
        uint32_t st = Xil_In32(S4D_REG_STATUS);
        if (st & S4D_ST_ERROR) { return -2; }
        if ((st & S4D_ST_TENSOR_VALID) && (st & S4D_ST_BOTH_EMPTY)) { return 0; }
    }
    return -3;   /* 超时 */
}
#endif

/* PS 软件路径（v1 关键路径）：与 PL 版**同一参数表**的最近邻 letterbox + BGR→RGB + INT8 打包 */
__attribute__((unused)) static int s4d_preproc_sw(const s4d_host_req_t *req)
{
    if (s4d_pixfmt_from_code(req->pixfmt_code) != S4D_PIXFMT_BGR888) {
        return -4;   /* 未知像素格式：拒绝，不猜 */
    }
    if (req->logical_bytes > S4D_RAW_BYTES) { return -5; }
    s4d_region_invalidate(S4D_RAW_BASE, req->logical_bytes > 0 ? req->logical_bytes : S4D_RAW_BYTES);
    if (s4d_letterbox_pack((const uint8_t *)(uintptr_t)S4D_RAW_BASE,
                           (int8_t *)(uintptr_t)S4D_TENSOR_BASE) != 0) {
        return -6;
    }
    s4d_region_flush(S4D_TENSOR_BASE, S4D_TENSOR_BYTES);
    return 0;
}

/* ================= M4-b 自检模式（语义全部取自 r13 应用源码） =================
 * 见 docs/stage4/S4D_m4b_csr_semantics_20261027_r01.md（逐项标出处行号）。
 * 关键点：0x008 是命令编码（1=START、4=ACK）；状态在 0x00C[2:0]（0 IDLE/1 ARMING/2 RUN/
 * 4 DONE_SAFE/5 ERROR_SAFE/6 FAULT_ISOLATED），另 bit8 OWNER_PL、bit9 HEAD_VALID、
 * bit10 SAFE_REUSE、bit11 TERMINAL、bit12 AXI_PENDING、bit13 FIRST_PENDING；
 * epoch 由 0x050/0x054 双读校验；ACK 写 0x05C/0x060 后再写 0x008=4。
 * 参考数据（host 预置到 RAW 区）：head13 期望在 RAW+0x0000（5,070 B），
 * head26 期望在 RAW+0x2000（20,280 B）。
 */
#define S4D_CR(off)   (S4D_CSR_BASE + (off))
#define S4D_CSR_ID          S4D_CR(0x000u)
#define S4D_CSR_VER         S4D_CR(0x004u)
#define S4D_CSR_CMD         S4D_CR(0x008u)
#define S4D_CSR_STATUS      S4D_CR(0x00Cu)
#define S4D_CSR_ERROR       S4D_CR(0x010u)
#define S4D_CSR_FRAME_W     S4D_CR(0x014u)
#define S4D_CSR_INADDR_W    S4D_CR(0x018u)   /* input_addr（r13 写 0 = arena+0） */
#define S4D_CSR_INBYTES_W   S4D_CR(0x01Cu)
#define S4D_CSR_WADDR_W     S4D_CR(0x020u)   /* weight_addr（r13 写 0x00100000） */
#define S4D_CSR_WBYTES_W    S4D_CR(0x024u)
#define S4D_CSR_CORETO_W    S4D_CR(0x028u)
#define S4D_CSR_DRAINTO_W   S4D_CR(0x02Cu)
#define S4D_CSR_EPOCH_LO    S4D_CR(0x050u)
#define S4D_CSR_EPOCH_HI    S4D_CR(0x054u)
#define S4D_CSR_FRAME_R     S4D_CR(0x014u)   /* RTL 读映射：0x014=frame */
#define S4D_CSR_ACKLO_W     S4D_CR(0x05Cu)
#define S4D_CSR_ACKHI_W     S4D_CR(0x060u)
#define S4D_CSR_REJECT_R    S4D_CR(0x064u)

#define S4D_CMD_START  1u
#define S4D_CMD_ACK    4u
#define S4D_ST_IDLE    0u
#define S4D_ST_ARMING  1u
#define S4D_ST_RUN     2u
#define S4D_ST_DONE    4u
#define S4D_ST_ERROR   5u
#define S4D_ST_FAULT   6u
#define S4D_OWNER_PL   (1u << 8)
#define S4D_HEAD_VALID (1u << 9)
#define S4D_SAFE_REUSE (1u << 10)
#define S4D_TERMINAL   (1u << 11)
#define S4D_AXI_PEND   (1u << 12)
#define S4D_FIRST_PEND (1u << 13)

#define S4D_INPUT_BYTES   519168u
#define S4D_WEIGHT_BYTES  5903100u
#define S4D_HEAD13_OFF    0x01A46100u
#define S4D_HEAD13_BYTES  5070u
#define S4D_HEAD26_OFF    0x01AD5E80u
#define S4D_HEAD26_BYTES  20280u
#define S4D_INPUT_BASE    0x00100000u

/* ---------------- 解码入口：强实现（r13 冻结参考；head13/head26 取自 arena 固定偏移） ---------------- */
#define S4D_DEC_SCORE_TH   0.25
#define S4D_DEC_MAX_BOX    15u
#define S4D_HEAD13_SCALE   (0.24267549589862975)
#define S4D_HEAD26_SCALE   (0.30223452951025775)

static double s4d_logits13[S4D_HEAD13_BYTES];
static double s4d_logits26[S4D_HEAD26_BYTES];
static uint32_t s4d_cur_src_w = 640u;
static uint32_t s4d_cur_src_h = 480u;
uint32_t s4d_last_box_count;
uint32_t s4d_last_raw_candidates;

int s2a_decode_nms_reference(const int8_t *heads, uint32_t session_id, uint32_t frame_id,
                             void *out_boxes, uint32_t *out_count)
{
    s2a_t62_detection det[S4D_DEC_MAX_BOX];
    const int8_t *h13 = (const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF);
    const int8_t *h26 = (const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD26_OFF);
    size_t count = 0u, raw = 0u;
    int rc;
    uint32_t i;
    if (heads == NULL) { if (out_count) { *out_count = 0u; } return S2A_T62_INVALID_ARGUMENT; }
    (void)heads;   /* 语义：head13/head26 由 arena 固定偏移给出（r13 同源） */
    for (i = 0u; i < S4D_HEAD13_BYTES; i++) {
        s4d_logits13[i] = (double)h13[i] * S4D_HEAD13_SCALE;
    }
    for (i = 0u; i < S4D_HEAD26_BYTES; i++) {
        s4d_logits26[i] = (double)h26[i] * S4D_HEAD26_SCALE;
    }
    rc = s2a_t62_decode_nms(s4d_logits13, S4D_HEAD13_BYTES, s4d_logits26, S4D_HEAD26_BYTES,
                            s4d_cur_src_w, s4d_cur_src_h, S4D_DEC_SCORE_TH,
                            det, S4D_DEC_MAX_BOX, &count, &raw);
    s4d_last_box_count = (uint32_t)count;
    s4d_last_raw_candidates = (uint32_t)raw;
    if (rc == S2A_T62_OK && out_boxes != NULL && count > 0u) {
        memcpy(out_boxes, det, count * sizeof(det[0]));
    }
    if (out_count) { *out_count = (uint32_t)count; }
    (void)session_id; (void)frame_id;
    return rc;
}



static inline uint32_t s4d_rd(uint32_t addr) { return Xil_In32(addr); }
static inline void s4d_wr(uint32_t addr, uint32_t v)
{
    Xil_Out32(addr, v);
    __asm__ volatile("dsb sy" ::: "memory");
}
static inline void s4d_dsb(void) { __asm__ volatile("dsb sy" ::: "memory"); }

static int s4d_read_epoch(uint64_t *epoch)
{
    unsigned int r;
    for (r = 0; r < 8u; r++) {
        uint32_t hi = s4d_rd(S4D_CSR_EPOCH_HI), lo = s4d_rd(S4D_CSR_EPOCH_LO);
        if (hi == s4d_rd(S4D_CSR_EPOCH_HI)) {
            *epoch = ((uint64_t)hi << 32) | lo;
            return 1;
        }
    }
    return 0;
}

static int s4d_is_idle(void)
{
    uint32_t st = s4d_rd(S4D_CSR_STATUS);
    return ((st & 7u) == S4D_ST_IDLE) && ((st & S4D_SAFE_REUSE) != 0u) &&
           ((st & (S4D_OWNER_PL | S4D_AXI_PEND | S4D_HEAD_VALID | S4D_TERMINAL | S4D_FIRST_PEND)) == 0u);
}

static int s4d_safe_done(uint32_t *status_out, uint32_t *error_out)
{
    uint32_t st = s4d_rd(S4D_CSR_STATUS);
    uint32_t state = st & 7u;
    uint32_t err = s4d_rd(S4D_CSR_ERROR);
    if ((state != S4D_ST_DONE && state != S4D_ST_ERROR) ||
        (st & (S4D_SAFE_REUSE | S4D_TERMINAL)) != (S4D_SAFE_REUSE | S4D_TERMINAL) ||
        (st & (S4D_OWNER_PL | S4D_AXI_PEND | S4D_FIRST_PEND)) != 0u) {
        if (status_out) *status_out = st;
        return 0;
    }
    if (status_out) *status_out = st;
    if (error_out) *error_out = err;
    if (state == S4D_ST_DONE) return ((st & S4D_HEAD_VALID) != 0u && err == 0u) ? 1 : 0;
    return ((st & S4D_HEAD_VALID) == 0u && err != 0u) ? 2 : 0;   /* 2 = 合法 ERROR_SAFE */
}

/* ---------------- 网络启动入口：强实现（2B CSR 冻结语义；替换 weak 桩） ---------------- */
int s2b_network_start_from_tensor(uint32_t session_id, uint32_t frame_id)
{
    uint64_t epoch = 0u;
    uint32_t spin;
    if (!s4d_is_idle()) { return -2; }
    if (!s4d_read_epoch(&epoch) || epoch == UINT64_MAX) { return -3; }
    s4d_wr(S4D_CSR_FRAME_W, frame_id);
    s4d_wr(S4D_CSR_INADDR_W, 0u);
    s4d_wr(S4D_CSR_INBYTES_W, S4D_INPUT_BYTES);
    s4d_wr(S4D_CSR_WADDR_W, S4D_INPUT_BASE);
    s4d_wr(S4D_CSR_WBYTES_W, S4D_WEIGHT_BYTES);
    s4d_wr(S4D_CSR_CORETO_W, 400u);
    s4d_wr(S4D_CSR_DRAINTO_W, 400u);
    s4d_wr(S4D_CSR_CMD, S4D_CMD_START);
    for (spin = 0u; spin < 200000000u; spin++) {
        uint32_t st = s4d_rd(S4D_CSR_STATUS);
        uint32_t state = st & 7u;
        if ((st & S4D_TERMINAL) != 0u) {
            return (state == S4D_ST_DONE) ? 0 : -4;
        }
        if (state == S4D_ST_FAULT) { return -5; }
    }
    (void)session_id;
    return -6;
}

static uint32_t s4d_count_diff(const uint8_t *a, const uint8_t *b, uint32_t n, uint32_t *first)
{
    uint32_t i, d = 0;
    for (i = 0; i < n; i++) {
        if (a[i] != b[i]) { if (d == 0u && first) { *first = i; } d++; }
    }
    return d;
}

int s4d_m4b_selfcheck(void)
{
    xil_printf("M4B STEP=0 enter\r\n");
    const uint8_t *arena = (const uint8_t *)(uintptr_t)S4D_TENSOR_BASE;   /* 0x10000000 */
    const uint8_t *ref = (const uint8_t *)(uintptr_t)S4D_RAW_BASE;        /* host 预置参考 */
    uint64_t epoch_before = 0, epoch = 0;
    uint32_t st = 0, err = 0, spin = 0;
    int stale = 0, gate = 0, done = 0, idle_after_ack = 0;
    uint32_t d13 = 0, d26 = 0, f13 = 0xFFFFFFFFu, f26 = 0xFFFFFFFFu;
    uint32_t frame = 1u;

    xil_printf("M4B STEP=1 read CSR_ID addr=0x%08x\r\n", (unsigned)S4D_CSR_ID);
    xil_printf("M4B CSR id=0x%08x ver=0x%08x\r\n",
               (unsigned)s4d_rd(S4D_CSR_ID), (unsigned)s4d_rd(S4D_CSR_VER));

    xil_printf("M4B STEP=2 check idle: status=0x%08x\r\n", (unsigned)s4d_rd(S4D_CSR_STATUS));
    if (!s4d_is_idle()) {
        xil_printf("M4B RESULT={\"pass\":0,\"reason\":\"not_idle\",\"status\":%u}\r\n",
                   (unsigned)s4d_rd(S4D_CSR_STATUS));
        return -1;
    }

    /* 陈旧检测：运行前 head13 与参考不同才可判新旧 */
    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, 64);
    stale = (arena[S4D_HEAD13_OFF] != ref[0] || arena[S4D_HEAD13_OFF + 1] != ref[1]) ? 1 : 0;

    xil_printf("M4B STEP=3 read epoch\r\n");
    if (!s4d_read_epoch(&epoch_before)) { xil_printf("M4B RESULT={\"pass\":0,\"reason\":\"epoch_read_fail\"}\r\n"); return -1; }
    epoch = epoch_before + 1u;

    /* prepare_cache：输入/权重 flush（64 B 外对齐），前后 DSB */
    s4d_region_flush(S4D_TENSOR_BASE, S4D_INPUT_BYTES);
    s4d_region_flush(S4D_TENSOR_BASE + S4D_INPUT_BASE, S4D_WEIGHT_BYTES);
    s4d_dsb();

    xil_printf("M4B STEP=4 cache flush done\r\n");
    /* configure_start（r13 顺序与偏移） */
    s4d_wr(S4D_CSR_FRAME_W, frame);
    s4d_wr(S4D_CSR_INADDR_W, 0u);
    s4d_wr(S4D_CSR_INBYTES_W, S4D_INPUT_BYTES);
    s4d_wr(S4D_CSR_WADDR_W, S4D_INPUT_BASE);
    s4d_wr(S4D_CSR_WBYTES_W, S4D_WEIGHT_BYTES);
    s4d_wr(S4D_CSR_CORETO_W, 400u);
    s4d_wr(S4D_CSR_DRAINTO_W, 400u);
    s4d_wr(S4D_CSR_CMD, S4D_CMD_START);

    xil_printf("M4B STEP=5 START cmd written\r\n");
    /* 完成序门控：START 后第一拍快照 */
    st = s4d_rd(S4D_CSR_STATUS);
    if (((st & 7u) == S4D_ST_ARMING || (st & 7u) == S4D_ST_RUN) &&
        (st & S4D_OWNER_PL) != 0u && (st & (S4D_HEAD_VALID | S4D_TERMINAL | S4D_SAFE_REUSE)) == 0u) {
        gate = 1;   /* BLOCKED：可观测到"运行中、结果未有效" */
    } else if ((st & 7u) == S4D_ST_DONE) {
        gate = 2;   /* INCONCLUSIVE：首拍已 DONE，无法证明门控 */
    }

    /* 等待安全终态（超时即 FAIL，不重试） */
    for (spin = 0; spin < 50000000u; spin++) {
        int r = s4d_safe_done(&st, &err);
        if (r == 1) { done = 1; break; }
    if (done == 0) {
        xil_printf("M4B STEP=6 TIMEOUT wait spin=%u status=0x%08x error=0x%08x\r\n",
                   (unsigned)spin, (unsigned)st, (unsigned)err);
    } else {
        xil_printf("M4B STEP=6 wait done=%d status=0x%08x error=0x%08x\r\n",
                   done, (unsigned)st, (unsigned)err);
    }
        if (r == 2) { done = 2; break; }
        if ((st & 7u) == S4D_ST_FAULT) break;
    }

    /* PL→PS 可见性：invalidate 后逐字节比对 head13/head26 */
    xil_printf("M4B STEP=7 compare heads (done=%d)\r\n", done);
    if (done == 1) {
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
        d13 = s4d_count_diff(arena + S4D_HEAD13_OFF, ref, S4D_HEAD13_BYTES, &f13);
        d26 = s4d_count_diff(arena + S4D_HEAD26_OFF, ref + 0x2000u, S4D_HEAD26_BYTES, &f26);
        xil_printf("M4B HEADS diff13=%u first13=%d diff26=%u first26=%d\r\n",
                   (unsigned)d13, (d13 == 0u) ? -1 : (int)f13,
                   (unsigned)d26, (d26 == 0u) ? -1 : (int)f26);
    }

    /* ACK 收尾：safe snapshot 匹配 → 0x05C/0x060 → 0x008=4 → is_idle */
    xil_printf("M4B STEP=8 ACK phase (idle_before=%d)\r\n", s4d_is_idle());
    if (done == 1) {
        uint64_t e2 = 0;
        uint32_t st2 = s4d_rd(S4D_CSR_STATUS);
        if (s4d_read_epoch(&e2) && e2 == epoch && s4d_rd(S4D_CSR_FRAME_R) == frame) {
            s4d_wr(S4D_CSR_ACKLO_W, (uint32_t)epoch);
            s4d_wr(S4D_CSR_ACKHI_W, (uint32_t)(epoch >> 32));
            s4d_wr(S4D_CSR_CMD, S4D_CMD_ACK);
            idle_after_ack = s4d_is_idle();
        }
        (void)st2;
    }

    xil_printf("M4B RESULT={\"pass\":%d,\"done\":%d,\"diff13\":%u,\"diff26\":%u,"
               "\"first13\":%d,\"first26\":%d,\"stale\":%d,\"gate\":%d,"
               "\"ack_idle\":%d,\"epoch\":%u,\"status\":%u,\"error\":%u}\r\n",
               (done == 1 && d13 == 0u && d26 == 0u && stale == 1 && gate == 1 && idle_after_ack == 1) ? 1 : 0,
               done, (unsigned)d13, (unsigned)d26,
               (d13 == 0u) ? -1 : (int)f13, (d26 == 0u) ? -1 : (int)f26,
               stale, gate, idle_after_ack,
               (unsigned)(uint32_t)epoch, (unsigned)st, (unsigned)err);
    return (done == 1 && d13 == 0u && d26 == 0u && stale == 1 && gate == 1 && idle_after_ack == 1) ? 0 : -2;
}

/* ---------------- infer_one_from_pl_tensor：跳过 CPU memcpy / 输入写回 ---------------- */
int infer_one_from_pl_tensor(const s4d_host_req_t *req)
{
    int rc;
    /* 1) PL 已写 tensor：只做 invalidate，绝不 memcpy 覆盖 */
    s4d_region_invalidate(S4D_TENSOR_BASE, S4D_TENSOR_BYTES);
    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
    /* 2) 源图尺寸用于解码裁剪/坐标还原（ABI 未给时用 640x480 约定） */
    if (req->width != 0u && req->height != 0u) {
        s4d_cur_src_w = req->width; s4d_cur_src_h = req->height;
    }
    /* 3) 强实现：冻结 2B CSR 语义启动网络（不再返回 -1 桩值） */
    rc = s2b_network_start_from_tensor(req->session_id, req->frame_id);
    if (rc != 0) { return rc; }
    __asm__ volatile("dsb sy" ::: "memory");
    /* 4) 复用 r13 冻结解码参考；head13/head26 来自 arena 固定偏移（非连续） */
    (void)s2a_decode_nms_reference((const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF),
                                  req->session_id, req->frame_id, NULL, NULL);
    return 0;
}

/* ---------------- 主循环：轮询 HOST_REQ → 预处理 → 推理 → 发布 PS_RESULT ---------------- */
int main(void)
{
    /* 保活解码/启动强符号，防止仅自检变体被 --gc-sections 裁掉 */
    __asm__ volatile("" : : "r"(s4d_keep_strong_symbols[0]) : "memory");
    xil_printf("\r\nS4D PS APP: PREPROC_SRC=%d ABI=%u\r\n", PREPROC_SRC, S4D_ABI_VERSION);
#if defined(S4D_M4B_SELFCHECK) && S4D_M4B_SELFCHECK
    xil_printf("S4D MODE=M4B_SELFCHECK geom=%s\r\n", S4D_GEOM.name);
    (void)s4d_m4b_selfcheck();
    for (;;) { }
#endif
    uint32_t last_frame = 0xFFFFFFFFu;
    uint32_t result_seq = 0;

    for (;;) {
        const s4d_host_req_t *req = (const s4d_host_req_t *)(uintptr_t)S4D_META_HOST_REQ;
        s4d_region_invalidate(S4D_META_HOST_REQ, sizeof(*req));
        if (req->magic != S4D_MAGIC_REQ || req->version != S4D_ABI_VERSION) { continue; }
        if (req->frame_id == last_frame) { continue; }   /* 同帧不重复消费 */

        const uint8_t *raw = (const uint8_t *)(uintptr_t)S4D_RAW_BASE;
        s4d_region_invalidate(S4D_RAW_BASE, req->logical_bytes);
        if (s4d_crc32(raw, req->logical_bytes) != req->raw_crc32) {
            /* COMMIT 校验失败：拒绝，不猜 */
            continue;
        }

        #if PREPROC_SRC
        int rc = s4d_preproc_pl(req);
#else
        int rc = s4d_preproc_sw(req);
#endif
        if (rc == 0) { rc = infer_one_from_pl_tensor(req); }

        s4d_result_t *res = (s4d_result_t *)(uintptr_t)S4D_META_PS_RESULT;
        memset(res, 0, sizeof(*res));
        res->magic = S4D_MAGIC_RESULT;
        res->version = S4D_ABI_VERSION;
        res->session_id = req->session_id;
        res->frame_id = req->frame_id;
        res->result_seq = (rc == 0) ? ++result_seq : result_seq;
        res->phys_status = (rc == 0) ? 0u : 1u;
        res->raw_candidate_count = s4d_last_raw_candidates;
        res->box_count = s4d_last_box_count;
        res->error_code = (uint32_t)(rc < 0 ? -rc : rc);
        res->tensor_sha_prefix[0] = (uint64_t)s4d_crc32((const void *)(uintptr_t)S4D_TENSOR_BASE, S4D_TENSOR_BYTES);
        res->crc32 = 0;
        res->crc32 = s4d_crc32(res, sizeof(*res) - 4u);
        s4d_region_flush(S4D_META_PS_RESULT, sizeof(*res));

        last_frame = req->frame_id;
        xil_printf("S4D frame=%u rc=%d seq=%u\r\n",
                   (unsigned)req->frame_id, rc, (unsigned)res->result_seq);
    }
    return 0;
}

/* 保留强符号：M4-b 等仅走自检的变体在 --gc-sections 下也必须保留解码/启动入口 */
__attribute__((used)) static const void *const s4d_keep_strong_symbols[] = {
    (const void *)s2a_t62_decode_nms,
    (const void *)s2a_decode_nms_reference,
    (const void *)s2b_network_start_from_tensor,
};
