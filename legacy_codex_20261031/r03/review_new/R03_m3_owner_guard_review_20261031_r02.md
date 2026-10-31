# R-03 定向复审 r02：收尾写入失败语义（2026-10-31）

## 结论

**PASS。** 上一份复审报告保留原样。此前 `server_close.json` 写入失败仍报成功的问题已修复；本次定向 OSError mock 与正常收尾 mock 都显示 stdout、进程退出码及 cleanup 字段语义一致。

## 本轮被审差异

只读核查 `D:\codex-worktrees\w6\legacy_codex_20261031\m3_w02\hold_hw_server.py` 与 `test_owner_guard.py`，冻结 SHA 与总控提供值相符：

- `hold_hw_server.py`：`e3ba842ee8f22229b73c49d54aec06c3cb84b914bc6235c12a1b84dfdddcb222`
- `test_owner_guard.py`：`2b0fd6762c5ba2079ba5d897b047368aa3e37d625de2c4589e0be03986ec7720`

变化集中在 `_finish_close` 与新增 `test_close_record_write_oserror_fails_but_preserves_cleanup_result`。没有修改源文件。

## 核查结果

- `_finish_close` 先根据 Job 句柄关闭、根进程 wait、线程 join 等字段独立计算 `cleanup_status`；之后单独确定收窗状态和收尾记录写入状态。写入抛出 `OSError` 时保持实际 `cleanup_status`，将 `close_status` 改为 `FAILED_CLOSE`，设置记录写入失败状态和错误文本，并返回 2；超时路径仍返回 124。
- 新 OSError 反例验证：stdout 为 `FAILED_CLOSE`，同时保留 `CLEANUP_CONFIRMED`；报告 `close_record_write_status=FAILED` 和 `mock disk full`；没有 `CLOSED_BY_REQUEST` 文本；退出码 2。该用例以 mock writer 抛出异常，不创建硬件进程或 socket。
- 另用临时目录执行正常收尾 mock：stdout 为 `CLOSED_BY_REQUEST`、`CLEANUP_CONFIRMED`、记录写入 `WRITTEN`；退出码 0。落盘 `server_close.json` 包含相同 `close_status` 与 cleanup 结果。该文件不包含自我证明的 `close_record_write_status` 字段，写入结果由同步 stdout 和进程码报告，没有将 `NOT_ATTEMPTED` 错写入成功记录。
- Job 清理事实与收尾记录保存结果继续分离：记录写失败不会把 `cleanup_confirmed=true` 改成 false，但不再因此报告正常收窗。这与“Job 已清理、记录未能保存”的事实一致。

## 定向验证

- `C:\Users\22061\.local\bin\python3.11.exe -B -m unittest -v test_owner_guard.OwnerGuardTests.test_close_record_write_oserror_fails_but_preserves_cleanup_result`（工作目录 `m3_w02`，临时目录在 `D:\FPGA_Competition\tmp`）：**exit 0，1/1 通过**。
- 正常 `_finish_close` mock 写入验证：**exit 0**；stdout/退出码/落盘记录字段如上。
- 未重跑原 28 项、未重复 Native 正控。未访问真实 socket、XSDB、Vivado、hw_server、DSH 窗口或硬件；没有 Git 写操作。

## 判定边界

本 PASS 关闭的是收尾记录写失败这一项实现审查，不代表获得新的 DSH OFFER、板卡已 ready 或 M3 实物测量通过。当前没有有效 OFFER，不得启动硬件。