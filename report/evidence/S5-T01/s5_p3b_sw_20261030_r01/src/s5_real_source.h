/*
 * s5_real_source.h —— 真实数据源适配：结果块解析 + 原始画面转换 + 回退判据
 *
 * 设计要点：
 *   · 全部是**纯函数**（只吃内存指针/长度），主机自检可原样跑（用 fixture 造块），
 *     板上只是把指针换成 0x20800000 / 0x12000000；
 *   · 解析做**双重一致性检查**：读 frame_id → 解析 → 再读 frame_id，不一致判“半更新”（torn），
 *     这一帧回退，不渲染撕裂的中间态；
 *   · 回退判据（lead 冻结）：
 *       magic 不符 / status.valid=0 / torn  → 回退模拟源（src="sim"，RESULT 带 reason）
 *       raw 画面全 0（相机未启动）        → 视频区用测试图案（src="test"，RESULT 带 reason）
 *   · 单位换算只用 s5_timebase.h 的 S5_GT_HZ=333333343，不走 BSP 的无括号宏。
 */
#ifndef S5_REAL_SOURCE_H
#define S5_REAL_SOURCE_H

#include <stdint.h>

#include "s5_display_app.h" /* S5FrameInfo / S5DetBox / S5_ST_* */
#include "s5_result_abi.h"
#include "s5_timebase.h"

/* 本帧画面/数据来自哪里（S5_SRC_* 定义在 s5_display_app.h，供绘图与结果行共用） */

/* S5Real_Parse 返回码（负值） */
#define S5_PARSE_OK 0
#define S5_PARSE_ERR_MAGIC -1    /* magic != 0x53355253 */
#define S5_PARSE_ERR_NOT_VALID -2 /* status.bit0(valid) == 0 */
#define S5_PARSE_ERR_TORN -3     /* frame_id 前后不一致（生产端正在写） */
#define S5_PARSE_ERR_SHAPE -4    /* n_dets > 16 等越界 */

/* 解析后的结果块（已做字节序/位域展开） */
typedef struct S5RealBlock {
    uint32_t magic;
    uint32_t frame_id;
    uint32_t n_dets;   /* 原始字段 */
    uint32_t n;        /* 实际采用（clamp 到 S5_RESULT_MAX_DETS） */
    uint32_t status;   /* 原始 status 字 */
    uint32_t valid;    /* bit0 */
    uint32_t overrun;  /* bit1 */
    uint32_t stale;    /* bit2 */
    uint64_t cap_ticks; /* t_capture_end（0xF8F00200 计数） */
    uint64_t inf_ticks; /* t_infer_done */
    S5ResultDet det[S5_RESULT_MAX_DETS];
} S5RealBlock;

/* 源名字（RESULT 的 src 值） */
const char *S5Src_Name(uint32_t kind);
/* 解析返回码 → RESULT 的 reason 字符串（成功返回 0） */
const char *S5Src_Reason(int parse_rc);

/* 解析结果块：0=可用；负值见 S5_PARSE_ERR_*（调用方据此回退并在 RESULT 里给 reason）。 */
int S5Real_Parse(const uint32_t *blk, S5RealBlock *out);

/* 结果块 → 每帧信息：age = now − cap、latency = now − inf（ticks → ms），
 * det 坐标保持原图 640×480（映射在绘图侧做），stale/overrun 转成 S5_ST_* 位。 */
void S5Real_ToFrameInfo(const S5RealBlock *b, uint64_t now_ticks, S5FrameInfo *info);

/* raw frame 是否全 0（相机未启动/未写入）。1=全 0，0=有内容。命中非 0 字节即提前返回。 */
int S5Real_IsBlank(const uint8_t *raw, uint32_t bytes);

/* 640×480 BGR888（紧排）→ 画布像素 0x00RRGGBB，共 pixels 个像素。 */
void S5Real_BgrToCanvas(const uint8_t *raw, uint32_t *canvas, uint32_t pixels);

/* Q8 分数（0..255）→ 整数百分比（0..100），四舍五入。 */
uint32_t S5Real_ScoreToPct(uint32_t score_q8);

/* ---------------- FPS 滑动窗口（真实源用时间戳算，模拟源用模型值） ---------------- */
typedef struct S5FpsWin {
    uint64_t t_first;
    uint64_t t_last;
    uint32_t n;
} S5FpsWin;

void S5Fps_Reset(S5FpsWin *w);
void S5Fps_Add(S5FpsWin *w, uint64_t t); /* 一次一帧的时间戳 */
uint32_t S5Fps_Get(const S5FpsWin *w);   /* 整数 fps；样本 <2 或 dt=0 返回 0 */
uint32_t S5Fps_GetX10(const S5FpsWin *w); /* ×10 定点（面板显示 30.0 用）；同上返回 0 */

#endif /* S5_REAL_SOURCE_H */