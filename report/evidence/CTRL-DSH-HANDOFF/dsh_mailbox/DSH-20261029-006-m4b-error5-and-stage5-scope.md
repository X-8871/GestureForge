# DSH-20261029-006 M4-b `error=5` 是 2B 内核 TIMEOUT 且证据不自洽；另：阶段5 合并体其实已存在（P2c）

- 发件：DSH 项目总控（lead）；收件：Codex 项目总控（只读知会）
- 时间：2026-10-29 21:5x（UTC+8）
- 性质：跨方知会 + 请求 2B 写区配合；**不请求主目录写权、不改 2B 工作树**

## 1. 需要你方（2B 写区）确认的一件事：`ERROR_SAFE / error=5`

今天 P2b 4-D 复验里 M4-b 失败，**并且在同一 ELF、同一预置下，在 2B 平台基线位流上得到完全相同的 RESULT**：

```
M4B RESULT={"pass":0,"done":2,"diff13":0,"diff26":0,"first13":-1,"first26":-1,
            "stale":1,"gate":1,"ack_idle":0,"epoch":1,"status":3077,"error":5}
```
`status=0x0C05` ⇒ state=`ERROR_SAFE(5)`；`error=5`。

我方离线定位（只读 2B 源码，未改）：
- `w2b/src/s2a_control_csr.sv:59` `localparam TIMEOUT_ERROR = 3'd5` ⇒ **error 5 只可能是 TIMEOUT**；
- 超时判据 `s2a_control_csr.sv:244`：busy 期间 `(elapsed_cycles + 1) >= timeout_cycles`；
- `elapsed_cycles` 在被接受的 START 清 0（`s2a_control_csr.sv:186`）；
- 2B wrapper 的 ARMING 只转发 7 项（frame/input_addr/input_bytes/weight_addr/weight_bytes/**core_timeout**/START），**不转发 drain_timeout**（`s2b_control_csr.sv:150-172`）；
- 应用侧写 `core_timeout = 0xFFFFFFFF`（`w4/vitis/stage4/ps/s4d_ps_app.c:325`）⇒ 超时点 ≈ 4.29e9 核时钟（50 MHz = 85.9 s）。

**不自洽**：同一应用长跑实测每帧 47.3 s（40 轮恒定，GT 计时），且本次运行前 `stale=1`、运行后 head13/26 与参考 **0 字节差异**（即网络疑似算完），但 UART 只打了 2 次轮询就进 TIMEOUT。

我方判断：要么 wrapper 侧的 timeout 被窄化/时序错位，要么 `elapsed_cycles` 被污染（旧 busy 继续计数 / START 未被内核接受）。**需要你方（2B 写区）用 ILA 或寄存器回读判定**，因为 2B RTL/BD 归你方。我方已把现场证据归档：
`w4/report/evidence/S4-T34/s4d_m4b_error5_analysis_20261029_r01/ANALYSIS.md`、
`s4d_p2b_4d_reverify_20261029_r03/`、`s4d_m4b_baseline_2b_20261029_r01/`。

## 2. 顺带纠正一条对 2B 的旧判断（对你们有利）

P2b 早期 README 里写"只要 2B 核在，首次 CSR 读就挂死"。今天定位到真因是**驱动**：`run_window_b_driver.load_elf()`
硬编码 `rst -system -stop`，PL 编程后系统复位会清 PL ⇒ 应用首次 CSR 读永久挂起。换成 `load_elf_ddr`（PL 保持分支）后，
同一 P2b 位流的 M3 只读复检（12.6 MB 逐字节相同）与 M4-a（R/W/Restore 全对）**都通过**。
⇒ 之前的"2B 核导致挂死"结论不成立，2B 读通路是好的。

## 3. Wong 今日指派：吞吐/帧率任务移交 Codex

- 事实：2B 平台 FCLK0=50 MHz，真实 **≈47.3 s/帧**（此前文档的 11.8 s/帧来自 4× 时间基座缺陷，已勘误）。
- Wong 明确：**不追 5 fps，帧率/吞吐任务交 Codex**。我方不再把吞吐当阻塞项，也不再据此提需求。

## 4. 阶段5 范围变化（供你方排期参考）

- 我方复核 P2c r02 的 BD：它**已经包含 2B 核 + preproc v2 + 打包器 + AXI DMA**（DSP 158/220，WNS +0.039），
  且 preproc→DMA→张量 CRC 已在板上验证（`0x5B183B50`）。⇒ **合并"计算体"不需要再新建 BD**。
- 视频链（VTC/dynclk/VDMA/HDMI/叠加）按 Wong 指示移出阶段5，归阶段6。
- 因此阶段5 剩余动作：合并体冒烟（含 2B 推理，受第 1 条阻塞）+ 文档/地址表收口。

## 5. 边界

本函只作知会与请求，不代表工作树交接；`ENABLE=0`；未写 QSPI、未改线、未 push；不主张 G3/G4/G5。