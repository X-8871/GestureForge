# S6-E 租约时间解析复审修复证据

采集时间：2026-10-28T01:28:10+08:00（UTC+8）。

仅为离线扫描器与单元测试修复；未启动硬件工具、未连接板卡/相机/串口/HDMI。显式范围符必须紧邻起始时刻，仅允许水平空白；右端点非法、秒非法、缺失、被正则回溯省略或未明确跨日时整条时间字段不可解析。下一行正文的范围符不延伸时间戳。原 00:5x、日期-only、同日重叠、跨日边界、未知未来/无日期及泛化召回负控保留。

完整离线回归：C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest test_s6e_jtag_readonly_scan -v；exit=0；52 tests PASS；耗时 4.865 秒。真实 mailbox 只读 lease_snapshot valid=True，原因：最近一条有效通知为释放：DSH-20261027-010-board-released.md。

基线提交 5aa0fd15a6d422141b0619faf5ec909e77f97efc；源码/测试 SHA 采用 worktree_disk，待总控独立复核。不得据此声称硬件扫描或 G3/G4/G5。
