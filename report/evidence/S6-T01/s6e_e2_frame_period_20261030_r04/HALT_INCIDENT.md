# E2 idleprobe 窗 r04 事件：core0 无法 JTAG halt（需断电重启）

- RunId：`s6e_e2_frame_period_20261030_r04`
- 时间：2026-10-30 22:13:12–22:14:43（UTC+8）
- PL：P3q `4d6ea2ef…`（fpga_exit=0）；ELF：`s5_display_app_p3q_producer_idleprobe.elf` sha `7357c3e5…63fe`（300,812 B）

## 现象
1. ELF 装载成功（`RUN_STATE Running`），UART 只打出 8 行 banner（到 `TEST PATTERN DRAWN: bars8+border+cross` 为止），
   **60 s 内无 `VDMA: init OK`、无帧行、无 `S5DISP RESULT`** ⇒ 应用在画完测试图后卡住。
2. 收窗停核失败：`Cannot halt processor core, timeout`；
3. 事后只读复查（独立会话）：`1 APU / 2 A9#0 (Running) / 3 A9#1 (Running) / 4 xc7z020`，
   `stop` 与 `state` 均返回 **`Cannot halt processor core, timeout`**。
4. 无 APB/DAP status 错误码；属"核不响应 debug halt"状态。

## 处置
- **立即停手**：不重试 halt、不改用其它复位、不 `rst -system`、不再编程。
- 需 **整板断电重启**（断电 ≥5 s）恢复。
- 结论：本窗作废（保留证据）；E2 仍待有效 P 口径。

## 附：本窗之前 r03（FRMCNT 方法）已实测
- `VDMA CR[23:16] FRMCNT` 1500 次采样值恒为 **1**、帧沿 **0** ⇒ 与 video-sw 说法一致，**FRMCNT 在 P3q BD 下不递增**，不能用于 P。
- 同窗 UART `S5DISP frame` 斜率 = **33,364.67 µs**（≈29.97 fps 更新节拍；非 60 Hz 显示周期）。
- 结论：E2 的 60 Hz P 需 idleprobe 的 `idle_period_us`（或新增 60 Hz 计数器）。

## 待办
1. Wong 断电重启；
2. 请 video-sw 确认 22:05 版 `producer_idleprobe` ELF（`7357c3e5…`）在该 P3q 位流+当前软件环境下是否可用（本窗表现为画完测试图即卡死）；
3. 恢复后建议先做实机 E1 级只读枚举确认 DAP 正常，再重跑 E2-idleprobe（RunId r05）。