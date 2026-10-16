#ifndef S2A_PS_DECODE_NMS_REFERENCE_H
#define S2A_PS_DECODE_NMS_REFERENCE_H

#include <stddef.h>
#include <stdint.h>

/* 单个 tiny416 解码结果，坐标为裁剪后的归一化 xyxy。 */
typedef struct {
    int32_t class_id;
    int32_t source_order;
    double score;
    double x1;
    double y1;
    double x2;
    double y2;
} s2a_t62_detection;

/* C API 返回值：0 成功；非法参数 -1，非有限输入 -2，exp 溢出 -3，内存错误 -4。 */
enum {
    S2A_T62_OK = 0,
    S2A_T62_INVALID_ARGUMENT = -1,
    S2A_T62_NONFINITE_INPUT = -2,
    S2A_T62_EXP_OVERFLOW = -3,
    S2A_T62_NO_MEMORY = -4
};

/* 解码 [3,10,13,13] 和 [3,10,26,26] 的 float64 raw logits 并执行 D6 稳定 NMS。 */
/* 出错时 output、output_count 和 raw_candidate_count 保持调用前内容。 */
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
    size_t *raw_candidate_count);

#endif
