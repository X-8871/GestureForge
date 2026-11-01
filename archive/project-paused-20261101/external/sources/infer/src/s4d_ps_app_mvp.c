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
#include "xil_exception.h"
#include "xil_io.h"
#include "xil_printf.h"
#include "xparameters.h"

#include "s4d_geometry.h"   /* 唯一几何参数表 + 最近邻 letterbox（PL/SW 共用，禁止另写字面量） */
#include "s2a_ps_decode_nms_reference.h"   /* r13 冻结解码参考：强符号 s2a_t62_decode_nms */
#include "s5_result_abi.h"   /* 阶段5 冻结结果块 ABI（0x20800000；只读引用，不改布局） */

/* ================= MVP（2026-10-31）：相机帧 → YOLO → S5RS 结果块 =================
 * 依据（只读）：
 *   · 结果块 ABI：`s5_result_abi.h`（阶段5 冻结，0x20800000，16 B/框，坐标 640×480）；
 *   · 帧源：相机 raw 在 0x12000000，BGR888 紧排；默认 1280×720（2,764,800 B），
 *     尺寸可用 `-DS4D_MVP_RAW_W/H` 覆盖（相机 ELF 定稿后以实测格式为准）；
 *   · 预处理：`s4d_sw_preproc_bgr888_to_chw_int8()`（D2 冻结口径，已与冻结张量逐字节对拍）；
 *   · 推理：`s2b_network_start_from_tensor()` + `s2a_decode_nms_reference()`（与 S4-B-REAL 同路径）。
 * 时间戳口径（全部 GT ticks → ms；分母已修好 S4D_MS_DIV）：
 *   t0_pre    = 预处理完成时刻
 *   t1_pl     = PL 2B 内核完成（DONE_SAFE）时刻
 *   t2_decode = 解码/NMS 完成时刻
 *   t3_pub    = S5RS 发布完成时刻
 *   dt_pre    = 预处理耗时（内部 t_begin→t0_pre）
 *   dt_pl     = t1_pl - t0_pre
 *   dt_dec    = t2_decode - t1_pl
 *   dt_all    = t3_pub - t_begin
 */
#ifndef S4D_FRAME_SRC_CAM
#define S4D_FRAME_SRC_CAM 1
#endif
#ifndef S4D_MVP_RAW_W
#define S4D_MVP_RAW_W 1280u
#endif
#ifndef S4D_MVP_RAW_H
#define S4D_MVP_RAW_H 720u
#endif
#define S4D_MVP_RAW_BYTES (S4D_MVP_RAW_W * S4D_MVP_RAW_H * 3u)
#define S4D_MVP_SESSION   0x534D5650u   /* 'SMVP'，S5RS 不消费 frame_id 以外字段 */

#include "s4d_sw_preproc.h"   /* 4-D SW 预处理（D2 冻结口径，逐字节对拍已通过） */
#include "xiltimer.h"      /* COUNTS_PER_SECOND（BSP xtimer_config.h：CPU_CORE_CLOCK/2） */

/* SDT BSP 未随附 xtime_l.h；libxiltimer.a 已导出 XTime_GetTime（arm-none-eabi-nm 已核），此处按 BSP 原型声明 */
extern void XTime_GetTime(uint64_t *Result);

/* ---- 时间基座修复（2026-10-29，负面清单见 S4-T34/s4d_time_basis_20261029_r01/ERRATUM_ROOT_CAUSE.md）----
 * BSP xtimer_config.h 的 XSLEEPTIMER_FREQ 宏无括号：
 *     #define XSLEEPTIMER_FREQ  XPAR_CPU_CORE_CLOCK_FREQ_HZ/2
 *     #define COUNTS_PER_SECOND  XSLEEPTIMER_FREQ
 * 若直接写 (uint64_t)COUNTS_PER_SECOND，会被展开成 (uint64_t)666666687/2 = 1,333,333,374，
 * 即有效分母是 GT 频率的 4 倍 —— 历史上所有 "ms" 都被压小 4 倍（11.8 s/帧 实为 ~47 s/帧）。
 * 这里统一用带括号的分母；计数直接读 Zynq 全局定时器（与 XTime_GetTime 同源，规避宏歧义）。 */
#define S4D_MS_DIV   ((uint64_t)(COUNTS_PER_SECOND))
_Static_assert(sizeof(uint64_t) == 8, "需要 64 位 uint64_t");

static uint64_t s4d_gt_ticks(void)
{
    uint32_t hi1, lo, hi2;
    do {
        hi1 = Xil_In32(0xF8F00204u);
        lo  = Xil_In32(0xF8F00200u);
        hi2 = Xil_In32(0xF8F00204u);
    } while (hi1 != hi2);
    return ((uint64_t)hi1 << 32) | (uint64_t)lo;
}

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
/* head13 尾 word 偏移：5,070 % 4 = 2 ⇒ 最后一个 32-bit word 在偏移 5,068，
 * 仅 lane 0/1（byte 5,068/5,069）属逻辑张量；lane 2/3（byte 5,070/5,071）在张量之外。
 * 依据 2A-T01 冻结规格：“5,070-byte head13 尾 word 只选择 lane 0011；不得因为 word
 * 对齐而越过其逻辑张量尾部”。M4-b 自检用该偏移做运行前后 lane 取证（不参与 pass 判据）。 */
#define S4D_HEAD13_TAIL_OFF ((uint32_t)(S4D_HEAD13_BYTES & ~3u))   /* = 5,068 */
#define S4D_HEAD26_OFF    0x01AD5E80u

/* 网络启动超时（正常推理路径与 M4-b 自检共用）：窗口 #4 实测旧值 400 周期 ≈ 8 µs，
 * 而 2B 实测整帧 START 需 47.4017962 s ⇒ 取 2B 冻结部署值 0xFFFFFFFF（名义 85.8993459 s @50MHz）。 */
#define S4D_NET_TIMEOUT_CYCLES  0xFFFFFFFFu
#define S4D_M4B_WALL_MS         120000u       /* 墙钟预算 120 s：主判据 */
#define S4D_M4B_SPIN_MAX        150000000u    /* 轮询次数安全网（>=1.5e8） */
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
    s4d_wr(S4D_CSR_CORETO_W, S4D_NET_TIMEOUT_CYCLES);
    s4d_wr(S4D_CSR_DRAINTO_W, S4D_NET_TIMEOUT_CYCLES);
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
    uint32_t tail13_before = 0u, tail13_after = 0u, tail13_ref = 0u;
    uint32_t lane01_ok = 0u, lane23_ok = 0u;
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

    /* 尾 word lane 取证（2026-10-29 定位 head13 byte 5,068/5,069 差异）：运行前快照
     * arena 尾 word（偏移 5,068）。运行后该 word 的低 16 位应等于参考尾 2 字节
     * （byte 5,068=0x06 / 5,069=0x05，见 test_fist_000_head13.raw），高 16 位
     * （byte 5,070/5,071）在逻辑张量之外，按 2A 规格 PL 必须以 lane 0011 写、
     * 不得产生副作用，故须与运行前一致。宿主侧若对该 word 投毒（如 0x5A5A5A5A），
     * lane 2/3 是否被改写即成为“是否越过逻辑张量尾部”的直接证据。
     * 该取证仅供诊断，不参与 pass 判据（避免改动已冻结的验收语义）。 */
    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF + S4D_HEAD13_TAIL_OFF, 4u);
    tail13_before = *(const volatile uint32_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF + S4D_HEAD13_TAIL_OFF);

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
    s4d_wr(S4D_CSR_CORETO_W, S4D_NET_TIMEOUT_CYCLES);
    s4d_wr(S4D_CSR_DRAINTO_W, S4D_NET_TIMEOUT_CYCLES);
    uint64_t t0 = 0, t1 = 0;
    uint32_t elapsed_ms = 0;
    t0 = s4d_gt_ticks();
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
    /* 等待安全终态：**120 s 墙钟为主判据**，spin<1.5e8 为安全网；每 5 s 打一行进度。
       注：窗口 #4 实测旧实现在**每轮**都打印，长等待会刷屏，故改为只在进度/终态打印。 */
    {
        uint32_t last_progress_ms = 0;
        for (spin = 0; spin < S4D_M4B_SPIN_MAX; spin++) {
            int r = s4d_safe_done(&st, &err);
            t1 = s4d_gt_ticks();
            elapsed_ms = (uint32_t)(((t1 - t0) * 1000ull) / S4D_MS_DIV);
            if (r == 1) { done = 1; break; }
            if (r == 2) { done = 2; break; }
            if ((st & 7u) == S4D_ST_FAULT) { done = 3; break; }
            if (elapsed_ms >= S4D_M4B_WALL_MS) { done = 0; break; }
            if (elapsed_ms - last_progress_ms >= 5000u) {
                last_progress_ms = elapsed_ms;
                xil_printf("M4B STEP=6 progress elapsed_ms=%u status=0x%08x error=0x%08x\r\n",
                           (unsigned)elapsed_ms, (unsigned)st, (unsigned)err);
            }
        }
        if (done == 1) {
            xil_printf("M4B STEP=6 wait done=1 elapsed_ms=%u spin=%u status=0x%08x error=0x%08x\r\n",
                       (unsigned)elapsed_ms, (unsigned)spin, (unsigned)st, (unsigned)err);
        } else if (done == 2) {
            xil_printf("M4B STEP=6 terminal done=2 elapsed_ms=%u spin=%u status=0x%08x error=0x%08x\r\n",
                       (unsigned)elapsed_ms, (unsigned)spin, (unsigned)st, (unsigned)err);
        } else if (done == 3) {
            xil_printf("M4B STEP=6 FAULT elapsed_ms=%u spin=%u status=0x%08x error=0x%08x\r\n",
                       (unsigned)elapsed_ms, (unsigned)spin, (unsigned)st, (unsigned)err);
        } else {
            xil_printf("M4B STEP=6 TIMEOUT elapsed_ms=%u spin=%u status=0x%08x error=0x%08x\r\n",
                       (unsigned)elapsed_ms, (unsigned)spin, (unsigned)st, (unsigned)err);
        }
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

        /* 尾 word 取证（诊断字段，不参与 pass）：一次上板即可区分
         *   (a) PL 尾字 lane/越界缺陷 与 (b) 参考预置未覆盖尾 2 字节。
         * 判读：after 低 16 位 = 参考低 16 位（此处 0x0506）⇒ lane 0/1 正确；
         *       after 高 16 位 = 运行前高 16 位 ⇒ PL 未越过逻辑张量尾部（lane 0011）。
         * 若 after 高 16 位被改写 ⇒ 违 2A 规格，属 PL 侧缺陷。 */
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF + S4D_HEAD13_TAIL_OFF, 4u);
        tail13_after = *(const volatile uint32_t *)(uintptr_t)
                       (S4D_TENSOR_BASE + S4D_HEAD13_OFF + S4D_HEAD13_TAIL_OFF);
        tail13_ref = (uint32_t)ref[S4D_HEAD13_TAIL_OFF]
                   | ((uint32_t)ref[S4D_HEAD13_TAIL_OFF + 1u] << 8)
                   | ((uint32_t)ref[S4D_HEAD13_TAIL_OFF + 2u] << 16)
                   | ((uint32_t)ref[S4D_HEAD13_TAIL_OFF + 3u] << 24);
        lane01_ok = ((tail13_after & 0xFFFFu) == (tail13_ref & 0xFFFFu)) ? 1u : 0u;
        lane23_ok = ((tail13_after & 0xFFFF0000u) == (tail13_before & 0xFFFF0000u)) ? 1u : 0u;
        xil_printf("M4B TAIL13 off=%u before=0x%08x after=0x%08x ref=0x%08x lane01_ok=%u lane23_ok=%u\r\n",
                   (unsigned)S4D_HEAD13_TAIL_OFF, (unsigned)tail13_before,
                   (unsigned)tail13_after, (unsigned)tail13_ref,
                   (unsigned)lane01_ok, (unsigned)lane23_ok);
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
               "\"ack_idle\":%d,\"epoch\":%u,\"status\":%u,\"error\":%u,"
               "\"elapsed_ms\":%u,\"spin\":%u,"
               "\"tail13_before\":%u,\"tail13_after\":%u,\"tail13_ref\":%u,"
               "\"lane01_ok\":%u,\"lane23_ok\":%u}\r\n",
               (done == 1 && d13 == 0u && d26 == 0u && stale == 1 && gate == 1 && idle_after_ack == 1) ? 1 : 0,
               done, (unsigned)d13, (unsigned)d26,
               (d13 == 0u) ? -1 : (int)f13, (d26 == 0u) ? -1 : (int)f26,
               stale, gate, idle_after_ack,
               (unsigned)(uint32_t)epoch, (unsigned)st, (unsigned)err,
               (unsigned)elapsed_ms, (unsigned)spin,
               (unsigned)tail13_before, (unsigned)tail13_after, (unsigned)tail13_ref,
               (unsigned)lane01_ok, (unsigned)lane23_ok);
    return (done == 1 && d13 == 0u && d26 == 0u && stale == 1 && gate == 1 && idle_after_ack == 1) ? 0 : -2;
}

#if defined(S4D_CHAIN_SELFCHECK) && S4D_CHAIN_SELFCHECK
/* ---------------- chain-lite-A 自检：注入张量 -> PL 网络 -> PS 解码/NMS -> UART 框 JSON ----------------
 * 判据（事先写死，不得放宽）：DONE_SAFE + error=0；框 JSON 与 r13 冻结参考逐字段一致（容差 1e-9）。
 * 不做预处理（PREPROC=INJECTED_TENSOR）；不与 RAW 0x12000000 参考比较（本步不涉及）。
 */
static int s4d_chain_selfcheck(void)
{
    uint32_t st = 0, err = 0;
    uint64_t epoch = 0, epoch_before = 0;
    uint64_t t0 = 0, t1 = 0;
    uint32_t elapsed_ms = 0, spin = 0;
    uint32_t frame = 1u;
    s2a_t62_detection det[S4D_DEC_MAX_BOX];
    uint32_t count = 0u, raw = 0u;
    int decode_rc = -99, done = 0, ack_idle = 0;
    uint32_t i;

    s4d_cur_src_w = 1440u;   /* 冻结几何（host_result_test_fist_000.json: geometry 1440x1920） */
    s4d_cur_src_h = 1920u;

    xil_printf("CHAIN STEP=0 enter PREPROC=INJECTED_TENSOR geom=1440x1920\r\n");
    xil_printf("CHAIN STEP=1 read CSR_ID addr=0x%08x\r\n", (unsigned)S4D_CSR_ID);
    xil_printf("CHAIN CSR id=0x%08x ver=0x%08x\r\n",
               (unsigned)s4d_rd(S4D_CSR_ID), (unsigned)s4d_rd(S4D_CSR_VER));
    xil_printf("CHAIN STEP=2 check idle: status=0x%08x\r\n", (unsigned)s4d_rd(S4D_CSR_STATUS));
    if (!s4d_is_idle()) {
        xil_printf("CHAIN RESULT={\"pass\":0,\"reason\":\"not_idle\",\"status\":%u}\r\n",
                   (unsigned)s4d_rd(S4D_CSR_STATUS));
        return -1;
    }
    xil_printf("CHAIN STEP=3 read epoch\r\n");
    if (!s4d_read_epoch(&epoch_before)) { xil_printf("CHAIN RESULT={\"pass\":0,\"reason\":\"epoch_read_fail\"}\r\n"); return -1; }
    epoch = epoch_before + 1u;

    s4d_region_flush(S4D_TENSOR_BASE, S4D_INPUT_BYTES);
    s4d_region_flush(S4D_TENSOR_BASE + S4D_INPUT_BASE, S4D_WEIGHT_BYTES);
    s4d_dsb();
    xil_printf("CHAIN STEP=4 cache flush done\r\n");

    s4d_wr(S4D_CSR_FRAME_W, frame);
    s4d_wr(S4D_CSR_INADDR_W, 0u);
    s4d_wr(S4D_CSR_INBYTES_W, S4D_INPUT_BYTES);
    s4d_wr(S4D_CSR_WADDR_W, S4D_INPUT_BASE);
    s4d_wr(S4D_CSR_WBYTES_W, S4D_WEIGHT_BYTES);
    s4d_wr(S4D_CSR_CORETO_W, S4D_NET_TIMEOUT_CYCLES);
    s4d_wr(S4D_CSR_DRAINTO_W, S4D_NET_TIMEOUT_CYCLES);
    t0 = s4d_gt_ticks();
    s4d_wr(S4D_CSR_CMD, S4D_CMD_START);
    xil_printf("CHAIN STEP=5 START cmd written\r\n");

    {
        uint32_t last_progress_ms = 0;
        for (spin = 0u; spin < S4D_M4B_SPIN_MAX; spin++) {
            int r = s4d_safe_done(&st, &err);
            t1 = s4d_gt_ticks();
            elapsed_ms = (uint32_t)(((t1 - t0) * 1000ull) / S4D_MS_DIV);
            if (r == 1) { done = 1; break; }
            if (r == 2) { done = 2; break; }
            if ((st & 7u) == S4D_ST_FAULT) { done = 3; break; }
            if (elapsed_ms >= S4D_M4B_WALL_MS) { done = 0; break; }
            if (elapsed_ms - last_progress_ms >= 5000u) {
                last_progress_ms = elapsed_ms;
                xil_printf("CHAIN STEP=6 progress elapsed_ms=%u status=0x%08x error=0x%08x\r\n",
                           (unsigned)elapsed_ms, (unsigned)st, (unsigned)err);
            }
        }
    }
    xil_printf("CHAIN STEP=6 wait done=%d elapsed_ms=%u spin=%u status=0x%08x error=0x%08x\r\n",
               done, (unsigned)elapsed_ms, (unsigned)spin, (unsigned)st, (unsigned)err);
    if (done != 1) {
        xil_printf("CHAIN RESULT={\"pass\":0,\"reason\":\"not_done_safe\",\"done\":%d,"
                   "\"status\":%u,\"error\":%u,\"elapsed_ms\":%u,\"spin\":%u}\r\n",
                   done, (unsigned)st, (unsigned)err, (unsigned)elapsed_ms, (unsigned)spin);
        return -1;
    }

    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
    xil_printf("CHAIN STEP=7 heads invalidated\r\n");

    decode_rc = s2a_decode_nms_reference(
        (const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF), frame, frame, det, &count);
    raw = s4d_last_raw_candidates;   /* 候选数由封装函数经全局回传（R13 口径） */
    xil_printf("CHAIN STEP=8 decode rc=%d count=%u raw=%u\r\n",
               decode_rc, (unsigned)count, (unsigned)raw);
    /* 注：xil_printf 是 Xilinx 精简实现，**不支持 %g/浮点**（窗口实测：%g 输出为空且后续参数错位）。
     * 故 double 一律按 IEEE-754 位模式输出（hi/lo 两个 32-bit hex），主机端按位重建，位级精确。 */
    for (i = 0u; i < count; i++) {
        union { double d; uint64_t u; } sc, b1, b2, b3, b4;
        sc.d = det[i].score; b1.d = det[i].x1; b2.d = det[i].y1; b3.d = det[i].x2; b4.d = det[i].y2;
        xil_printf("CHAIN DET idx=%u class=%d "
                   "score_hi=%08x score_lo=%08x "
                   "x1_hi=%08x x1_lo=%08x y1_hi=%08x y1_lo=%08x "
                   "x2_hi=%08x x2_lo=%08x y2_hi=%08x y2_lo=%08x order=%d\r\n",
                   (unsigned)i, (int)det[i].class_id,
                   (unsigned)(uint32_t)(sc.u >> 32), (unsigned)(uint32_t)(sc.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b1.u >> 32), (unsigned)(uint32_t)(b1.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b2.u >> 32), (unsigned)(uint32_t)(b2.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b3.u >> 32), (unsigned)(uint32_t)(b3.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b4.u >> 32), (unsigned)(uint32_t)(b4.u & 0xFFFFFFFFu),
                   (int)det[i].source_order);
    }

    xil_printf("CHAIN STEP=9 ACK phase (idle_before=%d)\r\n", s4d_is_idle());
    {
        uint64_t e2 = 0;
        if (s4d_read_epoch(&e2) && e2 == epoch && s4d_rd(S4D_CSR_FRAME_R) == frame) {
            s4d_wr(S4D_CSR_ACKLO_W, (uint32_t)epoch);
            s4d_wr(S4D_CSR_ACKHI_W, (uint32_t)(epoch >> 32));
            s4d_wr(S4D_CSR_CMD, S4D_CMD_ACK);
            ack_idle = s4d_is_idle();
        }
    }
    xil_printf("CHAIN RESULT={\"pass\":%d,\"done\":1,\"status\":%u,\"error\":%u,\"decode_rc\":%d,"
               "\"count\":%u,\"raw\":%u,\"ack_idle\":%d,\"elapsed_ms\":%u,\"spin\":%u}\r\n",
               (done == 1 && err == 0u && decode_rc == 0 && count >= 1u && ack_idle == 1) ? 1 : 0,
               (unsigned)st, (unsigned)err, decode_rc, (unsigned)count, (unsigned)raw,
               ack_idle, (unsigned)elapsed_ms, (unsigned)spin);
    return (done == 1 && err == 0u && decode_rc == 0 && count >= 1u && ack_idle == 1) ? 0 : -2;
}
#endif


#if defined(S4D_CHAINB_SELFCHECK) && S4D_CHAINB_SELFCHECK
/* ---------------- chain-lite-B 自检：RAW 640x480 BGR888 -> SW 预处理 -> PL 网络 -> 解码 -> 框 JSON ----------
 * 判据（与 chain-lite-A 同强度）：DONE_SAFE + error=0 + decode_rc=0 + count>=1 + ACK 回 idle；
 * 预处理后打印张量 CRC-32（= zlib crc32），供离线同输入比对，自证板上预处理实现。
 */
static int s4d_chainb_selfcheck(void)
{
    uint32_t st = 0, err = 0, tcr = 0;
    uint64_t epoch = 0, epoch_before = 0;
    uint64_t t0 = 0, t1 = 0;
    uint32_t elapsed_ms = 0, spin = 0;
    uint32_t frame = 1u;
    s2a_t62_detection det[S4D_DEC_MAX_BOX];
    uint32_t count = 0u, raw = 0u;
    int decode_rc = -99, done = 0, ack_idle = 0, prc;
    uint32_t i;

    s4d_cur_src_w = 640u;
    s4d_cur_src_h = 480u;

    xil_printf("CHAINB STEP=0 enter PREPROC=SW RAW=0x%08x %s\r\n",
               (unsigned)S4D_RAW_BASE, S4D_GEOM.name);
    xil_printf("CHAINB STEP=1 read CSR_ID addr=0x%08x\r\n", (unsigned)S4D_CSR_ID);
    xil_printf("CHAINB CSR id=0x%08x ver=0x%08x\r\n",
               (unsigned)s4d_rd(S4D_CSR_ID), (unsigned)s4d_rd(S4D_CSR_VER));
    if (!s4d_is_idle()) {
        xil_printf("CHAINB RESULT={\"pass\":0,\"reason\":\"not_idle\",\"status\":%u}\r\n",
                   (unsigned)s4d_rd(S4D_CSR_STATUS));
        return -1;
    }
    if (!s4d_read_epoch(&epoch_before)) { xil_printf("CHAINB RESULT={\"pass\":0,\"reason\":\"epoch_read_fail\"}\r\n"); return -1; }
    epoch = epoch_before + 1u;

    /* ---- SW 预处理：RAW BGR888(640x480) -> INT8 CHW(416x416x3) 写入 arena ---- */
    prc = s4d_sw_preproc_bgr888_to_chw_int8((const uint8_t *)(uintptr_t)S4D_RAW_BASE, 640, 480,
                                            (int8_t *)(uintptr_t)S4D_TENSOR_BASE);
    s4d_region_flush(S4D_TENSOR_BASE, S4D_INPUT_BYTES);
    s4d_region_flush(S4D_TENSOR_BASE + S4D_INPUT_BASE, S4D_WEIGHT_BYTES);
    s4d_dsb();
    tcr = s4d_crc32((const void *)(uintptr_t)S4D_TENSOR_BASE, S4D_INPUT_BYTES);
    xil_printf("CHAINB STEP=2 sw_preproc rc=%d tensor_crc32=0x%08x bytes=%u\r\n",
               prc, (unsigned)tcr, (unsigned)S4D_INPUT_BYTES);
    if (prc != 0) { xil_printf("CHAINB RESULT={\"pass\":0,\"reason\":\"preproc_fail\",\"rc\":%d}\r\n", prc); return -1; }

    xil_printf("CHAINB STEP=3 read epoch ok\r\n");
    s4d_wr(S4D_CSR_FRAME_W, frame);
    s4d_wr(S4D_CSR_INADDR_W, 0u);
    s4d_wr(S4D_CSR_INBYTES_W, S4D_INPUT_BYTES);
    s4d_wr(S4D_CSR_WADDR_W, S4D_INPUT_BASE);
    s4d_wr(S4D_CSR_WBYTES_W, S4D_WEIGHT_BYTES);
    s4d_wr(S4D_CSR_CORETO_W, S4D_NET_TIMEOUT_CYCLES);
    s4d_wr(S4D_CSR_DRAINTO_W, S4D_NET_TIMEOUT_CYCLES);
    t0 = s4d_gt_ticks();
    s4d_wr(S4D_CSR_CMD, S4D_CMD_START);
    xil_printf("CHAINB STEP=4 START cmd written\r\n");

    {
        uint32_t last_progress_ms = 0;
        for (spin = 0u; spin < S4D_M4B_SPIN_MAX; spin++) {
            int r = s4d_safe_done(&st, &err);
            t1 = s4d_gt_ticks();
            elapsed_ms = (uint32_t)(((t1 - t0) * 1000ull) / S4D_MS_DIV);
            if (r == 1) { done = 1; break; }
            if (r == 2) { done = 2; break; }
            if ((st & 7u) == S4D_ST_FAULT) { done = 3; break; }
            if (elapsed_ms >= S4D_M4B_WALL_MS) { done = 0; break; }
            if (elapsed_ms - last_progress_ms >= 5000u) {
                last_progress_ms = elapsed_ms;
                xil_printf("CHAINB STEP=5 progress elapsed_ms=%u status=0x%08x error=0x%08x\r\n",
                           (unsigned)elapsed_ms, (unsigned)st, (unsigned)err);
            }
        }
    }
    xil_printf("CHAINB STEP=5 wait done=%d elapsed_ms=%u spin=%u status=0x%08x error=0x%08x\r\n",
               done, (unsigned)elapsed_ms, (unsigned)spin, (unsigned)st, (unsigned)err);
    if (done != 1) {
        xil_printf("CHAINB RESULT={\"pass\":0,\"reason\":\"not_done_safe\",\"done\":%d,\"status\":%u,"
                   "\"error\":%u,\"tensor_crc32\":%u,\"elapsed_ms\":%u,\"spin\":%u}\r\n",
                   done, (unsigned)st, (unsigned)err, (unsigned)tcr, (unsigned)elapsed_ms, (unsigned)spin);
        return -1;
    }

    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
    s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
    decode_rc = s2a_decode_nms_reference(
        (const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF), frame, frame, det, &count);
    raw = s4d_last_raw_candidates;
    xil_printf("CHAINB STEP=6 decode rc=%d count=%u raw=%u\r\n",
               decode_rc, (unsigned)count, (unsigned)raw);
    for (i = 0u; i < count; i++) {
        union { double d; uint64_t u; } sc, b1, b2, b3, b4;
        sc.d = det[i].score; b1.d = det[i].x1; b2.d = det[i].y1; b3.d = det[i].x2; b4.d = det[i].y2;
        xil_printf("CHAINB DET idx=%u class=%d "
                   "score_hi=%08x score_lo=%08x "
                   "x1_hi=%08x x1_lo=%08x y1_hi=%08x y1_lo=%08x "
                   "x2_hi=%08x x2_lo=%08x y2_hi=%08x y2_lo=%08x order=%d\r\n",
                   (unsigned)i, (int)det[i].class_id,
                   (unsigned)(uint32_t)(sc.u >> 32), (unsigned)(uint32_t)(sc.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b1.u >> 32), (unsigned)(uint32_t)(b1.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b2.u >> 32), (unsigned)(uint32_t)(b2.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b3.u >> 32), (unsigned)(uint32_t)(b3.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(b4.u >> 32), (unsigned)(uint32_t)(b4.u & 0xFFFFFFFFu),
                   (int)det[i].source_order);
    }

    xil_printf("CHAINB STEP=7 ACK phase (idle_before=%d)\r\n", s4d_is_idle());
    {
        uint64_t e2 = 0;
        if (s4d_read_epoch(&e2) && e2 == epoch && s4d_rd(S4D_CSR_FRAME_R) == frame) {
            s4d_wr(S4D_CSR_ACKLO_W, (uint32_t)epoch);
            s4d_wr(S4D_CSR_ACKHI_W, (uint32_t)(epoch >> 32));
            s4d_wr(S4D_CSR_CMD, S4D_CMD_ACK);
            ack_idle = s4d_is_idle();
        }
    }
    xil_printf("CHAINB RESULT={\"pass\":%d,\"done\":1,\"status\":%u,\"error\":%u,\"decode_rc\":%d,"
               "\"count\":%u,\"raw\":%u,\"ack_idle\":%d,\"tensor_crc32\":%u,\"elapsed_ms\":%u,\"spin\":%u}\r\n",
               (done == 1 && err == 0u && decode_rc == 0 && count >= 1u && ack_idle == 1) ? 1 : 0,
               (unsigned)st, (unsigned)err, decode_rc, (unsigned)count, (unsigned)raw,
               ack_idle, (unsigned)tcr, (unsigned)elapsed_ms, (unsigned)spin);
    return (done == 1 && err == 0u && decode_rc == 0 && count >= 1u && ack_idle == 1) ? 0 : -2;
}
#endif


#if defined(S4D_LONGRUN_SELFCHECK) && S4D_LONGRUN_SELFCHECK
/* ---- 仪表化 v2：32 B 记录区（8 字）+ 数据中止捕获 ----
 * 布局（精确 32 B，只写 0x11B00000 的 8 个字；不触候选区、不触冻结对象）：
 *   [0] MAGIC 0x53344C01（版本 1）
 *   [1] step_id | iter<<8          —— 即将进入的步骤
 *   [2] done_step_id | iter<<8     —— 最后**成功完成**的步骤
 *   [3] 即将访问的 CSR 地址（0=非 CSR/纯 CPU 步）
 *   [4] 写入值；读访问用 0xFFFFFFFF 哨兵
 *   [5] DFSR（仅在捕获中止时写入）
 *   [6] DFAR（仅在捕获中止时写入；先解 DFSR，异步中止时 DFAR 不可靠）
 *   [7] COMMIT：0xC0DEC0DE=记录有效；0xAB0AB70B=已捕获中止
 * 说明：记录**在每次 CSR 访问之前**写入并 flush+DSB；若总线挂死导致记录不可见，
 *       只能说“无法取证”，不能解释为“没有发生”。
 */
#define S4D_LR_REC_ADDR      0x11B00000u
#define S4D_LR_REC_BYTES     32u
#define S4D_LR_MAGIC_VAL     0x53344C01u
#define S4D_LR_COMMIT_VALID  0xC0DEC0DEu
#define S4D_LR_COMMIT_ABORT  0xAB0AB70Bu
#define S4D_LR_READ_SENTINEL 0xFFFFFFFFu

static void s4d_lr_rec_flush(void)
{
    Xil_DCacheFlushRange((UINTPTR)S4D_LR_REC_ADDR, S4D_LR_REC_BYTES);
    s4d_dsb();
}

static void s4d_lr_rec_init(void)
{
    volatile uint32_t *m = (volatile uint32_t *)(uintptr_t)S4D_LR_REC_ADDR;
    m[0] = S4D_LR_MAGIC_VAL; m[1] = 0u; m[2] = 0u; m[3] = 0u;
    m[4] = 0u; m[5] = 0u; m[6] = 0u; m[7] = S4D_LR_COMMIT_VALID;
    s4d_lr_rec_flush();
}

/* 进入某步之前调用：记录“即将访问”的 CSR 地址与写入值 */
static void s4d_lr_mark(uint32_t step_id, uint32_t iter, uint32_t csr_addr, uint32_t csr_val)
{
    volatile uint32_t *m = (volatile uint32_t *)(uintptr_t)S4D_LR_REC_ADDR;
    m[1] = (step_id & 0xFFu) | (iter << 8);
    m[3] = csr_addr;
    m[4] = csr_val;
    s4d_lr_rec_flush();
}

/* 某步成功完成后调用：记录“最后成功步骤” */
static void s4d_lr_done(uint32_t step_id, uint32_t iter)
{
    volatile uint32_t *m = (volatile uint32_t *)(uintptr_t)S4D_LR_REC_ADDR;
    m[2] = (step_id & 0xFFu) | (iter << 8);
    s4d_lr_rec_flush();
}

static void s4d_lr_rec_clear(void)
{
    volatile uint32_t *m = (volatile uint32_t *)(uintptr_t)S4D_LR_REC_ADDR;
    uint32_t i;
    for (i = 0u; i < (S4D_LR_REC_BYTES / 4u); i++) { m[i] = 0u; }
    s4d_lr_rec_flush();
}

/* 数据中止处理器：记录 DFSR/DFAR + 提交标记后停机（主机用普通 mrd 读记录区即可定位） */
static __attribute__((noinline, used)) void s4d_lr_data_abort_handler(void *arg)
{
    volatile uint32_t *m = (volatile uint32_t *)(uintptr_t)S4D_LR_REC_ADDR;
    uint32_t dfsr = 0u, dfar = 0u;
    (void)arg;
    __asm__ volatile("mrc p15, 0, %0, c5, c0, 0" : "=r"(dfsr));
    __asm__ volatile("mrc p15, 0, %0, c6, c0, 0" : "=r"(dfar));
    m[5] = dfsr;
    m[6] = dfar;
    m[7] = S4D_LR_COMMIT_ABORT;
    s4d_lr_rec_flush();
    for (;;) { }
}

/* ---------------- 长跑自检：SW 预处理一次 -> 循环[START -> DONE_SAFE -> 解码 -> ACK] ----------------
 * 判据（事先写死，见证据 README）：wall_ms>=1800000、iterations>=140、failures==0、
 * 每轮 status==0x00000E04(DONE_SAFE) 且 error==0、decode_rc==0、count==1、raw==2、ack_idle==1、
 * epoch 单调递增、框 8 字段与第一轮逐位一致（第一轮框另由主机侧与离线参考比对）。
 * 停止：任一轮失败即停并打印失败轮次/状态；wall>=1800 s 或 iter>=160 先到者。
 */
#define S4D_LR_WALL_MS     1800000u
#define S4D_LR_MAX_ITERS   160u
/* 2026-10-29 判据勘误（S4-T34/s4d_time_basis_20261029_r01/ERRATUM_ROOT_CAUSE.md）：
 * 旧值 140 是按**坏掉的时间口径**（分母 4× ⇒ 应用 ms 只有真实 1/4）选的：那时 30 min
 * 等于 2 h 真实、约 152 轮。修好时间基座后，真实 30 min ≈ 38 轮（实测 47.3 s/轮），
 * 140 轮永远达不到（循环在 1.8e6 ms 就 break），导致 RESULT 恒 exit=3。
 * 现按真实口径取 38（30 min ÷ 47.3 s），与 S4D_LR_WALL_MS=1,800,000 一致。 */
#define S4D_LR_MIN_ITERS   38u
#define S4D_LR_PROGRESS    10u

typedef union { double d; uint64_t u; } s4d_lr_dbl;

typedef struct {
    int class_id;
    int source_order;
    s4d_lr_dbl score, x1, y1, x2, y2;
} s4d_lr_box;

static int s4d_lr_box_equal(const s4d_lr_box *a, const s4d_lr_box *b)
{
    return a->class_id == b->class_id && a->source_order == b->source_order
        && a->score.u == b->score.u && a->x1.u == b->x1.u && a->y1.u == b->y1.u
        && a->x2.u == b->x2.u && a->y2.u == b->y2.u;
}

static __attribute__((noinline)) int s4d_longrun_selfcheck(void)
{
    uint32_t st = 0, err = 0, tcr = 0, prc;
    uint64_t t_start = 0, t_now = 0, wall_ms = 0;
    uint64_t epoch_first = 0, epoch_last = 0, epoch_prev = 0;
    uint32_t iter = 0, failures = 0;
    uint32_t e_min = 0xFFFFFFFFu, e_max = 0u, e_sum = 0u;
    s2a_t62_detection det[S4D_DEC_MAX_BOX];
    s4d_lr_box first;
    int first_valid = 0;
    int exit_code = 0;

    /* 异常链：必须在 longrun **实际入口**注册（历史缺陷：注册曾位于不可达的 chainb 分支）。
     * VBAR 指向 BSP 的 _vector_table；显式 Xil_ExceptionInit 保证已设置。 */
    Xil_ExceptionInit();
    Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_DATA_ABORT_INT,
                                 (Xil_ExceptionHandler)s4d_lr_data_abort_handler, NULL);
    s4d_lr_rec_init();

    s4d_cur_src_w = 640u;
    s4d_cur_src_h = 480u;
    memset(&first, 0, sizeof(first));

    xil_printf("LONGRUN STEP=0 enter PREPROC=SW RAW=0x%08x wall_ms_max=%u iter_max=%u\r\n",
               (unsigned)S4D_RAW_BASE, (unsigned)S4D_LR_WALL_MS, (unsigned)S4D_LR_MAX_ITERS);

    prc = s4d_sw_preproc_bgr888_to_chw_int8((const uint8_t *)(uintptr_t)S4D_RAW_BASE, 640, 480,
                                            (int8_t *)(uintptr_t)S4D_TENSOR_BASE);
    s4d_region_flush(S4D_TENSOR_BASE, S4D_INPUT_BYTES);
    s4d_region_flush(S4D_TENSOR_BASE + S4D_INPUT_BASE, S4D_WEIGHT_BYTES);
    s4d_dsb();
    tcr = s4d_crc32((const void *)(uintptr_t)S4D_TENSOR_BASE, S4D_INPUT_BYTES);
    xil_printf("LONGRUN STEP=1 sw_preproc rc=%d tensor_crc32=0x%08x\r\n", prc, (unsigned)tcr);
    if (prc != 0) {
        xil_printf("LONGRUN RESULT={\"exit\":1,\"reason\":\"preproc_fail\",\"rc\":%d}\r\n", prc);
        return -1;
    }
    /* 探针（2026-10-29）：首次 CSR 访问之前读 SLCR —— PS 内部寄存器，不依赖 PL。
     * 目的：判定"首次 CSR 读挂住"是否因 PL 侧无时钟/无响应（长跑静默停住）。
     * 只读、不写任何 SLCR、不改变任何判据。 */
    {
        uint32_t p_shftr = Xil_In32(0xF8000900u);   /* LVL_SHFTR_EN */
        uint32_t p_fclk0 = Xil_In32(0xF8000170u);   /* FCLK_CTRL0 */
        uint32_t p_aper  = Xil_In32(0xF8000120u);   /* APER_CLK_CTRL */
        uint32_t p_frst  = Xil_In32(0xF8000240u);   /* FPGA_RST_CTRL */
        xil_printf("LONGRUN PROBE slcr shftr=0x%08x fclk0=0x%08x aper=0x%08x fpga_rst=0x%08x\r\n",
                   (unsigned)p_shftr, (unsigned)p_fclk0, (unsigned)p_aper, (unsigned)p_frst);
    }
    /* 细分探针（2026-10-29）：把"整条 PS→PL 读通路挂"与"只有 STATUS 读挂"分开。
     * 先读 ID(0x000)，再读 STATUS(0x00C)；两次之间都有打印，谁不打印就说明卡在哪一步。 */
    {
        uint32_t p_id = s4d_rd(S4D_CR(0x000u));
        xil_printf("LONGRUN PROBE id=0x%08x\r\n", (unsigned)p_id);
        uint32_t p_st = s4d_rd(S4D_CR(0x00Cu));
        xil_printf("LONGRUN PROBE status=0x%08x\r\n", (unsigned)p_st);
    }
    if (!s4d_is_idle()) {
        xil_printf("LONGRUN RESULT={\"exit\":1,\"reason\":\"not_idle\",\"status\":%u}\r\n",
                   (unsigned)s4d_rd(S4D_CSR_STATUS));
        return -1;
    }

    t_start = s4d_gt_ticks();
    for (iter = 1u; iter <= S4D_LR_MAX_ITERS; iter++) {
        uint64_t e_before = 0, e_expect = 0, e_after = 0;
        uint64_t t0 = 0, t1 = 0;
        uint32_t elapsed_ms = 0, spin = 0, count = 0u, raw = 0u;
        int done = 0, decode_rc = -99, ack_idle = 0;
        int round_fail = 0;
        const char *fail_why = "";

        t_now = s4d_gt_ticks();
        wall_ms = (uint64_t)(((t_now - t_start) * 1000ull) / S4D_MS_DIV);
        if (wall_ms >= S4D_LR_WALL_MS) { break; }
        s4d_lr_mark(8u, iter, 0u, 0u);   /* 8 = 下一轮开始（纯 CPU） */
        xil_printf("LONGRUN PROBE iter=%u start\r\n", (unsigned)iter);

        /* STEP A：epoch */
        s4d_lr_mark(1u, iter, S4D_CSR_EPOCH_LO, S4D_LR_READ_SENTINEL);   /* 1 = 读 epoch */
        if (!s4d_read_epoch(&e_before)) { round_fail = 1; fail_why = "epoch_read_fail"; }
        e_expect = e_before + 1u;
        if (round_fail == 0 && !s4d_is_idle()) { round_fail = 1; fail_why = "not_idle_before_round"; }
        if (round_fail == 0) { s4d_lr_done(1u, iter); }
        xil_printf("LONGRUN PROBE iter=%u epoch_ok e_before=%u\r\n", (unsigned)iter, (unsigned)e_before);

        /* STEP B：配置 + START */
        if (round_fail == 0) {
            s4d_lr_mark(2u, iter, S4D_CSR_FRAME_W, iter);   /* 2 = 配置 CSR（首写 FRAME） */
            s4d_wr(S4D_CSR_FRAME_W, iter);
            s4d_wr(S4D_CSR_INADDR_W, 0u);
            s4d_wr(S4D_CSR_INBYTES_W, S4D_INPUT_BYTES);
            s4d_wr(S4D_CSR_WADDR_W, S4D_INPUT_BASE);
            s4d_wr(S4D_CSR_WBYTES_W, S4D_WEIGHT_BYTES);
            s4d_wr(S4D_CSR_CORETO_W, S4D_NET_TIMEOUT_CYCLES);
            s4d_wr(S4D_CSR_DRAINTO_W, S4D_NET_TIMEOUT_CYCLES);
            s4d_lr_done(2u, iter);
            t0 = s4d_gt_ticks();
            s4d_lr_mark(3u, iter, S4D_CSR_CMD, S4D_CMD_START);   /* 3 = 写 START */
            s4d_wr(S4D_CSR_CMD, S4D_CMD_START);
            s4d_lr_done(3u, iter);
            xil_printf("LONGRUN PROBE iter=%u start_written\r\n", (unsigned)iter);
        }

        /* STEP C：等 DONE_SAFE */
        if (round_fail == 0) {
            s4d_lr_mark(4u, iter, S4D_CSR_STATUS, S4D_LR_READ_SENTINEL);   /* 4 = 等 DONE_SAFE */
            xil_printf("LONGRUN PROBE iter=%u wait_done_pre\r\n", (unsigned)iter);
            for (spin = 0u; spin < S4D_M4B_SPIN_MAX; spin++) {
                int r = s4d_safe_done(&st, &err);
                t1 = s4d_gt_ticks();
                elapsed_ms = (uint32_t)(((t1 - t0) * 1000ull) / S4D_MS_DIV);
                if (r == 1) { done = 1; break; }
                if (r == 2) { done = 2; break; }
                if ((st & 7u) == S4D_ST_FAULT) { done = 3; break; }
                if (elapsed_ms >= S4D_M4B_WALL_MS) { done = 0; break; }
            }
            if (done != 1) { round_fail = 1; fail_why = "not_done_safe"; }
            else if (st != 0x00000E04u) { round_fail = 1; fail_why = "status_not_0E04"; }
            else if (err != 0u) { round_fail = 1; fail_why = "error_nonzero"; }
            xil_printf("LONGRUN PROBE iter=%u done=%d st=0x%08x elapsed_ms=%u\r\n",
                       (unsigned)iter, done, (unsigned)st, (unsigned)elapsed_ms);
            if (round_fail == 0) { s4d_lr_done(4u, iter); }
        }

        /* STEP D：invalidate + 解码 */
        if (round_fail == 0) {
            s4d_lr_mark(5u, iter, 0u, 0u);   /* 5 = invalidate head（纯 cache 维护） */
            s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
            s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
            s4d_lr_mark(6u, iter, 0u, 0u);   /* 6 = 解码（纯 CPU） */
            decode_rc = s2a_decode_nms_reference(
                (const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF), (uint32_t)iter, (uint32_t)iter,
                det, &count);
            raw = s4d_last_raw_candidates;
            s4d_lr_done(5u, iter);
            if (decode_rc != 0) { round_fail = 1; fail_why = "decode_rc_nonzero"; }
            else if (count != 1u) { round_fail = 1; fail_why = "count_not_1"; }
            else if (raw != 2u) { round_fail = 1; fail_why = "raw_not_2"; }
            if (round_fail == 0) { s4d_lr_done(6u, iter); }
        }

        /* STEP E：核对框是否与第一轮逐位一致 */
        if (round_fail == 0) {
            s4d_lr_box b;
            b.class_id = (int)det[0].class_id;
            b.source_order = (int)det[0].source_order;
            b.score.d = det[0].score; b.x1.d = det[0].x1; b.y1.d = det[0].y1;
            b.x2.d = det[0].x2; b.y2.d = det[0].y2;
            if (first_valid == 0) {
                first = b;
                first_valid = 1;
                xil_printf("LONGRUN BOX iter=%u class=%d order=%d score_hi=%08x score_lo=%08x "
                           "x1_hi=%08x x1_lo=%08x y1_hi=%08x y1_lo=%08x "
                           "x2_hi=%08x x2_lo=%08x y2_hi=%08x y2_lo=%08x\r\n",
                           (unsigned)iter, b.class_id, b.source_order,
                           (unsigned)(uint32_t)(b.score.u >> 32), (unsigned)(uint32_t)(b.score.u & 0xFFFFFFFFu),
                           (unsigned)(uint32_t)(b.x1.u >> 32), (unsigned)(uint32_t)(b.x1.u & 0xFFFFFFFFu),
                           (unsigned)(uint32_t)(b.y1.u >> 32), (unsigned)(uint32_t)(b.y1.u & 0xFFFFFFFFu),
                           (unsigned)(uint32_t)(b.x2.u >> 32), (unsigned)(uint32_t)(b.x2.u & 0xFFFFFFFFu),
                           (unsigned)(uint32_t)(b.y2.u >> 32), (unsigned)(uint32_t)(b.y2.u & 0xFFFFFFFFu));
            } else if (!s4d_lr_box_equal(&b, &first)) {
                round_fail = 1; fail_why = "box_changed";
            }
        }

        /* STEP F：ACK 回 idle */
        if (round_fail == 0) {
            s4d_lr_mark(7u, iter, S4D_CSR_CMD, S4D_CMD_ACK);   /* 7 = ACK */
            if (s4d_read_epoch(&e_after) && e_after == e_expect && s4d_rd(S4D_CSR_FRAME_R) == (uint32_t)iter) {
                s4d_wr(S4D_CSR_ACKLO_W, (uint32_t)e_expect);
                s4d_wr(S4D_CSR_ACKHI_W, (uint32_t)(e_expect >> 32));
                s4d_wr(S4D_CSR_CMD, S4D_CMD_ACK);
                ack_idle = s4d_is_idle();
            }
            if (ack_idle != 1) { round_fail = 1; fail_why = "ack_not_idle"; }
            if (round_fail == 0) { s4d_lr_done(7u, iter); }
        }

        /* STEP G：epoch 单调 */
        if (round_fail == 0) {
            if (epoch_prev != 0 && e_expect <= epoch_prev) { round_fail = 1; fail_why = "epoch_not_monotonic"; }
            epoch_prev = e_expect;
            if (epoch_first == 0) { epoch_first = e_expect; }
            epoch_last = e_expect;
            if (e_min > elapsed_ms) { e_min = elapsed_ms; }
            if (e_max < elapsed_ms) { e_max = elapsed_ms; }
            e_sum += elapsed_ms;
        }

        if (round_fail != 0) {
            failures++;
            xil_printf("LONGRUN FAIL iter=%u why=%s status=0x%08x error=0x%08x decode_rc=%d count=%u raw=%u "
                       "ack_idle=%d elapsed_ms=%u spin=%u\r\n",
                       (unsigned)iter, fail_why, (unsigned)st, (unsigned)err, decode_rc,
                       (unsigned)count, (unsigned)raw, ack_idle, (unsigned)elapsed_ms, (unsigned)spin);
            exit_code = 2;
            break;
        }
        /* 心跳：**每轮一行**（诊断窗口据此确定最后完成的轮次） */
        xil_printf("LONGRUN STEP iter=%u elapsed_ms=%u wall_ms=%u epoch_lo=%u epoch_hi=%u status=0x%08x\r\n",
                   (unsigned)iter, (unsigned)elapsed_ms, (unsigned)wall_ms,
                   (unsigned)(uint32_t)e_expect, (unsigned)(uint32_t)(e_expect >> 32), (unsigned)st);
    }

    s4d_lr_rec_clear();   /* 收尾清零记录区（W4 校验全 0） */
    t_now = s4d_gt_ticks();
    wall_ms = (uint64_t)(((t_now - t_start) * 1000ull) / S4D_MS_DIV);
    {
        uint32_t done_iters = (failures == 0u) ? iter : (iter - 1u);
        uint32_t avg = (done_iters > 0u && e_min != 0xFFFFFFFFu) ? (e_sum / done_iters) : 0u;
        int within = (wall_ms >= S4D_LR_WALL_MS && done_iters >= S4D_LR_MIN_ITERS && failures == 0u) ? 1 : 0;
        if (failures == 0u && within == 0) { exit_code = 3; }
        if (failures == 0u) { exit_code = within ? 0 : 3; }
        xil_printf("LONGRUN RESULT={\"exit\":%d,\"iterations\":%u,\"failures\":%u,\"wall_ms_lo\":%u,"
                   "\"wall_ms_hi\":%u,\"min_elapsed_ms\":%u,\"avg_elapsed_ms\":%u,\"max_elapsed_ms\":%u,"
                   "\"epoch_first_lo\":%u,\"epoch_last_lo\":%u,\"tensor_crc32\":%u,\"box_class\":%d,"
                   "\"box_order\":%d,\"box_score_hi\":%08x,\"box_score_lo\":%08x,"
                   "\"box_x1_hi\":%08x,\"box_x1_lo\":%08x,\"box_y1_hi\":%08x,\"box_y1_lo\":%08x,"
                   "\"box_x2_hi\":%08x,\"box_x2_lo\":%08x,\"box_y2_hi\":%08x,\"box_y2_lo\":%08x,"
                   "\"within_judgement\":%d}\r\n",
                   exit_code, (unsigned)done_iters, (unsigned)failures,
                   (unsigned)(uint32_t)(wall_ms & 0xFFFFFFFFu), (unsigned)(uint32_t)(wall_ms >> 32),
                   (unsigned)((e_min == 0xFFFFFFFFu) ? 0u : e_min), (unsigned)avg, (unsigned)e_max,
                   (unsigned)(uint32_t)epoch_first, (unsigned)(uint32_t)epoch_last, (unsigned)tcr,
                   first.class_id, first.source_order,
                   (unsigned)(uint32_t)(first.score.u >> 32), (unsigned)(uint32_t)(first.score.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(first.x1.u >> 32), (unsigned)(uint32_t)(first.x1.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(first.y1.u >> 32), (unsigned)(uint32_t)(first.y1.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(first.x2.u >> 32), (unsigned)(uint32_t)(first.x2.u & 0xFFFFFFFFu),
                   (unsigned)(uint32_t)(first.y2.u >> 32), (unsigned)(uint32_t)(first.y2.u & 0xFFFFFFFFu),
                   within);
    }
    return exit_code;
}
#endif


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


/* ================= MVP 实现（必须在常量/工具函数定义之后） ================= */
_Static_assert(S4D_MVP_RAW_BYTES <= S4D_RAW_BYTES, "MVP raw frame 必须落在 RAW 区 [0x12000000,0x12C00000)");
_Static_assert(S5_RESULT_MAX_DETS >= S4D_DEC_MAX_BOX, "S5RS 容量必须 >= 解码上限（15）");
_Static_assert(S5_RESULT_ST_VALID == 0x00000001u, "S5RS status.bit0 必须为 valid=0x1（显示侧门控）");
_Static_assert((S5_RESULT_ST_VALID & 0x00000004u) == 0u, "MVP 不置 stale(bit2)，避免 47s/轮被 stale 挡显示");

static s2a_t62_detection s4d_mvp_dets[S5_RESULT_MAX_DETS];
static uint32_t s4d_mvp_ndet;

static uint32_t s4d_mvp_ms(uint64_t ticks)
{
    uint64_t ms = (ticks * 1000ull) / S4D_MS_DIV;
    return (uint32_t)ms;
}

/* 写 S5RS：先写框数据 + 头字段，flush 后再写 magic（读侧不会读到半成品，显示侧另有双读校验）。 */
static void s4d_mvp_publish(uint32_t frame_id, uint32_t ndet,
                            uint64_t t_cap, uint64_t t_inf, uint32_t status)
{
    volatile S5ResultHeader *hdr = (volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE;
    volatile S5ResultDet *dets = (volatile S5ResultDet *)(uintptr_t)(S5_RESULT_BASE + S5_RESULT_DETS_OFFSET);
    uint32_t i;

    if (ndet > S5_RESULT_MAX_DETS) { ndet = S5_RESULT_MAX_DETS; }
    for (i = 0u; i < ndet; i++) {
        double x1 = s4d_mvp_dets[i].x1, y1 = s4d_mvp_dets[i].y1;
        double x2 = s4d_mvp_dets[i].x2, y2 = s4d_mvp_dets[i].y2;
        double s = s4d_mvp_dets[i].score;
        double w, h;
        uint32_t xs, ys, ws, hs, q;
        /* 归一化（相对相机原图 1280×720）→ 显示画布 640×480 坐标 */
        if (x1 < 0.0) x1 = 0.0;
        if (y1 < 0.0) y1 = 0.0;
        if (x2 > 1.0) x2 = 1.0;
        if (y2 > 1.0) y2 = 1.0;
        xs = (uint32_t)(x1 * (double)S5_RAW_OUT_W + 0.5);
        ys = (uint32_t)(y1 * (double)S5_RAW_OUT_H + 0.5);
        w = (x2 - x1) * (double)S5_RAW_OUT_W;
        h = (y2 - y1) * (double)S5_RAW_OUT_H;
        ws = (uint32_t)(w + 0.5);
        hs = (uint32_t)(h + 0.5);
        if (xs >= S5_RAW_OUT_W) xs = S5_RAW_OUT_W - 1u;
        if (ys >= S5_RAW_OUT_H) ys = S5_RAW_OUT_H - 1u;
        if (ws == 0u) ws = 1u;
        if (hs == 0u) hs = 1u;
        if (xs + ws > S5_RAW_OUT_W) ws = S5_RAW_OUT_W - xs;
        if (ys + hs > S5_RAW_OUT_H) hs = S5_RAW_OUT_H - ys;
        if (s < 0.0) s = 0.0;
        if (s > 1.0) s = 1.0;
        q = (uint32_t)(s * 255.0 + 0.5);
        if (q > 255u) q = 255u;
        dets[i].x = (uint16_t)xs;
        dets[i].y = (uint16_t)ys;
        dets[i].w = (uint16_t)ws;
        dets[i].h = (uint16_t)hs;
        dets[i].cls = (uint8_t)((s4d_mvp_dets[i].class_id < 0) ? 0 : s4d_mvp_dets[i].class_id);
        dets[i].score_q8 = (uint8_t)q;
        dets[i].reserved = 0u;
        dets[i].pad = 0u;
    }
    hdr->frame_id = frame_id;
    hdr->n_dets = ndet;
    hdr->cap_lo = (uint32_t)(t_cap & 0xFFFFFFFFu);
    hdr->cap_hi = (uint32_t)(t_cap >> 32);
    hdr->inf_lo = (uint32_t)(t_inf & 0xFFFFFFFFu);
    hdr->inf_hi = (uint32_t)(t_inf >> 32);
    hdr->status = status;
    s4d_region_flush(S5_RESULT_BASE, S5_RESULT_BLOCK_BYTES);
    __asm__ volatile("dsb sy" ::: "memory");
    hdr->magic = S5_RESULT_MAGIC;          /* 最后写 magic：之前的字节已 flush */
    s4d_region_flush(S5_RESULT_BASE, 32u);
    __asm__ volatile("dsb sy" ::: "memory");
}

/* 2B 引擎每帧必须 ACK 才能回到 IDLE/SAFE_REUSE；否则下一轮 START 直接返回 -2（not idle），
 * 自循环会以"每帧瞬间失败 → status=0"空转（r08/r09 现象：frame_id=0x37A、n_dets=0、status=0）。
 * S4-B 主机路径里 ACK 由 host 发 OP_ACK；MVP 自循环必须自己发：读 epoch 双读校验 → ACKLO/ACKHI → CMD=4 → 等 idle。 */
static int s4d_mvp_ack(void)
{
    uint64_t epoch = 0u;
    uint32_t spin;
    if (!s4d_read_epoch(&epoch) || epoch == UINT64_MAX) { return -1; }
    s4d_wr(S4D_CSR_ACKLO_W, (uint32_t)(epoch & 0xFFFFFFFFu));
    s4d_wr(S4D_CSR_ACKHI_W, (uint32_t)(epoch >> 32));
    s4d_wr(S4D_CSR_CMD, S4D_CMD_ACK);
    for (spin = 0u; spin < 2000000u; spin++) {
        uint32_t st = s4d_rd(S4D_CSR_STATUS);
        if (((st & 7u) == S4D_ST_IDLE) && ((st & S4D_SAFE_REUSE) != 0u) &&
            ((st & (S4D_OWNER_PL | S4D_AXI_PEND | S4D_HEAD_VALID | S4D_TERMINAL | S4D_FIRST_PEND)) == 0u)) {
            return 0;
        }
    }
    return -2;
}

/* MVP 主循环：相机 raw(0x12000000) → D2 letterbox 416 → 2B PL 网络 → 解码/NMS → S5RS。 */
__attribute__((used, noinline)) static void s4d_mvp_cam_loop(void)
{
    const uint8_t *raw = (const uint8_t *)(uintptr_t)S5_RAW_FRAME_BASE;
    int8_t *tensor = (int8_t *)(uintptr_t)S4D_TENSOR_BASE;
    uint32_t frame_id = 0u;

    xil_printf("\r\nMVP APP: CAM=%d raw=0x%08x %ux%u bgr888 bytes=%u s5rs=0x%08x\r\n",
               (int)S4D_FRAME_SRC_CAM, (unsigned)S5_RAW_FRAME_BASE,
               (unsigned)S4D_MVP_RAW_W, (unsigned)S4D_MVP_RAW_H,
               (unsigned)S4D_MVP_RAW_BYTES, (unsigned)S5_RESULT_BASE);
    {
        const uint8_t *w = (const uint8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_INPUT_BASE);
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_INPUT_BASE, 8u);
        xil_printf("MVP WEIGHTS: %s @0x%08x\r\n",
                   (memcmp(w, "GFINT8W1", 8u) == 0) ? "GFINT8W1 OK" : "MISSING(GFINT8W1)",
                   (unsigned)(S4D_TENSOR_BASE + S4D_INPUT_BASE));
    }

    for (;;) {
        uint64_t t_begin = s4d_gt_ticks();
        uint64_t t_pre, t_pl, t_dec, t_pub;
        uint32_t dt_pre, dt_pl, dt_dec, dt_all, raw_nz = 0u;
        uint32_t nz_i;
        int rc;

        /* 1) 帧源：相机 raw（BGR888，紧排）。先统计前 4 KB 非零字，判断"帧有没有进来" */
        s4d_region_invalidate(S5_RAW_FRAME_BASE, S4D_MVP_RAW_BYTES);
        {
            const volatile uint32_t *rw = (const volatile uint32_t *)(uintptr_t)S5_RAW_FRAME_BASE;
            for (nz_i = 0u; nz_i < 1024u; nz_i++) { if (rw[nz_i] != 0u) { raw_nz++; } }
        }
        /* 2) D2 冻结口径预处理：端点对齐双线性 + v/255 + 对称量化 1/127 + pad 0.5 */
        rc = s4d_sw_preproc_bgr888_to_chw_int8(raw, (int)S4D_MVP_RAW_W, (int)S4D_MVP_RAW_H, tensor);
        t_pre = s4d_gt_ticks();
        if (rc != 0) {
            xil_printf("MVP ERR preproc rc=%d frame=%u\r\n", rc, (unsigned)frame_id);
            s4d_mvp_publish(frame_id, 0u, t_begin, t_pre, 0u);
            frame_id++;
            continue;
        }
        s4d_region_flush(S4D_TENSOR_BASE, S4D_TENSOR_BYTES);

        /* 3) PL 2B 网络（DONE_SAFE 后返回） */
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD13_OFF, S4D_HEAD13_BYTES);
        s4d_region_invalidate(S4D_TENSOR_BASE + S4D_HEAD26_OFF, S4D_HEAD26_BYTES);
        rc = s2b_network_start_from_tensor(S4D_MVP_SESSION, frame_id);
        t_pl = s4d_gt_ticks();
        if (rc != 0) {
            xil_printf("MVP ERR network rc=%d frame=%u\r\n", rc, (unsigned)frame_id);
            (void)s4d_mvp_ack();   /* 尽力把引擎从终态拉回 idle，避免后续每轮 -2 空转 */
            s4d_mvp_publish(frame_id, 0u, t_pre, t_pl, 0u);
            frame_id++;
            continue;
        }
        __asm__ volatile("dsb sy" ::: "memory");
        /* 3b) 每帧 ACK：释放 2B 引擎回 IDLE/SAFE_REUSE（缺失会让下一轮 START 返回 -2，status 永久 0） */
        if (s4d_mvp_ack() != 0) {
            xil_printf("MVP WARN ack failed frame=%u\r\n", (unsigned)frame_id);
        }

        /* 4) 解码/NMS（r13 冻结参考；坐标相对相机原图归一化） */
        s4d_cur_src_w = S4D_MVP_RAW_W;
        s4d_cur_src_h = S4D_MVP_RAW_H;
        rc = s2a_decode_nms_reference((const int8_t *)(uintptr_t)(S4D_TENSOR_BASE + S4D_HEAD13_OFF),
                                      S4D_MVP_SESSION, frame_id,
                                      s4d_mvp_dets, &s4d_mvp_ndet);
        t_dec = s4d_gt_ticks();
        if (rc != 0) {
            xil_printf("MVP ERR decode rc=%d frame=%u\r\n", rc, (unsigned)frame_id);
            s4d_mvp_publish(frame_id, 0u, t_pre, t_pl, 0u);
            frame_id++;
            continue;
        }

        /* 5) 发布 S5RS（先数据后 magic；cap/inf 为 GT ticks）
         *   安全失败闸：raw 前 4 KB 全零（相机未通）时，零 logits 会让 sigmoid(0)*sigmoid(0)=0.25
         *   恰好命中 score>=0.25 阈值，解码器会吐出"假框"——因此显式丢弃为 n_dets=0（帧仍 valid=1，
         *   网络照跑用于验证链路），并打印 MVP NOTE raw_blank。 */
        if (raw_nz == 0u) {
            if (s4d_mvp_ndet != 0u) {
                xil_printf("MVP NOTE raw_blank n_dets=%u->0 (raw 前 4KB 全零，判定无相机帧)\r\n",
                           (unsigned)s4d_mvp_ndet);
            }
            s4d_mvp_ndet = 0u;
        }
        s4d_mvp_publish(frame_id, s4d_mvp_ndet, t_pre, t_pl,
                        S5_RESULT_ST_VALID);
        t_pub = s4d_gt_ticks();
        /* 5b) 回读自检：status 写入路径必须可观测（raw_blank 时 status 仍必须=0x1、n_dets=0） */
        {
            volatile S5ResultHeader *rb = (volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE;
            uint32_t mg_rb, st_rb, n_rb;
            s4d_region_invalidate(S5_RESULT_BASE, 32u);
            __asm__ volatile("dsb sy" ::: "memory");
            mg_rb = rb->magic; st_rb = rb->status; n_rb = rb->n_dets;
            if ((mg_rb != S5_RESULT_MAGIC) || (st_rb != S5_RESULT_ST_VALID) || (n_rb != s4d_mvp_ndet)) {
                xil_printf("MVP ASSERT FAIL s5rs magic=0x%08x status=0x%x n=%u exp(magic=0x%08x status=0x%x n=%u)\r\n",
                           (unsigned)mg_rb, (unsigned)st_rb, (unsigned)n_rb,
                           (unsigned)S5_RESULT_MAGIC, (unsigned)S5_RESULT_ST_VALID,
                           (unsigned)s4d_mvp_ndet);
            }
            if (raw_nz == 0u) {
                xil_printf("MVP CHECK raw_blank status=0x%x n_dets=%u (exp status=0x1 n=0) %s\r\n",
                           (unsigned)st_rb, (unsigned)n_rb,
                           ((st_rb == S5_RESULT_ST_VALID) && (n_rb == 0u)) ? "OK" : "FAIL");
            }
        }
        dt_pre = s4d_mvp_ms(t_pre - t_begin);
        dt_pl = s4d_mvp_ms(t_pl - t_pre);
        dt_dec = s4d_mvp_ms(t_dec - t_pl);
        dt_all = s4d_mvp_ms(t_pub - t_begin);
        xil_printf("MVP TIME t0_pre=%u t1_pl=%u t2_decode=%u t3_pub=%u "
                   "dt_pre=%u dt_pl=%u dt_dec=%u dt_all=%u raw_nz=%u\r\n",
                   (unsigned)s4d_mvp_ms(t_pre), (unsigned)s4d_mvp_ms(t_pl),
                   (unsigned)s4d_mvp_ms(t_dec), (unsigned)s4d_mvp_ms(t_pub),
                   (unsigned)dt_pre, (unsigned)dt_pl, (unsigned)dt_dec, (unsigned)dt_all,
                   (unsigned)raw_nz);
        xil_printf("MVP S5RS frame=%u n_dets=%u magic=0x%08x status=0x%x\r\n",
                   (unsigned)frame_id, (unsigned)s4d_mvp_ndet,
                   (unsigned)((volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE)->magic,
                   (unsigned)((volatile S5ResultHeader *)(uintptr_t)S5_RESULT_BASE)->status);
        frame_id++;
    }
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
#if defined(S4D_CHAIN_SELFCHECK) && S4D_CHAIN_SELFCHECK
    xil_printf("S4D MODE=CHAIN_SELFCHECK geom=%s\r\n", S4D_GEOM.name);
    (void)s4d_chain_selfcheck();
    for (;;) { }
#endif
#if defined(S4D_CHAINB_SELFCHECK) && S4D_CHAINB_SELFCHECK
    xil_printf("S4D MODE=CHAINB_SELFCHECK geom=%s\r\n", S4D_GEOM.name);
    (void)s4d_chainb_selfcheck();
    for (;;) { }
#endif
#if defined(S4D_LONGRUN_SELFCHECK) && S4D_LONGRUN_SELFCHECK
    xil_printf("S4D MODE=LONGRUN_SELFCHECK geom=%s\r\n", S4D_GEOM.name);
    (void)s4d_longrun_selfcheck();
    xil_printf("LONGRUN DONE, halting\r\n");
    for (;;) { }
#endif

#if defined(S4D_FRAME_SRC_CAM) && S4D_FRAME_SRC_CAM
    s4d_mvp_cam_loop();   /* MVP：相机帧自主循环（不返回） */
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
