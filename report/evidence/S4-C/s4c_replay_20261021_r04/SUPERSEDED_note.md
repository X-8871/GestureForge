# 说明：本 RunId 已被取代（S4-A 契约 r04 → r05，工具字节未变）

- `s4c_replay_20261021_r04` 绑定的是 S4-A 契约 **r04**（sha256
  `1d7fd5f02bc4948fc6aa16734bf7bd258c1be34d2141f67eb487a2449f3be350`，提交 `5ccc2313`）。
- Lead 随后把契约升级为 **r05**（sha256
  `3524d02ae410ae365a9dbfc5f04dcd9f300f8013086a076259a641f7eb8afb87`，提交 `7e5717f`），
  并把 r05 作为阶段4 离线准备的冻结契约版本；因此交付物需要绑定同一契约版本。
- r05 相对 r04 的变化（已用 `git show` 逐节核对）：
  1. 新增 `evidence_annotation.measurement_scope` 定义（关闭悬空引用）；
  2. `anomaly_accounting.candidate_overflow` 改为与 2B 参考实现一致的**硬错误**语义
     （候选数达上限 → state=ERROR、error_code=BAD_ARGUMENT(1)、detections=[]，不定义截断）；
  3. 新增 `derived_values_not_draft` 与 `plan_requirements_not_measured`，把推得值与计划要求
     移出 `draft_proposed_thresholds`（该节现仅剩 WARNING 与 `stale_age_limit_ms`）；
  4. 另有 `evidence_annotation`、`revision_note`、`state_enum`、`timing_definitions`、
     `uart_mapping`、`upstream_bindings`、`limitations` 的文档性更新。
- 对本工具的影响：**无**。本工具只读 `frozen_2a_constants`，其 22 个键集合未增删，
  工具实际校验的 9 项冻结值（阈值 0.25 含等号、NMS 0.45、每图 ≤15、5 类顺序、
  两头 5,070/20,280 B、score 与 xyxy 容限 1e-6、相对容限 0）在 r04→r05 之间逐项相同；
  该节唯一文本变化是 `candidate_theoretical_max_basis` 的描述文字（新增与 2B
  `S2A_T62_MAX_CANDIDATES` 的上游自检说明），不参与对拍。
- 三个交付物字节在 r04 之后**未做任何编辑**（`verification/s4_replay_compare.py`
  `3c2a61aeee7006ff394a6794333262f57c85aa00b86bb7cd3ecfe2ed41d32625`、
  `verification/test_s4_replay_compare.py`
  `b3cf7bf02b0b5b552ec94dcba95286302a528ea3b5139f5476e00be3e15d40d9`、
  `scripts/stage4_s4c/run_s4c_replay.py`
  `2dfccea4a2cecb59afdd3cf3ea8ed9b96c0cc590c15f6091e4b8ba06e1e565d9`）；本轮只是用同一
  份被审字节重跑并刷新契约绑定。
- 最终证据见同根下 `s4c_replay_20261021_r05`（契约 r05）。本目录内容未改写，仅为保留审计轨迹。