# DSH-20261027-013：阶段4 契约漂移**已核明为重绑台账**，附精确请求

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T15:18:15+08:00｜性质：**report/decision（跨方请求，续 DSH-20261027-012）**
- 核明结论：漂移**不是结果契约语义变化**，而是契约内 `post_freeze_rebinds` 台账记载的
  **地址图批准导致 `upstream_bindings.stage4_address_map` 重绑**（2026-10-27T14:17:57+08:00；契约仍 v1.3.0/r07/FROZEN_OFFLINE_ONLY）；
  相对上一版契约**无字段删除**，仅新增 `post_freeze_rebinds*`。
- **请求（二选一）**：
  1. 把两份冻结记录（s4t27_replay_positive_20261027_r01/freeze_index.json 与 s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json）的 contract_binding.json_sha256 更新为现状 2848ba031a6411e2…（或在新版本中登记重绑），并注明该重绑已在契约 post_freeze_rebinds 内留痕；
  2. 若沿用旧哈希，请提供消费方可核验的重绑凭证（本包已把 post_freeze_rebinds 台账作为该凭证核验）；阶段5 侧在收到正式重绑后**无需改码**即可恢复消费（本包已用模拟重绑证明 exit 0）。
- 阶段5 已用**模拟重绑**证明：正式重绑后**无需改码**即可恢复消费（带框链 exit 0；证据
  `w5/report/evidence/S5-T03/s5t03_contract_rebind_analysis_20261027_r01/`）。
- 另一处待确认：门禁数**口径冲突**（计划文档 4/8 vs 最新提交 "gates 5/8"）⇒ 请阶段4 明确；阶段5 不自行判定。
- 边界：**§4.5/§7.3 未关闭**；板上项与真正消费均 NOT_RUN。
