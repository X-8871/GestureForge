# S6-E 只读扫描离线准备 r07

- RunId：`s6e_jtag_readonly_prep_20261028_r07`；状态：`PREPARED_NOT_RUN`。
- 时间：2026-10-28 UTC+8；w6 基线：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，HEAD `d04258fd0e88c220e3678950def82de192922f09`。
- 被测源码/测试（worktree_disk）：scanner `f9af18ed4d9382254a9e81479186d13fa1247b92c14e4083fb609f85bfb238e1`；tests `76bed296affd86d355fcb6011eb3e0f9fe62777302c7f272b11364d414e5c43c`。

## 实际离线验证

工作目录：`D:\codex-worktrees\w6\verification`

```text
C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest test_s6e_jtag_readonly_scan -v
```

本次实际退出码 0，40 tests / 40 passed / 0 skipped，运行 5.262 秒；完整 stdout/stderr 在 `offline_tests.log`。测试使用临时 Git 仓库、桩进程和合成日志，不含硬件动作。

## r06 失败轨迹与当前阻塞

- 不覆盖的 r06 原失败日志：`report/evidence/S6-E/s6e_jtag_readonly_prep_20261027_r06/offline_tests.log`，SHA-256 `cc4ca2aa220963fa924c6d61c484b7e4e2f97b324287618200675328d3d15bda`；其记录为 39 tests、1 failure（阶段5限定 notice 的 marker 回归）。该日志对应的旧测试 SHA 为 `cba3637f479ec725046a94140f88e85f3b5e41a5774d6a0478e04fe7341b91e2`；旧 scanner SHA `9433cf5c923986bdaf67c06d12534ec0de50418c1c6a73f11fcf07e4158759b7` 是从当前源码逆向本轮后续两处补丁计算，旧日志未内嵌源码哈希，故此来源仅作轨迹关联说明。
- 当前现场租约快照 `BLOCKED`：DSH mailbox 的 `DSH-20261024-004-stage3-window-j10-scope-w4-takeover.md`（SHA-256 `b820fcd1dbe8b213056f88f395ad3ac5a3569f153cde490a5816231a4c76510c`）缺可解析 UTC+8 时间。不得按文件名或阶段猜测事件顺序。
- 主 STATE 与 w6 STATE 均未找到 `S6E-JTAG-RO::s6_hardware_session_handoff` 的正式 OFFER/CLAIM 行。执行器指向 r06 的 `reviewer_receipt.json` 缺失；没有可用 Reviewer PASS 回执。
- 板卡扫描 `NOT_RUN`：未启动 `hw_server`/`xsdb`，未连接或操作实物。无 G3/G4/G5 或阶段验收结论。

此包只记录离线准备和阻塞。解除阻塞需可核验的租约时间/通知、正式 OFFER/CLAIM、独立 Reviewer 对绑定版本的实际 PASS 及总控回执；本包不授权执行板卡操作。
