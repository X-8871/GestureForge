# S6-E 邮件时序区间修复离线证据

采集时间：2026-10-28T01:18:19+08:00（UTC+8）。

范围：仅修改阶段6只读扫描器与对应离线单元测试；未启动 Vivado、XSDB、hw_server、JTAG 或任何板级会话，未连接摄像头、串口或 HDMI。

时间口径：00:5x 保留为 [00:50, 01:00)；明确日期但无时刻使用 [当日 00:00, 次日 00:00)。仅当通知区间整体早于后续释放区间起点时才清除其阻断效力；重叠、更晚、无日期、无法解析及泛化召回仍 fail-closed。不读取 mtime。

回归：C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest test_s6e_jtag_readonly_scan -v，exit=0，48 项通过，耗时 5.054 秒。当前只读 lease_snapshot valid=True；最近一条有效通知为释放：DSH-20261027-010-board-released.md。

源码基线提交：5aa0fd15a6d422141b0619faf5ec909e77f97efc。源码/测试使用 worktree_disk SHA 绑定未提交待审字节，SHA：{"verification/s6e_jtag_readonly_scan.py": "a5a07f3887cc5eaefb4e582da110d3848eec58e770315b21f492a853bbaf8b7b", "verification/test_s6e_jtag_readonly_scan.py": "15d778855d0295d25b4555edc170f97cd007652f660aaa6b0763122484a8c18c"}。

限制：此快照不构成正式硬件 OFFER/CLAIM、Reviewer 回执、硬件扫描、G3/G4/G5 或实物验收；硬件扫描保持 NOT_RUN。
