# 指针：本目录 summary 的 C1 措辞范围以增补件为准（关闭 S5-R OBS-02）

- 时间：2026-10-22 10:50（UTC+8）
- 本目录（`s5c_regression_20261021_r04`）的全部原始产物**未被修改**，其 PASS 与 13/13 退出码不变。
- 但本目录 `summary.md` 中「离散字段全等」的**措辞范围**已被上级目录的增补件收窄：
  - `../S5C-ADDENDUM-20261022-001-C1-discrete-fields.md`（人读）
  - `../c1_discrete_fields_claim_v2.json`（机器可读）
- 收窄后准确说法：6 个可由上游承载的离散字段（`frame_id`、`detection_count`、`class_id`、`class_name`、`source_order`、`box_count`）**COMPARED 且全等**；`nms_decision`、`output_order` 为 **NOT_COMPARED（上游未承载）**。
- 相关审查：`../../S5-CTRL/S5-R01/s5r01_20261022_r01/independent_review.md`（F-01）与 `../../S5-CTRL/S5-R01/s5r01_20261022_r02/closure_review.md`（CLOSED）。