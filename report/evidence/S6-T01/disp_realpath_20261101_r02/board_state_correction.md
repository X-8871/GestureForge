# board_state 更正记录 — `disp_realpath_20261101_r02`

- 更正时间：2026-11-01T03:37（UTC+8）；更正人：board-runner（`corrected_by=board-runner`）
- 原标记：`abnormal=true, reason=process_exit_without_clean_teardown`（03:36:09）

## 事实（可复核）

1. 本窗失败于 **S2_loadhw_stop 之后的记录步骤**：脚本自身 bug（`state` 字典缺 `steps` 键，`KeyError: 'steps'`），属脚本崩溃。
2. **未对板卡做任何配置**：证据目录只有 `S2_loadhw_stop.*` 与 `S12_stop.*`；**无** `S3a_init`/`S3b_ps7init`/`S4_fpga`/`S6_dow_con` 日志 ⇒ 未跑 init.elf、未 ps7_init、未编程 PL、未 dow。
3. S2 内容：`LH_OK` + 双核 stop（core0/core1 原本由上一窗收窗停住）。
4. 收窗：`S12_stop.log` 正常；`hw_server=0`、3121 空闲、零残留。
5. 结论：abnormal 属"脚本崩溃误标"，板卡状态未受影响；按既有先例更正，保留全部证据、不改写、不重跑同名 RunId。

## 更正动作
- `board_state.mark_por('disp_realpath_20261101_r02_corrected_by_board_runner')` 清除 abnormal；
- note 注明"脚本 bug 误标、未做任何 PS/PL 配置、teardown clean、非物理 POR"；
- 修正脚本 bug 后，用 **新 RunId `disp_realpath_20261101_r03`** 重跑。
