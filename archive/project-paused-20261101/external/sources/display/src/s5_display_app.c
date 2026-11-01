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
#include "xil_io.h"
#include "s5_display_app.h"

#include <string.h>

#include "s5_font8x16.h"
#include "s5_hud_font.h"
#include "s5_result_abi.h" /* 结果块 ABI（生产者打包与消费者解析共用同一份定义） */
#include "s5_publish_abi.h" /* 生产者 v2 sidecar S5X1 / seqlock / 业务状态映射 */
#include "s5_camera.h"      /* R-07/P3r：可选相机采集（S5_CAMERA=1，与显示/producer 正交） */
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

/* ---------------- MVP HUD（手势中文名 + 置信度 + 延迟 + 边框颜色） ---------------- */
#define S5_GESTURE_NUM 5u
static const uint32_t s5_hud_color_tbl[S5_GESTURE_NUM] = {
    0x00E74C3Cu, 0x00349ADBu, 0x002ECC71u, 0x00F1C40Fu, 0x009B59B6u,
};
static const char *s5_hud_name_utf8[S5_GESTURE_NUM] = {
    "拳头", "布", "数字一", "数字二", "数字三",
};
/* 与 s5_hud_font.h 中字形一致：手势： + 名字 */
static const uint16_t s5_hud_prefix[3] = {0x624Bu, 0x52BFu, 0xFF1Au};
static const uint16_t s5_hud_name_ch[S5_GESTURE_NUM][4] = {
    {0x62F3u, 0x5934u, 0u, 0u},
    {0x5E03u, 0u, 0u, 0u},
    {0x6570u, 0x5B57u, 0x4E00u, 0u},
    {0x6570u, 0x5B57u, 0x4E8Cu, 0u},
    {0x6570u, 0x5B57u, 0x4E09u, 0u},
};
static const uint8_t s5_hud_name_len[S5_GESTURE_NUM] = {2u, 1u, 3u, 3u, 3u};

static const uint8_t *s5_hud_glyph_find(uint16_t ch)
{
    uint32_t i;

    for (i = 0u; i < (uint32_t)(sizeof(s5_hud_glyphs) / sizeof(s5_hud_glyphs[0])); i++) {
        if (s5_hud_glyphs[i].ch == ch) {
            return s5_hud_glyphs[i].bmp;
        }
    }
    return 0;
}

static void s5_hud_glyph(uint32_t *fb, int x, int y, uint16_t ch, uint32_t fg, int scale)
{
    const uint8_t *bmp = s5_hud_glyph_find(ch);
    int gy, gx;

    if (bmp == 0) {
        return;
    }
    for (gy = 0; gy < 16; gy++) {
        uint32_t hi = bmp[gy * 2], lo = bmp[gy * 2 + 1];
        for (gx = 0; gx < 16; gx++) {
            uint32_t on = (gx < 8) ? ((hi >> (7 - gx)) & 1u) : ((lo >> (15 - gx)) & 1u);
            if (on != 0u) {
                S5Draw_RectFill(fb, x + gx * scale, y + gy * scale, scale, scale, fg);
            }
        }
    }
}

static void s5_hud_title(uint32_t *fb, int x, int y, uint8_t cls, uint32_t fg, int scale)
{
    int i, n = (int)s5_hud_name_len[cls];

    for (i = 0; i < 3; i++) {
        s5_hud_glyph(fb, x, y, s5_hud_prefix[i], fg, scale);
        x += 16 * scale;
    }
    for (i = 0; i < n; i++) {
        s5_hud_glyph(fb, x, y, s5_hud_name_ch[cls][i], fg, scale);
        x += 16 * scale;
    }
}

void S5Display_DrawHud(uint32_t *fb, const S5FrameInfo *info)
{
    static uint8_t last_cls = 0xFFu;
    uint32_t cls = 0xFFu, best = 0u, i, color, fg = 0x00FFFFFFu;
    char line[48];
    int x0 = S5_VID_X, y0 = S5_VID_Y, w = S5_VID_W, h = S5_VID_H;

    if ((fb == 0) || (info == 0)) {
        return;
    }
    for (i = 0u; i < info->det_count && i < S5_MAX_DET; i++) {
        if ((uint32_t)info->det[i].score >= best) {
            best = (uint32_t)info->det[i].score;
            cls = info->det[i].cls;
        }
    }
    if (cls >= S5_GESTURE_NUM) {
        cls = 0u;
        color = 0x007F8C8Du; /* 无检测：灰 */
    } else {
        color = s5_hud_color_tbl[cls];
    }
    /* 5 类各一色边框（4 px，画在视频区四边） */
    S5Draw_RectLine(fb, x0, y0, w, h, 6, color);
    /* 左上大号中文：手势：<名字> */
    if (cls < S5_GESTURE_NUM) {
        s5_hud_title(fb, x0 + 24, y0 + 18, (uint8_t)cls, fg, 3);
    } else {
        S5Draw_Text(fb, x0 + 24, y0 + 24, "gesture=none", fg, S5_COLOR_TRANSPARENT);
    }
    /* 置信度 */
    if (info->det_count == 0u) {
        S5Draw_Text(fb, x0 + 24, y0 + 84, "conf=0.00", fg, S5_COLOR_TRANSPARENT);
    } else {
        uint32_t q = best / 100u;      /* 0 */
        uint32_t q2 = best % 100u;     /* 0..99 = 百分位 */

        line[0] = 'c'; line[1] = 'o'; line[2] = 'n'; line[3] = 'f'; line[4] = '=';
        line[5] = (char)('0' + (q % 10u));
        line[6] = '.';
        line[7] = (char)('0' + (q2 / 10u) % 10u);
        line[8] = (char)('0' + (q2 % 10u));
        line[9] = 0;
        S5Draw_Text(fb, x0 + 24, y0 + 84, line, fg, S5_COLOR_TRANSPARENT);
    }
    /* 右下：latency_ms */
    {
        uint32_t ms = info->latency_ms;
        int n = 0;
        char buf[16];

        buf[n++] = 'l'; buf[n++] = 'a'; buf[n++] = 't'; buf[n++] = '=';
        if (ms == 0u) {
            buf[n++] = '?';
        } else {
            char tmp[8];
            int k = 0;
            while ((ms > 0u) && (k < 8)) {
                tmp[k++] = (char)('0' + (ms % 10u));
                ms /= 10u;
            }
            while (k > 0) {
                buf[n++] = tmp[--k];
            }
        }
        buf[n++] = 'm'; buf[n++] = 's'; buf[n] = 0;
        S5Draw_Text(fb, x0 + w - 260, y0 + h - 36, buf, fg, S5_COLOR_TRANSPARENT);
    }
    /* UART：切换一行 + 周期一行（每 30 帧） */
    if (cls != last_cls) {
        xil_printf("APP: gesture_changed from=%s to=%s\r\n",
                   (last_cls < S5_GESTURE_NUM) ? s5_hud_name_utf8[last_cls] : "none",
                   (cls < S5_GESTURE_NUM) ? s5_hud_name_utf8[cls] : "none");
        last_cls = (uint8_t)cls;
    }
    if ((info->frame_id % 30u) == 0u) {
        xil_printf("CAM: frm=%u cr=0x%x sr=0x%x cam_gpio=0x%x s2mm_beat=0x%x tlast=0x%x\r\n",
                   (unsigned)info->frame_id,
                   (unsigned)Xil_In32(0x43C60030u), (unsigned)Xil_In32(0x43C60034u),
                   (unsigned)Xil_In32(0x43C70000u),
                   (unsigned)Xil_In32(0x43CC0000u), (unsigned)Xil_In32(0x43CB0000u));
    }
    if (((info->frame_id % 30u) == 0u) && (cls < S5_GESTURE_NUM)) {
        xil_printf("APP: gesture=%s cls=%u conf=0.%02u latency_ms=%u\r\n",
                   s5_hud_name_utf8[cls], (unsigned)cls, (unsigned)best,
                   (unsigned)info->latency_ms);
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
        S5Display_DrawHud(fb, info);
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

/* 确定性测试图（P3m 目视判读，无随机、无文字覆盖关键区域）：
 *   8 条竖彩条（白/黄/青/绿/品红/红/蓝/黑，各 160 px 宽，整屏高）
 *   + 四边 4 px 白框（判断显示窗口是否对齐/裁切）
 *   + 中央白十字（8 px 粗，判断是否撕裂/滚动/像素错位）
 * 注意：颜色都用 8-bit 满幅，若上屏看到“红蓝互换/颜色发灰”，即为 tdata[23:0] 字节序问题。 */
void S5Display_DeterministicPattern(uint32_t *fb)
{
    static const uint32_t bars[8] = {
        S5_COLOR_WHITE, S5_COLOR_YELLOW, S5_COLOR_CYAN, S5_COLOR_GREEN,
        S5_COLOR_MAGENTA, S5_COLOR_RED, S5_COLOR_BLUE, S5_COLOR_BLACK,
    };
    const int bar_w = S5_CANVAS_W / 8;
    int i;
    int y;

    if (fb == 0) {
        return;
    }
    /* 竖彩条（整屏，含信息栏区域，先证明整屏 DMA 通路） */
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
    /* 四边 4 px 白框 */
    S5Draw_RectFill(fb, 0, 0, S5_CANVAS_W, 4, S5_COLOR_WHITE);
    S5Draw_RectFill(fb, 0, S5_CANVAS_H - 4, S5_CANVAS_W, 4, S5_COLOR_WHITE);
    S5Draw_RectFill(fb, 0, 0, 4, S5_CANVAS_H, S5_COLOR_WHITE);
    S5Draw_RectFill(fb, S5_CANVAS_W - 4, 0, 4, S5_CANVAS_H, S5_COLOR_WHITE);
    /* 中央白十字（8 px 粗，整幅） */
    S5Draw_RectFill(fb, (S5_CANVAS_W / 2) - 4, 0, 8, S5_CANVAS_H, S5_COLOR_WHITE);
    S5Draw_RectFill(fb, 0, (S5_CANVAS_H / 2) - 4, S5_CANVAS_W, 8, S5_COLOR_WHITE);
    /* 左上角标识（黑字压在白条上，便于确认识别到了这张图） */
    S5Draw_Text(fb, 12, 10, "S5 TEST: BARS8+BORDER+CROSS", S5_COLOR_BLACK, S5_COLOR_TRANSPARENT);
}

/* ---------------- 结果行（runner 契约实现，纯函数） ----------------
 * 契约（写死，不得改字段名/单位，见 s5_display_app.h）：
 *   S5DISP RESULT={"pass":1,"fps_cap":60,"fps_inf":0,"fps_dis":60,"latency_ms":0,
 *                  "age_ms":47320,"vdma_err":0,"frames":180,"vcnt":180}
 * 失败时追加 "reason":"..."。整行必须在**同一行**输出（调用方只补一次 \r\n）。 */
/* ---------------- CRC32（G3 需要 box_crc / fb_crc） ---------------- */

static uint32_t s5_crc_tab[256];
static int s5_crc_tab_ready;

/* ---------------- 生产者：结果块打包（纯函数，主机可自检） ---------------- */

void S5Prod_PackBlock(uint32_t *buf, uint32_t frame_id, uint32_t n_dets, const S5DetBox *det,
                      uint64_t cap_ticks, uint64_t inf_ticks, uint32_t status)
{
    uint32_t i;
    uint32_t n = (n_dets > S5_RESULT_MAX_DETS) ? S5_RESULT_MAX_DETS : n_dets;

    if (buf == 0) {
        return;
    }
    /* 整块清零（0x120 = 288 B，仅头+项）：保证保留字段/未用槽位恒 0 */
    for (i = 0u; i < (S5_RESULT_BLOCK_BYTES / 4u); i++) {
        buf[i] = 0u;
    }
    /* 头 32 B */
    buf[S5_RESULT_W_MAGIC] = S5_RESULT_MAGIC;
    buf[S5_RESULT_W_FRAME_ID] = frame_id;
    buf[S5_RESULT_W_N_DETS] = n;
    buf[S5_RESULT_W_CAP_LO] = (uint32_t)(cap_ticks & 0xFFFFFFFFu);
    buf[S5_RESULT_W_CAP_HI] = (uint32_t)(cap_ticks >> 32);
    buf[S5_RESULT_W_INF_LO] = (uint32_t)(inf_ticks & 0xFFFFFFFFu);
    buf[S5_RESULT_W_INF_HI] = (uint32_t)(inf_ticks >> 32);
    buf[S5_RESULT_W_STATUS] = status;
    /* 检测项：16 B 步进，x,y,w,h u16（源 640×480 坐标）+ cls/score_q8 + reserved/pad = 0 */
    for (i = 0u; i < n; i++) {
        uint32_t *d = &buf[(S5_RESULT_DETS_OFFSET / 4u) + i * (S5_RESULT_DET_BYTES / 4u)];

        d[0] = ((uint32_t)(uint16_t)det[i].y << 16) | (uint32_t)(uint16_t)det[i].x;
        d[1] = ((uint32_t)(uint16_t)det[i].h << 16) | (uint32_t)(uint16_t)det[i].w;
        d[2] = ((uint32_t)det[i].score << 8) | (uint32_t)det[i].cls;
        d[3] = 0u; /* 末尾 4 B 填充 */
    }
    /* session 标记（ABI 允许的 reserved 字段；不影响既有字段语义） */
    buf[(S5_RESULT_DETS_OFFSET / 4u) + 15u * (S5_RESULT_DET_BYTES / 4u) + 2u] =
        (uint32_t)S5_PROD_SESSION_TAG << 16;
}

/* ---------------- 生产者 v2：sidecar / seq / 业务状态（纯函数，主机可自检） ---------------- */

const char *S5Pub_StateName(uint32_t state)
{
    switch (state) {
    case S5_BIZ_OK:
        return "OK";
    case S5_BIZ_NO_HAND:
        return "NO_HAND";
    case S5_BIZ_TIMEOUT:
        return "TIMEOUT";
    default:
        return "ERROR";
    }
}

void S5Pub_PackSidecar(uint32_t *sc, uint32_t session_id, uint32_t result_seq,
                       uint64_t result_time_ticks, uint32_t seqlock)
{
    if (sc == 0) {
        return;
    }
    sc[S5_PUB_W_MAGIC2] = S5_PUB_MAGIC2;
    sc[S5_PUB_W_VERSION] = S5_PUB_VERSION;
    sc[S5_PUB_W_SESSION_ID] = session_id & 0xFFFFu;
    sc[S5_PUB_W_RESULT_SEQ] = result_seq;
    sc[S5_PUB_W_RTIME_LO] = (uint32_t)(result_time_ticks & 0xFFFFFFFFu);
    sc[S5_PUB_W_RTIME_HI] = (uint32_t)(result_time_ticks >> 32);
    sc[S5_PUB_W_SEQLOCK] = seqlock;
    sc[S5_PUB_W_RESERVED] = 0u;
}

int S5Pub_NextSeq(uint32_t last, uint32_t *out)
{
    if (out == 0) {
        return -1;
    }
    if (last >= S5_PUB_SEQ_LAST) {
        return -1; /* 0xFFFFFFFF → 0 一律拒绝（须新 session） */
    }
    *out = last + 1u; /* 0xFFFFFFFE → 0xFFFFFFFF 正常（上限之内） */
    return ((*out > last) ? 0 : -1);
}

uint32_t S5Pub_AgePublishMs(uint64_t now_ticks, uint64_t result_time_ticks)
{
    uint64_t d;

    if (result_time_ticks == 0u) {
        return 0u; /* 时间戳未知 */
    }
    if (now_ticks < result_time_ticks) {
        return 0u; /* 时钟回绕/未来时间戳 */
    }
    d = now_ticks - result_time_ticks;
    return (uint32_t)((d * 1000u) / S5_GT_HZ);
}

uint32_t S5Pub_BizState(const S5PubView *v, uint32_t age_publish_ms)
{
    if (v == 0) {
        return S5_BIZ_ERROR;
    }
    if ((v->status & S5_RESULT_ST_VALID) == 0u) {
        return S5_BIZ_ERROR; /* 优先级 1 */
    }
    if ((v->status & S5_RESULT_ST_OVERRUN) != 0u) {
        return S5_BIZ_ERROR; /* 优先级 2 */
    }
    if (((v->status & S5_RESULT_ST_STALE) != 0u) || (age_publish_ms > S5_BIZ_AGE_LIMIT_MS)) {
        return S5_BIZ_TIMEOUT; /* 优先级 3 */
    }
    if (v->n_dets == 0u) {
        return S5_BIZ_NO_HAND; /* 优先级 4 */
    }
    return S5_BIZ_OK; /* 优先级 5 */
}

int S5Pub_SeqlockStable(uint32_t s_first, uint32_t s_second)
{
    if ((s_first & 1u) != 0u) {
        return -1; /* 读到奇数：写入中 */
    }
    return (s_first == s_second) ? 0 : -1;
}

/* ---------------- rev4：seqlock 严格顺序的实现（纯函数 + 回调，主机可记录调用序） ---------------- */

#define S5_PUB_W_LOCK (S5_PUB_SIDECAR_OFFSET / 4u + S5_PUB_W_SEQLOCK) /* 0x100/4 + 6 = 70 */
#define S5_PUB_W_RT_LO (S5_PUB_SIDECAR_OFFSET / 4u + S5_PUB_W_RTIME_LO)
#define S5_PUB_W_RT_HI (S5_PUB_SIDECAR_OFFSET / 4u + S5_PUB_W_RTIME_HI)

int S5Pub_WritePublish(S5PubMem *m, uint32_t *sl, const uint32_t *blk, uint64_t result_time_ticks)
{
    uint32_t i;
    uint32_t odd;
    uint32_t even;

    if ((m == 0) || (m->payload == 0) || (m->flush == 0) || (m->barrier == 0) || (sl == 0) || (blk == 0)) {
        return -1;
    }
    if ((*sl & 1u) != 0u) {
        return -1; /* 起始必须为偶（稳定态） */
    }
    odd = *sl + 1u;
    even = *sl + 2u;

    /* ① 锁变奇 → 单独 flush 锁行 → DSB */
    m->payload[S5_PUB_W_LOCK] = odd;
    m->flush(m->ctx, &m->payload[S5_PUB_W_LOCK], 4u);
    m->barrier(m->ctx);

    /* ② 写头/项/sidecar 非时间字段，最后写 result_time */
    for (i = 0u; i < (S5_PUB_PUBLISH_BYTES / 4u); i++) {
        if ((i == S5_PUB_W_LOCK) || (i == S5_PUB_W_RT_LO) || (i == S5_PUB_W_RT_HI)) {
            continue;
        }
        m->payload[i] = blk[i];
    }
    m->payload[S5_PUB_W_RT_LO] = (uint32_t)(result_time_ticks & 0xFFFFFFFFu);
    m->payload[S5_PUB_W_RT_HI] = (uint32_t)(result_time_ticks >> 32);

    /* ③ flush 整个发布区（288 B）→ DSB */
    m->flush(m->ctx, m->payload, S5_PUB_PUBLISH_BYTES);
    m->barrier(m->ctx);

    /* ④ 锁变偶 → flush 锁行 → DSB */
    m->payload[S5_PUB_W_LOCK] = even;
    m->flush(m->ctx, &m->payload[S5_PUB_W_LOCK], 4u);
    m->barrier(m->ctx);
    *sl = even;
    return 0;
}

int S5Pub_ReadPublish(S5PubMem *m, uint32_t *blk_out, uint32_t *sl_out, S5PubReadTrace *tr)
{
    uint32_t attempt;
    uint32_t i;
    uint32_t s1;
    uint32_t s2;

    if (tr != 0) {
        tr->attempts = 0u;
        tr->retries = 0u;
        tr->s1_last = 0u;
        tr->s2_last = 0u;
    }
    if ((m == 0) || (m->payload == 0) || (m->invalidate == 0) || (m->barrier == 0) || (blk_out == 0)) {
        return -1;
    }
    for (attempt = 0u; attempt < 3u; attempt++) {
        /* ① 先 invalidate（锁行 + payload 一起失效） */
        m->invalidate(m->ctx, m->payload, S5_PUB_PUBLISH_BYTES);
        /* ② 读 s1；奇数=写入中，重试 */
        s1 = m->payload[S5_PUB_W_LOCK];
        if (tr != 0) {
            tr->attempts = attempt + 1u;
            tr->s1_last = s1;
        }
        if ((s1 & 1u) != 0u) {
            continue; /* 写入中：重试（s2_last 保持 0，表示未读到第二把锁） */
        }
        /* ③ 读 payload → DMB */
        for (i = 0u; i < (S5_PUB_PUBLISH_BYTES / 4u); i++) {
            blk_out[i] = m->payload[i];
        }
        m->barrier(m->ctx);
        /* ④ 再读 s2，须 s1==s2 且为偶 */
        s2 = m->payload[S5_PUB_W_LOCK];
        if (tr != 0) {
            tr->s2_last = s2;
        }
        if (((s2 & 1u) == 0u) && (s2 == s1)) {
            if (sl_out != 0) {
                *sl_out = s2;
            }
            if (tr != 0) {
                tr->retries = attempt;
            }
            return 0;
        }
    }
    if (tr != 0) {
        tr->retries = (tr->attempts > 0u) ? (tr->attempts - 1u) : 0u;
    }
    return -1; /* 重试超限：TIMEOUT */
}

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

    if ((st == 0) || (buf == 0) || (cap < 360u)) {
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
    /* r06c：空闲测速结果（不写帧存时 VDMA 读帧存周期）；未测时两项均为 0 */
    p = s5_cat(p, ",\"fps_dis_idle\":");
    p = s5_u32(p, S5_FPS_CLAMP(st->fps_dis_idle), 0);
    p = s5_cat(p, ",\"idle_period_us\":");
    p = s5_u32(p, st->idle_period_us, 0);
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
    /* underflow 像素计数：uf_pix 兼容字段（= uf_total）；P3p 另给 uf_frame/uf_total */
    p = s5_cat(p, ",\"uf_pix\":");
    p = s5_u32(p, st->uf_pix, 0);
    p = s5_cat(p, ",\"uf_frame\":");
    p = s5_u32(p, st->uf_frame, 0);
    p = s5_cat(p, ",\"uf_total\":");
    p = s5_u32(p, st->uf_total, 0);

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
#include "xaxivdma.h"
#include "xil_printf.h"
#include "xparameters.h"
#include "xil_io.h"

#include "s5_timebase.h"
#include "s5_real_source.h"  /* 真实数据源：结果块解析 / raw 画面转换 / 回退判据 */
#include "s5_result_abi.h"   /* 结果块 ABI（0x20800000）+ raw frame（0x12000000） */
#include "xtimer_config.h" /* COUNTS_PER_SECOND（无括号宏，用括号包裹后做静态断言） */

/* v29：相机 VDMA（S2MM-only, 24bpp, DRE=1, SG=0）驱动配置（与阶段3 对齐） */
static XAxiVdma_Config s5_vdma_cfg = {
    .Name = "s5_cam_vdma",
    .BaseAddress = 0x43C60000u,
    .MaxFrameStoreNum = 1,
    .HasMm2S = 0,
    .HasMm2SDRE = 0,
    .Mm2SWordLen = 0,
    .HasS2Mm = 1,
    .HasS2MmDRE = 1,
    .S2MmWordLen = 2,
    .HasSG = 0,
    .EnableVIDParamRead = 0,
    .UseFsync = 0,
    .FlushonFsync = 0,
    .Mm2SBufDepth = 0,
    .S2MmBufDepth = 0,
    .Mm2SGenLock = 0,
    .S2MmGenLock = 0,
    .InternalGenLock = 0,
    .S2MmSOF = 0,
    .Mm2SStreamWidth = 0,
    .S2MmStreamWidth = 24,
    .AddrWidth = 32,
};

static const char *s5_cam_stage_name(int rc)
{
    switch (rc) {
    case -10: return "chipid";      case -11: return "sccb_probe";
    case -12: return "overlay";     case -13: return "regchk";
    case -17: return "init_table";  case -18: return "stream_on";
    case -19: return "stream_off";  case -20: return "timing";
    case -21: return "vdma_clear_reset"; case -22: return "vdma_start_rs";
    case -16: return "reset_seq";   default: return (rc < 0) ? "other" : "ok";
    }
}

static uint32_t app_now_ms(void)
{
    return (uint32_t)(S5Ticks_Now() / (S5_GT_HZ / 1000u));
}


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

#if S5_CAMERA != 0
/* ---- R-07/P3r：相机总线适配（真实 MMIO）与初始化 ---- */
static uint32_t s5_cam_bus_rd(void *ctx, uint32_t addr)
{
    (void)ctx;
    return Xil_In32(addr);
}

static void s5_cam_bus_wr(void *ctx, uint32_t addr, uint32_t val)
{
    (void)ctx;
    Xil_Out32(addr, val);
}

static void s5_cam_bus_delay(void *ctx, uint32_t us);

#if S5_CAM_DIAG != 0
static S5CamBus s5_cam_bus_diag = {0, s5_cam_bus_rd, s5_cam_bus_wr, s5_cam_bus_delay, app_now_ms};
#endif

static void s5_cam_bus_delay(void *ctx, uint32_t us)
{
    uint64_t t0 = S5Ticks_Now();

    (void)ctx;
    while ((S5Ticks_Now() - t0) < S5Ticks_FromUs(us)) {
        /* busy wait：仅相机上电/复位序列使用，5×500 ms 量级 */
    }
}

/* 返回值：0=相机就绪；<0=失败（显示继续，raw 无效时按四态回退到测试图/无框） */
static int s5_cam_bringup(S5CamInfo *info)
{
    static S5CamBus bus = {0, s5_cam_bus_rd, s5_cam_bus_wr, s5_cam_bus_delay, app_now_ms};
    int rc;

    rc = S5Cam_Init(&bus, (uint32_t)S5_CAM_I2C_CLK_HZ, info);
    if (rc == 0) {
        {
            uint8_t g3808 = 0u, g3809 = 0u, g380a = 0u, g380b = 0u;
            uint8_t g380c = 0u, g380d = 0u, g380e = 0u, g380f = 0u;

            (void)S5Cam_ReadReg(&bus, 0x3808u, &g3808);
            (void)S5Cam_ReadReg(&bus, 0x3809u, &g3809);
            (void)S5Cam_ReadReg(&bus, 0x380Au, &g380a);
            (void)S5Cam_ReadReg(&bus, 0x380Bu, &g380b);
            (void)S5Cam_ReadReg(&bus, 0x380Cu, &g380c);
            (void)S5Cam_ReadReg(&bus, 0x380Du, &g380d);
            (void)S5Cam_ReadReg(&bus, 0x380Eu, &g380e);
            (void)S5Cam_ReadReg(&bus, 0x380Fu, &g380f);
            xil_printf("CAM: vsize=%u hsize=%u stride=%u frame_bytes=%u\r\n",
                       (unsigned)S5_CAM_VDMA_VSIZE, (unsigned)S5_CAM_HSIZE,
                       (unsigned)S5_CAM_STRIDE,
                       (unsigned)(S5_CAM_STRIDE * S5_CAM_VDMA_VSIZE));
            {
                uint8_t w1 = 0u, w2 = 0u;

                (void)S5Cam_WriteReg(&bus, 0x380Au, 0x02u);
                (void)S5Cam_WriteReg(&bus, 0x380Bu, 0xD0u);
                s5_cam_bus_delay(0, 1000u);
                (void)S5Cam_ReadReg(&bus, 0x380Au, &w1);
                (void)S5Cam_ReadReg(&bus, 0x380Bu, &w2);
                xil_printf("CAM: dvpvo_wr720_1ms=0x%02x%02x\r\n", (unsigned)w1, (unsigned)w2);
                s5_cam_bus_delay(0, 10000u);
                (void)S5Cam_ReadReg(&bus, 0x380Au, &w1);
                (void)S5Cam_ReadReg(&bus, 0x380Bu, &w2);
                xil_printf("CAM: dvpvo_wr720_10ms=0x%02x%02x\r\n", (unsigned)w1, (unsigned)w2);
            }
            xil_printf("CAM: geom dvpho=%u dvpvo=%u hts=%u vts=%u (expect 1280/720/1892/740)\r\n",
                       (unsigned)(((uint32_t)g3808 << 8) | g3809),
                       (unsigned)(((uint32_t)g380a << 8) | g380b),
                       (unsigned)(((uint32_t)g380c << 8) | g380d),
                       (unsigned)(((uint32_t)g380e << 8) | g380f));
        }
        {
            uint32_t sr0 = 0u, sr1 = 0u;

            (void)S5Cam_VdmaClearSr(&bus, &sr0, &sr1);
            xil_printf("CAM: sr_after_clear=0x%x (before=0x%x, expect 0x10000 or 0x0)\r\n",
                       (unsigned)sr1, (unsigned)sr0);
            s5_cam_bus_delay(0, 1000000u);
            xil_printf("CAM: sr_after_1s=0x%x (0x14810 => FSZ_MORE recurs per frame -> SOF phase/hw)\r\n",
                       (unsigned)Xil_In32(0x43C60034u));
        }
        xil_printf("CAM: init OK chip=0x%04x %dx%d stride=%d raw=0x%x (24bpp BGR888)\r\n",
                   (unsigned)info->chip_id, (int)S5_CAM_CAP_W, (int)S5_CAM_VSIZE,
                   (int)S5_CAM_STRIDE, (unsigned)S5_CAM_RAW_BASE);
    } else if (rc == -10) {
        xil_printf("CAM: FAILED rc=%d（CHIPID 不是 0x5640：SCCB 不通/摄像头未接）→ 继续显示测试图\r\n", rc);
    } else if (rc == -15) {
        xil_printf("CAM: FAILED rc=%d（S2MM 未退出 HALTED：无像素时钟/VDMA 基址 0x%x 不对）\r\n",
                   rc, (unsigned)S5_CAM_VDMA_BASE);
    } else {
        xil_printf("CAM: FAILED rc=%d（I2C/覆盖表/回读/S2MM 配置阶段失败）→ 继续显示测试图\r\n", rc);
    }
    return rc;
}
#endif

/* ================= 生产者 v2（S5_PRODUCER=1，阶段6 6-D 口径冻结 2026-10-30） =================
 * 发布范围（身份 A）：32 B 头 + 检测项（n_dets≤14）+ 32 B sidecar S5X1（0x20800100），
 *           一次 Xil_DCacheFlushRange(0x20800000, 0x120) 覆盖全部（288 B）。
 * seqlock：seqlock++（奇）→ 写头/项/sidecar → 写 result_time（整块最后一个字段）→ flush
 *          → seqlock++（偶）→ flush（让偶值可见）。
 * result_seq：会话内从 0 严格 +1；0xFFFFFFFE→0xFFFFFFFF 正常；0xFFFFFFFF→0 / 任何回退
 *           → 拒绝（seq 不前进）并置 status.overrun=1（sticky）。
 * session_id：(GT_at_start>>10)&0xFFFF；与旧 sidecar 的 session 碰撞则 +1 重试（≤8 次）。
 */
#if S5_PRODUCER != 0

_Static_assert((uint64_t)COUNTS_PER_SECOND == S5_GT_HZ,
               "COUNTS_PER_SECOND 必须与 S5_GT_HZ 一致（xtimer 宏无括号坑）");

static uint32_t s5_pub_sid;     /* 本会话 session_id */
static uint32_t s5_pub_seq;     /* 本会话 result_seq（严格 +1） */
static uint32_t s5_pub_seqlock; /* 偶数=稳定，奇数=写入中 */
static uint32_t s5_pub_overrun; /* sticky：seq 拒绝/内部不一致 → status.overrun=1 */
static uint32_t s5_pub_pubcnt;  /* 已尝试发布帧数（故障循环相位用） */

static uint64_t s5_prod_now(void)
{
    /* 本 BSP 无 xtime_l.h（无 XTime_GetTime）：直接读全局定时器 0xF8F00200（hi-lo-hi），
     * 与 XTime_GetTime 同一计数器、同一 COUNTS_PER_SECOND（上方已静态断言）。 */
    return S5Ticks_Now();
}

static void s5_dsb(void)
{
#if defined(__arm__)
    __asm__ volatile("dsb" ::: "memory");
#endif
}

static void s5_dmb(void)
{
#if defined(__arm__)
    __asm__ volatile("dmb" ::: "memory");
#endif
}

/* rev4：统一的内存操作端口（写者用 flush+DSB，消费者用 invalidate+DMB） */
static void s5_pub_mem_flush(void *ctx, const volatile void *addr, uint32_t bytes)
{
    (void)ctx;
    Xil_DCacheFlushRange((UINTPTR)addr, (INTPTR)bytes);
}

static void s5_pub_mem_invalidate(void *ctx, const volatile void *addr, uint32_t bytes)
{
    (void)ctx;
    Xil_DCacheInvalidateRange((UINTPTR)addr, (INTPTR)bytes);
}

static void s5_pub_mem_barrier(void *ctx)
{
    (void)ctx;
    s5_dsb();
}

/* session 起始标记用：写完整块后 flush 288 B + DSB */
static void s5_pub_flush(void)
{
    Xil_DCacheFlushRange((UINTPTR)S5_RESULT_BASE, (INTPTR)S5_PUB_PUBLISH_BYTES);
    s5_dsb();
}

static S5PubMem s5_pub_mem = {
    0,
    (volatile uint32_t *)S5_RESULT_BASE,
    s5_pub_mem_flush,
    s5_pub_mem_invalidate,
    s5_pub_mem_barrier,
};

/* 消费者：读 payload 之后要 DMB（不是 DSB） */
static void s5_pub_mem_barrier_dmb(void *ctx)
{
    (void)ctx;
    s5_dmb();
}

static S5PubMem s5_pub_read_mem = {
    0,
    (volatile uint32_t *)S5_RESULT_BASE,
    s5_pub_mem_flush,
    s5_pub_mem_invalidate,
    s5_pub_mem_barrier_dmb,
};

/* session_id（rev4 措辞）：上电 GT>>10 & 0xFFFF，与上一会话（残留在 sidecar 里）碰撞则 +1，最多 8 次。
 * **只主张"会话内 session_id 恒定"；跨 POR 的唯一性不主张**（列为阶段7 R-14）。
 * 该 +1 重试仅为降低碰撞概率的 best-effort，不构成唯一性保证。 */
static uint32_t s5_pub_pick_session_id(void)
{
    volatile uint32_t *sc = (volatile uint32_t *)S5_PUB_SIDECAR_BASE;
    uint32_t cand = (uint32_t)((s5_prod_now() >> 10) & 0xFFFFu);
    uint32_t prev = 0u;
    uint32_t have_prev = 0u;
    uint32_t i;

    if ((sc[S5_PUB_W_MAGIC2] == S5_PUB_MAGIC2) && (sc[S5_PUB_W_VERSION] == S5_PUB_VERSION)) {
        prev = sc[S5_PUB_W_SESSION_ID] & 0xFFFFu;
        have_prev = 1u;
    }
    for (i = 0u; i < S5_PUB_SESSION_RETRY_MAX; i++) {
        if ((have_prev == 0u) || (cand != prev)) {
            break;
        }
        cand = (cand + 1u) & 0xFFFFu;
    }
    return cand;
}

/* 当前生效的故障注入类型（编译期固定值，或 CYCLE 模式按相位轮换） */
static uint32_t s5_pub_fault_now(void)
{
#if S5_PROD_FAULT == S5_PROD_FAULT_CYCLE
    static const uint32_t phases[5] = {S5_PROD_FAULT_NONE, S5_PROD_FAULT_NO_HAND, S5_PROD_FAULT_STALE,
                                       S5_PROD_FAULT_OVERRUN, S5_PROD_FAULT_INVALID};
    return phases[(s5_pub_pubcnt / S5_PROD_FAULT_PHASE) % 5u];
#else
    return (uint32_t)S5_PROD_FAULT;
#endif
}

static const char *s5_pub_fault_name(uint32_t f)
{
    switch (f) {
    case S5_PROD_FAULT_OVERRUN:
        return "overrun";
    case S5_PROD_FAULT_STALE:
        return "stale";
    case S5_PROD_FAULT_INVALID:
        return "invalid";
    case S5_PROD_FAULT_NO_HAND:
        return "no_hand";
    default:
        return "none";
    }
}

/* session 起始标记：frame_id=0、n_dets=0、valid=1、seq=0、seqlock=0（偶）、result_time=now */
static void s5_prod_session_start(void)
{
    static uint32_t blk[S5_PUB_PUBLISH_BYTES / 4u];
    static uint32_t sc[8];
    uint64_t now = s5_prod_now();
    uint32_t i;

    s5_pub_sid = s5_pub_pick_session_id();
    s5_pub_seq = 0u;
    s5_pub_seqlock = 0u;
    s5_pub_overrun = 0u;
    s5_pub_pubcnt = 0u;

    S5Prod_PackBlock(blk, 0u, 0u, 0, now, now, S5_RESULT_ST_VALID);
    S5Pub_PackSidecar(sc, s5_pub_sid, 0u, now, 0u);
    for (i = 0u; i < (S5_RESULT_BLOCK_BYTES / 4u); i++) {
        ((volatile uint32_t *)S5_RESULT_BASE)[i] = blk[i];
    }
    for (i = 0u; i < 8u; i++) {
        ((volatile uint32_t *)S5_PUB_SIDECAR_BASE)[i] = sc[i];
    }
    s5_pub_flush();
    xil_printf("S5PROD session start: sid=%d frame_id=0 tag=%x status=0x1 rtime_ms=%d (333 Hz)\r\n",
               (int)s5_pub_sid, (unsigned)S5_PROD_SESSION_TAG, (int)S5Ticks_ToMs(now));
}

/* 发布一帧：cap 为本帧开始渲染时刻；inf = cap + S5_PROD_INF_OFFSET_TICKS（模拟推理完成） */
static void s5_prod_emit(uint64_t cap_ticks, const S5DetBox *det, uint32_t n_dets)
{
    static uint32_t blk[S5_PUB_PUBLISH_BYTES / 4u];
    uint32_t fault;
    uint32_t n = (n_dets > S5_PUB_NDETS_MAX) ? S5_PUB_NDETS_MAX : n_dets;
    uint32_t status;
    uint32_t age_ms;
    uint32_t next_seq;
    uint64_t rtime;
    S5PubView v;

    s5_pub_pubcnt++;
    fault = s5_pub_fault_now();

    /* n_dets fail-closed（身份 A：≤14）：sidecar 占用槽位 14/15，>14 时拒绝发布本帧并置 overrun，
     * 禁止静默截断（截断会让消费端以为结果完整）。 */
    if (S5Pub_NDetsOk(n_dets) != 0) {
        s5_pub_overrun = 1u;
        xil_printf("S5PROD REJECT n_dets=%d (>%d) status.overrun=1 (fail-closed, 本帧不发布)\r\n",
                   (int)n_dets, (int)S5_PUB_NDETS_MAX);
        return;
    }

    /* result_seq：严格 +1；0xFFFFFFFF→0 或回退一律拒绝（本帧不推进 seq，置 overrun） */
    if (S5Pub_NextSeq(s5_pub_seq, &next_seq) != 0) {
        s5_pub_overrun = 1u;
        xil_printf("S5PROD REJECT seq: last=%d (0xFFFFFFFF->0 或回退) status.overrun=1\r\n",
                   (int)s5_pub_seq);
    } else {
        s5_pub_seq = next_seq;
    }

    /* status 按冻结口径置位：valid=1（除非 invalid 故障）/ overrun(sticky 或注入) / stale(注入或 age>200ms) */
    age_ms = (uint32_t)S5Ticks_ToMs(s5_prod_now() - cap_ticks);
    status = S5_RESULT_ST_VALID;
    if ((s5_pub_overrun != 0u) || (fault == S5_PROD_FAULT_OVERRUN)) {
        status |= S5_RESULT_ST_OVERRUN;
    }
    if ((fault == S5_PROD_FAULT_STALE) || (age_ms > S5_BIZ_AGE_LIMIT_MS)) {
        status |= S5_RESULT_ST_STALE;
    }
    if (fault == S5_PROD_FAULT_INVALID) {
        status &= ~S5_RESULT_ST_VALID;
    }
    /* NO_HAND 注入：故障相位 no_hand，或编译期每 N 帧置 n_dets=0 */
    if ((fault == S5_PROD_FAULT_NO_HAND) ||
        ((S5_PROD_NO_HAND_EVERY_N > 0u) && ((s5_pub_pubcnt % S5_PROD_NO_HAND_EVERY_N) == 0u))) {
        n = 0u;
    }

    /* 打包（blk = 完整 0x120 镜像：头 + 项（≤14）+ sidecar 原位 +0x100） */
    S5Prod_PackBlock(blk, s5_pub_seq, n, det, cap_ticks,
                     cap_ticks + (uint64_t)S5_PROD_INF_OFFSET_TICKS, status);
    S5Pub_PackSidecar(&blk[S5_PUB_SIDECAR_OFFSET / 4u], s5_pub_sid, s5_pub_seq, 0u, 0u);

    /* rev4 严格顺序（S5Pub_WritePublish）：
     * 锁奇 → flush 锁行 → DSB → 写 payload（rtime 最后）→ flush 288B → DSB → 锁偶 → flush 锁行 → DSB */
    rtime = s5_prod_now();
    if (S5Pub_WritePublish(&s5_pub_mem, &s5_pub_seqlock, blk, rtime) != 0) {
        xil_printf("S5PROD REJECT publish: seqlock 起始非偶/参数错\r\n");
        return;
    }

    v.status = status;
    v.n_dets = n;
    v.session_id = s5_pub_sid;
    v.result_seq = s5_pub_seq;
    v.seqlock = s5_pub_seqlock;
    v.result_time = rtime;
    xil_printf("S5PROD frame_id=%d n=%d status=0x%x sid=%d seq=%d rtime_ms=%d age_pub=%d state=%s fault=%s cap_ms=%d\r\n",
               (int)s5_pub_seq, (int)n, (unsigned)status, (int)s5_pub_sid, (int)s5_pub_seq,
               (int)S5Ticks_ToMs(rtime), (int)S5Pub_AgePublishMs(s5_prod_now(), rtime),
               S5Pub_StateName(S5Pub_BizState(&v, 0u)), s5_pub_fault_name(fault),
               (int)S5Ticks_ToMs(cap_ticks));
}

/* 消费者视角（rev4 顺序，v5 增可观测）：返回 0=一致 / -1=重试超限(TIMEOUT) / -2=sidecar 缺失（旧生产者）
 * 顺序由 S5Pub_ReadPublish 保证：invalidate-first（含锁行）→ 读 s1 → 奇重试 → 读 payload → DMB → 读 s2（须偶且相同）；
 * v5 额外输出 S5PubReadTrace（attempts/retries/s1_last/s2_last）供 S5CONS 打印与 E6-A 证据。 */
static int s5_pub_consume(uint64_t now, S5PubView *v, uint32_t *age_ms, S5PubReadTrace *tr)
{
    static uint32_t blk[S5_PUB_PUBLISH_BYTES / 4u];
    const uint32_t scw = S5_PUB_SIDECAR_OFFSET / 4u;
    uint32_t sl = 0u;

    if (v == 0) {
        return -1;
    }
    if (S5Pub_ReadPublish(&s5_pub_read_mem, blk, &sl, tr) != 0) {
        return -1; /* 3 次重试仍不一致 ⇒ TIMEOUT */
    }
    if ((blk[scw + S5_PUB_W_MAGIC2] != S5_PUB_MAGIC2) || (blk[scw + S5_PUB_W_VERSION] != S5_PUB_VERSION)) {
        return -2; /* 旧生产者：无 sidecar */
    }
    v->status = blk[S5_RESULT_W_STATUS];
    v->n_dets = blk[S5_RESULT_W_N_DETS];
    v->session_id = blk[scw + S5_PUB_W_SESSION_ID] & 0xFFFFu;
    v->result_seq = blk[scw + S5_PUB_W_RESULT_SEQ];
    v->result_time = ((uint64_t)blk[scw + S5_PUB_W_RTIME_HI] << 32) |
                     (uint64_t)blk[scw + S5_PUB_W_RTIME_LO];
    v->seqlock = sl;
    *age_ms = S5Pub_AgePublishMs(now, v->result_time);
    return 0;
}

#endif /* S5_PRODUCER */


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
#if S5_NO_VTC == 0
    static S5Vtc vtc;
    S5VtcTiming timing;
#endif
    S5FrameInfo info;
    uint32_t *fb[2];
    uint32_t fb_addr[S5_VDMA_FS_PROG];
    uint32_t back = 0;
    uint32_t dma_state = S5_DMA_OFF;
    uint32_t major = 0;
    uint32_t minor = 0;
    uint32_t rev = 0;
    uint32_t i;
    uint32_t cam_ok = 0u; /* S5_CAMERA=1：相机采集是否就绪（仅用于周期打印） */
    int dma_init_ok = 0;
    int rc;
    uint32_t uf_frame = 0u;             /* P3p：本帧欠载像素 */
    uint32_t uf_total = 0xFFFFFFFFu;    /* 累计欠载像素（P3n = 单寄存器值）；未读到保持 FFFFFFFF */
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
    xil_printf("hw: VDMA AXI-Lite @%x, VTC=%s, UF GPIO @%x\r\n",
               S5_VDMA_BASE,
               (S5_NO_VTC != 0) ? "absent(P3m: axis_to_video owns timing)" : "present(P3b)",
               S5_UF_GPIO_BASE);
    S5Fps_Reset(&win_cap);
    S5Fps_Reset(&win_inf);
    S5Fps_Reset(&win_upd);
    xil_printf("run mode: %s, frames_cap=%d, time_cap_ms=%d\r\n",
               (S5_LONG_RUN != 0) ? "LONG(30min)" : "bounded",
               (int)((S5_LONG_RUN != 0) ? 0 : (int)S5_RUN_FRAMES),
               (int)((S5_LONG_RUN != 0) ? (int)S5_RUN_MAX_MS_LONG : (int)S5_RUN_MAX_MS));

    /* 1) VTC 生成器 720p60（仅 P3b 架构；P3m 无 VTC，时序由 PL axis_to_video 自产）。
     *    P3m 下**绝不访问 0x43C30000**：该地址不存在，误读可能挂总线。 */
#if S5_NO_VTC != 0
    xil_printf("VTC=absent(P3m): PL axis_to_video 自产 720p60，软件不配置 VTC（跳过 12/12 回读检查）\r\n");
#else
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
#endif

    /* 2) 先给两个帧存写入内容：证明“DDR 写 → VDMA 读 → 屏幕”整条通路。
     *    P3m 默认用**确定性测试图**，且 A/B 画同一张（circular 模式下两帧内容不同会造成闪烁）。 */
#if S5_TEST_PATTERN != 0
    S5Display_DeterministicPattern(fb[0]);
    s5_fb_flush(fb[0]);
    S5Display_DeterministicPattern(fb[1]);
    s5_fb_flush(fb[1]);
    xil_printf("TEST PATTERN DRAWN: bars8+border+cross\r\n");
#else
    S5Display_TestPattern(fb[0], 0); /* 棋盘 */
    s5_fb_flush(fb[0]);
    S5Display_TestPattern(fb[1], 1); /* 彩条 */
    s5_fb_flush(fb[1]);
#endif

#if S5_CAMERA != 0
    /* 2b) R-07/P3r：相机采集（可选）。先起 S2MM 把 640×480 BGR888 写进 raw 0x12000000，
     *     显示侧原有四态回退会自动从该块取真实画面；相机失败不影响显示（回退测试图）。 */
#if S5_CAM_DIAG != 0
    /* ---- 诊断 v2（ecam_diag r15）：SCCB 逐字节 trace + 地址扫描 + 寄存器 dump ---- */
    {
        uint32_t pin_b = 0u;
        uint32_t pin_a = 0u;
        uint32_t i;
        uint32_t j;
        uint8_t found[16];
        uint32_t nfound = 0u;
        int has_cam = 0;

        xil_printf("CAM: rst pin before=0x%x (reg 0x%x)\r\n",
                   (unsigned)Xil_In32(S5_CAM_RST_REG), (unsigned)S5_CAM_RST_REG);
        (void)S5Cam_ResetSeq(&s5_cam_bus_diag, &pin_b, &pin_a);
        xil_printf("CAM: reset seq: 1(release) %d ms -> 0(assert) %d ms -> 1(release) %d ms; pin before=0x%x after=0x%x\r\n",
                   (int)S5_CAM_RST_HOLD_MS, (int)S5_CAM_RST_HOLD_MS, (int)S5_CAM_RST_HOLD_MS,
                   (unsigned)pin_b, (unsigned)pin_a);
#if S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_PS
        {
            S5CamRegDump rd0;
            uint32_t rst_b = 0u;
            uint32_t rst_a = 0u;
            uint32_t aper;
            int prc;

            S5Cam_RegDump(&s5_cam_bus_diag, &rd0);
            xil_printf("CAM: i2c cr_raw_before=0x%x sr=0x%x impr=0x%x (init 前原始状态)\r\n",
                       (unsigned)rd0.cr, (unsigned)rd0.sr, (unsigned)rd0.impr);
            aper = S5Cam_SlcrRead(&s5_cam_bus_diag, S5_CAM_SLCR_APER);
            xil_printf("CAM: slcr aper(0xF800012C)=0x%x I2C0_CLKACT(bit18)=%d\r\n",
                       (unsigned)aper, (aper & (1u << 18)) ? 1 : 0);
            rst_b = S5Cam_SlcrRead(&s5_cam_bus_diag, S5_CAM_SLCR_I2C_RST);
            xil_printf("CAM: slcr i2c_rst before=0x%x (I2C0 in reset=%d)\r\n",
                       (unsigned)rst_b, (rst_b & 1u) ? 1 : 0);
            prc = S5Cam_I2cRstPulse(&s5_cam_bus_diag, 1u, &rst_b, &rst_a);
            xil_printf("CAM: slcr i2c_rst pulse: before=0x%x after=0x%x release_ok=%d\r\n",
                       (unsigned)rst_b, (unsigned)rst_a, (prc == 0) ? 1 : 0);
        }
#else
        xil_printf("CAM: backend=gpio_sccb ctrl=0x43C80000 stat=0x43C80008 (PS I2C0/SLCR 本版不用)\r\n");
#endif

        {
            uint32_t cr = 0u;
            uint32_t sr = 0u;
            uint32_t div = 0u;
            int rc = S5Cam_I2cInitEx(&s5_cam_bus_diag, S5_CAM_I2C_CLK_HZ, &cr, &sr, &div);
            uint32_t da = (div >> 8) & 0xFFu;
            uint32_t db = div & 0xFFu;
            uint32_t fscl = (uint32_t)S5_CAM_I2C_CLK_HZ / (22u * (da + 1u) * (db + 1u));

            xil_printf("CAM: backend=%s levels=0x%x (SCL=%d SDA=%d) half_us=%d\r\n",
                       (S5_CAM_I2C_BACKEND == S5_CAM_I2C_BACKEND_GPIO) ? "gpio_sccb" : "ps_i2c0",
                       (unsigned)sr, (sr & 1u) ? 1 : 0, (sr & 2u) ? 1 : 0,
                       (int)S5_CAM_GPIO_HALF_US);
            xil_printf("CAM: cr_bits MASTER(0x2)=%d RD_WR(0x1)=%d NEA(0x4)=%d ACKEN(0x8)=%d HOLD(0x10)=%d\r\n",
                       (cr & S5_I2C_CR_MS) ? 1 : 0, (cr & S5_I2C_CR_RD_WR) ? 1 : 0,
                       (cr & S5_I2C_CR_NEA) ? 1 : 0, (cr & S5_I2C_CR_ACKEN) ? 1 : 0,
                       (cr & S5_I2C_CR_HOLD) ? 1 : 0);
            xil_printf("CAM: i2c init rc=%d Fpclk=%d div_a=%d div_b=%d Fscl=%d cr=0x%x sr=0x%x\r\n",
                       rc, (int)S5_CAM_I2C_CLK_HZ, (int)da, (int)db, (int)fscl,
                       (unsigned)cr, (unsigned)sr);
        }

        xil_printf("CAM: sccb scan 7bit 0x08..0x77 (per-addr: waddr + read reg 0x300A 1B)\r\n");
        for (i = 0x08u; i <= 0x77u; i++) {
            S5CamTrace tr;
            uint8_t id = 0u;
            int ack = S5Cam_ScanAddr(&s5_cam_bus_diag, (uint8_t)i, &id, &tr);

            if (ack != 0) {
                xil_printf("CAM: scan addr7=0x%02x ack=1 id=0x%02x rc=%d isr=0x%x sr=0x%x\r\n",
                           (unsigned)i, (unsigned)id, tr.rc,
                           (unsigned)tr.final_isr, (unsigned)tr.final_sr);
                if (nfound < 16u) {
                    found[nfound++] = (uint8_t)i;
                }
                if ((uint8_t)i == S5_CAM_SCCB_ADDR) {
                    has_cam = 1;
                }
            }
        }
        xil_printf("CAM: scan result found=%d:", (int)nfound);
        for (i = 0u; i < nfound; i++) {
            xil_printf(" 0x%02x", (unsigned)found[i]);
        }
        xil_printf("\r\n");

        for (j = 0u; j < ((has_cam != 0) ? 2u : 3u); j++) {
            S5CamTrace tr;
            uint8_t b[2] = {0u, 0u};
            int rc;

            if ((has_cam == 0) && (j > 0u)) {
                s5_cam_bus_delay(0, 10000u);
            }
            rc = S5Cam_ReadRegTrace(&s5_cam_bus_diag, S5_CAM_SCCB_ADDR, 0x300Au, b, 2u, &tr);

            for (i = 0u; i < tr.n; i++) {
                const char *nm = (tr.step[i].kind == S5_CAM_TR_START) ? "start/waddr"
                                 : (tr.step[i].kind == S5_CAM_TR_REG_HI) ? "reg_hi"
                                 : (tr.step[i].kind == S5_CAM_TR_REG_LO) ? "reg_lo"
                                 : (tr.step[i].kind == S5_CAM_TR_RSTART) ? "rstart/raddr"
                                 : (tr.step[i].kind == S5_CAM_TR_DATA) ? "data"
                                 : (tr.step[i].kind == S5_CAM_TR_STOP) ? "stop" : "?";

                xil_printf("CAM: try%d step=%s byte=0x%02x isr=0x%x sr=0x%x cr=0x%x addr=0x%x trsz=%d\r\n",
                           (int)(j + 1u), nm, (unsigned)tr.step[i].byte,
                           (unsigned)tr.step[i].isr, (unsigned)tr.step[i].sr,
                           (unsigned)tr.step[i].cr, (unsigned)tr.step[i].addr,
                           (int)tr.step[i].trsz);
            }
            xil_printf("CAM: try%d dump rc=%d isr=0x%x sr=0x%x cr=0x%x addr=0x%x trsz=%d busy=%d b0=0x%02x b1=0x%02x\r\n",
                       (int)(j + 1u), rc, (unsigned)tr.final_isr, (unsigned)tr.final_sr,
                       (unsigned)tr.final_cr, (unsigned)tr.final_addr, (int)tr.final_trsz,
                       ((tr.final_sr & S5_I2C_SR_BUSY) != 0u) ? 1 : 0,
                       (unsigned)b[0], (unsigned)b[1]);
            {
                S5CamRegDump d;
                uint32_t ir;

                S5Cam_RegDump(&s5_cam_bus_diag, &d);
                ir = tr.final_isr;
                xil_printf("CAM: try%d isr_bits COMP=%d TO=%d NACK=%d ARB=%d RXOVR=%d TXOVR=%d RAW=0x%x\r\n",
                           (int)(j + 1u), (ir & S5_I2C_ISR_COMP) ? 1 : 0,
                           (ir & S5_I2C_ISR_TO) ? 1 : 0, (ir & S5_I2C_ISR_NACK) ? 1 : 0,
                           (ir & S5_I2C_ISR_ARB) ? 1 : 0, (ir & S5_I2C_ISR_RX_OVR) ? 1 : 0,
                           (ir & S5_I2C_ISR_TX_OVR) ? 1 : 0, (unsigned)ir);
                xil_printf("CAM: try%d sr_bits BA=%d RXDV=%d TXDV=%d BUSY=%d RAW=0x%x\r\n",
                           (int)(j + 1u), (d.sr & S5_I2C_SR_BUSY) ? 1 : 0,
                           (d.sr & S5_I2C_SR_RXDV) ? 1 : 0, (d.sr & S5_I2C_SR_TXDV) ? 1 : 0,
                           (d.busy != 0u) ? 1 : 0, (unsigned)d.sr);
                xil_printf("CAM: try%d impr=0x%x (controller version)\r\n",
                           (int)(j + 1u), (unsigned)d.impr);
            }
            xil_printf("CAM: try%d acks=addr:%d hi:%d lo:%d rstart:%d (1=ACK)\r\n",
                       (int)(j + 1u), (tr.acks & 1u) ? 1 : 0, (tr.acks & 2u) ? 1 : 0,
                       (tr.acks & 4u) ? 1 : 0, (tr.acks & 8u) ? 1 : 0);
            if (rc == 0) {
                if ((b[0] == 0x56u) && (b[1] == 0x40u)) {
                    xil_printf("CAM: try%d chipid=0x5640 OK\r\n", (int)(j + 1u));
                } else {
                    xil_printf("CAM: try%d FAIL sub=-7 data_anomaly chipid=0x%02x%02x\r\n",
                               (int)(j + 1u), (unsigned)b[0], (unsigned)b[1]);
                }
            } else {
                xil_printf("CAM: try%d FAIL sub=%d stage=%s\r\n", (int)(j + 1u), rc,
                           (rc == -2) ? "txdv_timeout" : (rc == -3) ? "nack"
                           : (rc == -4) ? "arb_lost" : (rc == -5) ? "rx_timeout" : "comp_timeout");
            }
        }
        {
            S5CamInfo vi;
            S5CamVdmaTrace vt;
            uint32_t k;
            int vrc;

            (void)vi;
            vrc = S5CamVdma_Config(&s5_cam_bus_diag, &vi, &vt);
            xil_printf("CAM: vdma base=0x%x config_rc=%d cand=%d first_bad=%d\r\n",
                       (unsigned)vt.base, vrc, (int)vt.cand, vt.first_bad);
            for (k = 0u; k < vt.n; k++) {
                xil_printf("CAM: vdma step %-18s off=0x%02x w=0x%x r=0x%x expect=0x%x ok=%d\r\n",
                           vt.step[k].name, (unsigned)vt.step[k].off,
                           (unsigned)vt.step[k].wval, (unsigned)vt.step[k].rval,
                           (unsigned)vt.step[k].expect, vt.step[k].ok ? 1 : 0);
            }
            xil_printf("CAM: vdma SR=0x%x halted=%d err=0x%x frmcnt=%d\r\n",
                       (unsigned)vi.vdma_sr, (vi.vdma_sr & S5_CAM_SR_HALTED) ? 1 : 0,
                       (unsigned)(vi.vdma_sr & S5_CAM_SR_ERR_ALL),
                       (int)((vi.vdma_sr & S5_CAM_SR_FRMCNT_MASK) >> S5_CAM_SR_FRMCNT_SHIFT));
            if (vrc == 0) {
                const uint32_t delays[3] = {0u, 20000u, 100000u};
                const char *tags[3] = {"started", "+20ms", "+100ms"};
                uint32_t base_fc = 0u;

                (void)S5CamVdma_Start(&s5_cam_bus_diag);
                for (j = 0u; j < 3u; j++) {
                    uint32_t sr = 0u;
                    int h = 0;
                    uint32_t err = 0u, fc = 0u;

                    if (delays[j] != 0u) {
                        s5_cam_bus_delay(0, delays[j]);
                    }
                    (void)S5CamVdma_Status(&s5_cam_bus_diag, &sr);
                    S5Cam_SrDecode(sr, &h, &err, &fc);
                    if (j == 0u) {
                        base_fc = fc;
                    }
                    xil_printf("CAM: vdma %s SR=0x%x halted=%d err=0x%x frmcnt=%d (+%d)\\r\\n",
                               tags[j], (unsigned)sr, h, (unsigned)err, (int)fc,
                               (int)(fc - base_fc));
                }
            }
            if (vt.first_bad >= 0) {
                xil_printf("CAM: VDMA FIRST_BAD name=%s off=0x%02x expect=0x%x actual=0x%x\r\n",
                           vt.step[vt.first_bad].name, (unsigned)vt.step[vt.first_bad].off,
                           (unsigned)vt.step[vt.first_bad].expect,
                           (unsigned)vt.step[vt.first_bad].rval);
            }
        }

        {
            S5CamInfo ci;
            int rc2;
            uint64_t t0;
            uint32_t t_ms;
            uint32_t gpio_b;
            uint32_t gpio_a;
            uint32_t gpio_c;
            uint8_t v3008 = 0u, v3035 = 0u, v3034 = 0u, v4300 = 0u, v460c = 0u;
            uint8_t v3808 = 0u, v3809 = 0u, v380a = 0u, v380b = 0u, v380e = 0u, v380f = 0u;

            xil_printf("CAM: init table entries=%d (stage3 frozen table)\r\n",
                       (int)S5Cam_InitTableCount());
            gpio_b = Xil_In32(0x43C70000u);
            xil_printf("CAM: vdma cold VER=0x%x CR=0x%x SR=0x%x\r\n",
                       (unsigned)Xil_In32(0x43C6002Cu), (unsigned)Xil_In32(0x43C60030u),
                       (unsigned)Xil_In32(0x43C60034u));
            t0 = S5Ticks_Now();
            rc2 = s5_cam_bringup(&ci);
            xil_printf("CAM: vdma hot  VER=0x%x CR=0x%x SR=0x%x\r\n",
                       (unsigned)Xil_In32(0x43C6002Cu), (unsigned)Xil_In32(0x43C60030u),
                       (unsigned)Xil_In32(0x43C60034u));
            t_ms = (uint32_t)((S5Ticks_Now() - t0) / (S5_GT_HZ / 1000u));
            gpio_a = Xil_In32(0x43C70000u);
            xil_printf("CAM: bringup rc=%d stage=%s elapsed_ms=%d\r\n", rc2, s5_cam_stage_name(rc2), (int)t_ms);
            xil_printf("CAM: ip warmup wait=%d ms elapsed=%d ms (vendor IP 300M PCLK power-up; PCLK=42MHz needs 7.14s)\r\n",
                       (int)S5_CAM_IP_WARMUP_MS, (int)S5Cam_WarmupMs);
            xil_printf("CAM: init OK capture=%dx%d stride=%d frame=%d (route B 2x subsample + 2x horizontal downsample)\r\n",
                       (int)S5_RAW_FRAME_W, (int)S5_RAW_FRAME_H, (int)S5_RAW_FRAME_STRIDE,
                       (int)S5_RAW_FRAME_BYTES);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3008u, &v3008);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3035u, &v3035);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3034u, &v3034);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x4300u, &v4300);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x460cu, &v460c);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3808u, &v3808);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3809u, &v3809);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Au, &v380a);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Bu, &v380b);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Eu, &v380e);
            (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Fu, &v380f);
            xil_printf("CAM: reg 0x3008=0x%02x 0x3035=0x%02x 0x3034=0x%02x 0x4300=0x%02x 0x460C=0x%02x\r\n",
                       (unsigned)v3008, (unsigned)v3035, (unsigned)v3034, (unsigned)v4300, (unsigned)v460c);
            xil_printf("CAM: reg DVPHO=0x%02x%02x DVPVO=0x%02x%02x VTS=0x%02x%02x\r\n",
                       (unsigned)v3808, (unsigned)v3809, (unsigned)v380a, (unsigned)v380b,
                       (unsigned)v380e, (unsigned)v380f);
            s5_cam_bus_delay(0, 50000u);
            gpio_c = Xil_In32(0x43C70000u);
            xil_printf("CAM: CAM_GPIO before=0x%x after=0x%x +50ms=0x%x\r\n",
                       (unsigned)gpio_b, (unsigned)gpio_a, (unsigned)gpio_c);
            {
                S5CamRegCheck chk[16];
                uint32_t nchk = 0u, bad = 0u, q;
                uint8_t r300e = 0u, r3017 = 0u, r3018 = 0u, r3008f = 0u;

                (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x300Eu, &r300e);
                (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3017u, &r3017);
                (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3018u, &r3018);
                (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3008u, &r3008f);
                (void)S5Cam_CheckKeyRegs(&s5_cam_bus_diag, chk, 16u, &nchk, &bad);
                for (q = 0u; q < nchk; q++) {
                    xil_printf("CAM: reg 0x%04x read=0x%02x expect=0x%02x ok=%d\r\n",
                               (unsigned)chk[q].reg, (unsigned)chk[q].read,
                               (unsigned)chk[q].expect, chk[q].ok ? 1 : 0);
                }
                xil_printf("CAM: key regs checked=%d mismatches=%d (0=all match)\r\n",
                           (int)nchk, (int)bad);
                {
                    uint8_t a3814 = 0u, a3815 = 0u, a380c = 0u, a380d = 0u;
                    uint8_t a380e = 0u, a380f = 0u, a3035 = 0u, a3036 = 0u;
                    uint8_t a3037 = 0u, a3108 = 0u;
                    uint32_t hts, vts, thz;

                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3814u, &a3814);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3815u, &a3815);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Cu, &a380c);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Du, &a380d);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Eu, &a380e);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x380Fu, &a380f);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3035u, &a3035);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3036u, &a3036);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3037u, &a3037);
                    (void)S5Cam_ReadReg(&s5_cam_bus_diag, 0x3108u, &a3108);
                    hts = ((uint32_t)a380c << 8) | (uint32_t)a380d;
                    vts = ((uint32_t)a380e << 8) | (uint32_t)a380f;
                    thz = S5Cam_TheoryPclk(hts, vts, 15u);
                    xil_printf("CAM: v14 subsample 0x3814=0x%02x 0x3815=0x%02x (expect 0x31 = 2x route B)\r\n",
                               (unsigned)a3814, (unsigned)a3815);
                    xil_printf("CAM: v14 HTS=0x%02x%02x(%d) VTS=0x%02x%02x(%d) offsets 0x3810-13=0\r\n",
                               (unsigned)a380c, (unsigned)a380d, (int)hts,
                               (unsigned)a380e, (unsigned)a380f, (int)vts);
                    xil_printf("CAM: v14 PLL 0x3035=0x%02x 0x3036=0x%02x 0x3037=0x%02x 0x3108=0x%02x\r\n",
                               (unsigned)a3035, (unsigned)a3036, (unsigned)a3037, (unsigned)a3108);
                    xil_printf("CAM: v14 theory HTS*VTS*15fps = %d Hz (%.2f MHz); build9 measured PCLK=40.35 MHz\r\n",
                               (int)thz, (double)thz / 1000000.0);
                }
                {
                    uint64_t tf0, tf1;
                    uint32_t c0, p0, h0, v0, c1, p1, h1, v1;
                    uint32_t dv, dp, dh, dt_us, dt_ms, dvn;

                    c0 = Xil_In32(0x43C70000u);
                    p0 = Xil_In32(0x43C90000u);
                    h0 = Xil_In32(0x43C90008u);
                    v0 = Xil_In32(0x43CA0000u);
                    tf0 = S5Ticks_Now();
                    s5_cam_bus_delay(0, 500000u);
                    tf1 = S5Ticks_Now();
                    c1 = Xil_In32(0x43C70000u);
                    p1 = Xil_In32(0x43C90000u);
                    h1 = Xil_In32(0x43C90008u);
                    v1 = Xil_In32(0x43CA0000u);
                    dt_us = (uint32_t)(((tf1 - tf0) * 1000000u) / S5_GT_HZ);
                    dt_ms = dt_us / 1000u;
                    dv = v1 - v0; /* 32 位无符号差，允许回绕 */
                    dp = p1 - p0;
                    dh = h1 - h0;
                    dvn = (dv == 0u) ? 0u : (dh / dv);
                    xil_printf("CAM: flow dt=%dms dVSYNC=%d dPCLK=%d dHREF=%d pixels_per_frame=%d pclk_khz=%d\r\n",
                               (int)dt_ms, (int)dv, (int)dp, (int)dh, (int)dvn,
                               (dt_ms == 0u) ? 0 : (int)(dp / dt_ms));
                    xil_printf("CAM: flow snaps cam=%d->%d pclk=%d->%d href=%d->%d vsync=%d->%d\r\n",
                               (int)c0, (int)c1, (int)p0, (int)p1, (int)h0, (int)h1, (int)v0, (int)v1);
                }

/* v29：改用 Xilinx XAxiVdma 驱动（与阶段3 相同路径），打印每步 XST_* 返回码。 */
            {
                XAxiVdma vdma;
                XAxiVdma_DmaSetup ws = {0};
                UINTPTR buf[1];
                volatile uint32_t *crp = (volatile uint32_t *)0x43C60030u;
                volatile uint32_t *srp = (volatile uint32_t *)0x43C60034u;
                volatile uint32_t *rawp7 = (volatile uint32_t *)0x12000000u;
                int st_cfg, st_conf, st_addr, st_start;
                uint32_t k, fc;

                xil_printf("CAM: v29 enter\r\n");
                st_cfg = XAxiVdma_CfgInitialize(&vdma, &s5_vdma_cfg, s5_vdma_cfg.BaseAddress);
                xil_printf("drv: CfgInitialize=%d (XST_SUCCESS=%d)\r\n", st_cfg, XST_SUCCESS);
                ws.VertSizeInput = 720;
                ws.HoriSizeInput = 3840;
                ws.Stride = 3840;
                ws.FrameDelay = 0;
                ws.EnableCircularBuf = 1;
                ws.EnableSync = 1;
                ws.PointNum = 0;
                ws.EnableFrameCounter = 0;
                ws.FixedFrameStoreAddr = 0;
                st_conf = XAxiVdma_DmaConfig(&vdma, XAXIVDMA_WRITE, &ws);
                xil_printf("drv: DmaConfig=%d (VERT=%d HORI=%d STRIDE=%d circ=%d sync=%d)\r\n",
                           st_conf, ws.VertSizeInput, ws.HoriSizeInput, ws.Stride,
                           ws.EnableCircularBuf, ws.EnableSync);
                buf[0] = 0x12000000u;
                st_addr = XAxiVdma_DmaSetBufferAddr(&vdma, XAXIVDMA_WRITE, buf);
                xil_printf("drv: DmaSetBufferAddr=%d buf0=0x%x\r\n", st_addr, (unsigned)buf[0]);
                st_start = XAxiVdma_DmaStart(&vdma, XAXIVDMA_WRITE);
                xil_printf("drv: DmaStart=%d\r\n", st_start);
                s5_cam_bus_delay(0, 1000000u);
                fc = ((*srp) & S5_CAM_SR_FRMCNT_MASK) >> S5_CAM_SR_FRMCNT_SHIFT;
                xil_printf("after1s: cr=%08x sr=%08x frmcnt=%u\r\n",
                           (unsigned)*crp, (unsigned)*srp, (unsigned)fc);
                Xil_DCacheInvalidateRange((UINTPTR)0x12000000u, 64u);
                xil_printf("ddr 0x12000000:");
                for (k = 0u; k < 16u; k++) {
                    xil_printf(" %08x", (unsigned)rawp7[k]);
                }
                xil_printf("\r\n");
                xil_printf("CAM: v29 exit\r\n");
            }
                xil_printf("CAM: final 0x3008=0x%02x (expect 0x02); 0x300E=0x%02x MIPI_bit6=%d; 0x3017=0x%02x 0x3018=0x%02x DVP_pads_en=%d\r\n",
                           (unsigned)r3008f, (unsigned)r300e, (int)((r300e >> 6) & 1u),
                           (unsigned)r3017, (unsigned)r3018,
                           (((r3017 != 0u) && (r3018 != 0u)) ? 1 : 0));


            }
        }

    }
#else
    {
        S5CamInfo cam_info;
        int cam_rc = s5_cam_bringup(&cam_info);

        cam_ok = (cam_rc == 0) ? 1u : 0u;
        if (cam_rc != 0) {
            xil_printf("CAM: FAIL rc=%d stage=%s (rc map: -10 chipid/-11 sccb/-12 overlay/-13 regchk/-17 table/-18 stream_on/-19 stream_off/-20 timing/-21 clear_reset/-22 start_rs)\r\n",
                       cam_rc, s5_cam_stage_name(cam_rc));
        }
    }
#endif
#endif /* S5_CAMERA */

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

    /* 3c) 确定性测试图保持窗口（P3m 目视判读）：VDMA 已启动、两帧存内容相同，
     *     保持 S5_TEST_PATTERN_HOLD_MS，观察是否有雪花/闪烁/撕裂/红蓝互换/行错位。
     *     期间不写帧存（CPU 不抢带宽），因此这也是一个“纯净出流”检查。 */
#if S5_TEST_PATTERN != 0
    {
        uint64_t th0 = S5Ticks_Now();
        uint32_t hold_err = 0;

        xil_printf("TEST PATTERN HOLD: %d ms (VDMA running, CPU idle)\r\n",
                   (int)S5_TEST_PATTERN_HOLD_MS);
        while (S5Ticks_ToMs(S5Ticks_Now() - th0) < (uint64_t)S5_TEST_PATTERN_HOLD_MS) {
            if (dma_state != S5_DMA_OFF) {
                uint32_t hs = S5Vdma_Status(&dma);

                if ((hs & S5_VDMA_SR_ERR_ALL) != 0u) {
                    hold_err++;
                    dma_state = S5_DMA_ERR;
                }
            }
        }
        xil_printf("TEST PATTERN HOLD done, vdma_err=%d\r\n", (int)hold_err);
    }
#endif

#if S5_PRODUCER != 0
    /* 生产者模式：主循环开始前写 session 起始标记（frame_id=0），之后每帧写真实时间戳结果块。
     * 放在测试图保持窗口之后，保证消费端第一帧读到的 cap 是"刚刚"，不会因 2 s 保持而误判超龄。 */
    s5_prod_session_start();
#endif

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
        char res[384];
        const uint32_t run_frames = (S5_LONG_RUN != 0) ? 0xFFFFFFFFu
                                   : ((S5_IDLE_PROBE != 0) ? (uint32_t)S5_IDLE_PROBE_FRAMES
                                                           : (uint32_t)S5_RUN_FRAMES);
        const uint64_t run_ms = (S5_LONG_RUN != 0) ? (uint64_t)S5_RUN_MAX_MS_LONG
                                                   : (uint64_t)S5_RUN_MAX_MS;
        uint64_t last_tick_ms = 0u;
#if S5_PRODUCER != 0
        uint64_t t_frame_cap = 0u; /* 生产者模式：本帧开始渲染时刻（cap 时间戳） */
#endif
        /* r06c 空闲测速状态 */
        uint32_t idle_probed = 0u;
        uint32_t fps_dis_idle = 0u;
        uint32_t idle_period_us = 0u;
        uint64_t t_render_end = 0u;

        while ((frames < run_frames) &&
               (S5Ticks_ToMs(S5Ticks_Now() - t_start) < run_ms)) {
#if S5_PRODUCER != 0
            t_frame_cap = s5_prod_now(); /* cap = 本帧开始渲染时刻（真实全局定时器） */
#endif
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
                        S5Real_BgrToCanvasDecim((const uint8_t *)S5_RAW_FRAME_BASE, s5_cam,
                                                S5_RAW_OUT_W, S5_RAW_OUT_H,
                                                S5_RAW_DECIM_X, S5_RAW_DECIM_Y, S5_RAW_FRAME_STRIDE);
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
                        S5Real_BgrToCanvasDecim((const uint8_t *)S5_RAW_FRAME_BASE, s5_cam,
                                                S5_RAW_OUT_W, S5_RAW_OUT_H,
                                                S5_RAW_DECIM_X, S5_RAW_DECIM_Y, S5_RAW_FRAME_STRIDE);
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
#if S5_CAMERA != 0
            if ((cam_ok != 0u) && ((frames % 60u) == 0u)) {
                static S5CamBus cam_bus2 = {0, s5_cam_bus_rd, s5_cam_bus_wr, s5_cam_bus_delay, app_now_ms};
                uint32_t cam_sr = 0u;
                int cs = S5CamVdma_Status(&cam_bus2, &cam_sr);

                xil_printf("CAM: sr=0x%x%s frames=%d\r\n", (unsigned)cam_sr,
                           (cs == 0) ? "" : " (ERR)", (int)((cam_sr >> 16) & 0xFFu));
            }
#endif
            if ((frames % 60u) == 0u) {
                xil_printf("S5DISP frame=%d lat=%d age=%d st=%x sr=%x src=%s nbox=%d\r\n",
                           (int)frames, (int)info.latency_ms, (int)info.age_ms,
                           (unsigned)info.status, (unsigned)S5Vdma_Status(&dma),
                           S5Src_Name(src_kind), (int)info.det_count);
            }
#if S5_PRODUCER != 0
            /* 4.45 生产者 v2 发布：模拟检测框（源 640×480）+ 真实时间戳 + 单调 seq + sidecar/seqlock */
            if ((frames % (uint32_t)S5_PROD_EVERY_N) == 0u) {
                S5FrameInfo prod_info;

                S5Sim_NextFrame(&prod_info); /* 仅取 det[]/det_count，不使用其模拟时间戳 */
                s5_prod_emit(t_frame_cap, prod_info.det, prod_info.det_count);
            }
            /* 4.46 消费者视角校验（每 60 帧一行）：seqlock 协议 + 业务状态映射 */
            if ((frames % 60u) == 0u) {
                S5PubView v = {0};
                S5PubReadTrace tr;
                uint32_t age_pub = 0u;
                int crc = s5_pub_consume(s5_prod_now(), &v, &age_pub, &tr);

                /* v5（E6-A 取证）：正常行只在 s1==s2 且为偶（协议成功条件）时输出，
                 * 并附带本次消费的两次锁读值与重试次数；发生重试另打 RETRY 行，超限打 TIMEOUT 行。 */
                if (crc == 0) {
                    if (tr.retries != 0u) {
                        xil_printf("S5CONS RETRY seq=%d attempt=%d s1=%d s2=%d\r\n",
                                   (int)v.result_seq, (int)tr.attempts,
                                   (int)tr.s1_last, (int)tr.s2_last);
                    }
                    xil_printf("S5CONS sid=%d seq=%d n=%d status=0x%x age_pub=%d state=%s seqlock=%d s1=%d s2=%d retries=%d\r\n",
                               (int)v.session_id, (int)v.result_seq, (int)v.n_dets, (unsigned)v.status,
                               (int)age_pub, S5Pub_StateName(S5Pub_BizState(&v, age_pub)),
                               (int)v.seqlock, (int)tr.s1_last, (int)tr.s2_last, (int)tr.retries);
                } else if (crc == -2) {
                    xil_printf("S5CONS sidecar absent (旧生产者, 非原子路径)\r\n");
                } else {
                    xil_printf("S5CONS TIMEOUT seq=%d attempt=%d s1=%d s2=%d\r\n",
                               (int)v.result_seq, (int)tr.attempts,
                               (int)tr.s1_last, (int)tr.s2_last);
                }
            }
#endif
        /* 4.5 空闲测速（r06c，G3-A 定位）：渲染满 S5_IDLE_PROBE_FRAMES 帧后**停止写帧存**，
             *     让 VDMA 继续从最后两帧读（显示不中断），在 S5_IDLE_PROBE_MS 窗口内测 READSTR 切换周期。
             *     判据：空闲≈60 而渲染时 45–52 ⇒ CPU 写 DDR 抢带宽；两者都低 ⇒ VDMA/HP2 通路本身不够。 */
            if ((S5_IDLE_PROBE != 0) && (idle_probed == 0u) &&
                (frames >= (uint32_t)S5_IDLE_PROBE_FRAMES)) {
                uint64_t ti0 = S5Ticks_Now();
                uint32_t last_cs = S5Vdma_CurrentReadStore(&dma);
                uint32_t edges = 0u;
                uint64_t t_first = 0u;
                uint64_t t_last = 0u;
                uint32_t poll = 0u;
                uint64_t idle_ms = 0u;

                idle_probed = 1u;
                t_render_end = ti0; /* fps_upd 只按“渲染阶段”计，不含空闲 3 s */
                xil_printf("S5DISP idle start: stop rendering, VDMA keeps running %d ms\r\n",
                           (int)S5_IDLE_PROBE_MS);
                do {
                    uint32_t cs = S5Vdma_CurrentReadStore(&dma);

                    if (cs != last_cs) {
                        uint64_t now_ticks = S5Ticks_Now();

                        last_cs = cs;
                        if (edges == 0u) {
                            t_first = now_ticks;
                        }
                        t_last = now_ticks;
                        edges++;
                        vcnt_sw++; /* 空闲期间 VDMA 仍在消耗帧，vcnt 照常累计 */
                    }
                    poll++;
                    if ((poll & 0x3FFu) == 0u) {
                        sr = S5Vdma_Status(&dma);
                        if ((sr & S5_VDMA_SR_ERR_ALL) != 0u) {
                            vdma_err++;
                            dma_state = S5_DMA_ERR;
                        }
                    }
                    idle_ms = S5Ticks_ToMs(S5Ticks_Now() - ti0);
                } while (idle_ms < (uint64_t)S5_IDLE_PROBE_MS);

                if ((edges >= 2u) && (t_last > t_first)) {
                    uint64_t period = (t_last - t_first) / (uint64_t)(edges - 1u);

                    idle_period_us = (uint32_t)((period * 1000000u) / S5_GT_HZ);
                }
                fps_dis_idle = (idle_ms > 0u)
                                   ? (uint32_t)(((uint64_t)edges * 1000u) / idle_ms)
                                   : 0u;
                xil_printf("S5DISP idle fps_dis=%d period_us=%d frames=%d vcnt=%d err=%d\r\n",
                           (int)fps_dis_idle, (int)idle_period_us, (int)frames,
                           (int)vcnt_sw, (int)vdma_err);
                break; /* 测速完成即收尾，进入 RESULT */
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
            /* fps_upd 仅按**渲染阶段**计（空闲测速的 3 s 不计入，否则会冤枉软件） */
            uint64_t elapsed_ms = (t_render_end != 0u)
                                      ? S5Ticks_ToMs(t_render_end - t_start)
                                      : S5Ticks_ToMs(S5Ticks_Now() - t_start);

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
        /* r06c：空闲测速结果（仅 S5_IDLE_PROBE=1 时有值；未测为 0，不虚填） */
        st.fps_dis_idle = fps_dis_idle;
        st.idle_period_us = idle_period_us;
        /* G3：box_crc = 绘制所用框（映射后坐标）；fb_crc = 显示用 framebuffer（0x20000000 那帧）。
         * 两者都在**最后一帧写完后**算一次；fb_crc 先 invalidate，确保读的是 DDR 里的最新像素。 */
        st.box_crc = S5Display_BoxesCrc(last_det, last_det_count);
        s5_invalidate((const void *)S5_FB_A_BASE, S5_FB_BYTES);
        st.fb_crc = S5Display_Crc32((const void *)S5_FB_A_BASE, S5_FB_BYTES);
        /* underflow 像素计数（AXI GPIO 只读）：
         *   P3n：单寄存器（0x43C10000 = 累计值）→ uf_total=该值，uf_frame=0；
         *   P3p：0x43C10000 = 本帧欠载（每 vsync 归零），0x43C10008 = 累计(sticky)。 */
#if (S5_UF_FRAME_REG == S5_UF_TOTAL_REG)
        uf_total = (uint32_t)Xil_In32(S5_UF_FRAME_REG);
        uf_frame = 0u;
#else
        uf_frame = (uint32_t)Xil_In32(S5_UF_FRAME_REG);
        uf_total = (uint32_t)Xil_In32(S5_UF_TOTAL_REG);
#endif
        st.uf_frame = uf_frame;
        st.uf_total = uf_total;
        st.uf_pix = uf_total; /* 兼容旧字段 */
        xil_printf("UF GPIO frame@%x=%d total@%x=%d\r\n",
                   S5_UF_FRAME_REG, (int)uf_frame, S5_UF_TOTAL_REG, (int)uf_total);

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

        xil_printf("S5DISP done frames=%d vcnt=%d(sw) vdma_err=%d idle_fps=%d idle_us=%d\r\n",
                   (int)st.frames, (int)st.vcnt, (int)st.vdma_err,
                   (int)st.fps_dis_idle, (int)st.idle_period_us);
        S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
        xil_printf("%s\r\n", res);
    }

    return 0;
}

#endif /* !S5_HOST_TEST */


