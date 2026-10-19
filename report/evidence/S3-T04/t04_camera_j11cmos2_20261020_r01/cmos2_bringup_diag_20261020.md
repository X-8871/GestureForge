# S3-T04 摄像头通道诊断：CMOS1 无响应、CMOS2 可用；S2MM 帧同步未闭合（2026-10-20 04:0x–04:4x，UTC+8）

## 一、CMOS1 通道：无 I2C 应答（J10 与 J11 两次独立验证）

| 运行 | 变体 | 结果 |
|---|---|---|
| `tmp/s3r06/t04_camera_j11_20261020_r01` | J11 + CMOS1（PIN20–35） | `SCAN_ACK_COUNT=0`；CHIPID 读值 0x0000/0x2A2A/0x2E2E（未初始化栈值，说明读失败） |
| 更早：J10 + CMOS1（r03） | 官方 22 工程原生映射 | 同上（`SCAN_ACK_COUNT=0`） |

两个不同口、两套独立 bitstream、同一现象 → 端口/位流/映射均排除；模块 **CMOS1 侧**（传感器或该路 I2C）不响应。

## 二、CMOS2 通道：**摄像头正常**

运行 `tmp/s3r06/t04_camera_j11cmos2_20261020_r01`（J11 + CMOS2，模块当前位置）：

```
S3_DIAG2_DEV=0x3C recv=0 val=0x56
S3_DIAG2_SCAN_ACK_COUNT=1
S3_DIAG2_CHIPID_TRY0/1/2 = 0x5640        <- OV5640 芯片 ID，三次一致
S3_DIAG3_OUT_W=0x0500 (1280)  OUT_H=0x02D0 (720)  VTS=0x02E4 (740)
S3_DIAG3_3035=0x21 3034=0x1A 4300=0x60 501F=0x01
S3_DIAG_DISPLAY_START status=0
```
→ I2C 通、`sensor_init` 写入生效、传感器确为 **1280×720@…** 输出。

## 三、本轮排除的假设（都有实测/原文依据）

1. **不是端口选错**：V3.0 手册 Table 7.4.1/7.5.1 原文逐针核对，J10 PIN20–35=T16…B20、J11 PIN20–35=J20…J14，与工程约束一致。
2. **不是软件读法**：I2C 控制器 0xE0004000 配置正常；厂商 `i2c_reg16_read()` 传输失败时返回未初始化栈值（0x2A2A/0x2E2E 每次不同即证据）。
3. **不是模块连接器针序**：放大官方模块原理图（`AN5642-2016-12-14.pdf`），J3 逐针为 Pin3=CMOS2_D9、4=SDA、5=D6、6=SCL、7=D7、8=D2、9=HREF、10=D8、11=D3、12=RESET、13=D4、14=D5、15=D1、16=D0、**17=VSYNC**、18=PCLK；Pin20–35 为 CMOS1 同构；Pin1=GND、2=+5V、19/36=NC、37/38=GND、39/40=+3.3V —— 与官方双目 XDC 逐条一致。
4. **不是器件/许可/构建**：BASIC 许可、`xc7z020clg400-2`、J10/J11/CMOS2 三套 bitstream 均构建通过、时序为正、DRC 0 error。
5. **不是采集 IP 上电等待**：`alinx_ov5640.v` 内含 `reset_cnt` 200M + `fifo_ready_cnt` 100M 个 PCLK 周期的硬等待；已试"等 15 秒再启动 S2MM"（v4 应用），仍未解决。
6. **不是 S2MM 配置参数**：回读确认 VSIZE=0x2D0、HSIZE=STRIDE=0xF00、ADDR=0x00110C00；BD 与官方双目工程 S2MM 配置逐项一致（`c_use_s2mm_fsync=2`、`num_fstores=1`、linebuffer 4096、burst 128、dre 1）。

## 四、当前唯一未闭合点：S2MM 收不到帧起始（SOF）

在线实验（`scripts/stage3_t04/jtag_s2mm_vsize_trial.tcl`，改 VSIZE + 复位重启 S2MM，观察 SR）：

| VSIZE | S2MM SR | 判读 |
|---|---|---|
| 720 (0x2D0) | `0x00015810` | ERR_INTERNAL(0x10) + **FSZ_MORE(0x800)** |
| 721 (0x2D1) | `0x00014810` | 仍 FSZ_MORE |
| 740 (0x2E4) | `0x00010810` | 仍 FSZ_MORE |
| 2000 (0x7D0) | `0x00014810` | 仍 FSZ_MORE |

一帧实际只有 ~740 行；若 SOF 正常，VSIZE=2000 必然报 `FSZ_LESS(0x80)`。**任何 VSIZE 都报 FSZ_MORE ⇒ 流入的流里没有帧起始（TUSER/SOF）**，行数据（TLAST）在流。
后果：`0x00110C00` 帧缓冲始终为 0，显示缓冲因此全黑；显示 MM2S 侧无任何错误。

候选原因（按可能性排序）：
1. 模块 **CMOS2_VSYNC 未真正到达 PL**（该路信号/触点问题）——IP 的 SOF 正是靠 VSYNC 下降沿产生；
2. S2MM 处于 `c_use_s2mm_fsync=2`（fsync_out）模式，帧边界不采用流入 TUSER；
3. 采集 IP 的 TUSER 未进入流（FIFO 位序/转换器 TUSER_REMAP 之外的问题）。

## 五、下一步（需要一次新的 PL 构建）

在 BD 上加一个 **5 探针 ILA**（BASIC 许可允许 ≤5 probes；厂商原 ILA 是 6 探针才被拒），探针取
`cmos_vsync`、`cmos_href`、`m_axis_video_tuser`、`m_axis_video_tlast`、`m_axis_video_tvalid`，
用 Vivado Hardware Manager/ILA 直接看：VSYNC 是否有下降沿、TUSER 是否产生、TLAST 频率是否=720/帧。
若确认 VSYNC 无翻转 → 模块该路信号问题；若 TUSER 有但 S2MM 不认 → 改 `c_use_s2mm_fsync=0` 复验。

## 六、产物与哈希（本轮）

- J11+CMOS2 bitstream：`tmp/s3r06/t04_camera_j11cmos2_20261020_r01/.../design_1_wrapper.bit`，SHA-256 `7c6d2522df7596e63339624cbeae2112fcb4ca8ab39c94fc33899c1e23bade98`（WNS=1.1412、WHS=0.0583、DRC 0 error）
- XSA：SHA-256 `c598375429f88f17f9e80c680555ece943837257aee13ce25ce34a477566dd27`
- 诊断应用补丁：`board/stage3/software/sensor/s3_t04_app_diag_v2/v3/v4.patch`（v2=I2C 扫描，v3=传感器关键寄存器回读，v4=S2MM 延时启动＋帧缓冲回读）
- 串口原文：`.../jtag_download{,_v3,_v4}/uart_*.log`；VDMA 寄存器：`.../vdma_regs.log`、`vdma_addr.log`

## 七、边界

全程仅易失性 JTAG 下载与只读回读；VSIZE 试验会停止/重启摄像头 VDMA（重下应用即可恢复）；未烧 QSPI、未改接线、未带电测量。**摄像头画面仍未显示，G3 未闭合。**