# 阶段 3 只读 JTAG 枚举与 A9 状态尝试 r02

- RunId：`t17_w1_a9_enum_20261026_r02`
- 工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`。
- 源码绑定基线：`15aaca4ee7daf0f2e808f3aea4b18e5cffdff1c3`。
- 授权：Wong 批准最多 10 分钟的只读 JTAG 枚举；仅当 A9 target 可见时读取一次 `state`。禁止暂停/继续 A9、MMIO/寄存器访问、复位、烧录和改线。
- 脚本：`enumerate_a9_state.tcl`，仅执行连接、JTAG/target 枚举、条件性读取 A9 state 和断开连接。

## 执行结果

- XSDB 2026.1 连接成功；识别 Digilent JTAG-HS1（序列号 `210512180081`）、`arm_dap`（IDCODE `0x4BA00477`）与 `xc7z020`（IDCODE `0x23727093`）。
- Target tree 显示 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`，没有 A9 target。Tcl 以 `ENUM_EXIT=5` 结束，包装器退出码为 `0`。
- 因 A9 不可见，未读取 `state`；未执行 CPU 停止/继续、MMIO/寄存器访问、复位、烧录或改线。
- 执行时间：`2026-10-26T15:11:49.9525342+08:00` 至 `2026-10-26T15:11:57.4421411+08:00`；耗时约 7.49 秒。
- 收窗复查：无 Vivado/XSDB/hw_server/Vitis 进程，3121 无监听（仅有 TCP `TIME_WAIT`），`index.lock` 不存在；未终止任何进程。Windows `tasklist` 系统级查询被拒绝，当前用户进程视图及 Vivado MCP 会话查询均未见目标进程/会话。

## 结论与边界

JTAG-HS1 和 FPGA 可见，但 DAP APB 错误阻断处理器侧 target 枚举。当前 A9 运行态、HDMI 画面、部署身份、VDMA 状态及运行期地址均未确认；阶段 3 G3/G4/G5 仍未通过。本次无硬件状态变更。

原始 XSDB 输出、退出码、时间戳、前置/收尾检查及文件哈希见本目录。证据清单 `delivery_manifest.json` 的 `CHECKS_OK`（若通过）只表示包装与文件哈希有效，不代表 JTAG 目标出现或阶段验收通过。
