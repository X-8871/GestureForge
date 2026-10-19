# S3-T04/T05 无摄像头板卡预测试记录（2026-10-20，UTC+8）

目的：在 Wong 接上摄像头与显示器之前，先在已上电、JTAG 模式的板卡上验证 T04 硬件工程与摄像头应用软件链路，把"板卡/PS/应用/诊断"与"摄像头实物"两类风险分开。

## 授权与范围

- Wong 2026-10-20 00:3x 指示继续阶段3，并已上电、接 JTAG 与 UART；本轮下载经 Wong 直接指示下的同一授权范围。
- 只做**易失性** JTAG 下载（PL bitstream + PS 初始化 + ELF）；未烧 QSPI/非易失、未改跳线、未接摄像头、未接显示器。
- 无显示器、无摄像头：因此本记录**不含**任何画面结论，只证明电气/逻辑链路被正确配置。

## 输入（下载时逐项哈希核对）

```
5f6d357d57fa4b206390103ed6fcc90d5fbbca310c471ce3c956c09aa4f10738  design_1_wrapper.bit (T04, r03)
5e0663b661611f1d44dcff600f90553150a8623f23470426dba1cffdbc2db9a7  design_1_wrapper.xsa (T04, r03)
a3720d8c6d50ea9d4671ecc2029a4341911b350ab9b80d54066b84673c8bfa74  an5642_single_t04_r03.elf (302,004 B)
4fc101938cf5aae4ea646e219e9e55c4ebcb837f35f40b3e922f3a1e2e5e6faa  ps7_init.tcl（自 T04 XSA 解出）
```

## 命令与结果

| 步骤 | 命令 | 结果 |
|---|---|---|
| JTAG 下载 | `bash scripts/stage3_t03b/run_jtag_download_t03.sh <t04_run_dir> <t04_elf>` | 九步全 OK；`T03_DL_ALL_DONE=1`；exit 0 |
| UART 抓取 | `python scripts/stage3_t03b/read_uart.py COM4 150 <log>` | 105 B，4 条诊断行全部命中 |
| 寄存器回读 | `bash scripts/stage3_t03b/run_xsdb.sh scripts/stage3_t04/jtag_readback_t04.tcl` | 见下表 |

日志：`tmp/s3r06/t04_camera_20261020_r03/jtag_download/`（download.log、uart_t04_nocamera.log、readback_r02.log）。

## UART 原文（105 字节）

```
S3_DIAG_APP_ENTER
S3_DIAG_SENSOR_ID=0x0000
S3_DIAG_DISPLAY_START status=0
S3_DIAG_VDMA_WRITE_STARTED
```

判读：
- `APP_ENTER`：ELF 下载并运行成功；
- `SENSOR_ID=0x0000`：**未接摄像头，I2C 无应答，符合预期**（接上摄像头后应为 `0x5640`）；
- `DISPLAY_START status=0`：显示控制器 `DisplayStart()` 返回 `XST_SUCCESS`；
- `VDMA_WRITE_STARTED`：摄像头 VDMA S2MM 调用完成。

## 寄存器回读（值 + 判读）

| 寄存器 | 地址 | 值 | 判读 |
|---|---|---|---|
| 显示 VDMA MM2S CR | 0x4300_0000 | `0x00010001` | RS(bit0)=1，运行中 |
| 显示 VDMA MM2S SR | 0x4300_0004 | `0x00011000` | Halted(bit0)=0 |
| 摄像头 VDMA S2MM CR | 0x4301_0030 | `0x00018003` | RS=1、循环模式，运行中 |
| 摄像头 VDMA S2MM SR | 0x4301_0034 | `0x00010000` | Halted=0，无错误位 |
| cmos_rst | 0x4120_0000 | `0x00000001` | 传感器复位已释放 |
| v_tc CTRL / STATUS | 0x43C0_0000 / 04 | `0x03F7EF06` / `0x00013000` | 时序发生器已配置 |
| axi_dynclk CTRL / STATUS / LOCK_L | 0x43C1_0000 / 04 / 18 | `0x1` / `0x1` / `0xCFAFA401` | 像素时钟已启动并锁定 |

**口径修正记录**：首轮回读把摄像头 VDMA 的 CR/SR 读在 `+0x00/+0x04`（那是 MM2S 寄存器组），得到 0 值；VDMA 的 **S2MM 寄存器组在 `+0x30`**（CR=+0x30、SR=+0x34）。修正后读数如上。首轮错误读数与日志（`readback.log`）保留，未覆盖。

## 结论

- **已验证**：T04 bitstream 可在实物上配置；PS（DDR/时钟）初始化成功；摄像头应用运行；显示控制器启动成功；**显示与采集两个 VDMA 均处于运行状态**；诊断 UART 链路可用。
- **未验证**：摄像头识别（需实物）、HDMI 画面与显示器兼容（需实物）、撕裂/丢帧、≥30 分钟耐久。**T04 实物关口未闭合。**
- 接上摄像头与显示器后，用**同一条下载命令**重跑，预期 `S3_DIAG_SENSOR_ID=0x5640` 且显示器出现 1280×720 实时画面。

## 复现

```bash
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_jtag_download_t03.sh \
  "D:/codex-worktrees/dbdf/tmp/s3r06/t04_camera_20261020_r03" \
  "D:/codex-worktrees/dbdf/report/evidence/S3-T03/vitis_rehearsal_20261020_r01/an5642_single_t04_r03.elf"
python /d/codex-worktrees/dbdf/scripts/stage3_t03b/read_uart.py COM4 150 <新日志>
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_xsdb.sh \
  "D:\codex-worktrees\dbdf\scripts\stage3_t04\jtag_readback_t04.tcl"
```
UART 抓取必须在 `con`（应用开始运行）之前启动；应用只在启动瞬间打印一次。