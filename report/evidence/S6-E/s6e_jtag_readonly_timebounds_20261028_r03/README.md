# S6-E 时区语法 fail-closed 修复证据

采集时间：2026-10-28T01:37:30+08:00（UTC+8）。

本轮只收紧通知时间区的完整解析：接受 UTC+8（括号/裸后缀）与完整 ISO ±HH:MM；ISO 负偏移要求 T 日期时间分隔符以避免与 ASCII 时间范围歧义。UTC+9、PST、UTC-8、矛盾/重复后缀及日期-only偏移均拒绝，不回退本地 UTC+8。范围符仅限同一行水平空白规则，跨行范围符不并入字段。

完整离线回归：C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest test_s6e_jtag_readonly_scan -v；exit=0；56 tests PASS；耗时 4.924 秒。真实 mailbox 只读 lease_snapshot valid=True；最近一条有效通知为释放：DSH-20261027-010-board-released.md。

r02 predecessor manifest SHA-256：db0790b44f03f37708d1645b8ab869a1bd212165c490181196335ccd499ed2cf；副本包含于 inputs/prior_r02_delivery_manifest.json。源码基线提交：5aa0fd15a6d422141b0619faf5ec909e77f97efc；源码/测试按 worktree_disk SHA 绑定待审字节。

限制：未启动硬件工具或连接板卡；该证据不代表正式硬件交接、G3/G4/G5 或实物验收。
