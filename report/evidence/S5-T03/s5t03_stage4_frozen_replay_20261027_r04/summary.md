# S5-T03 阶段4 冻结包离线消费（RunId `s5t03_stage4_frozen_replay_20261027_r04`）

> 范围：离线主机回放；不代表 PL、实物或实时检测输出。板上真实回放仍需硬件 OFFER/CLAIM + 八类门禁（当前 0/8）。

## 结论（全部由本包产物派生）

- 冻结包逐文件复算：sha256+bytes **10/10 PASS**（`freeze_integrity.json`）。
- 契约绑定：`7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145`，与冻结记录一致 = **True**。
- `upstream_bindings` 漂移现场复算：**17/17 PASS**。
- 逐帧输入：1 帧（状态 {'NO_HAND': 1}），回放帧检测框 0 个；显示五元组 1 条。
- 输入口径标签：`input_kind=stage4_frozen_replay`、`consumption_mode=replay_only`、`evidence_kind=offline_replay`（已覆盖既有 `synthetic_replay`）。
- 独立对拍（`xyxy_px` 逐框 vs 检查器从冻结包重算）：**2 框 / 8 轴，mismatch=0，verdict=PASS**；门禁样本框 2 个。
- 对拍总分节：labels=PASS、frame_records=PASS、five_tuples=PASS、package_consistency=PASS；总 verdict=PASS。

## 命令与真实退出码

| 步骤 | 命令 | 真实退出码 | 日志 |
|---|---|---|---|
| freeze_integrity | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B scripts/stage5_t03/s5t03_freeze_integrity.py --freeze-record D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t27_replay_package_freeze_20261027_r01\replay_package_freeze.json --package-dir D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t26_gate_rerun_20261027_r04 --contract D:\codex-worktrees\w4\docs\stage4\s4b_shared_input_result_contract.json --out D:\codex-worktrees\w5\tmp\5\S5-T03\s5t03_stage4_frozen_replay_20261027_r04\freeze_integrity_cli.json` | 0 | `console/freeze_integrity.txt` |
| consumer | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B scripts/stage5_t03/s5t03_stage4_frozen_replay.py --out D:\codex-worktrees\w5\report\evidence\S5-T03\s5t03_stage4_frozen_replay_20261027_r04 --package-dir D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t26_gate_rerun_20261027_r04 --freeze-record D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t27_replay_package_freeze_20261027_r01\replay_package_freeze.json --contract D:\codex-worktrees\w4\docs\stage4\s4b_shared_input_result_contract.json` | 0 | `console/consumer.txt` |
| crosscheck | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B scripts/stage5_t03/check_s5t03_frozen_replay.py --artifacts D:\codex-worktrees\w5\report\evidence\S5-T03\s5t03_stage4_frozen_replay_20261027_r04 --package-dir D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t26_gate_rerun_20261027_r04 --freeze-record D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t27_replay_package_freeze_20261027_r01\replay_package_freeze.json --contract D:\codex-worktrees\w4\docs\stage4\s4b_shared_input_result_contract.json --out D:\codex-worktrees\w5\report\evidence\S5-T03\s5t03_stage4_frozen_replay_20261027_r04\crosscheck_report.json` | 0 | `console/crosscheck.txt` |
| unittest | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B -m unittest -v scripts.stage5_t03.test_s5t03_json_contract_malformed scripts.stage5_t03.test_s5t03_hud_occlusion scripts.stage5_t03.test_s5t03_json_contract scripts.stage5_t03.test_s5t03_multi_geometry_render scripts.stage5_t03.test_s5t03_long_run_replay scripts.stage5_t03.test_s5t03_replay_display scripts.stage5_t03.test_s5t03_skeleton scripts.stage5_t03.test_s5t03_frozen_replay` | 0 | `console/unittest_all.txt` |

回归套件：8 个模块（既有 7 + 新增 1），解析 `Ran 139` 例、OK=True、FAILED=False。

## 时间口径（冻结件陷阱处理）

- `capture_time_ns` 基准 = `documented_stage3_wallclock_second_unix_epoch`（冻结包已文档化的秒级墙钟抓取时刻，**非** PS 单调采集计数）。
- `result_time_ns` / `end_to_end_latency_ns` / 两个 `age_*_ns` 均**不可定义**（`stale_evaluation=NOT_RUN_OFFLINE_REPLAY_HAS_NO_MONOTONIC_PUBLISH_CLOCK`）；未伪造年龄或延迟。
- `injection_start_ns` **未**被当作采集时间（`injection_start_ns_used_as_capture_time=false`）；`FILE_INJECTION` 的 0 哨兵路径由检查器与判别力用例覆盖。

## 限制与 NOT_RUN

- 只允许离线回放口径的数值一致性结论；不代表板上行为、UART 实收或实时检测。
- 回放帧本体无候选（raw_candidate_count=0 ⇒ NO_HAND 零框）；阳性检测门禁样本不属于回放帧，仅用于 xyxy→像素换算对拍，display_eligible=false。
- 时间字段一律不可定义（无单调发布时钟）；若阶段4 补发布时刻，需重绑后重跑。
- 输入为非连续单帧；无真实帧周期证据。
- G0/G1/G3/G4/G5 均未通过；P/4-D NOT_RUN。
- NOT_RUN：板上真实回放接入（需硬件 OFFER/CLAIM + 八类门禁；当前记录 0/8）
- NOT_RUN：真实采集路径（摄像头未到货）与真实连续帧周期
- NOT_RUN：PS 单调发布时刻 / 结果年龄 / 端到端延迟（冻结包声明 stale_evaluation=NOT_RUN）
- NOT_RUN：P / 4-D / G3 / G4 / G5 关口判定（不归本任务）

## 诚实边界声明

- 允许声明：离线回放口径下的数值一致性；task-27 结果包可被阶段5 消费。
- 禁止声明：板上行为/PL 真实运行、UART 实收/真帧、真实摄像头采集质量或颜色、P/4-D/G3/G4/G5 任一项通过、把回放结果当实时结果。
- §4.5/§7.3 未关闭；G0/G1/G3/G4/G5 判定不归本任务。
