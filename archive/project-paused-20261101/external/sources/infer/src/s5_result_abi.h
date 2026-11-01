/*
 * s5_result_abi.h —— 阶段5 P3b-sw：显示应用读取的**推理结果块 ABI**（lead 2026-10-30 冻结）
 *
 * 生产者：推理/解码应用（chain-lite A 另派生）；消费者：本显示应用。
 * 位置：DDR `0x20800000`（在帧缓冲末端 0x20708000 之后，预留 8 MiB）。
 *
 * 布局（全部 little-endian，u32 对齐）：
 *   0x00 u32 magic      = 0x53355253 ("S5RS")
 *   0x04 u32 frame_id
 *   0x08 u32 n_dets     (0..16)
 *   0x0C u32 cap_lo     t_capture_end 低 32 位（0xF8F00200 全局定时器 ticks）
 *   0x10 u32 cap_hi
 *   0x14 u32 inf_lo     t_infer_done 低 32 位
 *   0x18 u32 inf_hi
 *   0x1C u32 status     bit0=valid, bit1=overrun(结果丢失), bit2=stale(超 1 帧)
 *   0x20 起 16 × 16 B 检测项：
 *        u16 x, u16 y, u16 w, u16 h   （原图 640×480 坐标）
 *        u8  cls, u8 score_q8, u16 reserved
 *
 * ⚠ ABI 文本写“每项 16 B”，但字段合计 12 B（8 + 1 + 1 + 2）→ 末尾 4 B 为填充。
 *   本实现按 **16 B 步进** 读取、忽略填充；若生产端按 12 B 紧凑排布会产生 4 B 错位，
 *   联调时必须用同一份步进（见报告 §7 风险项）。
 *
 * 画面源：raw frame 放 DDR `0x12000000`（640×480 **BGR888** 紧排，921,600 B = 640×480×3）。
 *   该区属阶段4 裁决允许的 raw_frame `[0x12000000,0x12C00000)`（禁区已缩到
 *   `[0x12C08000,0x20000000)`），不属禁区。
 */
#ifndef S5_RESULT_ABI_H
#define S5_RESULT_ABI_H

#include <stdint.h>

/* ---- 结果块 ---- */
#define S5_RESULT_BASE 0x20800000u
#define S5_RESULT_SPACE_BYTES 0x00800000u /* 预留 8 MiB（实际只读 0x120 B） */
#define S5_RESULT_MAGIC 0x53355253u       /* "S5RS" */
#define S5_RESULT_MAX_DETS 16u
#define S5_RESULT_DET_BYTES 16u
#define S5_RESULT_DETS_OFFSET 0x0020u
#define S5_RESULT_BLOCK_BYTES (S5_RESULT_DETS_OFFSET + S5_RESULT_MAX_DETS * S5_RESULT_DET_BYTES) /* 0x120 */

/* 头部偏移（u32 字索引 = 偏移/4） */
#define S5_RESULT_W_MAGIC 0u
#define S5_RESULT_W_FRAME_ID 1u
#define S5_RESULT_W_N_DETS 2u
#define S5_RESULT_W_CAP_LO 3u
#define S5_RESULT_W_CAP_HI 4u
#define S5_RESULT_W_INF_LO 5u
#define S5_RESULT_W_INF_HI 6u
#define S5_RESULT_W_STATUS 7u

/* status 位 */
#define S5_RESULT_ST_VALID 0x00000001u
#define S5_RESULT_ST_OVERRUN 0x00000002u
#define S5_RESULT_ST_STALE 0x00000004u

/* 16 B / 项：前 12 B 有定义，后 4 B 填充（ABI 写死 16 B 步进） */
typedef struct S5ResultDet {
    uint16_t x;        /* 0..639，原图坐标 */
    uint16_t y;        /* 0..479 */
    uint16_t w;
    uint16_t h;
    uint8_t cls;       /* 0..4（五类） */
    uint8_t score_q8;  /* 0..255，Q8 分数（显示时按 /255*100 取整百分比） */
    uint16_t reserved; /* 保留，读端忽略 */
    uint32_t pad;      /* 填充到 16 B（见文件头 §ABI 16 vs 12 说明） */
} S5ResultDet;

typedef struct S5ResultHeader {
    uint32_t magic;
    uint32_t frame_id;
    uint32_t n_dets;
    uint32_t cap_lo;
    uint32_t cap_hi;
    uint32_t inf_lo;
    uint32_t inf_hi;
    uint32_t status;
} S5ResultHeader;

/* ---- 原始画面 ---- */
#define S5_RAW_FRAME_BASE 0x12000000u
#define S5_RAW_FRAME_H 720u
#define S5_RAW_FRAME_BPP 3u /* BGR888 */

/* B 路线（默认）：sensor 1280x480@15fps（2x 子采样，r31 已验证出流），显示侧水平 2x 抽样到 640x480。
 * -D S5_CAM_CAPTURE_1280=0 可切回 640x480 直采（4x 子采样若将来可用）。 */
#ifndef S5_CAM_CAPTURE_1280
#define S5_CAM_CAPTURE_1280 1
#endif

#if S5_CAM_CAPTURE_1280
#define S5_RAW_FRAME_W 1280u
#define S5_RAW_OUT_W 640u
#define S5_RAW_OUT_H 480u
#define S5_RAW_DECIM_X 1u
#define S5_RAW_DECIM_Y 1u
#else
#define S5_RAW_FRAME_W 640u
#define S5_RAW_OUT_W 640u
#define S5_RAW_DECIM_X 1u
#endif
#define S5_RAW_FRAME_STRIDE (S5_RAW_FRAME_W * S5_RAW_FRAME_BPP) /* 1280:3840 / 640:1920 */
#define S5_RAW_FRAME_BYTES (S5_RAW_FRAME_STRIDE * S5_RAW_FRAME_H) /* 1,843,200 / 921,600 */
#define S5_RAW_OUT_BYTES (S5_RAW_OUT_W * S5_RAW_OUT_H * S5_RAW_FRAME_BPP)

/* 编译期自检（ABI 尺寸写错会在编译时就失败，而不是上板读错位） */
_Static_assert(sizeof(S5ResultHeader) == 32u, "结果块头部必须 8×u32 = 32 B");
_Static_assert(sizeof(S5ResultDet) == S5_RESULT_DET_BYTES, "检测项必须 16 B（含 4 B 填充）");
_Static_assert((S5_RESULT_DETS_OFFSET % 4u) == 0u, "检测项起点必须 4 B 对齐");
_Static_assert(S5_RAW_FRAME_STRIDE == (S5_RAW_FRAME_W * 3u), "raw stride = W*3");
_Static_assert((S5_RAW_FRAME_BYTES == 2764800u) || (S5_RAW_FRAME_BYTES == 921600u),
               "raw frame 必须 1280x720x3(2,764,800) 或 640x480x3(921,600)");
_Static_assert((S5_RAW_OUT_W * S5_RAW_DECIM_X) <= S5_RAW_FRAME_W, "输出宽 x 抽样 <= 采集宽");
_Static_assert((S5_RAW_OUT_H * S5_RAW_DECIM_Y) <= S5_RAW_FRAME_H, "输出高 x 抽样 <= 采集高");

#endif /* S5_RESULT_ABI_H */