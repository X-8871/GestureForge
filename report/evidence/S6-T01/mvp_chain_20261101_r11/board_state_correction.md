# board_state 更正记录 — `mvp_chain_20261101_r11`

- 更正时间：2026-11-01T04:52（UTC+8）；更正人：board-runner（`corrected_by=board-runner`）；**已获 Team Lead 明确批准（选 A）**
- 原标记：`abnormal=true, reason=process_exit_without_clean_teardown`（04:44:42）

## 事实（可复核）

1. 崩溃原因：脚本 bug —— 新加的 `--clear-raw` 分支里变量名写错（`RUN` 应为 `run`），`NameError: name 'RUN' is not defined`。
2. **崩溃点在 `S5_pl_probe` 之后、应用加载之前**：证据目录含 `S1_IDENT`…`S5_pl_probe` 全部步骤，**无** `S5b_clear_raw`/`S6a_dow_core0`/`S7_weights`/`S8_core1_start`/`S10_uart_collect` 日志 ⇒ **未 dow 显示 ELF、未 dow 权重、未启动 core1、无任何应用运行**。
3. 崩溃时板卡状态：组合 init 已完成（init.elf、ps7_init、APER=0x017C000D、DDR 检查、DDR 窗口）、**PL 已编程 build11k 且 PL 探测 PASS**、双核处于停止态。
4. 收窗：脚本未走 `S13_teardown`，残留 `hw_server`（PID 24196）；board-runner 已手工停止，核验 **`hw_server=0`、`xsdb=0`、3121/3122 均空闲、零残留**。
5. 判定：属**脚本 bug**（非 DAP/halt 异常、非板卡故障），且崩溃前无应用运行；组合 init 会重新执行 `init.elf + ps7_init + PL 编程`，状态可确定重建 ⇒ 按先例以 `corrected_by` 更正，**不需要物理 POR**（Team Lead 批准）。

## 更正动作

- `board_state.mark_por('mvp_chain_20261101_r11_corrected_by_board_runner')` 清除 abnormal；note 注明"脚本 bug 误标、崩溃在应用加载前、残留已手工清除、零残留、非物理 POR"。
- 脚本已修复：`RUN`→`run`（清零步骤内两处）、并给 `__main__` 增加兜底 teardown（异常时也停 hw_server/关 UART），dry-run 通过。
- 以**新 RunId `mvp_chain_20261101_r11b`** 重跑同一窗口（同 b11k/v35/core1 新 sha/权重，`--clear-raw` 120 s）。

## 后续规则（Lead 明确）
- 若再崩在**应用加载前**：同样按 correction 处理并重跑，不每次等 POR。
- 若崩在**应用运行中**（core1/相机已启动）：**必须停手等物理 POR**。
