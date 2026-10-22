# S6-A v1.1 / r02 运行摘要

- 任务：`S6-A`；RunId：`s6a_g0_20261022_r02`；工作树：`D:\codex-worktrees\w6`
- 修订基线提交：`1fe4648cba5a9f1ffc87dbe21cea732b72716bff`（证据由未提交工作树生成）
- 状态：**DELIVERED_PENDING_REVIEW**（复评由项目总控另派；本摘要不构成通过）
- 阈值纪律：24 项参数值未改，全部 `PENDING_APPROVAL`；未在测试集上调参；未触碰硬件。

## 真实命令与退出码（由 `verification/s6a_build_evidence.py` 实跑记录）

| 检查 | 命令（绝对 project-root） | 实测退出码 |
|---|---|---|
| 自检（16 项） | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\s6_g0_selfcheck.py --json D:\codex-worktrees\w6\docs\stage6\s6a_stage6_g0_behavior_v1.json --doc D:\codex-worktrees\w6\docs\stage6\S6A_stage6_g0_behavior_spec_v1.md --cases D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r02\hand_computed_cases.json --upstream D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r02\upstream_bindings.json --project-root D:\codex-worktrees\w6 --evidence-dir D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r02 --out D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r02\selfcheck_result.json` | 0 |
| check_stage_delivery --mode inputs | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode inputs --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r02\inputs_manifest.json --project-root D:\codex-worktrees\w6` | 0 |
| check_stage_delivery --mode evidence | `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe -B D:\codex-worktrees\w6\verification\check_stage_delivery.py --mode evidence --manifest D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r02\delivery_manifest.json --project-root D:\codex-worktrees\w6` | 见 `delivery_manifest.json.checks`（构建器实跑写入） |
| 自检 --manifest（C11 清单/STATE 核对） | 构建器在清单定稿后实跑，输出写 tmp | 见构建器 stdout（真实退出码） |

> `delivery_manifest.json.checks` 中 status=PASS 的条目，其 exit_code 均为构建器实测值（PASS 必须为 0）。
> 清单定稿后构建器再实跑一次 evidence 模式作为最终确认。

## 证据文件

- `delivery_manifest.json`：机器可读清单（按实际文件生成，清单本身不列入 files）。
- `inputs_manifest.json`：冻结上游接口与输入文件绑定。
- `hashes_sha256.txt`：本目录所有已存在文件的 SHA-256（不含自身与清单）。
- `selfcheck_result.json`：修复包自检 `ALL_PASS`（16 项）。
- `selfcheck_old_package_failure.json` / `..._stdout.txt`：加固自检在旧包（`1fe4648`）上的失败输出。
- `old_package_under_test.json`：旧包被检文件清单与哈希。
- `fix_record.json` / `fix_record.md`：B-01..B-05、N-01..N-10 修复记录。
- `coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`。

## 结论边界

- `selfcheck_result.json` 的 `ALL_PASS` 只表示规格一致性、算术边界与证据存在性复算通过；
  `check_stage_delivery.py` 的 `CHECKS_OK` 只表示清单/文件绑定检查通过。
- 均不代表状态机行为正确、G0 复评通过、独立审查通过或任何板上/摄像头验收。
- 回放/注入类结论的适用范围仅限回放/注入输入；本包未运行任何状态机。

## 限制与未执行

见 `limitations_not_executed.json`（含 T6-A03 NOT_RUN、M4/M7 不可达、阶段4/5 依赖 BLOCKED、独立复评 PENDING）。
