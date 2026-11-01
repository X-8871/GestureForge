/*
 * vtc_ctrl.c —— v_tc 6.2 生成器寄存器级初始化 + 回读校验
 *
 * 依据见 vtc_ctrl.h 文件头（xvtc_hw.h 偏移/位域 + xvtc.c 写序列 + P3a BD 预设值）。
 * 本文件不依赖 vtc 驱动库（BSP 未含），全部 Xil_In32/Xil_Out32 直写；
 * 也不依赖 printf/xil_printf —— 校验结果由调用方用 S5Vtc_Format*() 打印，
 * 这样同一份代码能在主机自检（printf）与裸机（xil_printf）下复用。
 */
#include "vtc_ctrl.h"

#include "s5_timebase.h"
#include "xil_io.h"

/* 编译器/总线屏障（与 vdma_ctrl.c 一致；主机自检时不需要） */
static inline void s5_vtc_mb(void)
{
#if defined(__GNUC__) && !defined(S5_HOST_TEST)
    __asm__ __volatile__("dsb" ::: "memory");
#endif
}

uint32_t S5Vtc_Read(const S5Vtc *vtc, uint32_t off)
{
    return Xil_In32(vtc->base + off);
}

void S5Vtc_Write(S5Vtc *vtc, uint32_t off, uint32_t val)
{
    Xil_Out32(vtc->base + off, val);
    s5_vtc_mb();
}

/* ---------------- 内部：定宽十六进制/十进制文本 ---------------- */

static uint32_t s5v_put(char *buf, uint32_t cap, uint32_t pos, char c)
{
    if (pos + 1u < cap) {
        buf[pos] = c;
        return pos + 1u;
    }
    return pos;
}

static uint32_t s5v_cat(char *buf, uint32_t cap, uint32_t pos, const char *s)
{
    while ((*s != '\0') && (pos + 1u < cap)) {
        buf[pos++] = *s++;
    }
    return pos;
}

static uint32_t s5v_hex8(char *buf, uint32_t cap, uint32_t pos, uint32_t v)
{
    static const char hex[] = "0123456789ABCDEF";
    int i;

    for (i = 7; i >= 0; i--) {
        pos = s5v_put(buf, cap, pos, hex[(v >> (unsigned)(i * 4)) & 0xFu]);
    }
    return pos;
}

static uint32_t s5v_u32(char *buf, uint32_t cap, uint32_t pos, uint32_t v)
{
    char tmp[10];
    uint32_t n = 0;

    do {
        tmp[n++] = (char)('0' + (v % 10u));
        v /= 10u;
    } while ((v != 0u) && (n < 10u));
    while (n > 0u) {
        pos = s5v_put(buf, cap, pos, tmp[--n]);
    }
    return pos;
}

static uint32_t s5v_end(char *buf, uint32_t cap, uint32_t pos)
{
    buf[(pos < cap) ? pos : (cap - 1u)] = '\0';
    return pos;
}

/* ---------------- 几何参数 ---------------- */

void S5Vtc_Default720p60(S5VtcTiming *t)
{
    if (t == 0) {
        return;
    }
    t->h_active = 1280u;
    t->h_total = 1650u;
    t->h_sync_width = 40u;
    t->h_back_porch = 220u;

    t->v_active = 720u;
    t->v_total = 750u;
    t->v_sync_width = 5u;
    t->v_back_porch = 20u;
}

/* ---------------- 复位 / 编程 / 校验 ---------------- */

int S5Vtc_Reset(S5Vtc *vtc, uint32_t timeout_us)
{
    uint64_t t0;
    uint32_t ctl;

    /* XVtc_Reset()：CTL |= RESET，随后等硬件自清 */
    ctl = S5Vtc_Read(vtc, S5_VTC_CTL);
    S5Vtc_Write(vtc, S5_VTC_CTL, ctl | S5_VTC_CTL_RESET);

    t0 = S5Ticks_Now();
    for (;;) {
        ctl = S5Vtc_Read(vtc, S5_VTC_CTL);
        if ((ctl & S5_VTC_CTL_RESET) == 0u) {
            return 0;
        }
        if (S5Ticks_Elapsed(t0, S5Ticks_FromUs(timeout_us))) {
            return -1;
        }
    }
}

static void s5_vtc_chk_add(S5Vtc *vtc, const char *name, uint32_t off, uint32_t want)
{
    if (vtc->n_chk < S5_VTC_MAX_CHK) {
        S5VtcChk *c = &vtc->chk[vtc->n_chk++];

        c->name = name;
        c->off = off;
        c->want = want;
        c->got = 0u;
        c->ok = 0;
    }
}

int S5Vtc_Program(S5Vtc *vtc, const S5VtcTiming *t)
{
    uint32_t h_front;
    uint32_t h_sync_start;
    uint32_t h_sync_end;
    uint32_t v_front;
    uint32_t v_sync_start;
    uint32_t v_sync_end;
    uint32_t val;

    if ((t == 0) || (vtc == 0)) {
        return -2;
    }
    if ((t->h_total == 0u) || (t->v_total == 0u) || (t->h_active == 0u) || (t->v_active == 0u)) {
        return -2;
    }
    if ((t->h_active + t->h_sync_width + t->h_back_porch) > t->h_total) {
        return -2; /* 前肩为负：几何不合法 */
    }
    if ((t->v_active + t->v_sync_width + t->v_back_porch) > t->v_total) {
        return -2;
    }

    h_front = t->h_total - t->h_active - t->h_sync_width - t->h_back_porch;
    h_sync_start = t->h_active + h_front;
    h_sync_end = h_sync_start + t->h_sync_width;

    v_front = t->v_total - t->v_active - t->v_sync_width - t->v_back_porch;
#if S5_VTC_VSYNC_USE_IP_PRESET
    /* v_tc 编码：GVSYNC = V0SyncStart + vactive - 1（见 XVtc_SetGenerator 源码），
     * 故 720p 的 725..730 在寄存器里是 724..729，与 P3a BD 的 IP 预设一致。 */
    v_sync_start = t->v_active + v_front - 1u;
#else
    v_sync_start = t->v_active + v_front;
#endif
    v_sync_end = v_sync_start + t->v_sync_width;

    vtc->n_chk = 0u;
    vtc->fail_count = 0u;

    /* 行总周期 */
    val = t->h_total & S5_VTC_SB_START_MASK;
    S5Vtc_Write(vtc, S5_VTC_GHSIZE, val);
    s5_vtc_chk_add(vtc, "GHSIZE", S5_VTC_GHSIZE, val);

    /* 场总行数（逐行扫描：场 1 = 场 0） */
    val = (t->v_total & S5_VTC_VSIZE_F0_MASK) |
          ((t->v_total << S5_VTC_VSIZE_F1_SHIFT) & S5_VTC_VSIZE_F1_MASK);
    S5Vtc_Write(vtc, S5_VTC_GVSIZE, val);
    s5_vtc_chk_add(vtc, "GVSIZE", S5_VTC_GVSIZE, val);

    /* 有效尺寸（行/场） */
    val = (t->h_active & S5_VTC_ASIZE_HORI_MASK) |
          ((t->v_active << S5_VTC_ASIZE_VERT_SHIFT) & S5_VTC_ASIZE_VERT_MASK);
    S5Vtc_Write(vtc, S5_VTC_GASIZE, val);
    s5_vtc_chk_add(vtc, "GASIZE", S5_VTC_GASIZE, val);

    val = (t->v_active << S5_VTC_ASIZE_VERT_SHIFT) & S5_VTC_ASIZE_VERT_MASK;
    S5Vtc_Write(vtc, S5_VTC_GASIZE_F1, val);
    s5_vtc_chk_add(vtc, "GASIZE_F1", S5_VTC_GASIZE_F1, val);

    /* 行同步起/止 */
    val = (h_sync_start & S5_VTC_SB_START_MASK) |
          ((h_sync_end << S5_VTC_SB_END_SHIFT) & S5_VTC_SB_END_MASK);
    S5Vtc_Write(vtc, S5_VTC_GHSYNC, val);
    s5_vtc_chk_add(vtc, "GHSYNC", S5_VTC_GHSYNC, val);

    /* 场同步起/止（场 0 / 场 1 同值） */
    val = (v_sync_start & S5_VTC_SB_START_MASK) |
          ((v_sync_end << S5_VTC_SB_END_SHIFT) & S5_VTC_SB_END_MASK);
    S5Vtc_Write(vtc, S5_VTC_GVSYNC, val);
    s5_vtc_chk_add(vtc, "GVSYNC", S5_VTC_GVSYNC, val);
    S5Vtc_Write(vtc, S5_VTC_GVSYNC_F1, val);
    s5_vtc_chk_add(vtc, "GVSYNC_F1", S5_VTC_GVSYNC_F1, val);

    /* 场消隐 / 场同步的水平起止（驱动默认：场消隐在行有效结束时，场同步在行同步起点） */
    val = (t->h_active & S5_VTC_SB_START_MASK) |
          ((t->h_active << S5_VTC_SB_END_SHIFT) & S5_VTC_SB_END_MASK);
    S5Vtc_Write(vtc, S5_VTC_GVBHOFF, val);
    s5_vtc_chk_add(vtc, "GVBHOFF", S5_VTC_GVBHOFF, val);

    val = (h_sync_start & S5_VTC_SB_START_MASK) |
          ((h_sync_start << S5_VTC_SB_END_SHIFT) & S5_VTC_SB_END_MASK);
    S5Vtc_Write(vtc, S5_VTC_GVSHOFF, val);
    s5_vtc_chk_add(vtc, "GVSHOFF", S5_VTC_GVSHOFF, val);

    /* 极性：720p 全正极性（BD：GEN_*_POLARITY 全 High） */
    val = S5_VTC_POL_ALL_HIGH;
    S5Vtc_Write(vtc, S5_VTC_GPOL, val);
    s5_vtc_chk_add(vtc, "GPOL", S5_VTC_GPOL, val);

    /* 编码：逐行扫描（PROG=0）、RGB（无 chroma 跳过） */
    val = 0u;
    S5Vtc_Write(vtc, S5_VTC_GFENC, val);
    s5_vtc_chk_add(vtc, "GFENC", S5_VTC_GFENC, val);

    return 0;
}

uint32_t S5Vtc_Verify(S5Vtc *vtc)
{
    uint32_t i;

    if (vtc == 0) {
        return 0xFFFFFFFFu;
    }
    vtc->fail_count = 0u;
    for (i = 0; i < vtc->n_chk; i++) {
        S5VtcChk *c = &vtc->chk[i];

        c->got = S5Vtc_Read(vtc, c->off);
        c->ok = (c->got == c->want) ? 1 : 0;
        if (!c->ok) {
            vtc->fail_count++;
        }
    }

    /* CTL：SW|GE 必须置位、RESET 必须自清 */
    vtc->ctl_got = S5Vtc_Read(vtc, S5_VTC_CTL);
    if (((vtc->ctl_got & (S5_VTC_CTL_SW | S5_VTC_CTL_GE)) != (S5_VTC_CTL_SW | S5_VTC_CTL_GE)) ||
        ((vtc->ctl_got & S5_VTC_CTL_RESET) != 0u)) {
        vtc->fail_count++;
    }
    return vtc->fail_count;
}

int S5Vtc_Init(S5Vtc *vtc, const S5VtcTiming *t, uint32_t timeout_us)
{
    uint32_t ctl;
    int rc;

    if ((vtc == 0) || (t == 0)) {
        return -2;
    }
    vtc->base = S5_VTC_BASE;
    vtc->n_chk = 0u;
    vtc->fail_count = 0u;

    /* 1) 判活：版本寄存器既不是全 0 也不是全 1 */
    vtc->version = S5Vtc_Read(vtc, S5_VTC_VER);
    if ((vtc->version == 0u) || (vtc->version == 0xFFFFFFFFu)) {
        return -2;
    }

    /* 2) 软复位 */
    rc = S5Vtc_Reset(vtc, timeout_us);
    if (rc != 0) {
        return -1;
    }

    /* 3) 生成器时序/极性/编码 */
    rc = S5Vtc_Program(vtc, t);
    if (rc != 0) {
        return -2;
    }

    /* 4) 使能：XVtc_Enable() → CTL.SW；XVtc_EnableGenerator() → CTL.GE */
    ctl = S5Vtc_Read(vtc, S5_VTC_CTL);
    ctl &= ~S5_VTC_CTL_RESET;
    ctl |= (S5_VTC_CTL_SW | S5_VTC_CTL_GE);
    S5Vtc_Write(vtc, S5_VTC_CTL, ctl);
    vtc->ctl_want = ctl;

    /* 5) 回读校验：失败不静默，返回 -3 */
    if (S5Vtc_Verify(vtc) != 0u) {
        return -3;
    }
    return 0;
}

/* ---------------- 文本输出 ---------------- */

uint32_t S5Vtc_FormatCheck(const S5Vtc *vtc, uint32_t idx, char *buf, uint32_t cap)
{
    const S5VtcChk *c;
    uint32_t p = 0u;

    if ((vtc == 0) || (buf == 0) || (cap < 8u)) {
        return 0u;
    }
    if (idx < vtc->n_chk) {
        c = &vtc->chk[idx];
        p = s5v_cat(buf, cap, p, c->name);
        p = s5v_cat(buf, cap, p, " @");
        p = s5v_hex8(buf, cap, p, vtc->base + c->off);
        p = s5v_cat(buf, cap, p, " want=");
        p = s5v_hex8(buf, cap, p, c->want);
        p = s5v_cat(buf, cap, p, " got=");
        p = s5v_hex8(buf, cap, p, c->got);
        p = s5v_cat(buf, cap, p, c->ok ? " OK" : " **MISMATCH**");
    } else {
        /* 最后一项：CTL */
        p = s5v_cat(buf, cap, p, "CTL     @");
        p = s5v_hex8(buf, cap, p, vtc->base + S5_VTC_CTL);
        p = s5v_cat(buf, cap, p, " want=");
        p = s5v_hex8(buf, cap, p, vtc->ctl_want);
        p = s5v_cat(buf, cap, p, " got=");
        p = s5v_hex8(buf, cap, p, vtc->ctl_got);
        p = s5v_cat(buf, cap, p, ((vtc->ctl_got & (S5_VTC_CTL_SW | S5_VTC_CTL_GE)) ==
                                  (S5_VTC_CTL_SW | S5_VTC_CTL_GE))
                                     ? " OK" : " **MISMATCH**");
    }
    s5v_end(buf, cap, p);
    return p;
}

uint32_t S5Vtc_FormatSummary(const S5Vtc *vtc, char *buf, uint32_t cap)
{
    uint32_t p = 0u;
    uint32_t total;

    if ((vtc == 0) || (buf == 0) || (cap < 8u)) {
        return 0u;
    }
    total = vtc->n_chk + 1u; /* + CTL */
    p = s5v_cat(buf, cap, p, "VTC verify: ");
    p = s5v_u32(buf, cap, p, total - vtc->fail_count);
    p = s5v_put(buf, cap, p, '/');
    p = s5v_u32(buf, cap, p, total);
    if (vtc->fail_count == 0u) {
        p = s5v_cat(buf, cap, p, " OK");
    } else {
        p = s5v_cat(buf, cap, p, " **FAIL(");
        p = s5v_u32(buf, cap, p, vtc->fail_count);
        p = s5v_cat(buf, cap, p, ")**");
    }
    s5v_end(buf, cap, p);
    return p;
}

uint32_t S5Vtc_FormatTiming(const S5Vtc *vtc, char *buf, uint32_t cap)
{
    /* 从已编程的 chk[] 反读不方便，这里直接用寄存器回读重建可读摘要 */
    uint32_t p = 0u;
    uint32_t ghsync;
    uint32_t gvsync;
    uint32_t gasize;

    if ((vtc == 0) || (buf == 0) || (cap < 16u)) {
        return 0u;
    }
    gasize = S5Vtc_Read(vtc, S5_VTC_GASIZE);
    ghsync = S5Vtc_Read(vtc, S5_VTC_GHSYNC);
    gvsync = S5Vtc_Read(vtc, S5_VTC_GVSYNC);

    p = s5v_cat(buf, cap, p, "VTC timing ");
    p = s5v_u32(buf, cap, p, gasize & S5_VTC_ASIZE_HORI_MASK);
    p = s5v_put(buf, cap, p, 'x');
    p = s5v_u32(buf, cap, p, (gasize & S5_VTC_ASIZE_VERT_MASK) >> S5_VTC_ASIZE_VERT_SHIFT);
    p = s5v_cat(buf, cap, p, " Htotal=");
    p = s5v_u32(buf, cap, p, S5Vtc_Read(vtc, S5_VTC_GHSIZE) & S5_VTC_SB_START_MASK);
    p = s5v_cat(buf, cap, p, " Hsync=");
    p = s5v_u32(buf, cap, p, ghsync & S5_VTC_SB_START_MASK);
    p = s5v_cat(buf, cap, p, "..");
    p = s5v_u32(buf, cap, p, (ghsync & S5_VTC_SB_END_MASK) >> S5_VTC_SB_END_SHIFT);
    p = s5v_cat(buf, cap, p, " Vtotal=");
    p = s5v_u32(buf, cap, p, S5Vtc_Read(vtc, S5_VTC_GVSIZE) & S5_VTC_VSIZE_F0_MASK);
    p = s5v_cat(buf, cap, p, " Vsync=");
    p = s5v_u32(buf, cap, p, gvsync & S5_VTC_SB_START_MASK);
    p = s5v_cat(buf, cap, p, "..");
    p = s5v_u32(buf, cap, p, (gvsync & S5_VTC_SB_END_MASK) >> S5_VTC_SB_END_SHIFT);
    s5v_end(buf, cap, p);
    return p;
}