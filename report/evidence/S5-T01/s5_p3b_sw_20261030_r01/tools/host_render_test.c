/*
 * host_render_test.c —— 主机端（x86 + MinGW gcc）离线自检：用**同一份绘图源码**
 * 渲染 1280×720 画布并落成 PPM，用于人工/自动核对：
 *   · 布局：左 160 px 黑边、960×720 视频区、右 320 px 信息栏；
 *   · 缩放：640×480 → 960×720 最近邻（1.5×）；
 *   · 检测框 2 px、类别配色、标签；
 *   · 8×16 字库在 1280 宽画布上的实际可读性；
 *   · 三条测试图（棋盘/彩条/灰阶）。
 *
 * 与 ARM 构建的区别只有两点：不编译 vdma_ctrl.c / s5_timebase.c，
 * 这里提供 S5Ticks_Now() 的假实现（每次 +3.33 ms 的计数），其余源码完全相同。
 *
 * 编译（MinGW gcc）：
 *   gcc -std=gnu11 -O2 -Wall -Wextra -DS5_HOST_TEST -Isrc \
 *       tools/host_render_test.c src/s5_display_app.c -o build/host_render_test.exe
 */
#define S5_HOST_TEST 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "s5_display_app.h"

/* 两种布局各渲染一套 PNG：文件名后缀随 S5_LAYOUT_BARS 变化 */
#if S5_LAYOUT_BARS
#define S5_SUFFIX "_bars"
#else
#define S5_SUFFIX ""
#endif

/* 假时间基：按 ~300 MHz 计数递增，每次调用 +3.33 ms（≈ 720p 一帧） */
uint64_t S5Ticks_Now(void)
{
    static uint64_t t = 1000000ULL;

    t += 1000000ULL;
    return t;
}

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

int main(void)
{
    uint32_t *fb = (uint32_t *)malloc(S5_FB_BYTES);
    uint32_t *cam = (uint32_t *)malloc((size_t)S5_CAM_W * S5_CAM_H * 4u);
    S5FrameInfo info;
    int rc = 0;

    if ((fb == 0) || (cam == 0)) {
        fprintf(stderr, "OOM\n");
        return 1;
    }

    /* 1) 三条测试图 */
    S5Display_TestPattern(fb, 0);
    rc |= ppm_write("build/pattern_checker" S5_SUFFIX ".ppm", fb);
    S5Display_TestPattern(fb, 1);
    rc |= ppm_write("build/pattern_colorbars" S5_SUFFIX ".ppm", fb);
    S5Display_TestPattern(fb, 2);
    rc |= ppm_write("build/pattern_grayramp" S5_SUFFIX ".ppm", fb);

    /* 2) 一帧完整画面：合成摄像头 + 3 个检测框 + 信息栏 */
    memset(&info, 0, sizeof(info));
    info.frame_id = 1234;
    info.fps_cap_x10 = 300;
    info.fps_inf_x10 = 281;
    info.fps_dis_x10 = 600;
    info.latency_ms = 17;
    info.age_ms = 31;
    info.status = S5_ST_CAM_OK | S5_ST_INF_OK;
    info.det_count = 3;
    info.det[0].x = 120;
    info.det[0].y = 90;
    info.det[0].w = 160;
    info.det[0].h = 140;
    info.det[0].cls = 0;
    info.det[0].score = 87;
    info.det[1].x = 380;
    info.det[1].y = 260;
    info.det[1].w = 120;
    info.det[1].h = 110;
    info.det[1].cls = 2;
    info.det[1].score = 92;
    info.det[2].x = 40;
    info.det[2].y = 330;
    info.det[2].w = 180;
    info.det[2].h = 100;
    info.det[2].cls = 4;
    info.det[2].score = 74;

    S5Sim_CameraFrame(cam, 1234);
    S5Display_RenderFrame(fb, cam, &info, S5_DMA_RUN);
    rc |= ppm_write("build/frame_full" S5_SUFFIX ".ppm", fb);

    /* 3) 超龄告警样式（AGE OVER 红色路径） */
    info.age_ms = 41;
    info.status |= S5_ST_AGE_OVER;
    S5Display_RenderFrame(fb, cam, &info, S5_DMA_ERR);
    rc |= ppm_write("build/frame_age_over" S5_SUFFIX ".ppm", fb);

    /* 4) 有界运行 S5_RUN_FRAMES(180) 帧（模拟源）→ 用**与板上同一份** S5Display_FormatResult()
     *    生成 RESULT 行。这里 180 帧是真渲染（含信息栏抽点自检），只是没有 VDMA/MMIO。 */
    {
        S5RunStats st;
        char res[224];
        uint32_t i;
        uint32_t last_lat = 0;
        uint32_t last_age = 0;
        uint32_t t0 = (uint32_t)S5Ticks_Now();

        for (i = 0; i < (uint32_t)S5_RUN_FRAMES; i++) {
            S5Sim_NextFrame(&info);
            S5Sim_CameraFrame(cam, info.frame_id);
            S5Display_RenderFrame(fb, cam, &info, S5_DMA_RUN);
            last_lat = info.latency_ms;
            last_age = info.age_ms;
        }

        st.pass = S5Display_CheckFrame(fb) ? 1u : 0u;
        st.reason = (st.pass != 0u) ? 0 : "frame_check_failed";
        st.src = "sim"; /* 本工具只跑模拟源；真实源见 tools/real_source_selftest.c */
        st.fps_cap = (uint32_t)(info.fps_cap_x10 / 10u);
        st.fps_inf = 0u; /* 无真实推理源：与板上 S5_RESULT_FPS_INF_FROM_SIM=0 口径一致 */
        st.fps_dis = (uint32_t)(info.fps_dis_x10 / 10u);
        st.latency_ms = last_lat;
        st.age_ms = last_age;
        st.vdma_err = 0u;
        st.frames = (uint32_t)S5_RUN_FRAMES;
        st.vcnt = (uint32_t)S5_RUN_FRAMES; /* 离线：模拟 VDMA 每帧消耗一帧 */

        S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
        printf("%s\n", res);
        printf("RESULT 行长度=%u 字符（单行，不含换行）\n", (unsigned)strlen(res));

        /* 4.1 失败路径契约演示：pass:0 + reason 也必须是同一行 */
        st.pass = 0u;
        st.reason = "vdma_init_failed";
        S5Display_FormatResult(&st, res, (uint32_t)sizeof(res));
        printf("%s\n", res);
        printf("180 帧渲染耗时(假时钟计数差)=%u\n", (unsigned)((uint32_t)S5Ticks_Now() - t0));
    }

    free(cam);
    free(fb);
    printf("host render test %s\n", rc == 0 ? "PASS" : "FAIL");
    return rc;
}
