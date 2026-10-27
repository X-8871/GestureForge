# S5-T03 阶段4 冻结包离线消费（真实回放口径，v1，2026-10-27）

> 状态：`OFFLINE_REPLAY_CONSUMPTION_IMPLEMENTED_OFFLINE_ONLY`。本文只登记**离线主机回放**消费口径与产物，
> **不改** `S5A-G0-v2` 的任何阈值/几何/语义，也不把本文升级为真实集成、板级或关口结论。
> 机器可读产物：`report/evidence/S5-T03/s5t03_stage4_frozen_replay_20261027_r01/`。
> 相关：`S5T03_input_contract_binding_colour_v1.md`（范围标签绑定层；其 §11 实现状态表仍适用）、
> `docs/stage5/s5t03_json_contract_v1.json`（既有阶段5 JSON 契约）。

## 1. 消费对象（已冻结，现场复算）

| 项 | 值 |
|---|---|
| 共享结果契约 | `docs/stage4/s4b_shared_input_result_contract.json`（`s4-shared-io` v1.3.0、r07、`FROZEN_OFFLINE_ONLY`） |
| 契约 JSON SHA-256（本树复算） | `7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145` |
| 冻结记录 | `w4/report/evidence/S4-CTRL/s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json` |
| 冻结包目录 | `w4/report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04/`（10 个文件） |
| 包身份 | `S4-T26-GOLDEN-REBIND`；结果键 `(session_id=853466600, frame_id=1, result_seq=1)` |
| 包标注 | `replay_only=true`、`evidence_kind=offline_replay`、`buffer_scope=offline_host` |

**完整性纪律（冻结件原文）**：消费方必须先按清单**逐文件**复算 `sha256` 与 `bytes`，任一不符即拒绝消费，
**不得只校验 package.json**；并按契约 `authority_rules.drift_detection` 现场复算 `upstream_bindings`。
跨树条目按条目 `byte_basis` 在**所属工作树**复算（`git_blob_content` → `git -C <tree> cat-file blob <rev>:<rel>`）；
在别的树取 blob 会得到空输入哈希 `e3b0c442…` 并伪报漂移，本实现对该情形显式记 FAIL（判别力用例覆盖）。

## 2. 输入口径标签（取代既有 `synthetic_replay`）

| 字段 | 本任务取值 | 说明 |
|---|---|---|
| `input_kind` | `stage4_frozen_replay` | 输入是阶段4 冻结回放包，不是合成流 |
| `consumption_mode` | `replay_only` | 只用于回放内部一致性 |
| `evidence_kind` | `offline_replay` | 与冻结包 `marking.evidence_kind` 一致 |
| `buffer_scope` | `offline_host` | 离线主机缓冲，不含板级 DDR |
| `scope_statement` | `离线主机回放；不代表 PL、实物或实时检测输出` | 逐产物携带 |

- 字段名/结构沿用 `scripts/stage5_t03/s5t03_dynamic_stream.py` 的输入绑定结构（关联键、消费字段、
  检测字段），并补齐契约 `result_contract.result_record.fields` 的 `candidate_count`、
  `candidate_count_pre_threshold`、`candidate_overflow`——**不另立第二套语义**。
- 标签守卫为 fail-closed：`input_kind`/`consumption_mode`/`evidence_kind` 任一不符，或产物被改回
  `synthetic*`，产出与检查器均判失败。

## 3. 几何与对拍口径

- 换算规则**只**来自冻结参考 `verification/s5_display_geometry_reference.py`：
  `clip_unit_box` → `original_norm_to_display_px`（`round_half_up(v*(span-1))`，只在最后取整一次）
  → `border_pixel_sets`（2 px 偶数线宽居中、逐边钳入画布）。本实现不重写第二套逆映射。
- 画布 = 源帧分辨率（`fit=exact`）：回放帧 1280×720；阳性门禁样本 1440×1920（其 `input_shape_bgr`
  由同包冻结文件 `replay_forward_bridge_result.json` 提供）。
- **独立对拍**：`check_s5t03_frozen_replay.py` **不采信产物声明**，按产物 `source_ref` 回到冻结包取原始
  `xyxy`，从冻结包重新解析画布，重新换算像素并逐框、逐轴比对 `detections[].xyxy_px`。

## 4. 时间口径（注入陷阱）

| 字段 | 本冻结包取值 | 基准声明 |
|---|---|---|
| `capture_time_ns` | `1792776253000000000`（非零） | `documented_stage3_wallclock_second_unix_epoch`；`clock_domain=replay_documented_wallclock`；秒级精度；**不是** PS 单调采集计数 |
| `result_time_ns` | `null`（不可定义） | `UNAVAILABLE_OFFLINE_REPLAY_NO_MONOTONIC_PUBLISH_CLOCK`（冻结包 `stale_evaluation=NOT_RUN_…`） |
| `inference_time_ns` | `null`（不可定义） | `offline_host_elapsed_ms`（5765.3 ms，主机 CPU 墙钟）**不是** PS 推理时间 |
| `end_to_end_latency_ns` | `null`（不可定义） | 无与采集同域的发布时刻 |
| `age_result_ns` / `age_frame_ns` | `null`（不可定义） | 五元组内 `age_basis` 显式声明；`age_frame_ns` 基准=已文档化采集时刻，**绝不**用 `injection_start_ns` 冒充 |
| `stale` | `null` | `NOT_DECLARED_IN_FROZEN_PACKAGE`（包只给 `stale_evaluation`） |

- `FILE_INJECTION` 分支：`capture_time_ns` 为 **0 哨兵** ⇒ `end_to_end_latency_ns` 不可定义；
  消费者与检查器都显式拒绝"把 `injection_start_ns` 当采集时间"（有判别力用例）。
- **不伪造时间**：本包不产出任何年龄/延迟数值；若阶段4 后续补 PS 单调发布时刻，须重绑契约后重跑。

## 5. 归属纪律（防止把门禁样本冒充回放帧检出）

- 回放帧本体 `replay_frame.d9.raw_candidate_count_before_stable_nms=0`、`decoded_predictions=[]`
  ⇒ 逐帧输入记录 `state=NO_HAND`、零框（契约：`NO_HAND` 必须零框且非过期）。
- 冻结包内的阳性检测门禁样本（`test_fist_000`）**不属于回放帧**：单独落在
  `gate_evidence_projection.json`，标 `display_eligible=false`、`attribution=gate_evidence_sample_not_replay_frame`，
  **不进入显示流**，仅用于 `xyxy→像素` 逐框对拍（含 `t29_reference_predictions` 参考列表，共 2 个框实例）。

## 6. 产物与入口

| 产物 | 路径 | 说明 |
|---|---|---|
| 消费者 | `scripts/stage5_t03/s5t03_stage4_frozen_replay.py` | 冻结包 → 逐帧输入 + 五元组 + 门禁几何投影 |
| 完整性/漂移复算 | `scripts/stage5_t03/s5t03_freeze_integrity.py` | 逐文件 sha256+bytes、契约绑定、17 条绑定漂移 |
| 独立对拍检查器 | `scripts/stage5_t03/check_s5t03_frozen_replay.py` | 逐框 verdict + 标签/时间口径（退出码 0/1/2） |
| 证据驱动 | `scripts/stage5_t03/run_s5t03_frozen_replay_evidence.py` | 生成 RunId 证据包（含真实退出码） |
| 新增测试 | `scripts/stage5_t03/test_s5t03_frozen_replay.py` | 含篡改判别力用例；用例数见证据包 `console/unittest_all.txt` |
| 证据包（消费入口） | `report/evidence/S5-T03/s5t03_stage4_frozen_replay_20261027_r04/` | `manifest.json` / `summary.md` / JSON/JSONL |
| 受取代的中间 RunId | `…_r01`（套件用例数解析为 None 的缺陷）、`…_r02`/`…_r03`（定稿前的中间产物） | 保留不改写；**不得**作为消费入口 |

- 回归证据：既有 7 个 `test_s5t03_*` 模块 + 本任务新增 1 个模块（共 8 个模块）。
  用例数、`OK/FAILED` 与**真实退出码**一律以证据包 `console/unittest_all.txt`、`manifest.exit_codes`
  与 `manifest.verdict` 为准（本文不复制这些数字，避免文档与证据漂移）。

## 7. 实现状态

| 项 | 状态 |
|---|---|
| 阶段4 冻结包离线消费（真实回放口径标签、逐帧输入、几何投影、独立对拍） | **已实现（离线）** |
| `capture_time_ns` 非零传递与基准声明（`camera`/回放口径） | **已实现（离线）** |
| `FILE_INJECTION` 0 哨兵 ⇒ 延迟不可定义 | **已实现（判别力用例覆盖）** |
| `camera_live_colour` 实时采集路径 | **NOT_RUN / 未实现** |
| 板上真实回放接入 | **NOT_RUN**：需硬件 OFFER/CLAIM + 八类门禁（当前 **0/8**） |
| 真实连续帧周期 / 结果年龄 / 端到端延迟 | **NOT_RUN**（无 PS 单调发布时钟） |

### 7.1 显示路径可用性（逐项，可机检）

| 显示路径要素 | 状态 | 依据 |
|---|---|---|
| 契约结果字段齐备 | **PASS** | 每条逐帧记录通过冻结参考 `validate_result_record` |
| 几何（`xyxy`→画布像素→边框像素） | **PASS** | `clip_unit_box` → `original_norm_to_display_px` → `border_pixel_sets` |
| 帧关联键与五元组字段 | **PASS** | `session_id/frame_id/result_seq/repeat_index` + 五元组字段齐备（年龄基准显式声明） |
| 年龄 / 过期（`age_*`、`stale` 判定） | **NOT_RUN** | 需单调发布时刻；冻结包声明 `stale_evaluation=NOT_RUN_…`，本包置 `null` 而不伪造 |
| 现有 `s5t03_display_pipeline.DisplayPipeline` 直接接入 | **受限** | 其年龄路径读取 `result_time_ns`（本包为 `null`）⇒ 未用其跑年龄/stale，不另立替代口径 |

## 8. 诚实边界

- **允许**：离线回放口径下的数值一致性；task-27 结果包可被阶段5 消费。
- **禁止**：板上行为/PL 真实运行、UART 实收/真帧、真实摄像头采集质量或颜色、
  **P/4-D/G3/G4/G5 任一项通过**、把回放结果当实时结果。
- `§4.5/§7.3 未关闭`；G0/G1/G3/G4/G5 判定不归本任务；`ENABLE=0` 未变。
- 本文与证据只读消费 w4 冻结件，**未**写 w4/主目录，**未**接板卡，**未**启动
  vivado/xsdb/hw_server/vitis/xsim，**未**终止任何进程。

## 9. RunId 取代登记（不改写被取代目录）

| RunId | 状态 | 处置 |
|---|---|---|
| `s5t03_stage4_frozen_replay_20261027_r01` | **受取代（失败证据）** | 证据驱动的真实缺陷：只解析 `unittest` 的 **stdout**，而 `-v` 详细输出走 **stderr** ⇒ `summary.md`/`manifest.json` 的套件用例数写成 `Ran None`、`OK=False`（其余数字正确）；目录保留不改写，**不得**作为消费入口 |
| `s5t03_stage4_frozen_replay_20261027_r02` | **受取代（中间产物）** | 修复解析后数字正确，但其源码哈希绑定早于本文档与 `display_path_compatibility` 定稿；目录保留不改写 |
| `s5t03_stage4_frozen_replay_20261027_r03` | **受取代（中间产物）** | 代码/产物自洽，但本文档当时硬编码的用例数过时（138 vs 实测 139）⇒ 文档已改为不复制数字并指向最终 RunId；目录保留不改写 |
| `s5t03_stage4_frozen_replay_20261027_r04` | **当前消费入口** | 代码/文档定稿后重跑，全部源码哈希与产物自洽 |