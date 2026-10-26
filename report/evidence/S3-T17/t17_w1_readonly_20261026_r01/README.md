# 阶段3 W1 只读回读结果

- RunId：`t17_w1_readonly_20261026_r01`
- 工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，基线 `358034df5f3f75c2d851ebe76b4558b57fd7f39a`
- 范围：复用 Wong 2026-10-25 批准的 W1 只读范围；本轮仅核对 JTAG 链/A9 状态和 VDMA 只读寄存器，不写寄存器、不复位、不烧录。
- 前置：四树无 `index.lock`，没有其他 `xsdb`、`hw_server`、Vivado/Vitis 会话或 3121 监听；Windows 枚举到 FTDI USB 设备 `210512180081` 与 COM4。
- 结果：XSDB 确认 Digilent JTAG-HS1、`arm_dap`、`xc7z020`（IDCODE `0x23727093`）；A9 起始状态 `Running`，`stop` 后读为 `Stopped: (Suspended)`。首个寄存器 `S2MM_SR@0x43010034` 读取超时，探测 exit 2；XSDB wrapper exit 0。脚本未读运行期地址，未执行 `con`、复位、写寄存器或烧录。
- 收窗：随后确认无 `xsdb`/`hw_server` 进程与 3121 监听。错误后 XSDB 状态不再满足 halted 匹配条件，但脚本没有打印返回状态值，因此 A9 最终执行状态未确认。部署身份、现场真彩确认、VDMA 状态和运行期地址均未闭合。
- 判定：`BLOCKED_READBACK_TIMEOUT`。本包不表示阶段3 G3/G4/G5 通过，也不关闭 VDMA 根因。

失败输出和脚本原样保留；若后续重试，必须使用新 RunId。
