/*
 * s5_camera.h —— R-07 / P3r：AN5642(OV5640) 640×480 采集 + S2MM VDMA（可选 S5_CAMERA=1）
 *
 * 数据宽度结论（以阶段3 冻结 BD 为准，见报告 §11.15）：
 *   ov5640_ip AXIS **16-bit（RGB565）** → `axis_subset_converter_0` 16→24 位（零填充扩展）
 *   → VDMA S2MM **24 bpp** → DDR 每像素 3 字节；阶段3 app 回读 HSIZE=STRIDE=0xF00=3840=1280×3
 *   与阶段3 实测 DDR 字节序 **B,G,R** 一致 ⇒ 正好等于阶段5 冻结的 raw ABI（BGR888 / stride 1920@640）。
 *   故 PS 侧**不做** 565→888 展开，只做 S2MM 配置（24bpp）与传感器窗口切换。
 *
 * 本模块可主机自检（S5_HOST_TEST）：所有 MMIO 通过 S5CamBus 函数指针注入，不直接依赖 Xilinx 头。
 */
#ifndef S5_CAMERA_H
#define S5_CAMERA_H

#include <stdint.h>

/* ---- 编译开关（与 producer/display 正交） ---- */
#ifndef S5_CAMERA
#define S5_CAMERA 0
#endif

/* ---- 地址/几何（P3r；VDMA 基址以最终 XSA 为准，宏可改） ---- */
#ifndef S5_CAM_I2C_BASE
#define S5_CAM_I2C_BASE 0xE0004000u /* PS I2C0（阶段3 使用 ps_i2c0） */
#endif
#ifndef S5_CAM_VDMA_BASE
#define S5_CAM_VDMA_BASE 0x43C60000u /* 相机 S2MM VDMA（P3r BD；最终以 XSA 为准） */
#endif
#define S5_CAM_RAW_BASE 0x12000000u /* 与显示 raw ABI 相同 */
#ifndef S5_CAM_W
#define S5_CAM_W 640u /* 与 s5_display_app.h 的相机源尺寸同义；避免宏重定义告警 */
#endif
#ifndef S5_CAM_H
#define S5_CAM_H 480u
#endif
#define S5_CAM_BPP 3u /* 24bpp（PL 已由 16→24 converter 展开） */
#define S5_CAM_STRIDE (S5_CAM_W * S5_CAM_BPP)   /* 1920 */
#define S5_CAM_FRAME_BYTES (S5_CAM_STRIDE * S5_CAM_H) /* 921,600 */
#define S5_CAM_SCCB_ADDR 0x3Cu /* OV5640 7 位地址 0x3C（写 0x78 / 读 0x79） */
#ifndef S5_CAM_I2C_CLK_HZ
#define S5_CAM_I2C_CLK_HZ 111111115u /* Zynq PS I2C0 参考时钟（板上按 xparameters 再核） */
#endif

/* S2MM 寄存器偏移（axi_vdma：S2MM 空间从 0x30 起） */
#define S5_CAM_S2MM_CR 0x30u
#define S5_CAM_S2MM_SR 0x34u
#define S5_CAM_S2MM_VSIZE 0x50u
#define S5_CAM_S2MM_HSIZE 0x54u
#define S5_CAM_S2MM_STRIDE 0x58u
#define S5_CAM_S2MM_ADDR0 0x5Cu
#define S5_CAM_S2MM_ADDR1 0x60u
#define S5_CAM_CR_RUNSTOP 0x00000001u
#define S5_CAM_CR_TAIL_EN 0x00000002u
#define S5_CAM_CR_RESET 0x00000004u
#define S5_CAM_SR_HALTED 0x00000001u
#define S5_CAM_SR_IDLE 0x00000002u
#define S5_CAM_SR_ERR_ALL 0x00000FF0u

/* PS I2C0 寄存器（Cadence；与 Vitis iicps_v3_23 xiicps_hw.h 一致） */
#define S5_I2C_CR 0x00u
#define S5_I2C_SR 0x04u
#define S5_I2C_ADDR 0x08u
#define S5_I2C_DATA 0x0Cu
#define S5_I2C_ISR 0x10u
#define S5_I2C_TRANS_SIZE 0x14u
#define S5_I2C_TIME_OUT 0x1Cu
#define S5_I2C_CR_EN 0x00000001u
#define S5_I2C_CR_MS 0x00000002u
#define S5_I2C_CR_NEA 0x00000004u
#define S5_I2C_CR_ACKEN 0x00000008u
#define S5_I2C_CR_HOLD 0x00000010u
#define S5_I2C_CR_CLR_FIFO 0x00000040u
#define S5_I2C_SR_TXDV 0x00000040u
#define S5_I2C_SR_RXDV 0x00000020u
#define S5_I2C_ISR_COMP 0x00000001u
#define S5_I2C_ISR_ERROR 0x00000002u
#define S5_I2C_ISR_NACK 0x00000010u
#define S5_I2C_ISR_ARB 0x00000020u
#define S5_I2C_ISR_TO 0x00000800u

/* 传感器 640×480 覆盖（在阶段3 基线 720p 初始化之后写；PCLK 保持 84 MHz，HTS 保持 1892，
 * VTS=1480 → 1892×1480×30 = 84.0 MHz ⇒ 30 fps；线间隙 1252、场间隙 1,892,000，
 * 故 PL 的 GAP_THRESH=16384 仍严格夹在两者之间，不需要改补丁）。 */
#define S5_CAM_VTS 1480u /* 0x05C8；若改 60fps 用 740（0x02E4） */

typedef struct S5CamBus {
    void *ctx; /* 自检用：记录器/假寄存器堆 */
    uint32_t (*rd)(void *ctx, uint32_t addr);
    void (*wr)(void *ctx, uint32_t addr, uint32_t val);
} S5CamBus;

typedef struct S5CamInfo {
    uint16_t chip_id;   /* 期望 0x5640 */
    uint16_t dvpho;     /* 期望 640 */
    uint16_t dvpvo;     /* 期望 480 */
    uint16_t hts;       /* 期望 1892 */
    uint16_t vts;       /* 期望 S5_CAM_VTS */
    uint32_t frames;    /* S2MM 观测到的帧数（软件计数） */
    uint32_t vdma_sr;   /* 最近一次 S2MM SR */
} S5CamInfo;

/* I2C0 初始化（polled master，7-bit 地址） */
int S5Cam_I2cInit(const S5CamBus *bus, uint32_t cpu_hz);
/* SCCB 单寄存器读写（16 位寄存器地址） */
int S5Cam_WriteReg(const S5CamBus *bus, uint16_t reg, uint8_t val);
int S5Cam_ReadReg(const S5CamBus *bus, uint16_t reg, uint8_t *val);
/* 读 CHIPID（0x300A/0x300B → 0x5640） */
int S5Cam_Probe(const S5CamBus *bus, uint16_t *chip_id);
/* 写 640×480 覆盖表（窗口/HTS/VTS/偏移），不做回读 */
int S5Cam_ApplyVga(const S5CamBus *bus);
/* 回读校验：0x3808/09=640、0x380A/0B=480、0x380C/0D=1892、0x380E/0F=VTS；≤3 次重试 */
int S5Cam_VerifyVga(const S5CamBus *bus, S5CamInfo *info);
/* S2MM VDMA：非 SG、24bpp、stride 1920、单地址 0x12000000（循环） */
int S5CamVdma_Init(const S5CamBus *bus, S5CamInfo *info);
int S5CamVdma_Start(const S5CamBus *bus);
int S5CamVdma_Stop(const S5CamBus *bus);
int S5CamVdma_Status(const S5CamBus *bus, uint32_t *sr);
/* 高层：I2C 初始化 → CHIPID → VGA 覆盖 → 回读 → S2MM 初始化/启动；返回 0=全部成功 */
int S5Cam_Init(const S5CamBus *bus, uint32_t cpu_hz, S5CamInfo *info);

#endif /* S5_CAMERA_H */