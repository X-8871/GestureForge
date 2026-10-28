# 阶段4 离线冻结 r5 · 验证 RunId（post-freeze 验证证据）

- 被验证对象：annotated tag **`stage4-offline-freeze-20261028-r5`**（冻结包 `../stage4_freeze_20261028_r05/`）。
- **顺序**：冻结提交（tag r5，只含冻结包 6 个输入类文件） → **本验证提交**。本目录**不在** tag r5 内。
- 记录：`--selftest` exit 0；仓库内 exit 0（115/115）；真 `git archive(tag r5)` 导出 + `--disk` exit 0（4359 文件，115/115）；旧 F1–F8 语义验证器 exit 1（7/8，F5）。
- 日志为 `*.stdout.txt`（`*.log` 属 gitignore，不入库）。
- 边界：全离线；`ENABLE=0`；不改写既有证据；不 push；不主张阶段4 通过/G3/G4/G5。
