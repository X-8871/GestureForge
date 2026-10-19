# 阶段3 板测操作手册（T03 HDMI 独立画面 / T04 摄像头直通）

适用：AX7020（器件实测 `xc7z020`）+ AN5642 双目模块 + HDMI 显示器；时间以 UTC+8 记。
执行方式：下载与寄存器回读可由阶段3总控直接执行（易失性 JTAG，不烧 QSPI）；实物接线、上电、拔插必须由 Wong 执行。

## 0. 安全前置（每次接触硬件前）

- **断电插拔**：接/拔 AN5642 与 HDMI 线前必须断电（拔掉板卡电源），严禁带电插拔。
- **J10 Pin1 对齐**：AN5642 40 针必须与 J10 插座逐针对齐，Pin1（GND）方向不得偏移。
  J10/模块 **Pin2 都是 +5V**（供电），不是信号脚；Pin19/Pin36 为 NC（无针脚）。错位可能把 +5V 加到信号脚上，属不可逆损坏风险。
- BANK35 默认 I/O 为 **3.3V**，官方例程全部使用 `LVCMOS33`；不得接 5V I/O。
- 本阶段设计使用官方例程的 **CMOS1 通道（模块 Pin20–35 → J10 Pin20–35）**。
- 禁止以“试上电”判断插接方向；引脚弯曲/短路/插座松动时立即停止。

## 1. T03 HDMI 独立画面（当前可做，只需显示器）

### 1.1 接线
1. 断电，把 HDMI 线接到板卡 HDMI 口（BANK34，官方例程 HDMI OUT）。
2. 显示器上电，切换到对应 HDMI 输入源。
3. 板卡上电。启动模式为 JTAG（与当前实测一致）；代价是不需要 SD 卡。

### 1.2 下载（阶段3总控执行，已授权的易失性下载）
```bash
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_jtag_download_t03.sh \
  "D:/codex-worktrees/dbdf/tmp/s3r06/t03b_hdmi_20261020_r01" \
  "<T03 ELF 绝对路径>"
```
预期：9 步全 OK（CONNECT→PS_RESET→FPGA_PROGRAM→PS7_INIT→POST_CONFIG→A9_SELECT→DOW_ELF→RUN）。

### 1.3 预期结果
- 显示器出现 **800×600@60Hz** 的画面（应用使用 `VMODE_800x600`，内容为 800×600 静态图片 `pic_800_600.h`）。
- 显示器应识别到信号并自动切到 800×600；若显示器只支持 720p/1080p，可能显示“无信号/不支持的模式”——这是显示器兼容问题，不是 FPGA 失败（可在 T04 用 1280×720 复验）。

### 1.4 UART（可选，用于区分故障模式）
```bash
python /d/codex-worktrees/dbdf/scripts/stage3_t03b/read_uart.py COM4 10 <out.log>
```
T03 应用只在出错时打印（`Display Ctrl initialization failed...`、`Couldn't start display...`）；**无打印 = 无错误**。

### 1.5 寄存器回读（机器可验证）
```bash
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_xsdb.sh \
  "D:\codex-worktrees\dbdf\scripts\stage3_t03b\jtag_readback_t03.tcl"
```
判定：`DYNCLK_STATUS` bit0=1（RUNNING）、`VDMA_MM2S_CR` bit0=1（RS）、`VDMASR` Halted=0、帧缓冲非全零。
2026-10-20 00:4x 实测已全部满足（见 `report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/bringup_record.md`）。

### 1.6 异常停止点
- 下载脚本任一步 `T03_DL_FAIL=...`：立即停止并回传 `jtag_download/download.log`。
- 板上电后板卡异常发热、电源指示异常、显示器反复闪烁：断电并回传现象与时间。

## 2. T04 摄像头原始画面直通（需 AN5642 + 显示器）

### 2.1 前置
- 先完成 T03（证明 HDMI 通路）；或直接做 T04（更贴最终目标）。
- **断电**后把 AN5642 插到 J10（Pin1 对齐），再上电。

### 2.2 下载
```bash
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_jtag_download_t03.sh \
  "D:/codex-worktrees/dbdf/tmp/s3r06/t04_camera_20261020_r02" \
  "<T04 摄像头应用 ELF 绝对路径>"
```
（脚本对 bitstream/XSA/ELF 三个路径做哈希记录；T04 用其自身 XSA 解出的 `ps7_init.tcl`。）

### 2.3 预期结果与 UART 判定
显示器出现 **1280×720@60Hz** 的摄像头实时画面（厂商例程为单帧缓冲直通，快速移动时可能有撕裂，属已知口径）。

UART 必须出现（应用已打诊断补丁 `board/stage3/software/sensor/s3_t04_app_diag.patch`）：
```
S3_DIAG_APP_ENTER
S3_DIAG_SENSOR_ID=0x5640          <- OV5640 CHIP ID；0x5640=正确识别
S3_DIAG_DISPLAY_START status=0    <- 0=XST_SUCCESS
S3_DIAG_VDMA_WRITE_STARTED
```
抓取命令：`python scripts/stage3_t03b/read_uart.py COM4 15 <out.log>`

故障对照：
| 现象 | 含义 | 下一步 |
|---|---|---|
| 无任何 `S3_DIAG_APP_ENTER` | 应用未运行/未下载成功 | 查下载日志 |
| `SENSOR_ID` 非 0x5640（常为 0x0000/0xFFFF） | I2C 无应答：摄像头未插好、Pin1 错位或供电异常 | 断电复查插接与对齐 |
| `DISPLAY_START status!=0` | 显示控制器启动失败 | 回读 dynclk/VDMA/v_tc 寄存器 |
| UART 正常但屏幕无画面 | HDMI 信号/显示器兼容问题 | 换显示器或改用 T03 800×600 复验 |

### 2.4 寄存器回读（T04 地址与 T03 不同）
- `axi_vdma_0`（显示读） 0x4300_0000；`axi_vdma_1`（摄像头写） 0x4301_0000；`cmos_rst` 0x4120_0000；`v_tc` 0x43C0_0000；`axi_dynclk` 0x43C1_0000。
- 判定要点：两个 VDMA 的 CR.RS=1、状态寄存器 Halted=0；dynclk STATUS bit0=1。

### 2.5 异常停止点
- 摄像头插入后板卡电流/温度异常、模块明显发热：立即断电。
- UART 出现 I2C 无响应且重新插接后仍失败：停止，不反复热插拔。

## 3. 回传材料（每次板测）

1. 下载日志 `jtag_download/download.log` 与 `input_hashes.txt`；
2. UART 抓取文件；
3. 显示器画面照片或短视频（注明分辨率与拍摄时间）；
4. 现象与时间点、异常停止点的描述。

## 4. 边界

- 本手册不授权烧写 QSPI/非易失、不改跳线、不做带电测量。
- 未取得显示器画面照片前，HDMI 物理链路一律记为“未验证”。