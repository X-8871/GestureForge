# 阶段5 离线 replay/display JSON 契约 v1（`gestureforge_s5t03_json_contract` **1.0.3**）

- 冻结时刻（UTC+8）：2026-10-27 01:10；维护：DSH 阶段5 总控（w5 接管后）
- 机器可读契约：[`s5t03_json_contract_v1.json`](s5t03_json_contract_v1.json)（**校验器只读此文件**，字段清单不在代码里硬编码）
- 校验器：[`../../scripts/stage5_t03/validate_s5t03_json.py`](../../scripts/stage5_t03/validate_s5t03_json.py)
- 定位：供**阶段6/7 消费**的稳定接口；**JSON/日志为权威**，`keyframes/*.png` 与 `demo.mp4` **不作验收依据**。
- 边界：只约束**离线合成回放**产物（`input_scope_label=synthetic_replay`、`status=PRELIMINARY`）；**真实回放接入 / 板上动态映射 / 摄像头 = NOT_RUN**；**G0/G1/G3/G4/G5 均未通过**。

> **v1.0.1 变更（关闭 JSON 契约专项复审 B1–B6）**：
> B1 逐帧 **stable 必需子集**纳入校验（`assertion_mode` 由"稳定必需"降为**稳定可选**——短跑包未产出该键）；
> B2 `schema_version` **值**受守卫；B3 `manifest.files[].sha256` **实测内容**；B4 `checks.passed` 必须为 `true` 且与 `failures` 自洽；
> B5 契约本体缺键 **fail-closed 退出码 2**；B6 退出码语义固定（0/1/2）。
> 另：`results.stream.frame_period_ns` 升为**稳定**（阶段6 T6-A03 帧周期来源）、`manifest.tools` 记法改为 **role→对象映射**、
> 登记事件日志拒绝原因键 **`rr`**、补充未分类字段策略与交叉一致性检查（run_id/source_commit/schema_version）。

## 1. 产物与权威性
| 产物 | 权威 | 说明 |
|---|---|---|
| `results.json` | ✅ | 口径、不变量、计数、边界、关键帧索引、限制、NOT_RUN |
| `frame_assertions.jsonl` / `.jsonl.gz` | ✅ | 逐帧断言；长跑用 gzip + compact |
| `logs/events_*.jsonl(.gz)` | ✅ | 帧级事件日志，可**独立复算**全部计数（键位见 §6） |
| `manifest.json` | ✅ | 文件哈希、工具/参数哈希、检查结论、限制、NOT_RUN |
| `keyframes/*.png`、`demo.mp4` | ❌ | 人工抽检/演示；**不得**作为验收证据（`demo_only=true`） |
| `summary.md` | ❌（派生） | 与本契约产物冲突时**以 JSON/日志为准** |

## 2. 三类产物（由字段自动判定，不靠猜）
| kind | schema_version（值受守卫） | 逐帧断言 | 必需 results 字段 |
|---|---|---|---|
| `replay_display` | `gestureforge_s5t03_replay_display_v1` | 必需 | `counters, boundary_cases, keyframes, demo, limitations, not_run` |
| `long_run_replay` | `gestureforge_s5t03_long_run_replay_v1` | 必需 | 上述 + `invariants, stream, assertion_count` |
| `multi_geometry_render` | `gestureforge_s5t03_multi_geometry_render_v1` | **不需要** | `geometries, numeric_checks, limitations, not_run` |

公共必需：`schema_version, run_id, task_id, generated_utc8, source_commit, status, input_scope_label, checks`。
`checks` 必须是对象且 `passed` 为布尔、`failures` 为数组；**`passed` 必须为 `true`**（失败运行不得作为交付证据）。
交叉一致性：`manifest.run_id / source_commit / schema_version` 必须与 `results.json` 一致。

**计数语义（14 键，稳定）**：`frames_committed, overlay_drawn_frames, boxes_drawn, warmup_frames, dropped_frames, timeouts, error_results, invalid_records, stale_cleared, duplicate_results, duplicate_frame_id_results, out_of_order_results, zero_hand_frames, zero_area_dropped`。

**长跑不变量**：必需 10 键 `period_count, period_ns, virtual_elapsed_ns, required_ns, margin_ns, canonical_long_run, one_commit_event_per_frame, commit_timestamps_monotonic, recompute_matches_online, no_deadlock`；实际产物含 15 键（另有 `virtual_elapsed_s, margin_within_one_period, min_frames_for_canonical, deadlock_evidence` 等，属细节）。
- `period_count = frames − 1`；`virtual_elapsed_ns = period_count × period_ns ≥ required_ns`；`margin_ns ∈ [0, period_ns)`；
- `one_commit_event_per_frame` 是**死锁判据**（每显示帧恰好一次 overlay 提交）；`no_deadlock` 仅表示"断言覆盖全部帧"，其口径见 `deadlock_evidence`。

**逐帧断言（stable 必需，校验器逐帧检查）**：`frame_index, displayed_frame_id, result_frame_id, result_seq, state, drawn, boxes, stale_effective, stale_reason, skip_reason, age_result_ns, age_frame_ns, display_semantics, input_scope_label`。
**stable 可选**：`zero_area_dropped, assertion_mode, input_frame_sha256, seed, canvas, overlay_commit_ns, rejects_this_frame, coordinate_mapping, hud, checks, render` 等。
⚠️ **`assertion_mode` 是可选**：短跑包（full detail）不产出该键；长跑包（compact）产出 `compact`。消费者不得假定其存在。

## 3. 稳定 vs 细节（阶段6/7 只可用"稳定"）
- **稳定（可依赖）**：公共必需字段、14 项计数语义、长跑不变量必需键、逐帧 stable 必需子集、
  **`results.stream.frame_period_ns`（短跑与长跑均提供；阶段6 T6-A03 的帧周期来源）**、
  `manifest.files[].path/sha256`（校验器**实测**）、`manifest.tools.<role>.path/sha256`、`limitations`、`not_run`。
- **细节（不得依赖）**：`process_seconds`、`render.*`、`demo.*`、`keyframes[]`、`artifacts.*`、`logs.*`、
  `recomputed_counters`、`input.*`、`submit_verdicts`、`commits`、`hud_last`、`five_tuples_head`、
  `odd_padding`、`canvas_fit`、manifest 侧的 `counters/invariants/checks/logs/render/demo/numeric_checks/goal_reached/summary/scope_statement`、`console/*`、PNG/MP4。
- **未分类策略**：未在 stable/detail 中**逐键**列出的**容器内字段**一律视为 detail；消费者不得依赖；若阶段6/7 需要，走版本升级流程加入 `stable_for_consumers`。

## 4. 给阶段6/7 的消费口径
- **阶段6（T6-A03）**：`t_effective − window_complete` 的帧周期取 **`results.stream.frame_period_ns`**（短跑与长跑均有，稳定）；
  帧关联消费 `results.counters` + 逐帧 stable 必需子集。
  ⚠️ 本轮**没有**板上 PS 绘制完成时刻语义（板上动态映射 = NOT_RUN）；不得把离线虚拟步长当作板上实测值。
- **阶段7**：只消费 `schema_version`（**值受校验器守卫**）+ 稳定字段；不得依赖仓库路径、PNG/MP4 或摘要文本。
- 若需唯一拒绝原因：**以事件日志 `rr` 为准**（见 §6 与 `known_inconsistencies`）。

## 5. 版本规则与退出码
1. 语义变化（字段含义/单位/取值范围）⇒ 提升 `schema_version` 值，**不原地修改 v1**；
2. 仅新增可选字段可在 v1 内进行，须在 `detail_not_for_consumers` 或本文档说明；
3. 删除/重命名稳定字段 ⇒ 破坏性变更，新建版本并登记迁移说明；
4. 契约本体新增必填键属契约版本提升；校验器对**契约缺键**必须 fail-closed；
5. 校验器退出码：**0** 全部通过 / **1** 违约（含 `checks.passed` 非 true、哈希不符、schema_version 值不符）/ **2** 输入或环境错误（契约缺失或不完整、包目录不存在、`--packages-from` 文件不存在、未指定包）。

## 6. 事件日志键位（权威可复算来源，**与 `.json` 的 `event_log_fields` 逐字一致**）
> **v1.0.2/v1.0.3 更正**：本节早期版本曾把 `frame_assertions` 的字段名误当事件日志键位（幻影键
> `rseq/state/drawn/boxes/sr/sk/ar/af/zd/verdict/outcome`）。现一律以下列 **compact 键**为准，
> 图例出处：`docs/stage5/s5t03_offline_skeleton_params_v1.json`
> `#/newly_frozen_for_skeleton_only/log_artifacts/compact_fields_result_submit` 与 `.../compact_fields_overlay_commit`。
> 校验器会读 `logs/events_*.jsonl(.gz)` 的键集与本节/`.json` 声明比对，漂移即违约。

- **submit 记录（11 键）**：`t, fid, sid, seq, oc, vf, rr, ri, rd, rb, pri`
  （`t="sub"`；`oc`=outcome；`vf`=verdict；`rr`=reject_reason；`ri/rd/rb/pri`=repeat 相关）。
- **commit 记录（12 键）**：`t, dfid, ts, rfid, sid, seq, st, dr, bx, za, se, w`
  （`t="commit"`；`dfid`=displayed_frame_id；`ts`=overlay_commit_ns；`st`=state；`dr`=drawn 0/1；
  `bx`=boxes；`za`=zero_area_dropped；`se`=stale_effective 0/1；`w`=warmup 0/1）。
- **拒绝原因键是 `rr`**（不是 `reason`）；`results.submit_verdicts[].reject_reason` 是另一路描述，
  二者可能不同（见 `known_inconsistencies`）。

## 7. 已知不一致（登记，不在 v1 内统一）
| id | 描述 | 消费规则 |
|---|---|---|
| `reject_reason_two_forms` | 同一被拒提交：`submit_verdicts[].reject_reason`（如 `derived:duplicate`）与事件日志 `rr`（如 `duplicate_result_key`）可能不同；仅 `submit_verdicts` 侧带 `reject_reason_source` | 需要唯一原因时**以事件日志 `rr` 为准**；统一留待后续版本 |

## 8. 校验方式（只读）
```
python -B scripts/stage5_t03/validate_s5t03_json.py \
    --package report/evidence/S5-T03/s5t03_offline_replay_display_20261026_r06 \
    --package report/evidence/S5-T03/s5t03_offline_long_run_replay_20261026_r04 \
    --package report/evidence/S5-T03/s5t03_multi_geometry_render_20261026_r02
```
**注意**：`CHECKS_OK` 仅表示**结构契约与文件哈希**通过，不代表接口语义正确、测试成功、独立审查通过或 G0/G2/G4/G5。