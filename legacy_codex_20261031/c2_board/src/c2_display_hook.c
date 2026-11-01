#include <stdint.h>

#include "s5_display_app.h"
#include "s5_real_source.h"
#include "vdma_ctrl.h"
#ifndef C2_DISPLAY_PROFILE_P3Q_RTL_TIMING
#define C2_DISPLAY_PROFILE_P3Q_RTL_TIMING 0
#endif

#if (C2_DISPLAY_PROFILE_P3Q_RTL_TIMING != 0) && (C2_DISPLAY_PROFILE_P3Q_RTL_TIMING != 1)
#error "C2_DISPLAY_PROFILE_P3Q_RTL_TIMING must be 0 or 1"
#endif

#if C2_DISPLAY_PROFILE_P3Q_RTL_TIMING
#define C2_DISPLAY_PROFILE_NAME "P3Q_RTL_TIMING"
#define C2_DISPLAY_TIMING_SOURCE "PL_RTL"
#else
#define C2_DISPLAY_PROFILE_NAME "P3B_VTC"
#define C2_DISPLAY_TIMING_SOURCE "PS_VTC"
#include "vtc_ctrl.h"
#endif
#include "xil_cache.h"
#include "xil_printf.h"

static uint32_t c2_display_canvas[S5_CAM_W * S5_CAM_H];

int C2_DisplayOneFrame(uint64_t now_ticks, uint32_t expected_frame_id, uint32_t expected_count)
{
    static S5Vdma dma;
#if !C2_DISPLAY_PROFILE_P3Q_RTL_TIMING
    static S5Vtc vtc;
#endif
    static S5RealBlock result;
    const uint32_t addresses[2] = {S5_FB_A_BASE, S5_FB_B_BASE};
    uint32_t *frame_a = (uint32_t *)(uintptr_t)S5_FB_A_BASE;
    uint32_t *frame_b = (uint32_t *)(uintptr_t)S5_FB_B_BASE;
#if !C2_DISPLAY_PROFILE_P3Q_RTL_TIMING
    S5VtcTiming timing;
#endif
    S5FrameInfo info;
#if !C2_DISPLAY_PROFILE_P3Q_RTL_TIMING
    int rc_vtc;
#endif
    int rc_vdma;
    uint32_t box_crc;
    uint32_t frame_crc;

    if (S5Real_Parse((const uint32_t *)(uintptr_t)S5_RESULT_BASE, &result) != S5_PARSE_OK ||
        result.frame_id != expected_frame_id || result.n != expected_count || result.n > 14u) {
        xil_printf("C2 DISPLAY RESULT={\"pass\":0,\"reason\":\"result_parse_or_mismatch\"}\r\n");
        return -1;
    }
    S5Real_ToFrameInfo(&result, now_ticks, &info);
    S5Real_BgrToCanvas((const uint8_t *)(uintptr_t)S5_RAW_FRAME_BASE,
                       c2_display_canvas, S5_CAM_W * S5_CAM_H);

#if C2_DISPLAY_PROFILE_P3Q_RTL_TIMING
    xil_printf("C2 DISPLAY PROFILE=%s timing_source=%s fclk1_required_mhz=100 fclk1_verified=0\r\n",
               C2_DISPLAY_PROFILE_NAME, C2_DISPLAY_TIMING_SOURCE);
#else
    S5Vtc_Default720p60(&timing);
    rc_vtc = S5Vtc_Init(&vtc, &timing, 10000u);
    if (rc_vtc != 0) {
        xil_printf("C2 DISPLAY VTC RESULT={\"pass\":0,\"rc\":%d}\r\n", rc_vtc);
        return -2;
    }
#endif

    S5Display_RenderFrameSrc(frame_a, c2_display_canvas, &info, S5_DMA_OFF, S5_VIDEO_SRC_CAM);
    S5Display_RenderFrameSrc(frame_b, c2_display_canvas, &info, S5_DMA_OFF, S5_VIDEO_SRC_CAM);
    if (!S5Display_CheckFrame(frame_a) || !S5Display_CheckFrame(frame_b)) {
        xil_printf("C2 DISPLAY RESULT={\"pass\":0,\"reason\":\"frame_check\"}\r\n");
        return -3;
    }
    box_crc = S5Display_BoxesCrc(info.det, info.det_count);
    frame_crc = S5Display_Crc32(frame_a, S5_FB_BYTES);
    Xil_DCacheFlushRange((UINTPTR)frame_a, S5_FB_BYTES);
    Xil_DCacheFlushRange((UINTPTR)frame_b, S5_FB_BYTES);
    __asm__ volatile("dsb sy" ::: "memory");

    rc_vdma = S5Vdma_Init(&dma, addresses, 2u,
                          (uint32_t)S5_CANVAS_W * 4u, (uint32_t)S5_CANVAS_H);
    if (rc_vdma != 0) {
        xil_printf("C2 DISPLAY RESULT={\"pass\":0,\"render\":1,\"reason\":\"vdma_init\",\"rc\":%d,\"box_crc\":%u,\"frame_crc\":%u}\r\n",
                   rc_vdma, (unsigned)box_crc, (unsigned)frame_crc);
        return -4;
    }
    if ((S5Vdma_Status(&dma) & S5_VDMA_SR_ERR_ALL) != 0u) {
        xil_printf("C2 DISPLAY RESULT={\"pass\":0,\"render\":1,\"reason\":\"vdma_status\",\"box_crc\":%u,\"frame_crc\":%u}\r\n",
                   (unsigned)box_crc, (unsigned)frame_crc);
        return -5;
    }
    xil_printf("C2 DISPLAY RESULT={\"pass\":1,\"render\":1,\"display_profile\":\"%s\",\"timing_source\":\"%s\",\"source\":\"real_fixture\",\"frame_id\":%u,\"n_dets\":%u,\"age_ms\":%u,\"latency_ms\":%u,\"box_crc\":%u,\"frame_crc\":%u,\"vdma\":\"started\",\"physical_scanout\":\"NOT_VERIFIED\"}\r\n",
               C2_DISPLAY_PROFILE_NAME, C2_DISPLAY_TIMING_SOURCE,
               (unsigned)info.frame_id, (unsigned)info.det_count, (unsigned)info.age_ms,
               (unsigned)info.latency_ms, (unsigned)box_crc, (unsigned)frame_crc);
    return 0;
}
