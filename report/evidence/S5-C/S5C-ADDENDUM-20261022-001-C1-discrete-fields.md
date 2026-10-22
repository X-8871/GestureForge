# S5C-ADDENDUM-20261022-001｜C1「离散字段全等」口径收敛（关闭 S5-R 发现 F-01）

- 提出时间：2026-10-22 10:45（UTC+8）
- 作者：DSH 阶段5 总控（Lead）。**原 Developer `dev-s5c` 已不可用（子代理失败退出）**，本增补由 Lead 代写，归属明确。
- 性质：**增补说明，不覆盖、不修改** `s5c_regression_20261021_r04` 的任何原始产物；r04 的 PASS 结论与退出码不变，但其 summary 中「离散字段全等」的**措辞范围被本增补收窄**。
- 触发：独立审查 `report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r01/independent_review.md` 发现 **F-01（MEDIUM）**。

## 1. 事实

- 阶段5 契约 `docs/stage5/s5a_stage5_display_g0_fields.json` 的 `coordinate_gate.A_numeric_chain.discrete_fields_must_match` 沿用 2A 规格第 75 行，列出 **8** 个离散字段：`frame_id`、`detection_count`、`class_id`、`class_name`、`source_order`、`nms_decision`、`output_order`、`box_count`。
- S5-C 的 C1 检查实际比较 **6** 个：`frame_id`、`detection_count`、`class_id`、`class_name`、`source_order`、`box_count`。
- `nms_decision` 与 `output_order` 在上游输入中**不存在**：
  - S4-C `replay_golden_109.json` 的 `detections_expected` 与 `detections_actual` 均**无**这两个字段；
  - 阶段4 S4-A 契约 `detection_record.fields` 同样**未承载**这两个字段（其 `nms_decision`/`output_order` 语义在阶段4 由「稳定 tie 顺序」与 `source_order` 隐式体现，不落成独立字段）。
- 因此 C1 既无法比较它们，也未在 r04 的 summary / run_manifest / limitations 中显式登记，而 summary 以「离散字段全等」呈现 → 属**措辞范围大于实测范围**（不构成伪造，但属不精确声明）。

## 2. 收窄后的准确声明（替代 r04 summary 的措辞）

| 字段 | C1 状态 | 依据 |
|---|---|---|
| `frame_id`、`detection_count`、`class_id`、`class_name`、`source_order`、`box_count` | **COMPARED（全等）** | S4-C golden 逐样本逐框比较，109/109、104 框、mismatch 0 |
| `nms_decision`、`output_order` | **NOT_COMPARED（上游未承载）** | S4-C golden 与 S4-A `detection_record.fields` 均无该字段；非本层可比较项 |

- 间接约束（不替代直接比较，仅降低风险）：C2 的「显示层 accepted 集合 ≡ 阶段4 框集合（对象别名，不重排）」与 Gate D 的「逐字节位型一致」共同约束了输出顺序与 NMS 结果的传递一致性；这**不是**对 `nms_decision`/`output_order` 的逐值比较。
- 后续动作（正式阶段5 G0 建议）：把契约清单拆分为「本层可比较 / 上游未承载」两段并注明依据；届时应与阶段4 契约同步，本阶段不擅自改冻结正文。

## 3. 绑定

| 项 | 值 |
|---|---|
| 被增补运行 | `report/evidence/S5-C/s5c_regression_20261021_r04`（权威，未修改） |
| 该运行 manifest SHA256 | `61c0d507f022de3ce2e57255b284df2e7f4ed5f3a0115b728fbd8561313120a9` |
| 检查器 | `scripts/stage5_s5c/check_s5c_stage4_regression.py` SHA256 `703959a2df4d230e596baca52e556b782f609efaf19b27d877ad1511eebfc5ab` |
| 契约 | `docs/stage5/s5a_stage5_display_g0_fields.json` SHA256 `8eac70076c3ba39de0c615bcc08b66bcc45f3fe87f0449a9eb3e32a318709911` |
| 机器可读版 | 同目录 `c1_discrete_fields_claim_v2.json` |
| 审查发现 | F-01（MEDIUM），关闭条件见 `independent_review.md` |