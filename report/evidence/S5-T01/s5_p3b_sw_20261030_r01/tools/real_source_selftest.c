/*
 * real_source_selftest.c —— 真实数据源离线自检（主机端，无板卡）
 *
 * 目的：把**真正上板的两个源文件**（s5_real_source.c + s5_display_app.c）原样编译运行，验证：
 *   1) 合法结果块 + 真实 640×480 BGR888 画面 → src="real"，渲染出含真实画面/检测框/信息栏的 PNG；
 *   2) magic 错误 → 回退模拟源，RESULT 带 reason（src="sim"，pass=0）；
 *   3) 结果块合法但 raw 全 0 → 测试图案回退（src="test"，pass=1，reason="raw_frame_blank"）；
 *   4) status.bit2 → 面板显示 STALE / 状态位含 S5_ST_STALE。
 *
 * 画面用现成 fixture 的副本（640×480 BGR888，921,600 B）；缺文件时退化为合成渐变，便于无 fixture 环境跑。
 *
 * 编译（MinGW gcc）：
 *   gcc -std=gnu11 -O2 -Wall -Wextra -DS5_HOST_TEST -Isrc \
 *       tools/real_source_selftest.c src/s5_real_source.c src/s5_display_app.c \
 *       -o build/host_real_source_selftest.exe
 */
#define S5_HOST_TEST 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "s5_display_app.h"
#include "s5_real_source.h"
#include "s5_result_abi.h"

#define FIXTURE_DEFAULT "fixtures/fixture_fist_000_640x480_bgr888.raw"
#define RUN_FRAMES 36u

/* 假时钟：由测试显式推进，保证 RESULT 里的 fps/age 可复现 */
static uint64_t g_now;

uint64_t S5Ticks_Now(void)
{
    return g_now;
}

/* ---------------- 结果块构造 ---------------- */

static void block_reset(uint32_t *blk)
{
    memset(blk, 0, S5_RESULT_BLOCK_BYTES);
}

static void block_set_header(uint32_t *blk, uint32_t frame_id, uint32_t n_dets,
                             uint64_t cap, uint64_t inf, uint32_t status)
{
    blk[S5_RESULT_W_MAGIC] = S5_RESULT_MAGIC;
    blk[S5_RESULT_W_FRAME_ID] = frame_id;
    blk[S5_RESULT_W_N_DETS] = n_dets;
    blk[S5_RESULT_W_CAP_LO] = (uint32_t)(cap & 0xFFFFFFFFu);
    blk[S5_RESULT_W_CAP_HI] = (uint32_t)(cap >> 32);
    blk[S5_RESULT_W_INF_LO] = (uint32_t)(inf & 0xFFFFFFFFu);
    blk[S5_RESULT_W_INF_HI] = (uint32_t)(inf >> 32);
    blk[S5_RESULT_W_STATUS] = status;
}

/* 每项 16 B = 4 个 u32：w0=x|y<<16, w1=w|h<<16, w2=cls|score<<8, w3=填充 */
static void block_set_det(uint32_t *blk, uint32_t idx,
                          uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                          uint8_t cls, uint8_t score_q8)
{
    uint32_t *d = &blk[(S5_RESULT_DETS_OFFSET / 4u) + idx * (S5_RESULT_DET_BYTES / 4u)];

    d[0] = ((uint32_t)y << 16) | x;
    d[1] = ((uint32_t)h << 16) | w;
    d[2] = ((uint32_t)score_q8 << 8) | cls;
    d[3] = 0u;
}

/* ---------------- 工具 ---------------- */

static int ppm_write(const char *path, const uint32_t *fb)
{
    FILE *f = fopen(path, "wb");
    int y;
    int x;

    if (f == 0) {
        fprintf(stderr, "cannot write %s\n", path);
        return -1;
    }
    fprintf(f, "P6\n%d %d\n255\n", S5_CANVAS_W, S5_CANVAS_H);
    for (y = 0; y < S5_CANVAS_H; y++) {
        for (x = 0; x < S5_CANVAS_W; x++) {
            uint32_t c = fb[(size_t)y * S5_CANVAS_W + (size_t)x];
            unsigned char rgb[3];

            rgb[0] = (unsigned char)((c >> 16) & 0xFFu);
            rgb[1] = (unsigned char)((c >> 8) & 0xFFu);
            rgb[2] = (unsigned char)(c & 0xFFu);
            fwrite(rgb, 1, 3, f);
        }
    }
    fclose(f);
    printf("wrote %s\n", path);
    return 0;
}

static uint8_t *load_raw(const char *path)
{
    FILE *f;
    long sz;
    uint8_t *buf;
    size_t got;
    uint32_t i;

    buf = (uint8_t *)malloc(S5_RAW_FRAME_BYTES);
    if (buf == 0) {
        return 0;
    }
    f = fopen(path, "rb");
    if (f != 0) {
        sz = (long)S5_RAW_FRAME_BYTES;
        got = fread(buf, 1, (size_t)sz, f);
        fclose(f);
        if (got == (size_t)sz) {
            printf("raw fixture: %s (%u B)\n", path, (unsigned)sz);
            return buf;
        }
        fprintf(stderr, "raw fixture 尺寸不符（%u B），改用合成图\n", (unsigned)got);
    } else {
        fprintf(stderr, "raw fixture 缺失：%s，改用合成图\n", path);
    }
    /* 合成：斜向渐变 + 一个亮块（BGR 顺序） */
    for (i = 0; i < (uint32_t)S5_RAW_FRAME_BYTES; i += 3u) {
        uint32_t px = i / 3u;
        uint32_t x = px % S5_RAW_FRAME_W;
        uint32_t y = px / S5_RAW_FRAME_W;

        buf[i + 0u] = (uint8_t)((x * 180u) / (S5_RAW_FRAME_W - 1u));
        buf[i + 1u] = (uint8_t)((y * 180u) / (S5_RAW_FRAME_H - 1u));
        buf[i + 2u] = (uint8_t)(80u + ((x + y) & 0x3Fu));
    }
    return buf;
}

/* ---------------- 用例 ---------------- */

static int run_real_case(const uint8_t *raw, uint32_t *blk, uint32_t *cam, uint32_t *fb,
                         const char *ppm)
{
    S5RunStats st;
    S5RealBlock rb;
    S5FpsWin wc;
    S5FpsWin wi;
    S5FpsWin wd;
    S5FrameInfo info;
    char res[224];
    uint32_t i;
    uint32_t last_fid = 0xFFFFFFFFu;
    uint64_t cap = 0u;
    uint64_t inf = 0u;
    int rc = 0;

    memset(&info, 0, sizeof(info));
    S5Fps_Reset(&wc);
    S5Fps_Reset(&wi);
    S5Fps_Reset(&wd);

    /* 真实相机 30 fps，显示 60 fps：每 2 个显示帧产生一份新结果。
     * 时间戳按“本帧显示时刻”反推：采集结束 ≈ 32 ms 前、推理完成 ≈ 8 ms 前
     * （即 age≈32 ms、latency≈8 ms，均在 G0 的 33 ms 上限内）。 */
    for (i = 0; i < RUN_FRAMES; i++) {
        uint32_t frame_id = i / 2u;

        g_now += S5Ticks_FromUs(16667u); /* 60 Hz 显示节拍 */
        cap = (g_now > S5Ticks_FromUs(32000u)) ? (g_now - S5Ticks_FromUs(32000u)) : 0u;
        inf = (g_now > S5Ticks_FromUs(8000u)) ? (g_now - S5Ticks_FromUs(8000u)) : 0u;

        block_reset(blk);
        block_set_header(blk, frame_id, 3u, cap, inf,
                         S5_RESULT_ST_VALID);
        block_set_det(blk, 0u, 120u, 90u, 160u, 140u, 0u, 220u);
        block_set_det(blk, 1u, 380u, 260u, 120u, 110u, 2u, 235u);
        block_set_det(blk, 2u, 40u, 330u, 180u, 100u, 4u, 190u);

        if (S5Real_Parse(blk, &rb) != S5_PARSE_OK) {
            printf("case1: 合法块解析失败（不应发生）\n");
            return 1;
        }
        S5Real_ToFrameInfo(&rb, g_now, &info);
        /* 真实源：raw→画布 */
        S5Real_BgrToCanvas(raw, cam, S5_RAW_FRAME_W * S5_RAW_FRAME_H);
        if (rb.frame_id != last_fid) {
            S5Fps_Add(&wc, rb.cap_ticks);
            S5Fps_Add(&wi, rb.inf_ticks);
            last_fid = rb.frame_id;
        }
        S5Fps_Add(&wd, g_now);
        /* 面板显示实时 FPS（与板上逻辑一致：窗口 ×10 回填） */
        info.fps_cap_x10 = (uint16_t)S5Fps_GetX10(&wc);
        info.fps_inf_x10 = (uint16_t)S5Fps_GetX10(&wi);
        info.fps_dis_x10 = (uint16_t)S5Fps_GetX10(&wd);
        S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_CAM);
    }

    st.pass = (uint32_t)S5Display_CheckFrame(fb);
    st.src = S5Src_Name(S5_SRC_REAL);
    st.reason = 0;
    st.frames = RUN_FRAMES;
    st.vcnt = RUN_FRAMES;
    st.vdma_err = 0u;
    st.fps_cap = S5Fps_Get(&wc);
    st.fps_inf = S5Fps_Get(&wi);
    st.fps_dis = S5Fps_Get(&wd);
    st.latency_ms = info.latency_ms;
    st.age_ms = info.age_ms;
    S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
    printf("case1 (real): %s\n", res);
    printf("case1 status=0x%04X det=%u age=%u lat=%u\n",
           (unsigned)info.status, (unsigned)info.det_count,
           (unsigned)info.age_ms, (unsigned)info.latency_ms);
    if ((info.det_count != 3u) || (st.pass == 0u) || (st.fps_cap < 25u) || (st.fps_cap > 35u)) {
        printf("case1: FAIL（det/fps/pass 不符合预期）\n");
        rc = 1;
    }
    rc |= ppm_write(ppm, fb);
    return rc;
}

static int run_magic_bad_case(uint32_t *blk, uint32_t *cam, uint32_t *fb, const char *ppm)
{
    S5RunStats st;
    S5RealBlock rb;
    S5FrameInfo info;
    char res[224];
    int parse_rc;
    int rc = 0;

    block_reset(blk);
    block_set_header(blk, 7u, 1u, 0u, 0u, S5_RESULT_ST_VALID);
    blk[S5_RESULT_W_MAGIC] = 0xDEADBEEFu; /* 故意写错 magic */

    parse_rc = S5Real_Parse(blk, &rb);
    printf("case2 (magic bad): parse_rc=%d reason=%s\n",
           parse_rc, (S5Src_Reason(parse_rc) != 0) ? S5Src_Reason(parse_rc) : "(null)");
    /* 回退模拟源并渲染 */
    S5Sim_NextFrame(&info);
    S5Sim_CameraFrame(cam, info.frame_id);
    S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_CAM);

    st.pass = 0u; /* 真实源不可用：判据给出可读失败原因 */
    st.src = S5Src_Name(S5_SRC_SIM);
    st.reason = S5Src_Reason(parse_rc);
    st.frames = 1u;
    st.vcnt = 0u;
    st.vdma_err = 0u;
    st.fps_cap = (uint32_t)(info.fps_cap_x10 / 10u);
    st.fps_inf = 0u;
    st.fps_dis = (uint32_t)(info.fps_dis_x10 / 10u);
    st.latency_ms = info.latency_ms;
    st.age_ms = info.age_ms;
    S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
    printf("case2 (fallback sim): %s\n", res);
    rc |= ppm_write(ppm, fb);
    return ((parse_rc == S5_PARSE_ERR_MAGIC) && (st.reason != 0) && (rc == 0)) ? 0 : 1;
}

static int run_blank_case(uint32_t *blk, uint32_t *cam, uint32_t *fb, const char *ppm)
{
    S5RunStats st;
    S5RealBlock rb;
    S5FrameInfo info;
    uint8_t *zero_raw;
    char res[224];
    int blank;

    zero_raw = (uint8_t *)calloc(1, S5_RAW_FRAME_BYTES); /* 全 0 = 相机未启动 */
    if (zero_raw == 0) {
        return 1;
    }
    block_reset(blk);
    block_set_header(blk, 3u, 1u,
                     g_now - S5Ticks_FromUs(32000u), /* age ≈ 32 ms */
                     g_now - S5Ticks_FromUs(8000u),  /* latency ≈ 8 ms */
                     S5_RESULT_ST_VALID);
    block_set_det(blk, 0u, 300u, 200u, 120u, 90u, 1u, 210u);
    if (S5Real_Parse(blk, &rb) != S5_PARSE_OK) {
        free(zero_raw);
        return 1;
    }
    blank = S5Real_IsBlank(zero_raw, S5_RAW_FRAME_BYTES);
    printf("case3 (raw blank): S5Real_IsBlank=%d\n", blank);

    S5Real_ToFrameInfo(&rb, g_now, &info);
    info.src_kind = S5_SRC_TEST;
    /* 空白 → 视频区测试图案；检测框仍来自结果块 */
    S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_TEST);

    st.pass = (uint32_t)S5Display_CheckFrame(fb); /* 显示仍可用 → pass=1 */
    st.src = S5Src_Name(S5_SRC_TEST);
    st.reason = "raw_frame_blank";
    st.frames = 1u;
    st.vcnt = 0u;
    st.vdma_err = 0u;
    st.fps_cap = 0u;
    st.fps_inf = 0u;
    st.fps_dis = 0u;
    st.latency_ms = info.latency_ms;
    st.age_ms = info.age_ms;
    S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
    printf("case3 (fallback test): %s\n", res);
    free(zero_raw);
    return ((blank == 1) && (st.pass == 1u) && (ppm_write(ppm, fb) == 0)) ? 0 : 1;
}

static int run_stale_case(uint32_t *blk, uint32_t *cam, uint32_t *fb, const char *ppm)
{
    S5RealBlock rb;
    S5FrameInfo info;

    block_reset(blk);
    block_set_header(blk, 9u, 1u, g_now - S5Ticks_FromUs(50000u), g_now - S5Ticks_FromUs(45000u),
                     S5_RESULT_ST_VALID | S5_RESULT_ST_STALE);
    block_set_det(blk, 0u, 260u, 180u, 140u, 120u, 3u, 200u);
    if (S5Real_Parse(blk, &rb) != S5_PARSE_OK) {
        return 1;
    }
    memset(&info, 0, sizeof(info));
    S5Real_ToFrameInfo(&rb, g_now, &info);
    printf("case4 (stale): status=0x%04X stale_bit=%u age=%u ms\n",
           (unsigned)info.status, (unsigned)((info.status & S5_ST_STALE) ? 1u : 0u),
           (unsigned)info.age_ms);
    S5Display_RenderFrame(fb, cam, &info, S5_DMA_RUN);
    return ((info.status & S5_ST_STALE) != 0u) ? (ppm_write(ppm, fb) != 0) : 1;
}

int main(int argc, char **argv)
{
    const char *fixture = (argc > 1) ? argv[1] : FIXTURE_DEFAULT;
    uint8_t *raw;
    uint32_t *blk;
    uint32_t *cam;
    uint32_t *fb;
    int fail = 0;

    printf("==== S5 真实数据源离线自检（ABI@0x%08X, raw@0x%08X）====\n",
           S5_RESULT_BASE, S5_RAW_FRAME_BASE);
    g_now = 1000000u;

    raw = load_raw(fixture);
    blk = (uint32_t *)calloc(1, S5_RESULT_BLOCK_BYTES);
    cam = (uint32_t *)malloc((size_t)S5_CAM_W * S5_CAM_H * 4u);
    fb = (uint32_t *)malloc(S5_FB_BYTES);
    if ((raw == 0) || (blk == 0) || (cam == 0) || (fb == 0)) {
        fprintf(stderr, "OOM\n");
        return 1;
    }

    fail |= run_real_case(raw, blk, cam, fb, "build/frame_real.ppm");
    fail |= run_magic_bad_case(blk, cam, fb, "build/frame_fallback_sim.ppm");
    fail |= run_blank_case(blk, cam, fb, "build/frame_test_fallback.ppm");
    fail |= run_stale_case(blk, cam, fb, "build/frame_stale.ppm");

    free(fb);
    free(cam);
    free(blk);
    free(raw);
    printf("==== real-source selftest: %s ====\n", (fail == 0) ? "PASS" : "FAIL");
    return (fail == 0) ? 0 : 1;
}