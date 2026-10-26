# 阶段3 W1 A9 运行态恢复尝试

- RunId：`t17_w1_recover_a9_20261026_r01`；状态：`BLOCKED_TARGET_ENUMERATION`。
- 工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，基线 `dee446850c84d8c0186ecc85e341bc738695cc31`。
- Wong 于 2026-10-26 批准最多 5 分钟的恢复窗口：仅当 A9 状态精确为 `Stopped` 时执行一次 `con` 并核对状态；不得读写寄存器、暂停、复位或烧录。

## 前置与执行

11:21:33 UTC+8 前置复核：7 个已登记工作树均无 `index.lock`；无 `xsdb`、`hw_server`、Vivado、Vitis 进程，无 3121 监听，无 Vivado MCP 会话。PnP 仍枚举 FTDI USB Serial Converter 与 Silicon Labs COM4。恢复脚本复制到本 RunId 后 SHA-256 为 `86f336aae232ab20cb9ae3b6617a844bf78670594a0c4fcef86e8060b482a318`，见 `preflight.json`。

XSDB 执行时间为 11:22:33–11:22:40 UTC+8（7.194 秒）。连接成功，但目标列表只有 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`；精确 Cortex-A9 target 不存在。Tcl 退出码 2，批处理包装退出码 0。由于目标不可见，脚本未查询 A9 状态，也未执行 `con`。没有读取或写入寄存器、暂停 CPU、复位、烧录或改线。

## 程序偏差

本次实际复制并执行的旧恢复脚本，其条件接受 `Stopped` **或** `Stopped: (Suspended)`；Wong 对本窗口的批准只允许状态精确为 `Stopped`。因此脚本门禁宽于授权，属于程序偏差。A9 target 选择在状态查询前失败，条件分支未运行，未执行 `con`，没有发生越界的状态恢复动作。为保持执行事实可审计，原脚本和 XSDB 输出原样保留；不得复用该脚本或覆盖本 RunId。任何后续恢复须先按授权收窄脚本并取得新的明确批准。

收窗于 11:22:52 UTC+8：无 `xsdb`、`hw_server`、Vivado、Vitis 进程，无 3121 监听；Vivado MCP 无活动会话。完整输出保留于 `xsdb.stdout.txt`/`xsdb.stderr.txt`，退出码和耗时见 `wrapper_result.json`，收窗核对见 `postrun.json`。

## 当前结论与限制

前次 W1 证据记载 A9 在一次只读寄存器超时前由 Running 被停为 Suspended，超时后未执行 `con`，最终状态未确认。Wong 随后报告 HDMI 冻结或黑屏。本次恢复仍无法枚举 A9，因此**当前 A9 状态与 HDMI 是否因前次暂停而冻结仍未知**；本次没有恢复板卡运行态。该 RunId 是一次性记录，不重跑；任何后续硬件访问都需要新的具体授权。

此结果不关闭 VDMA 粘滞位根因、TIMING-17/36 与 I/O delay、task-11 完整 RTL↔网表顺序等价，也未确认当前部署身份、运行期地址或 HDMI 画面。阶段3 G5 仍未通过，不得冻结。
