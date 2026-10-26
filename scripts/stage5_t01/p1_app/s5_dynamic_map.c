/* S5-T02：动态映射核心实现。**逐字镜像**冻结参考（S5A-G0-v2）与渲染层 label_anchor/safe_area_px。
 * 单一来源纪律：本文件不得引入任何与参考不同的取整/线宽/钳位规则；对拍由 verify_dynamic_map.py 强制。
 */
#include "s5_dynamic_map.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

const char *const S5D_HUD_FIELDS[S5D_HUD_FIELD_COUNT] = {
    "CAPTURE_FPS", "INFERENCE_FPS", "DISPLAY_FPS", "INFERENCE_TIME_NS", "AGE_RESULT_NS",
    "AGE_FRAME_NS", "FRAME_ID", "BOXES", "STALE_CLEARED", "DROPPED_FRAMES", "TIMEOUTS",
    "WARMUP_STATE", "DISPLAY_SEMANTICS",
};

int s5d_round_half_up(double value)
{
    return (int)floor(value + 0.5);
}

int s5d_clip_unit_box(const s5d_box_f *in, s5d_box_f *out, int *out_clipped, int *out_zero_area)
{
    double cx1, cy1, cx2, cy2;
    if (in == NULL || out == NULL) {
        return S5D_E_DIMENSION;
    }
    if (!isfinite(in->x1) || !isfinite(in->y1) || !isfinite(in->x2) || !isfinite(in->y2)) {
        return S5D_E_NONFINITE;
    }
    if (!(in->x2 > in->x1 && in->y2 > in->y1)) {
        return S5D_E_NONPOSITIVE_AREA;             /* 上游必须正面积 */
    }
    cx1 = fmax(0.0, fmin(1.0, in->x1));
    cy1 = fmax(0.0, fmin(1.0, in->y1));
    cx2 = fmax(0.0, fmin(1.0, in->x2));
    cy2 = fmax(0.0, fmin(1.0, in->y2));
    out->x1 = cx1; out->y1 = cy1; out->x2 = cx2; out->y2 = cy2;
    if (out_clipped != NULL) {
        *out_clipped = !(cx1 == in->x1 && cy1 == in->y1 && cx2 == in->x2 && cy2 == in->y2);
    }
    if (out_zero_area != NULL) {
        *out_zero_area = !(cx2 > cx1 && cy2 > cy1);   /* 裁剪后零面积 ⇒ 不绘制 */
    }
    return S5D_OK;
}

int s5d_norm_to_display_px(const s5d_box_f *box, int display_width, int display_height,
                           s5d_rect_i *out)
{
    if (box == NULL || out == NULL || display_width <= 0 || display_height <= 0) {
        return S5D_E_DIMENSION;
    }
    /* fit="exact"：画布即原帧分辨率；中间量保持 double 连续，**只在最后一步取整一次** */
    out->x1 = s5d_round_half_up(box->x1 * (double)(display_width - 1));
    out->y1 = s5d_round_half_up(box->y1 * (double)(display_height - 1));
    out->x2 = s5d_round_half_up(box->x2 * (double)(display_width - 1));
    out->y2 = s5d_round_half_up(box->y2 * (double)(display_height - 1));
    return S5D_OK;
}

int s5d_safe_area_px(int canvas_height)
{
    int safe = s5d_round_half_up((double)S5D_SAFE_AREA_PX_1080P * (double)canvas_height / 1080.0);
    return safe < 1 ? 1 : safe;                    /* 与渲染层同口径：至少 1 px */
}

int s5d_label_anchor(const s5d_rect_i *box, int text_width, int text_height,
                     int canvas_width, int canvas_height, int safe,
                     int *out_x, int *out_y, const char **out_placement)
{
    /* 冻结规则：框左上外侧 → 越界翻转到框内左上 → 仍越界则钳入安全区。
     * placement 串与渲染层逐字一致：后缀顺序固定为 +clamped_bottom 再 +clamped_x。
     */
    static const char *const placements[8] = {
        "outside_top_left",
        "outside_top_left+clamped_x",
        "outside_top_left+clamped_bottom",
        "outside_top_left+clamped_bottom+clamped_x",
        "inside_top_left",
        "inside_top_left+clamped_x",
        "inside_top_left+clamped_bottom",
        "inside_top_left+clamped_bottom+clamped_x",
    };
    int x, y, max_x, flipped = 0, clamped_bottom = 0, clamped_x = 0;
    if (box == NULL || out_x == NULL || out_y == NULL) {
        return S5D_E_DIMENSION;
    }
    x = box->x1;
    y = box->y1 - text_height - S5D_LABEL_GAP_PX;
    if (y < safe) {                                  /* 上方越界 ⇒ 翻转到框内左上 */
        flipped = 1;
        y = box->y1 + S5D_LABEL_GAP_PX;
    }
    if (y + text_height > canvas_height - safe) {    /* 仍越界 ⇒ 钳入下安全边 */
        int clamped = canvas_height - safe - text_height;
        clamped_bottom = 1;
        y = (safe > clamped) ? safe : clamped;
    }
    max_x = canvas_width - safe - text_width;
    if (max_x < safe) {
        max_x = safe;                                /* 与 Python 的 max(safe, ...) 等价 */
    }
    if (x < safe || x > max_x || box->x2 > canvas_width - safe) {
        int target = x < safe ? safe : (x > max_x ? max_x : x);
        if (target != x) {
            clamped_x = 1;
        }
        x = target;
    }
    *out_x = x;
    *out_y = y;
    if (out_placement != NULL) {
        *out_placement = placements[(flipped ? 4 : 0) | (clamped_bottom ? 2 : 0) | (clamped_x ? 1 : 0)];
    }
    return S5D_OK;
}

static int s5d_push_pixel(int x, int y, int canvas_width, int canvas_height,
                          int *xs, int *ys, size_t count, size_t capacity)
{
    size_t i;
    if (x < 0 || x >= canvas_width || y < 0 || y >= canvas_height) {
        return 0;                                  /* 逐边钳到画布内 */
    }
    for (i = 0; i < count; i++) {                  /* 去重（像素规模小，线性扫描足够） */
        if (xs[i] == x && ys[i] == y) {
            return 0;
        }
    }
    if (count >= capacity) {
        return -1;
    }
    xs[count] = x;
    ys[count] = y;
    return 1;
}

size_t s5d_border_pixels(const s5d_rect_i *rect, int width,
                         int canvas_width, int canvas_height,
                         int *out_xs, int *out_ys, size_t capacity)
{
    int xa, xb, ya, yb, d, x, y;
    size_t count = 0;
    if (rect == NULL || out_xs == NULL || out_ys == NULL || width < 1 || (width % 2) != 0) {
        return 0;
    }
    xa = rect->x1 < rect->x2 ? rect->x1 : rect->x2;
    xb = rect->x1 < rect->x2 ? rect->x2 : rect->x1;
    ya = rect->y1 < rect->y2 ? rect->y1 : rect->y2;
    yb = rect->y1 < rect->y2 ? rect->y2 : rect->y1;
    /* 与参考同序：先上/下边（x 外、d 中、y 内），再左/右边；offsets = [-(w/2), w/2) */
    for (x = xa; x <= xb; x++) {
        for (d = -(width / 2); d < width / 2; d++) {
            int ys_pair[2];
            int k;
            ys_pair[0] = rect->y1 + d;
            ys_pair[1] = rect->y2 + d;
            for (k = 0; k < 2; k++) {
                int pushed = s5d_push_pixel(x, ys_pair[k], canvas_width, canvas_height,
                                            out_xs, out_ys, count, capacity);
                if (pushed < 0) {
                    return count;
                }
                count += (size_t)pushed;
            }
        }
    }
    for (y = ya; y <= yb; y++) {
        for (d = -(width / 2); d < width / 2; d++) {
            int xs_pair[2];
            int k;
            xs_pair[0] = rect->x1 + d;
            xs_pair[1] = rect->x2 + d;
            for (k = 0; k < 2; k++) {
                int pushed = s5d_push_pixel(xs_pair[k], y, canvas_width, canvas_height,
                                            out_xs, out_ys, count, capacity);
                if (pushed < 0) {
                    return count;
                }
                count += (size_t)pushed;
            }
        }
    }
    /* 参考返回 sorted(pixels)：按 (x,y) 升序（插入排序，规模小） */
    {
        size_t i, j;
        for (i = 1; i < count; i++) {
            int kx = out_xs[i], ky = out_ys[i];
            j = i;
            while (j > 0 && (out_xs[j - 1] > kx || (out_xs[j - 1] == kx && out_ys[j - 1] > ky))) {
                out_xs[j] = out_xs[j - 1];
                out_ys[j] = out_ys[j - 1];
                j--;
            }
            out_xs[j] = kx;
            out_ys[j] = ky;
        }
    }
    return count;
}

int s5d_effective_stale(int stale_flag, int64_t age_frame_ns, int64_t limit_ns, s5d_stale *out)
{
    int by_flag, by_age;
    if (out == NULL) {
        return S5D_E_DIMENSION;
    }
    by_flag = stale_flag ? 1 : 0;
    by_age = age_frame_ns > limit_ns ? 1 : 0;      /* 严格大于 */
    out->stale_flag = by_flag;
    out->age_frame_exceeds_limit = by_age;
    out->limit_ns = limit_ns;
    out->age_frame_ns = age_frame_ns;
    out->stale_effective = by_flag || by_age;
    if (by_flag && by_age) {
        out->reason = S5D_STALE_REASON_BOTH;
    } else if (by_flag) {
        out->reason = S5D_STALE_REASON_FLAG;
    } else if (by_age) {
        out->reason = S5D_STALE_REASON_AGE;
    } else {
        out->reason = S5D_STALE_REASON_NONE;
    }
    return S5D_OK;
}

int s5d_compute_ages(int64_t capture_time_ns, int64_t result_time_ns, int64_t overlay_commit_ns,
                     int64_t *out_age_result_ns, int64_t *out_age_frame_ns)
{
    if (overlay_commit_ns < result_time_ns) {
        return S5D_E_DIMENSION;                    /* 时间倒流不允许 */
    }
    if (out_age_result_ns != NULL) {
        *out_age_result_ns = overlay_commit_ns - result_time_ns;
    }
    if (out_age_frame_ns != NULL) {
        *out_age_frame_ns = overlay_commit_ns - capture_time_ns;
    }
    return S5D_OK;
}

s5d_status s5d_process_frame(const s5d_frame *frame, int canvas_width, int canvas_height,
                             const char *const *label_texts, const int *label_text_widths,
                             const int *label_text_heights, int nlabel_hint,
                             s5d_frame_result *out, s5d_counters *counters)
{
    int i, safe, drawn = 0;
    uint64_t zero_area = 0;
    s5d_frame_result result;
    (void)nlabel_hint;

    if (frame == NULL || out == NULL) {
        return S5D_E_DIMENSION;
    }
    if (frame->nbox > S5D_MAX_BOXES) {
        return S5D_E_TOO_MANY_BOXES;               /* ≤15 框；不重排 */
    }
    memset(&result, 0, sizeof(result));
    if (counters != NULL) {
        counters->frames_committed += 1;
    }
    result.display_semantics = S5D_DISPLAY_SEMANTICS;
    /* 五元组（两个年龄 + 语义）与过期判定**先于任何状态提前返回**统一计算：
     * 预热/超时/错误/等价/乱序帧同样必须报道五元组，否则 ≥100 帧索引不成立。 */
    if (s5d_compute_ages(frame->capture_time_ns, frame->result_time_ns,
                         frame->overlay_commit_ns, &result.age_result_ns,
                         &result.age_frame_ns) != S5D_OK) {
        return S5D_E_DIMENSION;
    }
    s5d_effective_stale(frame->stale_flag, result.age_frame_ns, S5D_STALE_AGE_LIMIT_NS,
                        &result.stale);

    if (frame->state != NULL && strcmp(frame->state, "TIMEOUT") == 0) {
        if (counters != NULL) { counters->timeouts += 1; }
        *out = result;
        return S5D_OK;                             /* 超时：单独计数，不冒充零框、不绘制 */
    }
    if (frame->state != NULL && strcmp(frame->state, "ERROR") == 0) {
        if (counters != NULL) { counters->error_results += 1; }
        *out = result;
        return S5D_OK;
    }
    if (frame->state != NULL && strcmp(frame->state, "DUPLICATE") == 0) {
        if (counters != NULL) { counters->duplicate_results += 1; }   /* 等价结果：计数、不绘制 */
        *out = result;
        return S5D_OK;
    }
    if (frame->state != NULL && strcmp(frame->state, "OUT_OF_ORDER") == 0) {
        if (counters != NULL) { counters->out_of_order_results += 1; }
        *out = result;
        return S5D_OK;
    }
    if (frame->warmup) {
        if (counters != NULL) { counters->warmup_frames += 1; }       /* 预热：计数、不绘制 */
        *out = result;
        return S5D_OK;
    }
    if (frame->state != NULL && strcmp(frame->state, "NO_HAND") == 0) {
        /* 无手势 ⇒ boxes=0 且**如实报"非过期"**（任务卡 §3）：清掉按 age 派生的 stale 标记，
         * 不计 stale_cleared（曾因把派生标记原样上报而与参考/任务卡口径冲突 —— 复审 B7）。 */
        result.stale.stale_effective = 0;
        result.stale.age_frame_exceeds_limit = 0;
        result.stale.reason = S5D_STALE_REASON_NONE;
        *out = result;
        return S5D_OK;
    }

    if (result.stale.stale_effective) {
        /* 过期 ⇒ 不绘制，stale_cleared +1（每结果只计一次：由调用方逐结果调用保证） */
        if (counters != NULL) { counters->stale_cleared += 1; }
        *out = result;
        return S5D_OK;
    }

    safe = s5d_safe_area_px(canvas_height);
    for (i = 0; i < frame->nbox; i++) {
        s5d_box_f clipped;
        s5d_rect_i rect;
        int clipped_flag = 0, zero = 0, tw, th, ax, ay;
        const char *placement = "outside_top_left";
        if (s5d_clip_unit_box(&frame->boxes[i].xyxy, &clipped, &clipped_flag, &zero) != S5D_OK) {
            return S5D_E_NONPOSITIVE_AREA;
        }
        if (zero) {                                 /* 零面积：不绘制且计数（不计入 stale） */
            zero_area += 1;
            continue;
        }
        if (s5d_norm_to_display_px(&clipped, canvas_width, canvas_height, &rect) != S5D_OK) {
            return S5D_E_DIMENSION;
        }
        tw = (label_text_widths != NULL) ? label_text_widths[i] : 0;
        th = (label_text_heights != NULL) ? label_text_heights[i] : 0;
        if (s5d_label_anchor(&rect, tw, th, canvas_width, canvas_height, safe,
                             &ax, &ay, &placement) != S5D_OK) {
            return S5D_E_DIMENSION;
        }
        {
            /* N2（复审）：核心自己算边框像素数并写入结果，避免板上调用方依赖一个从未赋值的字段 */
            static int border_xs[S5D_MAX_BORDER_PIXELS];
            static int border_ys[S5D_MAX_BORDER_PIXELS];
            size_t pixels = s5d_border_pixels(&rect, S5D_DISPLAY_LINE_WIDTH_PX,
                                              canvas_width, canvas_height,
                                              border_xs, border_ys, S5D_MAX_BORDER_PIXELS);
            result.drawn[drawn].border_pixels = (int)pixels;
        }
        result.drawn[drawn].class_id = frame->boxes[i].class_id;
        result.drawn[drawn].score = frame->boxes[i].score;
        result.drawn[drawn].rect = rect;
        result.drawn[drawn].label_x = ax;
        result.drawn[drawn].label_y = ay;
        result.drawn[drawn].label_placement = placement;
        (void)label_texts;
        drawn++;
        if (drawn >= S5D_MAX_BOXES) {
            break;
        }
    }
    result.nbox_drawn = drawn;
    result.zero_area_dropped = zero_area;
    if (counters != NULL) {
        counters->zero_area_dropped += zero_area;
        counters->boxes_drawn += (uint64_t)drawn;
    }
    *out = result;
    return S5D_OK;
}