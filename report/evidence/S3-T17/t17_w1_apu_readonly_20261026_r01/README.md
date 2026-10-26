# 阶段3 W1 APU 只读回读候选方案

- 候选 RunId：`t17_w1_apu_readonly_20261026_r01`
- 状态：`EXECUTED_BLOCKED_DAP_APB_ERROR`
- 拟申请窗口：最多 15 分钟，包含前置核验、一次主读回、必要时一次条件式恢复及收窗核验。
- 适用工作树：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`
- 目的：尝试用 APU/AXI-AP 读取 VDMA 状态和运行期地址，替代已超时的 Cortex-A9 处理器指令式读取。

## 方法依据与边界

AMD UG1725 说明：活动目标选为处理器时，`mrd` 由处理器执行调试器注入的 load 指令；而 APU/RPU/PSU 等非处理器目标通过 Arm DAP 中的 AXI-AP 访问物理内存。AMD 同一指南说明 Zynq 的 APU target 可访问 Arm DAP/MEM-AP 地址空间。参考：[mrd](https://docs.amd.com/r/en-US/ug1725-xsdb-reference-guide/mrd)、[Non-processor Targets](https://docs.amd.com/r/en-US/ug1725-xsdb-reference-guide/Non-processor-Targets)、[targets](https://docs.amd.com/r/en-US/ug1725-xsdb-reference-guide/targets)。

这是对前次 timeout 的**新路径假设**，尚未在此板验证，不能称其必然可用。AMD 文档指出 APU memory access 会执行 cache flush/invalidate；候选脚本不直接读写 DDR 地址，但工具的缓存维护可能影响系统内存/运行时延，须在新的明确硬件批准下使用。候选脚本不写寄存器、不烧录、不复位、不改线；先检查 A9 状态严格等于 `Running`，再由脚本短暂停止、确认状态严格为 `Stopped` 或 `Stopped: (Suspended)` 后切换至唯一精确名称 `APU` 的 target 读寄存器，最后只在状态严格匹配停止白名单时执行 `con` 并确认恢复为 `Running`。任何 target 不匹配、非运行初态、读回超时或状态不确定均停止后续读取；读回失败只用新 RunId 记录，不重试。若 stop 尝试后无法重选 A9/读取状态，处理器可能仍停止或状态不明；脚本会显式写出 `W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1`，不得自行复位，须先取得新的恢复授权。

**进程异常风险**：若 XSDB/连接在 A9 暂停期间被外部终止，Tcl 清理段可能不运行，A9 可能留在停止态且不会产生恢复标记。经新批准窗口执行时，如发生这种情况，先核验旧 `xsdb/hw_server` 进程及 3121 监听归属；旧会话仍在则不另起会话。确认没有遗留会话后，才可在同一已批准窗口运行 `recover_a9_if_confirmed_halted.tcl` 一次：它只查询状态，精确为 `Stopped` 或 `Stopped: (Suspended)` 才执行 `con`；精确 `Running` 不动作；其他结果不猜测、不复位，停止并报告。恢复脚本失败后不再试第二次。

## 候选读取顺序

1. 新窗口前重新检查四树 `index.lock`、硬件进程、3121 监听、PnP/JTAG；先记录目标树及 A9 状态。若旧 XSDB/hw_server 会话或 3121 监听仍在，不启动新会话。
2. 仅当 A9 确认 `Running`，才执行一次 `stop` 并确认 `Stopped`。
3. 选择唯一 `name == APU` 的目标；若无/多于一个，跳过读取，按脚本逻辑尝试安全恢复 A9。
4. 在 APU target 上依次只读 `S2MM_SR 0x43010034`、`ADDR_S2MM 0x430100AC`、`ADDR_MM2S 0x4300005C`。首个访问错误即中止剩余寄存器；不使用 `-force`。
5. 重新选择 A9，仅当 `state` 精确等于 `Stopped` 或 `Stopped: (Suspended)` 时执行 `con`，并核实恢复为精确值 `Running`；精确为 `Running` 则不动作；其他状态均不猜测、不复位，写恢复授权提示并停止。
6. 现场目视仅由 Wong 确认；任务端不得声称已观看 HDMI。收窗后复查无残留 `xsdb/hw_server` 与 3121 监听。

若主脚本起始状态不是 `Running`（包括前次运行遗留的可能停机状态），主脚本会在读寄存器前退出。仅在 Wong 的新批准明确包含条件式恢复时，且确认没有旧 XSDB/hw_server/3121 会话后，才可对同一 RunId 执行恢复脚本一次；它会先独立查询状态，只有精确 stopped 白名单才 `con`。无授权或恢复脚本仍失败时，不采取其他硬件动作。

## 启动命令（仅获新批准后）

在 `D:\codex-worktrees\dbdf` 启动 XSDB 2026.1 并执行主脚本：

```powershell
& 'D:\Xilinx\2026.1\Vivado\bin\xsdb.bat' 'D:\codex-worktrees\dbdf\report\evidence\S3-T17\t17_w1_apu_readonly_20261026_r01\apu_target_readback.tcl'
```

保存主读回与必要时恢复脚本各自的原始 stdout/stderr、准确退出码、执行前后资源检查和现场目视确认。不得将启动脚本的包装退出码覆盖 Tcl 脚本退出码。恢复脚本只有在 Wong 的新批准明确包含该条件式恢复、主脚本起始为非运行状态或发生进程异常、且无旧硬件会话时才运行，最多一次。

即便本路径读回通过，也只补充阶段3 W1/G3 证据，不会单独冻结阶段3：VDMA 根因、TIMING-17/36 与 C2/I/O delay、完整 task-11 RTL↔网表顺序等价仍是独立未关闭项。

## 本次运行结果（2026-10-26）

- Wong 批准了本 RunId 最多 15 分钟的窗口与一次条件式恢复；用户报告当前 HDMI 为冻结或黑屏。
- 主脚本开始于 `2026-10-26 11:05:49 UTC+8`。JTAG 链识别 Digilent JTAG-HS1、`arm_dap`、`xc7z020`（IDCODE `0x23727093`）；XSDB target tree 只有 `DAP (APB AP transaction error, DAP status 0x30000021)` 与 `xc7z020`，未发现 Cortex-A9 或 APU target。主脚本在 target 选择处退出，Tcl exit 2、XSDB wrapper exit 0；没有执行 stop、mrd、con、寄存器写入、复位或烧录。
- 条件恢复脚本开始于 `2026-10-26 11:06:57 UTC+8`，同样因 A9 target 不存在而退出；恢复脚本 exit 2、XSDB wrapper exit 0，没有执行 `con`。
- 收窗复核于 `11:08:05 UTC+8`：无 `xsdb/hw_server/vivado/vitis` 进程、无 3121 监听、无 Vivado MCP 会话。两个 `hw_server` 均由本次 XSDB 启动，并在收窗核验前自行退出；未终止其他进程。
- 本 RunId 未读到 VDMA 状态或运行期地址，未核实部署身份、A9 最终状态或 HDMI 画面；Wong 报告冻结/黑屏，任务端未直接观察。状态为 `BLOCKED_TARGET_ENUMERATION`，禁止复用本 RunId 重试。
