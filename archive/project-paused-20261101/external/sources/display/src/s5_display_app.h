/*
 * s5_display_app.h —— 阶段5 HDMI 显示链 PS 侧绘图/帧装配（P3b-sw）
 *
 * 布局口径（G0 冻结，不允许在本文件里另造尺寸）：
 *   画布 1280×720，32-bit/像素，低 24 位 = RGB888（0x00RRGGBB）；
 *   摄像头画面 640×480 → 等比 960×720 居中，左右各 160 px 黑边；
 *   右侧 320×720 信息栏；检测框线宽 2 px；文字 8×16 点阵。
 *
 * 设计要点：
 *   · 全部绘图函数是**纯函数**（只依赖传入的像素缓冲），不碰 MMIO/时钟，
 *     因此可以在主机上用同一份源码渲染出 PNG 做离线自检（tools/host_render_test.c）；
 *   · 帧缓冲地址是冻结的物理地址（DDR 0x13000000 / 0x13384000），由 main() 以绝对
 *     指针传入，绘图函数不知道地址来源，便于替换。
 */
#ifndef S5_DISPLAY_APP_H
#define S5_DISPLAY_APP_H

#include <stdint.h>

/* ---------------- 画布与帧缓冲（地址已按 lead 2026-10-30 裁决迁移） ----------------
 * 原定 0x13000000 落在阶段4 冻结的 must_not_access 禁区 [0x12C08000, 0x20000000) 内
 * （依据 decisions/stage4_raw_address_d1_optionA_20261027_r01.md），**不可用**。
 * 裁决：帧缓冲迁到 0x20000000 —— 禁区之上、应用 ELF 之上（ELF end≈0x0034A8xx）、
 * PS DDR 低 1 GiB（0x00000000..0x3FFFFFFF）之内且空闲。
 *   A = 0x20000000
 *   B = 0x20384000（= A + 0x384000）
 *   每帧 3,686,400 B，两帧 7,372,800 B，终点 0x20708000。 */
#define S5_CANVAS_W 1280
#define S5_CANVAS_H 720
#define S5_FB_BYTES (S5_CANVAS_W * S5_CANVAS_H * 4u) /* 3,686,400 B = 0x384000 */

#define S5_FB_A_BASE 0x20000000u
#define S5_FB_B_BASE 0x20384000u /* A + 0x384000 */
#define S5_FB_END (S5_FB_B_BASE + S5_FB_BYTES) /* 0x20708000 */

/* ---------------- 摄像头/视频区/信息栏几何 ---------------- */
#define S5_CAM_W 640
#define S5_CAM_H 480
#define S5_VID_W 960 /* 640 × 1.5 */
#define S5_VID_H 720 /* 480 × 1.5 */
#define S5_VID_Y 0
#define S5_PANEL_X 960
#define S5_PANEL_W 320 /* 1280 - 960 */
#define S5_PANEL_H 720

/* ---- 布局选择（重要：G0 文本内部自相矛盾，需裁决）----
 * G0 冻结串：“1280×720 画布；摄像头 640×480 等比显示为 960×720 居中（左右各 160 px 黑边）；
 *              右侧 320×720 信息栏” —— 但 160 + 960 + 320 = 1440 > 1280，三个数字不可能同时成立。
 * 两种自洽解法（其余组合都会裁切画面或拉伸）：
 *   S5_LAYOUT_BARS=0（**默认**）：视频 0..959（960×720，4:3，无黑边）+ 信息栏 960..1279，互不重叠；
 *   S5_LAYOUT_BARS=1（字面方案）：视频 160..1119（左右各 160 黑边，居中），信息栏 960..1279
 *                                 覆盖视频右侧 160 px —— 可见画面被裁掉 1/6，不建议上板。
 * 两套都已实现并各自渲染了 PNG（build/frame_full*.png），等阶段总控/Wong 裁决后定默认值。 */
#ifndef S5_LAYOUT_BARS
#define S5_LAYOUT_BARS 0
#endif
#if S5_LAYOUT_BARS
#define S5_VID_X 160 /* 左黑边 */
#else
#define S5_VID_X 0 /* 无黑边：960×720 正好是 640×480 的 1.5 倍，4:3 不变形 */
#endif

/* 缩放系数：960/640 = 720/480 = 3/2（整数运算，误差 ≤1 px） */
#define S5_SCALE_NUM 3
#define S5_SCALE_DEN 2

/* 检测框线宽（G0 冻结） */
#define S5_BOX_LINE_W 2

/* ---------------- 颜色（0x00RRGGBB） ---------------- */
#define S5_RGB(r, g, b) ((((uint32_t)(r) & 0xFFu) << 16) | (((uint32_t)(g) & 0xFFu) << 8) | ((uint32_t)(b) & 0xFFu))
#define S5_COLOR_BLACK 0x00000000u
#define S5_COLOR_WHITE 0x00FFFFFFu
#define S5_COLOR_RED 0x00FF0000u
#define S5_COLOR_GREEN 0x0000FF00u
#define S5_COLOR_BLUE 0x000000FFu
#define S5_COLOR_YELLOW 0x00FFFF00u
#define S5_COLOR_CYAN 0x0000FFFFu
#define S5_COLOR_MAGENTA 0x00FF00FFu
#define S5_COLOR_GRAY 0x00808080u
/* 信息栏配色（深色底 + 高对比文字） */
#define S5_COLOR_PANEL_BG 0x00101820u
#define S5_COLOR_PANEL_TITLE 0x0000D7FFu
#define S5_COLOR_PANEL_TEXT 0x00E0E0E0u
#define S5_COLOR_PANEL_DIM 0x00909090u
#define S5_COLOR_OK 0x0000E676u
#define S5_COLOR_WARN 0x00FFB020u
#define S5_COLOR_BAD 0x00FF4040u
/* 透明：文字背景不写（用于叠加在画面上） */
#define S5_COLOR_TRANSPARENT 0xFFFFFFFFu

/* ---------------- 检测结果 ---------------- */
#define S5_MAX_DET 16
#define S5_CLASS_NUM 5 /* 五类带框手势检测（类别名见 .c 的表，占位待阶段5 确认） */

/* 一个检测框：坐标是**摄像头原始 640×480 坐标**（不是画布坐标），
 * 由 S5Draw_Boxes() 按冻结的 letterbox 映射换算到画布。 */
typedef struct S5DetBox {
    int16_t x;
    int16_t y;
    int16_t w;
    int16_t h;
    uint8_t cls;   /* 0..S5_CLASS_NUM-1 */
    uint8_t score; /* 0..100，整数百分比（面板按整数打印） */
} S5DetBox;

/* ---------------- 每帧信息（数值全部由调用方/模拟源给出） ---------------- */
#define S5_ST_CAM_OK 0x0001u
#define S5_ST_INF_OK 0x0002u
#define S5_ST_DMA_ERR 0x0004u /* VDMA SR 错误位非 0 */
#define S5_ST_AGE_OVER 0x0008u /* 结果年龄超 1 帧 + 16.7 ms */
#define S5_ST_TEAR 0x0010u     /* 写侧等不到安全窗口，可能撕裂 */
#define S5_ST_CAM_LOST 0x0020u
#define S5_ST_STALE 0x0040u   /* 结果块 status.bit2：结果超 1 帧（面板显示 STALE） */
#define S5_ST_OVERRUN 0x0080u /* 结果块 status.bit1：结果丢失（面板显示 OVR） */

/* 结果年龄上限：1 帧（16.7 ms）+ 16.7 ms ≈ 33.4 ms，取整 33 ms（G0 冻结） */
#define S5_AGE_LIMIT_MS 33u
/* 720p60 帧周期 */
#define S5_FRAME_MS 17u

/* 本帧数据来源（RESULT 的 src 字段 / 面板 SRC 行；ABI 见 s5_result_abi.h）
 *   REAL      = 真实结果块 + 真实 raw 画面（有框）
 *   REAL_NOBOX= 结果块不可用但 raw 有效 → 只画真实画面、不画框（r05，pass 可为 1）
 *   TEST      = raw 全 0 → 测试图案；无生产者时的合法上屏自检（pass=1）
 *   SIM       = 仅当 S5_SOURCE_REAL=0（强制模拟）或测试图案也失败（pass=0） */
#define S5_SRC_NONE 0u
#define S5_SRC_REAL 1u
#define S5_SRC_SIM 2u
#define S5_SRC_TEST 3u
#define S5_SRC_REAL_NOBOX 4u

typedef struct S5FrameInfo {
    uint32_t frame_id;
    uint16_t fps_cap_x10;  /* 采集口径，×10（301 = 30.1 fps） */
    uint16_t fps_inf_x10;  /* 推理口径 */
    uint16_t fps_dis_x10;  /* **显示刷新率**（≈600 = 60.0 fps；来自 VDMA 帧周期测量） */
    uint16_t fps_upd_x10;  /* **软件更新（渲染）速率**（≈350 = 35.0 fps） */
    uint16_t latency_ms;   /* 显示延迟 = t_display_start - t_infer_done */
    uint16_t age_ms;       /* 结果年龄 = t_display_start - t_capture_end */
    uint16_t status;       /* S5_ST_* 位或 */
    uint8_t det_count;     /* 有效检测框个数（<= S5_MAX_DET） */
    uint8_t src_kind;      /* S5_SRC_*：本帧数据来源（面板/RESULT 的 src 用） */
    S5DetBox det[S5_MAX_DET];
} S5FrameInfo;

/* ---------------- 有界运行 + 结果行（runner 契约；字段名/单位写死，不得改） ----------------
 * 上屏窗口的执行器按固定契约解析，改动字段名/单位会直接让判据失效。
 * 单位：fps_cap/fps_inf/fps_dis = **整数 fps（0..60）**，不是 ×10；
 *       latency_ms / age_ms = 整数毫秒；frames/vcnt/vdma_err = 计数。 */
#define S5_RUN_FRAMES 180u  /* 默认帧数上限；可用 -DS5_RUN_FRAMES=N 覆盖 */
#define S5_RUN_MAX_MS 60000u /* 或运行 ≥60 s，先到者停机（UART 采集器可收尾） */
/* 长时间运行（G3 / S6-F 30 min）：-DS5_LONG_RUN=1 时帧数上限取消，仅按时间上限退出 */
#ifndef S5_LONG_RUN
#define S5_LONG_RUN 0
#endif
#define S5_RUN_MAX_MS_LONG 1800000u /* 1800 s = 30 min */
#define S5_TICK_MS 60000u           /* 长跑时每 60 s 打一行 S5DISP tick（看是否死锁） */
/* 空闲测速（r06c，G3-A 定位）：-DS5_IDLE_PROBE=1 时只跑 10 帧，然后停写帧存、VDMA 继续跑 3 s，
 * 期间测 PARKPTR.READSTR 切换周期 → 区分“CPU 写 DDR 抢带宽”与“VDMA/HP2 通路本身到不了”。 */
#ifndef S5_IDLE_PROBE
#define S5_IDLE_PROBE 0
#endif
#define S5_IDLE_PROBE_FRAMES 10u  /* 先渲染这么多帧，再进入空闲观测 */
#define S5_IDLE_PROBE_MS 3000u    /* 空闲观测窗口 3 s */
/* P3m 硬件（2026-10-30）：删除 VTC 与 vid_out，时序由 PL 的 axis_to_video 自产 720p60。
 * S5_NO_VTC=1（默认）：软件完全不访问 VTC（0x43C30000 在 P3m 不存在，误访问可能挂总线）。
 * P3b 回归：-DS5_NO_VTC=0 -DS5_VDMA_BASE=0x43C40000u。 */
#ifndef S5_NO_VTC
#define S5_NO_VTC 1
#endif
/* underflow 像素计数（AXI GPIO 只读）：
 *   P3q（默认）：0x43C50000 = 本帧欠载（每 vsync 归零）、0x43C50004 = 累计（sticky）
 *   P3n：单寄存器 0x43C10000（累计）→ 两宏设相同
 *   P3p（fsync）：0x43C10000 本帧 / 0x43C10008 累计 */
#ifndef S5_UF_FRAME_REG
#define S5_UF_FRAME_REG 0x43C50000u  /* P3q：underflow GPIO（P2d 计算侧之外） */
#endif
#ifndef S5_UF_TOTAL_REG
#define S5_UF_TOTAL_REG 0x43C50008u  /* P3q：+0x08 = 累计欠载像素（axi_gpio 通道2 数据寄存器；
                                      * 注意 +0x04 是通道1 三态寄存器，不是数据！） */
#endif
#define S5_UF_GPIO_BASE S5_UF_FRAME_REG /* 兼容旧名（P3n 单寄存器语义） */
/* 确定性启动测试图（P3m 目视判读，默认开）：8 竖彩条（白/黄/青/绿/品红/红/蓝/黑）
 * + 四边 4 px 白框 + 中央白十字；A/B 两帧存画**同一张**（避免 circular 输出时两帧不同图案造成闪烁）；
 * VDMA 启动后先保持 S5_TEST_PATTERN_HOLD_MS 再进入渲染循环，便于目视。
 * -DS5_TEST_PATTERN=0 恢复旧行为（A=棋盘、B=彩条，仅用于区分帧存）。 */
#ifndef S5_TEST_PATTERN
#define S5_TEST_PATTERN 1
#endif
#define S5_TEST_PATTERN_HOLD_MS 2000u
/* 生产者模式（6-D）：同一份显示软件里模拟"生产端"每帧写结果块到 0x20800000，
 * 时间戳来自真实全局定时器（XTime_GetTime，COUNTS_PER_SECOND=333333343），frame_id 单调，
 * 用于给 Codex 阶段6 的 6-D 提供真实写端。S5_PRODUCER=1 开启；默认 0（消费外部生产者）。 */
#ifndef S5_PRODUCER
#define S5_PRODUCER 0
#endif
#define S5_PROD_EVERY_N 1u              /* 每 N 帧写一次（默认每帧） */
#define S5_PROD_INF_OFFSET_TICKS 2333334u /* 模拟推理完成 = cap + 7 ms（7e-3 * 333333343） */
#define S5_PROD_SESSION_TAG 0xA55Au     /* session 标记：写在检测项槽位 15 的 reserved */
/* 生产者 v2（sidecar S5X1 / seqlock / 故障注入），口径见 s5_publish_abi.h 与阶段6 6-D 冻结文档 */
#ifndef S5_PROD_FAULT
#define S5_PROD_FAULT 0 /* 0=none 1=overrun 2=stale 3=invalid 4=no_hand 5=按相位循环 */
#endif
#define S5_PROD_NO_HAND_EVERY_N 0u /* >0：每 N 帧注入 n_dets=0（NO_HAND）；0=关闭 */
#define S5_PROD_FAULT_PHASE 120u   /* S5_PROD_FAULT=5 时每个故障相位持续的帧数 */

#define S5_RESULT_PREFIX "S5DISP RESULT="

typedef struct S5RunStats {
    uint32_t pass;      /* 1=自检通过，0=失败 */
    uint32_t fps_cap;   /* 采集口径，整数 fps */
    uint32_t fps_inf;   /* 推理口径，整数 fps；无真实推理源时为 0（契约允许） */
    uint32_t fps_dis;   /* **显示刷新率**（≈60；VDMA 帧周期测量，非软件循环速率） */
    uint32_t fps_upd;   /* **软件更新（渲染）速率**（frames/elapsed，如实报告 ≈35） */
    uint32_t fps_dis_idle;  /* **空闲（不写帧存）时测得的显示刷新率**；未做空闲测速时为 0（r06c 新增） */
    uint32_t idle_period_us; /* 空闲测速得到的 VDMA 读帧存周期（µs）；未测为 0（r06c 新增） */
    uint32_t latency_ms;
    uint32_t age_ms;
    uint32_t vdma_err;  /* VDMA SR 错误位累计次数 */
    uint32_t frames;    /* 实际渲染帧数 */
    uint32_t vcnt;      /* 软件观测的 VDMA 消耗帧计数（PARKPTR.READSTR 切换次数） */
    uint32_t box_crc;   /* 绘制所用检测框（映射后 960×720，[x,y,w,h]×u16 序列）的 CRC32 */
    uint32_t fb_crc;    /* 显示用 framebuffer（0x20000000 那帧，1280×720×4）的 CRC32，结束前算一次 */
    uint32_t uf_pix;    /* 兼容字段：等于 uf_total（P3n 单寄存器语义；无 GPIO 时 0xFFFFFFFF） */
    uint32_t uf_frame;  /* **P3p**：本帧欠载像素数（GPIO 0x43C10000，每 vsync 归零；P3n 恒 0） */
    uint32_t uf_total;  /* **P3p**：累计欠载像素数（GPIO 0x43C10008，sticky；P3n = uf_pix） */
    const char *src;    /* "real" / "real_nobox" / "test" / "sim"：本窗口数据源 */
    const char *reason; /* 失败/回退原因（ASCII，无引号）；无则 NULL */
} S5RunStats;

/* 生产者打包（纯函数，遵守冻结 ABI；身份 A：头 32 B + 检测项（≤14）+ sidecar 在 +0x100，flush 0x120）：
 *   buf 需要 (S5_RESULT_BLOCK_BYTES/4) 个 u32；det 为**源 640×480 坐标**的检测框；
 *   cap/inf 为全局定时器 ticks（64 位）；status 用 S5_RESULT_ST_* 位。
 *   检测项：u16 x,y,w,h + u8 cls + u8 score_q8 + u16 reserved(0) + u32 pad(0)，16 B 步进；
 *   session 标记写在槽位 15 的 reserved（0xA55A），其余保留字段恒 0。 */
void S5Prod_PackBlock(uint32_t *buf, uint32_t frame_id, uint32_t n_dets, const S5DetBox *det,
                      uint64_t cap_ticks, uint64_t inf_ticks, uint32_t status);

/* CRC32（IEEE 802.3，多项式 0xEDB88320，初值/结果异或 0xFFFFFFFF）。
 * 表在首次调用时生成（1 KiB .bss），后续查表；用于 box_crc / fb_crc。 */
uint32_t S5Display_Crc32(const void *data, uint32_t bytes);

/* 生成单行结果：S5DISP RESULT={...}（不含换行；调用方自行补 \r\n）。
 * 返回写入长度（不含结尾 0）。字段顺序与契约一致。 */
uint32_t S5Display_FormatResult(const S5RunStats *st, char *buf, uint32_t cap);
/* 绘制所用检测框（映射到画布坐标，u16 [x,y,w,h] 序列）的 CRC32（G3 比对用）。 */
uint32_t S5Display_BoxesCrc(const S5DetBox *det, uint32_t n);
/* 把框映射到 960×720 显示坐标（裁剪后），每框写入 out[4k..4k+3] = x,y,w,h；返回框数。 */
uint32_t S5Display_BoxesMapped(const S5DetBox *det, uint32_t n, uint16_t *out, uint32_t max_boxes);

/* 帧完整性自检：抽点确认视频区有内容、信息栏有文字（0=异常，1=OK）。 */
int S5Display_CheckFrame(const uint32_t *fb);

/* ---------------- 绘图原语（纯函数，可在主机渲染） ---------------- */
void S5Draw_Pixel(uint32_t *fb, int x, int y, uint32_t color);
void S5Draw_Clear(uint32_t *fb, uint32_t color);
void S5Draw_RectFill(uint32_t *fb, int x, int y, int w, int h, uint32_t color);
void S5Draw_RectLine(uint32_t *fb, int x, int y, int w, int h, int line_w, uint32_t color);
void S5Draw_Checker(uint32_t *fb, int cell, uint32_t c0, uint32_t c1);
void S5Draw_ColorBars(uint32_t *fb);
void S5Draw_GrayRamp(uint32_t *fb);
/* 文字：x,y 是左上角；bg 传 S5_COLOR_TRANSPARENT 表示只画前景像素 */
void S5Draw_Text(uint32_t *fb, int x, int y, const char *text, uint32_t fg, uint32_t bg);

/* 摄像头 640×480 → 画布 960×720 最近邻缩放 + 左右黑边 */
void S5Draw_CameraLetterbox(uint32_t *fb, const uint32_t *cam);
/* 检测框（2 px 线宽，颜色按类别）+ 类别名/分数标签 */
void S5Draw_Boxes(uint32_t *fb, const S5DetBox *det, uint32_t n);

/* MVP HUD：手势中文名 + 置信度 + latency + 5 类颜色边框 */
void S5Display_DrawHud(uint32_t *fb, const S5FrameInfo *info);
/* 右侧 320×720 信息栏 */
void S5Draw_InfoPanel(uint32_t *fb, const S5FrameInfo *info, uint32_t dma_state);

/* 一帧完整装配：清屏 → 视频区（摄像头画面或测试图案）→ 检测框 → 信息栏。
 * video_src: S5_VIDEO_SRC_CAM（真实/模拟画面）或 S5_VIDEO_SRC_TEST（raw 全 0 回退测试图案）。 */
#define S5_VIDEO_SRC_CAM 0u
#define S5_VIDEO_SRC_TEST 1u

void S5Display_RenderFrameSrc(uint32_t *fb, const uint32_t *cam, const S5FrameInfo *info,
                              uint32_t dma_state, uint32_t video_src);
/* 兼容旧入口（等价 video_src=S5_VIDEO_SRC_CAM）。 */
void S5Display_RenderFrame(uint32_t *fb, const uint32_t *cam,
                           const S5FrameInfo *info, uint32_t dma_state);

/* 测试图（证明上屏通路）：mode 0=棋盘 1=彩条 2=灰阶 */
void S5Display_TestPattern(uint32_t *fb, uint32_t mode);
/* 确定性测试图（P3m 判读）：8 竖彩条 + 4 px 白框 + 中央白十字（无随机、无文字遮挡关键区域） */
void S5Display_DeterministicPattern(uint32_t *fb);

/* dma_state 取值（信息栏显示用） */
#define S5_DMA_OFF 0u
#define S5_DMA_RUN 1u
#define S5_DMA_ERR 2u

/* ---------------- 模拟数据源（离线自测；接真实推理结果时替换实现） ---------------- */
/* 生成一帧“像真的”信息：帧号递增、三口径 FPS、延迟/年龄（用真实定时器换算）、
 * 1~3 个缓慢移动的检测框；每 47 帧注入一次超龄异常，便于验证告警路径。 */
void S5Sim_NextFrame(S5FrameInfo *info);

/* 生成一帧合成摄像头画面（640×480，含移动色块/渐变），供离线渲染与上电自检。 */
void S5Sim_CameraFrame(uint32_t *cam, uint32_t frame_id);

#endif /* S5_DISPLAY_APP_H */
