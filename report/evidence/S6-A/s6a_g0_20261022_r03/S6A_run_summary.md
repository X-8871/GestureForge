# S6-A v1.2 / r03 运行摘要

- 任务：`S6-A`；RunId：`s6a_g0_20261022_r03`；工作树：`D:\codex-worktrees\w6`
- 修订基线提交：`3b59674f93e8a2c020a0670fa475ee6a15330833`（证据由未提交工作树生成）
- 状态：**DELIVERED_PENDING_REVIEW**（复评由项目总控另派；本摘要不构成通过）
- 阈值纪律：24 项参数值与 `PENDING_APPROVAL` 状态未改；未在测试集调参；未触碰硬件。

## 真实命令与退出码

| 检查 | 命令（绝对 project-root） | 实测退出码 |
|---|---|---|
| 自检（16 项，含完整 C11） | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\s6_g0_selfcheck.py --json D:\codex-worktrees\w6\docs\stage6\s6a_stage6_g0_behavior_v1.json --doc D:\codex-worktrees\w6\docs\stage6\S6A_stage6_g0_behavior_spec_v1.md --cases D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03\hand_computed_cases.json --upstream D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03\upstream_bindings.json --project-root D:\codex-worktrees\w6 --evidence-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03 --out D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03\selfcheck_result.json --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03\delivery_manifest.json --state D:\codex-worktrees\w6\.codex\STATE.md` | 见 `delivery_manifest.json.checks` 与 `selfcheck_c11_stdout.txt` |
| check_stage_delivery --mode inputs | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode inputs --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03\inputs_manifest.json --project-root D:\codex-worktrees\w6` | 0（stdout: `check_inputs_mode_output.txt`） |
| check_stage_delivery --mode evidence | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode evidence --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03\delivery_manifest.json --project-root D:\codex-worktrees\w6` | 见 `delivery_manifest.json.checks`（stdout: `check_evidence_mode_output.txt`） |

> 清单 checks 中 status=PASS 的条目其 exit_code 均为构建器实测值（PASS 必须为 0）。
> 入库 `selfcheck_result.json` 由带 `--manifest` + `--state` 的命令生成，C11 detail 含清单双向一致与 STATE 声明核对。

## 证据文件

- `delivery_manifest.json` / `inputs_manifest.json` / `hashes_sha256.txt`（只哈希实际存在文件）
- `selfcheck_result.json`（ALL_PASS 16 项，含完整 C11）+ `selfcheck_c11_stdout.txt`
- `check_inputs_mode_output.txt` / `check_evidence_mode_output.txt`（检查器完整 stdout）
- `selfcheck_old_package_failure.json/.txt` + `old_package_under_test.json`（r01，git 字节可复核）
- `selfcheck_r02_blk1_failure.json/.txt` + `r02_package_under_test.json`（r02，C12 捕获 BLK-1）
- `fix_record.json` / `fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`

## 结论边界

- `ALL_PASS`/`CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不验证状态机行为，不代表 G0 复评/独立审查/实物验收通过。
- 回放/注入类结论仅限回放/注入输入；本包未运行任何状态机。

## 限制与未执行

见 `limitations_not_executed.json`（T6-A03 NOT_RUN、M4/M7 不可达、阶段4/5 依赖 BLOCKED、独立复评 PENDING）。
