# 阶段3 状态（AN5642 原始视频链路）

更新：2026-10-20 01:00（UTC+8）。工作树 `D:\codex-worktrees\dbdf`／分支 `codex/stage3-video`。
规则见 `D:\FPGA_Competition\AGENTS.md`；本文件只记阶段技术事实，不复制主 STATE。

## 目标与第一版范围

- 第一版：AN5642(OV5640) → J10 扩展口 → PL 采集/DDR 缓冲 → HDMI → 显示器【原始画面直通】。先单通道。
- 不加 CNN、不加检测框、不加手势交互。路线：T01/T02 资料与接口（旧轮已完成）→ **T03 HDMI 独立画面（本轮打通）** → T04/T05 采集直通（进行中）→ T06 耐久/证据包（降级为后续可选）。

## 器件与环境（现行事实）

- 器件：**XC7Z020-2CLG400I**，Vivado part = **`xc7z020clg400-2`**。JTAG 目标名显示 `xc7z020`。
- **器件身份更正（2026-10-20 01:40，复核 Vault 板卡正面照片）**：芯片丝印为 `XA7Z020` + `CLG400ABX2117` + `DB424532A`（XA 级、后缀速度等级在照片上不可辨）。JTAG 目标名 `xc7z020` 只反映公共裸片/IDCODE，**不能区分 XC/XA**，也不能证明 `-2`。本轮按 Wong 现行事实用 `xc7z020clg400-2` 构建并在实物上成功启动；`-1` 与 `-2` 的时序签核问题仍未关闭。
- 官方源（fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327）的 14/22/23 三个工程 `create_project.tcl:39` **本来就是 `xc7z020clg400-2`**；本树历史文档里的 `xa7z020clg400-1I` 是上一轮自设偏差，已停用。
- BASIC 许可 `D:\Xilinx_licenses\basic_only.lic`（至 2027-08-07，host-locked，`TS_OK`）：**必须按进程注入** `XILINXD_LICENSE_FILE`，否则 Vivado 2026.1 启动/许可检出失败（上一轮 exit 42 的根因）。注入后 Synthesis/Implementation/bitstream 对 `xc7z020` 全部可用（已实测）。
- Vivado 2026.1 = `D:\Xilinx\2026.1\Vivado\bin\vivado`（**Tcl 模式**）；Vitis 2026.1 的 **XSCT 已禁用**（`xsct.bat` 直接报错退出），软件侧改走 HSI + make；JTAG 用 Vivado 自带 **Tcl 版 `xsdb.bat`**（Vitis 的 xsdb 是 Python 版）。
- 本机 16 GB：同时只跑一个重型综合/实现；`TEMP/TMP=D:\tmp`。

## 本轮已完成（S3-T03b）

- 官方 `14_vdma_hdmi_out` 在 `xc7z020clg400-2` 上**重建到比特流**：00:31:06→00:37:53、exit 0、`synth_1`/`impl_1` Complete；WNS=1.2925、WHS=0.0116、TNS/THS=0（时序收敛）；LUT 6.66%、FF 5.92%、BRAM 5.36%、DSP 0%、DRC 0 error；峰值内存 2488 MB。
- 产物：bitstream SHA-256 `7143427f99e25ad44b3ead13510b52dd63522f67f8f57e011214408051450d7f`；XSA `02174319ba1b6206274fc11b62c3b1d165cd7980b7695661830f7e4c3977b96c`（内含 `ps7_init.tcl`）；应用 ELF `f6686cd7e10a68ecabeedd02b0c4ebc21498f362a77d2bf35c7bc3229fe6aa9f`。
- **实物 JTAG 启动成功**：九步全 OK（CONNECT→PS_RESET→FPGA_PROGRAM→PS7_INIT→POST_CONFIG→A9 选择→DOW_ELF→RUN）。只做易失性下载，未烧 QSPI/非易失。
- **寄存器回读证据**：dynclk STATUS bit0=1（RUNNING）、LOCK_L=0x7E8FA401；VDMA CR=0x00010001（RS=1）、VDMASR=0x00011000（Halted=0）；v_tc CTRL=0x03F7EF06；帧缓冲 0x26CBC0 起为图像数据 → 显示通路已在实物上被配置并运行。
- 证据入口：`report/evidence/S3-T03/t03b_hdmi_build_20261020_r01/`（build_report.json、bringup_record.md）；运行现场 `tmp/s3r06/t03b_hdmi_20261020_r01/`；厂商工程调研 `report/evidence/S3-T01/survey_20261020_r01/vendor_project_survey.md`。

## 本轮已完成（S3-T04/T05 硬件侧）

- 官方 `22_ov5640_single`（AN5642 单通道采集→VDMA/DDR→HDMI 直通）在 `xc7z020clg400-2` 上**构建成功**（run `tmp/s3r06/t04_camera_20261020_r03`）：01:02:00→01:11:02、exit 0、synth/impl/bitstream/XSA 全出；WNS=1.1200、WHS=0.0411、TNS/THS=0；LUT 10.43%、FF 8.77%、BRAM 10.36%、IOB 18.40%、DRC 0 error；峰值内存 2564 MB。
- 产物：bitstream SHA-256 `5f6d357d57fa4b206390103ed6fcc90d5fbbca310c471ce3c956c09aa4f10738`（1,714,005 B，压缩开启）；XSA `5e0663b661611f1d44dcff600f90553150a8623f23470426dba1cffdbc2db9a7`。
- 两个必须记住的工具事实：① **BASIC 许可不支持 >5 probes 的 ILA**（`Chipscope 16-620`），厂商 `alinx_ov5640` IP 的 `DEBUG_OV5640` 默认 true 会内嵌 ila_0，必须在 BD 上设 `CONFIG.DEBUG_OV5640=false`；② OOC 子 run 偶发启动期 `ERROR [Common 17-354] Could not open 'C' for writing` + `tclapp::load_apps` failed（非 IP 专属，r01/r03 各命中 2 个 run），**reset_run + 重新 launch_runs 重试可通过**，根因未定位。
- 外设基址（软件侧必须用 T04 自己的 XSA 生成 BSP）：显示 `axi_vdma_0` 0x4300_0000、摄像头 `axi_vdma_1` 0x4301_0000、`cmos_rst` 0x4120_0000、`v_tc` 0x43C0_0000、`axi_dynclk` 0x43C1_0000；显示模式 `VMODE_1280x720`（固定，不读 EDID）；显示与采集共用同一帧缓冲（官方例程口径，快速运动可能撕裂）。
- 应用诊断补丁 `board/stage3/software/sensor/s3_t04_app_diag.patch`（4 条 S3_DIAG UART 打印，已验证可干净应用）；UART 抓取 `scripts/stage3_t03b/read_uart.py`（COM4@115200）；板测步骤 `board/stage3/board_test_runbook.md`。
- 证据入口：`report/evidence/S3-T04/t04_camera_build_20261020_r03/build_report.json`。
- **无摄像头板卡预测试已通过**（2026-10-20 01:2x，无显示器/无摄像头）：T04 bitstream + 摄像头 ELF 经 JTAG 下载运行，UART 输出 `S3_DIAG_APP_ENTER` / `SENSOR_ID=0x0000`（未接摄像头，I2C 无应答，符合预期）/ `DISPLAY_START status=0`（成功）/ `VDMA_WRITE_STARTED`；寄存器回读两个 VDMA 均运行（显示 MM2S CR=0x00010001、SR Halted=0；摄像头 S2MM CR=0x43010030=`0x00018003`、SR Halted=0），dynclk RUNNING/LOCK=0xCFAFA401。记录 `report/evidence/S3-T04/t04_camera_build_20261020_r03/board_pretest_record.md`。
- **口径坑**：VDMA 的 **S2MM 寄存器组在 +0x30**（CR=+0x30、SR=+0x34），MM2S 才在 +0x00；首轮回读因偏移错误得到 0，已修正并保留错误日志。
- 软件侧交付（由 Developer 产出）：可重放脚本 `scripts/stage3_t04_vitis/run_stage3_vitis_elf.cmd`（参数 = XSA / 输出目录 / 应用源码 / [ELF 名] / [补丁]）；T03 ELF 与 T04 摄像头 ELF（`an5642_single_t04_r03.elf`，302,004 B，SHA-256 `a3720d8c6d50ea9d4671ecc2029a4341911b350ab9b80d54066b84673c8bfa74`）、报告在 `report/evidence/S3-T03/vitis_rehearsal_20261020_r01/`。Vitis 2026.1 入口 = `sdtgen`（仍加载完整 HSI：`hsi::open_hw_design`→`create_sw_design`→`generate_bsp`/`generate_app`）+ `make`；Unified 平台不可用的根因是 XSA 的 `xsa.xml` 无处理器节点。

## 可复用命令（Git Bash）

```bash
bash scripts/stage3_t03b/run_t03b_hdmi_build.sh <新run名>        # 构建 HDMI-only 到比特流+XSA
bash scripts/stage3_t04/run_t04_camera_build.sh  <新run名>       # 构建摄像头直通（22_ov5640_single）
bash scripts/stage3_t03b/run_jtag_download_t03.sh <run_dir> <elf> # JTAG 下载 bit+PS初始化+ELF
bash scripts/stage3_t03b/run_xsdb.sh <脚本.tcl>                   # JTAG/寄存器只读回读
```
运行目录必须不存在（脚本拒绝覆盖）；重跑一律用新 RunId，不覆盖旧证据。

## 未提交改动归属（接手声明，不覆盖不回退）

- 上一轮（2026-10-03~07）9 项未提交改动**由本轮阶段3总控接手**：`.codex/STATE.md`（本文件，本轮覆盖更新）、`board/stage3/README.md`、`board/stage3/prepower_check.md`、`board/stage3/hardware_photo_evidence.md`、`scripts/s3_implement_hdmi_only_diag.tcl`、`docs/adr/ADR-0002-stage3-gitbash-runner.md`、`scripts/stage3_t03/**`（旧 .NET 守卫+Git Bash runner，仅历史/对照，**不是**本轮活动入口）。
- 不提交的散落文件：`NA/ps7_summary.html`、`clockInfo.txt`（Vivado 时钟调试输出，非证据、非代码），保留在工作区不动。

## 未关闭的阻碍与风险

- **T03 实物关口未闭合**：Wong 2026-10-20 明确“没接显示器”，HDMI 物理画面/EDID/显示器兼容未验证；不得记为 T03 实物通过。
- `CRITICAL WARNING [Timing 38-249]`：`rgb2dvi_0/U0/SerialClk` 生成时钟与 `axi_dynclk_0_PXL_CLK_O` 无逻辑路径（厂商原 XDC 未声明 PixelClk→SerialClk ×5 关系）。DRC 0 error、时序为正，但不等价于完整 I/O 时序签核。
- 旧 `scripts/s3_implement_hdmi_only_diag.tcl` 链路锁定 XA/-1I 且不产出比特流，**不得**作为活动构建入口复用。
- 软件侧 ELF 流程（HSI + make）尚需封装为可重放脚本；T04 应用必须用 T04 的 XSA 重新生成 BSP（外设地址/ID 不同）。**T04 摄像头应用 ELF 尚未产出**，这是第一版上板的最后一块。
- 厂商缓存 `tmp/stage3_reference/AX7020_2023.1` 出现 7 个未跟踪新增文件（`14_vdma_hdmi_out/Vitis/` 下的 design_1_wrapper.bit 与 ps7_init.*，2026-10-20 00:38:08，软件侧 HSI 解包所致）：已跟踪源文件未被修改、未被删除；已在 T04 证据中声明归属，后续解包一律放 `tmp/s3r06/`。
- T04 未上板：摄像头与显示器未接，实物画面未验证。
- 与 2B 的硬件互斥：2B 名义持有 hw_server/JTAG/COM4；本轮开工时无 hw_server 运行，已发跨方请求 `report/evidence/CTRL-DSH-HANDOFF/codex_mailbox/CDX-20261020-003-stage3-jtag-com4-request.md`，未收到回执前不再假设独占。

## 下一步

- T04/T05：官方 `22_ov5640_single` 构建（进行中，run `tmp/s3r06/t04_camera_20261020_r01`）→ 摄像头应用 ELF → Wong 接显示器+摄像头后做直通实物确认。
- 恢复入口：`git -C D:/codex-worktrees/dbdf status --short`；`bash scripts/stage3_t03b/run_xsdb.sh scripts/stage3_t03b/jtag_readback_t03.tcl`。
- 实物操作一律给出精确步骤/预期/异常停止点，由 Wong 执行或明确授权；不烧 QSPI、不动厂商原件。