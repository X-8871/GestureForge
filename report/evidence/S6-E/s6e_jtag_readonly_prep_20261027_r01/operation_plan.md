# S6-E 只读 JTAG 拓扑扫描准备记录

- RunId：`s6e_jtag_readonly_prep_20261027_r01`
- 时间：2026-10-27 22:31（UTC+8）
- 状态：`PREPARED_NOT_RUN`。本记录只固定操作方案与离线检查；本轮未启动 `hw_server`/`xsdb`，未连接或操作板卡。
- 范围：只枚举 JTAG 线缆、链与 target；不运行模型、摄像头、交互状态机或 S6-E 真实验收用例。

## 规则适用性

Wong 已批准阶段6使用板卡；DSH 限时租用记录为 `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261027-008-board-lease-stage6.md`。本任务是独立、只读的连接拓扑诊断，不冒充 S6-E 真实推理/动作验收。因此 S6-E 的阶段4真实推理、阶段5显示契约、`P_meas`、冷启动部署身份等验收前置不构成本诊断的结果判据，也不会被本扫描置为满足。

该诊断仍须遵守板卡租用与硬件会话串行规则。实际执行前必须复核租约仍有效、没有 DSH 收回通知、确认独占窗口，并取得本诊断 scope 的正式硬件交接/CLAIM 与独立审查；当前历史 6-E 窗口申请 `NOT_REQUESTED` 不是本诊断的 CLAIM。本诊断结论不满足或替代 S6-E 的 `hardware_session_handoff` 验收门禁，也不代表 G3/G4/G5。

## 固定输入

| 输入 | 精确路径 | SHA-256 / 用途 |
|---|---|---|
| 只读 Tcl | `D:\FPGA_Competition\report\evidence\CTRL-HW-SCAN\hw_scan_20261022_r01\scan2.tcl` | `B6987E0A60F4A5A8681F2B3803E60B64B5050A228D9543C3B708CCA2E13BA046`；仅 `connect`、`targets`、`jtag targets`、`disconnect` |
| hw_server | `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe` | 执行时记录 SHA-256 |
| XSDB | `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\xsdb.exe` | 执行时记录 SHA-256 |
| 租约 | `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261027-008-board-lease-stage6.md` | 执行时复核文本并记录 SHA-256 |

## 单次执行步骤

1. 审查通过后，为实际扫描分配全新 RunId：`s6e_jtag_readonly_YYYYMMDD_rNN`；不得复用本准备 RunId 或任何历史 RunId。
2. 执行前人工重读 DSH mailbox 与租约；确认尚未收到 DSH 提前通知/收回。重新枚举 `hw_server`、`xsdb`、Vivado/Vitis 相关进程与 TCP 3121 LISTEN；任何查询失败、进程存在或端口已有 listener 均停止，不触碰外部会话。
3. 仅在诊断 scope 的 CLAIM、独占窗口与四项 CLI 确认齐备后，执行：

   ```powershell
   & 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\codex-worktrees\w6\verification\s6e_jtag_readonly_scan.py' --run-id s6e_jtag_readonly_YYYYMMDD_rNN --execute --confirm-lease-active --confirm-no-dsh-recall --confirm-exclusive-window --confirm-handoff-claimed
   ```

4. 工具只启动本次 `hw_server.exe -s tcp::3121`；确认唯一的 3121 LISTEN PID 等于本次 `Popen` PID 后，才运行 `xsdb.exe <固定 scan2.tcl>`。
5. `scan2.tcl` 输出连接、目标数量、JTAG 链及断开标记；目标数大于零、链输出存在且 XSDB 退出码为 0 才记拓扑扫描通过。该结果只证明本次连接时观察到的拓扑。
6. XSDB 退出后，只通过本次 `Popen` 句柄停止本次创建的 `hw_server`（先 terminate；等待 5 秒仍未退出才 kill 该句柄）。禁止按进程名 `taskkill`、停止其他 PID 或重试。
7. 记录命令、实际起止时刻、工具/Tcl/租约哈希、退出码、原始日志、目标输出、收尾进程与 3121 状态。收尾须确认本次进程退出、3121 无 LISTEN；否则判失败并保留现场。

## 时限与停止条件

- 单次总预算 60 秒；`hw_server` 获得 3121 最多 10 秒；XSDB 扫描最多 30 秒；只尝试一次。
- 立即停止条件：租约不明/被收回、独占失败、进程或端口冲突、路径/哈希不符、连接/目标/JTAG 输出异常、XSDB 超时/非零退出、清理或收尾核验失败。
- 异常时保留 RunId、日志、进程 PID 与现场状态，不复位、不烧录、不下载、不改接线、不读写寄存器或存储、不结束外部进程、不覆盖证据。由 Wong/DSH 确认后再决定恢复。

## 当前静态核验

- 本次只读进程检查：未见 `vivado`/`xsim`/`xsdb`/`hw_server`/`vitis` 命名进程，TCP 3121 无 LISTEN；较宽 CIM 查询受访问拒绝，因此本记录的现场快照不是开窗时实时核验。
- 既有 2026-10-22 `CTRL-HW-SCAN` 结果仅作操作参考，不证明当前板卡/线缆状态。
- 6-E 八类验收门禁并未因本准备记录或未来拓扑扫描而关闭；真实 6-E、`T6-A03`、G3/G4/G5 保持未执行或未通过。
