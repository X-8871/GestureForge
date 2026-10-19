# S3-T04 摄像头未识别：板上 I2C/DVP 诊断记录（2026-10-20 02:0x，UTC+8）

## 现象

Wong 断电插好 AN5642 到 **J10**（丝印位号已读为 J10；两端齐平、无悬空；模块不热、无异味、无弯针）后，重新经 JTAG 下载 T04 bitstream + 摄像头应用，串口仍为：

```
S3_DIAG_APP_ENTER
S3_DIAG_SENSOR_ID=0x0000        <- 传感器未识别
S3_DIAG_DISPLAY_START status=0
S3_DIAG_VDMA_WRITE_STARTED
```

## 诊断用的应用版本（本轮新建）

- 补丁：`board/stage3/software/sensor/s3_t04_app_diag_v2.patch`（在 v1 的 4 条打印之上，增加 PS I2C 控制器寄存器、整总线扫描、CHIP ID 3 次重试）
- ELF：`tmp/s3r06/t04_camera_diag2_r02/app/an5642_single_diag2.elf`
  SHA-256 `2a087536229854a51fb84e378cf93524f8cc9f13ae4693e9228379122b2fe30f`
- 构建：`scripts/stage3_t04_vitis/run_stage3_vitis_elf.cmd`（r03 XSA 重建 BSP，exit 0）

## 串口结果（`tmp/s3r06/t04_camera_20261020_r03/jtag_download_i2cscan/uart_i2cscan.log`）

```
S3_DIAG2_IIC_BASE=0xE0004000
S3_DIAG2_IIC_CR=0x0000E30E  SR=0x00000040  ISR=0x00000004
S3_DIAG2_SCAN_ACK_COUNT=0                     <- 0x08~0x77 全地址无任何 ACK
S3_DIAG2_CHIPID_TRY0=0x0000
S3_DIAG2_CHIPID_TRY1=0x2A2A
S3_DIAG2_CHIPID_TRY2=0x2E2E
S3_DIAG_SENSOR_ID=0x3333
```

## 判读

1. **I2C 控制器本身正常**：BaseAddress=0xE0004000（PS I2C0 正确）、CR 已配置（master/ACKEN/DIV）、SR 未显示总线卡死（BA 未置位）。
2. **整条总线没有任何器件应答**（0x08~0x77 全部 NACK）→ 摄像头的 OV5640 没有响应。
3. **CHIP ID 三次读取的值每次不同**（0x0000/0x2A2A/0x2E2E/0x3333）→ 证明厂商的 `i2c_reg16_read()` 在传输失败时**返回未初始化的栈数据**（该函数不检查传输状态）。因此之前"0x0000"不能当作"传感器返回 0"，而是"读失败"。
4. 只读寄存器探测（`tmp/…/jtag_download_i2cscan/camera_probe.log`）：
   - 帧缓冲 `0x00110C00` 与中段全为 **0** → **没有任何 DVP 数据写入**；
   - 摄像头 VDMA S2MM CR=0x00018003（RS=1）、SR=0x00010000（Halted=0、无错误）；
   - 显示 VDMA 与 dynclk 正常；`cmos_rst` GPIO = 1（复位已释放）；
   - PS I2C ADDR 残留 0x3C、ISR=0x00000004。

## 已排除

- **口选错**：用 V3.0 手册 Table 7.4.1（J10 针脚表）直接核对 —— J10 的 PIN20=T16、PIN21=V18、PIN22=V17、PIN23=T15、…、PIN33=A20、PIN34=B19、PIN35=B20，与本工程 `an5642.xdc` 的 CMOS1 引脚**逐针一致**；J11 是 F17/F16/F20…（不同 bank）。所以 J10 正确。
- **整列错位/未插到底**：Wong 已确认两端与针阵齐平。
- **传感器复位被拉住**：`cmos_rst` GPIO 终态为 1（按厂商代码语义为释放）。

## 仍需物理确认（软件已无法继续分辨）

- 模块连接器是否存在 **Pin1 标记/防呆缺口**；若无防呆，则**反插（180°）在物理上同样"齐平"**，会造成模块无供电，与现象完全一致。
- 模块是否**单通道**（若只有一路且接在 CMOS2 侧 Pin3–18，则本设计的 CMOS1 I2C 永远不通）。
- 模块是否有电源指示灯、上电后是否点亮。
- （需授权）万用表测量：J10 Pin1–Pin2 是否约 +5 V；插/拔模块时 J10 Pin2 对 GND 的阻值是否有变化。

## 边界

本轮只做易失性 JTAG 下载与只读寄存器回读；未带电测量、未改接线、未烧 QSPI。摄像头识别与 HDMI 画面仍未通过，G3 未闭合。