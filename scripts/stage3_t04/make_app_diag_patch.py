"""生成 S3-T04/S3-T05 应用诊断补丁：只给厂商摄像头应用加 UART 诊断打印，不改任何寄存器时序与配置。

用法: make_app_diag_patch.py <厂商应用源目录> <输出补丁> <scratch 目录> [v4|v5]

做四件事：
1) 从官方源复制一份应用目录到 scratch；
2) 在 main() 关键节点插入 S3_DIAG 打印（应用启动、传感器 CHIP ID、显示启动状态、VDMA 写入启动）；
3) v5 变体追加：memset 后 DCache flush、DCache 失效后回读物理内存三处（S3_DIAG5_NZ）、
   S2MM SR 按真实位定义解码 + 帧计数（S3_DIAG5_REG/SR_DECODE/CFG）、t≈5/15/25 秒三次采样、
   传感器关键寄存器只读回显（S3_DIAG5_SENS）、main 不返回；
4) 用 git diff --no-index 生成 unified diff，并对全新副本验证补丁可干净应用。

默认变体 v4（保持既有 s3_t04_app_diag_v4.patch 可复现）；v5 只改 display_demo.c，输出路径由调用方给定。
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
# 变体选择：默认 v4，避免影响既有补丁的可复现性。
VARIANT = sys.argv[4].strip().lower() if len(sys.argv) > 4 else "v4"
if VARIANT not in ("v4", "v5"):
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

if VARIANT == "v5":
    # 替换 vdma_write_init 锚点的替换文本（保留 15 秒等待；改用 v5 的 t≈5/15/25 三次采样）
    insertions = [
        (old, V5_WRITE_INIT_NEW) if old.startswith("\tvdma_write_init(") else (old, new)
        for (old, new) in insertions
    ]
    insertions += [
        ("int main(void)\n{", V5_HELPERS + "int main(void)\n{"),
        (V5_MEMSET_OLD, V5_MEMSET_NEW),
        (V5_DIAG3_OLD, V5_DIAG3_NEW),
        (V5_RETURN_OLD, V5_RETURN_NEW),
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
if VARIANT == "v5":
    print(f"VERIFY_HAS_D5_REG={'S3_DIAG5_REG' in verify_text}")
    print(f"VERIFY_HAS_D5_SR_DECODE={'S3_DIAG5_SR_DECODE' in verify_text}")
    print(f"VERIFY_HAS_D5_CFG={'S3_DIAG5_CFG' in verify_text}")
    print(f"VERIFY_HAS_D5_NZ={'S3_DIAG5_NZ' in verify_text}")
    print(f"VERIFY_HAS_D5_SENS={'S3_DIAG5_SENS' in verify_text}")
    print(f"VERIFY_HAS_D5_SAMPLES={'S3_DIAG5_SAMPLE=%d' in verify_text}")
    print(f"VERIFY_HAS_DCACHE_FLUSH={'Xil_DCacheFlushRange((INTPTR)dispCtrl.framePtr[dispCtrl.curFrame], 1920 * 1080 * 3)' in verify_text}")
    print(f"VERIFY_HAS_DCACHE_INV4096={'Xil_DCacheInvalidateRange((INTPTR)s3_p, 4096)' in verify_text}")
    print(f"VERIFY_HAS_IDLE_LOOP={'for (;;) { sleep(1); }' in verify_text}")
    print(f"VERIFY_MAIN_TAIL_IDLE={verify_text_norm.rstrip().endswith(V5_TAIL_IDLE_SUFFIX)}")
    print(f"VERIFY_TAIL_STILL_RETURNS={V5_TAIL_RETURN in verify_text_norm}")
print(f"PATCH_LINES={len(diff.splitlines())}")
print(f"PATCH_SHA256={hashlib.sha256(OUT_PATCH.read_bytes()).hexdigest()}")
print(f"VERIFY_DISPLAY_DEMO_SHA256={hashlib.sha256((VERIFY / FILE).read_bytes()).hexdigest()}")