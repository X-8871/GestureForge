/* S5-T02（阶段5 §4.5 / §7.3 缺口）：**板上动态结果映射与绘制**的 C 实现（可移植核心）。
 *
 * 本文件是"宿主预计算框"的升级：把
 *   detection(class_id/score/xyxy 原图归一化) → 裁剪 → 显示像素索引 → 2 px 偶数线宽居中边框 → 标签锚点
 * 全部搬到 C 侧执行，**单一来源**镜像 `verification/s5_display_geometry_reference.py`（S5A-G0-v2）
 * 与 `scripts/stage5_t03/s5t03_render.py` 的 `label_anchor`/`safe_area_px`；**不得**另写第二套取整/线宽。
 *
 * 可移植性：核心只用 <math.h>/<stdint.h>/<stddef.h>，**不含任何 Xilinx 头**，因此可在宿主机隔离构建并
 * 与冻结参考逐像素对拍（离线上板对拍 ≠ 板上验证；板上项仍 NOT_RUN）。
 */

#ifndef S5_DYNAMIC_MAP_H
#define S5_DYNAMIC_MAP_H

#include <stddef.h>
#include <stdint.h>

#define S5D_CONTRACT_ID            "S5A-G0-v2"
#define S5D_ROUNDING_RULE          "round_half_up_to_nearest_pixel_index"
#define S5D_STALE_AGE_LIMIT_NS     (200000000LL)   /* 200 ms，与阶段4 同源常量 */
#define S5D_DISPLAY_LINE_WIDTH_PX  2               /* 正偶数；语义"偶数线宽居中" */
#define S5D_SAFE_AREA_PX_1080P     16              /* 按输出高度相对缩放 */
#define S5D_LABEL_GAP_PX           2
#define S5D_MAX_BOXES              15              /* ≤15 框，2A 稳定顺序**不重排** */
#define S5D_DISPLAY_SEMANTICS      "B_latest_result_overlay"
#define S5D_HUD_FIELD_COUNT        13
#define S5D_NOT_AVAILABLE          "NA"

/* 过期原因串（与冻结参考同字面） */
#define S5D_STALE_REASON_NONE  "none"
#define S5D_STALE_REASON_FLAG  "stale_flag"
#define S5D_STALE_REASON_AGE   "age_frame_exceeds_limit"
#define S5D_STALE_REASON_BOTH  "stale_flag_and_age_frame_exceeds_limit"

/* HUD 13 字段名（§5.4 顺序与 P1 一致） */
extern const char *const S5D_HUD_FIELDS[S5D_HUD_FIELD_COUNT];

typedef enum {
    S5D_OK = 0,
    S5D_E_NONFINITE = -1,          /* 坐标非有限 */
    S5D_E_NONPOSITIVE_AREA = -2,   /* 上游必须正面积：x2>x1 且 y2>y1 */
    S5D_E_TOO_MANY_BOXES = -3,     /* 超过 15 框 */
    S5D_E_DIMENSION = -4,          /* 画布/线宽非法 */
    S5D_E_CAPACITY = -5            /* 调用方缓冲不足 */
} s5d_status;

typedef struct { double x1, y1, x2, y2; } s5d_box_f;
typedef struct { int x1, y1, x2, y2; } s5d_rect_i;

typedef struct {
    int stale_flag;                /* 输入 */
    int age_frame_exceeds_limit;   /* 派生 */
    int64_t limit_ns;
    int64_t age_frame_ns;
    const char *reason;            /* 上面四个 S5D_STALE_REASON_* 之一 */
    int stale_effective;           /* 合并后：flag || age>limit（每结果只计一次由调用方保证） */
} s5d_stale;

typedef struct {
    uint64_t frames_committed;
    uint64_t warmup_frames;
    uint64_t dropped_frames;
    uint64_t timeouts;
    uint64_t error_results;
    uint64_t duplicate_results;
    uint64_t out_of_order_results;
    uint64_t stale_cleared;
    uint64_t zero_area_dropped;
    uint64_t boxes_drawn;
} s5d_counters;

typedef struct {
    int class_id;
    double score;
    s5d_box_f xyxy;
} s5d_detection;

typedef struct {
    int class_id;
    double score;
    s5d_rect_i rect;               /* 板上像素矩形（未钳画布的原始索引） */
    int border_pixels;             /* 展开并钳到画布后的边框像素数 */
    int label_x, label_y;          /* 标签锚点 */
    const char *label_placement;
} s5d_drawn_box;

typedef struct {
    int64_t capture_time_ns;
    int64_t result_time_ns;
    int64_t overlay_commit_ns;
    uint32_t frame_id;             /* 结果帧 id（result_frame_id） */
    uint32_t displayed_frame_id;
    uint32_t result_seq;
    int stale_flag;
    int warmup;                    /* 预热帧：计数、不绘制 */
    const char *state;             /* OK / NO_HAND / TIMEOUT / ERROR / DUPLICATE / OUT_OF_ORDER */
    int nbox;
    s5d_detection boxes[S5D_MAX_BOXES];
} s5d_frame;

typedef struct {
    int64_t age_result_ns;
    int64_t age_frame_ns;
    const char *display_semantics;
    s5d_stale stale;
    int nbox_drawn;
    uint64_t zero_area_dropped;
    s5d_drawn_box drawn[S5D_MAX_BOXES];
} s5d_frame_result;

/* ── 单一来源几何（与冻结参考逐字对应） ───────────────────────────────────── */
int s5d_round_half_up(double value);                                  /* floor(v+0.5) */
int s5d_clip_unit_box(const s5d_box_f *in, s5d_box_f *out,
                      int *out_clipped, int *out_zero_area);
int s5d_norm_to_display_px(const s5d_box_f *box, int display_width, int display_height,
                           s5d_rect_i *out);                          /* v·(span−1) 后一次性取整 */
int s5d_safe_area_px(int canvas_height);
int s5d_label_anchor(const s5d_rect_i *box, int text_width, int text_height,
                     int canvas_width, int canvas_height, int safe,
                     int *out_x, int *out_y, const char **out_placement);
size_t s5d_border_pixels(const s5d_rect_i *rect, int width,
                         int canvas_width, int canvas_height,
                         int *out_xs, int *out_ys, size_t capacity);   /* 返回像素数；按 (x,y) 升序 */
int s5d_effective_stale(int stale_flag, int64_t age_frame_ns, int64_t limit_ns, s5d_stale *out);
int s5d_compute_ages(int64_t capture_time_ns, int64_t result_time_ns, int64_t overlay_commit_ns,
                     int64_t *out_age_result_ns, int64_t *out_age_frame_ns);

/* ── 逐帧处理（板上同一份逻辑；宿主用于离线对拍） ─────────────────────────── */
s5d_status s5d_process_frame(const s5d_frame *frame, int canvas_width, int canvas_height,
                             const char *const *label_texts, const int *label_text_widths,
                             const int *label_text_heights, int nlabel_hint,
                             s5d_frame_result *out, s5d_counters *counters);

#endif /* S5_DYNAMIC_MAP_H */