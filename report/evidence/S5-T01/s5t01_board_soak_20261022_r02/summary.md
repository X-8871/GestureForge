# S5-T01 T5-09 连续长跑 RunId `s5t01_board_soak_20261022_r02`（30 分钟采集窗）

- 时间（UTC+8）：2026-10-22 19:39（下载完成）→ 20:09（采集结束）
- 被测件：`s5t01_frames_r05b.elf` SHA256 `4260d20a138e3a88d2a9cd8f6b74ef6ba85070cc98542e459b7ad197960aada5`（120 帧结果流循环）+ 冻结灰度位流 `44e609cc…c4afb`（易失）
- 方式：`run_t05_board_capture.sh <RUN_DIR> <ELF> soak 1800`（含下载 + 1800 s UART 采集 + 收尾只读转储）
- 退出码：`pipeline_exit=0`、`XSDB_EXIT=0`、`T05_ALL_DONE=1`

## 1. 结果（`console/soak_verify.json`，校验 exit 0）

| 项 | 实测 |
|---|---|
| 轮次 | **119 轮**（`S5_5T_SUMMARY` 行），其中 **118 轮完整**（120 帧/轮），末轮被采集窗截断（74 帧） |
| 应用连续运行时长 | **1774.0 s = 29.57 分钟**（118 完整轮 + 截断轮；应用侧 `elapsed_ms` 累计） |
| 采集窗 | 1800 s（其中前 ~35 s 用于下载 ⇒ 应用运行 < 采集窗） |
| 每轮计数（118 轮**完全一致**） | displayed=107 / stale_cleared=17 / dropped=7 / timeouts=6 / dup=5 / ooo=4 / warmup=9 / uniq_displayed=101 |
| 每轮耗时 | `elapsed_ms=14907`（≈14.9 s/轮，与 107×60 ms 睡眠 + 渲染一致） |
| 每轮 FPS | `display_fps_x10=71`、`unique_frame_update_fps_x10=67` |
| `occ_max` | 2133 px（HUD 遮挡量化，全程不变） |
| 死锁判据 | **轮次持续推进**（119 轮无中断）、每轮计数与模型一致、FPS 可复算 ⇒ **无死锁** |

## 2. 校验明细（11/11 PASS，exit 0）
- `rounds_present` / `at_least_one_complete_round`：119 轮、118 完整
- `displayed_result_sequence_matches_model`：**118 个完整轮的 (displayed,result) 序列与调度模型完全一致**
- `counters_match_model`：计数逐轮与模型一致（见上表）
- `semantics_unique_B` / `age_frame_ge_age_result` / `stale_implies_no_box` / `stale_iff_age_over_limit`：全部通过（stale 行 2042 次判定，0 违反）
- `pattern_vs_flag_counts_explained`：观测 dup=708 / ooo=354 与标记计数（590/472）之差由 **1 处 OOO 撞值（k=116 目标 113 恰等于上一条）** 解释，逐条列出
- `fps_recomputable`：由 `displayed/elapsed_ms` 复算与板上打印一致
- `soak_duration_ge_required`：29.57 分钟（按 2% 容差判定通过）

## 3. 如实限制（不夸大）

- **严格计时口径**：应用连续运行 **29.57 分钟 < 30.0 分钟**（差 26 s）。差异来源是采集窗固定 1800 s，而下载占用前 ~35 s；**按 2% 容差判 PASS**，但**严格 30 分钟未达到**。
  → 已另起**纯 UART 采集**（无下载开销）`s5t01_board_soak_20261022_r03`（1860 s）以严格满足 ≥30 分钟；其结果另附。
- **仅显示侧**：本长跑验证的是"**显示/叠加路径**在 30 分钟内的连续性与计数可复算"；`inference_fps=NA`（无阶段4 注入源），**不得**据此声称"推理 30 分钟无死锁"。
- result 流为**合成**（非阶段4 输出）；跨进程外部故障注入未做。
- 未烧 QSPI、`0x503D` 未改；采集后 `hw_server` 已清理（见让出记录）。

## 4. 证据文件
- `console/uart_soak.log`（1.64 MB 原始 UART）、`console/capture_soak.txt`、`console/download_soak.log`、`console/read_safe_soak.log`
- `console/soak_verify.json` / `soak_verify_stdout.txt`（11/11 PASS，exit 0）
- `console/soak_start.txt`（起止时间戳）、`console/input_hashes.txt`