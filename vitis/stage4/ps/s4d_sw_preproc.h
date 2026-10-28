/*
 * s4d_sw_preproc.h —— 4-D SW 预处理（PS 侧）：RAW BGR888 -> letterbox -> 416x416 INT8 CHW
 *
 * 口径来源（**逐位复现，不得自定**）：
 *   · 几何：Darknet letterbox_image —— `s1_t02_d2_numeric_reference.py:116-138`（letterbox_geometry）
 *       640x480 → new 416x312、offset_x=0、offset_y=52（与 `vitis/stage4/ps/s4d_geometry.h` 参数表一致）
 *   · 缩放：Darknet resize_image 端点对齐双线性 —— 同文件 `:140-181`（_resize_bilinear_rgb_values）
 *   · 归一化/量化：`v/255` → 对称量化 scale=INPUT_SCALE=1/127、半数远离零舍入、饱和 [-127,127]
 *       —— 同文件 `:21`（INPUT_SCALE）、`:32-37`（round_away_from_zero）、`:44-52`（quantize_symmetric）、`:249-254`
 *   · pad：normalized 0.5 → int8 64 —— 同文件 `:136-137`（padding_normalized/uint8）、`:349-352`
 *   · 布局：CHW（plane 0=R、1=G、2=B）—— 同文件 `:228-247`（normalized_hwc_to_chw）
 *
 * 与 `s4d_geometry.h` 的差异（**已知规范冲突，见 S4D 证据说明**）：该头文件写的是"最近邻 + int8(v-128) + pad=0"，
 * 与冻结 D2 口径（双线性 + 1/127 + pad=0.5）不同；本实现按 **D2 口径**（因为冻结张量 da26d385… 由 D2 产生，
 * 网络输入语义以 D2 为准）。冲突需 lead/Wong 裁决后统一文档。
 */
#ifndef S4D_SW_PREPROC_H
#define S4D_SW_PREPROC_H

#include <stdint.h>

#define S4D_SW_PREPROC_DST_W   416
#define S4D_SW_PREPROC_DST_H   416
#define S4D_SW_PREPROC_BYTES   (S4D_SW_PREPROC_DST_W * S4D_SW_PREPROC_DST_H * 3)

/* 几何计算结果（Darknet letterbox_image 口径） */
typedef struct {
    int src_w, src_h;
    int new_w, new_h;
    int offset_x, offset_y;
} s4d_sw_geom_t;

/* 计算几何（与 letterbox_geometry 完全一致） */
void s4d_sw_letterbox_geometry(int src_w, int src_h, int dst_w, int dst_h, s4d_sw_geom_t *out);

/* 主入口：src 为 BGR888 HWC（每像素 B,G,R），out 为 INT8 CHW（R plane, G plane, B plane）。
 * 返回 0 成功；-1 参数非法。 */
int s4d_sw_preproc_bgr888_to_chw_int8(const uint8_t *bgr, int src_w, int src_h, int8_t *out);

/* 便于主机对拍：输入 RGB888 HWC */
int s4d_sw_preproc_rgb888_to_chw_int8(const uint8_t *rgb, int src_w, int src_h, int8_t *out);

#endif /* S4D_SW_PREPROC_H */