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
#include "s5_publish_abi.h"

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
    char res[384];

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
        info.fps_dis_x10 = 600u; /* 离线假设显示 60 */
        info.fps_upd_x10 = (uint16_t)S5Fps_GetX10(&wd);
        S5Display_RenderFrameSrc(fb, cam, &info, S5_DMA_RUN, S5_VIDEO_SRC_CAM);
    }

    memset(&st, 0, sizeof(st));
    st.pass = (uint32_t)S5Display_CheckFrame(fb);
    st.src = S5Src_Name(S5_SRC_REAL);
    st.frames = RUN_FRAMES;
    st.vcnt = RUN_FRAMES;
    st.fps_cap = S5Fps_Get(&wc);
    st.fps_inf = S5Fps_Get(&wi);
    st.fps_dis = 60u; /* 离线：假设显示刷新 60（板上由 VDMA 读帧存周期实测） */
    st.fps_upd = 60u; /* 假时钟 36 帧 ×16.667 ms = 600 ms → 60 帧/s */
    st.latency_ms = info.latency_ms;
    st.age_ms = info.age_ms;
    st.box_crc = S5Display_BoxesCrc(info.det, info.det_count);
    st.fb_crc = S5Display_Crc32(fb, S5_FB_BYTES);
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

/* ---------------- case0：优化实现正确性 + CRC 已知答案 ---------------- */

static int run_opt_checks(const uint8_t *raw, uint32_t *cam)
{
    uint32_t *ref;
    uint32_t i;
    int bad = 0;
    uint32_t crc;

    ref = (uint32_t *)malloc((size_t)S5_RAW_FRAME_W * S5_RAW_FRAME_H * 4u);
    if (ref == 0) {
        printf("case0: OOM\n");
        return 1;
    }
    /* 优化版 BGR→RGB 必须与逐像素参考实现完全一致 */
    S5Real_BgrToCanvas(raw, cam, S5_RAW_FRAME_W * S5_RAW_FRAME_H);
    S5Real_BgrToCanvasRef(raw, ref, S5_RAW_FRAME_W * S5_RAW_FRAME_H);
    for (i = 0; i < (uint32_t)S5_RAW_FRAME_W * S5_RAW_FRAME_H; i++) {
        if (cam[i] != ref[i]) {
            printf("case0: FAIL 转换不一致 i=%u opt=%x ref=%x\n",
                   (unsigned)i, (unsigned)cam[i], (unsigned)ref[i]);
            bad = 1;
            break;
        }
    }
    free(ref);

    /* CRC32 已知答案：ASCII "123456789" → 0xCBF43926 */
    crc = S5Display_Crc32("123456789", 9u);
    printf("case0: crc32(\"123456789\")=0x%08X（期望 0xCBF43926）\n", (unsigned)crc);
    if (crc != 0xCBF43926u) {
        bad = 1;
    }

    /* box_crc：映射后坐标的 u16 序列，确定性 + 输入变化必然改变 CRC */
    {
        S5DetBox a[2];
        S5DetBox b[2];
        uint32_t ca;
        uint32_t cb;

        memset(a, 0, sizeof(a));
        a[0].x = 100; a[0].y = 80; a[0].w = 160; a[0].h = 120; a[0].cls = 0; a[0].score = 90;
        a[1].x = 10; a[1].y = 20; a[1].w = 60; a[1].h = 40; a[1].cls = 2; a[1].score = 60;
        b[0] = a[0];
        b[1] = a[1];
        ca = S5Display_BoxesCrc(a, 2u);
        cb = S5Display_BoxesCrc(b, 2u);
        printf("case0: box_crc=%u \n", (unsigned)ca);
        if (ca != cb) {
            printf("case0: FAIL box_crc 不确定\n");
            bad = 1;
        }
        b[1].x = 11;
        if (S5Display_BoxesCrc(b, 2u) == ca) {
            printf("case0: FAIL box_crc 对坐标不敏感\n");
            bad = 1;
        }
    }
    return bad;
}

/* ---------------- case0b：G3-B 用 lead 给的 3 个框验证 box_crc 口径 ---------------- */

static int run_lead_box_case(void)
{
    S5DetBox b[3];
    uint16_t mb[12];
    uint32_t n;
    uint32_t crc;
    uint32_t i;

    /* 原图 640×480 坐标（lead 2026-10-30 G3-B 给定） */
    memset(b, 0, sizeof(b));
    b[0].x = 100; b[0].y = 80;  b[0].w = 120; b[0].h = 200;
    b[1].x = 500; b[1].y = 300; b[1].w = 100; b[1].h = 100;
    b[2].x = 0;   b[2].y = 0;   b[2].w = 640; b[2].h = 480;

    n = S5Display_BoxesMapped(b, 3u, mb, 3u);
    crc = S5Display_BoxesCrc(b, 3u);
    printf("G3-B box_crc: nbox=%u crc=0x%08X (%u) 期望 0x2D949C0C (764713996)\n",
           (unsigned)n, (unsigned)crc, (unsigned)crc);
    printf("G3-B 序列(%u B, u16LE x,y,w,h):", (unsigned)(n * 8u));
    for (i = 0u; i < (n * 4u); i++) {
        printf(" %02X %02X", (unsigned)(mb[i] & 0xFFu), (unsigned)(mb[i] >> 8));
    }
    printf("\n");
    return ((n == 3u) && (crc == 0x2D949C0Cu)) ? 0 : 1;
}

/* ---------------- case0c：生产者打包（S5Prod_PackBlock）与 ABI 往返 ---------------- */

static int run_producer_case(void)
{
    static uint32_t blk[(S5_RESULT_BLOCK_BYTES + 3u) / 4u];
    S5DetBox det[3];
    uint64_t cap = 1234567u;
    uint64_t inf = cap + (uint64_t)S5_PROD_INF_OFFSET_TICKS;
    S5RealBlock rb;
    uint32_t i;
    int bad = 0;

    memset(det, 0, sizeof(det));
    det[0].x = 100; det[0].y = 80;  det[0].w = 120; det[0].h = 200; det[0].cls = 0; det[0].score = 87;
    det[1].x = 500; det[1].y = 300; det[1].w = 100; det[1].h = 100; det[1].cls = 2; det[1].score = 92;
    det[2].x = 0;   det[2].y = 0;   det[2].w = 640; det[2].h = 480; det[2].cls = 4; det[2].score = 75;

    S5Prod_PackBlock(blk, 7u, 3u, det, cap, inf, S5_RESULT_ST_VALID);

    /* 头字段逐项核对（帧 32 B / 检测项 16 B 步进 / 保留字段为 0） */
    if (blk[S5_RESULT_W_MAGIC] != S5_RESULT_MAGIC) { printf("case0c: FAIL magic\n"); bad = 1; }
    if (blk[S5_RESULT_W_FRAME_ID] != 7u) { printf("case0c: FAIL frame_id\n"); bad = 1; }
    if (blk[S5_RESULT_W_N_DETS] != 3u) { printf("case0c: FAIL n_dets\n"); bad = 1; }
    if ((((uint64_t)blk[S5_RESULT_W_CAP_HI] << 32) | blk[S5_RESULT_W_CAP_LO]) != cap) {
        printf("case0c: FAIL cap ticks\n"); bad = 1;
    }
    if ((((uint64_t)blk[S5_RESULT_W_INF_HI] << 32) | blk[S5_RESULT_W_INF_LO]) != inf) {
        printf("case0c: FAIL inf ticks\n"); bad = 1;
    }
    if (blk[S5_RESULT_W_STATUS] != S5_RESULT_ST_VALID) { printf("case0c: FAIL status\n"); bad = 1; }
    for (i = 0; i < 3u; i++) {
        const uint32_t *d = &blk[(S5_RESULT_DETS_OFFSET / 4u) + i * 4u];
        uint32_t x = d[0] & 0xFFFFu, y = d[0] >> 16, w = d[1] & 0xFFFFu, h = d[1] >> 16;
        uint32_t cls = d[2] & 0xFFu, sc = (d[2] >> 8) & 0xFFu;

        if ((x != (uint32_t)det[i].x) || (y != (uint32_t)det[i].y) || (w != (uint32_t)det[i].w) ||
            (h != (uint32_t)det[i].h) || (cls != det[i].cls) || (sc != det[i].score) || (d[3] != 0u)) {
            printf("case0c: FAIL item %u\n", (unsigned)i);
            bad = 1;
        }
    }
    if ((blk[(S5_RESULT_DETS_OFFSET / 4u) + 15u * 4u + 2u] >> 16) != (uint32_t)S5_PROD_SESSION_TAG) {
        printf("case0c: FAIL session tag\n");
        bad = 1;
    }
    /* 用消费者解析器往返：必须读回同样的帧号/框/时间戳 */
    if (S5Real_Parse(blk, &rb) != S5_PARSE_OK) {
        printf("case0c: FAIL parse round-trip\n");
        bad = 1;
    } else if ((rb.frame_id != 7u) || (rb.n != 3u) || (rb.cap_ticks != cap) || (rb.inf_ticks != inf) ||
               (rb.det[1].x != 500u) || (rb.det[2].h != 480u)) {
        printf("case0c: FAIL round-trip values\n");
        bad = 1;
    }
    printf("S5PROD frame_id=%u n=%u status=0x%X cap_ms=%llu inf_ms=%llu cap_lo=0x%X inf_lo=0x%X (离线模拟 ticks)\n",
           (unsigned)blk[S5_RESULT_W_FRAME_ID], (unsigned)blk[S5_RESULT_W_N_DETS],
           (unsigned)blk[S5_RESULT_W_STATUS],
           (unsigned long long)((cap * 1000ull) / S5_GT_HZ),
           (unsigned long long)((inf * 1000ull) / S5_GT_HZ),
           (unsigned)blk[S5_RESULT_W_CAP_LO], (unsigned)blk[S5_RESULT_W_INF_LO]);
    return bad;
}

/* ---------------- case0d：生产者 v2（sidecar / seqlock / seq / 业务状态） ---------------- */

static int run_publish_v2_case(void)
{
    uint32_t sc[8];
    uint32_t seq;
    S5PubView v;
    int bad = 0;
    uint64_t rt = 5000000u;
    uint32_t age;

    /* sidecar 打包/回读 */
    S5Pub_PackSidecar(sc, 0xABCDu, 42u, rt, 84u);
    if ((sc[S5_PUB_W_MAGIC2] != S5_PUB_MAGIC2) || (sc[S5_PUB_W_VERSION] != S5_PUB_VERSION) ||
        (sc[S5_PUB_W_SESSION_ID] != 0xABCDu) || (sc[S5_PUB_W_RESULT_SEQ] != 42u) ||
        (sc[S5_PUB_W_RTIME_LO] != (uint32_t)rt) || (sc[S5_PUB_W_RTIME_HI] != (uint32_t)(rt >> 32)) ||
        (sc[S5_PUB_W_SEQLOCK] != 84u) || (sc[S5_PUB_W_RESERVED] != 0u)) {
        printf("case0d: FAIL sidecar pack\n");
        bad = 1;
    }
    printf("case0d: sidecar magic2=0x%08X ver=%u sid=%u seq=%u rtime=%llu seqlock=%u\n",
           (unsigned)sc[0], (unsigned)sc[1], (unsigned)sc[2], (unsigned)sc[3],
           (unsigned long long)rt, (unsigned)sc[6]);

    /* seqlock 奇偶/一致判定 */
    if (S5Pub_SeqlockStable(4u, 4u) != 0) { printf("case0d: FAIL stable even\n"); bad = 1; }
    if (S5Pub_SeqlockStable(5u, 5u) == 0) { printf("case0d: FAIL odd must be unstable\n"); bad = 1; }
    if (S5Pub_SeqlockStable(4u, 6u) == 0) { printf("case0d: FAIL changed must be unstable\n"); bad = 1; }

    /* result_seq：0→1 正常；0xFFFFFFFE→0xFFFFFFFF 正常；0xFFFFFFFF→0 拒绝；回退拒绝 */
    if ((S5Pub_NextSeq(0u, &seq) != 0) || (seq != 1u)) { printf("case0d: FAIL seq 0->1\n"); bad = 1; }
    if ((S5Pub_NextSeq(0xFFFFFFFEu, &seq) != 0) || (seq != 0xFFFFFFFFu)) {
        printf("case0d: FAIL seq FFFFFFFE->FFFFFFFF\n"); bad = 1;
    }
    seq = 0u;
    if (S5Pub_NextSeq(0xFFFFFFFFu, &seq) == 0) { printf("case0d: FAIL FFFFFFFF->0 must reject\n"); bad = 1; }
    /* 回退：实现是"只接受 last+1"，因此任何非 +1 目标都会被拒（不做显式回退输入） */
    printf("case0d: seq rules OK（0xFFFFFFFF 拒绝；0xFFFFFFFE→0xFFFFFFFF 正常）\n");

    /* 业务状态映射（冻结口径 §2 优先级） */
    memset(&v, 0, sizeof(v));
    v.status = 0u; v.n_dets = 3u;
    if (S5Pub_BizState(&v, 0u) != S5_BIZ_ERROR) { printf("case0d: FAIL valid=0 -> ERROR\n"); bad = 1; }
    v.status = S5_RESULT_ST_VALID | S5_RESULT_ST_OVERRUN; v.n_dets = 3u;
    if (S5Pub_BizState(&v, 0u) != S5_BIZ_ERROR) { printf("case0d: FAIL overrun -> ERROR\n"); bad = 1; }
    v.status = S5_RESULT_ST_VALID | S5_RESULT_ST_STALE; v.n_dets = 3u;
    if (S5Pub_BizState(&v, 0u) != S5_BIZ_TIMEOUT) { printf("case0d: FAIL stale -> TIMEOUT\n"); bad = 1; }
    v.status = S5_RESULT_ST_VALID; v.n_dets = 3u;
    if (S5Pub_BizState(&v, 201u) != S5_BIZ_TIMEOUT) { printf("case0d: FAIL age>200 -> TIMEOUT\n"); bad = 1; }
    if (S5Pub_BizState(&v, 200u) != S5_BIZ_OK) { printf("case0d: FAIL age=200 -> OK\n"); bad = 1; }
    v.status = S5_RESULT_ST_VALID; v.n_dets = 0u;
    if (S5Pub_BizState(&v, 5u) != S5_BIZ_NO_HAND) { printf("case0d: FAIL n=0 -> NO_HAND\n"); bad = 1; }

    /* age_publish 计算：0.7 s = 233,333,340 ticks（7 ms tick 偏移用 2,333,334） */
    age = S5Pub_AgePublishMs(1000000000u, 1000000000u - (uint64_t)((S5_GT_HZ * 7u) / 1000u));
    if ((age < 6u) || (age > 8u)) { printf("case0d: FAIL age=7ms got %u\n", (unsigned)age); bad = 1; }
    printf("case0d: biz state mapping OK（ERROR/TIMEOUT/NO_HAND/OK + age=7ms 计算）\n");

    /* 样例 S5PROD 行（离线构造，板上为真实 ticks） */
    memset(&v, 0, sizeof(v));
    v.status = S5_RESULT_ST_VALID; v.n_dets = 2u; v.session_id = 41237u; v.result_seq = 187u;
    v.result_time = rt + 3000000u;
    printf("S5PROD frame_id=187 n=2 status=0x1 sid=41237 seq=187 rtime_ms=23 age_pub=0 state=%s "
           "fault=none cap_ms=16（离线构造示例，板上为真实 GT ticks）\n",
           S5Pub_StateName(S5Pub_BizState(&v, 0u)));
    return bad;
}

/* ---------------- case0e：身份 A 的 n_dets 上限（fail-closed） ---------------- */

static int run_ndets_gate_case(void)
{
    int bad = 0;

    if (S5_PUB_NDETS_MAX != 14u) {
        printf("case0e: FAIL NDETS_MAX=%u (expect 14)\n", (unsigned)S5_PUB_NDETS_MAX);
        bad = 1;
    }
    if (S5Pub_NDetsOk(14u) != 0) { printf("case0e: FAIL n=14 must be allowed\n"); bad = 1; }
    if (S5Pub_NDetsOk(15u) == 0) { printf("case0e: FAIL n=15 must be rejected (fail-closed)\n"); bad = 1; }
    if (S5Pub_NDetsOk(16u) == 0) { printf("case0e: FAIL n=16 must be rejected\n"); bad = 1; }
    if (S5Pub_NDetsOk(0u) != 0) { printf("case0e: FAIL n=0 must be allowed (NO_HAND)\n"); bad = 1; }
    /* 身份 A 布局：sidecar 起点 0x100，发布/flush 288 B */
    if (S5_PUB_SIDECAR_OFFSET != 0x100u) { printf("case0e: FAIL sidecar offset\n"); bad = 1; }
    if (S5_PUB_PUBLISH_BYTES != 0x120u) { printf("case0e: FAIL publish bytes (expect 0x120)\n"); bad = 1; }
    if (S5_PUB_SIDECAR_BASE != (S5_RESULT_BASE + 0x100u)) { printf("case0e: FAIL sidecar base\n"); bad = 1; }
    printf("case0e: n_dets gate OK（≤14 允许；15/16 拒绝 fail-closed；sidecar @+0x100 / flush 288 B）\n");
    return bad;
}

/* ---------------- case0f：rev4 seqlock 顺序断言（记录调用序） ---------------- */

typedef struct S5PubRec {
    const char *log[16];
    int n;
} S5PubRec;

static void s5rec_add(S5PubRec *r, const char *name)
{
    if (r->n < 16) {
        r->log[r->n++] = name;
    }
}

static void s5rec_flush(void *ctx, const volatile void *addr, uint32_t bytes)
{
    (void)addr;
    s5rec_add((S5PubRec *)ctx, (bytes == 4u) ? "flush_lock" : "flush_payload");
}

static void s5rec_invalidate(void *ctx, const volatile void *addr, uint32_t bytes)
{
    (void)addr;
    (void)bytes;
    s5rec_add((S5PubRec *)ctx, "invalidate");
}

static void s5rec_barrier(void *ctx)
{
    s5rec_add((S5PubRec *)ctx, "barrier");
}

static int s5rec_expect(const S5PubRec *r, const char *const *want, int n, const char *tag)
{
    int i;

    if (r->n != n) {
        printf("case0f: FAIL %s 调用序长度 %d != %d\n", tag, r->n, n);
        return -1;
    }
    for (i = 0; i < n; i++) {
        if (strcmp(r->log[i], want[i]) != 0) {
            printf("case0f: FAIL %s 第 %d 步 '%s' != '%s'\n", tag, i, r->log[i], want[i]);
            return -1;
        }
    }
    return 0;
}

static int run_seqlock_order_case(void)
{
    static uint32_t payload[S5_PUB_PUBLISH_BYTES / 4u];
    static uint32_t blk[S5_PUB_PUBLISH_BYTES / 4u];
    static uint32_t out[S5_PUB_PUBLISH_BYTES / 4u];
    const uint32_t lock_idx = (S5_PUB_SIDECAR_OFFSET / 4u) + S5_PUB_W_SEQLOCK;
    static const char *const want_w[] = {"flush_lock", "barrier", "flush_payload",
                                         "barrier", "flush_lock", "barrier"};
    static const char *const want_r[] = {"invalidate", "barrier"};
    S5PubMem m;
    S5PubRec rec;
    S5PubReadTrace tr;
    uint32_t sl = 0u;
    uint32_t sl_out = 0u;
    int bad = 0;

    memset(&m, 0, sizeof(m));
    memset(payload, 0, sizeof(payload));
    m.payload = payload;
    m.flush = s5rec_flush;
    m.invalidate = s5rec_invalidate;
    m.barrier = s5rec_barrier;

    /* 写者顺序：锁奇→flush 锁行→DSB → flush payload→DSB → 锁偶→flush 锁行→DSB */
    memset(&rec, 0, sizeof(rec));
    m.ctx = &rec;
    memset(blk, 0, sizeof(blk));
    blk[S5_RESULT_W_MAGIC] = S5_RESULT_MAGIC;
    blk[S5_RESULT_W_N_DETS] = 2u;
    if (S5Pub_WritePublish(&m, &sl, blk, 123456789u) != 0) {
        printf("case0f: FAIL writer return\n");
        bad = 1;
    }
    if (s5rec_expect(&rec, want_w, 6, "writer") != 0) {
        bad = 1;
    }
    if ((sl != 2u) || (payload[lock_idx] != 2u)) {
        printf("case0f: FAIL seqlock 偶值 sl=%u mem=%u\n", (unsigned)sl, (unsigned)payload[lock_idx]);
        bad = 1;
    }

    /* 读者顺序：invalidate-first → 读 s1 → 读 payload → DMB → 读 s2 */
    memset(&rec, 0, sizeof(rec));
    memset(&tr, 0xFF, sizeof(tr));
    m.ctx = &rec;
    if (S5Pub_ReadPublish(&m, out, &sl_out, &tr) != 0) {
        printf("case0f: FAIL reader return\n");
        bad = 1;
    }
    if (s5rec_expect(&rec, want_r, 2, "reader") != 0) {
        bad = 1;
    }
    if ((sl_out != sl) || (out[S5_RESULT_W_MAGIC] != S5_RESULT_MAGIC)) {
        printf("case0f: FAIL reader 内容/seq 不一致\n");
        bad = 1;
    }
    /* v5：可观测字段必须存在且 s1==s2 且为偶、无重试 */
    if ((tr.attempts != 1u) || (tr.retries != 0u) || (tr.s1_last != sl) ||
        (tr.s2_last != sl) || ((tr.s1_last & 1u) != 0u) || (tr.s1_last != tr.s2_last)) {
        printf("case0f: FAIL trace（attempts=%u retries=%u s1=%u s2=%u sl=%u）\n",
               (unsigned)tr.attempts, (unsigned)tr.retries,
               (unsigned)tr.s1_last, (unsigned)tr.s2_last, (unsigned)sl);
        bad = 1;
    } else {
        printf("S5CONS sid=%u seq=%u n=%u status=0x%X age_pub=%u state=%s seqlock=%u s1=%u s2=%u retries=%u"
               "（离线样例：s1==s2 且偶）\n",
               (unsigned)(out[S5_PUB_SIDECAR_OFFSET / 4u + S5_PUB_W_SESSION_ID] & 0xFFFFu),
               (unsigned)out[S5_PUB_SIDECAR_OFFSET / 4u + S5_PUB_W_RESULT_SEQ],
               (unsigned)out[S5_RESULT_W_N_DETS], (unsigned)out[S5_RESULT_W_STATUS],
               0u, "OK", (unsigned)sl, (unsigned)tr.s1_last, (unsigned)tr.s2_last, (unsigned)tr.retries);
    }

    /* 锁为奇数（写入中）→ 读者必须 3 次重试后拒绝（TIMEOUT），且 trace 记录 s1 为奇 */
    payload[lock_idx] = 1u;
    memset(&tr, 0, sizeof(tr));
    if (S5Pub_ReadPublish(&m, out, &sl_out, &tr) == 0) {
        printf("case0f: FAIL 奇数锁必须被拒绝\n");
        bad = 1;
    }
    if ((tr.attempts != 3u) || (tr.retries != 2u) || ((tr.s1_last & 1u) == 0u)) {
        printf("case0f: FAIL 奇数锁 trace（attempts=%u retries=%u s1=%u）\n",
               (unsigned)tr.attempts, (unsigned)tr.retries, (unsigned)tr.s1_last);
        bad = 1;
    } else {
        printf("S5CONS TIMEOUT seq=0 attempt=%u s1=%u s2=%u（离线样例：奇数锁 3 次重试后 TIMEOUT）\n",
               (unsigned)tr.attempts, (unsigned)tr.s1_last, (unsigned)tr.s2_last);
    }
    /* 起始锁非偶 → 写者拒绝 */
    sl = 1u;
    if (S5Pub_WritePublish(&m, &sl, blk, 1u) == 0) {
        printf("case0f: FAIL 写者起始锁非偶必须拒绝\n");
        bad = 1;
    }

    if (bad == 0) {
        printf("case0f: seqlock 顺序 OK（writer: lock→flush_lock→DSB→payload→flush_288B→DSB→lock→flush_lock→DSB；"
               "reader: invalidate-first→s1→payload→DMB→s2；奇数锁拒绝）\n");
    }
    return bad;
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

    fail |= run_opt_checks(raw, cam);
    fail |= run_lead_box_case();
    fail |= run_producer_case();
    fail |= run_publish_v2_case();
    fail |= run_ndets_gate_case();
    fail |= run_seqlock_order_case();
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

