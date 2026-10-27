# S6-E 只读 JTAG 扫描协调器 r06 准备记录

- RunId：`s6e_jtag_readonly_prep_20261027_r06`（准备证据，不是硬件执行 RunId）
- 记录时间：2026-10-28（UTC+8）
- 状态：`PREPARED_NOT_RUN`。本轮只修改协调器/离线测试并检查信箱文本；未启动 `hw_server`/`xsdb`，未连接、读取或操作板卡。
- 工作树基线：`D:\codex-worktrees\w6` / `stage6-interact-prep` / `d04258fd0e88c220e3678950def82de192922f09`；封包时必须复核实际 HEAD。
- r04/r05 旧准备包保留原样；本轮不创建 PASS 回执、不产生任何上板结论。

## 本轮修复及审查边界

1. 执行器预期 Reviewer 回执路径固定为本 r06 包内的 `reviewer_receipt.json`；回执仍缺失，只有独立 Reviewer 实际 PASS 后由总控据实生成。
2. unittest 摘要接受合法 `Ran 0 tests ... / OK` 文本；JSON Schema 对 `tests_run` 允许零。此行为仅避免解析层误拒绝格式，不把空测试视为本项目验证通过。
3. 增加真实临时 Git 仓库负测：11 字段合法 `CLAIMED` 行仅存在于 w6 工作树、未进入 HEAD 时，正式核验必须拒绝。
4. 召回检测覆盖正文中的暂停/归还语义。无阶段标签的通用板卡归还或暂停通知也按召回处理；晚于/同刻释放的未知阶段6板卡通知 fail-closed。明确仅阶段5且具有可信 UTC+8 事件时间、并早于阶段6最近已知租约事件的记录仅标作 `OUT_OF_SCOPE_STAGE5_PRE_RELEASE`，保留路径、SHA、时刻供复核。
5. 对 `DSH-20261027-001-stage5-hardware-window-and-physical-authorization.md` 的只读核对：记录正文限定 S5-T02/阶段5，收件方虽列 Codex 项目总控但不是阶段6交接请求；该文件未跟踪，不能用 Git commit 日期排序。正文写明 UTC+8 窗口 2026-10-27 12:26–12:40，早于 DSH-008 阶段6租用 22:10 与 DSH-010 明确释放 23:00，故仅作为阶段5较早事件记录，不覆写阶段6租用。

## 固定离线验证

工作目录：`D:\codex-worktrees\w6\verification`

执行命令 argv：

```text
C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
-B
-m
unittest
test_s6e_jtag_readonly_scan
-v
```

封包需保存完整 stdout/stderr、实际退出码、`Ran N tests`/`OK` 摘要、测试文件 SHA、扫描器 SHA 与基线 HEAD。仅本地临时 Git 仓库、桩进程和合成日志参与测试。不得把测试桩结果描述为硬件执行。

## 只读实物扫描的当前门槛与停止条件

- 本轮不执行扫描。将来只有在正式 OFFER 与 CLAIM 行都进入对应提交、Reviewer 对最终同字节源码/测试实际 PASS 且总控生成绑定回执、租约实时快照有效、板卡独占及进程/3121 复核都通过后，才允许另行决定是否启动。
- 当前现场租约快照若含无法解析时间的非阶段5板卡事件，状态必须 `BLOCKED`；不得用文件名顺序、CLI 开关、无锁或口头授权覆盖该状态。恢复需取得可核验的正式通知/时间，不修改上游信箱。
- 真正扫描前必须复核固定 SHA 的 `scan2.tcl`、`hw_server.exe`、`xsdb.exe`，并再次检查进程与 TCP 3121。异常、超时、租约召回或清理失败立即停止，保存原日志，只通过本次 `Popen` 句柄清理自起进程；不结束外部进程、不重试、不覆盖 RunId。
- 允许范围仅为现有已审 `scan2.tcl` 对 JTAG 链/目标的只读枚举。禁止存储写入、复位、下载、烧录、改接线、寄存器读取或修改、摄像头/HDMI/串口操作。
- 即使未来只读扫描通过，也仅为连接/目标诊断；不代表 S6-E、G3/G4/G5 或阶段6验收通过。

## Reviewer 回执信任模型

`reviewer_receipt.json` 是总控依据独立 Reviewer 实际结论形成的受信流程记录；校验器检查回执字段、版本、文件与日志哈希的一致性。该 JSON 没有数字签名，不声称具备密码学防伪能力。现在不创建或预填 PASS 回执。
