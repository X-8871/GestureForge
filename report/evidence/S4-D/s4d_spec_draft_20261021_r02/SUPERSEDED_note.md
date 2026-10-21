# SUPERSEDED — r02 已被 r03 取代

- 本运行 `report/evidence/S4-D/s4d_spec_draft_20261021_r02/` 是 S4-D 复审修复轮（D1–D8）的证据，已被 `report/evidence/S4-D/s4d_spec_draft_20261021_r03/`（复审 R1/O1/O2 修复轮）**取代（superseded）**。
- 本目录原文件未改动、未删除；其中 `selfcheck_result.json`、`coverage_matrix.json`、`letterbox_geometry_fixtures.json` 是 **R1 修复之前**那一版文档/JSON 的历史自检记录（当时 C1–C10 全 PASS、覆盖 48/48）。
- 本清单 `delivery_manifest.json` 绑定的是 **R1 修复前** 的三份交付物哈希。在 `docs/stage5/S5_stage5_display_spec_draft.md`、`docs/stage6/S6_stage6_interaction_spec_draft.md`、`docs/stage6/s6_interaction_thresholds.json` 被 R1/O1/O2 修改后，对本目录重跑 `python -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S4-D/s4d_spec_draft_20261021_r02/delivery_manifest.json` 会报告**预期的文档哈希漂移**——这是被取代证据的固有现象，不是新缺陷；r03 的 `commands.json` 记录了该重跑的实测结果。
- 复核、复审与被审版本一律以 **r03** 为准；本目录仅作历史留存（RunId 不覆盖重跑）。
- 未执行任何显示/交互/上板实测；本说明不构成任何验收依据。