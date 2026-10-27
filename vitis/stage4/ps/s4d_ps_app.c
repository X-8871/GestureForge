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
 *   · 本文件是**可编译骨架**：网络/解码入口用 weak 桩，完整 Vitis 应用链接 r13 既有目标文件后才具备推理能力；
 *   · SW 预处理只实现 BGR→RGB 与 INT8 打包的**最小路径**，几何 resize/pad 未实现（编译期标记 S4D_SW_GEOM_TODO）；
 *   · 未在板上运行过；不属于 G3。
 */

#include <stdint.h>
#include <string.h>

#include "xil_cache.h"
#include "xil_io.h"
#include "xil_printf.h"
#include "xparameters.h"

/* ---------------- 地址与 ABI 常量（冻结，ADR §8.2/§8.4） ---------------- */
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

/* ---------------- 网络/解码入口（完整 Vitis 应用提供；此处 weak 桩） ---------------- */
extern int s2b_network_start_from_tensor(uint32_t session_id, uint32_t frame_id);
extern int s2a_decode_nms_reference(const int8_t *heads, uint32_t session_id,
                                    uint32_t frame_id, void *out_boxes, uint32_t *out_count);

__attribute__((weak)) int s2b_network_start_from_tensor(uint32_t session_id, uint32_t frame_id)
{
    (void)session_id; (void)frame_id;
    return -1;   /* 桩：未链接 r13 网络目标文件 */
}

__attribute__((weak)) int s2a_decode_nms_reference(const int8_t *heads, uint32_t session_id,
                                                   uint32_t frame_id, void *out_boxes, uint32_t *out_count)
{
    (void)heads; (void)session_id; (void)frame_id; (void)out_boxes;
    if (out_count) { *out_count = 0; }
    return -1;
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

/* PS 软件路径（兜底）：BGR→RGB + INT8 打包；几何 resize/pad 未实现（S4D_SW_GEOM_TODO） */
__attribute__((unused)) static int s4d_preproc_sw(const s4d_host_req_t *req)
{
    if (s4d_pixfmt_from_code(req->pixfmt_code) != S4D_PIXFMT_BGR888) {
        return -4;   /* 未知像素格式：拒绝，不猜 */
    }
    if (req->logical_bytes > S4D_RAW_BYTES) { return -5; }
    const uint8_t *raw = (const uint8_t *)(uintptr_t)S4D_RAW_BASE;
    int8_t *tensor = (int8_t *)(uintptr_t)S4D_TENSOR_BASE;
    uint32_t pixels = req->logical_bytes / 3u;
    s4d_region_invalidate(S4D_RAW_BASE, req->logical_bytes);
    if (pixels > S4D_TENSOR_BYTES) { pixels = S4D_TENSOR_BYTES; }   /* 最小路径：不实现缩放 */
    for (uint32_t i = 0; i < pixels; i++) {
        /* BGR 存储顺序 → RGB 逻辑顺序，再偏移到 INT8 值域 */
        tensor[i * 3 + 0] = (int8_t)((int)raw[i * 3 + 2] - 128);
        tensor[i * 3 + 1] = (int8_t)((int)raw[i * 3 + 1] - 128);
        tensor[i * 3 + 2] = (int8_t)((int)raw[i * 3 + 0] - 128);
    }
    s4d_region_flush(S4D_TENSOR_BASE, S4D_TENSOR_BYTES);
    return 0;
}

/* ---------------- infer_one_from_pl_tensor：跳过 CPU memcpy / 输入写回 ---------------- */
int infer_one_from_pl_tensor(const s4d_host_req_t *req)
{
    /* 1) PL 已写 tensor：只做 invalidate + DSB，绝不 memcpy 覆盖 */
    s4d_region_invalidate(S4D_TENSOR_BASE, S4D_TENSOR_BYTES);
    /* 2) 冻结网络启动入口（复用既有权重/feature/head 语义） */
    int rc = s2b_network_start_from_tensor(req->session_id, req->frame_id);
    if (rc != 0) { return rc; }
    /* 3) feature flush+invalidate、head 输出 invalidate 由网络层按既有语义完成；
          此处只做一次全量 DSB，确保可见性顺序 */
    __asm__ volatile("dsb sy" ::: "memory");
    return 0;
}

/* ---------------- 主循环：轮询 HOST_REQ → 预处理 → 推理 → 发布 PS_RESULT ---------------- */
int main(void)
{
    xil_printf("\r\nS4D PS APP: PREPROC_SRC=%d ABI=%u\r\n", PREPROC_SRC, S4D_ABI_VERSION);
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