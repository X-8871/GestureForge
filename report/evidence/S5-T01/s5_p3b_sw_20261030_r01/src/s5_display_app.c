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

void S5Draw_InfoPanel(uint32_t *fb, const S5FrameInfo *info, uint32_t dma_state)
{
    const int x = S5_PANEL_X + 8;
    const int pitch = 20;
    int y = 34;
    char line[40];
    char *p;
    uint32_t i;
    uint32_t age_over;

    /* 背景 + 左侧分隔线 + 标题条 */
    S5Draw_RectFill(fb, S5_PANEL_X, 0, S5_PANEL_W, S5_PANEL_H, S5_COLOR_PANEL_BG);
    S5Draw_RectFill(fb, S5_PANEL_X, 0, 2, S5_PANEL_H, S5_COLOR_PANEL_TITLE);
    S5Draw_RectFill(fb, S5_PANEL_X + 2, 0, S5_PANEL_W - 2, 26, S5_RGB(0x1A, 0x2A, 0x38));
    S5Draw_Text(fb, x, 5, "S5 P3B DISPLAY 720p60", S5_COLOR_PANEL_TITLE, S5_COLOR_TRANSPARENT);

    age_over = (info->status & S5_ST_AGE_OVER) ? 1u : 0u;

    /* FRAME */
    p = s5_cat(line, "FRAME ");
    p = s5_u32(p, info->frame_id, 8);
    s5_end(p);
    S5Draw_Text(fb, x, y, line, S5_COLOR_PANEL_TEXT, S5_COLOR_PANEL_BG);
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
    p = s5_cat(p, age_over ? "OVER" : "OK");
    s5_end(p);
    S5Draw_Text(fb, x, y, line, age_over ? S5_COLOR_BAD : S5_COLOR_OK, S5_COLOR_PANEL_BG);
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

    /* 类别图例 */
    y = 560;
    S5Draw_Text(fb, x, y, "CLASS", S5_COLOR_PANEL_DIM, S5_COLOR_TRANSPARENT);
    y += 20;
    for (i = 0; i < S5_CLASS_NUM; i++) {
        int lx = x + (int)(i % 3u) * 100;
        int ly = y + (int)(i / 3u) * 24;

        S5Draw_RectFill(fb, lx, ly + 2, 12, 12, s5_class_color[i]);
        S5Draw_Text(fb, lx + 16, ly, s5_class_name[i], S5_COLOR_PANEL_TEXT, S5_COLOR_TRANSPARENT);
    }

    /* 页脚：分辨率与版面（便于上板一眼确认走的是哪个版本） */
    S5Draw_Text(fb, x, 680, "960x720 + 320 panel", S5_COLOR_PANEL_DIM, S5_COLOR_TRANSPARENT);
    S5Draw_Text(fb, x, 698, "P3B-SW r03", S5_COLOR_PANEL_DIM, S5_COLOR_TRANSPARENT);
}

/* ---------------- 帧装配 / 测试图 ---------------- */

void S5Display_RenderFrame(uint32_t *fb, const uint32_t *cam,
                           const S5FrameInfo *info, uint32_t dma_state)
{
    if ((fb == 0) || (info == 0)) {
        return;
    }
    /* 清屏把左右 160 px 黑边一次做掉；视频区随后被完全覆盖 */
    S5Draw_Clear(fb, S5_COLOR_BLACK);
    S5Draw_CameraLetterbox(fb, cam);
    S5Draw_Boxes(fb, info->det, info->det_count);
    S5Draw_InfoPanel(fb, info, dma_state);
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
uint32_t S5Display_FormatResult(const S5RunStats *st, char *buf, uint32_t cap)
{
    char *p = buf;

    if ((st == 0) || (buf == 0) || (cap < 200u)) {
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

    if ((st->pass == 0u) && (st->reason != 0)) {
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

/* 每帧把画布从 D-cache 刷到 DDR，否则 VDMA 可能读到旧像素。
 * 若 bring-up 时确认 D-cache 关闭，可把该宏改 0 省掉 ~115k 次 cache 维护。 */
#define S5_DCACHE_FLUSH 1

/* VDMA 周期的帧存个数：与 BD 一致，**2** 个（lead 2026-10-30 已把 c_num_fstores 改为 2）。
 * 双缓冲 A/B，只填 0x5C/0x60 两个地址寄存器，不写第 3 个。 */
#define S5_VDMA_FS_PROG 2u

/* 结果行 fps_inf 口径：本窗口没有真实推理源，按契约允许打印 0（面板仍显示模拟值供版式自检）。
 * 接入真实推理数据源后改为 1，并用滑动窗口计数替换（见报告 §9）。 */
#define S5_RESULT_FPS_INF_FROM_SIM 0

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
    if (dma_init_ok != 0) {
        /* CR.FRMCNT_EN 已在 Start() 里置位；这里再显式使能一次并记录（幂等）。 */
        (void)S5Vdma_EnableFrameCounter(&dma);
    }

    /* 4) 有界主循环：跑满 S5_RUN_FRAMES 帧或达到 S5_RUN_MAX_MS，先到者停机。
     *    有界是契约要求：UART 采集器要收尾并解析最终结果行，不能 for(;;) 无限跑。 */
    {
        uint64_t t_start = S5Ticks_Now();
        uint32_t frames = 0;
        uint32_t vdma_err = 0;
        uint32_t vcnt_hw = 0;
        uint32_t vcnt_sw = 0;
        uint32_t last_store = 0xFFFFFFFFu;
        uint32_t *last_fb = fb[0];
        uint32_t sr;
        S5RunStats st;
        char res[224];

        while ((frames < (uint32_t)S5_RUN_FRAMES) &&
               (S5Ticks_ToMs(S5Ticks_Now() - t_start) < (uint64_t)S5_RUN_MAX_MS)) {
            S5Sim_NextFrame(&info);
            S5Sim_CameraFrame(s5_cam, info.frame_id);

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
                /* vcnt：优先硬件帧计数（SR[23:16]）；读不到则退回软件观测读帧存切换 */
                vcnt_hw = S5Vdma_UpdateFrameCount(&dma);
                {
                    uint32_t cs = S5Vdma_CurrentReadStore(&dma);
                    if (cs != last_store) {
                        vcnt_sw++;
                        last_store = cs;
                    }
                }
            }

            /* 4.2 装配一帧 */
            S5Display_RenderFrame(fb[back], s5_cam, &info, dma_state);
            s5_fb_flush(fb[back]);
            last_fb = fb[back];

            /* 4.3 乒乓 */
            back ^= 1u;
            frames++;

            /* 4.4 进度行（与 RESULT 行分开，绝不拼在同一行） */
            if ((frames % 60u) == 0u) {
                xil_printf("S5DISP frame=%d lat=%d age=%d st=%x sr=%x\r\n",
                           (int)frames, (int)info.latency_ms, (int)info.age_ms,
                           (unsigned)info.status, (unsigned)S5Vdma_Status(&dma));
            }
        }

        /* 5) 停机：停止 VDMA 读取，便于采集器收尾后安全断电/复位 */
        if (dma_state != S5_DMA_OFF) {
            (void)S5Vdma_Stop(&dma);
        }

        /* 6) 结果行：pass = VDMA 无错 + ≥1 帧完整显示 + 信息栏刷新成功 */
        st.pass = 1u;
        st.reason = 0;
        st.frames = frames;
        st.vdma_err = vdma_err;
        st.vcnt = (vcnt_hw > 0u) ? vcnt_hw : vcnt_sw;
        st.fps_cap = (uint32_t)(info.fps_cap_x10 / 10u);
        st.fps_inf = (S5_RESULT_FPS_INF_FROM_SIM != 0) ? (uint32_t)(info.fps_inf_x10 / 10u) : 0u;
        st.fps_dis = (uint32_t)(info.fps_dis_x10 / 10u);
        st.latency_ms = (uint32_t)info.latency_ms;
        st.age_ms = (uint32_t)info.age_ms;

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
        }

        xil_printf("S5DISP done frames=%d vcnt=%d vdma_err=%d\r\n",
                   (int)st.frames, (int)st.vcnt, (int)st.vdma_err);
        S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
        xil_printf("%s\r\n", res);
    }

    return 0;
}

#endif /* !S5_HOST_TEST */
