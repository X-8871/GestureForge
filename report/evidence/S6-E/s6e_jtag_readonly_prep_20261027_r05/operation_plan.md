# S6-E 只读 JTAG 扫描器第二轮准备记录

- RunId：`s6e_jtag_readonly_prep_20261027_r05`（准备包，不是实际硬件执行 RunId）
- 时间：2026-10-27 UTC+8
- 状态：`PREPARED_NOT_RUN`。此轮只修改扫描器/离线测试并准备证据，未启动 `hw_server`/`xsdb`、未连接或操作板卡。
- 当前 w6 HEAD 基线：`d04258fd0e88c220e3678950def82de192922f09`；实际硬件运行时须重读。
- r04 原样保留；r05 针对第二轮 CHANGES_REQUIRED 修复，不产生 Reviewer PASS 或硬件结论。

## 第二轮修复点

1. OFFERED/CLAIMED 状态现在只接受完整状态 token，不接受 `OFFERED_FORGED`/`CLAIMED_FORGED`；工作树和分支字段需完整精确匹配，shadow path/branch 被拒绝。
2. Reviewer 回执中的 worktree SHA 必须与对应 reviewed commit Git blob SHA 相同；仅同时提供两个不同哈希不会通过。
3. 测试命令固定为下方 argv 与工作目录；日志需含唯一 `Ran N tests in ...s` 和唯一 `OK`，退出码必须为 0，summary 与日志一致且 skipped=0。
4. 临时 Git 仓库测试验证 main OFFER / w6 CLAIM 提交、STATE blob OID/SHA、来源与 OFFER 祖先关系，并拒绝错误 OID/SHA、分支非祖先和未提交 CLAIM 伪造。
5. 租约快照把 DSH-008 原始路径/预期与实测 SHA、通知事件的实际文件路径/SHA/UTC+8 时刻写入运行 manifest。解析与计算 SHA 使用同一份读入字节。
6. 失败路径回归覆盖两种 Popen 失败、XSDB 超时和 cleanup 失败；验证保留新 RunId manifest/log，仅清理本次 Popen 句柄，异常有界并明示残留。

## 审查、提交、回执顺序

Reviewer 可先依据冻结的工作树文件 SHA、HEAD 基线、离线测试日志及证据执行独立审查；不需预先有 PASS 回执，也不需先提交源码。PASS 后，总控只提交审核过的相同源码/测试字节，再依独立 Reviewer 实际结论生成 `reviewer_receipt.json` 并绑定该提交的 blob OID/SHA 与 worktree SHA。

JSON receipt 是总控根据独立 Reviewer 实际结果形成的**受信流程记录**。校验器检查内容、路径与哈希的一致性；它不含数字签名或其他密码学身份认证，不能声称脚本具备抗伪造保证。当前不创建、也不预填 PASS receipt。

## 固定审查测试

工作目录：`D:\codex-worktrees\w6\verification`

命令 argv：

```text
C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
-B
-m
unittest
test_s6e_jtag_readonly_scan
-v
```

Reviewer receipt 的 `tests` 对象须包括相同 argv、完全相同工作目录、实际退出码、日志路径及 SHA、以及日志摘要 `tests_run / failures / errors / skipped / success_marker`。摘要仅在解析到唯一的 unittest `Ran N tests` 与 `OK` 且无 skip/failure/error 时通过。

## 租约和实际执行边界

固定租约 DSH-008、DSH-009 召回和 DSH-010 释放均由动态运行期核验；每个租约检查把原始租约及事件来源路径、hash_basis、实际 SHA 和 UTC+8 通知时刻记入 manifest。DSH 未来召回会在启动前及 XSDB 等待期间阻断并记录。

实际扫描仍需要新的正式 OFFER/CLAIM、独立 Reviewer PASS 后提交并绑定的 receipt、人工独占窗口确认和开窗时进程/3121 空闲。当前准备不分配硬件执行 RunId，不启动执行命令。只读链路扫描即使将来通过，也不满足 S6-E、G3/G4/G5，不证明器件身份、阶段4/5集成、性能或实时行为。

失败或中断后仅经本次 `Popen` 句柄停止本次进程；terminate 最多等待 5 秒，仍运行才 kill 同一句柄并再等待 5 秒。Popen、超时、召回或清理失败均在新的 manifest/log 留证，不按名称终止外部进程、不重试、不覆盖 RunId。禁止复位、烧录、下载、改接线和任何板上读写。

