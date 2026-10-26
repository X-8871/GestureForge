# 阶段5 离线 replay/display JSON 契约 v1（`gestureforge_s5t03_json_contract` 1.0.0）

- 冻结时刻（UTC+8）：2026-10-26 23:50；冻结人：DSH 阶段5 总控（w5 接管后）
- 机器可读契约：`docs/stage5/s5t03_json_contract_v1.json`（**校验器只读此文件**，字段清单不在代码里硬编码）
- 校验器：`scripts/stage5_t03/validate_s5t03_json.py`
- 定位：供**阶段6/7 消费**的稳定接口；**JSON/日志为权威**，PNG/关键帧与 `demo.mp4` 一律**不作验收依据**。
- 边界：本契约只约束**离线合成回放**产物（`input_scope_label=synthetic_replay`、`status=PRELIMINARY`）；**真实回放接入 / 板上动态映射 / 摄像头路径 = NOT_RUN**；**G0/G1/G3/G4/G5 均未通过**。

## 1. 产物与权威性
| 产物 | 权威 | 说明 |
|---|---|---|
| `results.json` | ✅ | 口径、不变量、计数、边界、关键帧索引、限制、NOT_RUN |
| `frame_assertions.jsonl` / `.jsonl.gz` | ✅ | 逐帧断言（`assertion_mode=full/compact`）；长跑用 gzip + compact |
| `logs/events_*.jsonl(.gz)` | ✅ | 帧级事件日志，可**独立复算**全部计数 |
| `manifest.json` | ✅ | 文件哈希、工具/参数哈希、检查结论、限制、NOT_RUN |
| `keyframes/*.png`、`demo.mp4` | ❌ | 人工抽检/演示；**不得**作为验收证据（`demo_only`） |
| `summary.md` | ❌（派生） | 与本契约产物冲突时**以 JSON/日志为准** |

## 2. 三类产物（由字段自动判定，不靠猜）
| kind | schema_version | 逐帧断言 | 必需 results 字段 |
|---|---|---|---|
| `replay_display` | `gestureforge_s5t03_replay_display_v1` | 必需 | `counters, boundary_cases, keyframes, demo, limitations, not_run` |
| `long_run_replay` | `gestureforge_s5t03_long_run_replay_v1` | 必需 | 上述 + `invariants, stream, assertion_count` |
| `multi_geometry_render` | `gestureforge_s5t03_multi_geometry_render_v1` | **不需要** | `geometries, numeric_checks, limitations, not_run` |

公共必需：`schema_version, run_id, task_id, generated_utc8, source_commit, status, input_scope_label, checks{pased,failures}`（其中 `checks.passed` 必须与驱动退出码一致）。

**计数语义（14 键，稳定）**：`frames_committed, overlay_drawn_frames, boxes_drawn, warmup_frames, dropped_frames, timeouts, error_results, invalid_records, stale_cleared, duplicate_results, duplicate_frame_id_results, out_of_order_results, zero_hand_frames, zero_area_dropped`。

**长跑不变量（稳定）**：`period_count = frames − 1`、`virtual_elapsed_ns = period_count × period_ns ≥ required_ns`、`margin_ns ∈ [0, period_ns)`、`one_commit_event_per_frame`（每显示帧恰好一次 overlay 提交 ⇒ 死锁判据）、`commit_timestamps_monotonic`、`recompute_matches_online`、`no_deadlock`（口径＝断言覆盖全部帧，其证据字段为 `deadlock_evidence`）。

**逐帧断言（稳定子集）**：`frame_index, displayed_frame_id, result_frame_id, result_seq, state, drawn, boxes, zero_area_dropped, stale_effective, stale_reason, skip_reason, age_result_ns, age_frame_ns, display_semantics, input_scope_label, assertion_mode`。

## 3. 稳定 vs 细节（阶段6/7 只可用"稳定"）
- **稳定（可依赖）**：上表全部必需字段、14 项计数语义、长跑不变量、逐帧断言稳定子集、`manifest.files[].path/sha256`、`manifest.tools[].path/sha256`、`limitations`、`not_run`。
- **细节（不得依赖）**：`process_seconds`、`render.*`（Pillow 版本、字体身份、色表）、`demo.*`、`keyframes[].png_path`、`artifacts.*`、`logs.*`、`manifest.eol_status`、`manifest.manifest_refreshed_utc8`、`console/*`、PNG/MP4。

## 4. 给阶段6/7 的消费口径
- **阶段6（T6-A03）**：基线 `t_effective − window_complete` 可用的帧周期取 `results.stream.frame_period_ns`（长跑）或短跑 `results.stream`；**帧关联/计数**消费 `results.counters` + 逐帧断言稳定子集。
  ⚠️ 本轮**没有**板上 PS 绘制完成时刻语义（板上动态映射 = NOT_RUN）；不得把离线虚拟步长当作板上实测值使用。
- **阶段7**：只消费 `schema_version` + 稳定字段；不得依赖本仓库路径、PNG/MP4 或摘要文本。
- **一个被拒提交可能存在两处原因串**（`submit_verdicts.reject_reason` 与事件日志 `reason`），两者均已带来源标注；阶段6 若需唯一原因，**以事件日志为准**并在后续版本显式统一（登记为已知不一致，未在 v1 变更）。

## 5. 版本规则
1. **语义变化**（字段含义/单位/取值范围）⇒ 必须提升 `schema_version` 版本号，**不原地修改 v1**；
2. **仅新增可选字段**可在 v1 内进行，且须在 `stability.detail_not_for_consumers` 或本文档说明；
3. **删除/重命名稳定字段**属破坏性变更 ⇒ 新建版本并登记迁移说明；
4. 校验器 `--contract` 可指向新契约文件，便于并存校验。

## 6. 校验方式（只读）
```
python -B scripts/stage5_t03/validate_s5t03_json.py \
    --package report/evidence/S5-T03/s5t03_offline_replay_display_20261026_r06 \
    --package report/evidence/S5-T03/s5t03_offline_long_run_replay_20261026_r04 \
    --package report/evidence/S5-T03/s5t03_multi_geometry_render_20261026_r02
```
退出码：`0` 全通过 / `1` 存在违约 / `2` 输入或环境错误。
**注意**：`CHECKS_OK` 仅表示**结构契约**通过，不代表接口语义正确、测试成功、独立审查通过或 G0/G4/G5。