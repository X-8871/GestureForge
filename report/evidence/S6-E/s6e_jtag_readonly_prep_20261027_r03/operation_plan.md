# S6-E 只读 JTAG 拓扑扫描准备记录

- RunId：`s6e_jtag_readonly_prep_20261027_r03`
- 时间：2026-10-27 22:40（UTC+8）
- 状态：`PREPARED_NOT_RUN`。本轮只准备受控方案、核对静态输入并运行离线模拟测试；未启动 `hw_server`/`xsdb`，未连接或操作板卡。
- 范围与诊断 scope：`S6E_JTAG_READONLY_DIAGNOSTIC`，只枚举 JTAG 线缆、链与 target；不运行模型、摄像头、交互状态机或 S6-E 真实验收用例。
- r01、r02 准备轮保留原样；r03 是当前候审版本。

## 规则适用性

Wong 已批准阶段6使用板卡；限时租用依据为 `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261027-008-board-lease-stage6.md`（SHA-256 `519566fb79202689223e0cd52409b04c072b4cc31ca58270605a104102be88cb`）。本任务是独立、只读的连接拓扑诊断，不冒充 S6-E 真实推理/动作验收。因此 S6-E 的阶段4真实推理、阶段5显示契约、`P_meas`、冷启动部署身份等验收前置不构成本诊断的结果判据，也不会被本扫描置为满足。

该诊断仍须遵守租用与硬件会话串行规则。实际执行前必须复核租约仍有效、没有 DSH 收回通知、确认独占窗口，创建本诊断 scope 的正式硬件交接/CLAIM，并完成独立代码审查。本诊断结论不满足或替代 S6-E 的 `hardware_session_handoff` 验收门禁，也不代表 G3/G4/G5。

执行器的 `--confirm-command-review-pass` 只是防误启动的人工开关，不是独立审查证据。总控必须核验 reviewer PASS、被审源码 SHA/提交与执行源码一致后，才可提供该确认；不得只凭 CLI 开关判为已审。

## 固定输入

| 输入 | 精确路径 | SHA-256 / 用途 |
|---|---|---|
| 只读 Tcl | `D:\FPGA_Competition\report\evidence\CTRL-HW-SCAN\hw_scan_20261022_r01\scan2.tcl` | `b6987e0a60f4a5a8681f2b3803e60b64b5050a228d9543c3b708cca2e13ba046`；内容只做 `connect`、`targets`、`jtag targets`、`disconnect` |
| hw_server | `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe` | `e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3` |
| XSDB | `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\xsdb.exe` | `664dc93eb6cec40a2596162dbdf9bc42d5ab96ffbfc34d7515f8c68072fbac55` |
| 租约 | `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261027-008-board-lease-stage6.md` | `519566fb79202689223e0cd52409b04c072b4cc31ca58270605a104102be88cb` |

执行器每次开窗仍会重算上述输入哈希；任何输入改变均停止并要求新审查/新 RunId。

## 单次执行步骤

1. 独立审查通过后，为实际扫描分配全新 RunId：`s6e_jtag_readonly_YYYYMMDD_rNN`；不得复用 r01/r02/r03 准备 RunId 或任何历史 RunId。
2. 执行前人工重读 DSH mailbox 与租约；确认未收到 DSH 提前通知/收回。重新枚举 `hw_server`、`xsdb`、Vivado/Vitis 相关进程与 TCP 3121 LISTEN；任何查询失败、进程存在或端口已有 listener 均停止，不触碰外部会话。
3. 总控核验本诊断 scope 的 CLAIM、独占窗口和 reviewer 对应的提交/源码哈希。随后才可由操作人显式提供五项确认并执行：

   ```powershell
   & 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\codex-worktrees\w6\verification\s6e_jtag_readonly_scan.py' --run-id s6e_jtag_readonly_YYYYMMDD_rNN --execute --confirm-lease-active --confirm-no-dsh-recall --confirm-exclusive-window --confirm-handoff-claimed --confirm-command-review-pass
   ```

4. 工具只启动本次 `hw_server.exe -s tcp::3121`；确认唯一的 3121 LISTEN PID 等于本次 `Popen` PID 后，才运行固定 `xsdb.exe <scan2.tcl>`。
5. 目标数大于零、JTAG 链输出存在且 XSDB 退出码为 0 才记拓扑扫描通过；该结果只证明本次连接时观察到的拓扑，不判定板卡型号/速度级/工程部署身份。
6. XSDB 退出后，只通过本次 `Popen` 句柄停止本次创建的 `hw_server`（先 terminate；等待 5 秒仍未退出才 kill 该句柄）。禁止按进程名 `taskkill`、停止其他 PID 或重试。
7. 保存命令、实际起止时刻、源码提交/脚本哈希、工具/Tcl/租约哈希、退出码、原始日志、目标输出、收尾进程与 3121 状态。收尾须确认本次进程退出、3121 无 LISTEN；否则判失败并保留现场。

`scan2.tcl` 的 `disconnect` 由 Tcl `catch` 包裹，输出标记只证明流程走到断开语句；收尾还须依 XSDB 退出、本次 `hw_server` 停止、相关进程无残留及 3121 无 LISTEN 共同判断资源释放。

## 时限与停止条件

- 单次总预算 60 秒；服务器取得 3121 最多 10 秒；XSDB 扫描最多 30 秒；只尝试一次。总预算在启动前、各阶段和收尾均检查。
- 立即停止条件：租约不明/被收回、独占失败、进程或端口冲突、路径/哈希不符、正式交接/CLAIM 或审查未确认、连接/目标/JTAG 输出异常、XSDB 超时/非零退出、清理或收尾核验失败。
- 异常时保留 RunId、日志、进程 PID 与现场状态；不复位、不烧录、不下载、不改接线、不读写寄存器或存储、不结束外部进程、不覆盖证据。由 Wong/DSH 确认后再决定恢复。

## 当前静态核验与离线测试

- 2026-10-27 22:31 UTC+8 只读进程检查：未见 `vivado`/`xsim`/`xsdb`/`hw_server`/`vitis` 命名进程，TCP 3121 无 LISTEN；较宽 CIM 查询受访问拒绝，因此该现场快照不是开窗时实时核验。
- 既有 2026-10-22 `CTRL-HW-SCAN` 结果仅作操作参考，不证明当前板卡/线缆状态。
- `python -B -m unittest -v test_s6e_jtag_readonly_scan`：13 项离线回归通过，包含默认不执行、缺少 CLAIM/审查确认、占用拦截、输出判定、仅本次句柄清理及 mock 端到端命令次序；没有真实工具调用。
- 6-E 八类验收门禁未因本准备记录或未来拓扑扫描而关闭；真实 6-E、`T6-A03`、G3/G4/G5 保持未执行或未通过。
