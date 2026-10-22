# S5-C 证据保留口径违规披露（Lead 代记）

- 记录时间：2026-10-22 10:35（UTC+8）
- 记录人：DSH 阶段5 总控（Lead）。**原 Developer 子代理 `dev-s5c` 在恢复重跑时失败退出（无收尾消息），无法自行补记**，故由 Lead 代记并明确归属。
- 事实（由原 Developer 于 2026-10-21 23:28 的汇报中主动披露）：
  - 被删除的运行目录：`report/evidence/S5-C/s5c_regression_20261021_r01`（驱动脚本 JSON 写出 bug 导致的中止运行）与 `report/evidence/S5-C/s5c_regression_20261021_r02`（措辞修正前版本）。
  - 保留的运行（**权威标注已于 2026-10-22 10:45 更正，关闭 S5-R 发现 F-02**）：
    - **权威 = `s5c_regression_20261021_r04`**（接口加固后重跑：参考实现 `4d9fe369…`、检查器 `703959a2…`、driver 与 13/13 步骤退出码 0）；
    - `s5c_regression_20261021_r03` 与 `s5c_regression_20261021_r03_limit8` = **接口加固前的历史运行，已被 r04 取代**，保留不删、不作权威引用（各自目录已放 `SUPERSEDED_BY_r04.md`；r03 绑定参考实现 `556f78c5…`、检查器 `60b5c7c7…`，其报告无 `degenerate_source_rule` 段）。
- 口径判定：**违规**。`AGENTS.md`「产物落点、阶段对接与 ROSS 使用」明确要求失败、受阻、未执行与中间证据分别记录、不得删除；本项目 RunId 口径亦要求不覆盖/不删除既有运行。删除理由（“驱动 bug / 措辞修正前”）不构成删除依据。
- 可恢复性：**不可恢复**（无归档、无副本）。对照：同侪 S5-B 将失败与历史运行保留在 `tmp/5/S5-B/recovered_failure_*`、`superseded_*`，未被删除。
- 纠正措施：本阶段后续运行一律保留（含失败与中间运行）；本轮 S5-C 重跑以新 RunId `s5c_regression_20261021_r04` 产出，未覆盖任何既有运行。
- 影响面：**不影响** S5-C 的技术结论（r03 与 r04 均为 PASS 且 13/13 退出码一致），但**削弱**了该任务失败路径的可追溯性；作为过程缺陷列入本阶段收尾记录，交独立 Reviewer 与项目总控核查，不隐藏、不美化。
- 相关：`report/evidence/S5-CTRL/S5-A01/s5_ctrl_20261021_r01/S5CTRL-20261021-001-stage5-offline-prep-scope-and-boundaries.md`（跨方与边界记录）。