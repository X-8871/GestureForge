# S6-A v1.7 / r08 运行摘要

- 任务：`S6-A`；RunId：`s6a_g0_20261022_r08`；工作树：`D:\codex-worktrees\w6`
- 绑定提交：`87a6bdc9951b9fed1baf5dad85a88db288ecda6a`（证据由该次构建的工作树生成；交付提交由 `verification/export_selfproof.py` 导出复跑自证）
- 状态：**DELIVERED_PENDING_REVIEW**（复评由项目总控另派；本摘要不构成通过）
- 阈值纪律：24 项参数值与 `PENDING_APPROVAL` 状态未改；未在测试集调参；未触碰硬件。

## 真实命令与退出码

| 检查 | 命令（绝对 project-root） | 实测退出码 |
|---|---|---|
| 旧包失败证据重跑（r01/r02/r03/r04） | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\s6a_rerun_legacy_failures.py --run-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08 --project-root D:\codex-worktrees\w6` | 实测 0（各类失败输出落盘） |
| 判别力探针（基线 1 例 + 注入 7 例，共 8 例 + 历史口径对照 2 例） | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\s6a_r08_probe.py --run-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08 --project-root D:\codex-worktrees\w6` | 实测 0（各用例自检输出落盘） |
| 冻结自证（导出副本复跑，F6 规则） | `python -B verification/export_selfproof.py --commit <历史提交> --worktree-snapshot` | 见 `export_selfproof.json`（历史提交应 NOT_SELF_PROVEN、本包快照应 SELF_PROVEN） |
| 自检（17 项，含完整 C11 与 C17） | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\s6_g0_selfcheck.py --json D:\codex-worktrees\w6\docs\stage6\s6a_stage6_g0_behavior_v1.json --doc D:\codex-worktrees\w6\docs\stage6\S6A_stage6_g0_behavior_spec_v1.md --cases D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08\hand_computed_cases.json --upstream D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08\upstream_bindings.json --project-root D:\codex-worktrees\w6 --evidence-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08 --out D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08\selfcheck_result.json --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08\delivery_manifest.json --state D:\codex-worktrees\w6\.codex\STATE.md` | 见 `delivery_manifest.json.checks` 与 `selfcheck_c11_stdout.txt` |
| check_stage_delivery --mode inputs | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode inputs --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08\inputs_manifest.json --project-root D:\codex-worktrees\w6` | 0（stdout: `check_inputs_mode_output.txt`） |
| check_stage_delivery --mode evidence | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode evidence --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r08\delivery_manifest.json --project-root D:\codex-worktrees\w6` | 见 `delivery_manifest.json.checks`（stdout: `check_evidence_mode_output.txt`） |

> 清单 checks 中 status=PASS 的条目其 exit_code 均为构建器实测值（PASS 必须为 0）。
> 入库 `selfcheck_result.json` 由带 `--manifest` + `--state` 的命令生成，C11 detail 含清单双向一致与 STATE 声明核对。

## 证据文件

- `delivery_manifest.json` / `inputs_manifest.json` / `hashes_sha256.txt`（只哈希实际存在文件）
- `selfcheck_result.json`（ALL_PASS 17 项，含完整 C11 与 C17）+ `selfcheck_c11_stdout.txt`
- `check_inputs_mode_output.txt` / `check_evidence_mode_output.txt`（检查器完整 stdout）
- `selfcheck_old_package_failure.json/.txt` + `old_package_under_test.json`（r01，git 字节可复核）
- `selfcheck_r02_blk1_failure.json/.txt` + `r02_package_under_test.json`（r02，C12 捕获 BLK-1）
- `selfcheck_r03_failure.json/.txt` + `r03_package_under_test.json`（r03，C12 捕获 R3-B01/R3-B02、C17 捕获缺锁存块）
- `selfcheck_r04_failure.json/.txt` + `r04_package_under_test.json`（r04，C12 捕获 N-r04-01/02；C7 因样例数不足（29 < 32，缺 HC-30/31/32）失败；F4）
- `probe_summary.json` + `probe_*_stdout.txt`（基线 1 例 exit 0；注入 7 例各自捕获预期检查项，含 F1 的 `b07_old_wording` 与 F7 的 `case_out_of_sequence_index`；历史口径对照 2 例必须失败）
- `export_selfproof.json`/`export_selfproof.md`（F6 规则：导出副本复跑的三项真实退出码；r06 实测 C11 FAIL、本包快照 SELF_PROVEN）
- `fix_record.json` / `fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`

## 结论边界

- `ALL_PASS`/`CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不验证状态机行为，不代表 G0 复评/独立审查/实物验收通过。
- 回放/注入类结论仅限回放/注入输入；本包未运行任何状态机。

## 限制与未执行

见 `limitations_not_executed.json`（T6-A03 NOT_RUN、M4 可达并计入覆盖、阶段4/5 依赖 BLOCKED、独立复评 PENDING）。
