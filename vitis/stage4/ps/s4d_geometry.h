/*
 * s4d_geometry.h —— 4-D 预处理几何参数表与最近邻 letterbox（PL/SW 共用同一份参数与算法）
 *
 * 唯一参数来源（ADR §8.2/§8.4）：输入 640×480 BGR888，输出 416×416 INT8 打包 RGB，
 * 等比缩放 new_w=416 / new_h=312，上下 pad 52 行、左右 pad 0 列（letterbox）。
 *   · 缩放比 416/640 = 13/20 ⇒ src_x = (x*20)/13
 *   · src_y = ((y - PAD_T)*20)/13
 *   · 输出 = 416*416*3 = 519,168 B，与冻结输入张量大小一致
 *   · 每分量 v → int8(v-128)，饱和 [-128,127]；pad 像素写 INT8 零点 0x00
 *
 * 该头文件为纯 C（无平台依赖），可被 PS 固件与主机离线单测同时包含，
 * 以保证 "SW 与将来 PL 版参数一致" 可被机械核对。
 */

#ifndef S4D_GEOMETRY_H
#define S4D_GEOMETRY_H

#include <stdint.h>

typedef struct {
    const char *name;
    int in_w, in_h;      /* 输入帧尺寸 */
    int new_w, new_h;    /* 缩放后有效区域 */
    int pad_l, pad_t;    /* letterbox pad */
    int out_w, out_h;    /* 输出尺寸 */
    int pixels;          /* out_w*out_h */
    int bytes;           /* pixels*3 */
    int num, den;        /* 缩放比 num/den = new_w/in_w = 13/20 */
} s4d_geom_params_t;

/* 唯一参数表：任何一处需要几何参数都必须引用这里，不得另写字面量 */
static const s4d_geom_params_t S4D_GEOM = {
    "letterbox_640x480_to_416x416",
    640, 480,
    416, 312,
    0, 52,
    416, 416,
    416 * 416,          /* 173,056 pixels */
    416 * 416 * 3,      /* 519,168 bytes（= 冻结张量大小） */
    13, 20              /* new_w/in_w = 416/640 = 13/20 */
};

/* 输出坐标 → 输入坐标（最近邻；调用前须确保在有效区内） */
static inline int s4d_src_x(int x)
{
    return (x * S4D_GEOM.den) / S4D_GEOM.num;   /* x*20/13 */
}

static inline int s4d_src_y(int y)
{
    return ((y - S4D_GEOM.pad_t) * S4D_GEOM.den) / S4D_GEOM.num;   /* (y-52)*20/13 */
}

/* INT8 饱和：v → v-128 */
static inline int8_t s4d_to_int8(uint8_t v)
{
    int t = (int)v - 128;
    if (t > 127) return (int8_t)127;
    if (t < -128) return (int8_t)(-128);
    return (int8_t)t;
}

/* 有效输出像素判定（pad 区为 0） */
static inline int s4d_is_pad(int x, int y)
{
    if (x < S4D_GEOM.pad_l || x >= S4D_GEOM.pad_l + S4D_GEOM.new_w) return 1;
    if (y < S4D_GEOM.pad_t || y >= S4D_GEOM.pad_t + S4D_GEOM.new_h) return 1;
    return 0;
}

/*
 * 最近邻 letterbox + BGR→RGB + INT8 打包。
 *   bgr : 输入缓冲，大小 = in_w*in_h*3，逐像素 B/G/R
 *   out : 输出缓冲，大小 = bytes（out_w*out_h*3），逐像素 R8/G8/B8
 * 返回 0 成功；-1 参数/尺寸不符。
 */
static inline int s4d_letterbox_pack(const uint8_t *bgr, int8_t *out)
{
    int x, y, sx, sy;
    if (bgr == 0 || out == 0) return -1;
    for (y = 0; y < S4D_GEOM.out_h; y++) {
        for (x = 0; x < S4D_GEOM.out_w; x++) {
            int8_t *p = out + ((y * S4D_GEOM.out_w) + x) * 3;
            if (s4d_is_pad(x, y)) {
                p[0] = 0; p[1] = 0; p[2] = 0;       /* pad = INT8 零点 */
                continue;
            }
            sx = s4d_src_x(x);
            sy = s4d_src_y(y);
            if (sx < 0 || sx >= S4D_GEOM.in_w || sy < 0 || sy >= S4D_GEOM.in_h) {
                p[0] = 0; p[1] = 0; p[2] = 0;       /* 越界防御（正常不应发生） */
                continue;
            }
            {
                const uint8_t *q = bgr + ((sy * S4D_GEOM.in_w) + sx) * 3;
                p[0] = s4d_to_int8(q[2]);           /* R ← BGR 的第 3 字节 */
                p[1] = s4d_to_int8(q[1]);           /* G */
                p[2] = s4d_to_int8(q[0]);           /* B */
            }
        }
    }
    return 0;
}

#endif /* S4D_GEOMETRY_H */