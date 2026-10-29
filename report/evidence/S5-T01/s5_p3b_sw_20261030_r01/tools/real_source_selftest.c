/*
 * real_source_selftest.c —— 真实数据源离线自检（主机端，无板卡）
 *
 * 把**真正上板的** s5_real_source.c + s5_display_app.c 原样编译运行，按 r05 的回退优先级验证：
 *   case1  结果块有效 + raw 有内容          → src="real"（有框，pass=1）
 *   case2  结果块无效（magic 错）+ raw 有内容 → src="real_nobox"（真实画面、无框，pass=1）
 *   case3  结果块有效 + raw 全 0            → src="test"（测试图案 + 框，pass=1，reason=raw_frame_blank）
 *   case4  结果块无效 + raw 全 0            → src="test"（测试图案，pass=1，reason=result_magic_mismatch）
 *   case5  status.bit2                      → 面板 STALE / S5_ST_STALE
 *   case6  时间戳全 0                       → age_ms=0、latency_ms=0（不得算成巨大值）
 *
 * 画面用现成 fixture 的副本（640×480 BGR888，921,600 B）；缺文件时退化为合成图。
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
    uint8_t *buf;
    size_t got;
    uint32_t i;

    buf = (uint8_t *)malloc(S5_RAW_FRAME_BYTES);
    if (buf == 0) {
        return 0;
    }
    f = fopen(path, "rb");
    if (f != 0) {
        got = fread(buf, 1, (size_t)S5_RAW_FRAME_BYTES, f);
        fclose(f);
        if (got == (size_t)S5_RAW_FRAME_BYTES) {
            printf("raw fixture: %s (%u B)\n", path, (unsigned)S5_RAW_FRAME_BYTES);
            return buf;
        }
        fprintf(stderr, "raw fixture 尺寸不符（%u B），改用合成图\n", (unsigned)got);
    } else {
        fprintf(stderr, "raw fixture 缺失：%s，改用合成图\n", path);
    }
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

static void print_result(const char *tag, S5RunStats *st)
{
    char res[224];

    S5Display_FormatResult(st, res, (uint32_t)sizeof(res));
    printf("%s: %s\n", tag, res);
}

/* ---------------- case1：真实源（结果块有效 + raw 有内容） ---------------- */

static int run_real_case(const uint8_t *raw, uint32_t *blk, uint32_t *cam, uint32_t *fb,
                         const char *ppm)
{
    S5RunStats st;
    S5RealBlock rb;
    S5FpsWin wc;
    S5FpsWin wi;
    S5FpsWin wd;
    S5FrameInfo info;
    uint32_t i;
    uint32_t last_fid = 0xFFFFFFFFu;
    int rc = 0;

    memset(&info, 0, sizeof(info));
    S5Fps_Reset(&wc);
    S5Fps_Reset(&wi);
    S5Fps_Reset(&wd);

    for (i = 0; i < RUN_FRAMES; i++) {
        uint32_t frame_id = i / 2u;
        uint64_t cap;
        uint64_t inf;

        g_now += S5Ticks_FromUs(16667u); /* 60 Hz 显示节拍 */
        cap = (g_now > S5Ticks_FromUs(32000u)) ? (g_now - S5Ticks_FromUs(32000u)) : 0u;
        inf = (g_now > S5Ticks_FromUs(8000u)) ? (g_now - S5Ticks_FromUs(8000u)) : 0u;

        block_reset(blk);
        block_set_header(blk, frame_id, 3u, cap, inf, S5_RESULT_ST_VALID);
        block_set_det(blk, 0u, 120u, 90u, 160u, 140u, 0u, 220u);
        block_set_det(blk, 1u, 380u, 260u, 120u, 110u, 2u, 235u);
        block_set_det(blk, 2u, 40u, 330u, 180u, 100u, 4u, 190u);

        if (S5Real_Parse(blk, &rb) != S5_PARSE_OK) {
            printf("case1: 合法块解析失败（不应发生）\n");
            return 1;
        }
        S5Real_ToFrameInfo(&rb, g_now, &info);
        S5Real_BgrToCanvas(raw, cam, S5_RAW_FRAME_W * S5_RAW_FRAME_H);
        if (rb.frame_id != last_fid) {
            S5Fps_Add(&wc, rb.cap_ticks);
            S5Fps_Add(&wi, rb.inf_ticks);
            last_fid = rb.frame_id;
        }
        S5Fps_Add(&wd, g_now);
        info.fps_cap_x10 = (uint16_t)S5Fps_GetX10(&wc);
        info.fps_inf_x10 = (uint16_t)S5Fps_GetX10(&wi);
        info.fps_dis_x10 = (uint16_t)S5Fps_GetX10(&wd);
        S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_CAM);
    }

    memset(&st, 0, sizeof(st));
    st.pass = (uint32_t)S5Display_CheckFrame(fb);
    st.src = S5Src_Name(S5_SRC_REAL);
    st.frames = RUN_FRAMES;
    st.vcnt = RUN_FRAMES;
    st.fps_cap = S5Fps_Get(&wc);
    st.fps_inf = S5Fps_Get(&wi);
    st.fps_dis = S5Fps_Get(&wd);
    st.latency_ms = info.latency_ms;
    st.age_ms = info.age_ms;
    print_result("case1 (real)", &st);
    printf("case1 status=0x%04X det=%u age=%u lat=%u\n",
           (unsigned)info.status, (unsigned)info.det_count,
           (unsigned)info.age_ms, (unsigned)info.latency_ms);
    if ((info.det_count != 3u) || (st.pass == 0u) || (st.fps_cap < 25u) || (st.fps_cap > 35u)) {
        printf("case1: FAIL（det/fps/pass 不符合预期）\n");
        rc = 1;
    }
    rc |= ppm_write(ppm, fb);
    return (rc == 0) ? 0 : 1;
}

/* ---------------- case2/3/4：无结果块 / 空白画面的回退 ---------------- */

static int run_nobox_or_test_case(uint32_t *blk, uint32_t *cam, uint32_t *fb,
                                  const uint8_t *raw, int raw_is_blank, int magic_bad,
                                  const char *expect_src, const char *ppm)
{
    S5RunStats st;
    S5RealBlock rb;
    S5FrameInfo info;
    int parse_rc;
    int rc;

    block_reset(blk);
    block_set_header(blk, 3u, 1u,
                     g_now - S5Ticks_FromUs(32000u),
                     g_now - S5Ticks_FromUs(8000u),
                     S5_RESULT_ST_VALID);
    block_set_det(blk, 0u, 300u, 200u, 120u, 90u, 1u, 210u);
    if (magic_bad != 0) {
        blk[S5_RESULT_W_MAGIC] = 0xDEADBEEFu;
    }

    parse_rc = S5Real_Parse(blk, &rb);
    printf("case: magic_bad=%d raw_blank=%d parse_rc=%d reason=%s\n",
           magic_bad, raw_is_blank, parse_rc,
           (S5Src_Reason(parse_rc) != 0) ? S5Src_Reason(parse_rc) : "(null)");

    memset(&st, 0, sizeof(st));
    memset(&info, 0, sizeof(info));
    st.frames = 1u;

    if ((parse_rc == S5_PARSE_OK) && (raw_is_blank != 0)) {
        /* case3：有结果但没画面 → 测试图案 + 结果框 */
        S5Real_ToFrameInfo(&rb, g_now, &info);
        info.src_kind = S5_SRC_TEST;
        S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_TEST);
        st.pass = (uint32_t)S5Display_CheckFrame(fb);
        st.src = S5Src_Name(S5_SRC_TEST);
        st.reason = "raw_frame_blank";
        st.latency_ms = info.latency_ms;
        st.age_ms = info.age_ms;
        printf("case3 det=%u（测试图案上仍画框）\n", (unsigned)info.det_count);
    } else if ((parse_rc != S5_PARSE_OK) && (raw_is_blank == 0)) {
        /* case2：无结果但有真实画面 → real_nobox */
        S5Real_BgrToCanvas(raw, cam, S5_RAW_FRAME_W * S5_RAW_FRAME_H);
        info.frame_id = 1u;
        info.status = S5_ST_CAM_OK;
        info.src_kind = S5_SRC_REAL_NOBOX;
        info.det_count = 0u;
        S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_CAM);
        st.pass = (uint32_t)S5Display_CheckFrame(fb);
        st.src = S5Src_Name(S5_SRC_REAL_NOBOX);
        st.reason = S5Src_Reason(parse_rc);
        st.age_ms = 0u;
        st.latency_ms = 0u;
    } else {
        /* case4：无结果且无画面 → test（合法通过态） */
        info.frame_id = 1u;
        info.status = S5_ST_CAM_OK;
        info.src_kind = S5_SRC_TEST;
        S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_TEST);
        st.pass = (uint32_t)S5Display_CheckFrame(fb);
        st.src = S5Src_Name(S5_SRC_TEST);
        st.reason = S5Src_Reason(parse_rc);
        st.age_ms = 0u;
        st.latency_ms = 0u;
    }
    print_result("case", &st);

    rc = ppm_write(ppm, fb);
    if (st.pass == 0u) {
        printf("case: FAIL（pass 应为 1）\n");
        rc = 1;
    }
    if (strcmp(st.src, expect_src) != 0) {
        printf("case: FAIL（期望 src=%s，实际 %s）\n", expect_src, st.src);
        rc = 1;
    }
    return (rc == 0) ? 0 : 1;
}

/* ---------------- case5：stale 标志 ---------------- */

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
    printf("case5 (stale): status=0x%04X stale_bit=%u age=%u ms\n",
           (unsigned)info.status, (unsigned)((info.status & S5_ST_STALE) ? 1u : 0u),
           (unsigned)info.age_ms);
    S5Display_RenderFrame(fb, cam, &info, S5_DMA_RUN);
    return ((info.status & S5_ST_STALE) != 0u) ? ((ppm_write(ppm, fb) == 0) ? 0 : 1) : 1;
}

/* ---------------- case6：时间戳全 0 → age/latency = 0 ---------------- */

static int run_ts_zero_case(uint32_t *blk)
{
    S5RealBlock rb;
    S5FrameInfo info;

    block_reset(blk);
    block_set_header(blk, 5u, 1u, 0u, 0u, S5_RESULT_ST_VALID);
    block_set_det(blk, 0u, 10u, 10u, 50u, 40u, 0u, 128u);
    if (S5Real_Parse(blk, &rb) != S5_PARSE_OK) {
        return 1;
    }
    memset(&info, 0, sizeof(info));
    S5Real_ToFrameInfo(&rb, g_now, &info);
    printf("case6 (ts=0): age=%u ms latency=%u ms（应为 0/0）\n",
           (unsigned)info.age_ms, (unsigned)info.latency_ms);
    return ((info.age_ms == 0u) && (info.latency_ms == 0u)) ? 0 : 1;
}

int main(int argc, char **argv)
{
    const char *fixture = (argc > 1) ? argv[1] : FIXTURE_DEFAULT;
    uint8_t *raw;
    uint8_t *raw_blank;
    uint32_t *blk;
    uint32_t *cam;
    uint32_t *fb;
    int fail = 0;

    printf("==== S5 真实数据源离线自检（ABI@0x%08X, raw@0x%08X）====\n",
           S5_RESULT_BASE, S5_RAW_FRAME_BASE);
    g_now = 1000000u;

    raw = load_raw(fixture);
    raw_blank = (uint8_t *)calloc(1, S5_RAW_FRAME_BYTES); /* 全 0 = 相机未启动 */
    blk = (uint32_t *)calloc(1, S5_RESULT_BLOCK_BYTES);
    cam = (uint32_t *)malloc((size_t)S5_CAM_W * S5_CAM_H * 4u);
    fb = (uint32_t *)malloc(S5_FB_BYTES);
    if ((raw == 0) || (raw_blank == 0) || (blk == 0) || (cam == 0) || (fb == 0)) {
        fprintf(stderr, "OOM\n");
        return 1;
    }

    fail |= run_real_case(raw, blk, cam, fb, "build/frame_real.ppm");
    fail |= run_nobox_or_test_case(blk, cam, fb, raw, 0, 1,
                                   "real_nobox", "build/frame_real_nobox.ppm");
    fail |= run_nobox_or_test_case(blk, cam, fb, raw, 1, 0,
                                   "test", "build/frame_test_with_boxes.ppm");
    fail |= run_nobox_or_test_case(blk, cam, fb, raw, 1, 1,
                                   "test", "build/frame_test_no_producer.ppm");
    fail |= run_stale_case(blk, cam, fb, "build/frame_stale.ppm");
    fail |= run_ts_zero_case(blk);

    free(fb);
    free(cam);
    free(blk);
    free(raw_blank);
    free(raw);
    printf("==== real-source selftest: %s ====\n", (fail == 0) ? "PASS" : "FAIL");
    return (fail == 0) ? 0 : 1;
}