#include "s2a_ps_decode_nms_reference.h"

#include <math.h>
#include <stdlib.h>

#define S2A_T62_NETWORK_WIDTH 416u
#define S2A_T62_NETWORK_HEIGHT 416u
#define S2A_T62_CLASS_COUNT 5u
#define S2A_T62_ENTRY_COUNT 10u
#define S2A_T62_MAX_OUTPUTS 15u
#define S2A_T62_MAX_CANDIDATES 12675u
#define S2A_T62_NMS_IOU 0.45

static const uint32_t s2a_t62_anchor_width[6] = {10u, 23u, 37u, 81u, 135u, 344u};
static const uint32_t s2a_t62_anchor_height[6] = {14u, 27u, 58u, 82u, 169u, 319u};
static const uint32_t s2a_t62_mask13[3] = {3u, 4u, 5u};
static const uint32_t s2a_t62_mask26[3] = {1u, 2u, 3u};

static double s2a_t62_sigmoid(double value)
{
    if (value >= 0.0) {
        return 1.0 / (1.0 + exp(-value));
    }
    {
        const double exponential = exp(value);
        return exponential / (1.0 + exponential);
    }
}

static double s2a_t62_clip_unit(double value)
{
    if (value < 0.0) {
        return 0.0;
    }
    if (value > 1.0) {
        return 1.0;
    }
    return value;
}

static double s2a_t62_iou(const s2a_t62_detection *left, const s2a_t62_detection *right)
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

static int s2a_t62_compare_detection(const void *left_pointer, const void *right_pointer)
{
    const s2a_t62_detection *left = (const s2a_t62_detection *)left_pointer;
    const s2a_t62_detection *right = (const s2a_t62_detection *)right_pointer;
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

static int s2a_t62_decode_head(
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
    s2a_t62_detection *candidates,
    size_t *candidate_count)
{
    const size_t spatial_size = (size_t)grid_width * (size_t)grid_height;
    uint32_t row;
    for (row = 0u; row < grid_height; ++row) {
        uint32_t col;
        for (col = 0u; col < grid_width; ++col) {
            const size_t cell = (size_t)row * (size_t)grid_width + (size_t)col;
            uint32_t local_anchor;
            for (local_anchor = 0u; local_anchor < 3u; ++local_anchor) {
                const size_t base = (size_t)local_anchor * S2A_T62_ENTRY_COUNT * spatial_size + cell;
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
                uint32_t class_id;

                if (!isfinite(raw_x) || !isfinite(raw_y) || !isfinite(raw_width) ||
                    !isfinite(raw_height) || !isfinite(raw_objectness)) {
                    return S2A_T62_NONFINITE_INPUT;
                }
                tx = s2a_t62_sigmoid(raw_x) * 1.05 - 0.5 * (1.05 - 1.0);
                ty = s2a_t62_sigmoid(raw_y) * 1.05 - 0.5 * (1.05 - 1.0);
                width_scale = exp(raw_width);
                height_scale = exp(raw_height);
                if (isinf(width_scale) || isinf(height_scale)) {
                    return S2A_T62_EXP_OVERFLOW;
                }
                if (!isfinite(width_scale) || !isfinite(height_scale)) {
                    return S2A_T62_NONFINITE_INPUT;
                }
                box_width = width_scale * ((double)s2a_t62_anchor_width[anchor_index] / 416.0);
                box_height = height_scale * ((double)s2a_t62_anchor_height[anchor_index] / 416.0);
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
                if (!isfinite(box_width) || !isfinite(box_height) ||
                    !isfinite(x1) || !isfinite(y1) || !isfinite(x2) || !isfinite(y2)) {
                    return S2A_T62_NONFINITE_INPUT;
                }
                clipped_x1 = s2a_t62_clip_unit(x1);
                clipped_y1 = s2a_t62_clip_unit(y1);
                clipped_x2 = s2a_t62_clip_unit(x2);
                clipped_y2 = s2a_t62_clip_unit(y2);
                objectness = s2a_t62_sigmoid(raw_objectness);

                for (class_id = 0u; class_id < S2A_T62_CLASS_COUNT; ++class_id) {
                    const double raw_class = values[base + (5u + class_id) * spatial_size];
                    const double confidence = objectness * s2a_t62_sigmoid(raw_class);
                    if (!isfinite(raw_class) || !isfinite(confidence)) {
                        return S2A_T62_NONFINITE_INPUT;
                    }
                    if (confidence >= score_threshold && clipped_x2 > clipped_x1 && clipped_y2 > clipped_y1) {
                        s2a_t62_detection *candidate;
                        if (*candidate_count >= S2A_T62_MAX_CANDIDATES) {
                            return S2A_T62_INVALID_ARGUMENT;
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
                *source_order += (int32_t)S2A_T62_CLASS_COUNT;
            }
        }
    }
    return S2A_T62_OK;
}

int s2a_t62_decode_nms(
    const double *head13,
    size_t head13_len,
    const double *head26,
    size_t head26_len,
    uint32_t image_width,
    uint32_t image_height,
    double score_threshold,
    s2a_t62_detection *output,
    size_t output_capacity,
    size_t *output_count,
    size_t *raw_candidate_count)
{
    uint32_t resized_width;
    uint32_t resized_height;
    uint32_t pad_left;
    uint32_t pad_top;
    s2a_t62_detection *candidates;
    size_t candidate_count = 0u;
    int32_t source_order = 0;
    size_t selected_count;
    size_t kept_count = 0u;
    size_t index;
    int result;

    if (head13 == NULL || head26 == NULL || output == NULL || output_count == NULL ||
        raw_candidate_count == NULL || head13_len != 3u * 10u * 13u * 13u ||
        head26_len != 3u * 10u * 26u * 26u || image_width == 0u || image_height == 0u ||
        !isfinite(score_threshold) || score_threshold < 0.25 || score_threshold > 0.50 ||
        output_capacity < S2A_T62_MAX_OUTPUTS) {
        return S2A_T62_INVALID_ARGUMENT;
    }

    if ((uint64_t)416u * (uint64_t)image_height < (uint64_t)416u * (uint64_t)image_width) {
        resized_width = 416u;
        resized_height = (uint32_t)(((uint64_t)image_height * 416u) / image_width);
    } else {
        resized_height = 416u;
        resized_width = (uint32_t)(((uint64_t)image_width * 416u) / image_height);
    }
    if (resized_width == 0u || resized_height == 0u) {
        return S2A_T62_INVALID_ARGUMENT;
    }
    pad_left = (416u - resized_width) / 2u;
    pad_top = (416u - resized_height) / 2u;

    candidates = (s2a_t62_detection *)malloc(S2A_T62_MAX_CANDIDATES * sizeof(*candidates));
    if (candidates == NULL) {
        return S2A_T62_NO_MEMORY;
    }
    result = s2a_t62_decode_head(head13, 13u, 13u, s2a_t62_mask13,
                                 resized_width, resized_height, pad_left, pad_top,
                                 score_threshold, &source_order, candidates, &candidate_count);
    if (result == S2A_T62_OK) {
        result = s2a_t62_decode_head(head26, 26u, 26u, s2a_t62_mask26,
                                     resized_width, resized_height, pad_left, pad_top,
                                     score_threshold, &source_order, candidates, &candidate_count);
    }
    if (result != S2A_T62_OK) {
        free(candidates);
        return result;
    }

    qsort(candidates, candidate_count, sizeof(*candidates), s2a_t62_compare_detection);
    selected_count = candidate_count < S2A_T62_MAX_OUTPUTS ? candidate_count : S2A_T62_MAX_OUTPUTS;
    for (index = 0u; index < selected_count; ++index) {
        size_t kept_index;
        int suppressed = 0;
        for (kept_index = 0u; kept_index < kept_count; ++kept_index) {
            if (candidates[index].class_id == output[kept_index].class_id &&
                s2a_t62_iou(&candidates[index], &output[kept_index]) >= S2A_T62_NMS_IOU) {
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
    return S2A_T62_OK;
}
