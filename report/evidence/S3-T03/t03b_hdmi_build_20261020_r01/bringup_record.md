# S3-T03b 板卡启动记录（2026-10-20，UTC+8）

任务：官方 `14_vdma_hdmi_out` 在现行器件 `xc7z020clg400-2` 上重建到比特流，并经 JTAG 在 AX7020 实物上启动。

## 授权与实物前提

- Wong 2026-10-20 00:3x（UTC+8）直接指示继续阶段3，并说明：已插电、状态为 JTAG、已接电源与 UART。
- 实物操作范围：只做**易失性** JTAG 下载（PL bitstream + PS 初始化 + ELF 到 DDR）；**未**烧写 QSPI/非易失，**未**改动任何跳线或接线。
- Wong 明确回复当前“没接显示器”，因此本记录不包含任何显示器画面结论。

## 步骤与结果

| 步骤 | 命令/脚本 | 结果 |
|---|---|---|
| 许可探测 | `scripts/s3_run_license_probe.sh license_probe_20261020_r02 xc7z020clg400-2` | exit 0；BASIC 许可检出（至 2027-08-07）；synth/impl/bitstream 全通过；峰值内存 2235 MB |
| 工程构建 | `bash scripts/stage3_t03b/run_t03b_hdmi_build.sh t03b_hdmi_20261020_r01` | exit 0；00:31:06→00:37:53；`synth_1`/`impl_1` 均 Complete；WNS=1.2925、WHS=0.0116、TNS/THS=0 |
| JTAG 链路探测 | `bash scripts/stage3_t03b/run_xsdb.sh jtag_probe.tcl` | exit 0；目标 `APU`、`ARM Cortex-A9 MPCore #0/#1`、**`xc7z020`** |
| JTAG 下载 | `bash scripts/stage3_t03b/run_jtag_download_t03.sh <run_dir> <elf>` | 九步全 OK（CONNECT→PS_RESET→FPGA_PROGRAM→PS7_INIT→POST_CONFIG→A9_SELECT→DOW_ELF→RUN） |
| 板上回读 | `bash scripts/stage3_t03b/run_xsdb.sh jtag_readback_t03.tcl` | dynclk STATUS bit0=1(RUNNING)、LOCK_L=0x7E8FA401；VDMA CR=0x00010001(RS=1)、VDMASR=0x00011000(Halted=0)；v_tc CTRL=0x03F7EF06；帧缓冲 0x26CBC0 起为图像数据 |

## 输入哈希（下载时核对）

```
7143427f99e25ad44b3ead13510b52dd63522f67f8f57e011214408051450d7f  design_1_wrapper.bit
02174319ba1b6206274fc11b62c3b1d165cd7980b7695661830f7e4c3977b96c  design_1_wrapper.xsa
f6686cd7e10a68ecabeedd02b0c4ebc21498f362a77d2bf35c7bc3229fe6aa9f  vdma_hdmi.elf
ac98ab1a6567897fc8dd2329acf9e78e3f25b378878bd690c8265c9bf2ddb01b  ps7_init.tcl（自 XSA 解出）
```

## 结论与边界

- **已验证**：许可链路、工程可重建、时序收敛、bitstream/XSA 生成、JTAG 可下载、PS 初始化成功、应用在实物上运行并配置显示通路（dynclk 锁定 + VDMA 运行 + v_tc 已编程 + 帧缓冲有数据）。
- **未验证**：HDMI 物理信号与显示器画面（无显示器）、EDID/模式兼容、≥30 分钟耐久、丢帧口径。因此 **T03 实物关口（G3）未闭合**。
- 已知遗留：`Timing 38-249`（`rgb2dvi` 的 `SerialClk` 生成时钟与 `axi_dynclk_0_PXL_CLK_O` 无逻辑路径）为约束建模告警；DRC 0 error。

## 复现命令（Git Bash）

```bash
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_t03b_hdmi_build.sh t03b_hdmi_20261020_r02
bash /d/codex-worktrees/dbdf/scripts/stage3_t03b/run_jtag_download_t03.sh \
  "D:/codex-worktrees/dbdf/tmp/s3r06/t03b_hdmi_20261020_r02" \
  "D:/codex-worktrees/dbdf/tmp/s3r06/<elf_run>/vdma_hdmi.elf"
```
注意：`run_dir` 必须不存在（脚本拒绝覆盖既有运行目录）；正式重跑请使用新 RunId。