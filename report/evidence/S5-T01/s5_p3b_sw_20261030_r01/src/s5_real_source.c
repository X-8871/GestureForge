/*
 * s5_real_source.c —— 真实数据源适配实现（纯函数，可主机自检）
 *
 * ABI 见 s5_result_abi.h；回退判据见 s5_real_source.h。
 */
#include "s5_real_source.h"

/* ---------------- 源名字 / 失败原因 ---------------- */

const char *S5Src_Name(uint32_t kind)
{
    switch (kind) {
    case S5_SRC_REAL:
        return "real";
    case S5_SRC_SIM:
        return "sim";
    case S5_SRC_TEST:
        return "test";
    default:
        return "none";
    }
}

const char *S5Src_Reason(int parse_rc)
{
    switch (parse_rc) {
    case S5_PARSE_OK:
        return 0;
    case S5_PARSE_ERR_MAGIC:
        return "result_magic_mismatch";
    case S5_PARSE_ERR_NOT_VALID:
        return "result_not_valid";
    case S5_PARSE_ERR_TORN:
        return "result_torn";
    case S5_PARSE_ERR_SHAPE:
        return "result_shape_invalid";
    default:
        return "result_unknown_error";
    }
}

/* ---------------- 结果块解析 ---------------- */

int S5Real_Parse(const uint32_t *blk, S5RealBlock *out)
{
    uint32_t frame_id_first;
    uint32_t frame_id_second;
    uint32_t i;
    uint32_t n;

    if ((blk == 0) || (out == 0)) {
        return S5_PARSE_ERR_SHAPE;
    }

    /* 1) magic 必须先判（lead 冻结：读端先读 magic + status） */
    out->magic = blk[S5_RESULT_W_MAGIC];
    if (out->magic != S5_RESULT_MAGIC) {
        return S5_PARSE_ERR_MAGIC;
    }

    /* 2) status.valid */
    out->status = blk[S5_RESULT_W_STATUS];
    out->valid = out->status & S5_RESULT_ST_VALID;
    if (out->valid == 0u) {
        return S5_PARSE_ERR_NOT_VALID;
    }
    out->overrun = (out->status & S5_RESULT_ST_OVERRUN) ? 1u : 0u;
    out->stale = (out->status & S5_RESULT_ST_STALE) ? 1u : 0u;

    /* 3) 双重读 frame_id：生产端可能在写，前后不一致就判 torn（本帧回退） */
    frame_id_first = blk[S5_RESULT_W_FRAME_ID];
    out->frame_id = frame_id_first;

    out->n_dets = blk[S5_RESULT_W_N_DETS];
    n = out->n_dets;
    if (n > S5_RESULT_MAX_DETS) {
        return S5_PARSE_ERR_SHAPE;
    }
    out->n = n;

    out->cap_ticks = ((uint64_t)blk[S5_RESULT_W_CAP_HI] << 32) | (uint64_t)blk[S5_RESULT_W_CAP_LO];
    out->inf_ticks = ((uint64_t)blk[S5_RESULT_W_INF_HI] << 32) | (uint64_t)blk[S5_RESULT_W_INF_LO];

    /* 4) 检测项：每项 16 B = 4 个 u32
     *    w0 = x | y<<16, w1 = w | h<<16, w2 = cls | score<<8 | reserved<<16, w3 = 填充 */
    for (i = 0; i < n; i++) {
        const uint32_t *w = &blk[(S5_RESULT_DETS_OFFSET / 4u) + i * (S5_RESULT_DET_BYTES / 4u)];

        out->det[i].x = (uint16_t)(w[0] & 0xFFFFu);
        out->det[i].y = (uint16_t)((w[0] >> 16) & 0xFFFFu);
        out->det[i].w = (uint16_t)(w[1] & 0xFFFFu);
        out->det[i].h = (uint16_t)((w[1] >> 16) & 0xFFFFu);
        out->det[i].cls = (uint8_t)(w[2] & 0xFFu);
        out->det[i].score_q8 = (uint8_t)((w[2] >> 8) & 0xFFu);
        out->det[i].reserved = (uint16_t)((w[2] >> 16) & 0xFFFFu);
        out->det[i].pad = w[3];
    }

    frame_id_second = blk[S5_RESULT_W_FRAME_ID];
    if (frame_id_second != frame_id_first) {
        return S5_PARSE_ERR_TORN;
    }
    return S5_PARSE_OK;
}

/* ---------------- 结果块 → 每帧信息 ---------------- */

uint32_t S5Real_ScoreToPct(uint32_t score_q8)
{
    uint32_t q = (score_q8 > 255u) ? 255u : score_q8;
    uint32_t pct = (q * 100u + 127u) / 255u;

    return (pct > 100u) ? 100u : pct;
}

void S5Real_ToFrameInfo(const S5RealBlock *b, uint64_t now_ticks, S5FrameInfo *info)
{
    uint64_t age_ticks;
    uint64_t lat_ticks;
    uint64_t age_ms;
    uint64_t lat_ms;
    uint32_t i;

    if ((b == 0) || (info == 0)) {
        return;
    }

    info->frame_id = b->frame_id;
    /* fps 由调用方的滑动窗口填；这里先清零，避免沿用上一帧残留 */
    info->fps_cap_x10 = 0u;
    info->fps_inf_x10 = 0u;
    info->fps_dis_x10 = 0u;

    /* 时间戳可能“在未来”（时钟还没走到）→ 按 0 处理，不产生回绕的巨大 ms */
    age_ticks = (now_ticks >= b->cap_ticks) ? (now_ticks - b->cap_ticks) : 0u;
    lat_ticks = (now_ticks >= b->inf_ticks) ? (now_ticks - b->inf_ticks) : 0u;

    age_ms = S5Ticks_ToMs(age_ticks);
    lat_ms = S5Ticks_ToMs(lat_ticks);
    info->age_ms = (uint16_t)((age_ms > 0xFFFFu) ? 0xFFFFu : age_ms);
    info->latency_ms = (uint16_t)((lat_ms > 0xFFFFu) ? 0xFFFFu : lat_ms);

    info->status = S5_ST_CAM_OK | S5_ST_INF_OK;
    if (b->stale != 0u) {
        info->status |= S5_ST_STALE;
    }
    if (b->overrun != 0u) {
        info->status |= S5_ST_OVERRUN;
    }
    if (info->age_ms > S5_AGE_LIMIT_MS) {
        info->status |= S5_ST_AGE_OVER;
    }

    info->det_count = (uint8_t)((b->n > S5_MAX_DET) ? S5_MAX_DET : b->n);
    for (i = 0; i < info->det_count; i++) {
        info->det[i].x = (int16_t)b->det[i].x;
        info->det[i].y = (int16_t)b->det[i].y;
        info->det[i].w = (int16_t)b->det[i].w;
        info->det[i].h = (int16_t)b->det[i].h;
        info->det[i].cls = (uint8_t)((b->det[i].cls < S5_CLASS_NUM) ? b->det[i].cls : 0u);
        info->det[i].score = (uint8_t)S5Real_ScoreToPct(b->det[i].score_q8);
    }
    info->src_kind = S5_SRC_REAL;
}

/* ---------------- 原始画面 ---------------- */

int S5Real_IsBlank(const uint8_t *raw, uint32_t bytes)
{
    uint32_t i;

    if (raw == 0) {
        return 1;
    }
    /* 命中第一个非 0 字节就返回（真实画面通常第 1 个像素就有内容 → 几乎零成本）；
     * 全 0 时才扫满整幅（921,600 B），作为“相机未启动”的判据。 */
    for (i = 0; i < bytes; i++) {
        if (raw[i] != 0u) {
            return 0;
        }
    }
    return 1;
}

void S5Real_BgrToCanvas(const uint8_t *raw, uint32_t *canvas, uint32_t pixels)
{
    uint32_t i;

    if ((raw == 0) || (canvas == 0)) {
        return;
    }
    for (i = 0; i < pixels; i++) {
        uint8_t b = raw[i * 3u + 0u];
        uint8_t g = raw[i * 3u + 1u];
        uint8_t r = raw[i * 3u + 2u];

        canvas[i] = ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
    }
}

/* ---------------- FPS 滑动窗口 ---------------- */

void S5Fps_Reset(S5FpsWin *w)
{
    if (w != 0) {
        w->t_first = 0u;
        w->t_last = 0u;
        w->n = 0u;
    }
}

void S5Fps_Add(S5FpsWin *w, uint64_t t)
{
    if (w == 0) {
        return;
    }
    if (w->n == 0u) {
        w->t_first = t;
    }
    w->t_last = t;
    w->n++;
}

uint32_t S5Fps_GetX10(const S5FpsWin *w)
{
    uint64_t dt;
    uint64_t fps_x10;

    if ((w == 0) || (w->n < 2u)) {
        return 0u;
    }
    if (w->t_last <= w->t_first) {
        return 0u;
    }
    dt = w->t_last - w->t_first;
    /* fps×10 = (n-1) × S5_GT_HZ × 10 / dt_ticks（先乘后除，64 位；n≤180 时约 6e11，不溢出） */
    fps_x10 = ((uint64_t)(w->n - 1u) * S5_GT_HZ * 10u) / dt;
    return (fps_x10 > 0xFFFFu) ? 0xFFFFu : (uint32_t)fps_x10;
}

uint32_t S5Fps_Get(const S5FpsWin *w)
{
    return S5Fps_GetX10(w) / 10u;
}