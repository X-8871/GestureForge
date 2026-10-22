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

## 5. 复核更正（DSH 项目总控，2026-10-22 19:52）

1. **「文档缺 H-5 / M2 / M10」是误报**：用 `git show 1fe4648:docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` 核对，三项在 r01 中分别位于**第 41 / 66 / 74 行**。上一轮 `compare_spec.py` 的正则要求 `**：` 形式与特定来源状态写法，过严而漏检。→ 本记录 §2.2 与主 STATE 中「文档缺 H-5、M2/M10」的表述**作废**，以本节为准。`T6-S03`、`E_FRAME_CONFLICT`、`A_DISPLAY_STATE`、`M14` 的差异仍成立（阶段6 已在 r02 处理）。
2. **自检命令复现**：`s6_g0_selfcheck.py` 的 C11 要求 `--evidence-dir`（不静默跳过，属合理设计）。DSH 用 r01 时期登记的旧命令（无该参数）复跑得到 `FAILED` exit 1，系**使用旧命令**所致；r02 的 `S6A_run_summary.md` 与 w6 STATE 均已登记该参数，按完整命令复跑为 `ALL_PASS` exit 0。**不构成 r02 缺陷**。
3. 我方独立复核通过项（r02，提交 `3b59674`）：带 `--evidence-dir` 自检 `ALL_PASS` exit 0；`check_stage_delivery.py --mode inputs` 与 `--mode evidence` 均 `CHECKS_OK` exit 0（绝对 `--project-root`）；`W_min` / `TARGET_CONTINUES` / `WINDOW_MATCH` / `H-10` / `cooldown_policy` 在 MD 与 JSON 双侧均出现；旧包失败证据文件在位；24 项参数仍为 `PENDING_APPROVAL`。
4. 复评由 DSH 另派的**新** Reviewers 进行（非修订者、非本轮评审者）；其结论回来前，r02 **不得**作为 G0 批准输入。