# 阶段3 A9 条件恢复尝试 R02

- RunId：`t17_w1_recover_a9_20261026_r02`；基线：`f19b0c6a2b951082e8d0bdfe26e0e0f7b653e2ad`。
- 授权：Wong 允许多次尝试继续阶段3。此脚本经独立审查，只在 A9 状态精确等于 `Stopped` 时执行一次 `con`；不接受 Suspended，不读写寄存器、不暂停、复位或烧录。
- 脚本 SHA-256：`7f13b4a35e0f8ed2ed6d9f7cfcad5f0491ca7a6db5273334e94475ca8151e70b`。

## 执行结果

执行时间 2026-10-26 11:40:16–11:40:23 UTC+8，耗时 7.033 秒。XSDB 连接成功，但 A9 target 选择失败；可用列表仅有 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`。Tcl exit 2、wrapper exit 0。未查询 A9 状态，也未执行 `con`；未发生寄存器操作、CPU 暂停、复位、烧录或改线。

## 收窗

11:40:30 首次检查见本次 XSDB 启动的 `hw_server` PID 12056（Xilinx 2026.1，11:40:19 启动），3121 无监听。11:40:51 后复核时，该进程已自行退出；无 `xsdb/hw_server/vivado/vitis` 进程、无 3121 监听、无 Vivado MCP 会话。未终止其他进程。

本次仅能确认 A9 在 XSDB target tree 中不可见，不能确认 A9 最终状态或 HDMI 是否恢复。此结果不关闭阶段3 G5。
