# 阶段4 离线冻结 r4 · 验证 RunId（post-freeze 验证证据）

- 被验证对象：annotated tag **`stage4-offline-freeze-20261028-r4`**（冻结包 `../stage4_freeze_20261028_r04/`）。
- **提交顺序**：冻结提交（tag r4）→ **本验证提交**；本目录的文件描述冻结提交，因此**不出现在 tag r4 内**，其自身清单绑定包含它自己的验证提交。
- 本 RunId 记录：`--selftest`（5 例）、仓库内 115/115、**真 `git archive(tag r4)` 导出 + `--disk` 115/115**（导出文件数见 `exit_clean_export.txt`）、旧 F1–F8 语义验证器（exit 1，7/8，F5）。
- 日志以 `*.stdout.txt` 保管（`*.log` 属 gitignore，不入库）。
- 边界：全离线；`ENABLE=0`；不改写既有证据；不 push；不主张阶段4 通过/G3/G4/G5。
