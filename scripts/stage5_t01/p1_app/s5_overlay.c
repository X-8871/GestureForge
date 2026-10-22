/* S5-T01 P1：PS 合成视频源 + 软件叠框（零新增 PL）。
 *
 * 思路：阶段3 厂商应用已经把显示通道（MM2S VDMA → HDMI）初始化好并循环读取 pFrames[3]；
 * 本模块**直接往这些送显缓冲写像素**（合成测试图 + 预计算的检测框/标签），刷 cache 后即上屏。
 * 无传感器、无 S2MM：本函数被调用后**永不返回**，因此原 main 后续的 S2MM/传感器路径不会执行。
 *
 * 几何约束：框的像素矩形与标签位置由宿主端 `gen_overlay_cases.py` 用**冻结参考实现**
 * （verification/s5_display_geometry_reference.py，S5A-G0-v2）算好后嵌入 s5_overlay_cases.h；
 * 本文件**不含任何逆映射/取整逻辑**（只有 UI 布局与像素写入）。
 *
 * 字节序：按阶段3 证据，DDR 内为 B,G,R（offset0=蓝）。背景为灰度（三通道同值）故与字节序无关；
 *         框线颜色按该顺序书写，若实机 R/B 互换只影响颜色观感，不影响几何判定。
 */

#include "xil_printf.h"
#include "xil_cache.h"
#include "xtime_l.h"
#include "xil_types.h"
#include "xparameters.h"
#include "xaxivdma.h"
#include "display_ctrl.h"
#include "sleep.h"
#include <string.h>
#include "s5_overlay_cases.h"

#define S5_MM2S_SR_ADDR 0x43000004U   /* 显示通道 VDMA MM2S 状态寄存器（阶段3 证据：SR_MM2S=0x43000004） */
#define S5_DWELL_SECONDS 6U
#define S5_BAR_W 64
#ifndef S5_SINGLE_CASE
#define S5_SINGLE_CASE 0              /* 0=循环全部用例；N=只常显用例 N（便于确定性读数与拍照） */
#endif

static const u8 S5_CLASS_COLOR[5][3] = {
    {255, 64, 64}, {64, 255, 64}, {64, 64, 255}, {255, 255, 64}, {255, 64, 255},
};

static inline void s5_px(u8 *buf, u32 stride, int x, int y, u8 r, u8 g, u8 b)
{
    u8 *p;
    if (x < 0 || y < 0 || x >= S5_CANVAS_W || y >= S5_CANVAS_H) {
        return;
    }
    p = buf + (u32)y * stride + (u32)x * 3U;
    p[0] = b; p[1] = g; p[2] = r;      /* B,G,R（见文件头说明） */
}

static void s5_fill_rect(u8 *buf, u32 stride, int x1, int y1, int x2, int y2, u8 r, u8 g, u8 b)
{
    int x, y;
    for (y = y1; y <= y2; y++) {
        for (x = x1; x <= x2; x++) {
            s5_px(buf, stride, x, y, r, g, b);
        }
    }
}

static void s5_line(u8 *buf, u32 stride, int x1, int y1, int x2, int y2, int thick, u8 r, u8 g, u8 b)
{
    int steps = (x2 - x1 < 0 ? x1 - x2 : x2 - x1);
    int dy = (y2 - y1 < 0 ? y1 - y2 : y2 - y1);
    int i, t;
    if (dy > steps) steps = dy;
    if (steps == 0) steps = 1;
    for (i = 0; i <= steps; i++) {
        int x = x1 + (x2 - x1) * i / steps;
        int y = y1 + (y2 - y1) * i / steps;
        for (t = 0; t < thick; t++) {
            s5_px(buf, stride, x, y + t, r, g, b);
            if (thick > 1) s5_px(buf, stride, x + t, y, r, g, b);
        }
    }
}

/* 线宽 2、偶数线宽居中：几何线索引 p 占 {p-1, p}（与 border_pixel_sets 语义一致） */
static void s5_box_border(u8 *buf, u32 stride, int x1, int y1, int x2, int y2, const u8 *rgb)
{
    s5_line(buf, stride, x1, y1, x2, y1, 2, rgb[0], rgb[1], rgb[2]);   /* 上 */
    s5_line(buf, stride, x1, y2, x2, y2, 2, rgb[0], rgb[1], rgb[2]);   /* 下 */
    s5_line(buf, stride, x1, y1, x1, y2, 2, rgb[0], rgb[1], rgb[2]);   /* 左 */
    s5_line(buf, stride, x2, y1, x2, y2, 2, rgb[0], rgb[1], rgb[2]);   /* 右 */
}

static const s5_glyph_t *s5_glyph(char ch)
{
    int i;
    char up = (ch >= 'a' && ch <= 'z') ? (char)(ch - 'a' + 'A') : ch;
    for (i = 0; i < S5_GLYPH_COUNT; i++) {
        if (S5_GLYPHS[i].ch == up) return &S5_GLYPHS[i];
    }
    return 0;
}

static void s5_text(u8 *buf, u32 stride, int x, int y, const char *text, int scale,
                    u8 r, u8 g, u8 b)
{
    int cx = x;
    const char *p;
    for (p = text; *p; p++) {
        const s5_glyph_t *gl = s5_glyph(*p);          /* 注意：勿命名为 g，避免遮蔽颜色参数 g */
        if (gl) {
            int i;
            for (i = 0; i < gl->nseg; i++) {
                s5_line(buf, stride,
                        cx + gl->seg[i][0] * scale, y + gl->seg[i][1] * scale,
                        cx + gl->seg[i][2] * scale, y + gl->seg[i][3] * scale,
                        scale > 1 ? 2 : 1, r, g, b);
            }
        }
        cx += S5_GLYPH_ADV * scale;
    }
}

static void s5_text_plate(u8 *buf, u32 stride, int x, int y, const char *text, int scale, const u8 *rgb)
{
    int w = (int)S5_GLYPH_ADV * scale * (int)(strlen(text)) + 2;
    int h = S5_GLYPH_H * scale + 2;
    s5_fill_rect(buf, stride, x - 1, y - 1, x + w, y + h, 0, 0, 0);
    s5_text(buf, stride, x, y, text, scale, rgb[0], rgb[1], rgb[2]);
}

/* 确定性合成背景：竖直灰度条 + 64px 网格线 + 四角标记 + 中心十字（便于核对几何/画幅边界） */
static void s5_background(u8 *buf, u32 stride)
{
    int x, y;
    for (y = 0; y < S5_CANVAS_H; y++) {
        for (x = 0; x < S5_CANVAS_W; x++) {
            u8 v = (u8)((x / S5_BAR_W) * 32);
            s5_px(buf, stride, x, y, v, v, v);
        }
    }
    for (x = 0; x < S5_CANVAS_W; x += S5_BAR_W) {
        s5_line(buf, stride, x, 0, x, S5_CANVAS_H - 1, 1, 0, 0, 0);
    }
    s5_fill_rect(buf, stride, 0, 0, 15, 15, 255, 255, 255);
    s5_fill_rect(buf, stride, S5_CANVAS_W - 16, 0, S5_CANVAS_W - 1, 15, 255, 255, 255);
    s5_fill_rect(buf, stride, 0, S5_CANVAS_H - 16, 15, S5_CANVAS_H - 1, 255, 255, 255);
    s5_fill_rect(buf, stride, S5_CANVAS_W - 16, S5_CANVAS_H - 16, S5_CANVAS_W - 1, S5_CANVAS_H - 1, 255, 255, 255);
    s5_line(buf, stride, S5_CANVAS_W / 2, 0, S5_CANVAS_W / 2, S5_CANVAS_H - 1, 1, 255, 255, 255);
    s5_line(buf, stride, 0, S5_CANVAS_H / 2, S5_CANVAS_W - 1, S5_CANVAS_H / 2, 1, 255, 255, 255);
}

static void s5_render_case(u8 *buf, u32 stride, const s5_case_t *c)
{
    int i;
    s5_background(buf, stride);
    for (i = 0; i < c->nbox; i++) {
        const s5_box_t *b = &c->boxes[i];
        const u8 *rgb = S5_CLASS_COLOR[b->cls % 5];
        int lx = b->x1, ly = b->y1 - (S5_GLYPH_H * S5_LABEL_SCALE + 4);
        s5_box_border(buf, stride, b->x1, b->y1, b->x2, b->y2, rgb);
        if (ly < 18) ly = b->y1 + 4;                      /* 越界翻转到框内左上（契约锚点规则） */
        if (lx < 2) lx = 2;
        if (lx > S5_CANVAS_W - 4) lx = S5_CANVAS_W - 4;
        s5_text_plate(buf, stride, lx, ly, b->label, S5_LABEL_SCALE, rgb);
    }
    /* HUD：固定的 4 行（CASE n / BOXES n / SEM B / FRESH|STALE） */
    for (i = 0; i < 4; i++) {
        s5_text_plate(buf, stride, 24, 24 + i * (S5_GLYPH_H * S5_LABEL_SCALE + 8), c->hud[i],
                      S5_LABEL_SCALE, S5_CLASS_COLOR[i % 5]);
    }
}

static u32 s5_mm2s_frames(void)
{
    u32 sr = *(volatile u32 *)S5_MM2S_SR_ADDR;
    return (sr >> 16) & 0xFFU;                            /* VDMASR IRQFrameCntSts（阶段3 位定义证据） */
}

void s5_overlay_loop(u8 **pFrames, u32 num_frames, u32 stride, DisplayCtrl *disp)
{
    UINTPTR count_rate = COUNTS_PER_SECOND ? COUNTS_PER_SECOND : 1U;
    u32 ncase = S5_NUM_CASES;
    u32 ci;
    (void)disp;

    xil_printf("\r\nS5_P1_BEGIN canvas=%dx%d stride=%u frames=%u cases=%u\r\n",
               S5_CANVAS_W, S5_CANVAS_H, (unsigned)stride, (unsigned)num_frames, (unsigned)ncase);
    xil_printf("S5_P1_SOURCE=PS_SYNTHETIC (no sensor, no S2MM; zero new PL)\r\n");
    xil_printf("S5_P1_SEMANTICS=B_latest_result_overlay stale_limit_ns=%u\r\n", (unsigned)S5_STALE_LIMIT_NS);
    xil_printf("S5_P1_GEOMETRY=from_verification/s5_display_geometry_reference.py(S5A-G0-v2)\r\n");
    xil_printf("S5_P1_MEAS: display_fps start=MM2S frame_count increment stop=same(1s window)\r\n");
    {
        u32 i;
        for (i = 0; i < num_frames; i++) {
            xil_printf("S5_P1_BUF%u=%08X\r\n", (unsigned)i, (unsigned)(UINTPTR)pFrames[i]);
        }
    }

    for (ci = 0; ci < ncase; ci++) {
        xil_printf("S5_P1_CASE_TABLE id=%u boxes=%u stale=%u name=%s\r\n",
                   S5_CASES[ci].id, S5_CASES[ci].nbox, S5_CASES[ci].stale, S5_CASES[ci].name);
    }

    for (;;) {
        for (ci = 0; ci < ncase; ci++) {
            const s5_case_t *c = &S5_CASES[ci];
#if S5_SINGLE_CASE > 0
            if (c->id != (unsigned)S5_SINGLE_CASE) {
                continue;
            }
#endif
            u32 f;
            u32 f0, f1;
            XTime t0, t1;
            u32 sec;
            int fps10;

            for (f = 0; f < num_frames; f++) {
                s5_render_case(pFrames[f], stride, c);
                Xil_DCacheFlushRange((INTPTR)pFrames[f], stride * S5_CANVAS_H);
            }
            XTime_GetTime(&t0);
            f0 = s5_mm2s_frames();
            xil_printf("S5_P1_SHOW case=%u boxes=%u stale=%u hud=%s/%s/%s/%s\r\n",
                       c->id, c->nbox, c->stale, c->hud[0], c->hud[1], c->hud[2], c->hud[3]);

            for (sec = 0; sec < S5_DWELL_SECONDS; sec++) {
                usleep(1000000);
            }
            XTime_GetTime(&t1);
            f1 = s5_mm2s_frames();
            fps10 = (int)(((u64)((f1 - f0) & 0xFFU) * 10U * (u64)count_rate) /
                          (u64)(t1 - t0));
            xil_printf("S5_P1_MEAS case=%u frames_delta=%u window_counts=%u display_fps_x10=%d\r\n",
                       c->id, (unsigned)((f1 - f0) & 0xFFU), (unsigned)(t1 - t0), fps10);
        }
        xil_printf("S5_P1_CYCLE_DONE\r\n");
    }
}