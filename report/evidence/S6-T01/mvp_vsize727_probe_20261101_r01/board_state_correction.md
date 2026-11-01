# board_state 更正记录 — `mvp_vsize727_probe_20261101_r01`

- 更正时间：2026-11-01T02:41（UTC+8）
- 更正人：board-runner（`corrected_by=board-runner`）
- 原标记：`abnormal=true, reason=process_exit_without_clean_teardown`

## 事实（可复核）

1. 本窗在 **S2_loadhw_stop 之后即中止**，失败原因是**脚本自身的字符串检查 bug**（TCL 打印 `LH_OK`，脚本却检查 `LOADHW_OK`），属脚本崩溃，不是板卡异常。
2. **未对板卡做任何配置**：`S3a_init_elf.log` / `S3b_ps7init.log` / `S4_fpga.log` / `S6_dow_con.log` **均不存在** ⇒ 未跑 init.elf、未 ps7_init、未编程 PL、未 dow 应用。
3. S2 实际内容：`LH_OK`、`STOP0_ERR Already stopped`、`STOP1_ERR Already stopped` ⇒ 双核本来已停，loadhw 成功。
4. 收窗：`S12_stop.log` = `STOP Already stopped`；`hw_server` 已停、3121 空闲；`residual_processes=["vivado"]`（CPU 侧构建进程，非板卡会话）。
5. 因此该 abnormal 属"脚本崩溃误标"，板卡状态未受影响，按既有先例（r13/r18 同类更正）予以更正。

## 更正动作

- 调用 `board_state.mark_por('mvp_vsize727_probe_20261101_r01_corrected_by_board_runner')` 清除 abnormal，并在 note 中注明"脚本 bug 误标、未做任何 PS/PL 配置、teardown clean"。
- 保留本窗全部证据（不删除、不重跑同名 RunId）；后续验证用新 RunId `mvp_vsize727_probe_20261101_r02`。
