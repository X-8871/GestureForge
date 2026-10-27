/*
 * test_s4d_letterbox.c —— s4d_letterbox_pack 主机离线单测（不依赖板卡、不依赖 ARM 目标）
 *
 * 自检内容：
 *   1) 输出尺寸/字节数 = 416×416×3 = 519,168，与冻结张量大小一致；
 *   2) pad 行（y<52 与 y>=52+312）全零，pad 列（x<0 或 x>=416；本配置 pad_l=0）全零；
 *   3) 最近邻角点对应：有效区四角 (x,y) = (0,52),(415,52),(0,363),(415,363) 必须取到
 *      src=(0,0),(638,0),(0,478),(638,478) 的像素；
 *   4) 棋盘图案：把输入按 8×8 棋盘填成黑/白，输出有效区必须仍为棋盘且无插值混色（最近邻）；
 *   5) INT8 饱和：0x00→-128、0xFF→+127、0x80→0。
 *
 * 编译（任选）：
 *   gcc -O2 -std=c99 -o test_s4d_letterbox test_s4d_letterbox.c
 *   cl /O2 /W4 test_s4d_letterbox.c
 * 退出码：0=全部 PASS；1=存在 FAIL。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../vitis/stage4/ps/s4d_geometry.h"

#define IN_PIX (640 * 480)
#define IN_BYTES (IN_PIX * 3)

static int failures = 0;

static void expect_int(const char *what, long got, long exp)
{
    if (got != exp) {
        printf("[FAIL] %s: got=%ld exp=%ld\n", what, got, exp);
        failures++;
    }
}

static void expect_i8(const char *what, int got, int exp)
{
    if (got != exp) {
        printf("[FAIL] %s: got=%d exp=%d\n", what, got, exp);
        failures++;
    }
}

int main(void)
{
    uint8_t *bgr = (uint8_t *)malloc(IN_BYTES);
    int8_t *out = (int8_t *)malloc((size_t)S4D_GEOM.bytes);
    int x, y, i;
    if (!bgr || !out) { printf("[FAIL] 内存分配失败\n"); return 2; }

    /* 1) 尺寸 */
    expect_int("out_w", S4D_GEOM.out_w, 416);
    expect_int("out_h", S4D_GEOM.out_h, 416);
    expect_int("pixels", S4D_GEOM.pixels, 173056);
    expect_int("bytes", S4D_GEOM.bytes, 519168);
    expect_int("new_w", S4D_GEOM.new_w, 416);
    expect_int("new_h", S4D_GEOM.new_h, 312);
    expect_int("pad_t", S4D_GEOM.pad_t, 52);
    expect_int("pad_l", S4D_GEOM.pad_l, 0);

    /* 2) 最近邻映射端点 */
    expect_int("src_x(0)", s4d_src_x(0), 0);
    expect_int("src_x(415)", s4d_src_x(415), (415 * 20) / 13);      /* 638 */
    expect_int("src_y(52)", s4d_src_y(52), 0);
    expect_int("src_y(363)", s4d_src_y(363), ((363 - 52) * 20) / 13); /* 478 */

    /* 3) 输入填充：8×8 棋盘（黑白），BGR 三通道同值 */
    for (y = 0; y < 480; y++) {
        for (x = 0; x < 640; x++) {
            uint8_t v = (((x / 8) + (y / 8)) & 1) ? 0xFF : 0x00;
            uint8_t *q = bgr + ((y * 640) + x) * 3;
            q[0] = v; q[1] = v; q[2] = v;
        }
    }
    if (s4d_letterbox_pack(bgr, out) != 0) { printf("[FAIL] letterbox 返回非 0\n"); failures++; }

    /* 4) pad 行全零 */
    for (y = 0; y < 52; y++)
        for (x = 0; x < 416; x++) {
            const int8_t *p = out + ((y * 416) + x) * 3;
            if (p[0] || p[1] || p[2]) { failures++; printf("[FAIL] pad 行 y=%d x=%d 非零\n", y, x); y = 52; break; }
        }
    for (y = 364; y < 416; y++)
        for (x = 0; x < 416; x++) {
            const int8_t *p = out + ((y * 416) + x) * 3;
            if (p[0] || p[1] || p[2]) { failures++; printf("[FAIL] pad 行 y=%d x=%d 非零\n", y, x); y = 416; break; }
        }

    /* 5) 最近邻角点：四角输出必须等于对应输入像素的 INT8 值（棋盘 ⇒ 0x00→-128 或 0xFF→+127） */
    {
        int corners[4][2] = {{0, 52}, {415, 52}, {0, 363}, {415, 363}};
        for (i = 0; i < 4; i++) {
            int cx = corners[i][0], cy = corners[i][1];
            int sx = s4d_src_x(cx), sy = s4d_src_y(cy);
            const uint8_t *q = bgr + ((sy * 640) + sx) * 3;
            const int8_t *p = out + ((cy * 416) + cx) * 3;
            expect_i8("corner R", p[0], s4d_to_int8(q[2]));
            expect_i8("corner G", p[1], s4d_to_int8(q[1]));
            expect_i8("corner B", p[2], s4d_to_int8(q[0]));
        }
    }

    /* 6) 最近邻无混色：有效区每个像素必须恰好是 -128 或 +127（棋盘两色） */
    {
        int bad = 0;
        for (y = 52; y < 364; y++)
            for (x = 0; x < 416; x++) {
                const int8_t *p = out + ((y * 416) + x) * 3;
                if (!((p[0] == -128 || p[0] == 127) && p[0] == p[1] && p[1] == p[2])) bad++;
            }
        expect_int("non_nearest_pixels", bad, 0);
    }

    /* 7) INT8 饱和边界 */
    expect_i8("int8(0x00)", s4d_to_int8(0x00), -128);
    expect_i8("int8(0xFF)", s4d_to_int8(0xFF), 127);
    expect_i8("int8(0x80)", s4d_to_int8(0x80), 0);

    free(bgr);
    free(out);
    if (failures == 0) {
        printf("[PASS] s4d_letterbox：尺寸/pad/最近邻角点/无混色/INT8 饱和 全部通过\n");
        return 0;
    }
    printf("[FAIL] 共 %d 处不符\n", failures);
    return 1;
}