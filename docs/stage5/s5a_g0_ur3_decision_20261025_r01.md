# 阶段5 G0 UR-3 决策补遗 r01

- 决策时间：2026-10-25（UTC+8）
- 决策权限：Wong 于 2026-10-25 明确回复「你来决定」，授权 Codex 项目总控确定 UR-3 数值与显示参数。
- 适用范围：只关闭阶段5 UR-3 中的成品延迟上限、颜色表/字号、stale 域口径；不代表阶段5整体 G0/G1/G3/G4/G5 通过。
- 机器可读版本：同目录 `s5a_g0_ur3_decision_20261025_r01.json`。

## 决定

1. **成品延迟上限**：显示语义 B 下，显示中的结果框所对应的 `age_frame` 不得超过 **200 ms**。采样使用采集与显示共用的 PS 单调时基；`age_frame > 200 ms` 时立即清除旧框，等于 200 ms 时仍有效。实测报告记录样本数、P50/P95/P99 与最大值，不能只报通过比例或隐藏超时/丢帧。此值沿用阶段5离线草案，并与已批准的跨阶段 `stale_age_limit_ns=200000000` 同一数值；这是验收门槛，不是测量结果。
2. **stale 判定域**：阶段4 的生产字段 `stale` 只对 `state ∈ {OK, NO_HAND}` 有定义。阶段5 对保留叠框执行 `stale_effective = stale_flag OR (age_frame > 200 ms)`，年龄过期清除**不增加当前输入 state 守卫**，以保证连续超时/错误/丢帧时也能清除旧框。`TIMEOUT/ERROR/DROPPED` 继续分别记录和计数，不得伪装成 `NO_HAND`；这些状态不生成新叠框。阶段4 活动共享契约已将该常量标为 `APPROVED_BY_WONG`；S4-A r06 中的 `DRAFT_PENDING_APPROVAL` 是历史快照标签，不是当前待批准状态。阶段4 实际 stale 判定仍未实测。边界为严格 `>`。
3. **类别颜色（RGB `#RRGGBB`）**：沿用固定类别顺序，映射为 `fist #0072B2`、`palm #E69F00`、`one #009E73`、`two_up #CC79A7`、`three #D55E00`。渲染后端按其通道顺序转换，不改语义色值。
4. **字号**：基准画布 1280×720 使用 16 px；其他画布按 `round_half_up(16 × output_height / 720)` 缩放（1920×1080 为 24 px）。既有 2 px 框线、安全区、标签锚点和几何误差规则不变。

## 关联与边界

- 阶段5 显示侧 `age_frame` 门槛为 `200000000 ns`，与阶段4/5/6 使用的同源常量一致。活动来源为 `docs/stage4/s4b_shared_input_result_contract.json#/result_contract/stale_rule`（`stale_limit_status=APPROVED_BY_WONG`）；批准凭据为 `D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\decisions\stage6_approval_receipt_20261023_r01.md`（SHA-256 `d8edb84849cd1f93fded902dd913e841564bb1abedbfacd7c7ecde3112e874fb`）。Wong 于 2026-10-25 再次明确批准 200 ms。S4-A r06 的旧草案标签已由活动契约标注为历史快照，不得误读为当前待批。实际 stale 判定仍 `NOT_RUN`。阶段6 `T6-A03` 是 `t_effective − window_complete`，不是本补遗的 `age_frame` 指标；其数值当前 `NOT_RUN`，待阶段4实测帧周期 P 后再计算。
- 本补遗取代旧文档中 UR-3 的“待正式 G0”状态快照；旧运行证据与旧规格字节保留，不重写。
- 当前 camera/replay 实现、真实渲染和实物视觉检查仍未执行。此决定不把离线自测升级为板级验收或阶段冻结。
