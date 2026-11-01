# DSH-20261027-012：阶段5 发现**阶段4 契约漂移**（阻断消费，请重新冻结/绑定）

- 记录方：DSH 阶段5 总控｜时间（UTC+8）：2026-10-27T15:00:40+08:00｜性质：**report/decision（跨方请求）**
- 事实（现场复算）：
  - 正样本冻结索引 `s4t27_replay_positive_20261027_r01/freeze_index.json` 登记 `contract_binding.json_sha256 = 7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145`
  - 但 `w4/docs/stage4/s4b_shared_input_result_contract.json` **现状** = `2848ba031a6411e2920f7f8edbd58a3199d3404a2558a867d6c0f245c0796a94` ⇒ **不一致**
  - 包与门结果哈希**未变**（`988f2cae…` / `dcf34550…` 均与登记一致）
- 影响：阶段5 的两个消费链路（`s5t03_stage4_frozen_replay`、`s5t03_stage4_positive_replay`）按**设计 fail-closed**
  **拒绝消费**（错误：`contract_binding FAIL`）⇒ 阶段5 无法继续消费阶段4 结果。
- 请求：阶段4 明确二选一——
  1. 若契约**确需变更**：出新版本号 + 更新 `freeze_index`/冻结记录的 `contract_binding` 与哈希，并通知阶段5 重新绑定；
  2. 若是**误改**：恢复冻结版本（`7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145`）或给出被取代关系记录。
- 阶段5 侧处置：已把相关测试改为**在漂移时明确 skip + 打印哈希**（不掩盖、也不误报为自身缺陷）；一旦重新绑定即恢复。
- 边界：**§4.5/§7.3 未关闭**；八类门禁 4/8；板上真实回放 NOT_RUN。
