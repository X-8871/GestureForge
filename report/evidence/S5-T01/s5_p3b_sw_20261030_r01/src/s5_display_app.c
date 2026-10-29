/*
 * s5_display_app.c —— 阶段5 HDMI 显示链 PS 侧绘图/帧装配 + 模拟数据源（P3b-sw）
 *
 * 布局与口径见 s5_display_app.h（G0 冻结）。本文件分两部分：
 *   A) 纯绘图核心：只操作传入的像素缓冲，不碰 MMIO/时钟 → 可在主机上编译并渲染 PNG；
 *   B) 裸机 main()：仅在不定义 S5_HOST_TEST 时编译，负责帧缓冲绝对地址、VDMA 启动、
 *      每帧装配 + cache flush + 双缓冲乒乓。
 *
 * 像素格式：32-bit 字，低 24 位 RGB888（0x00RRGGBB）；VDMA 流侧 32-bit，
 * P3a BD 已用 xlslice 取 vid_data[23:0]，故高 8 位保持 0。
 */
#include "s5_display_app.h"

#include <string.h>

#include "s5_font8x16.h"
#include "s5_timebase.h" /* S5Ticks_Now/ToMs/FromUs：模拟源与真实实现共用同一时间基座；
                          * 该头文件只有声明 + static inline 换算，不依赖 Xilinx 头，主机自检可编译 */

/* ---------------- 基础工具 ---------------- */

static inline void s5_put(uint32_t *fb, int x, int y, uint32_t color)
{
    if ((x >= 0) && (x < S5_CANVAS_W) && (y >= 0) && (y < S5_CANVAS_H)) {
        fb[(uint32_t)y * (uint32_t)S5_CANVAS_W + (uint32_t)x] = color;
    }
}

static const uint8_t *s5_glyph(char ch)
{
    unsigned code = (unsigned char)ch;

    if ((code < S5_FONT_FIRST) || (code > S5_FONT_LAST)) {
        code = (unsigned char)'?';
    }
    return s5_font8x16[code - S5_FONT_FIRST];
}

/* 字符串拼接（不依赖 printf，xil_printf 的格式支持有限） */
static char *s5_cat(char *p, const char *s)
{
    while (*s != '\0') {
        *p++ = *s++;
    }
    return p;
}

/* 无符号十进制，width>0 时左侧补 0 */
static char *s5_u32(char *p, uint32_t v, int width)
{
    char tmp[10];
    int n = 0;

    do {
        tmp[n++] = (char)('0' + (v % 10u));
        v /= 10u;
    } while ((v != 0u) && (n < 10));

    while ((n < width) && (n < 10)) {
        tmp[n++] = '0';
    }
    while (n > 0) {
        *p++ = tmp[--n];
    }
    return p;
}

/* ×10 定点数 → "30.1" */
static char *s5_dec1(char *p, uint32_t x10)
{
    p = s5_u32(p, x10 / 10u, 0);
    *p++ = '.';
    *p++ = (char)('0' + (x10 % 10u));
    return p;
}

/* 8 位十六进制（大写） */
static char *s5_hex8(char *p, uint32_t v)
{
    static const char hex[] = "0123456789ABCDEF";
    int i;

    for (i = 7; i >= 0; i--) {
        *p++ = hex[(v >> (unsigned)(i * 4)) & 0xFu];
    }
    return p;
}

static char *s5_end(char *p)
{
    *p = '\0';
    return p;
}

/* 类别名/颜色表：**占位**，阶段5 类别定义冻结后替换（绘制逻辑不用改）。 */
static const char *const s5_class_name[S5_CLASS_NUM] = {"C0", "C1", "C2", "C3", "C4"};
static const uint32_t s5_class_color[S5_CLASS_NUM] = {
    S5_RGB(0xFF, 0x3B, 0x30), /* 红 */
    S5_RGB(0x34, 0xC7, 0x59), /* 绿 */
    S5_RGB(0x00, 0x71, 0xFF), /* 蓝 */
    S5_RGB(0xFF, 0xCC, 0x00), /* 黄 */
    S5_RGB(0xAF, 0x52, 0xDE), /* 紫 */
};

/* ---------------- 绘图原语 ---------------- */

void S5Draw_Pixel(uint32_t *fb, int x, int y, uint32_t color)
{
    s5_put(fb, x, y, color);
}

void S5Draw_Clear(uint32_t *fb, uint32_t color)
{
    uint32_t i;
    uint32_t n = (uint32_t)S5_CANVAS_W * (uint32_t)S5_CANVAS_H;

    for (i = 0; i < n; i++) {
        fb[i] = color;
    }
}

void S5Draw_RectFill(uint32_t *fb, int x, int y, int w, int h, uint32_t color)
{
    int yy;

    for (yy = y; yy < (y + h); yy++) {
        int xx;

        if ((yy < 0) || (yy >= S5_CANVAS_H)) {
            continue;
        }
        for (xx = x; xx < (x + w); xx++) {
            if ((xx >= 0) && (xx < S5_CANVAS_W)) {
                fb[(uint32_t)yy * (uint32_t)S5_CANVAS_W + (uint32_t)xx] = color;
            }
        }
    }
}

void S5Draw_RectLine(uint32_t *fb, int x, int y, int w, int h, int line_w, uint32_t color)
{
    int i;

    if ((w <= 0) || (h <= 0) || (line_w <= 0)) {
        return;
    }
    /* 上/下边 */
    for (i = 0; i < line_w; i++) {
        S5Draw_RectFill(fb, x, y + i, w, 1, color);
        S5Draw_RectFill(fb, x, y + h - 1 - i, w, 1, color);
    }
    /* 左/右边 */
    for (i = 0; i < line_w; i++) {
        S5Draw_RectFill(fb, x + i, y, 1, h, color);
        S5Draw_RectFill(fb, x + w - 1 - i, y, 1, h, color);
    }
}

void S5Draw_Checker(uint32_t *fb, int cell, uint32_t c0, uint32_t c1)
{
    int y;
    int x;

    if (cell <= 0) {
        cell = 40;
    }
    for (y = 0; y < S5_CANVAS_H; y++) {
        for (x = 0; x < S5_CANVAS_W; x++) {
            int odd = (((x / cell) + (y / cell)) & 1) != 0;
            fb[(uint32_t)y * (uint32_t)S5_CANVAS_W + (uint32_t)x] = odd ? c1 : c0;
        }
    }
}

void S5Draw_ColorBars(uint32_t *fb)
{
    /* 8 根标准彩条（75% 幅度），纵向贯穿整屏；右侧信息栏区域也一起画，便于证明整屏通路 */
    static const uint32_t bars[8] = {
        S5_RGB(0xBF, 0xBF, 0xBF), S5_RGB(0xBF, 0xBF, 0x00), S5_RGB(0x00, 0xBF, 0xBF),
        S5_RGB(0x00, 0xBF, 0x00), S5_RGB(0xBF, 0x00, 0xBF), S5_RGB(0xBF, 0x00, 0x00),
        S5_RGB(0x00, 0x00, 0xBF), S5_RGB(0x00, 0x00, 0x00),
    };
    int bar_w = S5_CANVAS_W / 8;
    int i;
    int y;

    for (y = 0; y < S5_CANVAS_H; y++) {
        for (i = 0; i < 8; i++) {
            int x;
            int x0 = i * bar_w;
            int x1 = (i == 7) ? S5_CANVAS_W : (x0 + bar_w);

            for (x = x0; x < x1; x++) {
                fb[(uint32_t)y * (uint32_t)S5_CANVAS_W + (uint32_t)x] = bars[i];
            }
        }
    }
}

void S5Draw_GrayRamp(uint32_t *fb)
{
    int y;
    int x;

    for (y = 0; y < S5_CANVAS_H; y++) {
        for (x = 0; x < S5_CANVAS_W; x++) {
            uint32_t g = (uint32_t)((x * 255) / (S5_CANVAS_W - 1));
            fb[(uint32_t)y * (uint32_t)S5_CANVAS_W + (uint32_t)x] = S5_RGB(g, g, g);
        }
    }
}

void S5Draw_Text(uint32_t *fb, int x, int y, const char *text, uint32_t fg, uint32_t bg)
{
    int cx = x;

    for (; *text != '\0'; text++, cx += S5_FONT_W) {
        const uint8_t *g = s5_glyph(*text);
        int row;

        for (row = 0; row < S5_FONT_H; row++) {
            uint8_t bits = g[row];
            int col;

            for (col = 0; col < S5_FONT_W; col++) {
                int on = (bits & (uint8_t)(0x80u >> col)) != 0u;
                if (on) {
                    s5_put(fb, cx + col, y + row, fg);
                } else if (bg != S5_COLOR_TRANSPARENT) {
                    s5_put(fb, cx + col, y + row, bg);
                }
            }
        }
    }
}

/* ---------------- 摄像头 letterbox 缩放 ---------------- */

void S5Draw_CameraLetterbox(uint32_t *fb, const uint32_t *cam)
{
    /* 最近邻：源坐标 = 目标坐标 × (640/960) = ×2/3，用“×2 再 /3”整数运算，误差 ≤1 px。
     * 逐列/逐行的源索引预先算好（LUT），避免每像素两次乘除；LUT 只初始化一次。 */
    static uint16_t sx_lut[S5_VID_W];
    static uint16_t sy_lut[S5_VID_H];
    static int inited;
    int y;

    if (cam == 0) {
        return;
    }

    if (!inited) {
        int x;

        for (x = 0; x < S5_VID_W; x++) {
            sx_lut[x] = (uint16_t)(((uint32_t)x * S5_CAM_W) / (uint32_t)S5_VID_W);
        }
        for (y = 0; y < S5_VID_H; y++) {
            sy_lut[y] = (uint16_t)(((uint32_t)y * S5_CAM_H) / (uint32_t)S5_VID_H);
        }
        inited = 1;
    }

    for (y = 0; y < S5_VID_H; y++) {
        const uint32_t *src = cam + (uint32_t)sy_lut[y] * (uint32_t)S5_CAM_W;
        uint32_t *dst = fb + (uint32_t)(S5_VID_Y + y) * (uint32_t)S5_CANVAS_W + (uint32_t)S5_VID_X;
        int x;

        for (x = 0; x < S5_VID_W; x++) {
            dst[x] = src[sx_lut[x]];
        }
    }
    /* 左右黑边由 S5Draw_Clear(BLACK) 保证（S5_VID_X = 160 px） */
}

/* 检测框：摄像头 640×480 坐标 → 画布坐标（x + 160，×3/2），2 px 线宽 */
void S5Draw_Boxes(uint32_t *fb, const S5DetBox *det, uint32_t n)
{
    uint32_t i;
    uint32_t count = (n > S5_MAX_DET) ? S5_MAX_DET : n;

    if (det == 0) {
        return;
    }
    for (i = 0; i < count; i++) {
        const S5DetBox *b = &det[i];
        uint32_t color = (b->cls < S5_CLASS_NUM) ? s5_class_color[b->cls] : S5_COLOR_WHITE;
        int x0 = S5_VID_X + ((int)b->x * S5_SCALE_NUM) / S5_SCALE_DEN;
        int y0 = S5_VID_Y + ((int)b->y * S5_SCALE_NUM) / S5_SCALE_DEN;
        int w = ((int)b->w * S5_SCALE_NUM) / S5_SCALE_DEN;
        int h = ((int)b->h * S5_SCALE_NUM) / S5_SCALE_DEN;
        char label[16];
        char *p;

        if ((w <= 0) || (h <= 0)) {
            continue;
        }

        S5Draw_RectLine(fb, x0, y0, w, h, S5_BOX_LINE_W, color);

        /* 标签：类别名 + 整数分数，黑底彩字，放在框上方（顶不下时放框内） */
        p = s5_cat(label, (b->cls < S5_CLASS_NUM) ? s5_class_name[b->cls] : "CX");
        *p++ = ' ';
        p = s5_u32(p, b->score, 2);
        s5_end(p);

        {
            int ly = (y0 >= (S5_FONT_H + 2)) ? (y0 - S5_FONT_H - 2) : (y0 + 2);
            int lx = x0;

            if (lx < S5_VID_X) {
                lx = S5_VID_X;
            }
            S5Draw_Text(fb, lx, ly, label, color, S5_COLOR_BLACK);
        }
    }
}

/* ---------------- 右侧信息栏 ---------------- */

static const char *s5_dma_state_text(uint32_t dma_state)
{
    switch (dma_state) {
    case S5_DMA_RUN:
        return "RUN";
    case S5_DMA_ERR:
        return "ERR";
    default:
        return "OFF";
    }
}

static uint32_t s5_dma_state_color(uint32_t dma_state)
{
    switch (dma_state) {
    case S5_DMA_RUN:
        return S5_COLOR_OK;
    case S5_DMA_ERR:
        return S5_COLOR_BAD;
    default:
        return S5_COLOR_WARN;
    }
}

/* 数据源文本（与 s5_real_source.c 的 S5Src_Name 同口径；这里自带一份，避免绘图核心耦合数据源模块） */
static const char *s5_src_text(uint32_t src_kind)
{
    switch (src_kind) {
    case S5_SRC_REAL:
        return "REAL";
    case S5_SRC_REAL_NOBOX:
        return "REAL_NB"; /* 真实画面、无结果块（无框） */
    case S5_SRC_TEST:
        return "TEST";
    case S5_SRC_SIM:
        return "SIM";
    default:
        return "NONE";
    }
}

/* ---------------- 信息栏局部重绘支持 ---------------- */

typedef struct {
    const uint32_t *fb;
    uint32_t sig;
    uint32_t inited;
} S5PanelCache;

static S5PanelCache s5_panel_cache[4];

static uint32_t s5_panel_sig(const S5FrameInfo *info, uint32_t dma_state)
{
    uint32_t h = 2166136261u;
    uint32_t i;

#define S5_SIG_U32(v) (h = (h ^ (uint32_t)(v)) * 16777619u)
    S5_SIG_U32(info->frame_id);
    S5_SIG_U32((uint32_t)info->fps_cap_x10);
    S5_SIG_U32((uint32_t)info->fps_inf_x10);
    S5_SIG_U32((uint32_t)info->fps_dis_x10);
    S5_SIG_U32((uint32_t)info->fps_upd_x10);
    S5_SIG_U32((uint32_t)info->latency_ms);
    S5_SIG_U32((uint32_t)info->age_ms);
    S5_SIG_U32((uint32_t)info->status);
    S5_SIG_U32(dma_state);
    S5_SIG_U32((uint32_t)info->src_kind);
    S5_SIG_U32((uint32_t)info->det_count);
    for (i = 0u; (i < info->det_count) && (i < S5_MAX_DET); i++) {
        S5_SIG_U32((uint32_t)(uint16_t)info->det[i].x);
        S5_SIG_U32((uint32_t)(uint16_t)info->det[i].y);
        S5_SIG_U32((uint32_t)(uint16_t)info->det[i].w);
        S5_SIG_U32((uint32_t)(uint16_t)info->det[i].h);
        S5_SIG_U32((uint32_t)info->det[i].cls);
        S5_SIG_U32((uint32_t)info->det[i].score);
    }
#undef S5_SIG_U32
    return h;
}

/* 清屏后信息栏被抹掉：把该 buffer 的面板缓存置为“未初始化”，强制下一帧整栏重绘 */
static void s5_panel_invalidate(const uint32_t *fb)
{
    uint32_t n;

    for (n = 0u; n < 4u; n++) {
        if (s5_panel_cache[n].fb == fb) {
            s5_panel_cache[n].inited = 0u;
        }
    }
}

void S5Draw_InfoPanel(uint32_t *fb, const S5FrameInfo *info, uint32_t dma_state)
{
    const int x = S5_PANEL_X + 8;
    const int pitch = 20;
    int y = 34;
    char line[40];
    char *p;
    uint32_t i;
    uint32_t age_over;
    uint32_t stale;
    uint32_t sig;
    uint32_t n;
    S5PanelCache *slot = 0;
    int full_draw;

    if ((fb == 0) || (info == 0)) {
        return;
    }

    /* 只在该 buffer 上面板数值变化时重绘；数值未变直接返回（低风险局部重绘） */
    sig = s5_panel_sig(info, dma_state);
    for (n = 0u; n < 4u; n++) {
        if (s5_panel_cache[n].fb == fb) {
            slot = &s5_panel_cache[n];
            break;
        }
    }
    if (slot != 0) {
        if ((slot->inited != 0u) && (slot->sig == sig)) {
            return; /* 这组数值已经画在该 buffer 上，逐像素重绘没有意义 */
        }
        full_draw = (slot->inited == 0u) ? 1 : 0;
    } else {
        for (n = 0u; n < 4u; n++) {
            if (s5_panel_cache[n].fb == 0) {
                slot = &s5_panel_cache[n];
                break;
            }
        }
        if (slot == 0) {
            slot = &s5_panel_cache[0];
        }
        full_draw = 1; /* 该 buffer 第一次见：先全画 */
        slot->inited = 0u;
    }

    if (full_draw != 0) {
        /* 背景 + 左侧分隔线 + 标题条（静态部分，只画一次） */
        S5Draw_RectFill(fb, S5_PANEL_X, 0, S5_PANEL_W, S5_PANEL_H, S5_COLOR_PANEL_BG);
        S5Draw_RectFill(fb, S5_PANEL_X, 0, 2, S5_PANEL_H, S5_COLOR_PANEL_TITLE);
        S5Draw_RectFill(fb, S5_PANEL_X + 2, 0, S5_PANEL_W - 2, 26, S5_RGB(0x1A, 0x2A, 0x38));
        S5Draw_Text(fb, x, 5, "S5 P3B DISPLAY 720p60", S5_COLOR_PANEL_TITLE, S5_COLOR_TRANSPARENT);
    } else {
        /* 只清动态数值区（y=28..372），保留标题条/图例/页脚 */
        S5Draw_RectFill(fb, S5_PANEL_X + 2, 28, S5_PANEL_W - 2, 344, S5_COLOR_PANEL_BG);
    }

    slot->fb = fb;
    slot->sig = sig;
    slot->inited = 1u;

    age_over = (info->status & S5_ST_AGE_OVER) ? 1u : 0u;
    stale = (info->status & S5_ST_STALE) ? 1u : 0u;

    /* FRAME + 数据源（REAL/SIM/TEST） */
    p = s5_cat(line, "FRAME ");
    p = s5_u32(p, info->frame_id, 8);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
    y += pitch;

    p = s5_cat(line, "SRC ");
    p = s5_cat(p, s5_src_text(info->src_kind));
    if ((info->status & S5_ST_OVERRUN) != 0u) {
        p = s5_cat(p, " OVR");
    }
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TITLE, S5_COLOR_PANEL_BG);
    y += pitch;

    /* FPS 三口径 */
    p = s5_cat(line, "FPS C ");
    p = s5_dec1(p, info->fps_cap_x10);
    p = s5_cat(p, " I ");
    p = s5_dec1(p, info->fps_inf_x10);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
    y += pitch;

    p = s5_cat(line, "FPS D ");
    p = s5_dec1(p, info->fps_dis_x10);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
    y += pitch;

    /* FPS U：软件更新（渲染）速率，与显示刷新 FPS D 分开 */
    p = s5_cat(line, "FPS U ");
    p = s5_dec1(p, info->fps_upd_x10);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
    y += pitch;

    /* 显示延迟 / 结果年龄 */
    p = s5_cat(line, "LAT ");
    p = s5_u32(p, info->latency_ms, 0);
    p = s5_cat(p, " ms");
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
    y += pitch;

    p = s5_cat(line, "AGE ");
    p = s5_u32(p, info->age_ms, 0);
    p = s5_cat(p, " ms  ");
    if (stale != 0u) {
        p = s5_cat(p, "STALE");
    } else {
        p = s5_cat(p, age_over ? "OVER" : "OK");
    }
    s5_end(p);
    S5Draw_Text(fb, x, y, line,
                (stale != 0u) ? S5_COLOR_WARN : (age_over ? S5_COLOR_BAD : S5_COLOR_OK),
                S5_COLOR_PANEL_BG);
    y += pitch;

    p = s5_cat(line, "LIM ");
    p = s5_u32(p, S5_AGE_LIMIT_MS, 0);
    p = s5_cat(p, " ms (1f+16.7)");
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_DIM, S5_COLOR_PANEL_BG);
    y += pitch;

    /* VDMA 状态 */
    p = s5_cat(line, "VDMA ");
    p = s5_cat(p, s5_dma_state_text(dma_state));
    s5_end(p);
    S5Draw_Text(fb, x, y, line, s5_dma_state_color(dma_state), S5_COLOR_PANEL_BG);
    y += pitch;

    /* 状态位（十六进制，便于上板对照） */
    p = s5_cat(line, "ST ");
    p = s5_hex8(p, (uint32_t)info->status);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_DIM, S5_COLOR_PANEL_BG);
    y += pitch;

    /* 检测数 */
    p = s5_cat(line, "DET ");
    p = s5_u32(p, info->det_count, 2);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
    y += pitch + 4;

    /* 逐框明细（最多 5 条：类别 + 分数 + 摄像头坐标 + 尺寸） */
    for (i = 0; (i < info->det_count) && (i < 5u) && (i < S5_MAX_DET); i++) {
        const S5DetBox *b = &info->det[i];
        uint32_t color = (b->cls < S5_CLASS_NUM) ? s5_class_color[b->cls] : S5_COLOR_WHITE;

        p = s5_cat(line, (b->cls < S5_CLASS_NUM) ? s5_class_name[b->cls] : "CX");
        *p++ = ' ';
        if (b->score < 100u) {
            *p++ = ' ';
        }
        p = s5_u32(p, b->score, 0);
        p = s5_cat(p, " @");
        p = s5_u32(p, (uint32_t)(uint16_t)b->x, 0);
        *p++ = ',';
        p = s5_u32(p, (uint32_t)(uint16_t)b->y, 0);
        p = s5_cat(p, " ");
        p = s5_u32(p, (uint32_t)(uint16_t)b->w, 0);
        *p++ = 'x';
        p = s5_u32(p, (uint32_t)(uint16_t)b->h, 0);
        s5_end(p);
        S5Draw_Text(fb, x, y, line, color, S5_COLOR_PANEL_BG);
        y += pitch;
    }

    /* 类别图例 + 页脚：静态部分，只在该 buffer 首次绘制时画 */
    if (full_draw != 0) {
        y = 560;
        S5Draw_Text(fb, x, y, "CLASS", S5_COLOR_PANEL_DIM, S5_COLOR_TRANSPARENT);
        y += 20;
        for (i = 0; i < S5_CLASS_NUM; i++) {
            int lx = x + (int)(i % 3u) * 100;
            int ly = y + (int)(i / 3u) * 24;

            S5Draw_RectFill(fb, lx, ly + 2, 12, 12, s5_class_color[i]);
            S5Draw_Text(fb, lx + 16, ly, s5_class_name[i], S5_COLOR_PANEL_TEXT, S5_COLOR_TRANSPARENT);
        }
        S5Draw_Text(fb, x, 680, "960x720 + 320 panel", S5_COLOR_PANEL_DIM, S5_COLOR_TRANSPARENT);
        S5Draw_Text(fb, x, 698, "P3B-SW r06", S5_COLOR_PANEL_DIM, S5_COLOR_TRANSPARENT);
    }
}

/* ---------------- 帧装配 / 测试图 ---------------- */

/* raw 画面全 0（相机未启动）时的视频区回退图案：只在视频矩形里画棋盘，不覆盖信息栏/黑边 */
static void s5_draw_video_test_pattern(uint32_t *fb)
{
    int y;
    int x;

    for (y = S5_VID_Y; y < (S5_VID_Y + S5_VID_H); y++) {
        for (x = S5_VID_X; x < (S5_VID_X + S5_VID_W); x++) {
            int odd = (((x >> 5) + (y >> 5)) & 1) != 0;
            s5_put(fb, x, y, odd ? S5_RGB(0xE0, 0xE0, 0xE0) : S5_RGB(0x20, 0x20, 0x20));
        }
    }
    S5Draw_Text(fb, S5_VID_X + 16, S5_VID_Y + 16, "TEST PATTERN: RAW FRAME IS BLANK (ALL ZERO)",
                S5_COLOR_RED, S5_COLOR_BLACK);
}

/* 每个 buffer 上一次画进视频区的内容类型（用于“静态测试图案不重复绘制”的优化） */
typedef struct {
    const uint32_t *fb;
    uint32_t kind;
    uint32_t nbox;
    uint32_t inited;
} S5VideoCache;

static S5VideoCache s5_video_cache[4];

static S5VideoCache *s5_video_slot(const uint32_t *fb)
{
    uint32_t n;
    S5VideoCache *slot = 0;

    for (n = 0u; n < 4u; n++) {
        if (s5_video_cache[n].fb == fb) {
            return &s5_video_cache[n];
        }
        if ((s5_video_cache[n].inited == 0u) && (slot == 0)) {
            slot = &s5_video_cache[n];
        }
    }
    return (slot != 0) ? slot : &s5_video_cache[0];
}

void S5Display_RenderFrameSrc(uint32_t *fb, const uint32_t *cam, const S5FrameInfo *info,
                              uint32_t dma_state, uint32_t video_src)
{
    S5VideoCache *vs;
    int skip_video = 0;

    if ((fb == 0) || (info == 0)) {
        return;
    }

    /* 优化：测试图案是静态的，且本帧无框（无生产者场景）→ 该 buffer 上一帧已经是同一张，
     * 不必再清屏/重画 691k 像素。真实画面（CAM）每帧都重画。 */
    vs = s5_video_slot(fb);
    if ((video_src == S5_VIDEO_SRC_TEST) && (info->det_count == 0u) &&
        (vs->inited != 0u) && (vs->fb == fb) && (vs->kind == S5_VIDEO_SRC_TEST) &&
        (vs->nbox == 0u)) {
        skip_video = 1;
    }

    if (skip_video == 0) {
        /* 清屏把视频区外区域铺黑；视频区随后被摄像头画面或测试图案完全覆盖 */
        S5Draw_Clear(fb, S5_COLOR_BLACK);
        if (video_src == S5_VIDEO_SRC_TEST) {
            s5_draw_video_test_pattern(fb);
        } else {
            S5Draw_CameraLetterbox(fb, cam);
        }
        /* 检测框仍按结果块坐标画（测试图案回退时也显示框，便于确认 ABI 通路） */
        S5Draw_Boxes(fb, info->det, info->det_count);
        /* 整屏清过 → 标题条/图例/页脚也没了：本次必须整栏重绘 */
        s5_panel_invalidate(fb);
        vs->fb = fb;
        vs->kind = video_src;
        vs->nbox = info->det_count;
        vs->inited = 1u;
    }

    S5Draw_InfoPanel(fb, info, dma_state);
}

void S5Display_RenderFrame(uint32_t *fb, const uint32_t *cam,
                           const S5FrameInfo *info, uint32_t dma_state)
{
    S5Display_RenderFrameSrc(fb, cam, info, dma_state, S5_VIDEO_SRC_CAM);
}

void S5Display_TestPattern(uint32_t *fb, uint32_t mode)
{
    if (fb == 0) {
        return;
    }
    switch (mode) {
    case 0:
        S5Draw_Checker(fb, 80, S5_RGB(0x20, 0x20, 0x20), S5_RGB(0xE0, 0xE0, 0xE0));
        S5Draw_Text(fb, 40, 40, "TEST PATTERN 0: CHECKER 1280x720",
                    S5_COLOR_RED, S5_COLOR_BLACK);
        break;
    case 1:
        S5Draw_ColorBars(fb);
        break;
    default:
        S5Draw_GrayRamp(fb);
        break;
    }
}

/* ---------------- 结果行（runner 契约实现，纯函数） ----------------
 * 契约（写死，不得改字段名/单位，见 s5_display_app.h）：
 *   S5DISP RESULT={"pass":1,"fps_cap":60,"fps_inf":0,"fps_dis":60,"latency_ms":0,
 *                  "age_ms":47320,"vdma_err":0,"frames":180,"vcnt":180}
 * 失败时追加 "reason":"..."。整行必须在**同一行**输出（调用方只补一次 \r\n）。 */
/* ---------------- CRC32（G3 需要 box_crc / fb_crc） ---------------- */

static uint32_t s5_crc_tab[256];
static int s5_crc_tab_ready;

uint32_t S5Display_Crc32(const void *data, uint32_t bytes)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFu;
    uint32_t i;

    if ((data == 0) || (bytes == 0u)) {
        return 0u;
    }
    if (!s5_crc_tab_ready) {
        uint32_t n;
        int k;

        for (n = 0u; n < 256u; n++) {
            uint32_t c = n;

            for (k = 0; k < 8; k++) {
                c = ((c & 1u) != 0u) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
            }
            s5_crc_tab[n] = c;
        }
        s5_crc_tab_ready = 1;
    }
    for (i = 0u; i < bytes; i++) {
        crc = s5_crc_tab[(crc ^ p[i]) & 0xFFu] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFFu;
}

/* 绘制所用检测框（映射到画布 960×720 坐标）→ u16 序列 [x,y,w,h]×n → CRC32。
 * 与 S5Draw_Boxes 的映射公式一致（含 S5_VID_X/Y 偏移，L0 下为 0）。 */
/* 绘制所用检测框 → 映射到画布 960×720 坐标（u16 [x,y,w,h]，**边界裁剪后**）。
 * 与 S5Draw_Boxes 同一映射（含 S5_VID_X/Y 偏移，L0 为 0）；宽/高 ≤0 的框跳过（不画、不入 CRC）。
 * 返回实际写入的框数；out 需 >= max_boxes*4 个 u16。 */
uint32_t S5Display_BoxesMapped(const S5DetBox *det, uint32_t n, uint16_t *out, uint32_t max_boxes)
{
    uint32_t count = (n > S5_MAX_DET) ? S5_MAX_DET : n;
    uint32_t i;
    uint32_t k = 0u;

    if ((det == 0) || (out == 0)) {
        return 0u;
    }
    for (i = 0u; (i < count) && (k < max_boxes); i++) {
        int x = S5_VID_X + ((int)det[i].x * S5_SCALE_NUM) / S5_SCALE_DEN;
        int y = S5_VID_Y + ((int)det[i].y * S5_SCALE_NUM) / S5_SCALE_DEN;
        int w = ((int)det[i].w * S5_SCALE_NUM) / S5_SCALE_DEN;
        int h = ((int)det[i].h * S5_SCALE_NUM) / S5_SCALE_DEN;

        /* 边界裁剪到显示区 [0,959]×[0,719] */
        if (x < 0) {
            w += x;
            x = 0;
        }
        if (y < 0) {
            h += y;
            y = 0;
        }
        if (x >= S5_CANVAS_W) {
            x = S5_CANVAS_W - 1;
            w = 0;
        }
        if (y >= S5_CANVAS_H) {
            y = S5_CANVAS_H - 1;
            h = 0;
        }
        if ((x + w) > S5_CANVAS_W) {
            w = S5_CANVAS_W - x;
        }
        if ((y + h) > S5_CANVAS_H) {
            h = S5_CANVAS_H - y;
        }
        if ((w <= 0) || (h <= 0)) {
            continue; /* 与绘制逻辑一致：宽高非正的框不画，也不进 CRC */
        }
        out[k * 4u + 0u] = (uint16_t)x;
        out[k * 4u + 1u] = (uint16_t)y;
        out[k * 4u + 2u] = (uint16_t)w;
        out[k * 4u + 3u] = (uint16_t)h;
        k++;
    }
    return k;
}

uint32_t S5Display_BoxesCrc(const S5DetBox *det, uint32_t n)
{
    uint16_t items[S5_MAX_DET * 4u];
    uint32_t k;

    k = S5Display_BoxesMapped(det, n, items, S5_MAX_DET);
    return S5Display_Crc32(items, k * 8u);
}

/* 信息栏局部重绘支持（定义必须早于 S5Draw_InfoPanel，见下）：类型/缓存/签名函数已提前 */

uint32_t S5Display_FormatResult(const S5RunStats *st, char *buf, uint32_t cap)
{
    char *p = buf;

    if ((st == 0) || (buf == 0) || (cap < 300u)) {
        return 0u; /* 契约要求单行完整，容量不足宁可不打印也不截断出半个 JSON */
    }

    p = s5_cat(p, S5_RESULT_PREFIX);
    p = s5_cat(p, "{\"pass\":");
    p = s5_u32(p, (st->pass != 0u) ? 1u : 0u, 0);

    /* fps 单位是整数 fps（0..60），不是 ×10；越界按 60 收敛，避免判据解析出非法值 */
#define S5_FPS_CLAMP(v) (((v) > 60u) ? 60u : (v))
    p = s5_cat(p, ",\"fps_cap\":");
    p = s5_u32(p, S5_FPS_CLAMP(st->fps_cap), 0);
    p = s5_cat(p, ",\"fps_inf\":");
    p = s5_u32(p, S5_FPS_CLAMP(st->fps_inf), 0);
    p = s5_cat(p, ",\"fps_dis\":");
    p = s5_u32(p, S5_FPS_CLAMP(st->fps_dis), 0);
    /* fps_upd：软件更新（渲染）速率，不参与 0..60 显示刷新 clamp（如实报告，可能 >60） */
    p = s5_cat(p, ",\"fps_upd\":");
    p = s5_u32(p, st->fps_upd, 0);
#undef S5_FPS_CLAMP

    p = s5_cat(p, ",\"latency_ms\":");
    p = s5_u32(p, st->latency_ms, 0);
    p = s5_cat(p, ",\"age_ms\":");
    p = s5_u32(p, st->age_ms, 0);
    p = s5_cat(p, ",\"vdma_err\":");
    p = s5_u32(p, st->vdma_err, 0);
    p = s5_cat(p, ",\"frames\":");
    p = s5_u32(p, st->frames, 0);
    p = s5_cat(p, ",\"vcnt\":");
    p = s5_u32(p, st->vcnt, 0);
    /* G3：检测框 CRC（映射后坐标）与 framebuffer CRC（十进制 u32，保持 JSON 合法） */
    p = s5_cat(p, ",\"box_crc\":");
    p = s5_u32(p, st->box_crc, 0);
    p = s5_cat(p, ",\"fb_crc\":");
    p = s5_u32(p, st->fb_crc, 0);

    /* src 是 ABI 回退判据（lead 2026-10-30 追加）：real / sim / test */
    p = s5_cat(p, ",\"src\":\"");
    p = s5_cat(p, (st->src != 0) ? st->src : "none");
    *p++ = '"';

    /* reason：只要非 NULL 就输出（回退到 test 时 pass 仍可为 1，但原因要可见） */
    if (st->reason != 0) {
        p = s5_cat(p, ",\"reason\":\"");
        p = s5_cat(p, st->reason);
        *p++ = '"';
    }
    *p++ = '}';
    *p = '\0';
    return (uint32_t)(p - buf);
}

/* 帧完整性抽点自检（结果行 pass 的第三个条件：至少一帧完整显示 + 信息栏刷新成功）。
 * 视频区：摄像头梯度不应全黑，抽样要求足够多的非黑点；
 * 信息栏：**标题条**（y=0..25）是实心填色带，正常渲染时该带内几乎全部 != 面板底色，
 *         用它判断“信息栏确实刷新过”，比随机抽文字像素稳健（文字覆盖率低，会误判）。 */
int S5Display_CheckFrame(const uint32_t *fb)
{
    int hits_video = 0;
    int hits_panel = 0;
    int y;
    int x;

    if (fb == 0) {
        return 0;
    }
    for (y = 40; y < S5_VID_H; y += 90) {
        for (x = 20; x < S5_VID_W - 20; x += 120) {
            if (fb[(uint32_t)y * (uint32_t)S5_CANVAS_W + (uint32_t)x] != S5_COLOR_BLACK) {
                hits_video++;
            }
        }
    }
    for (y = 6; y <= 20; y += 4) {
        for (x = S5_PANEL_X + 10; x < S5_PANEL_X + 200; x += 10) {
            if (fb[(uint32_t)y * (uint32_t)S5_CANVAS_W + (uint32_t)x] != S5_COLOR_PANEL_BG) {
                hits_panel++;
            }
        }
    }
    return ((hits_video >= 8) && (hits_panel >= 20)) ? 1 : 0;
}

/* ---------------- 模拟数据源 ----------------
 * 接真实推理结果时**只替换本函数**：
 *   info->frame_id      ← 采集帧号（与 PL 侧 frame counter 同一来源）
 *   info->fps_*_x10     ← 三个口径各自的滑动窗口计数（见报告 §5）
 *   info->latency_ms    ← S5Ticks_ToMs(t_display_start - t_infer_done)
 *   info->age_ms        ← S5Ticks_ToMs(t_display_start - t_capture_end)
 *   info->det[]         ← 解码/NMS 输出，坐标保持**摄像头 640×480 原始坐标**
 *   info->status        ← S5_ST_* 位或
 * 时间戳 t_capture_end / t_infer_done / t_display_start 都由 0xF8F00200 全局定时器取，
 * 分辨率 ~3 ns，换算见 s5_timebase.h。 */

static uint32_t s5_rand(void)
{
    static uint32_t s = 0x2545F491u; /* 固定种子：离线自测可复现 */

    s ^= s << 13;
    s ^= s >> 17;
    s ^= s << 5;
    return s;
}

void S5Sim_NextFrame(S5FrameInfo *info)
{
    static uint32_t frame;
    uint64_t now;
    uint32_t age_us;
    uint32_t lat_us;
    uint32_t i;
    uint32_t n;

    if (info == 0) {
        return;
    }
    memset(info, 0, sizeof(*info));
    frame++;

    now = S5Ticks_Now();

    /* 模拟流水线时间戳：采集结束在 30 ms 前（≈2 帧前），推理完成在 17 ms 前（1 帧前）。
     * 每 47 帧注入一次 41 ms 超龄，验证 AGE OVER 告警路径。 */
    age_us = 30000u + (s5_rand() % 4000u);
    lat_us = 17000u + (s5_rand() % 2500u);
    if ((frame % 47u) == 0u) {
        age_us = 41000u;
    }

    info->frame_id = frame;
    info->age_ms = (uint16_t)S5Ticks_ToMs(S5Ticks_FromUs(age_us));
    info->latency_ms = (uint16_t)S5Ticks_ToMs(S5Ticks_FromUs(lat_us));
    (void)now; /* 真实实现里用于 stamp：t_display_start = now */

    /* 三口径 FPS：模拟源用模型值 + 抖动；真实实现改用滑动窗口计数 */
    info->fps_cap_x10 = (uint16_t)(300u - (s5_rand() % 3u)); /* 29.7~30.0 */
    info->fps_inf_x10 = (uint16_t)(280u - (s5_rand() % 5u)); /* 27.5~28.0 */
    info->fps_dis_x10 = (uint16_t)(600u - (s5_rand() % 2u)); /* 59.8~60.0 */

    info->status = S5_ST_CAM_OK | S5_ST_INF_OK;
    if (info->age_ms > S5_AGE_LIMIT_MS) {
        info->status |= S5_ST_AGE_OVER;
    }
    info->src_kind = S5_SRC_SIM; /* 模拟源标记：面板 SRC= 行与 RESULT 的 src 用 */

    /* 1~3 个缓慢移动的框（保持在 640×480 内） */
    n = 1u + (frame % 3u);
    info->det_count = (uint8_t)n;
    for (i = 0; i < n; i++) {
        S5DetBox *b = &info->det[i];
        uint32_t cx = 40u + ((frame * (3u + i * 2u)) % 460u);
        uint32_t cy = 30u + ((frame * (2u + i)) % 340u);

        b->x = (int16_t)cx;
        b->y = (int16_t)cy;
        b->w = (int16_t)(80u + i * 30u);
        b->h = (int16_t)(70u + i * 20u);
        b->cls = (uint8_t)((frame + i) % S5_CLASS_NUM);
        b->score = (uint8_t)(60u + (s5_rand() % 40u));
    }
}

/* 合成摄像头画面：斜向渐变 + 三个移动色块 + 中心十字（便于目测缩放/黑边/框位置） */
static void s5_cam_rect(uint32_t *cam, int x0, int y0, int w, int h, uint32_t color)
{
    int y;

    for (y = y0; y < (y0 + h); y++) {
        int x;

        if ((y < 0) || (y >= S5_CAM_H)) {
            continue;
        }
        for (x = x0; x < (x0 + w); x++) {
            if ((x >= 0) && (x < S5_CAM_W)) {
                cam[(uint32_t)y * (uint32_t)S5_CAM_W + (uint32_t)x] = color;
            }
        }
    }
}

void S5Sim_CameraFrame(uint32_t *cam, uint32_t frame_id)
{
    int y;
    int x;

    if (cam == 0) {
        return;
    }
    for (y = 0; y < S5_CAM_H; y++) {
        for (x = 0; x < S5_CAM_W; x++) {
            uint32_t r = (uint32_t)((x * 200) / (S5_CAM_W - 1)) + 20u;
            uint32_t g = (uint32_t)((y * 200) / (S5_CAM_H - 1)) + 20u;
            uint32_t b = 64u + ((uint32_t)((x + y) >> 2) & 0x3Fu);
            cam[(uint32_t)y * (uint32_t)S5_CAM_W + (uint32_t)x] = S5_RGB(r, g, b);
        }
    }

    /* 移动色块（帧号驱动，离线渲染固定一帧也稳定） */
    s5_cam_rect(cam, (int)((frame_id * 7u) % 480u), 80, 120, 90, S5_RGB(0xFF, 0x40, 0x40));
    s5_cam_rect(cam, 60, (int)((frame_id * 5u) % 340u), 90, 110, S5_RGB(0x40, 0xFF, 0x40));
    s5_cam_rect(cam, 420, (int)((frame_id * 3u) % 300u) + 100, 140, 80, S5_RGB(0x40, 0x80, 0xFF));

    /* 中心十字：验证 1.5× 缩放后仍是直线且居中 */
    s5_cam_rect(cam, 316, 0, 8, S5_CAM_H, S5_RGB(0xFF, 0xFF, 0xFF));
    s5_cam_rect(cam, 0, 236, S5_CAM_W, 8, S5_RGB(0xFF, 0xFF, 0xFF));
}

/* ============================================================================
 * B) 裸机应用（ARM 侧）：帧缓冲绝对地址 + VDMA 启停 + 双缓冲乒乓
 * ==========================================================================*/
#ifndef S5_HOST_TEST

#include "vdma_ctrl.h"
#include "vtc_ctrl.h"
#include "xil_cache.h"
#include "xil_printf.h"
#include "xparameters.h"

#include "s5_timebase.h"
#include "s5_real_source.h"  /* 真实数据源：结果块解析 / raw 画面转换 / 回退判据 */
#include "s5_result_abi.h"   /* 结果块 ABI（0x20800000）+ raw frame（0x12000000） */

/* 每帧把画布从 D-cache 刷到 DDR，否则 VDMA 可能读到旧像素。
 * 若 bring-up 时确认 D-cache 关闭，可把该宏改 0 省掉 ~115k 次 cache 维护。 */
#define S5_DCACHE_FLUSH 1

/* VDMA 周期的帧存个数：与 BD 一致，**2** 个（lead 2026-10-30 已把 c_num_fstores 改为 2）。
 * 双缓冲 A/B，只填 0x5C/0x60 两个地址寄存器，不写第 3 个。 */
#define S5_VDMA_FS_PROG 2u

/* 结果行 fps_inf 口径：模拟源分支下按契约打印 0；真实源分支由时间戳窗口计算，不受此宏影响。 */
#define S5_RESULT_FPS_INF_FROM_SIM 0

/* 真实数据源开关（lead 2026-10-30）：默认开；结果块不可用时自动回退模拟源。
 * 置 0 可强制纯模拟（离线版式自检/无生产者联调时用）。 */
#ifndef S5_SOURCE_REAL
#define S5_SOURCE_REAL 1
#endif

/* 空白画面复检周期（帧）：raw 全 0 时不每帧扫 921,600 B，每 N 帧复检一次等相机启动 */
#define S5_BLANK_RECHECK_FRAMES 15u

/* DMA 写、CPU 读的区域：读之前必须 invalidate，否则可能读到 D-cache 里的旧行。
 * 若 bring-up 确认 D-cache 关闭，该操作是空转（可把 S5_DCACHE_FLUSH 置 0 省掉）。 */
static void s5_invalidate(const void *addr, uint32_t bytes)
{
#if S5_DCACHE_FLUSH
    Xil_DCacheInvalidateRange((UINTPTR)addr, (INTPTR)bytes);
#else
    (void)addr;
    (void)bytes;
#endif
}

static uint32_t s5_cam[S5_CAM_W * S5_CAM_H]; /* 640×480×4 B = 1.2 MB，放 .bss（DDR） */

static void s5_fb_flush(uint32_t *fb)
{
#if S5_DCACHE_FLUSH
    Xil_DCacheFlushRange((UINTPTR)fb, S5_FB_BYTES);
#else
    (void)fb;
#endif
}

int main(void)
{
    static S5Vdma dma;
    static S5Vtc vtc;
    S5VtcTiming timing;
    S5FrameInfo info;
    uint32_t *fb[2];
    uint32_t fb_addr[S5_VDMA_FS_PROG];
    uint32_t back = 0;
    uint32_t dma_state = S5_DMA_OFF;
    uint32_t major = 0;
    uint32_t minor = 0;
    uint32_t rev = 0;
    uint32_t i;
    int dma_init_ok = 0;
    char line[96];
    int rc;
    /* 真实数据源状态 */
    static S5RealBlock rblk;
    S5FpsWin win_cap;
    S5FpsWin win_inf;
    S5FpsWin win_upd;
    uint32_t src_kind = S5_SRC_SIM;
    uint32_t last_src = S5_SRC_SIM;
    uint32_t last_frame_id = 0xFFFFFFFFu; /* 真实源：上一份结果帧号（fps 窗口去重） */
    uint32_t blank_state = 0u; /* 0=未判定/有内容，1=raw 全 0 */
    int parse_rc = S5_PARSE_ERR_MAGIC;
    const char *frame_reason = 0;
    const char *last_reason = 0;
    /* 显示刷新率（fps_dis）：从 VDMA 读帧存切换周期测出来的常数；测不到则 0（不虚填） */
    uint32_t fps_dis_const = 0u;
    uint64_t disp_period_ticks = 0u;
    uint32_t fps_upd_win_x10 = 0u;
    /* 最后一帧的框（box_crc 用） */
    static S5DetBox last_det[S5_MAX_DET];
    uint32_t last_det_count = 0u;

    fb[0] = (uint32_t *)S5_FB_A_BASE;
    fb[1] = (uint32_t *)S5_FB_B_BASE;
    fb_addr[0] = S5_FB_A_BASE;
    fb_addr[1] = S5_FB_B_BASE;

    xil_printf("\r\n=== S5 P3B display app (P3b-sw, offline build) ===\r\n");
    xil_printf("canvas %dx%d, FB A=%x B=%x, %d B/frame, %d frame stores\r\n",
               S5_CANVAS_W, S5_CANVAS_H, S5_FB_A_BASE, S5_FB_B_BASE, S5_FB_BYTES,
               (int)S5_VDMA_FS_PROG);
    xil_printf("timer: GT %d Hz (S5_GT_HZ, 显式常量规避 xtimer 宏括号坑)\r\n",
               (int)(S5_GT_HZ / 1000000u));
    xil_printf("source: %s (result block @%x magic=%x, raw @%x %d B BGR888)\r\n",
               (S5_SOURCE_REAL != 0) ? "REAL with SIM fallback" : "SIM only",
               S5_RESULT_BASE, S5_RESULT_MAGIC, S5_RAW_FRAME_BASE, S5_RAW_FRAME_BYTES);
    S5Fps_Reset(&win_cap);
    S5Fps_Reset(&win_inf);
    S5Fps_Reset(&win_upd);
    xil_printf("run mode: %s, frames_cap=%d, time_cap_ms=%d\r\n",
               (S5_LONG_RUN != 0) ? "LONG(30min)" : "bounded",
               (int)((S5_LONG_RUN != 0) ? 0 : (int)S5_RUN_FRAMES),
               (int)((S5_LONG_RUN != 0) ? (int)S5_RUN_MAX_MS_LONG : (int)S5_RUN_MAX_MS));

    /* 1) VTC 生成器 720p60：先出时序，再让 VDMA 有流可推。
     *    写后回读校验，失败显式打印（不静默）。 */
    S5Vtc_Default720p60(&timing);
    rc = S5Vtc_Init(&vtc, &timing, 10000u);
    xil_printf("VTC: version=%x\r\n", (unsigned)vtc.version);
    for (i = 0; i < vtc.n_chk; i++) {
        S5Vtc_FormatCheck(&vtc, i, line, (uint32_t)sizeof(line));
        xil_printf("%s\r\n", line);
    }
    S5Vtc_FormatCheck(&vtc, vtc.n_chk, line, (uint32_t)sizeof(line)); /* CTL */
    xil_printf("%s\r\n", line);
    S5Vtc_FormatSummary(&vtc, line, (uint32_t)sizeof(line));
    xil_printf("%s\r\n", line);
    S5Vtc_FormatTiming(&vtc, line, (uint32_t)sizeof(line));
    xil_printf("%s\r\n", line);
    if (rc == 0) {
        xil_printf("VTC: init OK (720p60 generator enabled: SW|GE)\r\n");
    } else {
        xil_printf("VTC: init FAILED rc=%d (%s)\r\n", rc,
                   (rc == -1) ? "reset timeout" :
                   (rc == -2) ? "AXI-Lite/geometry invalid" : "readback mismatch");
        /* 不静默：继续画帧以便 JTAG 看 DDR，但状态位置错、面板 VDMA 转 ERR */
    }

    /* 2) 先上两张测试图：证明“DDR 写 → VDMA 读 → 屏幕”整条通路 */
    S5Display_TestPattern(fb[0], 0); /* 棋盘 */
    s5_fb_flush(fb[0]);
    S5Display_TestPattern(fb[1], 1); /* 彩条 */
    s5_fb_flush(fb[1]);

    /* 3) 启动 VDMA MM2S（非 SG，循环模式，2 帧存双缓冲） */
    rc = S5Vdma_Init(&dma, fb_addr, S5_VDMA_FS_PROG,
                     (uint32_t)S5_CANVAS_W * 4u, (uint32_t)S5_CANVAS_H);
    if (rc == 0) {
        dma_state = S5_DMA_RUN;
        S5Vdma_DecodeVersion(dma.version, &major, &minor, &rev);
        xil_printf("VDMA: init OK, version=%x (major %d minor %d rev %d)\r\n",
                   dma.version, (int)major, (int)minor, (int)rev);
        xil_printf("VDMA: buffers A=%x B=%x (num_fstores=%d), FRMSTORE readback=%d (expect 2)\r\n",
                   (unsigned)fb_addr[0], (unsigned)fb_addr[1], (int)S5_VDMA_FS_PROG,
                   (int)dma.fs_hw_readback);
        if ((dma.fs_hw_readback != 0u) && (dma.fs_hw_readback != S5_VDMA_FS_PROG)) {
            xil_printf("VDMA: WARN FRMSTORE readback != 2（检查 BD c_num_fstores）\r\n");
        }
    } else {
        dma_state = S5_DMA_ERR;
        xil_printf("VDMA: init FAILED rc=%d（继续画帧，便于用 JTAG 看 DDR 内容）\r\n", rc);
    }
    dma_init_ok = (dma_state == S5_DMA_RUN) ? 1 : 0;
    /* r05：不再有硬件帧计数（SR 无该字段），vcnt 由主循环软件观测 read-store 切换 */

    /* 3b) **fps_dis = 显示刷新率**：直接测 VDMA 读帧存的切换周期（= 每输出一帧的时间）。
     *     不是软件循环速率；软件渲染速率另算 fps_upd（frames/elapsed）。
     *     测不到（READSTR 不动/超时）就保持 0，不虚填 60。 */
    if (dma_init_ok != 0) {
        if (S5Vdma_MeasureReadPeriod(&dma, 6u, 200000u, &disp_period_ticks) == 0) {
            fps_dis_const = (uint32_t)((S5_GT_HZ + (disp_period_ticks / 2u)) / disp_period_ticks);
            xil_printf("VDMA: read period = %d ticks (%d us) -> fps_dis=%d (display refresh)\r\n",
                       (int)disp_period_ticks,
                       (int)((disp_period_ticks * 1000000u) / S5_GT_HZ),
                       (int)fps_dis_const);
        } else {
            xil_printf("VDMA: WARN 读帧存切换周期测不到（READSTR 不动）→ fps_dis=0（不虚填）\r\n");
        }
    }

    /* 4) 有界/长跑主循环：默认跑满 S5_RUN_FRAMES 帧或达到 S5_RUN_MAX_MS，先到者停机；
     *    S5_LONG_RUN=1 时帧数上限取消，只按 1800 s 时间上限退出（G3/S6-F 30 min）。
     *    长跑时每 60 s 打一行 S5DISP tick，便于判断是否死锁。 */
    {
        uint64_t t_start = S5Ticks_Now();
        uint32_t frames = 0;
        uint32_t vdma_err = 0;
        uint32_t vcnt_sw = 0;
        uint32_t frames_wo_result = 0; /* 结果块不可用的帧数（给无结果帧一个递增的帧号） */
        uint32_t last_store = 0xFFFFFFFFu;
        uint32_t *last_fb = fb[0];
        uint32_t sr;
        S5RunStats st;
        char res[320];
        const uint32_t run_frames = (S5_LONG_RUN != 0) ? 0xFFFFFFFFu : (uint32_t)S5_RUN_FRAMES;
        const uint64_t run_ms = (S5_LONG_RUN != 0) ? (uint64_t)S5_RUN_MAX_MS_LONG
                                                   : (uint64_t)S5_RUN_MAX_MS;
        uint64_t last_tick_ms = 0u;

        while ((frames < run_frames) &&
               (S5Ticks_ToMs(S5Ticks_Now() - t_start) < run_ms)) {
            {
                /* 长跑心跳：每 60 s 一行（与 RESULT/进度行分开） */
                uint64_t el = S5Ticks_ToMs(S5Ticks_Now() - t_start);

                if ((S5_LONG_RUN != 0) && ((el - last_tick_ms) >= (uint64_t)S5_TICK_MS)) {
                    last_tick_ms = el;
                    xil_printf("S5DISP tick t=%d frames=%d vcnt=%d err=%d\r\n",
                               (int)(el / 1000u), (int)frames, (int)vcnt_sw, (int)vdma_err);
                }
            }
            /* 4.0 取本帧数据（r05 回退优先级，lead 冻结）：
             *   ①结果块有效            → src="real"（有框；raw 全 0 时画面用测试图案）
             *   ②结果块无效 + raw 有效  → src="real_nobox"（真实画面、无框，pass 可为 1）
             *   ③结果块无效 + raw 全 0  → src="test"（测试图案，pass=1：无生产者时的合法上屏自检）
             *   ④仅当 S5_SOURCE_REAL=0（强制模拟）或测试图案画不出来 → src="sim"（pass=0） */
#if S5_SOURCE_REAL
            s5_invalidate((const void *)S5_RESULT_BASE, S5_RESULT_BLOCK_BYTES);
            parse_rc = S5Real_Parse((const uint32_t *)S5_RESULT_BASE, &rblk);
            {
                uint64_t now_ticks = S5Ticks_Now();
                uint32_t have_result = (parse_rc == S5_PARSE_OK) ? 1u : 0u;

                /* raw 空白判定（与结果块是否有效无关）：全 0 时每 15 帧复检一次，等相机启动 */
                if ((blank_state == 0u) || ((frames % S5_BLANK_RECHECK_FRAMES) == 0u)) {
                    s5_invalidate((const void *)S5_RAW_FRAME_BASE, S5_RAW_FRAME_BYTES);
                    blank_state = (uint32_t)S5Real_IsBlank((const uint8_t *)S5_RAW_FRAME_BASE,
                                                            S5_RAW_FRAME_BYTES);
                }

                if (have_result != 0u) {
                    if (blank_state != 0u) {
                        src_kind = S5_SRC_TEST; /* 有结果但没画面：测试图案 + 仍画框 */
                        frame_reason = "raw_frame_blank";
                    } else {
                        S5Real_BgrToCanvas((const uint8_t *)S5_RAW_FRAME_BASE, s5_cam,
                                           S5_RAW_FRAME_W * S5_RAW_FRAME_H);
                        src_kind = S5_SRC_REAL;
                        frame_reason = 0;
                    }
                    S5Real_ToFrameInfo(&rblk, now_ticks, &info);
                    info.src_kind = src_kind;

                    /* FPS：cap/inf 只在**新结果**（frame_id 变化）时计入窗口；
                     * dis 是显示刷新常数（硬件测量）；upd 是软件更新速率窗口。 */
                    if (rblk.frame_id != last_frame_id) {
                        S5Fps_Add(&win_cap, rblk.cap_ticks);
                        S5Fps_Add(&win_inf, rblk.inf_ticks);
                        last_frame_id = rblk.frame_id;
                    }
                    S5Fps_Add(&win_upd, now_ticks);

                    /* 面板实时 FPS：窗口 ×10 回填；FPS D 用测量到的显示刷新常数 */
                    {
                        uint32_t fc_x10 = S5Fps_GetX10(&win_cap);
                        uint32_t fi_x10 = S5Fps_GetX10(&win_inf);

                        fps_upd_win_x10 = S5Fps_GetX10(&win_upd);
                        info.fps_cap_x10 = (uint16_t)((fc_x10 > 0xFFFFu) ? 0xFFFFu : fc_x10);
                        info.fps_inf_x10 = (uint16_t)((fi_x10 > 0xFFFFu) ? 0xFFFFu : fi_x10);
                        info.fps_dis_x10 = (uint16_t)(fps_dis_const * 10u);
                        info.fps_upd_x10 = (uint16_t)((fps_upd_win_x10 > 0xFFFFu)
                                                          ? 0xFFFFu : fps_upd_win_x10);
                    }
                } else {
                    /* 结果块无效：没有框、没有推理时间戳；只保留画面与速率 */
                    S5Fps_Add(&win_upd, now_ticks);
                    fps_upd_win_x10 = S5Fps_GetX10(&win_upd);
                    memset(&info, 0, sizeof(info));
                    frames_wo_result++;
                    info.frame_id = frames_wo_result;
                    info.status = S5_ST_CAM_OK; /* 有画面，无推理结果：不置 INF_OK */
                    info.age_ms = 0u;           /* 时间戳未知 → 0（不是 now−0） */
                    info.latency_ms = 0u;
                    info.fps_dis_x10 = (uint16_t)(fps_dis_const * 10u);
                    info.fps_upd_x10 = (uint16_t)((fps_upd_win_x10 > 0xFFFFu)
                                                      ? 0xFFFFu : fps_upd_win_x10);

                    if (blank_state == 0u) {
                        S5Real_BgrToCanvas((const uint8_t *)S5_RAW_FRAME_BASE, s5_cam,
                                           S5_RAW_FRAME_W * S5_RAW_FRAME_H);
                        src_kind = S5_SRC_REAL_NOBOX;
                    } else {
                        src_kind = S5_SRC_TEST; /* 无结果 + 无画面：测试图案自检（合法通过态） */
                    }
                    frame_reason = S5Src_Reason(parse_rc); /* 根因：结果块为什么不可用 */
                    info.src_kind = src_kind;
                }
            }
#else
            src_kind = S5_SRC_SIM;
            frame_reason = "real_source_disabled";
            S5Sim_NextFrame(&info);
            S5Sim_CameraFrame(s5_cam, info.frame_id);
            {
                uint64_t now_ticks = S5Ticks_Now();

                S5Fps_Add(&win_upd, now_ticks);
                fps_upd_win_x10 = S5Fps_GetX10(&win_upd);
                info.fps_dis_x10 = (uint16_t)(fps_dis_const * 10u);
                info.fps_upd_x10 = (uint16_t)((fps_upd_win_x10 > 0xFFFFu)
                                                  ? 0xFFFFu : fps_upd_win_x10);
            }
#endif
            last_src = src_kind;
            last_reason = frame_reason;

            /* 记录最后一帧的框，供 box_crc 使用（映射后坐标在 S5Display_BoxesCrc 里做） */
            last_det_count = (info.det_count > S5_MAX_DET) ? S5_MAX_DET : info.det_count;
            for (i = 0u; i < last_det_count; i++) {
                last_det[i] = info.det[i];
            }

            /* 4.1 写前等安全窗口（判据用 != OFF：出错后 dma_state 转 ERR 但可能仍在搬数） */
            if (dma_state != S5_DMA_OFF) {
                if (S5Vdma_WaitNotReading(&dma, (uint32_t)(uintptr_t)fb[back], 100000u) != 0) {
                    info.status |= S5_ST_TEAR;
                }
                sr = S5Vdma_Status(&dma);
                if ((sr & S5_VDMA_SR_ERR_ALL) != 0u) {
                    info.status |= S5_ST_DMA_ERR;
                    dma_state = S5_DMA_ERR;
                    vdma_err++; /* 结果行 vdma_err：SR 错误位累计 */
                }
                /* vcnt：软件观测 PARKPTR.READSTR 的变化次数（每切换一次读帧存 ≈ 消耗一帧）。
                 * r05 结论：SR 里没有硬件帧计数字段（CR[23:16] 是调试用帧计数，需 genlock 语义），
                 * 因此不再读 SR[23:16]，见 vdma_ctrl.h 文件头说明。 */
                {
                    uint32_t cs = S5Vdma_CurrentReadStore(&dma);
                    if (cs != last_store) {
                        vcnt_sw++;
                        last_store = cs;
                    }
                }
            }

            /* 4.2 装配一帧（测试图案回退时 video_src=TEST，检测框仍来自结果块） */
            S5Display_RenderFrameSrc(fb[back], s5_cam, &info, dma_state,
                                     (src_kind == S5_SRC_TEST) ? S5_VIDEO_SRC_TEST : S5_VIDEO_SRC_CAM);
            s5_fb_flush(fb[back]);
            last_fb = fb[back];

            /* 4.3 乒乓 */
            back ^= 1u;
            frames++;

            /* 4.4 进度行（与 RESULT 行分开，绝不拼在同一行；含 src/nbox 便于现场判断数据源） */
            if ((frames % 60u) == 0u) {
                xil_printf("S5DISP frame=%d lat=%d age=%d st=%x sr=%x src=%s nbox=%d\r\n",
                           (int)frames, (int)info.latency_ms, (int)info.age_ms,
                           (unsigned)info.status, (unsigned)S5Vdma_Status(&dma),
                           S5Src_Name(src_kind), (int)info.det_count);
            }
        }

        /* 5) 停机：停止 VDMA 读取，便于采集器收尾后安全断电/复位 */
        if (dma_state != S5_DMA_OFF) {
            (void)S5Vdma_Stop(&dma);
        }

        /* 6) 结果行：pass = VDMA 无错 + ≥1 帧完整显示 + 信息栏刷新成功 */
        st.pass = 1u;
        st.reason = 0;
        st.src = S5Src_Name(last_src);
        st.frames = frames;
        st.vdma_err = vdma_err;
        st.vcnt = vcnt_sw; /* r05：只用软件观测（硬件帧计数不存在，见 vdma_ctrl.h） */

        /* FPS 语义（r06，lead 冻结）：
         *   fps_cap/fps_inf = 采集/推理时间戳窗口；
         *   fps_dis = **显示刷新率**（VDMA 读帧存切换周期测得的常数，≈60；测不到=0，不虚填）；
         *   fps_upd = **软件更新（渲染）速率** = frames / elapsed，如实报告（≈35）。 */
        {
            uint32_t f_cap = S5Fps_Get(&win_cap);
            uint32_t f_inf = S5Fps_Get(&win_inf);
            uint64_t elapsed_ms = S5Ticks_ToMs(S5Ticks_Now() - t_start);

            st.fps_cap = (f_cap != 0u) ? f_cap : (uint32_t)(info.fps_cap_x10 / 10u);
            st.fps_inf = (f_inf != 0u) ? f_inf : ((S5_RESULT_FPS_INF_FROM_SIM != 0)
                                                      ? (uint32_t)(info.fps_inf_x10 / 10u)
                                                      : 0u);
            st.fps_dis = fps_dis_const;
            st.fps_upd = (elapsed_ms > 0u)
                             ? (uint32_t)(((uint64_t)frames * 1000u) / elapsed_ms)
                             : 0u;
        }
        st.latency_ms = (uint32_t)info.latency_ms;
        st.age_ms = (uint32_t)info.age_ms;
        /* G3：box_crc = 绘制所用框（映射后坐标）；fb_crc = 显示用 framebuffer（0x20000000 那帧）。
         * 两者都在**最后一帧写完后**算一次；fb_crc 先 invalidate，确保读的是 DDR 里的最新像素。 */
        st.box_crc = S5Display_BoxesCrc(last_det, last_det_count);
        s5_invalidate((const void *)S5_FB_A_BASE, S5_FB_BYTES);
        st.fb_crc = S5Display_Crc32((const void *)S5_FB_A_BASE, S5_FB_BYTES);

        /* pass = 显示链路健康 + 真实数据源可用；回退到 test 仍算通过（显示可用），原因保留 */
        if (dma_init_ok == 0) {
            st.pass = 0u;
            st.reason = "vdma_init_failed";
        } else if (vdma_err != 0u) {
            st.pass = 0u;
            st.reason = "vdma_error";
        } else if (frames == 0u) {
            st.pass = 0u;
            st.reason = "no_frame_rendered";
        } else if (S5Display_CheckFrame(last_fb) == 0) {
            st.pass = 0u;
            st.reason = "frame_check_failed";
        } else if (last_src == S5_SRC_SIM) {
            /* 结果块不可用 → 已回退模拟源：真实数据窗口不算通过，但原因可读 */
            st.pass = 0u;
            st.reason = (last_reason != 0) ? last_reason : "result_block_unavailable";
        } else {
            st.pass = 1u;
            st.reason = last_reason; /* test 回退：pass=1 但保留 raw_frame_blank */
        }

        /* G3-B 联调：把 box_crc 实际使用的**映射后坐标**原样打出来（最多 5 框），
         * 便于生产端/测试端直接对字节序列（u16 小端 x,y,w,h 连续，无填充）。 */
        {
            uint16_t mb[S5_MAX_DET * 4u];
            uint32_t nbx = S5Display_BoxesMapped(last_det, last_det_count, mb, 5u);
            uint32_t bi;

            xil_printf("S5DISP boxes n=%d crc=%d hex=", (int)nbx, (int)st.box_crc);
            for (bi = 0u; bi < (nbx * 4u); bi++) {
                xil_printf("%x ", (unsigned)mb[bi]);
            }
            xil_printf("\r\n");
        }

        xil_printf("S5DISP done frames=%d vcnt=%d(sw) vdma_err=%d\r\n",
                   (int)st.frames, (int)st.vcnt, (int)st.vdma_err);
        S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
        xil_printf("%s\r\n", res);
    }

    return 0;
}

#endif /* !S5_HOST_TEST */

