# S6-A 独立评审记录（CHANGES_REQUIRED）

- 被审版本：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，提交 **`1fe4648`**
- 评审方：DSH 项目总控派出的**独立 Reviewer 子代理**（只读被审文件；一切验证只写隔离临时目录）
- 时间（UTC+8）：2026-10-22 19:29–19:36
- 结论：**`CHANGES_REQUIRED`**（3 类阻断问题）
- 本记录只覆盖该版本；**不代表** G0/G2/G4/G5 通过，也不代表阶段6 验收。

## 1. 通过项（可核验）

| 检查 | 结果 |
|---|---|
| 13 项上游/文件 SHA-256 复算 | **全部一致**（含 `git 73c3dad:` 与 `git 875e487:` 形式的只读引用） |
| 计数一致性 | 行为 28 行、参数 24、迁移 15、不变量 9、动作 5，与文档一致 |
| 20 个人工手算用例独立复算 | **20/20 通过**（含稳定窗口、冷却、去重、丢失、过期、抖动、frame_id、会话切换、保持只触发一次、迟滞、同分、动作事件、未知拒绝） |
| 阈值纪律（是否被写成已批准） | **无问题**（`approval_issues` 为空） |
| 自检脚本独立复跑 | 在其原始输入下 `ALL_PASS`（但见 §2.3 盲区） |

## 2. 阻断问题

### 2.1 声称的证据文件实际不存在（记录不实）

`w6/.codex/STATE.md` 与证据入口声明本轮证据包含：

- `delivery_manifest.json`
- `inputs_manifest.json`
- `hashes_sha256.txt`

但 `report/evidence/S6-A/s6a_g0_20261022_r01/` 实际只有：`coverage_matrix.json`、`hand_computed_cases.json`、`limitations_not_executed.json`、`S6A_run_summary.md`、`selfcheck_result.json`、`upstream_bindings.json`。

→ 要求：真实生成这三份，或把声明改为与实际一致；**不得保留无法核实的声明**。（DSH 项目总控按自检结果提交时未逐项核对该声明，已记录为本轮教训。）

### 2.2 文档 ↔ JSON 标识不一致

| 项 | 问题 |
|---|---|
| `H-5` | JSON 有，文档（MD）缺 |
| `M2`、`M10` | JSON 有，文档缺 |
| `T6-S03` | JSON 有，文档 §14 无该行 |
| `E_FRAME_CONFLICT` | JSON 有，文档 §3 无 |

→ 要求：以 JSON 为唯一权威，补文档或删 JSON 并说明理由，做到双向一致。

### 2.3 自检脚本存在系统性盲区

`verification/s6_g0_selfcheck.py` 的 C3 声称做"文档 ↔ JSON 标识双向一致"检查，却**未能捕获** §2.2 的全部四项。→ 要求：按 ID 集合双向比较（不变量/迁移/参数/事件），并新增"证据清单 vs 实际文件"存在性检查；先用旧包验证加固后的脚本**能捕获**这些缺陷（保留失败输出），再用修复包跑出 `ALL_PASS`。

## 3. 归档文件（评审方产出，原样保留）

- `independent_verify.py` / `independent_verify_result.json`：哈希复算、计数、手算用例复算、阈值纪律、缺失证据检测
- `compare_spec.py` / `compare_spec_result.txt`：文档↔JSON 逐项差异
- `selfcheck_independent.json`、`selfcheck_with_project_root_dot.json`：不同 `--project-root` 下的自检复跑输出
- `dump_source_order.py`、`make_manifests_sim.py`：辅助脚本

## 4. 处置

- 已下发共享任务 `task-3`（S6-A 修订）给阶段6 总控 `stage6-lead2`；修订后由项目总控**另行安排独立复评**（不得由修订者自评）。
- 修订期间 w6 写权仍归 `stage6-lead2`；本项目总控只读。