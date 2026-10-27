# 阶段4 冻结件独立核验（阶段5 只读） RunId `s4_freeze_verification_20261027_r01`

- 被核验：契约 `s4-shared-io` **v1.3.0** /
  **FROZEN_OFFLINE_ONLY**（SHA `7228f51350feb0c6…`，与冻结登记**一致**）；
  回放包冻结记录 `s4t27_replay_package_freeze_20261027_r01`（owner：Workbuddy 阶段4总控），`consumption_mode=replay_only`
- **完整性**：逐文件复算 **10/10 OK**、
  不符 **0**、缺失 **0**（基路径 `D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t26_gate_rerun_20261027_r04`）
- 结论：**CONSUMABLE_OFFLINE_REPLAY_ONLY**（可作阶段5 离线回放消费；本包**未做接入**）
- 允许声明：冻结输入与参考的数值一致性（离线回放口径）；回放链路的工具与判据有效性（含反例）…
- **禁止声明**：板上行为 / PL 真实运行；UART 实收 / S2BU 真帧；真实摄像头采集质量或颜色…（完整清单见 `verification.json`）
- **NOT_RUN**：板上真实回放（阶段4 冻结明示需硬件 OFFER/CLAIM + 八类门禁，当前 0/8）、真实回放消费产物、
  摄像头路径、P/4-D/G3/G4/G5 任一项判定
- 限制：只读核验；未写阶段4 缓冲、未改契约、未改阶段4 证据

## 契约上游绑定漂移检查（authority_rules.drift_detection）
- **17/17 OK**、0 漂移/缺失；跨工作树条目按 `git_blob_content` 在所属工作树取 HEAD blob 复算。
- 首轮曾误报 4 条 DRIFT（在 w4 内取 dbdf/w5 的 blob 得空输入哈希），已定位为**检查器缺陷**而非契约漂移，更正后全绿。
