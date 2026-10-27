# S5-T03 阶段4 契约漂移：**刻画 + 模拟重绑兼容性**（纯离线） RunId `s5t03_contract_rebind_analysis_20261027_r01`

## 1. 漂移结论（可核验）
- 冻结索引登记：`7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145`；契约现状：`2848ba031a6411e2920f7f8edbd58a3199d3404a2558a867d6c0f245c0796a94` ⇒ **不一致**（这就是我此前 fail-closed 拒收的原因）
- 契约仍为 **v1.3.0 / r07 / FROZEN_OFFLINE_ONLY**
- 契约内 `post_freeze_rebinds` 台账**解释了原因**：2026-10-27T14:17:57+08:00 ——
  **Wong 批准 stage4 地址图**（DRAFT_PENDING_REVIEW→APPROVED），其字节 SHA 变化 ⇒ 冻结契约的 `upstream_bindings`
  必须重绑（`stage4_address_map`：`8f554d95817e965b…` → 新值）
- **结构差异**：无字段删除；仅新增 `post_freeze_rebinds*`（重绑台账）⇒ **结果契约语义未变**，属**行政性重绑**

## 2. 关键结论：**一旦正式重绑，阶段5 无需改码即可恢复消费**
- 模拟重绑（把索引的 `contract_binding` 指向现状契约，写入 w5 tmp 副本）后跑带框消费链 ⇒ **exit 0**
  （integrity True、检测 1 框、`boxes_with_px=1`、包内交叉核对 True、五元组 `age_*=null` 如实标注）
- 旧冻结链在**未重绑**下仍按设计拒收（exit 1，`contract_binding FAIL`）

## 3. 对阶段4 的精确请求
1. 把两份冻结记录（s4t27_replay_positive_20261027_r01/freeze_index.json 与 s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json）的 contract_binding.json_sha256 更新为现状 2848ba031a6411e2…（或在新版本中登记重绑），并注明该重绑已在契约 post_freeze_rebinds 内留痕；
2. 若沿用旧哈希，请提供消费方可核验的重绑凭证（本包已把 post_freeze_rebinds 台账作为该凭证核验）；阶段5 侧在收到正式重绑后**无需改码**即可恢复消费（本包已用模拟重绑证明 exit 0）。

## 4. 门禁数口径冲突（阶段5 不自行判定）
- 计划文档写 **4/8**；最新提交信息写 **gates 5/8**（`af3b219` "close g0_approval"）⇒ **待阶段4 确认**；阶段5 不据此宣称任何关口。

## 5. 限制
- 纯离线只读分析；未修改 w4/main；模拟重绑仅写 w5 `tmp/`，**不改上游冻结记录**。
- 板上项、真正消费均 **NOT_RUN**（前者属板上；后者待阶段4 正式重绑）。**§4.5/§7.3 未关闭**。
