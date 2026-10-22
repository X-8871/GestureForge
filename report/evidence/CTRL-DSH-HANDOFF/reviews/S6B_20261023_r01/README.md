# S6-B/S6-C 实现轮独立复评（CHANGES_REQUIRED）

- 被审版本：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，提交 **`43f7995`**（S6-A 基线 r06=`04ea58e1`，契约 v1.5）
- 评审方：DSH 项目总控派出的**独立 Reviewer（实现轮）**；隔离目录 `tmp/review/S6B_20261023_r01/`；审查前后 w6 `git status` 为空、HEAD 未变
- 时间（UTC+8）：2026-10-23 02:41–03:00
- **结论：`CHANGES_REQUIRED`（阻断 1；非阻断 10）**
- **语义层未发现行为级缺陷**：38 项自构造对抗序列 + 22 条用例全部复现；阻断项在**证据/声明层**。
- 边界：只覆盖 S6-B/S6-C，不代表 G0/G2/G3/G4/G5；不评价 S6-A 规格本身（但 BLK-1 根因涉及 S6-A 的 `reachability.M4`／`U6-12`，已转 S6-A 侧）。

## 1. 阻断 `BLK-1`：M4 可达性/覆盖声明与同包自证据矛盾（证据失实）

- 声明：`reachability_notes.json`、`limitations_not_executed.json`、`s6b_run_summary.md:43` 与提交信息称"`T6-S04`=500ms ≥ `T6-L02`=300ms → M10 先命中 → M4 不可达、不计入覆盖"。
- 反证（同包）：用例 `C4-jitter-reset` 的 expected 就是 `transitions:["M1","M4"]`，实测日志 `M4@f7`（reason「抖动容忍耗尽且候选停留 ≥ `T6-S04`（M10 未命中）」），且该用例被 `runbook_matrix_coverage` 的"短暂抖动"类收录。
- 根因：规格 §3 的 `TARGET_CONTINUES` **不含** `score≥P02` → 低分/位移造成的 `WINDOW_MATCH` 中断仍刷新 `t_last_target_continues` 且 `miss_streak` 不增 → **M10 不会先命中**。
- 影响：以"不可达"为依据的 `U6-12`（删 M4/`T6-S04` 或改 `S04<L02`）会**删掉实际可达且已被覆盖的迁移**。
- 关闭条件：(a) 重推可达性，把 **M4 标为可达并计入覆盖**（或给出不可达所需的额外前提）；(b) 同步 S6-A 侧 `reachability.M4`／`U6-12`；(c) 证据包重生成，`hashes_sha256.txt`/`delivery_manifest.json` 复算一致。

## 2. 评审实测（真实退出码）

| # | 命令 | 退出码 |
|---|---|---|
| 1 | 隔离副本复跑驱动 | **0**（`run_report.json` 与 22 个 JSONL 与提交版**逐字节相同**，0.11s） |
| 2 | `s6b_probe.py` | **0**（baseline 0 / expected_tampered **2** / wrong_semantics **1** / threshold_tampered **1**） |
| 3–4 | `check_stage_delivery --mode inputs/evidence` | **0 / 0**（输出与入库 `*_mode_output.txt` 字节相同） |
| 5 | 注入 `T6-S02=4` / `T6-S01=100` / `T6-P02=0.7` | **1 / 1 / 1**（行为随 JSON 改变 ⇒ 阈值未写死） |
| 6 | 参数改 `APPROVED`、删必需参数 | **2**（装载即拒） |
| 7 | 篡改 expected 后运行 | **2**（"预期在冻结后被修改…拒绝运行"） |
| 8 | 旧口径注入（完成时刻记在第 `S02` 帧） | **1**（`C9c` FAIL：预期 233100000、实际 166500000；还原后 0） |
| 9 | 38 项自构造对抗序列 | **0** |

**已证事实**：22/22 可复现；4 探针如声明；两项交付检查真实 exit 0；清单无缺失、哈希全对；24 项仍全 `PENDING_APPROVAL`；无虚假"已审查/已通过"；范围声明明确限定"注入输入 + 虚拟单调时钟"。

## 3. 非阻断 10 项

| # | 要点 |
|---|---|
| `N-01` | 版本标注漂移：`s6_core.py` docstring/decision_notes（6 处）、`s6_params.py` docstring、`expected_derivation_note`、`reachability_notes.derived_from`、summary 标题、`s6b_frozen_interface_v1.json` 仍写 v1.4/r05（实际 v1.5/r06） |
| `N-02` | "21 例"残留（`probe_summary` baseline note、summary:42、builder:214），实际 22 条 |
| `N-03` | `runbook_matrix_coverage` 11 类只映射 21 条，`C9c-30fps-later-of` 未被任何类收录 |
| `N-04` | 日志字段不全：`ACTION_FAILED/UNOBSERVED`=0、`action_type/target_id/acquisition_id/t_trigger_ns`=0（`run_report` 无 `action_records`）；B09/B10 依据分类未记；§4 的 `transition_candidates`/`S_CONFLICT_RESOLVED` 未实现（`OUT_*`/`SUP_CONFLICT` 常量定义未用） |
| `N-05` | `M11` 不递增 `acquisition_id`（仅目标切换递增）→ `C3` 两次获取共用 0，B11/B15 的"新获取 id"记录不成立（行为本身正确） |
| `N-06` | `REQUIRED_PARAMETER_IDS` 仅 20 项：删非必需 `T6-A03` 仍能装载并 22/22 PASS ⇒"强制 24 项"只对在表参数成立 |
| `N-07` | `state=NO_HAND` 却带 detections 时静默忽略（`invalid=0`），未按 §11.3 计非法 |
| `N-08` | IDLE 已选出 `current_target` 时不求值 M10（实测距锚点 900ms > `L02` 仍 IDLE），规格 M10 写"任意有目标状态"，需在 `decision_notes` 声明 |
| `N-09` | `expected_freeze.json` 的 `cases_file_sha256` 运行时未校验；仅阈值内 score 篡改（0.9→0.31）仍 exit 0（行为改变型 0.10→1 由断言兜底） |
| `N-10` | `delivery_manifest.source_commit=6560b694…` **不在被审谱系**（非 `43f7995`、非父 `04ea58e`）；49 条文件哈希均与当前文件一致，内容绑定有效但提交归属不实 |

## 4. 处置

- 已派 `task-9`：BLK-1 重推（M4 可达）+ 证据重生成 + `N-01..N-10`；同时把 S6-A 侧 `reachability.M4`／`U6-12` 同步纳入。
- 建议把 `build_case_matrix.py`（只依赖 `json`/`pathlib`、**不 import 状态机** → 证明 expected 非回填）随证据登记。
- 本记录只搬结论与边界；S6-B 实现与证据仍在 w6。