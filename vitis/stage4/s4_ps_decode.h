/*
 * 阶段4 PS 侧 YOLOv4-tiny416 检测头解码/NMS（S4-B）。
 *
 * 语义来源：2A 冻结 D9（verification/s1_t02_d9_yolo_decode.py）与 2B 冻结 C
 * 参考（w2b/verification/s2a_ps_decode_nms_reference.c/.h）。本文件不改变
 * 2A D9 语义，只在其前面加一层 int8 -> binary64 反量化：
 *
 *   logit = (double)(signed int8 原字节) * 对应头 int8_scale
 *
 * 冻结语义要点（逐条与 D9 对齐）：
 *   - 阈值含等号：score >= score_threshold（0.25）；
 *   - 类别内 greedy NMS，IoU >= 0.45 抑制；跨类别不抑制；
 *   - 先按分数稳定排序截断到 15 个，再执行 NMS；
 *   - 稳定 tie 顺序：head 顺序 -> row-major cell -> anchor-local 顺序 -> class_id；
 *   - D2 整数截断 resize + 左上 floor padding 逆映射；逐边裁剪到 [0,1]；
 *     裁剪后零面积框丢弃；
 *   - score = sigmoid(objectness_logit) * sigmoid(class_logit)；
 *   - tx/ty 使用 1.05 缩放减 0.025，tw/th 使用 exp。
 *
 * 本文件是离线主机实现，不声明任何板上期限/吞吐结论。
 */

#ifndef S4_PS_DECODE_H
#define S4_PS_DECODE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* 网络输入与头几何（2A G0 冻结值）。 */
#define S4_NETWORK_WIDTH 416u
#define S4_NETWORK_HEIGHT 416u
#define S4_CLASS_COUNT 5u
#define S4_ENTRY_COUNT 10u
#define S4_HEAD13_GRID 13u
#define S4_HEAD26_GRID 26u
#define S4_HEAD13_BYTES 5070u   /* 3 * 10 * 13 * 13 */
#define S4_HEAD26_BYTES 20280u  /* 3 * 10 * 26 * 26 */

/* 冻结后处理参数。 */
#define S4_SCORE_THRESHOLD 0.25
#define S4_NMS_IOU 0.45
#define S4_MAX_OUTPUTS 15u
/* 候选缓冲上限：等于理论最大候选数 (3*13*13 + 3*26*26) * 5 = 12675，与 2B 冻结参考实现的
 * S2A_T62_MAX_CANDIDATES 一致。2B 参考实现在尝试追加第 (上限+1) 个候选时返回
 * S2A_T62_INVALID_ARGUMENT 并中止（硬错误，无“截断到上限”行为）。本实现同语义：置位
 * candidate_overflow 并返回 S4_DECODE_CANDIDATE_OVERFLOW；tiny416 固定配置下理论最大候选数
 * 恰等于该上限，因此该分支不可达，candidate_overflow 恒为 false，但仍必须显式记录该字段。
 * S4-A 草案早期的 candidate_limit=4096 已弃用（会引入 2A D9 与 2B 参考实现中都不存在的候选
 * 截断），本实现不启用。 */
#define S4_MAX_CANDIDATES 12675u

/* 两头 int8 反量化 scale（2A G0 冻结值）。 */
#define S4_HEAD13_SCALE 0.24267549589862975
#define S4_HEAD26_SCALE 0.30223452951025775

/* 单个检测结果，坐标为裁剪后的归一化原图 xyxy。 */
typedef struct {
    int32_t class_id;
    int32_t source_order;
    double score;
    double x1;
    double y1;
    double x2;
    double y2;
} s4_detection;

/* 返回值：0 成功；非法参数 -1，非有限输入 -2，exp 溢出 -3，内存错误 -4，
 * 候选数达到缓冲上限 -5（硬错误，镜像 2B 参考实现的 S2A_T62_INVALID_ARGUMENT；
 * tiny416 固定配置下不可达）。 */
enum {
    S4_DECODE_OK = 0,
    S4_DECODE_INVALID_ARGUMENT = -1,
    S4_DECODE_NONFINITE_INPUT = -2,
    S4_DECODE_EXP_OVERFLOW = -3,
    S4_DECODE_NO_MEMORY = -4,
    S4_DECODE_CANDIDATE_OVERFLOW = -5
};

/*
 * 解码两个检测头的 INT8 原字节并执行 D9 稳定 NMS。
 *
 * head13_len 必须为 5070，head26_len 必须为 20280，image_width/image_height
 * 为正整数，score_threshold 位于闭区间 [0.25, 0.50]，output_capacity >= 15。
 * 输入缓冲区按 const 读取，绝不被改写（本函数不写入 head13/head26 指向的内存）。
 * 出错时所有输出参数保持调用前内容。
 *
 * 候选计数输出参数（口径必须分别记录，不得混用；S4-A r05 契约口径）：
 *   - raw_candidate_count：S4-A candidate_count 与 2B 冻结实现、2A T29 黄金的同口径值，
 *     即“阈值筛除后、稳定排序截断到 15 之前、NMS 前”的候选数（每 (框, 类别) 一个候选）。
 *     UART raw_candidate_count 与结果记录 candidate_count 都使用该值。
 *   - pre_threshold_candidate_count：S4-A 可选诊断字段 candidate_count_pre_threshold 的值，
 *     即“阈值筛除前”的候选机会数 = CLASS_COUNT × candidate_box_count；不参与对拍口径、
 *     不进 UART，也不得替代 candidate_count。
 *   - candidate_box_count：裁剪后正面积、通过几何门的候选框数（透明化上面两个口径）。
 *   - candidate_overflow：候选数达到缓冲上限时为 1。按 2B 参考实现属硬错误路径
 *     （S2A_T62_INVALID_ARGUMENT，本实现返回 S4_DECODE_CANDIDATE_OVERFLOW），
 *     本合同不定义“截断到候选上限”；tiny416 理论上界恰等于上限，故不可达、恒为 0，
 *     但字段必须保留并显式记录“未超限”事实。
 */
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
    int *candidate_overflow);

/* int8 -> binary64 反量化；导出供自检与复用。dst 长度必须为 length。 */
void s4_dequantize_int8(const int8_t *source, size_t length, double scale, double *destination);

/* D2 letterbox 整数几何；导出供几何自检。返回 0 成功，-1 参数非法。 */
int s4_letterbox_geometry(uint32_t image_width, uint32_t image_height,
                          uint32_t *resized_width, uint32_t *resized_height,
                          uint32_t *pad_left, uint32_t *pad_top);

#ifdef __cplusplus
}
#endif

#endif /* S4_PS_DECODE_H */