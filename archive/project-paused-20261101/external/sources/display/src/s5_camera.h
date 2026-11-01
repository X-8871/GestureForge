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
#define S5_CAM_RAW_BASE 0x12000000u
#define S5_CAM_VDMA_FRMPTR S5_CAM_RAW_BASE /* v23：VDMA 目标；阶段3 的 0x00114C00 在 P3r 落在本 ELF RW 段内，不可用 */ /* 与显示 raw ABI 相同 */
#ifndef S5_CAM_CAPTURE_1280
#define S5_CAM_CAPTURE_1280 1
#endif
#if S5_CAM_CAPTURE_1280
#define S5_CAM_CAP_W 1280u
#else
#define S5_CAM_CAP_W 640u
#endif
#ifndef S5_CAM_H
#define S5_CAM_H 480u
#endif
#define S5_CAM_BPP 3u

/* B 路线（默认）：采集 1280x480（sensor 2x 子采样，r31 已验证出流）；显示侧水平 2x 抽样到 640x480。
 * -D S5_CAM_CAPTURE_1280=0 切回 640x480 直采。 */
#if S5_CAM_CAPTURE_1280
#define S5_CAM_VSIZE 720u  /* v22：阶段3 等价 1280x720 / VTS=740 */
#define S5_CAM_VDMA_VSIZE 720u /* v35：dvpvo 已可写回 720，VDMA 统一 720（三处全对齐） */
#define S5_CAM_HSIZE 3840u
#define S5_CAM_STRIDE 3840u
#else
#define S5_CAM_VSIZE 480u
#define S5_CAM_HSIZE 1920u
#define S5_CAM_STRIDE 1920u
#endif
#define S5_CAM_FRAME_BYTES (S5_CAM_STRIDE * S5_CAM_VSIZE) /* 1280x960: 3,686,400 */
_Static_assert((S5_CAM_FRAME_BYTES == 2764800u) || (S5_CAM_FRAME_BYTES == 921600u),
               "S5_CAM frame bytes must be 1280x720x3 or 640x480x3");
_Static_assert((S5_CAM_STRIDE % 8u) == 0u, "HSIZE must be 8-byte aligned");
#define S5_CAM_SCCB_ADDR 0x3Cu /* OV5640 7 位地址 0x3C（写 0x78 / 读 0x79） */
/* ---- 相机复位（阶段3 XPAR_CMOS_RST：AXI GPIO ch1 data @0x41200000，**低有效**） ----
 * 阶段3 实测时序（dbdf display_demo.c L259–267）：输出方向 → 写 1 → 500 ms → 写 0 → 500 ms
 * → 写 1 → 500 ms → 再 sensor_init。我们同样做"释放→保持→断言→保持→释放→保持"再 SCCB。 */
#ifndef S5_CAM_RST_REG
#define S5_CAM_RST_REG 0x41200000u
#endif
#ifndef S5_CAM_RST_ACTIVE_LOW
#define S5_CAM_RST_ACTIVE_LOW 1u
#endif
#ifndef S5_CAM_RST_HOLD_MS
#define S5_CAM_RST_HOLD_MS 500u
#endif
#ifndef S5_CAM_I2C_TARGET_HZ
#define S5_CAM_I2C_TARGET_HZ 40000u /* 阶段3 实机用 40 kHz（display_demo.c:257）；弱上拉+33Ω 串阻下更稳 */
#endif
/* 诊断版（S5_CAM_DIAG=1）：打印原始寄存器值、复位序列、I2C 分频候选、CHIPID 子码 */
#ifndef S5_CAM_DIAG
#define S5_CAM_DIAG 0
#endif
#define S5_CAM_DIAG_CANDS 6u


#ifndef S5_CAM_I2C_CLK_HZ
#define S5_CAM_I2C_CLK_HZ 111111115u /* Zynq PS I2C0 参考时钟（板上按 xparameters 再核） */
#endif

/* S2MM 寄存器偏移（axi_vdma v6.x 直接模式；依据 xaxivdma_hw.h + xaxivdma_channel.c）
 * Channel->StartAddrBase：S2MM = base + XAXIVDMA_S2MM_ADDR_OFFSET(0xA0)、MM2S = base + 0x50
 * 通道内：VSIZE +0x00、HSIZE +0x04、STRIDE/FRMDLY +0x08、FRMPTR1.. +0x0C+4*i
 * ⇒ S2MM: VSIZE=0xA0、HSIZE=0xA4、STRIDE=0xA8、FRMPTR1..=0xAC/0xB0/0xB4/0xB8
 * 注意：0xA0 是 VSIZE，不是帧指针（v7 写帧地址写错位置是 rc=-14 的直接原因）。 */
#define S5_CAM_S2MM_CR 0x30u
#define S5_CAM_S2MM_SR 0x34u
#define S5_CAM_S2MM_VSIZE 0xA0u
#define S5_CAM_S2MM_HSIZE 0xA4u
#define S5_CAM_S2MM_STRIDE 0xA8u
#define S5_CAM_S2MM_ADDR0 0xACu
#define S5_CAM_S2MM_ADDR1 0xB0u
#define S5_CAM_S2MM_VER 0x2Cu
#define S5_CAM_CR_RUNSTOP 0x00000001u
#define S5_CAM_CR_TAIL_EN 0x00000002u
#define S5_CAM_CR_RESET 0x00000004u
#define S5_CAM_SR_HALTED 0x00000001u
#define S5_CAM_SR_IDLE 0x00000002u
#define S5_CAM_SR_ERR_ALL 0x00000FF0u  /* XAXIVDMA_SR_ERR_ALL_MASK */
#define S5_CAM_SR_FRMCNT_MASK 0x00FF0000u /* bit[23:16] FRMCNT */
#define S5_CAM_SR_FRMCNT_SHIFT 16u

/* PS I2C0 寄存器（Cadence；与 Vitis iicps_v3_23 xiicps_hw.h 一致） */
#define S5_I2C_CR 0x00u
#define S5_I2C_SR 0x04u
#define S5_I2C_ADDR 0x08u
#define S5_I2C_DATA 0x0Cu
#define S5_I2C_ISR 0x10u
#define S5_I2C_TRANS_SIZE 0x14u
#define S5_I2C_TIME_OUT 0x1Cu
#define S5_I2C_IMPR 0x20u /* 控制器版本（诊断用） */
/* Cadence(PS I2C) CR 位（Vitis iicps_v3_23/xiicps_hw.h 原文）：
 * bit0 RD_WR（1=master read，0=master write）、bit1 MS（MASTER）、bit2 NEA（7bit）、
 * bit3 ACKEN、bit4 HOLD（重复起始/保持总线）、bit5 SLVMON、bit6 CLR_FIFO（自清）。
 * 注意：旧代码把 bit0 当 "ENABLE" 恒置 1 ⇒ 写事务方向错；MASTER 是 bit1=0x2（不是 0x20）。 */
#define S5_I2C_CR_RD_WR 0x00000001u
#define S5_I2C_CR_EN S5_I2C_CR_RD_WR /* 兼容旧名：实为 RD_WR，写事务必须清 0 */
#define S5_I2C_CR_MS 0x00000002u
#define S5_I2C_CR_NEA 0x00000004u
#define S5_I2C_CR_ACKEN 0x00000008u
#define S5_I2C_CR_HOLD 0x00000010u
#define S5_I2C_CR_CLR_FIFO 0x00000040u
#define S5_I2C_CR_DIV_B_MASK 0x00003F00u /* [13:8] */
#define S5_I2C_CR_DIV_A_MASK 0x0000C000u /* [15:14] */
#define S5_I2C_SR_TXDV 0x00000040u
#define S5_I2C_SR_RXDV 0x00000020u
/* ISR 位（与 Vitis iicps_v3_23/xiicps_hw.h 的 XIICPS_IXR_*_MASK 一致）
 * 注意：COMP=0x1、DATA=0x2、NACK=0x4、TO=0x8、SLV_RDY=0x10、RX_OVR=0x20、
 *       TX_OVR=0x40、RX_UNF=0x80、ARB_LOST=0x200；旧版把 NACK/ARB/TO 写错，已修。 */
#define S5_I2C_ISR_COMP 0x00000001u
#define S5_I2C_ISR_DATA 0x00000002u
#define S5_I2C_ISR_NACK 0x00000004u
#define S5_I2C_ISR_TO 0x00000008u
#define S5_I2C_ISR_SLV_RDY 0x00000010u
#define S5_I2C_ISR_RX_OVR 0x00000020u
#define S5_I2C_ISR_TX_OVR 0x00000040u
#define S5_I2C_ISR_RX_UNF 0x00000080u
#define S5_I2C_ISR_ARB 0x00000200u
#define S5_I2C_ISR_ERR_ALL (S5_I2C_ISR_NACK | S5_I2C_ISR_TO | S5_I2C_ISR_RX_OVR | \
                            S5_I2C_ISR_TX_OVR | S5_I2C_ISR_RX_UNF | S5_I2C_ISR_ARB)
#define S5_I2C_SR_BUSY 0x00000100u

/* 传感器 640×480 覆盖（在阶段3 基线 720p 初始化之后写；PCLK 保持 84 MHz，HTS 保持 1892，
 * VTS=1480 → 1892×1480×30 = 84.0 MHz ⇒ 30 fps；线间隙 1252、场间隙 1,892,000，
 * 故 PL 的 GAP_THRESH=16384 仍严格夹在两者之间，不需要改补丁）。 */
#define S5_CAM_VTS 740u /* 0x05C8；若改 60fps 用 740（0x02E4） */

/* 厂商 IP alinx_ov5640 上电等待：reset_cnt 200M + fifo_ready_cnt 100M PCLK ≈ 3.6 s@84MHz
 * （RTL 事实，video-bd 提供）；软件在 stream on 后等待该时长再配/启 VDMA。 */
#ifndef S5_CAM_IP_WARMUP_MS
#define S5_CAM_IP_WARMUP_MS 12000u  /* 12 s：覆盖 PCLK=42MHz 时 300M PCLK≈7.14 s 的假设 */
#endif
#ifndef S5_CAM_IP_SETTLE_MS
#define S5_CAM_IP_SETTLE_MS 2000u    /* 诊断：warmup 之后、几何探测之前再等 2 s */
#endif

extern uint32_t S5Cam_StreamOnMs; /* stream on 时刻（now_ms 域） */
extern uint32_t S5Cam_WarmupMs;   /* 实测 warmup 耗时（now_ms 域） */

typedef struct S5CamBus {
    void *ctx; /* 自检用：记录器/假寄存器堆 */
    uint32_t (*rd)(void *ctx, uint32_t addr);
    void (*wr)(void *ctx, uint32_t addr, uint32_t val);
    void (*delay_us)(void *ctx, uint32_t us); /* 可为 NULL（主机自检跳过延时） */
    uint32_t (*now_ms)(void); /* 可选：毫秒时基（warmup 实测/打印） */
} S5CamBus;

typedef struct S5CamInfo {
    uint16_t chip_id;   /* 期望 0x5640 */
    uint16_t dvpho;     /* 期望 640 */
    uint16_t dvpvo;     /* 期望 480 */
    uint16_t hts;       /* 期望 1892 */
    uint16_t vts;       /* 期望 S5_CAM_VTS */
    uint32_t frames;    /* S2MM 观测到的帧数（软件计数） */
    uint32_t vdma_sr;   /* 最近一次 S2MM SR */
    uint32_t vsreg;     /* 探测到的 VSIZE 偏移 */
    uint32_t hsreg;     /* 探测到的 HSIZE 偏移 */
    uint32_t strreg;    /* 探测到的 STRIDE 偏移 */
} S5CamInfo;

/* ---- VDMA(S2MM) 诊断：寄存器偏移候选 + 逐项 trace ---- */
#define S5_CAM_VDMA_TRACE_MAX 24u
#define S5_CAM_VDMA_CAND 3u

typedef struct S5CamVdmaStep {
    const char *name;
    uint32_t off;
    uint32_t wval;
    uint32_t rval;
    uint32_t expect;
    uint8_t has_expect;
    uint8_t ok;
} S5CamVdmaStep;

typedef struct S5CamVdmaTrace {
    S5CamVdmaStep step[S5_CAM_VDMA_TRACE_MAX];
    uint32_t n;
    int first_bad; /* -1=无 */
    uint32_t cand; /* 命中的候选集合索引 */
    uint32_t base;
} S5CamVdmaTrace;

/* ---- v12：系统/PLL/接口寄存器回读核对 ---- */
typedef struct S5CamRegCheck {
    uint16_t reg;
    uint8_t expect;
    uint8_t read;
    uint8_t ok;
} S5CamRegCheck;

uint32_t S5Cam_KeyRegList(uint16_t *regs, uint32_t max);
int S5Cam_LastWritten(uint16_t reg, uint8_t *val);
int S5Cam_CheckKeyRegs(const S5CamBus *bus, S5CamRegCheck *out, uint32_t max,
                       uint32_t *n, uint32_t *mismatch);

/* ---- OV5640 完整初始化表（阶段3 冻结件照抄）与 stream on ---- */
uint32_t S5Cam_InitTableCount(void);
int S5Cam_ApplyInitTable(const S5CamBus *bus); /* 302 项；0x3008 每写后延 5ms（含 soft reset） */
int S5Cam_StreamOn(const S5CamBus *bus);       /* 0x3008=0x02 + 20ms + 回读 */
int S5Cam_StreamOff(const S5CamBus *bus);      /* 0x3008=0x42 + >=10ms（改时序前必须停流） */
int S5Cam_StreamWithPolarity(const S5CamBus *bus, uint8_t pol4740); /* stream off → 写 0x4740 → stream on */
int S5Cam_SetPolarity(const S5CamBus *bus, uint8_t val);            /* 仅写 0x4740（HREF/VSYNC 极性） */      /* 0x3008=0x42 + >=10ms（改时序前必须停流） */
int S5Cam_ApplyTiming(const S5CamBus *bus);    /* 时序敏感覆盖重写：子采样/偏移/HTS/VTS/DVPHO/DVPVO/PLL */       /* 0x3008=0x02 + 20ms + 回读 */

/* v13：换几何重配（诊断用） + SR 错误位汇总 */
uint32_t S5Cam_SrErrors(uint32_t sr);
uint32_t S5Cam_TheoryPclk(uint32_t hts, uint32_t vts, uint32_t fps); /* SR & 0x0FF0 */
/* v17：单组几何探测（CR=0 → 等 HALTED=1 → W1C 清 SR → 配 → CR=1 → 等 HALTED=0 → 等 250ms → 读 SR → CR=0）
 * 全 fail-safe：任何一步超时返回 -4 并给出最后 SR；*sr_out 始终有效。 */
/* v20：配置一组几何并启动，**不停止**（tvalid 被 tready 门控，观察时必须保持 VDMA 运行） */
int S5CamVdma_StartGeometry(const S5CamBus *bus, uint32_t vsize, uint32_t hsize, uint32_t stride,
                            uint32_t *sr_out);

/* v33：清 S2MM SR（W1C 0x7F0），返回清前/清后；用于判断 FSZ_MORE 是否每帧复现 */
int S5Cam_VdmaClearSr(const S5CamBus *bus, uint32_t *sr_before, uint32_t *sr_after);

/* v25（驱动 xaxivdma_channel.c L1004-1030）：direct 模式启动 =
 * 配置后 CR: 清 TAIL_EN/SYNC_EN/FRMCNT_EN/RD_PTR，置 RS=1，写 CR；
 * 然后**再写一次 VSIZE(0xA0)** 作为 kick-off（这是关键，缺它则只收 beat 不写 DDR）。 */
#define S5_CAM_CR_CLEAR_START_MASK (S5_CAM_CR_TAIL_EN | 0x8u | 0x10u | 0xF00u)
#define S5_CAM_S2MM_CR_START S5_CAM_CR_RUNSTOP /* v25：direct 模式启动仅 RS=1，不带 TAIL_EN */
#define S5_CAM_S2MM_FRMSTORE 0x48u /* 仅打印回读用；驱动从不写 FRMSTORE */

int S5CamVdma_Probe(const S5CamBus *bus, uint32_t vsize, uint32_t hsize, uint32_t stride,
                    uint32_t *sr_out, S5CamVdmaTrace *tr);

int S5CamVdma_Reconfig(const S5CamBus *bus, uint32_t vsize, uint32_t hsize, uint32_t stride,
                       S5CamVdmaTrace *tr, uint32_t *sr_out);
/* SR 解码（掩码判据）：halted=bit0、err=0x0FF0、frmcnt=[23:16]；FRMCNT 不参与判错 */
void S5Cam_SrDecode(uint32_t sr, int *halted, uint32_t *err, uint32_t *frmcnt);

/* 自适应探测并配置 S2MM（写序：reset→HALTED→候选探测→配置→清 RESET→HALTED=0） */
int S5CamVdma_Config(const S5CamBus *bus, S5CamInfo *info, S5CamVdmaTrace *tr);
/* 启动：CR=RUNSTOP|TAIL_EN(=0x3) + 写 VSIZE 触发 */
int S5CamVdma_Start(const S5CamBus *bus);

/* ---- I2C 后端选择：gpio_sccb(0x43C80000，build7 已验证) 或 PS I2C0 ---- */
#define S5_CAM_I2C_BACKEND_PS 0
#define S5_CAM_I2C_BACKEND_GPIO 1
#ifndef S5_CAM_I2C_BACKEND
#define S5_CAM_I2C_BACKEND S5_CAM_I2C_BACKEND_GPIO /* 当前可用通道：gpio_sccb */
#endif
#define S5_CAM_GPIO_CTRL 0x43C80000u /* 写：bit0 mode(1=手动) bit1 SCL拉低 bit2 SDA拉低 */
#define S5_CAM_GPIO_STAT 0x43C80008u /* 读：bit0 SCL 电平 bit1 SDA 电平 */
#define S5_CAM_GPIO_MODE 0x00000001u
#define S5_CAM_GPIO_SCL_LOW 0x00000002u
#define S5_CAM_GPIO_SDA_LOW 0x00000004u
#ifndef S5_CAM_GPIO_HALF_US
#define S5_CAM_GPIO_HALF_US 40u /* 半周期延时（µs）≈12.5 kHz SCCB；弱上拉+33Ω 下更稳 */
#endif
#ifndef S5_CAM_GPIO_SAMPLE_US
#define S5_CAM_GPIO_SAMPLE_US 4u /* SCL 拉高后到采样 SDA 的额外延时（µs） */
#endif

/* ---- SLCR（I2C0 复位语义排查，v4） ---- */
#define S5_CAM_SLCR_BASE 0xF8000000u
#define S5_CAM_SLCR_UNLOCK 0xF8000008u /* 写 0xDF0D 解锁 */
#define S5_CAM_SLCR_LOCK 0xF8000004u   /* 写 0x767B 上锁 */
#define S5_CAM_SLCR_UNLOCK_VAL 0xDF0Du
#define S5_CAM_SLCR_LOCK_VAL 0x767Bu
#define S5_CAM_SLCR_I2C_RST 0xF8000214u /* I2C_RST_CTRL：bit0=I2C0 复位 */
#define S5_CAM_SLCR_APER 0xF800012Cu    /* APER_CLK_CTRL：bit18=I2C0_CPU_1XCLKACT */

/* SLCR 读（自动解锁/上锁），返回寄存器值 */
uint32_t S5Cam_SlcrRead(const S5CamBus *bus, uint32_t reg);
/* SLCR 写（自动解锁/上锁） */
void S5Cam_SlcrWrite(const S5CamBus *bus, uint32_t reg, uint32_t val);
/* I2C0 复位脉冲：若 bit0=1 或 force!=0，则断言 bit0=1 → 释放 bit0=0 → 等 10 ms；
 * before/after 返回调用前后的 I2C_RST_CTRL 值；返回 0=正常（after bit0=0） */
int S5Cam_I2cRstPulse(const S5CamBus *bus, uint32_t force, uint32_t *before, uint32_t *after);

/* ---- 诊断取证：SCCB 逐字节 trace（S5_CAM_DIAG=1 使用） ---- */
#define S5_CAM_TRACE_MAX 16u

#define S5_CAM_TR_START 1u  /* 起始条件 + 写地址字节 */
#define S5_CAM_TR_REG_HI 2u /* 寄存器地址高字节 */
#define S5_CAM_TR_REG_LO 3u /* 寄存器地址低字节 */
#define S5_CAM_TR_RSTART 4u /* 重复起始 + 读地址字节 */
#define S5_CAM_TR_DATA 5u   /* 读回的数据字节 */
#define S5_CAM_TR_STOP 6u   /* 停止条件（清 HOLD） */

typedef struct S5CamTraceStep {
    uint8_t kind;
    uint8_t byte;      /* 该步写入/读到的字节（无字节时忽略） */
    uint8_t have_byte;
    uint8_t bits; /* 读字节时采到的 8 位电平（bit7..bit0 的时间顺序，1=高） */
    uint32_t isr;
    uint32_t sr;
    uint32_t cr;
    uint32_t addr;
    uint32_t trsz;
} S5CamTraceStep;

typedef struct S5CamTrace {
    S5CamTraceStep step[S5_CAM_TRACE_MAX];
    uint32_t n;
    uint32_t final_isr;
    uint32_t final_sr;
    uint32_t final_cr;
    uint32_t final_addr;
    uint32_t final_trsz;
    uint32_t acks; /* bit0=addr bit1=reg_hi bit2=reg_lo bit3=rstart（1=ACK） */
    int rc;
} S5CamTrace;

typedef struct S5CamRegDump {
    uint32_t cr;
    uint32_t sr;
    uint32_t isr;
    uint32_t addr;
    uint32_t trsz;
    uint32_t busy;
    uint32_t impr;
} S5CamRegDump;

/* 抓取 I2C0 寄存器快照（诊断用） */
void S5Cam_RegDump(const S5CamBus *bus, S5CamRegDump *d);
/* 带逐字节 trace 的 SCCB 寄存器读（两段式：写 16b 寄存器地址 → 重复起始读 nbytes）
 * 返回 0=成功；-2=地址阶段 TXDV 超时；-3=寄存器地址字节 TXDV 超时；-4=NACK；
 *      -5=硬件超时(TO)；-6=仲裁/溢出；-7=读数据超时；-8=完成阶段超时 */
int S5Cam_ReadRegTrace(const S5CamBus *bus, uint8_t addr7, uint16_t reg,
                       uint8_t *val, uint32_t nbytes, S5CamTrace *tr);
/* SCCB 地址扫描：对 addr7 做一次"读 0x300A 1 字节"探测，返回 1=有应答/0=无应答/-1=其他错误 */
int S5Cam_ScanAddr(const S5CamBus *bus, uint8_t addr7, uint8_t *id, S5CamTrace *tr);

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

/* 复位序列（低有效）：返回 0；pin_before/pin_after 可为 NULL */
int S5Cam_ResetSeq(const S5CamBus *bus, uint32_t *pin_before, uint32_t *pin_after);

/* I2C 初始化并回读 CR/SR/分频值（诊断用；正常路径用 S5Cam_I2cInit） */
int S5Cam_I2cInitEx(const S5CamBus *bus, uint32_t cpu_hz, uint32_t *cr, uint32_t *sr, uint32_t *div);

/* 带子码的寄存器读：isr_addr=地址阶段 ISR，isr_data=数据阶段 ISR（诊断用）。
 * 返回 0=ok；-2=地址阶段失败(NACK/超时)；-3=写寄存器地址字节失败；-4=读数据超时；-5=完成阶段错误 */
int S5Cam_ReadRegEx(const S5CamBus *bus, uint16_t reg, uint8_t *val,
                    uint32_t *isr_addr, uint32_t *isr_data);

#endif /* S5_CAMERA_H */