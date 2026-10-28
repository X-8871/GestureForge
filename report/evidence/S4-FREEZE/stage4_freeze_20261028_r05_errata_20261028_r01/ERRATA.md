# ERRATA · 阶段4 离线冻结 r5（not_frozen_count 勘误）

- **位置**：`report/evidence/S4-FREEZE/stage4_freeze_20261028_r05/results_freeze.json`、
  `report/evidence/S4-FREEZE/stage4_freeze_20261028_r05/frozen_set_report.json` 的 `not_frozen_count` 字段。
- **r5 包内值**：35（统计口径错误，多记 3 项）。
- **正确值**：**32** —— 由 `frozen_set.not_frozen` 条目数直接计算（`len(frozen_set.not_frozen)`）；`git status` 实为 32 项，matched=32、undeclared=[]。
- **影响范围**：仅该数字字段；**冻结身份、115 个成员、11 项产物身份、门禁结论、导出结果均不受影响，冻结包文件字节未改动**。
- **处置**：本 errata RunId 记录勘误；**tag r5、`frozen_set.json`、冻结包 6 个文件一律未动**。
- **根因修复**：生成器 `scripts/stage4_s4ctrl/build_freeze_package_manifests.py` 现强制
  `not_frozen_count = len(frozen_set.not_frozen)`，并断言其等于 `git status` 声明匹配数；不一致且未允许修正时 **exit 8**（禁止手填/另算）。
- 边界：全离线；`ENABLE=0`；不 push；不主张 G3/G4/G5。
