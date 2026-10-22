# S4CTRL-20261022-003 阶段4 G0 更新、共享契约与对阶段5 的绑定变更

- 编号：`S4CTRL-20261022-003`；日期：2026-10-22（UTC+8）
- 提出方：DSH 阶段4 总控（工作树 `D:\codex-worktrees\w4`，分支 `stage4-infer-prep`）
- 依据：CDX-20261022-010（阶段4 运行书）、CDX-20261022-014 r02（阶段5 运行书）、CDX-20261022-015 r02（执行总入口）、CDX-20261022-007（2B 冻结）
- 传递：本文件写在本树内，不直写两个 mailbox；要点由项目总控转达。不是接口冻结、不是验收结论。

## 1. 2B 冻结事实已对齐（告知，无需回复）

- 2B 于 2026-10-22 正式冻结并释放硬件：代码基线 `16ce2cdf8c00c6214435629d75a5e4b63acb66a9`，最终提交 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`，冻结回执 SHA-256 `2687e87a9664d6415d17738a6f6ff10b8fe3e372696399eb710fa2d06d2778e1`，G4/G5 经独审 PASS，1000 连续任务 + 108 个 ACK 闭环黄金样本。
- 阶段4 已删除“2B 尚未验收/仍持硬件”的旧快照表述，改为“2B 已冻结并释放；当前硬件归属以现场会话核验为准（阶段5 正在板测）”。
- 本阶段**未执行任何硬件操作**：未访问 `hw_server`/JTAG/COM4/串口，未启动 Vivado/xsim。

## 2. 阶段4 G0 基线更新：S4-A r05 → r06（需阶段5 重新绑定）

- S4-A 契约已升 **r06**：`docs/stage4/s4a_stage4_g0_fields.json` = `657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5`，`status=G0_ROUND_FROZEN_R06`。被取代的 r05 = `3524d02ae410ae365a9dbfc5f04dcd9f300f8013086a076259a641f7eb8afb87`。
- r06 新增/明确：完整上游钉扎（24 条，含 `D:\FPGA_Data` 的 2A 模型/量化资产与 2B C 参考、冻结回执）、`g0_round_freeze`（6 冻结项 + 2 未冻结项）、UART 方案 B、三范围冻结、候选上限边界口径、测量范围词表（`source_kind`/`capture_time_available`/`injection_start_ns`/`clock_domain`）。
- **请阶段5 把其 G0 中记录的 S4-A 引用从 r05 改为 r06 并记录替换关系**（w5 `docs/stage5/s5a_stage5_display_g0_fields.json` 目前仍绑定 r05 `3524d02a…`）。阶段4 不会单方改 w5。

## 3. 共享输入/结果契约可用（草案 r02，阶段5 只读消费）

- 路径：`docs/stage4/s4b_shared_input_result_contract.md` + `.json`（`s4-shared-io/1.1.0`，`DRAFT_PENDING_REVIEW`，待独立审查后冻结）。
- 与阶段5 的直接相关点：
  1. **显示语义取值采用阶段5 G0 已决值 `B_latest_result_overlay`**（不是我方另立的 `latest_overlay`）；A/C 在阶段5 G0 登记但未启用，本契约不授权未批准语义。
  2. 五元组 `(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)` 与 CDX-014 §4 逐名一致；`age_result_ns = t_overlay_commit − t_result_publish`，`age_frame_ns = t_overlay_commit − t_capture(frame_id)`。
  3. HUD 13 字段来源表齐全；不可用量必须标不可用、不得用 0 伪装实测。
  4. 过期：`stale_effective = stale_flag OR age_frame_ns > stale_limit_ns`；**唯一常量来源 = 阶段5 G0 的 `STALE_AGE_LIMIT_NS`**（当前 w5 记为 `G0_FIXED_OFFLINE`，200000000 ns）；阶段4 侧仍 `DRAFT_PENDING_APPROVAL`，正式批准前不作为验收门槛，两端不得各造常量。
  5. UART 方案 B：时间/过期/丢帧/状态只在 PS 侧日志；唯一映射键 `(session_id, frame_id, result_seq)`；阶段5 必须从 PS 日志读取这些量，**不得声称来自 UART**。
  6. 注入模式：`capture_time_available=false`，`capture_time_ns` 结果侧为 0 哨兵 + 注解；注入起点只写 `injection_start_ns`，**不得冒充采集时间**；`capture_fps` 在注入/合成下为不可用。
- **请求阶段5 确认**：以上 6 点是否与其 G0/实现一致；若有冲突请以跨方请求回复，阶段4 决定是否出契约新版本（阶段5 不得自行改本契约）。

## 4. 需 Wong 决策/知悉（不阻断本轮离线开发）

1. `stale_age_limit` 与阶段5 `STALE_AGE_LIMIT_NS` 的最终唯一批准：请明确由哪一份 G0 作为批准载体（建议阶段5 G0 的 `STALE_AGE_LIMIT_NS` 为唯一载体，阶段4 引用）。
2. 阶段4 完整 G5 仍受摄像头验收约束（CDX-010 §6）；本轮只做离线，注入子项通过不等于摄像头 G5 通过。

## 5. 边界与限制

- 本文件不授予任何方修改对方信箱、主/阶段 STATE、业务代码或操作硬件的权限；不覆盖旧记录；后续同类事项使用新编号。
- 阶段4 本轮**全部证据只来自离线执行**；板上注入、真实串口、摄像头均为 `NOT_RUN`。