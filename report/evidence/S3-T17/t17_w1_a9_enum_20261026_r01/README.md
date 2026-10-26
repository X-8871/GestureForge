# 阶段 3 只读 JTAG 枚举与 A9 状态尝试 r01

- RunId：`t17_w1_a9_enum_20261026_r01`
- 工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`；检查基线 `110ddf1b5b3c2e2087afb7260a031a042a393a2c`。
- 授权：Wong 批准新的 10 分钟只读窗口；范围为重查锁/进程/资源、枚举 JTAG targets、仅在 A9 target 出现时读取一次 `state`。禁止暂停/继续 A9、MMIO/寄存器访问、复位、烧录和改线。
- 脚本：`enumerate_a9_state.tcl`，仅包含 `connect`、JTAG/target 枚举、精确选择 A9、读取 `state`、`disconnect`；不含 `con`、`stop`、`mrd`、`mwr`、`rst` 或编程命令。

## 执行结果

- XSDB 2026.1 连接成功；识别 Digilent JTAG-HS1（序列 `210512180081`）、`arm_dap` IDCODE `0x4BA00477`、`xc7z020` IDCODE `0x23727093`。
- XSDB target tree 为 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`；没有 A9 target。Tcl 以 `ENUM_EXIT=5` 收束，XSDB wrapper 退出码 0。
- 因 A9 target 不存在，未读取 `state`，未执行 `con`，未访问寄存器/MMIO，未暂停 CPU、复位、烧录或改线。
- 脚本开始时刻未单独捕获；执行器返回墙钟耗时 10.8 秒。后续收窗检查于 2026-10-26 14:14:02 +08:00 确认 Vivado/XSDB/hw_server/Vitis 进程均为 0、3121 无监听。该次 XSDB 创建的 hw_server 在随后检查前自行退出；未终止任何进程。
- 开窗前 `index.lock` 不存在；内存查询与 Windows PnP 查询均被系统拒绝。连接后直接识别到 JTAG-HS1/FPGA IDCODE，因此没有进一步启动服务或尝试修改设备。

## 结论与边界

这次只读枚举确认 JTAG 链路可见 FPGA，但 DAP APB 错误阻止 A9 target 出现。A9 当前运行态、HDMI 画面、部署身份、VDMA 状态及运行期地址仍未确认；阶段 3 G3/G4/G5 未通过。本次没有改变工作树、板卡或已部署位流。

原始输出保留在 `xsdb_wrapper.stdout.txt`、`xsdb_wrapper.stderr.txt` 和 `wrapper_exit_code.txt`；前置核验、执行摘要、收窗核验及文件哈希见同目录 JSON。
