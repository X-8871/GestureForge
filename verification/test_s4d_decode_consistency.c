/* test_s4d_decode_consistency.c —— 真实解码/NMS 与 r13 冻结参考的离线一致性单测（主机） */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "../verification/s2a_ps_decode_nms_reference.h"

#define HEAD13_BYTES 5070
#define HEAD26_BYTES 20280
#define HEAD13_SCALE 0.24267549589862975
#define HEAD26_SCALE 0.30223452951025775
#define IMG_W 1440
#define IMG_H 1920
#define SCORE_TH 0.25

static int fails = 0;
static void expect_d(const char *what, double got, double exp)
{
    double d = fabs(got - exp);
    double tol = 1e-9 * (fabs(exp) > 1.0 ? fabs(exp) : 1.0);
    if (d > tol) { printf("[FAIL] %s got=%.17g exp=%.17g diff=%.3g\n", what, got, exp, d); fails++; }
}

int main(int argc, char **argv)
{
    if (argc < 3) { printf("用法: %s <head13.raw> <head26.raw>\n", argv[0]); return 2; }
    FILE *f13 = fopen(argv[1], "rb");
    FILE *f26 = fopen(argv[2], "rb");
    if (!f13 || !f26) { printf("[FAIL] 无法打开参考文件\n"); return 2; }
    static int8_t r13[HEAD13_BYTES], r26[HEAD26_BYTES];
    static double l13[HEAD13_BYTES], l26[HEAD26_BYTES];
    if (fread(r13, 1, HEAD13_BYTES, f13) != HEAD13_BYTES) { printf("[FAIL] head13 尺寸\n"); return 2; }
    if (fread(r26, 1, HEAD26_BYTES, f26) != HEAD26_BYTES) { printf("[FAIL] head26 尺寸\n"); return 2; }
    fclose(f13); fclose(f26);
    for (int i = 0; i < HEAD13_BYTES; i++) l13[i] = (double)r13[i] * HEAD13_SCALE;
    for (int i = 0; i < HEAD26_BYTES; i++) l26[i] = (double)r26[i] * HEAD26_SCALE;

    static s2a_t62_detection boxes[15];
    size_t count = 0, raw_count = 0;
    int rc = s2a_t62_decode_nms(l13, HEAD13_BYTES, l26, HEAD26_BYTES,
                               IMG_W, IMG_H, SCORE_TH, boxes, 15, &count, &raw_count);
    printf("decode_rc=%d count=%zu raw_candidates=%zu\n", rc, count, raw_count);
    if (rc != S2A_T62_OK) { printf("[FAIL] 解码返回 %d\n", rc); return 1; }
    if (count != 1) { printf("[FAIL] 检测数 got=%zu exp=1\n", count); fails++; }
    if (raw_count != 2) { printf("[FAIL] 原始候选数 got=%zu exp=2\n", raw_count); fails++; }
    if (count >= 1) {
        printf("box0 class=%d order=%d score=%.17g xyxy=[%.17g,%.17g,%.17g,%.17g]\n",
               boxes[0].class_id, boxes[0].source_order, boxes[0].score,
               boxes[0].x1, boxes[0].y1, boxes[0].x2, boxes[0].y2);
        if (boxes[0].class_id != 0) { printf("[FAIL] class_id\n"); fails++; }
        expect_d("score", boxes[0].score, 0.76970842332524037);
        expect_d("x1", boxes[0].x1, 0.24812970451481631);
        expect_d("y1", boxes[0].y1, 0.37139423076923078);
        expect_d("x2", boxes[0].x2, 0.34786113088325127);
        expect_d("y2", boxes[0].y2, 0.43629807692307693);
        if (boxes[0].source_order != 6570) { printf("[FAIL] source_order got=%d exp=6570\n", boxes[0].source_order); fails++; }
    }
    if (fails == 0) { printf("[PASS] 真实解码/NMS 与 r13 冻结参考逐字段一致（1 框、score、xyxy、source_order、raw_count）\n"); return 0; }
    printf("[FAIL] 共 %d 处不符\n", fails); return 1;
}
