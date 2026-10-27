/* S5-T01 P1：PS 合成视频源 + 软件叠框（零新增 PL）。
 *
 * 无传感器、无 S2MM：本函数被调用后**永不返回**，原 main 后续的 S2MM/传感器路径不会执行。
 * 几何：框像素矩形由宿主端 `gen_overlay_cases.py` 用**冻结参考实现**算好嵌入；板上无逆映射逻辑。
 *
 * 修订：
 *   r02 D-1 平滑斜坡 / D-2 标签避让+HUD 置顶
 *   r03 §3 可信帧事件（XScuGic ID61=MM2S 帧完成、ID62=VTC）+ 四 FPS 口径
 *   r04 VTC 逐位计数定标（实测每帧 2 次事件）
 *   r05 §5.4 HUD **13 字段**（缺失值 NA，不用 0 伪装）+ §4 的 **≥100 帧消费**（五元组）
 *       + T5-11 故障计数（warm/drop/timeout/dup/ooo/stale）+ HUD 遮挡像素量化
 *
 * 模式（编译期）：
 *   S5_SINGLE_CASE=N>0  只常显用例 N（拍照/数值核对）
 *   S5_FRAMES_MODE=1    跑 120 帧结果流（五元组日志 + 计数），循环执行（可用于 30 分钟长跑）
 * 默认：6 用例循环
 *
 * 字节序：DDR 内 B,G,R（阶段3 证据）；背景灰度故与字节序无关。
 */

#include "xil_printf.h"
#include "xil_cache.h"
#include "xtime_l.h"
#include "xil_types.h"
#include "xil_exception.h"
#include "xparameters.h"
#include "xaxivdma.h"
#include "xscugic.h"
#include "display_ctrl.h"
#include "sleep.h"
#include <string.h>
#include "s5_overlay_cases.h"

/* S5-T02 板上动态映射（可选；默认 0 = 既有验收路径逐字节不变）。
 * 开启后几何不再来自宿主预计算：裁剪/像素索引/2px 居中边框/标签锚点全部由 C 核心计算；
 * 核心与 verification/s5_display_geometry_reference.py（S5A-G0-v2）逐字镜像。 */
#ifndef S5_DYNAMIC_MAP
#define S5_DYNAMIC_MAP 0
#endif

#if S5_DYNAMIC_MAP
/* 前置声明：色表定义在本文件后部，动态映射诊断需在此处引用 */
static const u8 S5_CLASS_COLOR[5][3];
#include "s5_dynamic_map.h"
static s5d_frame_result s5dm_res;
static s5d_counters s5dm_ctr;
static u32 s5dm_last_case = 0xFFFFFFFFu;

static void s5dm_run_case(const s5_case_t *c)
{
    s5d_frame f;
    const char *texts[S5D_MAX_BOXES];
    int tw[S5D_MAX_BOXES], th[S5D_MAX_BOXES];
    int i;
    memset(&f, 0, sizeof(f));
    f.frame_id = c->id;
    f.displayed_frame_id = c->id;
    f.result_seq = c->id;
    f.state = "OK";
    f.stale_flag = c->stale ? 1 : 0;
    /* 时钟口径：板上无真实采集/推理时间，用固定虚拟基准并在产物中显式声明（不得当实测） */
    f.capture_time_ns = 1000000000LL;
    f.result_time_ns = f.capture_time_ns + 500000LL;
    f.overlay_commit_ns = f.result_time_ns + 1000000LL;
    f.nbox = (int)c->nbox;
    for (i = 0; i < f.nbox; i++) {
        f.boxes[i].class_id = c->boxes[i].cls;
        f.boxes[i].score = 0.5;
        f.boxes[i].xyxy.x1 = (double)c->boxes[i].nx1;
        f.boxes[i].xyxy.y1 = (double)c->boxes[i].ny1;
        f.boxes[i].xyxy.x2 = (double)c->boxes[i].nx2;
        f.boxes[i].xyxy.y2 = (double)c->boxes[i].ny2;
        texts[i] = c->boxes[i].label;
        tw[i] = S5_GLYPH_ADV * S5_LABEL_SCALE * (int)strlen(c->boxes[i].label);
        th[i] = S5_GLYPH_H * S5_LABEL_SCALE;
    }
    if (s5d_process_frame(&f, S5_CANVAS_W, S5_CANVAS_H, texts, tw, th, f.nbox,
                          &s5dm_res, &s5dm_ctr) != S5D_OK) {
        xil_printf("S5DM_ERR id=%u\r\n", (unsigned)c->id);
        return;
    }
    if (c->id != s5dm_last_case) {
        xil_printf("S5DM id=%u nbox=%d stale=%d reason=%s age_frame_ns=%d zero_area=%u\r\n",
                   (unsigned)c->id, s5dm_res.nbox_drawn, (int)s5dm_res.stale.stale_effective,
                   s5dm_res.stale.reason, (int)s5dm_res.stale.age_frame_ns,
                   (unsigned)s5dm_res.zero_area_dropped);
        for (i = 0; i < s5dm_res.nbox_drawn; i++) {
            s5d_drawn_box *d = &s5dm_res.drawn[i];
            const u8 *dbg_rgb = S5_CLASS_COLOR[c->boxes[i].cls % 5];
            xil_printf("S5DM_B id=%u i=%d rect=%d,%d,%d,%d px=%d anchor=%d,%d pl=%s\r\n",
                       (unsigned)c->id, i, d->rect.x1, d->rect.y1, d->rect.x2, d->rect.y2,
                       d->border_pixels, d->label_x, d->label_y, d->label_placement);
            /* S5DM_B2：自报本框实际使用的 cls 与 RGB（用于与送显缓冲逐像素对齐定案） */
            xil_printf("S5DM_B2 id=%u i=%d cls=%u cls_id=%d rgb=%u,%u,%u core_cls=%d\r\n",
                       (unsigned)c->id, i, (unsigned)(c->boxes[i].cls % 5),
                       (int)c->boxes[i].cls, (unsigned)dbg_rgb[0], (unsigned)dbg_rgb[1],
                       (unsigned)dbg_rgb[2], d->class_id);
        }
        s5dm_last_case = c->id;
    }
}
#endif

#define S5_MM2S_CR_ADDR 0x43000000U
#define S5_MM2S_SR_ADDR 0x43000004U
#define S5_MM2S_FRMCNT_BIT 0x00001000U
#define S5_MM2S_FRMCNT_IRQ_EN 0x00001000U
#define S5_MM2S_FRMCNT_THRESH_SHIFT 16U
#define S5_VTC_BASE 0x43C00000U
#define S5_VTC_ISR_ADDR (S5_VTC_BASE + 0x04U)
#define S5_VTC_IER_ADDR (S5_VTC_BASE + 0x0CU)
#define S5_DWELL_SECONDS 6U
#define S5_BAR_W 64
#define S5_HUD_X 16
#define S5_HUD_Y 16
#define S5_HUD_LINE_H (S5_GLYPH_H * S5_LABEL_SCALE + 6)
#define S5_HUD_LINES (S5_HUD_FIELD_COUNT + 1)
#ifndef S5_SINGLE_CASE
#define S5_SINGLE_CASE 0
#endif
#ifndef S5_FRAMES_MODE
#define S5_FRAMES_MODE 0
#endif
#if S5_FRAMES_MODE
#define S5_STREAM_FRAMES 120
#define S5_STREAM_GAP_US 60000U
#endif

static const u8 S5_CLASS_COLOR[5][3] = {
    {255, 64, 64}, {64, 255, 64}, {64, 64, 255}, {255, 255, 64}, {255, 64, 255},
};

/* ── §3 可信帧事件 ─────────────────────────────────────────────────────────── */
static XScuGic s5_gic;
static volatile u32 s5_vtc_events, s5_mm2s_events;
static volatile u32 s5_vtc_last_isr, s5_mm2s_last_sr;
static volatile u32 s5_vtc_b12, s5_vtc_b13, s5_vtc_b16, s5_vtc_other;
static volatile u32 s5_irq_spurious;
static volatile u32 s5_commit_pending;
static volatile u64 s5_commit_counts;
static volatile u64 s5_first_event_after_commit;

/* ── HUD 状态（§5.4 13 字段） ─────────────────────────────────────────────── */
typedef struct {
    u32 display_fps_x10;     /* 0 表示尚未测得 → 显示 NA */
    u32 frame_id;
    u32 boxes;
    u32 stale_cleared;
    u32 dropped_frames;
    u32 timeouts;
    u32 warmup;              /* 1=WARM */
    u32 age_result_ns;
    u32 age_frame_ns;
    u32 occ_cur, occ_max;    /* HUD 面板覆盖的框线像素（当前/最大） */
} s5_stats_t;
static s5_stats_t s5_st;

static void s5_mm2s_isr(void *ref)
{
    u32 sr = *(volatile u32 *)S5_MM2S_SR_ADDR;
    (void)ref;
    s5_mm2s_last_sr = sr;
    *(volatile u32 *)S5_MM2S_SR_ADDR = sr & 0x00001F00U;   /* W1C */
    if (sr & S5_MM2S_FRMCNT_BIT) {
        s5_mm2s_events++;
        if (s5_commit_pending && s5_first_event_after_commit == 0U) {
            XTime t;
            XTime_GetTime(&t);
            s5_first_event_after_commit = (u64)t;
            s5_commit_pending = 0U;
        }
    } else {
        s5_irq_spurious++;
    }
}

static void s5_vtc_isr(void *ref)
{
    u32 isr = *(volatile u32 *)S5_VTC_ISR_ADDR;
    (void)ref;
    s5_vtc_last_isr = isr;
    *(volatile u32 *)S5_VTC_ISR_ADDR = isr;                /* W1C */
    if (isr & 0x00001000U) s5_vtc_b12++;
    if (isr & 0x00002000U) s5_vtc_b13++;
    if (isr & 0x00010000U) s5_vtc_b16++;
    if (isr & ~0x00013000U) s5_vtc_other++;
    if (isr != 0U) {
        s5_vtc_events++;
    }
}

static int s5_events_init(void)
{
    XScuGic_Config *cfg = XScuGic_LookupConfig(XPAR_SCUGIC_0_DEVICE_ID);
    if (cfg == NULL) return -1;
    if (XScuGic_CfgInitialize(&s5_gic, cfg, cfg->CpuBaseAddress) != XST_SUCCESS) return -1;
    Xil_ExceptionInit();
    Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_IRQ_INT,
                                 (Xil_ExceptionHandler)XScuGic_InterruptHandler, &s5_gic);
    if (XScuGic_Connect(&s5_gic, XPAR_FABRIC_AXI_VDMA_0_MM2S_INTROUT_INTR,
                        (Xil_ExceptionHandler)s5_mm2s_isr, NULL) != XST_SUCCESS) return -2;
    XScuGic_Enable(&s5_gic, XPAR_FABRIC_AXI_VDMA_0_MM2S_INTROUT_INTR);
    if (XScuGic_Connect(&s5_gic, XPAR_FABRIC_V_TC_0_IRQ_INTR,
                        (Xil_ExceptionHandler)s5_vtc_isr, NULL) != XST_SUCCESS) return -3;
    XScuGic_Enable(&s5_gic, XPAR_FABRIC_V_TC_0_IRQ_INTR);
    Xil_ExceptionEnable();
    return 0;
}

static void s5_arm_frame_irq(void)
{
    volatile u32 *cr = (volatile u32 *)S5_MM2S_CR_ADDR;
    u32 v = *cr;
    v = (v & 0x00FFFFFFU) | (1U << S5_MM2S_FRMCNT_THRESH_SHIFT);
    v |= S5_MM2S_FRMCNT_IRQ_EN;
    v |= 0x1U;
    *cr = v;
}

static void s5_arm_vtc_irq(void)
{
    *(volatile u32 *)S5_VTC_IER_ADDR = 0xFFFFFFFFU;
    *(volatile u32 *)S5_VTC_ISR_ADDR = 0xFFFFFFFFU;
}

/* ── 像素/图形原语 ────────────────────────────────────────────────────────── */
static inline void s5_px(u8 *buf, u32 stride, int x, int y, u8 r, u8 g, u8 b)
{
    u8 *p;
    if (x < 0 || y < 0 || x >= S5_CANVAS_W || y >= S5_CANVAS_H) return;
    p = buf + (u32)y * stride + (u32)x * 3U;
    p[0] = b; p[1] = g; p[2] = r;
}

static void s5_fill_rect(u8 *buf, u32 stride, int x1, int y1, int x2, int y2, u8 r, u8 g, u8 b)
{
    int x, y;
    for (y = y1; y <= y2; y++)
        for (x = x1; x <= x2; x++)
            s5_px(buf, stride, x, y, r, g, b);
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

static void s5_box_border(u8 *buf, u32 stride, int x1, int y1, int x2, int y2, const u8 *rgb)
{
    s5_line(buf, stride, x1, y1, x2, y1, 2, rgb[0], rgb[1], rgb[2]);
    s5_line(buf, stride, x1, y2, x2, y2, 2, rgb[0], rgb[1], rgb[2]);
    s5_line(buf, stride, x1, y1, x1, y2, 2, rgb[0], rgb[1], rgb[2]);
    s5_line(buf, stride, x2, y1, x2, y2, 2, rgb[0], rgb[1], rgb[2]);
}

static const s5_glyph_t *s5_glyph(char ch)
{
    int i;
    char up = (ch >= 'a' && ch <= 'z') ? (char)(ch - 'a' + 'A') : ch;
    for (i = 0; i < S5_GLYPH_COUNT; i++)
        if (S5_GLYPHS[i].ch == up) return &S5_GLYPHS[i];
    return 0;
}

static void s5_text(u8 *buf, u32 stride, int x, int y, const char *text, int scale,
                    u8 r, u8 g, u8 b)
{
    int cx = x;
    const char *p;
    for (p = text; *p; p++) {
        const s5_glyph_t *gl = s5_glyph(*p);
        if (gl) {
            int i;
            for (i = 0; i < gl->nseg; i++)
                s5_line(buf, stride, cx + gl->seg[i][0] * scale, y + gl->seg[i][1] * scale,
                        cx + gl->seg[i][2] * scale, y + gl->seg[i][3] * scale,
                        scale > 1 ? 2 : 1, r, g, b);
        }
        cx += S5_GLYPH_ADV * scale;
    }
}

static void s5_text_plate(u8 *buf, u32 stride, int x, int y, const char *text, int scale, const u8 *rgb)
{
    int w = (int)S5_GLYPH_ADV * scale * (int)strlen(text) + 2;
    int h = S5_GLYPH_H * scale + 2;
    s5_fill_rect(buf, stride, x - 1, y - 1, x + w, y + h, 0, 0, 0);
    s5_text(buf, stride, x, y, text, scale, rgb[0], rgb[1], rgb[2]);
}

static void s5_background(u8 *buf, u32 stride)
{
    int x, y;
    for (y = 0; y < S5_CANVAS_H; y++)
        for (x = 0; x < S5_CANVAS_W; x++) {
            u8 v = (u8)(((u32)x * 255U) / (u32)(S5_CANVAS_W - 1));
            s5_px(buf, stride, x, y, v, v, v);
        }
    for (x = 0; x < S5_CANVAS_W; x += S5_BAR_W)
        s5_line(buf, stride, x, 0, x, S5_CANVAS_H - 1, 1, 0, 0, 0);
    s5_fill_rect(buf, stride, 0, 0, 15, 15, 255, 255, 255);
    s5_fill_rect(buf, stride, S5_CANVAS_W - 16, 0, S5_CANVAS_W - 1, 15, 255, 255, 255);
    s5_fill_rect(buf, stride, 0, S5_CANVAS_H - 16, 15, S5_CANVAS_H - 1, 255, 255, 255);
    s5_fill_rect(buf, stride, S5_CANVAS_W - 16, S5_CANVAS_H - 16, S5_CANVAS_W - 1, S5_CANVAS_H - 1, 255, 255, 255);
    s5_line(buf, stride, S5_CANVAS_W / 2, 0, S5_CANVAS_W / 2, S5_CANVAS_H - 1, 1, 255, 255, 255);
    s5_line(buf, stride, 0, S5_CANVAS_H / 2, S5_CANVAS_W - 1, S5_CANVAS_H / 2, 1, 255, 255, 255);
}

static void s5_hud_rect(int *x1, int *y1, int *x2, int *y2)
{
    int widest = 0, i;
    for (i = 0; i < S5_HUD_FIELD_COUNT; i++) {
        int len = (int)strlen(S5_HUD_FIELDS[i]) + 8;      /* + "=值" 余量 */
        if (len > widest) widest = len;
    }
    *x1 = S5_HUD_X - 2;
    *y1 = S5_HUD_Y - 2;
    *x2 = S5_HUD_X - 2 + S5_GLYPH_ADV * S5_LABEL_SCALE * widest + 4;
    *y2 = S5_HUD_Y - 2 + S5_HUD_LINES * S5_HUD_LINE_H + 2;
}

/* HUD 遮挡量化：统计框线像素落在 HUD 面板内的数量（±4 角点重复计数，文档注明） */
static u32 s5_overlap_len(int a1, int a2, int b1, int b2)
{
    int lo = (a1 > b1) ? a1 : b1;
    int hi = (a2 < b2) ? a2 : b2;
    return (hi >= lo) ? (u32)(hi - lo + 1) : 0U;
}

static u32 s5_box_occluded(const s5_box_t *b, int hx1, int hy1, int hx2, int hy2)
{
    u32 n = 0;
    int r, c;
    for (r = b->y1; r <= b->y1 + 1; r++)
        if (r >= hy1 && r <= hy2) n += s5_overlap_len(b->x1, b->x2, hx1, hx2);
    for (r = b->y2; r <= b->y2 + 1; r++)
        if (r >= hy1 && r <= hy2) n += s5_overlap_len(b->x1, b->x2, hx1, hx2);
    for (c = b->x1; c <= b->x1 + 1; c++)
        if (c >= hx1 && c <= hx2) n += s5_overlap_len(b->y1, b->y2, hy1, hy2);
    for (c = b->x2; c <= b->x2 + 1; c++)
        if (c >= hx1 && c <= hx2) n += s5_overlap_len(b->y1, b->y2, hy1, hy2);
    return n;
}

/* ── HUD 文本（§5.4 13 字段；缺失值 NA） ─────────────────────────────────── */
static void s5_u32_dec(u32 v, char *out)
{
    char tmp[12];
    int n = 0, i = 0;
    if (v == 0U) {
        out[0] = '0';
        out[1] = '\0';
        return;
    }
    while (v > 0U && n < 11) {
        tmp[n++] = (char)('0' + (v % 10U));
        v /= 10U;
    }
    while (n > 0) out[i++] = tmp[--n];
    out[i] = '\0';
}

static void s5_fps10_text(u32 v10, char *out)
{
    if (v10 == 0U) {
        strcpy(out, "NA");
        return;
    }
    s5_u32_dec(v10 / 10U, out);
    {
        int n = (int)strlen(out);
        out[n++] = '.';
        out[n++] = (char)('0' + (v10 % 10U));
        out[n] = '\0';
    }
}

static void s5_hud_line(char *out, const char *name, const char *value)
{
    strcpy(out, name);
    strcat(out, "=");
    strcat(out, value);
}

static void s5_hud_draw(u8 *buf, u32 stride, const s5_case_t *c)
{
    int i, y = S5_HUD_Y;
    char line[40], val[16];
    s5_text_plate(buf, stride, S5_HUD_X, y, c->hud[0], S5_LABEL_SCALE, S5_CLASS_COLOR[0]);
    y += S5_HUD_LINE_H;
    for (i = 0; i < S5_HUD_FIELD_COUNT; i++) {
        switch (i) {
        case 0:  strcpy(val, "NA"); break;                        /* capture_fps：无摄像头 */
        case 1:  strcpy(val, "NA"); break;                        /* inference_fps：无阶段4 */
        case 2:  s5_fps10_text(s5_st.display_fps_x10, val); break;/* display_fps */
        case 3:  strcpy(val, "NA"); break;                        /* inference_time_ns */
        case 4:  s5_u32_dec(s5_st.age_result_ns, val); break;
        case 5:  s5_u32_dec(s5_st.age_frame_ns, val); break;
        case 6:  s5_u32_dec(s5_st.frame_id, val); break;
        case 7:  s5_u32_dec(s5_st.boxes, val); break;
        case 8:  s5_u32_dec(s5_st.stale_cleared, val); break;
        case 9:  s5_u32_dec(s5_st.dropped_frames, val); break;
        case 10: s5_u32_dec(s5_st.timeouts, val); break;
        case 11: strcpy(val, s5_st.warmup ? "WARM" : "STEADY"); break;
        default: strcpy(val, "B"); break;                         /* display_semantics */
        }
        s5_hud_line(line, S5_HUD_FIELDS[i], val);
        s5_text_plate(buf, stride, S5_HUD_X, y, line, S5_LABEL_SCALE, S5_CLASS_COLOR[i % 5]);
        y += S5_HUD_LINE_H;
    }
}

static void s5_render(u8 *buf, u32 stride, const s5_case_t *c, int draw_boxes)
{
    int i, hx1, hy1, hx2, hy2;
    u32 occ = 0;
    s5_background(buf, stride);
    s5_hud_rect(&hx1, &hy1, &hx2, &hy2);
#if S5_DYNAMIC_MAP
    /* 无条件计算：过期/NO_HAND 帧也必须如实上报状态与计数（B2/B4 证据口径） */
    s5dm_run_case(c);
    if (draw_boxes) {
        for (i = 0; i < s5dm_res.nbox_drawn; i++) {
            s5d_drawn_box *d = &s5dm_res.drawn[i];
            s5_box_t bb;
            const u8 *rgb;
            bb.x1 = (short)d->rect.x1; bb.y1 = (short)d->rect.y1;
            bb.x2 = (short)d->rect.x2; bb.y2 = (short)d->rect.y2;
            bb.cls = (unsigned char)c->boxes[i].cls; bb.label = c->boxes[i].label;
            rgb = S5_CLASS_COLOR[bb.cls % 5];
            occ += s5_box_occluded(&bb, hx1, hy1, hx2, hy2);
            s5_box_border(buf, stride, bb.x1, bb.y1, bb.x2, bb.y2, rgb);
            /* 标签锚点用核心（=冻结参考 label_anchor），不再用本文件历史经验规则 */
            s5_text_plate(buf, stride, d->label_x, d->label_y, bb.label, S5_LABEL_SCALE, rgb);
        }
    }
#else
    if (draw_boxes) {
        for (i = 0; i < c->nbox; i++) {
            const s5_box_t *b = &c->boxes[i];
            const u8 *rgb = S5_CLASS_COLOR[b->cls % 5];
            int lw = S5_GLYPH_ADV * S5_LABEL_SCALE * (int)strlen(b->label) + 2;
            int lh = S5_GLYPH_H * S5_LABEL_SCALE + 2;
            int lx = b->x1;
            int ly = b->y1 - (S5_GLYPH_H * S5_LABEL_SCALE + 4);
            occ += s5_box_occluded(b, hx1, hy1, hx2, hy2);
            s5_box_border(buf, stride, b->x1, b->y1, b->x2, b->y2, rgb);
            if (ly < 18) ly = b->y1 + 4;
            if (lx < 2) lx = 2;
            if (!(lx + lw < hx1 || lx > hx2 || ly + lh < hy1 || ly > hy2)) lx = hx2 + 6;
            if (lx + lw > S5_CANVAS_W - 2) lx = S5_CANVAS_W - 2 - lw;
            if (ly + lh > S5_CANVAS_H - 2) ly = S5_CANVAS_H - 2 - lh;
            s5_text_plate(buf, stride, lx, ly, b->label, S5_LABEL_SCALE, rgb);
        }
    }
#endif
    s5_st.occ_cur = occ;
    if (occ > s5_st.occ_max) s5_st.occ_max = occ;
    s5_hud_draw(buf, stride, c);     /* HUD 最后绘制（置顶） */
#if S5_DYNAMIC_MAP
    {
        /* 相位探针（S5DM_PHASE_PROBE）：缓冲行 0 起始 8 字节写已知魔数，并在像素 1 写已知颜色。
         * JTAG 转储若看到 53 35 44 4D 01 02 03 04 ⇒ 字节 0 = 像素 x0，且 3 字节/像素边界可实证定位；
         * 用于锁定"字(4B)读取 vs 像素(3B)"的对齐口径（离线相位扫描无法定案）。 */
        static const u8 magic[8] = {0x53, 0x35, 0x44, 0x4D, 0x01, 0x02, 0x03, 0x04};
        int k;
        for (k = 0; k < 8; k++) buf[k] = magic[k];
        buf[3] = 0x11; buf[4] = 0x22; buf[5] = 0x33;   /* 像素 x=1 的 (B,G,R) 已知值 */
    }
#endif
}

static u32 s5_mm2s_sr(void) { return *(volatile u32 *)S5_MM2S_SR_ADDR; }
static u32 s5_mm2s_frames(void) { return (s5_mm2s_sr() >> 16) & 0xFFU; }

static int s5_fps10(u32 events, u64 counts, UINTPTR rate)
{
    if (counts == 0U) return 0;
    return (int)(((u64)events * 10U * (u64)rate) / counts);
}

#if S5_FRAMES_MODE
/* §4：≥100 帧结果流消费（displayed_frame_id / result_frame_id / 两个年龄 / 语义 B）
 * T5-11：warm/drop/timeout/dup/ooo/stale 分别计数，绝不隐藏。 */
static void s5_frames_run(u8 **pFrames, u32 num_frames, u32 stride, UINTPTR rate)
{
    u32 round = 0;
    for (;;) {
        u32 k, displayed = 0, dup = 0, ooo = 0, warm = 0, stale = 0, dropped = 0, timeouts = 0;
        u32 uniq = 0, last_result = 0xFFFFFFFFU;
        u64 t0, t1;
        XTime tt;
        XTime_GetTime(&tt);
        t0 = (u64)tt;
        for (k = 0; k < S5_STREAM_FRAMES; k++) {
            const s5_case_t *c = &S5_CASES[k % S5_NUM_CASES];
            u32 result_fid = k;
            u32 age_result = ((k % 7U) == 0U) ? 250000000U : (k * 1000000U);
            u32 age_frame = age_result + 5000000U;
            int is_warm = (k < 9U);
            int is_drop = (k > 9U) && ((k % 17U) == 0U);
            int is_timeout = (k > 9U) && ((k % 19U) == 0U);
            int is_dup = (k > 9U) && ((k % 23U) == 0U);
            int is_ooo = (k > 9U) && ((k % 29U) == 0U);
            int is_stale;

            if (is_warm) warm++;
            s5_st.warmup = is_warm;
            s5_st.age_result_ns = age_result;
            s5_st.age_frame_ns = age_frame;
            if (is_drop) {
                dropped++;
                s5_st.dropped_frames = dropped;
                xil_printf("S5_5T_SKIP frames=%u kind=DROP result=%u age_result_ns=%u\r\n",
                           (unsigned)k, (unsigned)result_fid, (unsigned)age_result);
                continue;
            }
            if (is_timeout) {
                timeouts++;
                s5_st.timeouts = timeouts;
                xil_printf("S5_5T_SKIP frames=%u kind=TIMEOUT result=%u age_result_ns=%u\r\n",
                           (unsigned)k, (unsigned)result_fid, (unsigned)age_result);
                continue;
            }
            if (is_dup && last_result != 0xFFFFFFFFU) {
                dup++;
                result_fid = last_result;                  /* 重复结果：不改写 frame_id */
            }
            if (is_ooo && k > 3U) {
                ooo++;
                result_fid = k - 3U;                       /* 乱序结果：如实记录 */
            }
            if (result_fid != last_result) uniq++;
            is_stale = (age_result > (u32)S5_STALE_LIMIT_NS);
            if (is_stale) {
                stale++;
                s5_st.stale_cleared = stale;
                s5_st.boxes = 0;
            } else {
                s5_st.boxes = c->nbox;
            }
            s5_st.frame_id = result_fid;
            s5_st.display_fps_x10 = 0;                     /* 本模式不在此测，末尾汇总 */
            {
                u32 f;
                for (f = 0; f < num_frames; f++) {
                    s5_render(pFrames[f], stride, c, !is_stale);
                    Xil_DCacheFlushRange((INTPTR)pFrames[f], stride * S5_CANVAS_H);
                }
            }
            xil_printf("S5_5T displayed=%u result=%u age_result_ns=%u age_frame_ns=%u semantics=B "
                       "boxes=%u stale=%u warm=%u occ=%u\r\n",
                       (unsigned)displayed, (unsigned)result_fid, (unsigned)age_result,
                       (unsigned)age_frame, (unsigned)s5_st.boxes, (unsigned)(is_stale ? 1 : 0),
                       (unsigned)(is_warm ? 1 : 0), (unsigned)s5_st.occ_cur);
            displayed++;
            last_result = result_fid;
            usleep(S5_STREAM_GAP_US);
        }
        XTime_GetTime(&tt);
        t1 = (u64)tt;
        {
            u64 dt = (t1 - t0) ? (t1 - t0) : 1U;
            u32 fps_x10 = (u32)(((u64)displayed * 10U * (u64)rate) / dt);
            u32 uniq_x10 = (u32)(((u64)uniq * 10U * (u64)rate) / dt);
            s5_st.display_fps_x10 = fps_x10;
            xil_printf("S5_5T_SUMMARY round=%u frames=%u displayed=%u stale_cleared=%u dropped=%u "
                       "timeouts=%u dup=%u ooo=%u warmup=%u uniq_displayed=%u elapsed_ms=%u "
                       "display_fps_x10=%u unique_frame_update_fps_x10=%u occ_max=%u\r\n",
                       (unsigned)round, (unsigned)S5_STREAM_FRAMES, (unsigned)displayed,
                       (unsigned)stale, (unsigned)dropped, (unsigned)timeouts, (unsigned)dup,
                       (unsigned)ooo, (unsigned)warm, (unsigned)uniq,
                       (unsigned)((dt * 1000ULL) / (u64)rate), (unsigned)fps_x10,
                       (unsigned)uniq_x10, (unsigned)s5_st.occ_max);
        }
        round++;
    }
}
#endif

void s5_overlay_loop(u8 **pFrames, u32 num_frames, u32 stride, DisplayCtrl *disp)
{
    UINTPTR count_rate = COUNTS_PER_SECOND ? COUNTS_PER_SECOND : 1U;
    u32 ncase = S5_NUM_CASES;
    u32 ci;
    int ev_rc;
    (void)disp;

    memset(&s5_st, 0, sizeof(s5_st));
    xil_printf("\r\nS5_P1_BEGIN canvas=%dx%d stride=%u frames=%u cases=%u rev=r05\r\n",
               S5_CANVAS_W, S5_CANVAS_H, (unsigned)stride, (unsigned)num_frames, (unsigned)ncase);
    xil_printf("S5_P1_SOURCE=PS_SYNTHETIC (no sensor, no S2MM; zero new PL)\r\n");
    xil_printf("S5_P1_SEMANTICS=B_latest_result_overlay stale_limit_ns=%u\r\n", (unsigned)S5_STALE_LIMIT_NS);
    xil_printf("S5_P1_HUD_FIELDS=%u (capture_fps=NA inference_fps=NA inference_time_ns=NA)\r\n",
               (unsigned)S5_HUD_FIELD_COUNT);
    xil_printf("S5_P1_CLOCK counts_per_second=%u\r\n", (unsigned)count_rate);
    {
        u32 i;
        for (i = 0; i < num_frames; i++)
            xil_printf("S5_P1_BUF%u=%08X\r\n", (unsigned)i, (unsigned)(UINTPTR)pFrames[i]);
    }
    for (ci = 0; ci < ncase; ci++)
        xil_printf("S5_P1_CASE_TABLE id=%u boxes=%u stale=%u name=%s\r\n",
                   S5_CASES[ci].id, S5_CASES[ci].nbox, S5_CASES[ci].stale, S5_CASES[ci].name);

    ev_rc = s5_events_init();
    s5_arm_vtc_irq();
    s5_arm_frame_irq();
    xil_printf("S5_P1_EVENTS_INIT=%d MM2S_CR=%08X VTC_IER=%08X\r\n", ev_rc,
               (unsigned)*(volatile u32 *)S5_MM2S_CR_ADDR, (unsigned)*(volatile u32 *)S5_VTC_IER_ADDR);

#if S5_FRAMES_MODE
    s5_frames_run(pFrames, num_frames, stride, count_rate);
#else
    for (;;) {
        for (ci = 0; ci < ncase; ci++) {
            const s5_case_t *c = &S5_CASES[ci];
            u32 f, sec;
            u32 v_prev = s5_vtc_events, m_prev = s5_mm2s_events;
            XTime t_prev;
#if S5_SINGLE_CASE > 0
            if (c->id != (unsigned)S5_SINGLE_CASE) continue;
#endif
            s5_st.boxes = c->nbox;
            s5_st.frame_id = c->id;
            s5_st.stale_cleared = 0;
            s5_st.dropped_frames = 0;
            s5_st.timeouts = 0;
            s5_st.warmup = 0;
            s5_st.age_result_ns = 0;
            s5_st.age_frame_ns = 0;
            XTime_GetTime(&t_prev);
            s5_commit_counts = (u64)t_prev;
            s5_commit_pending = 1U;
            s5_first_event_after_commit = 0U;
            for (f = 0; f < num_frames; f++) {
                s5_render(pFrames[f], stride, c, !c->stale);
                Xil_DCacheFlushRange((INTPTR)pFrames[f], stride * S5_CANVAS_H);
            }
            xil_printf("S5_P1_SHOW case=%u boxes=%u stale=%u occ=%u age_result_ns=%u\r\n",
                       c->id, c->nbox, c->stale, (unsigned)s5_st.occ_cur, (unsigned)s5_st.age_result_ns);
            for (sec = 1U; sec <= S5_DWELL_SECONDS; sec++) {
                XTime t_now;
                u32 dv, dm;
                u64 dt;
                usleep(1000000);
                XTime_GetTime(&t_now);
                dv = s5_vtc_events - v_prev;
                dm = s5_mm2s_events - m_prev;
                dt = (u64)t_now - (u64)t_prev;
                s5_st.display_fps_x10 = (u32)s5_fps10(dm, dt, count_rate);
                xil_printf("S5_FPS4 case=%u win=%u vtc_events=%u mm2s_events=%u dt_counts=%u "
                           "video_refresh_fps_x10=%d display_fps_x10=%d inference_fps=NA "
                           "vtc_b12=%u vtc_b13=%u vtc_b16=%u spurious=%u occ=%u\r\n",
                           c->id, (unsigned)sec, (unsigned)dv, (unsigned)dm, (unsigned)dt,
                           s5_fps10(dv, dt, count_rate), s5_fps10(dm, dt, count_rate),
                           (unsigned)s5_vtc_b12, (unsigned)s5_vtc_b13, (unsigned)s5_vtc_b16,
                           (unsigned)s5_irq_spurious, (unsigned)s5_st.occ_cur);
                v_prev = s5_vtc_events;
                m_prev = s5_mm2s_events;
                t_prev = t_now;
            }
            if (s5_first_event_after_commit != 0U) {
                u64 delta = s5_first_event_after_commit - s5_commit_counts;
                xil_printf("S5_LAT case=%u commit_to_frame_complete_ns=%u "
                           "(definition=t_overlay_commit..next_MM2S_FrmCnt_event; NOT photon-to-screen)\r\n",
                           c->id, (unsigned)((delta * 1000000000ULL) / (u64)count_rate));
            } else {
                xil_printf("S5_LAT case=%u commit_to_frame_complete_ns=NA\r\n", c->id);
            }
        }
        xil_printf("S5_P1_CYCLE_DONE\r\n");
    }
#endif
}