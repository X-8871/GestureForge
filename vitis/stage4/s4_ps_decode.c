/*
 * 阶段4 PS 侧解码/NMS 实现（S4-B）。
 *
 * 算法主体逐行对应 2B 冻结参考
 * D:\FPGA_Competition\w2b\verification\s2a_ps_decode_nms_reference.c，
 * 仅增加 int8 -> double 反量化入口，并把候选上限的溢出事实显式上报。
 * 该参考的排序比较器（score 降序、同分按 source_order 升序）与 D9 的
 * Python 稳定排序等价：候选插入顺序恰为 source_order 升序，故同分时
 * 保持“head 顺序 -> row-major cell -> anchor-local -> class_id”。
 */

#include "s4_ps_decode.h"

#include <float.h>
#include <math.h>
#include <stdlib.h>

/* 显式有限性判定：语义等价于 math.h 的 isfinite/isinf(double)，但避免 GCC 在
 * -Wconversion 下对类型通用宏的 double->float 误报（本机 mingw 行为已实测正确）。 */
static int s4_is_finite(double value)
{
    return !(value != value) && value <= DBL_MAX && value >= -DBL_MAX;
}

static int s4_is_infinite(double value)
{
    return value > DBL_MAX || value < -DBL_MAX;
}

static const uint32_t s4_anchor_width[6] = {10u, 23u, 37u, 81u, 135u, 344u};
static const uint32_t s4_anchor_height[6] = {14u, 27u, 58u, 82u, 169u, 319u};
static const uint32_t s4_mask13[3] = {3u, 4u, 5u};
static const uint32_t s4_mask26[3] = {1u, 2u, 3u};

static double s4_sigmoid(double value)
{
    if (value >= 0.0) {
        return 1.0 / (1.0 + exp(-value));
    }
    {
        const double exponential = exp(value);
        return exponential / (1.0 + exponential);
    }
}

static double s4_clip_unit(double value)
{
    if (value < 0.0) {
        return 0.0;
    }
    if (value > 1.0) {
        return 1.0;
    }
    return value;
}

static double s4_iou(const s4_detection *left, const s4_detection *right)
{
    const double intersection_left = left->x1 > right->x1 ? left->x1 : right->x1;
    const double intersection_top = left->y1 > right->y1 ? left->y1 : right->y1;
    const double intersection_right = left->x2 < right->x2 ? left->x2 : right->x2;
    const double intersection_bottom = left->y2 < right->y2 ? left->y2 : right->y2;
    const double intersection_width = intersection_right - intersection_left;
    const double intersection_height = intersection_bottom - intersection_top;
    const double intersection = (intersection_width > 0.0 ? intersection_width : 0.0) *
                                (intersection_height > 0.0 ? intersection_height : 0.0);
    const double left_width = left->x2 - left->x1;
    const double left_height = left->y2 - left->y1;
    const double right_width = right->x2 - right->x1;
    const double right_height = right->y2 - right->y1;
    const double left_area = (left_width > 0.0 ? left_width : 0.0) *
                             (left_height > 0.0 ? left_height : 0.0);
    const double right_area = (right_width > 0.0 ? right_width : 0.0) *
                              (right_height > 0.0 ? right_height : 0.0);
    const double union_area = left_area + right_area - intersection;
    return union_area != 0.0 ? intersection / union_area : 0.0;
}

static int s4_compare_detection(const void *left_pointer, const void *right_pointer)
{
    const s4_detection *left = (const s4_detection *)left_pointer;
    const s4_detection *right = (const s4_detection *)right_pointer;
    if (left->score > right->score) {
        return -1;
    }
    if (left->score < right->score) {
        return 1;
    }
    if (left->source_order < right->source_order) {
        return -1;
    }
    if (left->source_order > right->source_order) {
        return 1;
    }
    return 0;
}

void s4_dequantize_int8(const int8_t *source, size_t length, double scale, double *destination)
{
    size_t index;
    for (index = 0u; index < length; ++index) {
        destination[index] = (double)source[index] * scale;
    }
}

int s4_letterbox_geometry(uint32_t image_width, uint32_t image_height,
                          uint32_t *resized_width, uint32_t *resized_height,
                          uint32_t *pad_left, uint32_t *pad_top)
{
    if (image_width == 0u || image_height == 0u || resized_width == NULL ||
        resized_height == NULL || pad_left == NULL || pad_top == NULL) {
        return -1;
    }
    if ((uint64_t)S4_NETWORK_WIDTH * (uint64_t)image_height <
        (uint64_t)S4_NETWORK_HEIGHT * (uint64_t)image_width) {
        *resized_width = S4_NETWORK_WIDTH;
        *resized_height = (uint32_t)(((uint64_t)image_height * S4_NETWORK_WIDTH) / image_width);
    } else {
        *resized_height = S4_NETWORK_HEIGHT;
        *resized_width = (uint32_t)(((uint64_t)image_width * S4_NETWORK_HEIGHT) / image_height);
    }
    if (*resized_width == 0u || *resized_height == 0u) {
        return -1;
    }
    *pad_left = (S4_NETWORK_WIDTH - *resized_width) / 2u;
    *pad_top = (S4_NETWORK_HEIGHT - *resized_height) / 2u;
    return 0;
}

static int s4_decode_head(
    const double *values,
    uint32_t grid_width,
    uint32_t grid_height,
    const uint32_t *anchor_mask,
    uint32_t resized_width,
    uint32_t resized_height,
    uint32_t pad_left,
    uint32_t pad_top,
    double score_threshold,
    int32_t *source_order,
    s4_detection *candidates,
    size_t *candidate_count,
    size_t *pre_threshold_candidate_count,
    size_t *candidate_box_count,
    int *candidate_overflow)
{
    const size_t spatial_size = (size_t)grid_width * (size_t)grid_height;
    uint32_t row;
    for (row = 0u; row < grid_height; ++row) {
        uint32_t col;
        for (col = 0u; col < grid_width; ++col) {
            const size_t cell = (size_t)row * (size_t)grid_width + (size_t)col;
            uint32_t local_anchor;
            for (local_anchor = 0u; local_anchor < 3u; ++local_anchor) {
                const size_t base = (size_t)local_anchor * S4_ENTRY_COUNT * spatial_size + cell;
                const double raw_x = values[base];
                const double raw_y = values[base + spatial_size];
                const double raw_width = values[base + 2u * spatial_size];
                const double raw_height = values[base + 3u * spatial_size];
                const double raw_objectness = values[base + 4u * spatial_size];
                const uint32_t anchor_index = anchor_mask[local_anchor];
                double tx;
                double ty;
                double width_scale;
                double height_scale;
                double box_width;
                double box_height;
                double center_x;
                double center_y;
                double left;
                double right;
                double top;
                double bottom;
                double x1;
                double y1;
                double x2;
                double y2;
                double clipped_x1;
                double clipped_y1;
                double clipped_x2;
                double clipped_y2;
                double objectness;
                int positive_area;
                uint32_t class_id;

                if (!s4_is_finite(raw_x) || !s4_is_finite(raw_y) || !s4_is_finite(raw_width) ||
                    !s4_is_finite(raw_height) || !s4_is_finite(raw_objectness)) {
                    return S4_DECODE_NONFINITE_INPUT;
                }
                tx = s4_sigmoid(raw_x) * 1.05 - 0.5 * (1.05 - 1.0);
                ty = s4_sigmoid(raw_y) * 1.05 - 0.5 * (1.05 - 1.0);
                width_scale = exp(raw_width);
                height_scale = exp(raw_height);
                if (s4_is_infinite(width_scale) || s4_is_infinite(height_scale)) {
                    return S4_DECODE_EXP_OVERFLOW;
                }
                if (!s4_is_finite(width_scale) || !s4_is_finite(height_scale)) {
                    return S4_DECODE_NONFINITE_INPUT;
                }
                box_width = width_scale * ((double)s4_anchor_width[anchor_index] / 416.0);
                box_height = height_scale * ((double)s4_anchor_height[anchor_index] / 416.0);
                center_x = ((double)col + tx) / (double)grid_width;
                center_y = ((double)row + ty) / (double)grid_height;
                left = (center_x - box_width / 2.0) * 416.0;
                right = (center_x + box_width / 2.0) * 416.0;
                top = (center_y - box_height / 2.0) * 416.0;
                bottom = (center_y + box_height / 2.0) * 416.0;
                x1 = (left - (double)pad_left) / (double)resized_width;
                y1 = (top - (double)pad_top) / (double)resized_height;
                x2 = (right - (double)pad_left) / (double)resized_width;
                y2 = (bottom - (double)pad_top) / (double)resized_height;
                if (!s4_is_finite(box_width) || !s4_is_finite(box_height) ||
                    !s4_is_finite(x1) || !s4_is_finite(y1) || !s4_is_finite(x2) || !s4_is_finite(y2)) {
                    return S4_DECODE_NONFINITE_INPUT;
                }
                clipped_x1 = s4_clip_unit(x1);
                clipped_y1 = s4_clip_unit(y1);
                clipped_x2 = s4_clip_unit(x2);
                clipped_y2 = s4_clip_unit(y2);
                objectness = s4_sigmoid(raw_objectness);
                positive_area = clipped_x2 > clipped_x1 && clipped_y2 > clipped_y1;
                /* 阈值筛除前的候选机会数，对应 S4-A 可选诊断字段 candidate_count_pre_threshold
                 * （= 正面积候选框数 × 类别数）；它不是 candidate_count——后者是阈值筛除后、
                 * 15 框截断前、NMS 前的候选数（由下面的候选循环统计）。 */
                if (positive_area) {
                    ++(*candidate_box_count);
                    *pre_threshold_candidate_count += (size_t)S4_CLASS_COUNT;
                }

                for (class_id = 0u; class_id < S4_CLASS_COUNT; ++class_id) {
                    const double raw_class = values[base + (5u + class_id) * spatial_size];
                    const double confidence = objectness * s4_sigmoid(raw_class);
                    if (!s4_is_finite(raw_class) || !s4_is_finite(confidence)) {
                        return S4_DECODE_NONFINITE_INPUT;
                    }
                    if (confidence >= score_threshold && positive_area) {
                        s4_detection *candidate;
                        if (*candidate_count >= S4_MAX_CANDIDATES) {
                            /* 硬错误路径（镜像 2B 参考实现的 S2A_T62_INVALID_ARGUMENT）：
                             * 尝试追加第 (上限+1) 个候选即中止，不截断、不静默丢弃已有候选。
                             * tiny416 理论上界恰等于上限，故本分支不可达。 */
                            *candidate_overflow = 1;
                            return S4_DECODE_CANDIDATE_OVERFLOW;
                        }
                        candidate = &candidates[*candidate_count];
                        candidate->class_id = (int32_t)class_id;
                        candidate->source_order = *source_order + (int32_t)class_id;
                        candidate->score = confidence;
                        candidate->x1 = clipped_x1;
                        candidate->y1 = clipped_y1;
                        candidate->x2 = clipped_x2;
                        candidate->y2 = clipped_y2;
                        ++(*candidate_count);
                    }
                }
                *source_order += (int32_t)S4_CLASS_COUNT;
            }
        }
    }
    return S4_DECODE_OK;
}

int s4_decode_nms_int8(
    const int8_t *head13,
    size_t head13_len,
    const int8_t *head26,
    size_t head26_len,
    uint32_t image_width,
    uint32_t image_height,
    double score_threshold,
    double head13_scale,
    double head26_scale,
    s4_detection *output,
    size_t output_capacity,
    size_t *output_count,
    size_t *raw_candidate_count,
    size_t *pre_threshold_candidate_count,
    size_t *candidate_box_count,
    int *candidate_overflow)
{
    uint32_t resized_width = 0u;
    uint32_t resized_height = 0u;
    uint32_t pad_left = 0u;
    uint32_t pad_top = 0u;
    double *values13 = NULL;
    double *values26 = NULL;
    s4_detection *candidates = NULL;
    size_t candidate_count = 0u;
    size_t pre_threshold_count = 0u;
    size_t box_count = 0u;
    int32_t source_order = 0;
    size_t selected_count;
    size_t kept_count = 0u;
    size_t index;
    int overflow = 0;
    int result;

    if (head13 == NULL || head26 == NULL || output == NULL || output_count == NULL ||
        raw_candidate_count == NULL || pre_threshold_candidate_count == NULL ||
        candidate_box_count == NULL || candidate_overflow == NULL ||
        head13_len != S4_HEAD13_BYTES || head26_len != S4_HEAD26_BYTES ||
        image_width == 0u || image_height == 0u ||
        !s4_is_finite(score_threshold) || score_threshold < 0.25 || score_threshold > 0.50 ||
        !s4_is_finite(head13_scale) || !s4_is_finite(head26_scale) ||
        output_capacity < S4_MAX_OUTPUTS) {
        return S4_DECODE_INVALID_ARGUMENT;
    }

    if (s4_letterbox_geometry(image_width, image_height,
                              &resized_width, &resized_height, &pad_left, &pad_top) != 0) {
        return S4_DECODE_INVALID_ARGUMENT;
    }

    candidates = (s4_detection *)malloc(S4_MAX_CANDIDATES * sizeof(*candidates));
    values13 = (double *)malloc(S4_HEAD13_BYTES * sizeof(*values13));
    values26 = (double *)malloc(S4_HEAD26_BYTES * sizeof(*values26));
    if (candidates == NULL || values13 == NULL || values26 == NULL) {
        free(candidates);
        free(values13);
        free(values26);
        return S4_DECODE_NO_MEMORY;
    }

    /* int8 原字节 -> binary64（与 2A T29 参考的 float64 反量化一致）。 */
    s4_dequantize_int8(head13, S4_HEAD13_BYTES, head13_scale, values13);
    s4_dequantize_int8(head26, S4_HEAD26_BYTES, head26_scale, values26);

    result = s4_decode_head(values13, 13u, 13u, s4_mask13,
                            resized_width, resized_height, pad_left, pad_top,
                            score_threshold, &source_order, candidates, &candidate_count,
                            &pre_threshold_count, &box_count, &overflow);
    if (result == S4_DECODE_OK) {
        result = s4_decode_head(values26, 26u, 26u, s4_mask26,
                                resized_width, resized_height, pad_left, pad_top,
                                score_threshold, &source_order, candidates, &candidate_count,
                                &pre_threshold_count, &box_count, &overflow);
    }
    free(values13);
    free(values26);
    if (result != S4_DECODE_OK) {
        free(candidates);
        return result;
    }

    qsort(candidates, candidate_count, sizeof(*candidates), s4_compare_detection);
    selected_count = candidate_count < S4_MAX_OUTPUTS ? candidate_count : S4_MAX_OUTPUTS;
    for (index = 0u; index < selected_count; ++index) {
        size_t kept_index;
        int suppressed = 0;
        for (kept_index = 0u; kept_index < kept_count; ++kept_index) {
            if (candidates[index].class_id == output[kept_index].class_id &&
                s4_iou(&candidates[index], &output[kept_index]) >= S4_NMS_IOU) {
                suppressed = 1;
                break;
            }
        }
        if (!suppressed) {
            output[kept_count] = candidates[index];
            ++kept_count;
        }
    }
    free(candidates);
    *output_count = kept_count;
    *raw_candidate_count = candidate_count;
    *pre_threshold_candidate_count = pre_threshold_count;
    *candidate_box_count = box_count;
    *candidate_overflow = overflow;
    return S4_DECODE_OK;
}