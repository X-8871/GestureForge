# S6-E 只读 JTAG 拓扑扫描准备记录

- RunId：`s6e_jtag_readonly_prep_20261027_r04`（准备包，不是硬件执行 RunId）
- 时间：2026-10-27 UTC+8
- 状态：`PREPARED_NOT_RUN`。仅改扫描器、离线测试和此准备包；未启动 `hw_server`/`xsdb`，未连接或操作板卡。
- scope：`S6E_JTAG_READONLY_DIAGNOSTIC`，固定 Tcl 只枚举 JTAG 连接、目标和链，不运行模型/摄像头/交互逻辑。
- r01-r03 原样保留；本轮没有硬件结果。

## 租约和验收边界

DSH-008 原始租约 SHA-256（worktree_disk）为 `519566fb79202689223e0cd52409b04c072b4cc31ca58270605a104102be88cb`。DSH-009 于 22:30 UTC+8 召回；DSH-010 于 23:00 明确关联 -009 并写明 -008 恢复有效。脚本固定 -008 SHA，并按正式通知标题与 UTC+8 时间判断后续释放/召回。此历史核验不证明未来开窗时租约仍有效。

扫描仅是独立只读拓扑诊断，不满足 S6-E、G3/G4/G5，也不证明器件型号/速度级、工程部署身份、4/5 阶段契约或实时功能。阶段6八门禁仍须分别验收。

本轮尚无正式 `S6E-JTAG-RO::s6_hardware_session_handoff` main OFFER/w6 CLAIMED，也无本版本独立 Reviewer PASS 回执；当前不能执行。旧 CLI boolean flags 不能作为凭据且已被移除。独占窗口 flag 只表示人工确认，执行器仍动态核验正式 11 字段交接、已提交 OFFER/CLAIM、Reviewer 回执、租约和占用。

## 固定只读输入

| 用途 | 精确路径 | SHA-256（基座：worktree_disk） |
|---|---|---|
| Tcl | `D:\FPGA_Competition\report\evidence\CTRL-HW-SCAN\hw_scan_20261022_r01\scan2.tcl` | `b6987e0a60f4a5a8681f2b3803e60b64b5050a228d9543c3b708cca2e13ba046` |
| DSH-008 | `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\dsh_mailbox\DSH-20261027-008-board-lease-stage6.md` | `519566fb79202689223e0cd52409b04c072b4cc31ca58270605a104102be88cb` |
| hw_server | `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe` | `e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3` |
| xsdb | `D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\xsdb.exe` | `664dc93eb6cec40a2596162dbdf9bc42d5ab96ffbfc34d7515f8c68072fbac55` |

执行器每次启动前重算四项哈希，任一不符即 fail-closed。

## Reviewer 回执及执行命令

独立 Reviewer 先审查冻结的工作树源码/测试字节 SHA、当前 HEAD 基线、离线测试日志和证据；审查本身不要求预先存在 PASS 回执或提交源码。Reviewer PASS 后，总控只提交审查通过的相同源码/测试字节，再在本目录创建 `reviewer_receipt.json`；格式见 `reviewer_receipt.schema.json`。回执绑定唯一 RunId、Reviewer、实际源码提交、两个被审文件的 worktree_disk SHA 与该提交的 commit_blob OID/SHA、测试命令/实际 exit=0/日志哈希、审查证据哈希。执行器只在未来真实执行前校验此提交与审查绑定。本准备轮不创建或预填 PASS 回执。

正式交接与 Reviewer 门禁通过后另分配未用实际硬件 RunId；以下命令仅为未来操作方案，本轮不运行：

```powershell
Set-Location -LiteralPath 'D:\codex-worktrees\w6\verification'
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B .\s6e_jtag_readonly_scan.py --run-id s6e_jtag_readonly_YYYYMMDD_rNN --execute --confirm-exclusive-window
```

启动器前置核验最多 20 秒；启动 `hw_server.exe -s tcp::3121` 前再次核对正式状态、Reviewer、输入 SHA、租约、进程及端口。只有 TCP 3121 唯一 LISTEN PID 等于本次 Popen PID 才运行固定 `xsdb.exe <scan2.tcl>`。输出须满足唯一 count、唯一非空 chain、唯一 connect/disconnect 标志、count 与明细数量相同、XSDB exit=0。

## 停止与清理

- hw_server 最多 10 秒监听，XSDB 最多 30 秒，活动总预算 60 秒，含有界清理总上限 80 秒；不重试、不复用 RunId。
- 执行期间轮询租约；召回、租约哈希变化、进程/端口冲突或端口 PID 改变均立即停止。
- 中断/异常时仅通过本次 Popen 句柄停止本次进程：terminate 等待 5 秒，再必要时 kill 并等待 5 秒。禁止按名称结束任何进程；外部残留只记录、不处理。
- 新 RunId 保存机器可读 manifest，绑定正式 CLAIM、Reviewer、源码/测试/基线、固定工具哈希、实际命令 exit code、原始日志和清理核验。失败时保留日志和状态，不覆盖、不重试。
- 不复位、烧录、下载、改线，不读写寄存器/存储；错误或清理不完整则停止并保留现场。

## 离线验证

命令（目录 `D:\codex-worktrees\w6\verification`）：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -m unittest test_s6e_jtag_readonly_scan -v
```

24 项回归均使用临时目录、Mock 和 Popen/租约桩，无真实工具调用或硬件连接。覆盖旧 flag 伪造、CLAIM/Reviewer 缺失、旧源码 SHA、租约改动与召回、输出重复/不一致、manifest 绑定和运行中召回时仅清理自起进程。该验证只属于离线软件测试，不升级为 G3/G4/G5。

