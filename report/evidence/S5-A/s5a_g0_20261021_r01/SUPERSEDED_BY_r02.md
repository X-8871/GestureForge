# 说明：`s5a_g0_20261021_r01` 已被 `s5a_g0_20261021_r02` 取代

- 时间：2026-10-21 23:00（UTC+8）
- 原因：r01 生成后，Lead 对 `docs/stage5/s5a_stage5_display_g0_fields.json` 做了两处**证据绑定补实**（S4-C 黄金 SHA256 由 `TBD_RECOMPUTED_BY_S5C` 换成真实值 `c5d25c64…`；计划文件补 `sha256_this_worktree_copy`）并新增 S4-B 文件哈希；r01 的 `run_manifest.json` 因此绑定了**旧**契约哈希。
- 处理：**不覆盖、不删除** r01（保留为过程证据）。
- **权威绑定指向已更正（2026-10-22 10:45，关闭 S5-R 发现 F-03）**：本自检的权威证据是 `report/evidence/S5-A/s5a_g0_20261021_r03/`（契约 `8eac7007…`、参考实现 `4d9fe369…`）。r02 本身也已被 r03 取代（见 `../s5a_g0_20261021_r02/SUPERSEDED_BY_r03.md`），故本条不再指向 r02。
- r01 的结论未被推翻：其 unittest 与 r03 同为退出码 0（26/26 PASS）。差异仅在契约 JSON 与参考实现的哈希绑定字段。