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
 * 修订：
 *   rev r02（2026-10-22）D-1 背景平滑斜坡；D-2 标签避让 HUD + HUD 置顶（照片缺陷修复）。
 *   rev r03（2026-10-22）§3 可信帧事件：XScuGic（ID 61=MM2S 帧完成、ID 62=VTC）双 ISR + 四种 FPS 口径：
 *       - video_refresh_fps：VTC 中断事件/秒（起止=连续两次 VTC 事件）
 *       - display_fps      ：MM2S FrmCntIrq 事件/秒（起止=连续两次帧完成事件；CR[23:16]=1 ⇒ 每帧一次）
 *       - unique_frame_update_fps：不同内容实际更新率（本轮为用例级；frame_id 级待 T5-05）
 *       - inference_fps    ：无阶段4 注入源 ⇒ **NOT_APPLICABLE**（打印 NA，不用 0 伪装）
 *     另报告 commit_to_frame_complete_ns（提交→首个帧完成事件；**不称光子到屏幕**）。
 *
 * 字节序：按阶段3 证据，DDR 内为 B,G,R（offset0=蓝）。背景为灰度（三通道同值）故与字节序无关；
 *         框线颜色按该顺序书写，若实机 R/B 互换只影响颜色观感，不影响几何判定。
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

#define S5_MM2S_CR_ADDR 0x43000000U   /* 显示通道 VDMA MM2S 控制寄存器 */
#define S5_MM2S_SR_ADDR 0x43000004U   /* 显示通道 VDMA MM2S 状态寄存器（阶段3 证据：SR_MM2S=0x43000004） */
#define S5_MM2S_FRMCNT_BIT 0x00001000U      /* SR bit12 = FrmCntIrq */
#define S5_MM2S_FRMCNT_IRQ_EN 0x00001000U   /* CR bit12 = Frame Count IRQ Enable */
#define S5_MM2S_FRMCNT_THRESH_SHIFT 16U     /* CR[23:16] = 帧计数阈值（=1 ⇒ 每帧一次 IRQ） */
#define S5_VTC_BASE 0x43C00000U             /* XPAR_V_TC_0_BASEADDR */
#define S5_VTC_ISR_ADDR (S5_VTC_BASE + 0x04U)
#define S5_VTC_IER_ADDR (S5_VTC_BASE + 0x0CU)
#define S5_DWELL_SECONDS 6U
#define S5_BAR_W 64
#define S5_HUD_X 24
#define S5_HUD_Y 24
#define S5_HUD_MAX_LEN 8              /* 最长 HUD 文本 "BOXES 15" */
#ifndef S5_SINGLE_CASE
#define S5_SINGLE_CASE 0              /* 0=循环全部用例；N=只常显用例 N（便于确定性读数与拍照） */
#endif

static const u8 S5_CLASS_COLOR[5][3] = {
    {255, 64, 64}, {64, 255, 64}, {64, 64, 255}, {255, 255, 64}, {255, 64, 255},
};

/* ── §3 可信帧事件（rev r03） ─────────────────────────────────────────────── */
static XScuGic s5_gic;
static volatile u32 s5_vtc_events;              /* VTC 中断事件数（视频刷新候选） */
static volatile u32 s5_mm2s_events;             /* MM2S FrmCntIrq 事件数（显示帧完成） */
static volatile u32 s5_vtc_last_isr;            /* 最近一次 VTC ISR 原始值（供证据判读位含义） */
static volatile u32 s5_mm2s_last_sr;            /* 最近一次 MM2S SR 原始值 */
static volatile u32 s5_vtc_bits_seen;           /* 累积出现过的 VTC ISR 位 */
static volatile u32 s5_irq_spurious;            /* 无 IRQ 位的中断次数（诊断） */
static volatile u32 s5_commit_pending;
static volatile u64 s5_commit_counts;           /* t_overlay_commit（提交）时刻 */
static volatile u64 s5_first_event_after_commit;/* 提交后首个帧完成事件时刻 */
static volatile u32 s5_case_commits;            /* 内容提交次数（用例级 distinct） */
static volatile u32 s5_vtc_b12, s5_vtc_b13, s5_vtc_b16, s5_vtc_other;  /* VTC ISR 逐位计数（定标用） */

static void s5_mm2s_isr(void *ref)
{
    u32 sr = *(volatile u32 *)S5_MM2S_SR_ADDR;
    (void)ref;
    s5_mm2s_last_sr = sr;
    /* W1C：清 IRQ 位（bit9 IOC / bit10 Dly / bit11 Err / bit12 FrmCnt） */
    *(volatile u32 *)S5_MM2S_SR_ADDR = sr & 0x00001F00U;
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
    s5_vtc_bits_seen |= isr;
    *(volatile u32 *)S5_VTC_ISR_ADDR = isr;       /* W1C 清除 */
    /* 位含义按实测原始值定标：r03 实机只见 0x1000/0x2000/0x10000，故逐位计数 */
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
    if (cfg == NULL) {
        return -1;
    }
    if (XScuGic_CfgInitialize(&s5_gic, cfg, cfg->CpuBaseAddress) != XST_SUCCESS) {
        return -1;
    }
    Xil_ExceptionInit();
    Xil_ExceptionRegisterHandler(XIL_EXCEPTION_ID_IRQ_INT,
                                 (Xil_ExceptionHandler)XScuGic_InterruptHandler, &s5_gic);
    if (XScuGic_Connect(&s5_gic, XPAR_FABRIC_AXI_VDMA_0_MM2S_INTROUT_INTR,
                        (Xil_ExceptionHandler)s5_mm2s_isr, NULL) != XST_SUCCESS) {
        return -2;
    }
    XScuGic_Enable(&s5_gic, XPAR_FABRIC_AXI_VDMA_0_MM2S_INTROUT_INTR);
    if (XScuGic_Connect(&s5_gic, XPAR_FABRIC_V_TC_0_IRQ_INTR,
                        (Xil_ExceptionHandler)s5_vtc_isr, NULL) != XST_SUCCESS) {
        return -3;
    }
    XScuGic_Enable(&s5_gic, XPAR_FABRIC_V_TC_0_IRQ_INTR);
    Xil_ExceptionEnable();
    return 0;
}

static void s5_arm_frame_irq(void)
{
    volatile u32 *cr = (volatile u32 *)S5_MM2S_CR_ADDR;
    u32 v = *cr;
    v = (v & 0x00FFFFFFU) | (1U << S5_MM2S_FRMCNT_THRESH_SHIFT);   /* 阈值=1 */
    v |= S5_MM2S_FRMCNT_IRQ_EN;                                    /* bit12 */
    v |= 0x1U;                                                     /* RS=1 */
    *cr = v;
}

static void s5_arm_vtc_irq(void)
{
    *(volatile u32 *)S5_VTC_IER_ADDR = 0xFFFFFFFFU;   /* 使能全部来源（ISR 内 W1C 自清） */
    *(volatile u32 *)S5_VTC_ISR_ADDR = 0xFFFFFFFFU;   /* 清残留 */
}

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
        const s5_glyph_t *gl = s5_glyph(*p);          /* 勿命名 g：避免遮蔽颜色参数 g */
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

/* 确定性合成背景：水平灰度斜坡 + 64px 黑网格线 + 四角白标记 + 中心白十字
 * D-1 修复：斜坡用 (x*255)/(W-1)，不再出现 u8 回绕黑带。 */
static void s5_background(u8 *buf, u32 stride)
{
    int x, y;
    for (y = 0; y < S5_CANVAS_H; y++) {
        for (x = 0; x < S5_CANVAS_W; x++) {
            u8 v = (u8)(((u32)x * 255U) / (u32)(S5_CANVAS_W - 1));
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

static void s5_hud_rect(int *x1, int *y1, int *x2, int *y2)
{
    *x1 = S5_HUD_X - 1;
    *y1 = S5_HUD_Y - 1;
    *x2 = S5_HUD_X - 1 + S5_GLYPH_ADV * S5_LABEL_SCALE * S5_HUD_MAX_LEN + 4;
    *y2 = S5_HUD_Y - 1 + 4 * (S5_GLYPH_H * S5_LABEL_SCALE + 8);
}

static void s5_render_case(u8 *buf, u32 stride, const s5_case_t *c)
{
    int i;
    int hx1, hy1, hx2, hy2;
    s5_background(buf, stride);
    s5_hud_rect(&hx1, &hy1, &hx2, &hy2);
    for (i = 0; i < c->nbox; i++) {
        const s5_box_t *b = &c->boxes[i];
        const u8 *rgb = S5_CLASS_COLOR[b->cls % 5];
        int lw = S5_GLYPH_ADV * S5_LABEL_SCALE * (int)strlen(b->label) + 2;
        int lh = S5_GLYPH_H * S5_LABEL_SCALE + 2;
        int lx = b->x1;
        int ly = b->y1 - (S5_GLYPH_H * S5_LABEL_SCALE + 4);
        s5_box_border(buf, stride, b->x1, b->y1, b->x2, b->y2, rgb);
        if (ly < 18) ly = b->y1 + 4;                     /* 越界翻转到框内左上（契约锚点规则） */
        if (lx < 2) lx = 2;
        /* D-2：与 HUD 区域重叠时右移避让 */
        if (!(lx + lw < hx1 || lx > hx2 || ly + lh < hy1 || ly > hy2)) {
            lx = hx2 + 6;
        }
        if (lx + lw > S5_CANVAS_W - 2) lx = S5_CANVAS_W - 2 - lw;
        if (ly + lh > S5_CANVAS_H - 2) ly = S5_CANVAS_H - 2 - lh;
        s5_text_plate(buf, stride, lx, ly, b->label, S5_LABEL_SCALE, rgb);
    }
    /* HUD 最后绘制（置顶），任何框/标签都不会压住 HUD 文本 */
    for (i = 0; i < 4; i++) {
        s5_text_plate(buf, stride, S5_HUD_X, S5_HUD_Y + i * (S5_GLYPH_H * S5_LABEL_SCALE + 8),
                      c->hud[i], S5_LABEL_SCALE, S5_CLASS_COLOR[i % 5]);
    }
}

static u32 s5_mm2s_sr(void)
{
    return *(volatile u32 *)S5_MM2S_SR_ADDR;
}

static u32 s5_mm2s_frames(void)
{
    return (s5_mm2s_sr() >> 16) & 0xFFU;                 /* VDMASR IRQFrameCntSts（阶段3 位定义证据） */
}

static int s5_fps10(u32 events, u64 counts, UINTPTR rate)
{
    if (counts == 0U) {
        return 0;
    }
    return (int)(((u64)events * 10U * (u64)rate) / counts);
}

void s5_overlay_loop(u8 **pFrames, u32 num_frames, u32 stride, DisplayCtrl *disp)
{
    UINTPTR count_rate = COUNTS_PER_SECOND ? COUNTS_PER_SECOND : 1U;
    u32 ncase = S5_NUM_CASES;
    u32 ci;
    u32 common_case_id = 0;
    int ev_rc;
    (void)disp;

    xil_printf("\r\nS5_P1_BEGIN canvas=%dx%d stride=%u frames=%u cases=%u rev=r04\r\n",
               S5_CANVAS_W, S5_CANVAS_H, (unsigned)stride, (unsigned)num_frames, (unsigned)ncase);
    xil_printf("S5_P1_SOURCE=PS_SYNTHETIC (no sensor, no S2MM; zero new PL)\r\n");
    xil_printf("S5_P1_SEMANTICS=B_latest_result_overlay stale_limit_ns=%u\r\n", (unsigned)S5_STALE_LIMIT_NS);
    xil_printf("S5_P1_GEOMETRY=from_verification/s5_display_geometry_reference.py(S5A-G0-v2)\r\n");
    xil_printf("S5_P1_FPS_DEF video_refresh=VTC_IRQ display=MM2S_FrmCntIrq uniq=content_commit "
               "inference=NA(no_stage4_source)\r\n");
    xil_printf("S5_P1_CLOCK counts_per_second=%u\r\n", (unsigned)count_rate);
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

    ev_rc = s5_events_init();
    xil_printf("S5_P1_EVENTS_INIT=%d (0=ok; -1=cfg -2=mm2s_connect -3=vtc_connect)\r\n", ev_rc);
    xil_printf("S5_P1_VTC_IER_BEFORE=%08X ISR_BEFORE=%08X\r\n",
               (unsigned)*(volatile u32 *)S5_VTC_IER_ADDR, (unsigned)*(volatile u32 *)S5_VTC_ISR_ADDR);
    s5_arm_vtc_irq();
    s5_arm_frame_irq();
    xil_printf("S5_P1_VTC_IER_AFTER=%08X MM2S_CR_ARMED=%08X MM2S_SR=%08X\r\n",
               (unsigned)*(volatile u32 *)S5_VTC_IER_ADDR,
               (unsigned)*(volatile u32 *)S5_MM2S_CR_ADDR, (unsigned)s5_mm2s_sr());

    for (;;) {
        for (ci = 0; ci < ncase; ci++) {
            const s5_case_t *c = &S5_CASES[ci];
            u32 f;
            u32 sec;
            u32 v_prev = s5_vtc_events;
            u32 m_prev = s5_mm2s_events;
            XTime t_prev;

#if S5_SINGLE_CASE > 0
            if (c->id != (unsigned)S5_SINGLE_CASE) {
                continue;
            }
#endif
            XTime_GetTime(&t_prev);
            s5_commit_counts = (u64)t_prev;
            s5_commit_pending = 1U;
            s5_first_event_after_commit = 0U;
            for (f = 0; f < num_frames; f++) {
                s5_render_case(pFrames[f], stride, c);
                Xil_DCacheFlushRange((INTPTR)pFrames[f], stride * S5_CANVAS_H);
            }
            if (c->id != common_case_id) {
                s5_case_commits++;
                common_case_id = c->id;
            }
            xil_printf("S5_P1_SHOW case=%u boxes=%u stale=%u hud=%s/%s/%s/%s uniq_case_updates=%u\r\n",
                       c->id, c->nbox, c->stale, c->hud[0], c->hud[1], c->hud[2], c->hud[3],
                       (unsigned)s5_case_commits);

            for (sec = 1U; sec <= S5_DWELL_SECONDS; sec++) {
                XTime t_now;
                u32 dv, dm;
                u64 dt;
                usleep(1000000);
                XTime_GetTime(&t_now);
                dv = s5_vtc_events - v_prev;
                dm = s5_mm2s_events - m_prev;
                dt = (u64)t_now - (u64)t_prev;
                xil_printf("S5_FPS4 case=%u win=%u vtc_events=%u mm2s_events=%u dt_counts=%u "
                           "video_refresh_fps_x10=%d display_fps_x10=%d inference_fps=NA "
                           "mm2s_frames_reg=%u raw_mm2s_sr=%08X raw_vtc_isr=%08X "
                           "vtc_b12=%u vtc_b13=%u vtc_b16=%u vtc_other=%u spurious=%u\r\n",
                           c->id, (unsigned)sec, (unsigned)dv, (unsigned)dm, (unsigned)dt,
                           s5_fps10(dv, dt, count_rate), s5_fps10(dm, dt, count_rate),
                           (unsigned)s5_mm2s_frames(), (unsigned)s5_mm2s_last_sr,
                           (unsigned)s5_vtc_last_isr, (unsigned)s5_vtc_b12, (unsigned)s5_vtc_b13,
                           (unsigned)s5_vtc_b16, (unsigned)s5_vtc_other, (unsigned)s5_irq_spurious);
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
                xil_printf("S5_LAT case=%u commit_to_frame_complete_ns=NA "
                           "(no MM2S frame-complete event observed in window)\r\n", c->id);
            }
        }
        xil_printf("S5_P1_CYCLE_DONE\r\n");
    }
}