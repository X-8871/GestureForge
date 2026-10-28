/*
 * s4d_sw_preproc.c —— 4-D SW 预处理实现：RAW BGR888 -> letterbox -> 416x416 INT8 CHW
 *
 * 逐位复现冻结 D2 数值口径（见 s4d_sw_preproc.h 头部引用），全部使用 double 中间量，
 * 不做任何中间取整（与冻结参考一致：双线性结果保持 double，最后一步才量化）。
 * 内存：单个 416*416 double 缓冲（约 1.38 MB，复用 3 次），不按源图尺寸分配。
 */
#include "s4d_sw_preproc.h"

#include <math.h>

#define S4D_INPUT_SCALE (1.0 / 127.0)
#define S4D_PAD_NORMALIZED 0.5
#define S4D_PLANE (S4D_SW_PREPROC_DST_W * S4D_SW_PREPROC_DST_H)

/* 半数远离零舍入（round_away_from_zero） */
static int s4d_round_away(double v)
{
    double mag = floor(fabs(v) + 0.5);
    return (int)(v >= 0.0 ? mag : -mag);
}

static int s4d_sat_int8(int v)
{
    if (v > 127) return 127;
    if (v < -127) return -127;
    return v;
}

/* 对称量化：q = sat(round_away(v / (1/127))) */
static int8_t s4d_quant_symmetric(double v)
{
    return (int8_t)s4d_sat_int8(s4d_round_away(v / S4D_INPUT_SCALE));
}

void s4d_sw_letterbox_geometry(int src_w, int src_h, int dst_w, int dst_h, s4d_sw_geom_t *out)
{
    int new_w, new_h;
    if (out == 0) return;
    out->src_w = src_w;
    out->src_h = src_h;
    if (src_w <= 0 || src_h <= 0 || dst_w <= 0 || dst_h <= 0) {
        out->new_w = out->new_h = out->offset_x = out->offset_y = 0;
        return;
    }
    if (((double)dst_w / (double)src_w) < ((double)dst_h / (double)src_h)) {
        new_w = dst_w;
        new_h = (src_h * dst_w) / src_w;
    } else {
        new_h = dst_h;
        new_w = (src_w * dst_h) / src_h;
    }
    out->new_w = new_w;
    out->new_h = new_h;
    out->offset_x = (dst_w - new_w) / 2;
    out->offset_y = (dst_h - new_h) / 2;
}

/* 端点对齐双线性，单通道：与 _resize_bilinear_rgb_values 的逐行/逐列特殊分支等价。
 * src 为 HWC 交错（步长 3），src_ch 为源通道号。 */
static void s4d_resize_bilinear_ch(const uint8_t *src, int src_w, int src_h, int src_ch,
                                   int new_w, int new_h, double *dst)
{
    double w_scale, h_scale;
    int x, y;
    if (src_w == new_w && src_h == new_h) {
        for (y = 0; y < src_h; y++) {
            for (x = 0; x < src_w; x++) {
                dst[y * src_w + x] = (double)src[((y * src_w + x) * 3) + src_ch];
            }
        }
        return;
    }
    w_scale = (new_w != 1) ? ((double)(src_w - 1) / (double)(new_w - 1)) : 0.0;
    h_scale = (new_h != 1) ? ((double)(src_h - 1) / (double)(new_h - 1)) : 0.0;
    for (y = 0; y < new_h; y++) {
        int iy, iy1;
        double dy;
        if (new_h == 1 || y == new_h - 1) {
            iy = src_h - 1;
            iy1 = iy;
            dy = 0.0;
        } else {
            double sy = (double)y * h_scale;
            iy = (int)sy;
            dy = sy - (double)iy;
            iy1 = (iy + 1 < src_h) ? iy + 1 : src_h - 1;
        }
        for (x = 0; x < new_w; x++) {
            int ix, ix1;
            double dx, top, bottom;
            if (new_w == 1 || x == new_w - 1) {
                ix = src_w - 1;
                ix1 = ix;
                dx = 0.0;
            } else {
                double sx = (double)x * w_scale;
                ix = (int)sx;
                dx = sx - (double)ix;
                ix1 = (ix + 1 < src_w) ? ix + 1 : src_w - 1;
            }
            top = (1.0 - dx) * (double)src[((iy * src_w + ix) * 3) + src_ch]
                + dx * (double)src[((iy * src_w + ix1) * 3) + src_ch];
            bottom = (1.0 - dx) * (double)src[((iy1 * src_w + ix) * 3) + src_ch]
                   + dx * (double)src[((iy1 * src_w + ix1) * 3) + src_ch];
            dst[y * new_w + x] = (1.0 - dy) * top + dy * bottom;
        }
    }
}

/*
 * 公共实现：src 为 HWC 交错 8-bit；swap_rb=1 时源为 BGR（输出 plane0=R ← 源 ch2）。
 * 输出 CHW：plane0=R、plane1=G、plane2=B。
 */
static int s4d_preproc_impl(const uint8_t *src, int src_w, int src_h, int swap_rb, int8_t *out)
{
    static double buf[S4D_PLANE];
    s4d_sw_geom_t g;
    int x, y, ch, pad_q;

    if (src == 0 || out == 0 || src_w <= 0 || src_h <= 0) return -1;
    s4d_sw_letterbox_geometry(src_w, src_h, S4D_SW_PREPROC_DST_W, S4D_SW_PREPROC_DST_H, &g);
    if (g.new_w <= 0 || g.new_h <= 0) return -1;

    pad_q = (int)s4d_quant_symmetric(S4D_PAD_NORMALIZED);
    for (ch = 0; ch < 3; ch++) {
        int8_t *plane = out + (size_t)ch * S4D_PLANE;
        int src_ch = swap_rb ? (2 - ch) : ch;
        s4d_resize_bilinear_ch(src, src_w, src_h, src_ch, g.new_w, g.new_h, buf);
        /* pad 全区 */
        for (y = 0; y < S4D_SW_PREPROC_DST_H; y++) {
            for (x = 0; x < S4D_SW_PREPROC_DST_W; x++) {
                plane[y * S4D_SW_PREPROC_DST_W + x] = (int8_t)pad_q;
            }
        }
        /* 有效区覆盖 */
        for (y = 0; y < g.new_h; y++) {
            for (x = 0; x < g.new_w; x++) {
                double n = buf[y * g.new_w + x] / 255.0;
                if (n < 0.0) n = 0.0;
                if (n > 1.0) n = 1.0;
                plane[(y + g.offset_y) * S4D_SW_PREPROC_DST_W + (x + g.offset_x)] = s4d_quant_symmetric(n);
            }
        }
    }
    return 0;
}

int s4d_sw_preproc_bgr888_to_chw_int8(const uint8_t *bgr, int src_w, int src_h, int8_t *out)
{
    return s4d_preproc_impl(bgr, src_w, src_h, 1, out);
}

int s4d_sw_preproc_rgb888_to_chw_int8(const uint8_t *rgb, int src_w, int src_h, int8_t *out)
{
    return s4d_preproc_impl(rgb, src_w, src_h, 0, out);
}