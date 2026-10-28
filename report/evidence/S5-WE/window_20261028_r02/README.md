# S5-WE 板级窗口 window_20261028_r02（执行体 stage6-lead3）

- 授权：DSH 项目总控直接指令接管（前一执行体 stage6-lead2 在窗口开始阶段失败、无收尾、0 B 写入）；非 OFFERED 交接。
- 口径：不主张 G5、不主张 B1–B10 全部完成；未执行项一律 NOT_RUN/BLOCKED_BY_DEPLOYMENT，不用离线证据冒充板上结论。

## 步骤与真实退出码
| 步 | 内容 | 证据 | 退出码 |
|---|---|---|---|
| 0 | P0 只读门禁：3121 仅 TIME_WAIT（非 LISTENING）、无 vivado/hw_server 进程、无 index.lock | `console/00_prewindow_identity.txt` | — |
| 1 | 身份核对：ELF / XSA / XSA 内 bit / ps7_init.tcl 四项 SHA 全等 | 同上 | 0 |
| 2 | 自起 hw_server（3121 LISTENING，pid 17904） | `console/01_hw_server_start.txt` | 0 |
| 3 | 只读 JTAG 探测（connect → targets → disconnect） | `console/02_jtag_probe.txt` | 0 |
| 4 | 装载（既有流程 `scripts/stage5_t01/jtag_download_port.tcl`：PS_RESET→FPGA_PROGRAM→PS7_INIT→DOW→RUN；仅易失） | `console/03_download.txt` | 0 |
| 5 | 读回：xc7z020 / DAP 4ba00477 / A9 #0,#1 Running / mrd 0xF8007014=40000F30 | `console/04_readback.txt` | 0 |
| 6 | B9 重连/恢复：connect(16)→disconnect→connect(16)→A9 Running | `console/05_b9_reconnect.txt` | 0 |
| 7 | 收尾：停自起 hw_server、核验 3121 无 LISTENING、无残留 | `console/06_window_close.txt` | 0 |

## 判定（详见 `results_window_20261028_r02.json`）
B1 PASS｜B2 NOT_RUN｜B3–B6/B8/B10 BLOCKED_BY_DEPLOYMENT｜B7 NOT_RUN｜B9 PASS。

## 安全
未烧 QSPI；未写阶段4 候选区 `[0x12000000,0x12C08000)`（ELF 载入区间 `[0x100000,0x130ad40)`，无重叠）；未改线/ENABLE；未发独立 `stop`；`vivado-mcp-server-*` 未碰。
