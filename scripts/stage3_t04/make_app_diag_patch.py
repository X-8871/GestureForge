"""生成 S3-T04/S3-T05 应用诊断补丁：只给厂商摄像头应用加 UART 诊断打印，不改任何寄存器时序与配置。

用法: make_app_diag_patch.py <厂商应用源目录> <输出补丁> <scratch 目录> [v4|v5|v6|v7|v8|v9|v10|v11|v12]

变体（默认 v5）：
  v4 = 延时启动 + FB 回读（历史补丁 s3_t04_app_diag_v4.patch，仍可逐字节复现）
  v5 = v4 + memset 后 DCache flush、DCache 失效后回读物理内存三处（S3_DIAG5_NZ）、
       S2MM SR 位解码 + 帧计数（S3_DIAG5_REG/SR_DECODE/CFG）、t≈5/15/25 秒三次采样、
       传感器关键寄存器只读回显（S3_DIAG5_SENS）、main 不返回
  v6 = 保留 v5 的辅助函数与一次性打印，把 v5 的三次 16 KB 采样换成帧缓冲 64 KB 区指纹五次采样
       （S3_DIAG6_FP：32 位加和 + 反射式 CRC-32/0xEDB88320，读前 Xil_DCacheInvalidateRange，
        t≈5/10/15/20/25 s，每次同时打印 S2MM SR），t≈30 s 传感器回读（S3_DIAG6_SENS），
       以及编译期开关 S3_TESTPATTERN（默认 0；=1 时启动 S2MM 前写 0x503D=0x80 彩条测试图）
  v7 = v6 + ISP/AWB 寄存器只读回读（0x5001/0x3406/0x3400..0x3405/0x3503/0x3500..0x3502/
       0x5580..0x558B/0x503D/0x4300/0x501F/0x3035），以及编译期开关 S3_AWB_OFF（默认 0；
       =1 时启动 S2MM 之前把 0x5001 bit0 清 0 关闭 AWB，并打印 before/after/write_status）
  v8 = v7 + 编译期手动白平衡：S3_WB_MANUAL（默认 0）+ S3_WB_R/S3_WB_G/S3_WB_B（默认 1024 = 1.0×）。
       =1 时启动 S2MM 之前写 0x3406=0x01 与 0x3400..0x3405（增益高位/低位），写入后立即回读校验
  v9 = v8 + DVP 端口/数据线 output select 只读回读（0x3017/0x3018/0x301D/0x301E/0x300A/0x300B/
       0x4741/0x4745/0x4300/0x501F + D9SEL/D6SEL 逐位判读），以及两个默认 0 的编译期写测试开关：
       S3_PAD_SEL_CLEAR（清 0x301D bit3 / 视回读清 0x301E bit1，写前后均回读校验）、
       S3_DVP_ORDER_DEBUG（置 0x4745[2:1]=10，不自动恢复，UART 明示 NOT_RESTORED）
  v10 = v9 + 传感器端去色（黑白）尝试：编译期 S3_GRAY_TRY=0/1/2/3
        （0=只回读不写；1=0x5583=0x5584=0x00 置 U/V 饱和度 0；2=0x5580 效果位 (rb&~0xC0)|0x40；
         3=(rb&~0xC0)|0x80），统一打印 before/after/readback，读失败跳过写入
  v11 = v10 + 取帧应用（供整帧导出）：指纹只做 3 次（t≈5/10/15 s），t≈20 s **停 S2MM**
        （清 S2MM_CR 的 RUN/STOP 位，停前/停后各做一次帧缓冲 cache 失效，打印
        S3_DIAG11_HALT=...），随后保持静止 240 s、每 30 s 一次 S3_DIAG11_HOLD 心跳；
        **不做任何寄存器写测试**（所有写开关保持默认 0）
  v12 = v11 + 传感器内置彩条测试图案：写 0x503D=0x80（先回读原值、写后回读校验，
        打印 S3_DIAG12_BARS=503D before/after/readback/write_status；读失败跳过写入），
        用于把**已知颜色**的图案经同一链路转储判读；保留 v11 的停帧保持能力

做四件事：
1) 从官方源复制一份应用目录到 scratch；
2) 在 main() 关键节点插入 S3_DIAG 打印；
3) 按变体追加 v5/v6/v7/v8/v9/v10/v11/v12 内容；
4) 用 git diff --no-index 生成 unified diff，并对全新副本验证补丁可干净应用。

只改 display_demo.c；输出补丁不进 Git 之外的地方。
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
# 归一化为绝对路径：验证步骤会用 cwd=<verify 副本> 调 git apply，相对路径会被解析到副本内部而失败。
OUT_PATCH = Path(sys.argv[2]).resolve()
SCRATCH = Path(sys.argv[3])
# 变体选择：默认 v5（最新诊断补丁）；v4 仍可显式指定以逐字节复现历史补丁。
VARIANT = sys.argv[4].strip().lower() if len(sys.argv) > 4 else "v5"
if VARIANT not in ("v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12"):
    print(f"UNKNOWN_VARIANT: {VARIANT}")
    sys.exit(2)

if SCRATCH.exists():
    shutil.rmtree(SCRATCH)
SCRATCH.mkdir(parents=True)
ORIG = SCRATCH / "orig"
WORK = SCRATCH / "work"
shutil.copytree(SRC, ORIG)
shutil.copytree(SRC, WORK)

FILE = "display_demo.c"
target = WORK / FILE
with open(target, "r", encoding="utf-8", newline="") as fh:
    raw = fh.read()
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

insertions = [
    (
        "int main(void)\n{\n\n\tint Status;",
        "int main(void)\n{\n\n\tint Status;\n\txil_printf(\"S3_DIAG_APP_ENTER\\r\\n\");",
    ),
    (
        "\tsensor_init(&ps_i2c0);\n",
        "\tsensor_init(&ps_i2c0);\n"
        "\t/* S3-DIAG: 传感器 I2C 连通性诊断；OV5640 CHIP ID 期望 0x5640 */\n"
        "\t{\n"
        "\t\tu8 s3_id_hi = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x300A);\n"
        "\t\tu8 s3_id_lo = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x300B);\n"
        "\t\txil_printf(\"S3_DIAG_SENSOR_ID=0x%02X%02X\\r\\n\", s3_id_hi, s3_id_lo);\n"
        "\t}\n",
    ),
    (
        "\tStatus = DisplayStart(&dispCtrl);\n",
        "\tStatus = DisplayStart(&dispCtrl);\n\txil_printf(\"S3_DIAG_DISPLAY_START status=%d\\r\\n\", Status);\n",
    ),
    (
        "\tvdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID,1280 * 3,720,1280 * 3,(unsigned int)dispCtrl.framePtr[dispCtrl.curFrame]);\n",
        "\t/* S3-DIAG4: 采集 IP 内部有 200M+100M 个 PCLK 周期的上电等待（见 alinx_ov5640.v 的\n"
        "\t * reset_cnt / fifo_ready_cnt），若不等它就绪就启动 S2MM，会在第一帧落下帧尺寸粘滞错误。*/\n"
        "\txil_printf(\"S3_DIAG4_WAIT_START\\r\\n\");\n"
        "\t{\n"
        "\t\tint s3_w;\n"
        "\t\tfor (s3_w = 0; s3_w < 15; s3_w++) { sleep(1); }\n"
        "\t}\n"
        "\txil_printf(\"S3_DIAG4_WAIT_DONE\\r\\n\");\n"
        "\tvdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID,1280 * 3,720,1280 * 3,(unsigned int)dispCtrl.framePtr[dispCtrl.curFrame]);\n"
        "\txil_printf(\"S3_DIAG_VDMA_WRITE_STARTED\\r\\n\");\n"
        "\t{\n"
        "\t\tint s3_w2;\n"
        "\t\tvolatile unsigned int *s3_fb = (volatile unsigned int *)dispCtrl.framePtr[dispCtrl.curFrame];\n"
        "\t\tfor (s3_w2 = 0; s3_w2 < 5; s3_w2++) { sleep(1); }\n"
        "\t\txil_printf(\"S3_DIAG4_FB=0x%08X 0x%08X 0x%08X 0x%08X\\r\\n\", s3_fb[0], s3_fb[1], s3_fb[2], s3_fb[3]);\n"
        "\t\txil_printf(\"S3_DIAG4_FB_MID=0x%08X 0x%08X\\r\\n\", s3_fb[960], s3_fb[961]);\n"
        "\t}\n",
    ),
    (
        "\tsensor_init(&ps_i2c0);\n"
        "\t/* S3-DIAG: 传感器 I2C 连通性诊断；OV5640 CHIP ID 期望 0x5640 */\n",
        "\tsensor_init(&ps_i2c0);\n"
        "\t/* S3-DIAG2: I2C 控制器寄存器 + 整总线扫描 + CHIP ID 重试读取。\n"
        "\t * 只读探测：用于区分“I2C 总线/连接不通（无任何 ACK）”与“器件存在但地址/配置不符”。*/\n"
        "\t{\n"
        "\t\tXIicPs *s3_iic = &ps_i2c0;\n"
        "\t\tint s3_a, s3_s, s3_s2;\n"
        "\t\tint s3_found = 0;\n"
        "\t\tu8 s3_wr[2];\n"
        "\t\txil_printf(\"S3_DIAG2_IIC_BASE=0x%08X\\r\\n\", (unsigned int)s3_iic->Config.BaseAddress);\n"
        "\t\txil_printf(\"S3_DIAG2_IIC_CR=0x%08X SR=0x%08X ISR=0x%08X\\r\\n\",\n"
        "\t\t\t(unsigned int)XIicPs_ReadReg(s3_iic->Config.BaseAddress, XIICPS_CR_OFFSET),\n"
        "\t\t\t(unsigned int)XIicPs_ReadReg(s3_iic->Config.BaseAddress, XIICPS_SR_OFFSET),\n"
        "\t\t\t(unsigned int)XIicPs_ReadReg(s3_iic->Config.BaseAddress, XIICPS_ISR_OFFSET));\n"
        "\t\tfor (s3_a = 0x08; s3_a < 0x78; s3_a++) {\n"
        "\t\t\tu8 s3_rd = 0;\n"
        "\t\t\ts3_wr[0] = 0x30; s3_wr[1] = 0x0A;\n"
        "\t\t\ts3_s = XIicPs_MasterSendPolled(s3_iic, s3_wr, 2, (u8)s3_a);\n"
        "\t\t\twhile (XIicPs_BusIsBusy(s3_iic));\n"
        "\t\t\tif (s3_s != XST_SUCCESS) { continue; }\n"
        "\t\t\ts3_s2 = XIicPs_MasterRecvPolled(s3_iic, &s3_rd, 1, (u8)s3_a);\n"
        "\t\t\twhile (XIicPs_BusIsBusy(s3_iic));\n"
        "\t\t\txil_printf(\"S3_DIAG2_DEV=0x%02X recv=%d val=0x%02X\\r\\n\", s3_a, s3_s2, s3_rd);\n"
        "\t\t\ts3_found++;\n"
        "\t\t}\n"
        "\t\txil_printf(\"S3_DIAG2_SCAN_ACK_COUNT=%d\\r\\n\", s3_found);\n"
        "\t\t{\n"
        "\t\t\tint s3_t;\n"
        "\t\t\tfor (s3_t = 0; s3_t < 3; s3_t++) {\n"
        "\t\t\t\tu8 s3_h = (u8)i2c_reg16_read(s3_iic, 0x3c, 0x300A);\n"
        "\t\t\t\tu8 s3_l = (u8)i2c_reg16_read(s3_iic, 0x3c, 0x300B);\n"
        "\t\t\t\txil_printf(\"S3_DIAG2_CHIPID_TRY%d=0x%02X%02X\\r\\n\", s3_t, s3_h, s3_l);\n"
        "\t\t\t\tusleep(200000);\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t}\n"
        "\t/* S3-DIAG3: 回读传感器关键寄存器，确认 sensor_init 的写是否生效（帧尺寸不匹配时用）*/\n"
        "\t{\n"
        "\t\tu8 d_3808 = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x3808);\n"
        "\t\tu8 d_3809 = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x3809);\n"
        "\t\tu8 d_380a = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x380A);\n"
        "\t\tu8 d_380b = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x380B);\n"
        "\t\tu8 d_380e = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x380E);\n"
        "\t\tu8 d_380f = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x380F);\n"
        "\t\tu8 d_3035 = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x3035);\n"
        "\t\tu8 d_3034 = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x3034);\n"
        "\t\tu8 d_4300 = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x4300);\n"
        "\t\tu8 d_501f = (u8)i2c_reg16_read(&ps_i2c0, 0x3c, 0x501F);\n"
        "\t\txil_printf(\"S3_DIAG3_OUT_W=0x%02X%02X(exp 0x0500)\\r\\n\", d_3808, d_3809);\n"
        "\t\txil_printf(\"S3_DIAG3_OUT_H=0x%02X%02X(exp 0x02D0)\\r\\n\", d_380a, d_380b);\n"
        "\t\txil_printf(\"S3_DIAG3_VTS=0x%02X%02X\\r\\n\", d_380e, d_380f);\n"
        "\t\txil_printf(\"S3_DIAG3_3035=0x%02X 3034=0x%02X 4300=0x%02X 501F=0x%02X\\r\\n\", d_3035, d_3034, d_4300, d_501f);\n"
        "\t}\n"
        "\t/* S3-DIAG: 传感器 I2C 连通性诊断；OV5640 CHIP ID 期望 0x5640 */\n",
    ),
]

# ---------------------------------------------------------------------------
# v5 变体追加内容（只在 VARIANT == "v5" 时生效，v4 输出保持不变）
# ---------------------------------------------------------------------------
V5_WRITE_INIT_NEW = (
    "\t/* S3-DIAG4: 采集 IP 内部有 200M+100M 个 PCLK 周期的上电等待（见 alinx_ov5640.v 的\n"
    "\t * reset_cnt / fifo_ready_cnt），若不等它就绪就启动 S2MM，会在第一帧落下帧尺寸粘滞错误。*/\n"
    "\txil_printf(\"S3_DIAG4_WAIT_START\\r\\n\");\n"
    "\t{\n"
    "\t\tint s3_w;\n"
    "\t\tfor (s3_w = 0; s3_w < 15; s3_w++) { sleep(1); }\n"
    "\t}\n"
    "\txil_printf(\"S3_DIAG4_WAIT_DONE\\r\\n\");\n"
    "\tvdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID,1280 * 3,720,1280 * 3,(unsigned int)dispCtrl.framePtr[dispCtrl.curFrame]);\n"
    "\txil_printf(\"S3_DIAG_VDMA_WRITE_STARTED\\r\\n\");\n"
    "\t/* S3-DIAG5: v5 用 cache 失效后的物理内存回读取代 v4 的 S3_DIAG4_FB/FB_MID\n"
    "\t * （那两行未失效 cache，读到的是脏零行，不可信）。\n"
    "\t * 启动后 t≈5/15/25 秒各采样一次，判断 DDR 帧缓冲是否真有 DMA 写进来的数据、\n"
    "\t * 以及数据是否随时间变化（活视频）。*/\n"
    "\ts3_diag5_regs(0);\n"
    "\t{\n"
    "\t\tint s3_k, s3_s;\n"
    "\t\tfor (s3_k = 0; s3_k < 3; s3_k++) {\n"
    "\t\t\tfor (s3_s = 0; s3_s < ((s3_k == 0) ? 5 : 10); s3_s++) { sleep(1); }\n"
    "\t\t\txil_printf(\"S3_DIAG5_SAMPLE=%d\\r\\n\", s3_k + 1);\n"
    "\t\t\ts3_diag5_regs(1);\n"
    "\t\t\ts3_diag5_site(0, 0x000000U);\n"
    "\t\t\ts3_diag5_site(1, 0x400000U);\n"
    "\t\t\ts3_diag5_site(2, 0x080000U);\n"
    "\t\t}\n"
    "\t}\n"
    "\txil_printf(\"S3_DIAG5_SAMPLING_DONE\\r\\n\");\n"
)

V5_HELPERS = (
    "/* ================= S3-DIAG5 只读诊断辅助（不改任何配置/时序） =================\n"
    " * S2MM/MM2S 状态寄存器位定义依据（三者一致，证据在 tmp/s3r06/t04_j11cmos2_elf_v5/）：\n"
    " *  1) 驱动头文件 axivdma_v6_17/src/xaxivdma_hw.h（任务卡引用 v6_15，位掩码同值）\n"
    " *  2) IP 元数据 data/ip/xilinx/axi_vdma_v6_3/component.xml -> S2MM_VDMASR 字段 bitOffset\n"
    " *  3) IP HDL axi_vdma_v6_3_vh_rfs.vhd -> DMASR_*_BIT 常量与状态寄存器拼装\n"
    " * bit4=DMAIntErr bit5=DMASlvErr bit6=DMADecErr bit7=FSizeErr(SOFEarlyErr)\n"
    " * bit8=LSizeErr(EOLEarlyErr) bit9=SGSlvErr bit10=SGDecErr bit11=FSizeMore/SOFLateErr\n"
    " * bit12=FrmCntIrq bit13=DlyCntIrq bit14=ErrIrq bit15=LSizeMore(EOLLateErr)\n"
    " * bit16..23=帧计数(IRQFrameCntSts) bit24..31=延迟计数\n"
    " * 注意：驱动头文件记 bit11 为 ERR_FSZ_MORE(0x800)，IP 元数据记为 SOFLateErr —— 同一物理位。*/\n"
    "static void s3_diag5_regs(u32 phase)\n"
    "{\n"
    "\tu32 s3_s2sr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_SR_OFFSET);\n"
    "\tu32 s3_s2cr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET);\n"
    "\tu32 s3_mmsr = XAxiVdma_ReadReg(XPAR_AXIVDMA_0_BASEADDR, XAXIVDMA_TX_OFFSET + XAXIVDMA_SR_OFFSET);\n"
    "\tu32 s3_vsz = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_S2MM_ADDR_OFFSET + 0x00);\n"
    "\tu32 s3_hsz = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_S2MM_ADDR_OFFSET + 0x04);\n"
    "\tu32 s3_str = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_S2MM_ADDR_OFFSET + 0x08);\n"
    "\tu32 s3_adr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_S2MM_ADDR_OFFSET + 0x0C);\n"
    "\txil_printf(\"S3_DIAG5_REG phase=%u S2MM_CR=0x%08X S2MM_SR=0x%08X FRMCNT=%u HALTED=%u IDLE=%u\\r\\n\",\n"
    "\t\tphase, s3_s2cr, s3_s2sr, (s3_s2sr >> XAXIVDMA_FRMCNT_SHIFT) & 0xFFU, s3_s2sr & 0x1U, (s3_s2sr >> 1) & 0x1U);\n"
    "\txil_printf(\"S3_DIAG5_SR_DECODE phase=%u INT=%u SLV=%u DEC=%u FSZ_LESS=%u LSZ_LESS=%u SG_SLV=%u SG_DEC=%u FSZ_MORE=%u FRMCNT_IRQ=%u DLY_IRQ=%u ERR_IRQ=%u LSZ_MORE=%u\\r\\n\",\n"
    "\t\tphase, (s3_s2sr >> 4) & 0x1U, (s3_s2sr >> 5) & 0x1U, (s3_s2sr >> 6) & 0x1U, (s3_s2sr >> 7) & 0x1U,\n"
    "\t\t(s3_s2sr >> 8) & 0x1U, (s3_s2sr >> 9) & 0x1U, (s3_s2sr >> 10) & 0x1U, (s3_s2sr >> 11) & 0x1U,\n"
    "\t\t(s3_s2sr >> 12) & 0x1U, (s3_s2sr >> 13) & 0x1U, (s3_s2sr >> 14) & 0x1U, (s3_s2sr >> 15) & 0x1U);\n"
    "\txil_printf(\"S3_DIAG5_CFG VSIZE=0x%08X HSIZE=0x%08X STRIDE=0x%08X ADDR=0x%08X MM2S_SR=0x%08X\\r\\n\",\n"
    "\t\ts3_vsz, s3_hsz, s3_str, s3_adr, s3_mmsr);\n"
    "}\n"
    "\n"
    "/* 只读：cache 失效后回读 DDR 物理内存；打印 4096 个字里的非零字个数与样本字。*/\n"
    "static void s3_diag5_site(u32 site, u32 off)\n"
    "{\n"
    "\tvolatile u32 *s3_p = (volatile u32 *)((u8 *)dispCtrl.framePtr[dispCtrl.curFrame] + off);\n"
    "\tu32 s3_i, s3_nz = 0;\n"
    "\t/* 卡要求：读帧缓冲前先失效 4096 B。NZ 统计覆盖 4096 个字（16 KB），\n"
    "\t * 故把剩余 12 KB 一并失效，否则统计区后段可能命中陈旧 cache 行。*/\n"
    "\tXil_DCacheInvalidateRange((INTPTR)s3_p, 4096);\n"
    "\tXil_DCacheInvalidateRange((INTPTR)s3_p + 4096, 4096 * 4 - 4096);\n"
    "\tfor (s3_i = 0; s3_i < 4096; s3_i++) {\n"
    "\t\tif (s3_p[s3_i] != 0U) { s3_nz++; }\n"
    "\t}\n"
    "\txil_printf(\"S3_DIAG5_NZ site=%u off=0x%06X nz=%u/4096 fb0=%08X %08X %08X %08X %08X %08X %08X %08X +1000=%08X %08X %08X %08X\\r\\n\",\n"
    "\t\tsite, off, s3_nz,\n"
    "\t\ts3_p[0], s3_p[1], s3_p[2], s3_p[3], s3_p[4], s3_p[5], s3_p[6], s3_p[7],\n"
    "\t\ts3_p[0x1000 / 4], s3_p[0x1000 / 4 + 1], s3_p[0x1000 / 4 + 2], s3_p[0x1000 / 4 + 3]);\n"
    "}\n"
    "\n"
    "/* 只读：带传输状态检查的 16 位寄存器读（厂商 i2c_reg16_read 不看状态，失败会返回未初始化栈值）。\n"
    " * 返回 0=成功，-1=失败；调用方按任务要求把读不到的值打印成 0xFF。*/\n"
    "static int s3_diag5_i2c_read16(u8 dev, u16 reg, u8 *val)\n"
    "{\n"
    "\tu8 s3_wr[2];\n"
    "\tu8 s3_rd = 0;\n"
    "\tint s3_st;\n"
    "\ts3_wr[0] = (u8)(reg >> 8);\n"
    "\ts3_wr[1] = (u8)(reg & 0xFF);\n"
    "\ts3_st = XIicPs_MasterSendPolled(&ps_i2c0, s3_wr, 2, dev);\n"
    "\twhile (XIicPs_BusIsBusy(&ps_i2c0)) { }\n"
    "\tif (s3_st != XST_SUCCESS) { return -1; }\n"
    "\ts3_st = XIicPs_MasterRecvPolled(&ps_i2c0, &s3_rd, 1, dev);\n"
    "\twhile (XIicPs_BusIsBusy(&ps_i2c0)) { }\n"
    "\tif (s3_st != XST_SUCCESS) { return -1; }\n"
    "\t*val = s3_rd;\n"
    "\treturn 0;\n"
    "}\n"
    "\n"
    "static u8 s3_diag5_sens(u16 reg)\n"
    "{\n"
    "\tu8 s3_v = 0xFF;\n"
    "\tif (s3_diag5_i2c_read16(0x3C, reg, &s3_v) != 0) { s3_v = 0xFF; }\n"
    "\treturn s3_v;\n"
    "}\n"
    "\n"
)

V5_MEMSET_OLD = "\tmemset(dispCtrl.framePtr[dispCtrl.curFrame], 0, 1920 * 1080 * 3);\n"
V5_MEMSET_NEW = (
    V5_MEMSET_OLD
    + "\t/* S3-DIAG5: memset 只写进 CPU cache（dirty 行）。不 flush 的话，S2MM 写进 DDR 的数据\n"
    "\t * 会被之后 cache 行回写覆盖，且 CPU 回读会命中脏零行 —— v4“帧缓冲全 0”的根因之一。*/\n"
    "\tXil_DCacheFlushRange((INTPTR)dispCtrl.framePtr[dispCtrl.curFrame], 1920 * 1080 * 3);\n"
)

V5_DIAG3_OLD = (
    "\t\txil_printf(\"S3_DIAG3_3035=0x%02X 3034=0x%02X 4300=0x%02X 501F=0x%02X\\r\\n\", d_3035, d_3034, d_4300, d_501f);\n"
    "\t}\n"
)
V5_DIAG3_NEW = (
    V5_DIAG3_OLD
    + "\t/* S3-DIAG5-SENS: 传感器关键寄存器只读回显（不做任何写）。\n"
    "\t * 用于区分“传感器停流/极性异常”与“PL 侧引脚/连线问题”：读不到的寄存器打印 0xFF。\n"
    "\t * 4202=streaming 控制(0x00=stream on) 3008=system control(bit6 软复位/bit1 standby)\n"
    "\t * 4740=DVP 极性(bit5 VSYNC/bit4 HREF/bit3 PCLK) 3035/3034=时钟分频 4300=输出格式\n"
    "\t * 501F=ISP 输入格式 3824=PCLK 手动分频 503D=test pattern 使能*/\n"
    "\t{\n"
    "\t\tu8 s3_4202 = s3_diag5_sens(0x4202);\n"
    "\t\tu8 s3_3008 = s3_diag5_sens(0x3008);\n"
    "\t\tu8 s3_4740 = s3_diag5_sens(0x4740);\n"
    "\t\tu8 s3_3035v = s3_diag5_sens(0x3035);\n"
    "\t\tu8 s3_3034v = s3_diag5_sens(0x3034);\n"
    "\t\tu8 s3_4300v = s3_diag5_sens(0x4300);\n"
    "\t\tu8 s3_501fv = s3_diag5_sens(0x501F);\n"
    "\t\tu8 s3_3824v = s3_diag5_sens(0x3824);\n"
    "\t\tu8 s3_503dv = s3_diag5_sens(0x503D);\n"
    "\t\txil_printf(\"S3_DIAG5_SENS=4202=0x%02X 3008=0x%02X 4740=0x%02X 3035=0x%02X 3034=0x%02X 4300=0x%02X 501F=0x%02X 3824=0x%02X 503D=0x%02X\\r\\n\",\n"
    "\t\t\ts3_4202, s3_3008, s3_4740, s3_3035v, s3_3034v, s3_4300v, s3_501fv, s3_3824v, s3_503dv);\n"
    "\t}\n"
)

V5_TAIL_RETURN = "\n\n\treturn 0;"
V5_RETURN_OLD = V5_TAIL_RETURN + "\n}"
V5_TAIL_IDLE_SUFFIX = "for (;;) { sleep(1); }\n}"
V5_RETURN_NEW = (
    "\n\n\t/* S3-DIAG5: main 不再返回（原 return 0 已删除）—— 保持显示中断/S2MM 持续运行，\n"
    "\t * 避免退出路径影响观测。*/\n"
    "\tfor (;;) { sleep(1); }\n"
    "}"
)

# ---------------------------------------------------------------------------
# v6 变体追加内容（只在 VARIANT == "v6" 时生效；v4/v5 输出保持不变）
# 设计：保留 v5 的辅助函数与一次性打印，把 v5 的三次 16 KB 采样换成五次 64 KB 指纹采样。
# ---------------------------------------------------------------------------
V6_INCLUDE_OLD = "#include \"sleep.h\"\n"
V6_INCLUDE_NEW = (
    "#include \"sleep.h\"\n"
    "#include \"xtime_l.h\" /* S3-DIAG6: XTime_GetTime/COUNTS_PER_SECOND 用于打印真实耗时秒 */\n"
)

V6_HELPERS = (
    "/* ================= S3-DIAG6 帧缓冲 64 KB 区指纹（只读） =================\n"
    " * 算法（五次采样完全相同）：32 位循环进位加和 sum；哈希 = 反射式 CRC-32，\n"
    " *   多项式 0xEDB88320、初值 0xFFFFFFFF、末取反，按小端 32 位字依次喂入\n"
    " *   （等价于对连续 64 KB 字节流做标准 CRC-32/IEEE）。\n"
    " * 读前必须 Xil_DCacheInvalidateRange，否则可能读到 CPU cache 里的陈旧行。\n"
    " * 编译期开关 S3_TESTPATTERN：默认 0；=1 时启动 S2MM 前写 OV5640 0x503D=0x80（彩条测试图）。*/\n"
    "#ifndef S3_TESTPATTERN\n"
    "#define S3_TESTPATTERN 0\n"
    "#endif\n"
    "#define S3_DIAG6_FP_BYTES (64 * 1024)\n"
    "static XTime s3_t6_start, s3_t6_now;\n"
    "\n"
    "static u32 s3_diag6_hash(const volatile u32 *p, u32 words, u32 *sum_out, u32 *nz_out)\n"
    "{\n"
    "\tu32 s3_i, s3_b, s3_nz = 0, s3_sum = 0, s3_crc = 0xFFFFFFFFU;\n"
    "\tfor (s3_i = 0; s3_i < words; s3_i++) {\n"
    "\t\tu32 s3_w = p[s3_i];\n"
    "\t\ts3_sum += s3_w;\n"
    "\t\tif (s3_w != 0U) { s3_nz++; }\n"
    "\t\ts3_crc ^= s3_w;\n"
    "\t\tfor (s3_b = 0; s3_b < 32; s3_b++) {\n"
    "\t\t\tif (s3_crc & 1U) { s3_crc = (s3_crc >> 1) ^ 0xEDB88320U; } else { s3_crc >>= 1; }\n"
    "\t\t}\n"
    "\t}\n"
    "\t*sum_out = s3_sum;\n"
    "\t*nz_out = s3_nz;\n"
    "\treturn ~s3_crc;\n"
    "}\n"
    "\n"
    "static void s3_diag6_fp(u32 tsec, u32 site, u32 off)\n"
    "{\n"
    "\tvolatile u32 *s3_p = (volatile u32 *)((u8 *)dispCtrl.framePtr[dispCtrl.curFrame] + off);\n"
    "\tu32 s3_sum = 0, s3_nz = 0, s3_hash;\n"
    "\tXil_DCacheInvalidateRange((INTPTR)s3_p, S3_DIAG6_FP_BYTES);\n"
    "\ts3_hash = s3_diag6_hash(s3_p, S3_DIAG6_FP_BYTES / 4, &s3_sum, &s3_nz);\n"
    "\txil_printf(\"S3_DIAG6_FP t=%u site=%u sum=0x%08X hash=0x%08X nz=%u\\r\\n\", tsec, site, s3_sum, s3_hash, s3_nz);\n"
    "}\n"
    "\n"
    "/* 只读：每次采样同时打印 S2MM SR/CR 与逐位判读（位定义见 S3-DIAG5 注释）。*/\n"
    "static void s3_diag6_sr(u32 tsec)\n"
    "{\n"
    "\tu32 s3_sr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_SR_OFFSET);\n"
    "\tu32 s3_cr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET);\n"
    "\txil_printf(\"S3_DIAG6_SR t=%u S2MM_SR=0x%08X S2MM_CR=0x%08X FRMCNT=%u HALTED=%u IDLE=%u INT=%u SLV=%u DEC=%u FSZ_LESS=%u LSZ_LESS=%u FSZ_MORE=%u LSZ_MORE=%u ERR_IRQ=%u\\r\\n\",\n"
    "\t\ttsec, s3_sr, s3_cr, (s3_sr >> XAXIVDMA_FRMCNT_SHIFT) & 0xFFU, s3_sr & 0x1U, (s3_sr >> 1) & 0x1U,\n"
    "\t\t(s3_sr >> 4) & 0x1U, (s3_sr >> 5) & 0x1U, (s3_sr >> 6) & 0x1U, (s3_sr >> 7) & 0x1U,\n"
    "\t\t(s3_sr >> 8) & 0x1U, (s3_sr >> 11) & 0x1U, (s3_sr >> 15) & 0x1U, (s3_sr >> 14) & 0x1U);\n"
    "}\n"
    "\n"
)

V6_WRITE_INIT_NEW = (
    "\t/* S3-DIAG6: 编译期开关 S3_TESTPATTERN（默认 0）。=1 时在启动 S2MM 之前写 OV5640 0x503D=0x80\n"
    "\t * 打开彩条测试图（用于颜色判读）；=0 时只打印 OFF，便于区分手里是哪个 ELF。*/\n"
    "#if S3_TESTPATTERN\n"
    "\t{\n"
    "\t\tint s3_tp_st = i2c_reg16_write(&ps_i2c0, 0x3c, 0x503D, 0x80);\n"
    "\t\txil_printf(\"S3_DIAG6_TESTPATTERN=ON write_status=%d\\r\\n\", s3_tp_st);\n"
    "\t}\n"
    "#else\n"
    "\txil_printf(\"S3_DIAG6_TESTPATTERN=OFF\\r\\n\");\n"
    "#endif\n"
    "\t/* S3-DIAG4: 采集 IP 内部有 200M+100M 个 PCLK 周期的上电等待（见 alinx_ov5640.v 的\n"
    "\t * reset_cnt / fifo_ready_cnt），若不等它就绪就启动 S2MM，会在第一帧落下帧尺寸粘滞错误。*/\n"
    "\txil_printf(\"S3_DIAG4_WAIT_START\\r\\n\");\n"
    "\t{\n"
    "\t\tint s3_w;\n"
    "\t\tfor (s3_w = 0; s3_w < 15; s3_w++) { sleep(1); }\n"
    "\t}\n"
    "\txil_printf(\"S3_DIAG4_WAIT_DONE\\r\\n\");\n"
    "\tvdma_write_init(XPAR_AXIVDMA_1_DEVICE_ID,1280 * 3,720,1280 * 3,(unsigned int)dispCtrl.framePtr[dispCtrl.curFrame]);\n"
    "\txil_printf(\"S3_DIAG_VDMA_WRITE_STARTED\\r\\n\");\n"
    "\t/* S3-DIAG6: 启动后 t≈5/10/15/20/25 秒各做一次 64 KB×3 区指纹（先失效 cache 再读物理内存），\n"
    "\t * 同一批内存每次都用同一算法与同一范围，用于判断是否为活视频（取代 v5 的三次 16 KB 采样）。*/\n"
    "\txil_printf(\"S3_DIAG6_ALGO=sum32+crc32(0xEDB88320) bytes=65536 sites=0x000000,0x080000,0x100000\\r\\n\");\n"
    "\ts3_diag5_regs(0);\n"
    "\tXTime_GetTime(&s3_t6_start);\n"
    "\t{\n"
    "\t\tint s3_k, s3_s;\n"
    "\t\tfor (s3_k = 0; s3_k < 5; s3_k++) {\n"
    "\t\t\tu32 s3_tsec;\n"
    "\t\t\tfor (s3_s = 0; s3_s < 5; s3_s++) { sleep(1); }\n"
    "\t\t\tXTime_GetTime(&s3_t6_now);\n"
    "\t\t\ts3_tsec = (u32)((s3_t6_now - s3_t6_start) / COUNTS_PER_SECOND);\n"
    "\t\t\txil_printf(\"S3_DIAG6_SAMPLE=%d\\r\\n\", s3_k + 1);\n"
    "\t\t\ts3_diag6_sr(s3_tsec);\n"
    "\t\t\ts3_diag6_fp(s3_tsec, 0, 0x000000U);\n"
    "\t\t\ts3_diag6_fp(s3_tsec, 1, 0x080000U);\n"
    "\t\t\ts3_diag6_fp(s3_tsec, 2, 0x100000U);\n"
    "\t\t}\n"
    "\t\t/* t≈30 s：再等 5 秒后回读传感器，判断传感器是否仍在流 */\n"
    "\t\tfor (s3_s = 0; s3_s < 5; s3_s++) { sleep(1); }\n"
    "\t}\n"
    "\tXTime_GetTime(&s3_t6_now);\n"
    "\t{\n"
    "\t\tu32 s3_tsec = (u32)((s3_t6_now - s3_t6_start) / COUNTS_PER_SECOND);\n"
    "\t\tu8 s3_s6_4202 = s3_diag5_sens(0x4202);\n"
    "\t\tu8 s3_s6_3008 = s3_diag5_sens(0x3008);\n"
    "\t\tu8 s3_s6_503d = s3_diag5_sens(0x503D);\n"
    "\t\tu8 s3_s6_3035 = s3_diag5_sens(0x3035);\n"
    "\t\txil_printf(\"S3_DIAG6_SENS=4202=0x%02X 3008=0x%02X 503D=0x%02X 3035=0x%02X t=%u\\r\\n\",\n"
    "\t\t\ts3_s6_4202, s3_s6_3008, s3_s6_503d, s3_s6_3035, s3_tsec);\n"
    "\t}\n"
    "\txil_printf(\"S3_DIAG6_SAMPLING_DONE\\r\\n\");\n"
)

# ---------------------------------------------------------------------------
# v7 变体追加内容（只在 VARIANT == "v7" 时生效；v4/v5/v6 输出保持不变）
# v7 = v6 + ISP/AWB/AEC 只读回读 + 编译期开关 S3_AWB_OFF（启动 S2MM 前关 AWB）
# ---------------------------------------------------------------------------
V7_HELPERS = (
    "/* ================= S3-DIAG7 编译期开关 =================\n"
    " * S3_AWB_OFF：默认 0（AWB 不动，只回读）。=1 时在启动 S2MM 之前把 OV5640 0x5001 的 bit0 清 0\n"
    " * （厂商 init 表 0x5001=0xa3，bit0=1 表示 AWB 使能），用来判定“蓝色分量被压到约 42%”是否由 ISP/AWB 造成。*/\n"
    "#ifndef S3_AWB_OFF\n"
    "#define S3_AWB_OFF 0\n"
    "#endif\n"
    "\n"
)

V7_AWB_READBACK = (
    "\t/* S3-DIAG7: ISP/AWB/AEC 只读回读（不做任何写）。读不到的寄存器打印 0xFF。\n"
    "\t * 5001=ISP 使能(bit0=AWB) 3406=AWB 手动增益使能 3400..3405=AWB 增益(R,G,B 各 16 位，高/低字节)\n"
    "\t * 3503=AEC/AGC 手动控制 3500..3502=AEC 曝光(4+8+8 位) 5580..558B=ISP 控制/特效 3035=PLL 分频*/\n"
    "\t{\n"
    "\t\tu8 s3_5001 = s3_diag5_sens(0x5001);\n"
    "\t\tu8 s3_3406 = s3_diag5_sens(0x3406);\n"
    "\t\tu8 s3_3400 = s3_diag5_sens(0x3400);\n"
    "\t\tu8 s3_3401 = s3_diag5_sens(0x3401);\n"
    "\t\tu8 s3_3402 = s3_diag5_sens(0x3402);\n"
    "\t\tu8 s3_3403 = s3_diag5_sens(0x3403);\n"
    "\t\tu8 s3_3404 = s3_diag5_sens(0x3404);\n"
    "\t\tu8 s3_3405 = s3_diag5_sens(0x3405);\n"
    "\t\tu8 s3_503d = s3_diag5_sens(0x503D);\n"
    "\t\tu8 s3_4300 = s3_diag5_sens(0x4300);\n"
    "\t\tu8 s3_501f = s3_diag5_sens(0x501F);\n"
    "\t\tu8 s3_3503 = s3_diag5_sens(0x3503);\n"
    "\t\tu8 s3_3500 = s3_diag5_sens(0x3500);\n"
    "\t\tu8 s3_3501 = s3_diag5_sens(0x3501);\n"
    "\t\tu8 s3_3502 = s3_diag5_sens(0x3502);\n"
    "\t\tu8 s3_3035 = s3_diag5_sens(0x3035);\n"
    "\t\tu8 s3_5580 = s3_diag5_sens(0x5580);\n"
    "\t\tu8 s3_5581 = s3_diag5_sens(0x5581);\n"
    "\t\tu8 s3_5582 = s3_diag5_sens(0x5582);\n"
    "\t\tu8 s3_5583 = s3_diag5_sens(0x5583);\n"
    "\t\tu8 s3_5584 = s3_diag5_sens(0x5584);\n"
    "\t\tu8 s3_5585 = s3_diag5_sens(0x5585);\n"
    "\t\tu8 s3_5586 = s3_diag5_sens(0x5586);\n"
    "\t\tu8 s3_5587 = s3_diag5_sens(0x5587);\n"
    "\t\tu8 s3_5588 = s3_diag5_sens(0x5588);\n"
    "\t\tu8 s3_5589 = s3_diag5_sens(0x5589);\n"
    "\t\tu8 s3_558a = s3_diag5_sens(0x558A);\n"
    "\t\tu8 s3_558b = s3_diag5_sens(0x558B);\n"
    "\t\txil_printf(\"S3_DIAG7_AWB=5001=0x%02X 3406=0x%02X 3400..3405=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X 503D=0x%02X 4300=0x%02X 501F=0x%02X\\r\\n\",\n"
    "\t\t\ts3_5001, s3_3406, s3_3400, s3_3401, s3_3402, s3_3403, s3_3404, s3_3405, s3_503d, s3_4300, s3_501f);\n"
    "\t\txil_printf(\"S3_DIAG7_AE=3503=0x%02X 3500..3502=0x%02X,0x%02X,0x%02X 3035=0x%02X\\r\\n\",\n"
    "\t\t\ts3_3503, s3_3500, s3_3501, s3_3502, s3_3035);\n"
    "\t\txil_printf(\"S3_DIAG7_ISP_A=5580..5585=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X\\r\\n\",\n"
    "\t\t\ts3_5580, s3_5581, s3_5582, s3_5583, s3_5584, s3_5585);\n"
    "\t\txil_printf(\"S3_DIAG7_ISP_B=5586..558B=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X\\r\\n\",\n"
    "\t\t\ts3_5586, s3_5587, s3_5588, s3_5589, s3_558a, s3_558b);\n"
    "\t}\n"
)

V7_AWB_SWITCH = (
    "\t/* S3-DIAG7: 编译期开关 S3_AWB_OFF（默认 0）。=1 时在启动 S2MM 之前关闭 AWB：\n"
    "\t * 0x5001 = (读回值 & ~0x01)。若读回失败（0xFF）则跳过写入并打印 write_status=-2，\n"
    "\t * 避免用不可信的值改写 ISP 使能寄存器；写入后再回读一次确认。*/\n"
    "#if S3_AWB_OFF\n"
    "\t{\n"
    "\t\tu8 s3_awb_before = s3_diag5_sens(0x5001);\n"
    "\t\tu8 s3_awb_after = (u8)(s3_awb_before & (u8)~0x01U);\n"
    "\t\tint s3_awb_wr = -2;\n"
    "\t\tu8 s3_awb_rd = 0xFF;\n"
    "\t\tif (s3_awb_before != 0xFF) {\n"
    "\t\t\ts3_awb_wr = i2c_reg16_write(&ps_i2c0, 0x3c, 0x5001, (char)s3_awb_after);\n"
    "\t\t\ts3_awb_rd = s3_diag5_sens(0x5001);\n"
    "\t\t} else {\n"
    "\t\t\ts3_awb_after = 0xFF;\n"
    "\t\t\txil_printf(\"S3_DIAG7_AWB_OFF_SKIPPED reason=0x5001_read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG7_AWB_OFF=ON before=0x%02X after=0x%02X write_status=%d\\r\\n\",\n"
    "\t\t\ts3_awb_before, s3_awb_after, s3_awb_wr);\n"
    "\t\txil_printf(\"S3_DIAG7_AWB_OFF_VERIFY readback=0x%02X\\r\\n\", s3_awb_rd);\n"
    "\t}\n"
    "#else\n"
    "\txil_printf(\"S3_DIAG7_AWB_OFF=OFF (0x5001 unchanged)\\r\\n\");\n"
    "#endif\n"
)

_V7_WRITE_INIT_ANCHOR = "\t/* S3-DIAG4: 采集 IP 内部"
if V6_WRITE_INIT_NEW.count(_V7_WRITE_INIT_ANCHOR) != 1:
    print("V7_WRITE_INIT_ANCHOR_NOT_UNIQUE")
    sys.exit(2)
V7_WRITE_INIT_NEW = V6_WRITE_INIT_NEW.replace(_V7_WRITE_INIT_ANCHOR, V7_AWB_SWITCH + _V7_WRITE_INIT_ANCHOR)

# ---------------------------------------------------------------------------
# v8 变体追加内容（只在 VARIANT == "v8" 时生效；v4/v5/v6/v7 输出保持不变）
# v8 = v7 + 编译期手动白平衡（S3_WB_MANUAL + S3_WB_R/G/B，写入后回读校验）
# ---------------------------------------------------------------------------
V8_HELPERS = (
    "/* ================= S3-DIAG8 手动白平衡开关 =================\n"
    " * S3_WB_MANUAL（默认 0）：=1 时在启动 S2MM 之前使能 AWB 手动增益（0x3406=0x01），\n"
    " *   并按 R/G/B 写 0x3400/0x3401、0x3402/0x3403、0x3404/0x3405，然后**回读校验**。\n"
    " * 位域假设（本任务未与 OV5640 手册核对，依据是 v7 上板实测的自动增益读法）：\n"
    " *   增益 = (0x3400<<8)|0x3401，即高字节 = 增益[10:8]（放进 8 位寄存器的低 3 位有效位），\n"
    " *   低字节 = 增益[7:0]；1024 = 0x0400 = 1.0×。v7 实测 R=(0x04<<8)|0x3D=1085、\n"
    " *   G=(0x04<<8)|0x00=1024、B=(0x07<<8)|0xE5=2021 —— 与该读法自洽。\n"
    " * 注意：本轮 B 档位 2048/2560/3072/3584 已超出 11 位（>2047），高字节因此带上 bit11+；\n"
    " *   若回读与写入不一致（例如被截成 0x0600），说明该字段比 12 位更窄，\n"
    " *   实际生效值一律以 UART 的 readback 为准（S3_DIAG8_WB_RB 行给出 match 标志）。*/\n"
    "#ifndef S3_WB_MANUAL\n"
    "#define S3_WB_MANUAL 0\n"
    "#endif\n"
    "#ifndef S3_WB_R\n"
    "#define S3_WB_R 1024\n"
    "#endif\n"
    "#ifndef S3_WB_G\n"
    "#define S3_WB_G 1024\n"
    "#endif\n"
    "#ifndef S3_WB_B\n"
    "#define S3_WB_B 1024\n"
    "#endif\n"
    "\n"
)

V8_WB_BLOCK = (
    "\t/* S3-DIAG8: 手动白平衡（编译期开关 S3_WB_MANUAL）。=1 时在启动 S2MM 之前：\n"
    "\t * 0x3406=0x01 使能 AWB 手动增益，再按位域假设写 R/G/B 增益高位/低位，并立即回读校验。*/\n"
    "#if S3_WB_MANUAL\n"
    "\t{\n"
    "\t\tu16 s3_wb_r = (u16)S3_WB_R;\n"
    "\t\tu16 s3_wb_g = (u16)S3_WB_G;\n"
    "\t\tu16 s3_wb_b = (u16)S3_WB_B;\n"
    "\t\tu8 s3_wb_3406a = 0;\n"
    "\t\tu8 s3_wb_3406b = 0;\n"
    "\t\tu8 s3_wb_rb0 = 0, s3_wb_rb1 = 0, s3_wb_rb2 = 0, s3_wb_rb3 = 0, s3_wb_rb4 = 0, s3_wb_rb5 = 0;\n"
    "\t\tu32 s3_wb_rd_r, s3_wb_rd_g, s3_wb_rd_b;\n"
    "\t\tint s3_wb_wr;\n"
    "\t\ts3_wb_3406a = s3_diag5_sens(0x3406);\n"
    "\t\ts3_wb_wr = i2c_reg16_write(&ps_i2c0, 0x3c, 0x3406, 0x01);\n"
    "\t\ts3_wb_3406b = s3_diag5_sens(0x3406);\n"
    "\t\ts3_wb_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x3400, (char)((s3_wb_r >> 8) & 0xFF));\n"
    "\t\ts3_wb_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x3401, (char)(s3_wb_r & 0xFF));\n"
    "\t\ts3_wb_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x3402, (char)((s3_wb_g >> 8) & 0xFF));\n"
    "\t\ts3_wb_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x3403, (char)(s3_wb_g & 0xFF));\n"
    "\t\ts3_wb_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x3404, (char)((s3_wb_b >> 8) & 0xFF));\n"
    "\t\ts3_wb_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x3405, (char)(s3_wb_b & 0xFF));\n"
    "\t\ts3_wb_rb0 = s3_diag5_sens(0x3400);\n"
    "\t\ts3_wb_rb1 = s3_diag5_sens(0x3401);\n"
    "\t\ts3_wb_rb2 = s3_diag5_sens(0x3402);\n"
    "\t\ts3_wb_rb3 = s3_diag5_sens(0x3403);\n"
    "\t\ts3_wb_rb4 = s3_diag5_sens(0x3404);\n"
    "\t\ts3_wb_rb5 = s3_diag5_sens(0x3405);\n"
    "\t\ts3_wb_rd_r = ((u32)s3_wb_rb0 << 8) | (u32)s3_wb_rb1;\n"
    "\t\ts3_wb_rd_g = ((u32)s3_wb_rb2 << 8) | (u32)s3_wb_rb3;\n"
    "\t\ts3_wb_rd_b = ((u32)s3_wb_rb4 << 8) | (u32)s3_wb_rb5;\n"
    "\t\txil_printf(\"S3_DIAG8_WB=MANUAL R=0x%04X G=0x%04X B=0x%04X before3406=0x%02X after3406=0x%02X readback3400..3405=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X\\r\\n\",\n"
    "\t\t\ts3_wb_r, s3_wb_g, s3_wb_b, s3_wb_3406a, s3_wb_3406b,\n"
    "\t\t\ts3_wb_rb0, s3_wb_rb1, s3_wb_rb2, s3_wb_rb3, s3_wb_rb4, s3_wb_rb5);\n"
    "\t\txil_printf(\"S3_DIAG8_WB_RB rb_r16=0x%04X rb_g16=0x%04X rb_b16=0x%04X match=%u,%u,%u write_status=%d\\r\\n\",\n"
    "\t\t\ts3_wb_rd_r, s3_wb_rd_g, s3_wb_rd_b,\n"
    "\t\t\t(s3_wb_rd_r == (u32)s3_wb_r) ? 1U : 0U, (s3_wb_rd_g == (u32)s3_wb_g) ? 1U : 0U,\n"
    "\t\t\t(s3_wb_rd_b == (u32)s3_wb_b) ? 1U : 0U, s3_wb_wr);\n"
    "\t}\n"
    "#else\n"
    "\txil_printf(\"S3_DIAG8_WB=OFF (auto AWB unchanged)\\r\\n\");\n"
    "#endif\n"
)

if V7_WRITE_INIT_NEW.count(_V7_WRITE_INIT_ANCHOR) != 1:
    print("V8_WRITE_INIT_ANCHOR_NOT_UNIQUE")
    sys.exit(2)
# 插在 v7 的 AWB 开关块之后、15 s 等待之前 → 顺序：测试图 → AWB 关 → 手动增益 → 等待 → 启动 S2MM
V8_WRITE_INIT_NEW = V7_WRITE_INIT_NEW.replace(_V7_WRITE_INIT_ANCHOR, V8_WB_BLOCK + _V7_WRITE_INIT_ANCHOR)

# ---------------------------------------------------------------------------
# v9 变体追加内容（只在 VARIANT == "v9" 时生效；v4~v8 输出保持不变）
# v9 = v8 + DVP 端口/数据线 output select 回读 + 两个默认 0 的可选写测试开关
# ---------------------------------------------------------------------------
V9_HELPERS = (
    "/* ================= S3-DIAG9 DVP 端口控制写测试开关 =================\n"
    " * 背景：19 行样本 24,320 像素实测蓝 bit7 与绿 bit4 置位率均为 0.000% ⇒ DVP 两个字节的 MSB 同时恒 0，\n"
    " *   指向单线 cmos_d[9] 无信号；OV5640 的 0x301D/0x301E 是 D[9:0] 的 output select\n"
    " *   （0=正常数据通路，1=寄存器固定值，按任务卡口径），若 D9 位为 1 则症状完全一致且软件可修。\n"
    " * S3_PAD_SEL_CLEAR（默认 0）：=1 时清 0x301D bit3（D9 select），并视回读结果清 0x301E bit1（D6 select）；\n"
    " *   写前先回读、写后回读校验，全程打印 before/after/readback。\n"
    " * S3_DVP_ORDER_DEBUG（默认 0）：=1 时置 0x4745[2:1]=10，**不自动恢复**（UART 明示 NOT_RESTORED），\n"
    " *   恢复办法：刷回最小改动 ELF 或复位传感器。\n"
    " * 两个开关可同时为 1；任一关键读失败时跳过对应写入（不用不可信的值改写端口控制寄存器）。*/\n"
    "#ifndef S3_PAD_SEL_CLEAR\n"
    "#define S3_PAD_SEL_CLEAR 0\n"
    "#endif\n"
    "#ifndef S3_DVP_ORDER_DEBUG\n"
    "#define S3_DVP_ORDER_DEBUG 0\n"
    "#endif\n"
    "\n"
)

V9_PAD_READBACK = (
    "\t/* S3-DIAG9: DVP 端口/数据线 output select 只读回读（不做任何写）。\n"
    "\t * 关键位：0x301D bit3 = D9 output select、0x301E bit1 = D6 output select（1=该线输出寄存器固定值）。\n"
    "\t * 注意：D9SEL/D6SEL 在读失败时打印 255（=未知），不会被误读成“置位 1”。*/\n"
    "\t{\n"
    "\t\tu8 s3_9_3017 = s3_diag5_sens(0x3017);\n"
    "\t\tu8 s3_9_3018 = s3_diag5_sens(0x3018);\n"
    "\t\tu8 s3_9_301d = 0;\n"
    "\t\tu8 s3_9_301e = 0;\n"
    "\t\tu8 s3_9_300a = s3_diag5_sens(0x300A);\n"
    "\t\tu8 s3_9_300b = s3_diag5_sens(0x300B);\n"
    "\t\tu8 s3_9_4741 = s3_diag5_sens(0x4741);\n"
    "\t\tu8 s3_9_4745 = s3_diag5_sens(0x4745);\n"
    "\t\tu8 s3_9_4300 = s3_diag5_sens(0x4300);\n"
    "\t\tu8 s3_9_501f = s3_diag5_sens(0x501F);\n"
    "\t\tu32 s3_9_d9 = 255U, s3_9_d6 = 255U;\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x301D, &s3_9_301d) != 0) {\n"
    "\t\t\ts3_9_301d = 0xFF;\n"
    "\t\t} else {\n"
    "\t\t\ts3_9_d9 = ((u32)s3_9_301d >> 3) & 1U;\n"
    "\t\t}\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x301E, &s3_9_301e) != 0) {\n"
    "\t\t\ts3_9_301e = 0xFF;\n"
    "\t\t} else {\n"
    "\t\t\ts3_9_d6 = ((u32)s3_9_301e >> 1) & 1U;\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG9_PAD=3017=0x%02X 3018=0x%02X 301D=0x%02X 301E=0x%02X 300A=0x%02X 300B=0x%02X 4741=0x%02X 4745=0x%02X 4300=0x%02X 501F=0x%02X S3_DIAG9_D9SEL=%u D6SEL=%u\\r\\n\",\n"
    "\t\t\ts3_9_3017, s3_9_3018, s3_9_301d, s3_9_301e, s3_9_300a, s3_9_300b,\n"
    "\t\t\ts3_9_4741, s3_9_4745, s3_9_4300, s3_9_501f, s3_9_d9, s3_9_d6);\n"
    "\t}\n"
)

V9_WRITE_BLOCK = (
    "\t/* S3-DIAG9: 两个可选写测试（编译期开关，默认 0）。\n"
    "\t * 原则：先回读原值 → 写 → 回读校验；关键读失败的寄存器跳过写入（write_status=-2），\n"
    "\t * 避免用不可信的值改写端口控制寄存器。*/\n"
    "#if S3_PAD_SEL_CLEAR\n"
    "\t{\n"
    "\t\tu8 s3_9d_before = 0, s3_9d_after = 0, s3_9d_rb = 0xFF;\n"
    "\t\tu8 s3_9e_before = 0, s3_9e_after = 0, s3_9e_rb = 0xFF;\n"
    "\t\tint s3_9d_ok, s3_9e_ok, s3_9_skip = 0, s3_9_wr = 0;\n"
    "\t\ts3_9d_ok = (s3_diag5_i2c_read16(0x3C, 0x301D, &s3_9d_before) == 0);\n"
    "\t\ts3_9e_ok = (s3_diag5_i2c_read16(0x3C, 0x301E, &s3_9e_before) == 0);\n"
    "\t\tif (s3_9d_ok) {\n"
    "\t\t\ts3_9d_after = (u8)(s3_9d_before & (u8)~0x08U);\n"
    "\t\t\ts3_9_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x301D, (char)s3_9d_after);\n"
    "\t\t\tif (s3_diag5_i2c_read16(0x3C, 0x301D, &s3_9d_rb) != 0) { s3_9d_rb = 0xFF; }\n"
    "\t\t} else {\n"
    "\t\t\ts3_9d_before = 0xFF; s3_9d_after = 0xFF; s3_9d_rb = 0xFF; s3_9_skip = 1;\n"
    "\t\t\txil_printf(\"S3_DIAG9_FIX_SKIPPED reg=301D reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\tif (s3_9e_ok) {\n"
    "\t\t\tif ((s3_9e_before & 0x02U) != 0U) {\n"
    "\t\t\t\ts3_9e_after = (u8)(s3_9e_before & (u8)~0x02U);\n"
    "\t\t\t\ts3_9_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x301E, (char)s3_9e_after);\n"
    "\t\t\t\tif (s3_diag5_i2c_read16(0x3C, 0x301E, &s3_9e_rb) != 0) { s3_9e_rb = 0xFF; }\n"
    "\t\t\t} else {\n"
    "\t\t\t\ts3_9e_after = s3_9e_before; s3_9e_rb = s3_9e_before;\n"
    "\t\t\t\txil_printf(\"S3_DIAG9_FIX_SKIP_301E=1 reason=bit1_already_0_no_write\\r\\n\");\n"
    "\t\t\t}\n"
    "\t\t} else {\n"
    "\t\t\ts3_9e_before = 0xFF; s3_9e_after = 0xFF; s3_9e_rb = 0xFF; s3_9_skip = 1;\n"
    "\t\t\txil_printf(\"S3_DIAG9_FIX_SKIPPED reg=301E reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG9_FIX=301D before=0x%02X after=0x%02X readback=0x%02X 301E before=0x%02X after=0x%02X readback=0x%02X write_status=%d\\r\\n\",\n"
    "\t\t\ts3_9d_before, s3_9d_after, s3_9d_rb, s3_9e_before, s3_9e_after, s3_9e_rb,\n"
    "\t\t\ts3_9_skip ? -2 : s3_9_wr);\n"
    "\t}\n"
    "#endif\n"
    "#if S3_DVP_ORDER_DEBUG\n"
    "\t{\n"
    "\t\tu8 s3_9o_before = 0, s3_9o_after = 0, s3_9o_rb = 0xFF;\n"
    "\t\tint s3_9o_wr = 0;\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x4745, &s3_9o_before) == 0) {\n"
    "\t\t\ts3_9o_after = (u8)((s3_9o_before & (u8)~0x06U) | 0x04U);\n"
    "\t\t\ts3_9o_wr = i2c_reg16_write(&ps_i2c0, 0x3c, 0x4745, (char)s3_9o_after);\n"
    "\t\t\tif (s3_diag5_i2c_read16(0x3C, 0x4745, &s3_9o_rb) != 0) { s3_9o_rb = 0xFF; }\n"
    "\t\t} else {\n"
    "\t\t\ts3_9o_before = 0xFF; s3_9o_after = 0xFF; s3_9o_rb = 0xFF; s3_9o_wr = -2;\n"
    "\t\t\txil_printf(\"S3_DIAG9_ORDER_SKIPPED reason=0x4745_read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG9_ORDER_WR=4745 before=0x%02X after=0x%02X readback=0x%02X write_status=%d\\r\\n\",\n"
    "\t\t\ts3_9o_before, s3_9o_after, s3_9o_rb, s3_9o_wr);\n"
    "\t\txil_printf(\"S3_DIAG9_ORDER=NOT_RESTORED no_auto_restore=1 (restore: reload minimal-change ELF or reset sensor)\\r\\n\");\n"
    "\t}\n"
    "#else\n"
    "\txil_printf(\"S3_DIAG9_ORDER=OFF (0x4745 unchanged)\\r\\n\");\n"
    "#endif\n"
)

if V8_WRITE_INIT_NEW.count(_V7_WRITE_INIT_ANCHOR) != 1:
    print("V9_WRITE_INIT_ANCHOR_NOT_UNIQUE")
    sys.exit(2)
# 插在 v8 的手动白平衡块之后、15 s 等待之前
# → 顺序：测试图 → AWB 关 → 手动增益 → 端口 select 写测试 → 输出顺序写测试 → 等待 → 启动 S2MM
V9_WRITE_INIT_NEW = V8_WRITE_INIT_NEW.replace(_V7_WRITE_INIT_ANCHOR, V9_WRITE_BLOCK + _V7_WRITE_INIT_ANCHOR)

# ---------------------------------------------------------------------------
# v10 变体追加内容（只在 VARIANT == "v10" 时生效；v4~v9 输出保持不变）
# v10 = v9 + 传感器端去色（黑白）尝试：编译期 S3_GRAY_TRY=0/1/2/3
# ---------------------------------------------------------------------------
V10_HELPERS = (
    "/* ================= S3-DIAG10 传感器端去色（黑白）尝试 =================\n"
    " * S3_GRAY_TRY（默认 0）：0=只回读不写；1=0x5583=0x5584=0x00（U/V 饱和度置 0，0x5580 不动）；\n"
    " *   2=0x5580 效果位 (rb & ~0xC0) | 0x40；3=(rb & ~0xC0) | 0x80。\n"
    " * 用途：手势识别不需要颜色，黑白可直接消除“偏黄”观感（缺的两位只表现为轻微明暗误差）。\n"
    " * 原则同 v7~v9：写前回读、写后回读校验；关键读失败跳过写入（write_status=-2）。*/\n"
    "#ifndef S3_GRAY_TRY\n"
    "#define S3_GRAY_TRY 0\n"
    "#endif\n"
    "\n"
)

V10_GRAY_BLOCK = (
    "\t/* S3-DIAG10: 传感器端去色（黑白）尝试（编译期 S3_GRAY_TRY=0/1/2/3，见 S3-DIAG10 注释）。\n"
    "\t * 统一打印 5580/5583/5584 的 before/after/readback；读失败跳过写入。*/\n"
    "\t{\n"
    "\t\tu8 s3_10_5580 = 0, s3_10_5583 = 0, s3_10_5584 = 0;\n"
    "\t\tu8 s3_10_5580_a, s3_10_5583_a, s3_10_5584_a;\n"
    "\t\tu8 s3_10_5580_rb = 0xFF, s3_10_5583_rb = 0xFF, s3_10_5584_rb = 0xFF;\n"
    "\t\tint s3_10_ok80, s3_10_ok83, s3_10_ok84, s3_10_wr = 0, s3_10_skip = 0;\n"
    "\t\ts3_10_ok80 = (s3_diag5_i2c_read16(0x3C, 0x5580, &s3_10_5580) == 0);\n"
    "\t\ts3_10_ok83 = (s3_diag5_i2c_read16(0x3C, 0x5583, &s3_10_5583) == 0);\n"
    "\t\ts3_10_ok84 = (s3_diag5_i2c_read16(0x3C, 0x5584, &s3_10_5584) == 0);\n"
    "\t\tif (!s3_10_ok80) { s3_10_5580 = 0xFF; }\n"
    "\t\tif (!s3_10_ok83) { s3_10_5583 = 0xFF; }\n"
    "\t\tif (!s3_10_ok84) { s3_10_5584 = 0xFF; }\n"
    "\t\ts3_10_5580_a = s3_10_5580;\n"
    "\t\ts3_10_5583_a = s3_10_5583;\n"
    "\t\ts3_10_5584_a = s3_10_5584;\n"
    "#if S3_GRAY_TRY == 1\n"
    "\t\tif (s3_10_ok83) {\n"
    "\t\t\ts3_10_5583_a = 0x00;\n"
    "\t\t\ts3_10_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x5583, 0x00);\n"
    "\t\t} else {\n"
    "\t\t\ts3_10_5583_a = 0xFF; s3_10_skip = 1;\n"
    "\t\t\txil_printf(\"S3_DIAG10_GRAY_SKIPPED reg=5583 reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\tif (s3_10_ok84) {\n"
    "\t\t\ts3_10_5584_a = 0x00;\n"
    "\t\t\ts3_10_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x5584, 0x00);\n"
    "\t\t} else {\n"
    "\t\t\ts3_10_5584_a = 0xFF; s3_10_skip = 1;\n"
    "\t\t\txil_printf(\"S3_DIAG10_GRAY_SKIPPED reg=5584 reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG10_GRAY_NOTE=TRY1_sat_uv_zero (0x5583=0x5584=0x00, 0x5580 unchanged)\\r\\n\");\n"
    "#elif S3_GRAY_TRY == 2\n"
    "\t\tif (s3_10_ok80) {\n"
    "\t\t\ts3_10_5580_a = (u8)((s3_10_5580 & (u8)~0xC0U) | 0x40U);\n"
    "\t\t\ts3_10_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x5580, (char)s3_10_5580_a);\n"
    "\t\t} else {\n"
    "\t\t\ts3_10_5580_a = 0xFF; s3_10_skip = 1;\n"
    "\t\t\txil_printf(\"S3_DIAG10_GRAY_SKIPPED reg=5580 reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG10_GRAY_NOTE=TRY2_effect_40 (0x5580[7:6]=10)\\r\\n\");\n"
    "#elif S3_GRAY_TRY == 3\n"
    "\t\tif (s3_10_ok80) {\n"
    "\t\t\ts3_10_5580_a = (u8)((s3_10_5580 & (u8)~0xC0U) | 0x80U);\n"
    "\t\t\ts3_10_wr |= i2c_reg16_write(&ps_i2c0, 0x3c, 0x5580, (char)s3_10_5580_a);\n"
    "\t\t} else {\n"
    "\t\t\ts3_10_5580_a = 0xFF; s3_10_skip = 1;\n"
    "\t\t\txil_printf(\"S3_DIAG10_GRAY_SKIPPED reg=5580 reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG10_GRAY_NOTE=TRY3_effect_80 (0x5580[7:6]=11)\\r\\n\");\n"
    "#else\n"
    "\t\txil_printf(\"S3_DIAG10_GRAY_NOTE=TRY0_read_only_no_write\\r\\n\");\n"
    "#endif\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x5580, &s3_10_5580_rb) != 0) { s3_10_5580_rb = 0xFF; }\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x5583, &s3_10_5583_rb) != 0) { s3_10_5583_rb = 0xFF; }\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x5584, &s3_10_5584_rb) != 0) { s3_10_5584_rb = 0xFF; }\n"
    "\t\txil_printf(\"S3_DIAG10_GRAY=TRY=%d 5580 before=0x%02X after=0x%02X readback=0x%02X | 5583 before=0x%02X after=0x%02X readback=0x%02X | 5584 before=0x%02X after=0x%02X readback=0x%02X write_status=%d\\r\\n\",\n"
    "\t\t\t(int)S3_GRAY_TRY, s3_10_5580, s3_10_5580_a, s3_10_5580_rb,\n"
    "\t\t\ts3_10_5583, s3_10_5583_a, s3_10_5583_rb,\n"
    "\t\t\ts3_10_5584, s3_10_5584_a, s3_10_5584_rb,\n"
    "\t\t\ts3_10_skip ? -2 : s3_10_wr);\n"
    "\t}\n"
)

if V9_WRITE_INIT_NEW.count(_V7_WRITE_INIT_ANCHOR) != 1:
    print("V10_WRITE_INIT_ANCHOR_NOT_UNIQUE")
    sys.exit(2)
# 插在 v9 的端口写测试之后、15 s 等待之前
# → 顺序：测试图 → AWB 关 → 手动增益 → 端口 select → 输出顺序 → 去色 → 等待 → 启动 S2MM
V10_WRITE_INIT_NEW = V9_WRITE_INIT_NEW.replace(_V7_WRITE_INIT_ANCHOR, V10_GRAY_BLOCK + _V7_WRITE_INIT_ANCHOR)

# ---------------------------------------------------------------------------
# v11 变体追加内容（只在 VARIANT == "v11" 时生效；v4~v10 输出保持不变）
# v11 = v10 + 取帧应用：指纹 3 次（t≈5/10/15 s）后 t≈20 s 停 S2MM，保持静止 240 s
# ---------------------------------------------------------------------------
V11_HELPERS = (
    "/* ================= S3-DIAG11 取帧应用：停 S2MM、保持静止 240 s =================\n"
    " * 目的：整帧经 JTAG 慢读期间 VDMA 仍在写新帧，会把多帧拼成撕裂帧（已实测到）。\n"
    " *   本变体在 t≈20 s 把 S2MM 停住（清 S2MM_CR 的 RUN/STOP 位，保持其他位），\n"
    " *   停前/停后各做一次帧缓冲 cache 失效，之后保持静止 240 s（每 30 s 一次心跳），\n"
    " *   供外部（JTAG/调试器）做干净的整帧导出。\n"
    " * 帧缓冲范围：720 行 × 3840 字节 = 2,764,800 = 0x2A3000（起点取 dispCtrl.framePtr[curFrame]，\n"
    " *   预期 0x00110C00，运行时会打印实际值）。\n"
    " * 本变体**不做任何寄存器写测试**：v6 测试图、v7 AWB、v8 手动增益、v9 端口/输出顺序、\n"
    " *   v10 去色等开关全部保持默认 0（只打印各自的 OFF/TRY=0 行）。*/\n"
    "#ifndef S3_DIAG11_FB_BYTES\n"
    "#define S3_DIAG11_FB_BYTES (720 * 3840)\n"
    "#endif\n"
    "\n"
)

# v11 替换掉 v6 的“5 次指纹 + t≈30 s 传感器回读”采样段：改成 3 次（t≈5/10/15 s）+ 传感器回读 + 停 S2MM。
# 直接从 V10_WRITE_INIT_NEW 里按锚点切出这一段，避免手抄出错（若锚点缺失就报错退出）。
_V11_SAMP_START_ANCHOR = "\t/* S3-DIAG6: 启动后 t≈5/10/15/20/25 秒各做一次 64 KB×3 区指纹"
_V11_SAMP_END_ANCHOR = "\txil_printf(\"S3_DIAG6_SAMPLING_DONE\\r\\n\");\n"
if V10_WRITE_INIT_NEW.count(_V11_SAMP_START_ANCHOR) != 1 or V10_WRITE_INIT_NEW.count(_V11_SAMP_END_ANCHOR) != 1:
    print("V11_SAMPLING_ANCHOR_NOT_UNIQUE")
    sys.exit(2)
_V11_I = V10_WRITE_INIT_NEW.index(_V11_SAMP_START_ANCHOR)
_V11_J = V10_WRITE_INIT_NEW.index(_V11_SAMP_END_ANCHOR, _V11_I) + len(_V11_SAMP_END_ANCHOR)
V11_SAMPLING_OLD = V10_WRITE_INIT_NEW[_V11_I:_V11_J]

V11_SAMPLING_NEW = (
    "\t/* S3-DIAG11 取帧应用：先做 3 次 64 KB×3 区指纹（t≈5/10/15 s）确认帧在动，\n"
    "\t * 然后 t≈20 s 停 S2MM 让帧缓冲静止，之后保持 240 s 供整帧导出。*/\n"
    "\txil_printf(\"S3_DIAG6_ALGO=sum32+crc32(0xEDB88320) bytes=65536 sites=0x000000,0x080000,0x100000\\r\\n\");\n"
    "\ts3_diag5_regs(0);\n"
    "\tXTime_GetTime(&s3_t6_start);\n"
    "\t{\n"
    "\t\tint s3_k, s3_s;\n"
    "\t\tfor (s3_k = 0; s3_k < 3; s3_k++) {\n"
    "\t\t\tu32 s3_tsec;\n"
    "\t\t\tfor (s3_s = 0; s3_s < 5; s3_s++) { sleep(1); }\n"
    "\t\t\tXTime_GetTime(&s3_t6_now);\n"
    "\t\t\ts3_tsec = (u32)((s3_t6_now - s3_t6_start) / COUNTS_PER_SECOND);\n"
    "\t\t\txil_printf(\"S3_DIAG6_SAMPLE=%d\\r\\n\", s3_k + 1);\n"
    "\t\t\ts3_diag6_sr(s3_tsec);\n"
    "\t\t\ts3_diag6_fp(s3_tsec, 0, 0x000000U);\n"
    "\t\t\ts3_diag6_fp(s3_tsec, 1, 0x080000U);\n"
    "\t\t\ts3_diag6_fp(s3_tsec, 2, 0x100000U);\n"
    "\t\t}\n"
    "\t\t/* t≈15 s 处再做一次只读传感器回读（保留 v6 的 S3_DIAG6_SENS 行；只读，不写寄存器）*/\n"
    "\t\t{\n"
    "\t\t\tu32 s3_tsec;\n"
    "\t\t\tu8 s3_s6_4202, s3_s6_3008, s3_s6_503d, s3_s6_3035;\n"
    "\t\t\tXTime_GetTime(&s3_t6_now);\n"
    "\t\t\ts3_tsec = (u32)((s3_t6_now - s3_t6_start) / COUNTS_PER_SECOND);\n"
    "\t\t\ts3_s6_4202 = s3_diag5_sens(0x4202);\n"
    "\t\t\ts3_s6_3008 = s3_diag5_sens(0x3008);\n"
    "\t\t\ts3_s6_503d = s3_diag5_sens(0x503D);\n"
    "\t\t\ts3_s6_3035 = s3_diag5_sens(0x3035);\n"
    "\t\t\txil_printf(\"S3_DIAG6_SENS=4202=0x%02X 3008=0x%02X 503D=0x%02X 3035=0x%02X t=%u\\r\\n\",\n"
    "\t\t\t\ts3_s6_4202, s3_s6_3008, s3_s6_503d, s3_s6_3035, s3_tsec);\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG6_SAMPLING_DONE\\r\\n\");\n"
    "\t\t/* 等到 t≈20 s（3 次采样约到 15 s，再等 5 秒）*/\n"
    "\t\tfor (s3_s = 0; s3_s < 5; s3_s++) { sleep(1); }\n"
    "\t}\n"
    "\t/* ---- S3-DIAG11: t≈20 s 停止 S2MM，让帧缓冲静止，供 JTAG 整帧导出 ---- */\n"
    "\t{\n"
    "\t\tu32 s3_11_crb, s3_11_cra, s3_11_sr, s3_11_frame0, s3_11_stride, s3_11_tsec;\n"
    "\t\tu8 *s3_11_fb = (u8 *)dispCtrl.framePtr[dispCtrl.curFrame];\n"
    "\t\tXTime_GetTime(&s3_t6_now);\n"
    "\t\ts3_11_tsec = (u32)((s3_t6_now - s3_t6_start) / COUNTS_PER_SECOND);\n"
    "\t\t/* 停住前：先失效帧缓冲 cache 范围（读前必须失效，否则可能读到陈旧 cache 行）*/\n"
    "\t\tXil_DCacheInvalidateRange((INTPTR)s3_11_fb, S3_DIAG11_FB_BYTES);\n"
    "\t\ts3_11_crb = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET);\n"
    "\t\tXAxiVdma_WriteReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET,\n"
    "\t\t\ts3_11_crb & ~((u32)XAXIVDMA_CR_RUNSTOP_MASK));\n"
    "\t\ts3_11_cra = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET);\n"
    "\t\t/* 停住后再失效一次：确保后续读到的就是 DDR 里的静止内容 */\n"
    "\t\tXil_DCacheInvalidateRange((INTPTR)s3_11_fb, S3_DIAG11_FB_BYTES);\n"
    "\t\ts3_11_sr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_SR_OFFSET);\n"
    "\t\ts3_11_frame0 = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_S2MM_ADDR_OFFSET + 0x0CU);\n"
    "\t\ts3_11_stride = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_S2MM_ADDR_OFFSET + 0x08U);\n"
    "\t\txil_printf(\"S3_DIAG11_HALT=1 CR_before=0x%08X CR_after=0x%08X SR=0x%08X HALTED_bit=%d FRAME0=0x%08X STRIDE=0x%08X FB=0x%08X FB_BYTES=0x%08X t=%u\\r\\n\",\n"
    "\t\t\ts3_11_crb, s3_11_cra, s3_11_sr,\n"
    "\t\t\t(s3_11_sr & ((u32)XAXIVDMA_SR_HALTED_MASK)) ? 1 : 0,\n"
    "\t\t\ts3_11_frame0, s3_11_stride, (u32)(UINTPTR)s3_11_fb, (u32)S3_DIAG11_FB_BYTES, s3_11_tsec);\n"
    "\t\t/* 保持静止 240 s：每 30 s 一次心跳（8 次），期间不再写任何寄存器 */\n"
    "\t\t{\n"
    "\t\t\tint s3_11_h;\n"
    "\t\t\tfor (s3_11_h = 0; s3_11_h < 8; s3_11_h++) {\n"
    "\t\t\t\tu32 s3_11_ts;\n"
    "\t\t\t\tint s3_11_w;\n"
    "\t\t\t\tfor (s3_11_w = 0; s3_11_w < 30; s3_11_w++) { sleep(1); }\n"
    "\t\t\t\tXTime_GetTime(&s3_t6_now);\n"
    "\t\t\t\ts3_11_ts = (u32)((s3_t6_now - s3_t6_start) / COUNTS_PER_SECOND);\n"
    "\t\t\t\ts3_11_sr = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_SR_OFFSET);\n"
    "\t\t\t\txil_printf(\"S3_DIAG11_HOLD t=%u SR=0x%08X HALTED_bit=%d\\r\\n\",\n"
    "\t\t\t\t\ts3_11_ts, s3_11_sr, (s3_11_sr & ((u32)XAXIVDMA_SR_HALTED_MASK)) ? 1 : 0);\n"
    "\t\t\t}\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG11_HOLD_DONE holds=8 seconds=240 frozen=1\\r\\n\");\n"
    "\t}\n"
)

V11_WRITE_INIT_NEW = V10_WRITE_INIT_NEW[:_V11_I] + V11_SAMPLING_NEW + V10_WRITE_INIT_NEW[_V11_J:]

# ---------------------------------------------------------------------------
# v12 变体追加内容（只在 VARIANT == "v12" 时生效；v4~v11 输出保持不变）
# v12 = v11 + 传感器内置彩条测试图案（0x503D=0x80，写入前回读、写入后回读校验）
# ---------------------------------------------------------------------------
V12_HELPERS = (
    "/* ================= S3-DIAG12 传感器内置彩条测试图案 =================\n"
    " * 目的：给第三方实验提供**已知颜色**的测试图案（0x503D=0x80），经同一条 DVP→VDMA→DDR 链路\n"
    " *   转储后判断“真缺色相/缺位”还是“仅 R/B 顺序或位拼接错”。\n"
    " * 做法：写 0x503D=0x80（先回读原值，写后再回读校验）；读失败则跳过写入（沿用 v7~v11 安全原则，\n"
    " *   不用不可信的值覆盖寄存器）。本变体同时保留 v11 的取帧能力（t≈20 s 停 S2MM、保持 240 s）。*/\n"
    "\n"
)

V12_BARS_BLOCK = (
    "\t/* S3-DIAG12: 打开传感器内置彩条测试图案（0x503D=0x80）。\n"
    "\t * 先回读原值 → 写 → 回读校验；读失败跳过写入并打印 SKIPPED/-2。*/\n"
    "\t{\n"
    "\t\tu8 s3_12_before = 0, s3_12_rb = 0xFF;\n"
    "\t\tint s3_12_wr;\n"
    "\t\tif (s3_diag5_i2c_read16(0x3C, 0x503D, &s3_12_before) == 0) {\n"
    "\t\t\ts3_12_wr = i2c_reg16_write(&ps_i2c0, 0x3c, 0x503D, 0x80);\n"
    "\t\t\tif (s3_diag5_i2c_read16(0x3C, 0x503D, &s3_12_rb) != 0) { s3_12_rb = 0xFF; }\n"
    "\t\t} else {\n"
    "\t\t\ts3_12_before = 0xFF; s3_12_rb = 0xFF; s3_12_wr = -2;\n"
    "\t\t\txil_printf(\"S3_DIAG12_BARS_SKIPPED reg=503D reason=read_failed\\r\\n\");\n"
    "\t\t}\n"
    "\t\txil_printf(\"S3_DIAG12_BARS=503D before=0x%02X after=0x%02X readback=0x%02X write_status=%d\\r\\n\",\n"
    "\t\t\ts3_12_before, 0x80U, s3_12_rb, s3_12_wr);\n"
    "\t}\n"
)

if V11_WRITE_INIT_NEW.count(_V7_WRITE_INIT_ANCHOR) != 1:
    print("V12_WRITE_INIT_ANCHOR_NOT_UNIQUE")
    sys.exit(2)
# 插在 v10 去色块之后、15 s 等待之前
# → 顺序：测试图(v6 开关 OFF) → AWB 关 → 手动增益 → 端口 select → 输出顺序 → 去色 → **彩条 v12** → 等待 → 启动 S2MM
V12_WRITE_INIT_NEW = V11_WRITE_INIT_NEW.replace(_V7_WRITE_INIT_ANCHOR, V12_BARS_BLOCK + _V7_WRITE_INIT_ANCHOR)

# S3_DIAG5_SENS 打印块（v5~v12 共用）的结尾：v7 起在其后追加 AWB 回读块
V5_SENS_ARGS_TAIL = (
    "\t\t\ts3_4202, s3_3008, s3_4740, s3_3035v, s3_3034v, s3_4300v, s3_501fv, s3_3824v, s3_503dv);\n"
    "\t}\n"
)
# S3_DIAG7_ISP_B 打印块（v7~v12 共用）的结尾：v9 起在其后追加 DVP 端口回读块
V7_ISP_B_TAIL = (
    "\t\txil_printf(\"S3_DIAG7_ISP_B=5586..558B=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X\\r\\n\",\n"
    "\t\t\ts3_5586, s3_5587, s3_5588, s3_5589, s3_558a, s3_558b);\n"
    "\t}\n"
)

if VARIANT in ("v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12"):
    # 替换 vdma_write_init 锚点的替换文本（保留 15 秒等待；各变体用各自的采样段）
    write_init_new = {
        "v5": V5_WRITE_INIT_NEW,
        "v6": V6_WRITE_INIT_NEW,
        "v7": V7_WRITE_INIT_NEW,
        "v8": V8_WRITE_INIT_NEW,
        "v9": V9_WRITE_INIT_NEW,
        "v10": V10_WRITE_INIT_NEW,
        "v11": V11_WRITE_INIT_NEW,
        "v12": V12_WRITE_INIT_NEW,
    }[VARIANT]
    insertions = [
        (old, write_init_new) if old.startswith("\tvdma_write_init(") else (old, new)
        for (old, new) in insertions
    ]
    insertions += [
        ("int main(void)\n{", V5_HELPERS + "int main(void)\n{"),
        (V5_MEMSET_OLD, V5_MEMSET_NEW),
        (V5_DIAG3_OLD, V5_DIAG3_NEW),
        (V5_RETURN_OLD, V5_RETURN_NEW),
    ]
    if VARIANT in ("v6", "v7", "v8", "v9", "v10", "v11", "v12"):
        insertions += [
            (V6_INCLUDE_OLD, V6_INCLUDE_NEW),
            ("int main(void)\n{", V6_HELPERS + "int main(void)\n{"),
        ]
    if VARIANT in ("v7", "v8", "v9", "v10", "v11", "v12"):
        insertions += [
            ("int main(void)\n{", V7_HELPERS + "int main(void)\n{"),
            (V5_SENS_ARGS_TAIL, V5_SENS_ARGS_TAIL + V7_AWB_READBACK),
        ]
    if VARIANT in ("v8", "v9", "v10", "v11", "v12"):
        insertions += [
            ("int main(void)\n{", V8_HELPERS + "int main(void)\n{"),
        ]
    if VARIANT in ("v9", "v10", "v11", "v12"):
        insertions += [
            ("int main(void)\n{", V9_HELPERS + "int main(void)\n{"),
            (V7_ISP_B_TAIL, V7_ISP_B_TAIL + V9_PAD_READBACK),
        ]
    if VARIANT in ("v10", "v11", "v12"):
        insertions += [
            ("int main(void)\n{", V10_HELPERS + "int main(void)\n{"),
        ]
    if VARIANT in ("v11", "v12"):
        insertions += [
            ("int main(void)\n{", V11_HELPERS + "int main(void)\n{"),
        ]
    if VARIANT == "v12":
        insertions += [
            ("int main(void)\n{", V12_HELPERS + "int main(void)\n{"),
        ]

for old, new in insertions:
    if old not in text:
        print(f"INSERT_CONTEXT_NOT_FOUND: {old.splitlines()[0][:60]}")
        sys.exit(2)
    if text.count(old) != 1:
        print(f"INSERT_CONTEXT_NOT_UNIQUE: {old.splitlines()[0][:60]} count={text.count(old)}")
        sys.exit(2)
    text = text.replace(old, new)

if crlf:
    text = text.replace("\n", "\r\n")
with open(target, "w", encoding="utf-8", newline="") as fh:
    fh.write(text)

# 生成 unified diff（保留 git 风格路径，便于 git apply -p1）
cp = subprocess.run(
    ["git", "diff", "--no-index", "--src-prefix=a/", "--dst-prefix=b/", str(ORIG / FILE), str(WORK / FILE)],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
)
diff = cp.stdout
# 只保留 hunk，自己写稳定表头，避免绝对路径/CRLF 差异导致 git apply 跳过
lines = diff.splitlines()
try:
    first_hunk = next(i for i, ln in enumerate(lines) if ln.startswith("@@"))
except StopIteration:
    print("NO_HUNK_IN_DIFF")
    sys.exit(2)
hunks = "\n".join(lines[first_hunk:]) + "\n"
diff = f"--- a/{FILE}\n+++ b/{FILE}\n{hunks}"
if not diff.strip():
    print("EMPTY_DIFF")
    sys.exit(2)
OUT_PATCH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATCH, "w", encoding="utf-8", newline="") as fh:
    fh.write(diff)

# 验证：对全新副本应用补丁
VERIFY = SCRATCH / "verify"
shutil.copytree(SRC, VERIFY)
res = subprocess.run(
    ["git", "apply", "--verbose", "-p1", str(OUT_PATCH)],
    cwd=VERIFY, capture_output=True, text=True, encoding="utf-8", errors="replace",
)
print(f"VARIANT={VARIANT}")
print(f"PATCH={OUT_PATCH}")
print(f"GIT_APPLY_EXIT={res.returncode}")
print(res.stdout.strip()[-500:])
print(res.stderr.strip()[-500:])
if res.returncode != 0:
    sys.exit(3)
with open(VERIFY / FILE, "r", encoding="utf-8", newline="") as fh:
    verify_text = fh.read()
# 厂商源是 CRLF，跨行断言先归一化换行，避免假阴性。
verify_text_norm = verify_text.replace("\r\n", "\n")
print(f"VERIFY_HAS_APP_ENTER={'S3_DIAG_APP_ENTER' in verify_text}")
print(f"VERIFY_HAS_SENSOR_ID={'S3_DIAG_SENSOR_ID' in verify_text}")
print(f"VERIFY_HAS_DISPLAY_START={'S3_DIAG_DISPLAY_START' in verify_text}")
print(f"VERIFY_HAS_VDMA_WRITE={'S3_DIAG_VDMA_WRITE_STARTED' in verify_text}")
if VARIANT in ("v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12"):
    print(f"VERIFY_HAS_D5_REG={'S3_DIAG5_REG' in verify_text}")
    print(f"VERIFY_HAS_D5_SR_DECODE={'S3_DIAG5_SR_DECODE' in verify_text}")
    print(f"VERIFY_HAS_D5_CFG={'S3_DIAG5_CFG' in verify_text}")
    print(f"VERIFY_HAS_D5_SENS={'S3_DIAG5_SENS' in verify_text}")
    print(f"VERIFY_HAS_DCACHE_FLUSH={'Xil_DCacheFlushRange((INTPTR)dispCtrl.framePtr[dispCtrl.curFrame], 1920 * 1080 * 3)' in verify_text}")
    print(f"VERIFY_HAS_IDLE_LOOP={'for (;;) { sleep(1); }' in verify_text}")
    print(f"VERIFY_MAIN_TAIL_IDLE={verify_text_norm.rstrip().endswith(V5_TAIL_IDLE_SUFFIX)}")
    print(f"VERIFY_TAIL_STILL_RETURNS={V5_TAIL_RETURN in verify_text_norm}")
if VARIANT == "v5":
    print(f"VERIFY_HAS_D5_NZ={'S3_DIAG5_NZ' in verify_text}")
    print(f"VERIFY_HAS_D5_SAMPLES={'S3_DIAG5_SAMPLE=%d' in verify_text}")
    print(f"VERIFY_HAS_DCACHE_INV4096={'Xil_DCacheInvalidateRange((INTPTR)s3_p, 4096)' in verify_text}")
if VARIANT in ("v6", "v7", "v8", "v9", "v10", "v11", "v12"):
    print(f"VERIFY_HAS_D6_ALGO={'S3_DIAG6_ALGO=sum32+crc32(0xEDB88320)' in verify_text}")
    print(f"VERIFY_HAS_D6_FP={'S3_DIAG6_FP t=%u site=%u sum=0x%08X hash=0x%08X nz=%u' in verify_text}")
    print(f"VERIFY_HAS_D6_SR={'S3_DIAG6_SR t=%u S2MM_SR=0x%08X' in verify_text}")
    print(f"VERIFY_HAS_D6_SENS={'S3_DIAG6_SENS=4202=0x%02X 3008=0x%02X 503D=0x%02X 3035=0x%02X t=%u' in verify_text}")
    print(f"VERIFY_HAS_D6_TP_SWITCH={'#if S3_TESTPATTERN' in verify_text and '#define S3_TESTPATTERN 0' in verify_text}")
    print(f"VERIFY_HAS_D6_TP_WRITE={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x503D, 0x80)' in verify_text}")
    print(f"VERIFY_HAS_D6_5SAMPLES={'for (s3_k = 0; s3_k < 5; s3_k++)' in verify_text}")
    print(f"VERIFY_HAS_D6_3SITES={'0x080000U' in verify_text and '0x100000U' in verify_text}")
    print(f"VERIFY_HAS_D6_INV64K={'Xil_DCacheInvalidateRange((INTPTR)s3_p, S3_DIAG6_FP_BYTES)' in verify_text}")
    print(f"VERIFY_HAS_XTIME={'#include \"xtime_l.h\"' in verify_text}")
    print(f"VERIFY_NO_D5_SAMPLING={'S3_DIAG5_SAMPLE=%d' not in verify_text}")
if VARIANT in ("v7", "v8", "v9", "v10", "v11", "v12"):
    print(f"VERIFY_HAS_D7_AWB={'S3_DIAG7_AWB=5001=0x%02X 3406=0x%02X 3400..3405=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X 503D=0x%02X 4300=0x%02X 501F=0x%02X' in verify_text}")
    print(f"VERIFY_HAS_D7_AE={'S3_DIAG7_AE=3503=0x%02X 3500..3502=0x%02X,0x%02X,0x%02X 3035=0x%02X' in verify_text}")
    print(f"VERIFY_HAS_D7_ISP_A={'S3_DIAG7_ISP_A=5580..5585=' in verify_text}")
    print(f"VERIFY_HAS_D7_ISP_B={'S3_DIAG7_ISP_B=5586..558B=' in verify_text}")
    print(f"VERIFY_HAS_D7_AWB_OFF_SWITCH={'#if S3_AWB_OFF' in verify_text and '#define S3_AWB_OFF 0' in verify_text}")
    print(f"VERIFY_HAS_D7_AWB_OFF_WRITE={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x5001, (char)s3_awb_after)' in verify_text}")
    print(f"VERIFY_HAS_D7_AWB_OFF_ON={'S3_DIAG7_AWB_OFF=ON before=0x%02X after=0x%02X write_status=%d' in verify_text}")
    print(f"VERIFY_HAS_D7_AWB_OFF_OFFLINE={'S3_DIAG7_AWB_OFF=OFF (0x5001 unchanged)' in verify_text}")
    print(f"VERIFY_HAS_D7_AWB_VERIFY={'S3_DIAG7_AWB_OFF_VERIFY readback=0x%02X' in verify_text}")
    print(f"VERIFY_HAS_D7_AWB_SKIP={'S3_DIAG7_AWB_OFF_SKIPPED reason=0x5001_read_failed' in verify_text}")
if VARIANT in ("v8", "v9", "v10", "v11", "v12"):
    print(f"VERIFY_HAS_D8_SWITCH={'#if S3_WB_MANUAL' in verify_text and '#define S3_WB_MANUAL 0' in verify_text}")
    print(f"VERIFY_HAS_D8_DEFAULTS={'#define S3_WB_R 1024' in verify_text and '#define S3_WB_G 1024' in verify_text and '#define S3_WB_B 1024' in verify_text}")
    print(f"VERIFY_HAS_D8_3406_ENABLE={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x3406, 0x01)' in verify_text}")
    print(f"VERIFY_HAS_D8_GAIN_WRITES={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x3400, (char)((s3_wb_r >> 8) & 0xFF))' in verify_text and 'i2c_reg16_write(&ps_i2c0, 0x3c, 0x3405, (char)(s3_wb_b & 0xFF))' in verify_text}")
    print(f"VERIFY_HAS_D8_WB_LINE={'S3_DIAG8_WB=MANUAL R=0x%04X G=0x%04X B=0x%04X before3406=0x%02X after3406=0x%02X readback3400..3405=0x%02X,0x%02X,0x%02X,0x%02X,0x%02X,0x%02X' in verify_text}")
    print(f"VERIFY_HAS_D8_WB_RB_LINE={'S3_DIAG8_WB_RB rb_r16=0x%04X rb_g16=0x%04X rb_b16=0x%04X match=%u,%u,%u write_status=%d' in verify_text}")
    print(f"VERIFY_HAS_D8_WB_OFFLINE={'S3_DIAG8_WB=OFF (auto AWB unchanged)' in verify_text}")
if VARIANT in ("v9", "v10", "v11", "v12"):
    print(f"VERIFY_HAS_D9_PAD_LINE={'S3_DIAG9_PAD=3017=0x%02X 3018=0x%02X 301D=0x%02X 301E=0x%02X 300A=0x%02X 300B=0x%02X 4741=0x%02X 4745=0x%02X 4300=0x%02X 501F=0x%02X S3_DIAG9_D9SEL=%u D6SEL=%u' in verify_text}")
    print(f"VERIFY_HAS_D9_SWITCHES={'#ifndef S3_PAD_SEL_CLEAR' in verify_text and '#define S3_PAD_SEL_CLEAR 0' in verify_text and '#ifndef S3_DVP_ORDER_DEBUG' in verify_text and '#define S3_DVP_ORDER_DEBUG 0' in verify_text}")
    print(f"VERIFY_HAS_D9_FIX_LINE={'S3_DIAG9_FIX=301D before=0x%02X after=0x%02X readback=0x%02X 301E before=0x%02X after=0x%02X readback=0x%02X write_status=%d' in verify_text}")
    print(f"VERIFY_HAS_D9_FIX_WRITE_301D={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x301D, (char)s3_9d_after)' in verify_text}")
    print(f"VERIFY_HAS_D9_FIX_WRITE_301E={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x301E, (char)s3_9e_after)' in verify_text}")
    print(f"VERIFY_HAS_D9_FIX_SKIPS={'S3_DIAG9_FIX_SKIPPED reg=301D reason=read_failed' in verify_text and 'S3_DIAG9_FIX_SKIP_301E=1 reason=bit1_already_0_no_write' in verify_text}")
    print(f"VERIFY_HAS_D9_ORDER_WR={'S3_DIAG9_ORDER_WR=4745 before=0x%02X after=0x%02X readback=0x%02X write_status=%d' in verify_text}")
    print(f"VERIFY_HAS_D9_ORDER_WRITE={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x4745, (char)s3_9o_after)' in verify_text}")
    print(f"VERIFY_HAS_D9_NOT_RESTORED={'S3_DIAG9_ORDER=NOT_RESTORED' in verify_text}")
    print(f"VERIFY_HAS_D9_ORDER_OFFLINE={'S3_DIAG9_ORDER=OFF (0x4745 unchanged)' in verify_text}")
    print(f"VERIFY_HAS_D9_NO_RESTORE_CODE={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x4745, (char)s3_9o_before)' not in verify_text}")
    print(f"VERIFY_HAS_D9_D9SEL_UNKNOWN={'s3_9_d9 = 255U' in verify_text and 's3_9_d6 = 255U' in verify_text}")
if VARIANT in ("v10", "v11", "v12"):
    print(f"VERIFY_HAS_D10_SWITCH={'#ifndef S3_GRAY_TRY' in verify_text and '#define S3_GRAY_TRY 0' in verify_text}")
    print(f"VERIFY_HAS_D10_GRAY_LINE={'S3_DIAG10_GRAY=TRY=%d 5580 before=0x%02X after=0x%02X readback=0x%02X | 5583 before=0x%02X after=0x%02X readback=0x%02X | 5584 before=0x%02X after=0x%02X readback=0x%02X write_status=%d' in verify_text}")
    print(f"VERIFY_HAS_D10_NOTE_TRY0={'S3_DIAG10_GRAY_NOTE=TRY0_read_only_no_write' in verify_text}")
    print(f"VERIFY_HAS_D10_NOTE_TRY1={'S3_DIAG10_GRAY_NOTE=TRY1_sat_uv_zero' in verify_text}")
    print(f"VERIFY_HAS_D10_NOTE_TRY2={'S3_DIAG10_GRAY_NOTE=TRY2_effect_40' in verify_text}")
    print(f"VERIFY_HAS_D10_NOTE_TRY3={'S3_DIAG10_GRAY_NOTE=TRY3_effect_80' in verify_text}")
    print(f"VERIFY_HAS_D10_WRITE_5583={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x5583, 0x00)' in verify_text}")
    print(f"VERIFY_HAS_D10_WRITE_5584={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x5584, 0x00)' in verify_text}")
    print(f"VERIFY_HAS_D10_WRITE_5580_40={'(s3_10_5580 & (u8)~0xC0U) | 0x40U' in verify_text}")
    print(f"VERIFY_HAS_D10_WRITE_5580_80={'(s3_10_5580 & (u8)~0xC0U) | 0x80U' in verify_text}")
    print(f"VERIFY_HAS_D10_SKIPS={'S3_DIAG10_GRAY_SKIPPED reg=5583' in verify_text and 'S3_DIAG10_GRAY_SKIPPED reg=5580' in verify_text}")
if VARIANT in ("v11", "v12"):
    print(f"VERIFY_HAS_D11_HELPER={'#define S3_DIAG11_FB_BYTES (720 * 3840)' in verify_text}")
    print(f"VERIFY_HAS_D11_HALT_LINE={'S3_DIAG11_HALT=1 CR_before=0x%08X CR_after=0x%08X SR=0x%08X HALTED_bit=%d FRAME0=0x%08X STRIDE=0x%08X' in verify_text}")
    print(f"VERIFY_HAS_D11_HOLD_LINE={'S3_DIAG11_HOLD t=%u SR=0x%08X' in verify_text}")
    print(f"VERIFY_HAS_D11_HOLD_DONE={'S3_DIAG11_HOLD_DONE holds=8 seconds=240 frozen=1' in verify_text}")
    print(f"VERIFY_HAS_D11_CR_WRITE={'XAxiVdma_WriteReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET,' in verify_text}")
    print(f"VERIFY_HAS_D11_RS_CLEAR={'s3_11_crb & ~((u32)XAXIVDMA_CR_RUNSTOP_MASK)' in verify_text}")
    print(f"VERIFY_HAS_D11_CR_READBACK={'s3_11_cra = XAxiVdma_ReadReg(XPAR_AXIVDMA_1_BASEADDR, XAXIVDMA_RX_OFFSET + XAXIVDMA_CR_OFFSET)' in verify_text}")
    print(f"VERIFY_D11_INV_COUNT={verify_text.count('Xil_DCacheInvalidateRange((INTPTR)s3_11_fb, S3_DIAG11_FB_BYTES)')}")
    print(f"VERIFY_HAS_D11_3SAMPLES={'for (s3_k = 0; s3_k < 3; s3_k++)' in verify_text}")
    print(f"VERIFY_NO_D11_5SAMPLES={'for (s3_k = 0; s3_k < 5; s3_k++)' not in verify_text}")
    print(f"VERIFY_HAS_D11_HOLD8={'for (s3_11_h = 0; s3_11_h < 8; s3_11_h++)' in verify_text}")
    print(f"VERIFY_HAS_D11_HOLD30={'for (s3_11_w = 0; s3_11_w < 30; s3_11_w++)' in verify_text}")
    print(f"VERIFY_HAS_D11_SENS_READONLY={'S3_DIAG6_SENS=4202=0x%02X 3008=0x%02X 503D=0x%02X 3035=0x%02X t=%u' in verify_text}")
    print(f"VERIFY_NO_D11_WRITE_TESTS={'#if S3_TESTPATTERN' in verify_text and '#if S3_AWB_OFF' in verify_text and '#if S3_WB_MANUAL' in verify_text and '#if S3_PAD_SEL_CLEAR' in verify_text and '#if S3_DVP_ORDER_DEBUG' in verify_text and '#if S3_GRAY_TRY == 1' in verify_text}")
print(f"PATCH_LINES={len(diff.splitlines())}")
print(f"PATCH_SHA256={hashlib.sha256(OUT_PATCH.read_bytes()).hexdigest()}")
print(f"VERIFY_DISPLAY_DEMO_SHA256={hashlib.sha256((VERIFY / FILE).read_bytes()).hexdigest()}")
if VARIANT == "v12":
    print(f"VERIFY_HAS_D12_BARS_LINE={'S3_DIAG12_BARS=503D before=0x%02X after=0x%02X readback=0x%02X write_status=%d' in verify_text}")
    print(f"VERIFY_HAS_D12_WRITE={'i2c_reg16_write(&ps_i2c0, 0x3c, 0x503D, 0x80)' in verify_text}")
    print(f"VERIFY_HAS_D12_SKIP={'S3_DIAG12_BARS_SKIPPED reg=503D reason=read_failed' in verify_text}")
    print(f"VERIFY_HAS_D12_READBACK={'if (s3_diag5_i2c_read16(0x3C, 0x503D, &s3_12_rb) != 0) { s3_12_rb = 0xFF; }' in verify_text}")
    print(f"VERIFY_HAS_D12_FREEZE_KEPT={'S3_DIAG11_HALT=1' in verify_text and 'S3_DIAG11_HOLD t=%u' in verify_text and 'S3_DIAG11_HOLD_DONE' in verify_text}")
    print(f"VERIFY_D12_INV_COUNT={verify_text.count('Xil_DCacheInvalidateRange((INTPTR)s3_11_fb, S3_DIAG11_FB_BYTES)')}")
