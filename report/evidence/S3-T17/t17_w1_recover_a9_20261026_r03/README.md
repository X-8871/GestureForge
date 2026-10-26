# 阶段3 A9 条件恢复尝试 R03

- RunId：`t17_w1_recover_a9_20261026_r03`；基线：`f19b0c6a2b951082e8d0bdfe26e0e0f7b653e2ad`。
- 授权：Wong 允许多次尝试继续阶段3。使用经独立审查的脚本，只在 A9 状态精确等于 `Stopped` 时执行一次 `con`；不接受 Suspended，不读写寄存器、不暂停、复位或烧录。
- 脚本 SHA-256：`7f13b4a35e0f8ed2ed6d9f7cfcad5f0491ca7a6db5273334e94475ca8151e70b`。

## 执行结果

执行时间 2026-10-26 11:41:45–11:41:52 UTC+8，耗时 6.998 秒。XSDB 连接成功，但 A9 target 选择失败；target tree 只有 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`。Tcl exit 2、wrapper exit 0。未查询 A9 状态、未执行 `con`，无寄存器操作、CPU 暂停、复位、烧录或改线。

## 收窗

11:41:57 检查见本次 XSDB 启动的 `hw_server` PID 11316（Xilinx 2026.1，11:41:48 启动），3121 无监听。紧接着核查时该进程已自行退出，其他 `xsdb/hw_server/vivado/vitis` 进程与 3121 监听均为 0；Vivado MCP 无活动会话。没有结束任何进程。

本次与 R02 在新 XSDB 会话中复现同一 target 枚举错误，仍不能确认 A9 最终状态或 HDMI 是否恢复；阶段3 G5 未通过。
