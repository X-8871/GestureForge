# S6-E 唯一权威通知时间解析修复证据

采集时间：2026-10-28T01:51:54+08:00（UTC+8）。RunId：`s6e_jtag_readonly_timebounds_20261028_r04`。

真实信箱盘点：48 条 DSH 通知中无重复的显式 `时间：`/`日期：` 字段。支持单一权威元数据字段，字段边界包含 `；`、`;`、`｜`、`|`。实际原文 DSH-20261027-001 的 `时间（UTC+8）：2026-10-27 12:26–12:40` 完整解析为闭开区间 12:26–12:41；不截断字段、不猜测或回退首字段。重复时间/日期字段、跨时区重复值、字段内多个日期、未知时区均 fail-closed。

离线回归命令：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest test_s6e_jtag_readonly_scan -v`；exit=0。总计 65 项，详见 `offline_tests.log`。只读真实信箱快照：valid=True；最近一条有效通知为释放：DSH-20261027-010-board-released.md。输入副本绑定 48 条信箱原文，另保存 r03 前版清单副本。

r03 delivery manifest SHA-256：`9a1f956f996fb449c7f232bd6c9c34bd17c680887180f643f5f63732c0d65f96`。基线 HEAD：`5aa0fd15a6d422141b0619faf5ec909e77f97efc`。源码和测试尚未提交，使用 `worktree_disk` 哈希绑定。

限制：只读文件，不操作板卡/摄像头，不启动硬件工具。没有正式会话 OFFER/CLAIM；本结果不代表 G3/G4/G5，硬件扫描 NOT_RUN，独立复审 NOT_RUN。
