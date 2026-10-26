# 阶段4 冻结判定记录（2026-10-27 r01）

- 判定人：Workbuddy 阶段4总控（依 Wong 2026-10-27 授权自主裁决）
- 工作树/分支：`D:\codex-worktrees\w4` / `stage4-infer-prep`
- 本记录只做**判定与索引**，不改任何冻结数值、不声称板级通过。

## 1. 结论（先给结果）

阶段4 **可以冻结的部分**：离线推理链（task-26 双样本门 + task-27 回放结果包）。
阶段4 **不能整体冻结**：RAW 系统 G0 仍有 10 项设计/复审缺口 + 4 项硬件依赖，板级 P、4-D、G3 均 `NOT_RUN`。

因此本轮判为 **`OFFLINE_SCOPE_FROZEN`（离线范围冻结）**，不宣称 G3/G4/G5 整体通过。

## 2. 逐项判定

| 关口/项 | 判定 | 依据 |
|---|---|---|
| 离线推理门（task-26） | **PASS（离线）** | `s4t26_gate_rerun_20261027_r02`：status PASS / exit 0，6/6 检查 PASS，两样本四个 head 与材料化黄金逐字节一致，单字节负控与 PNG 检查 PASS，task-25 回放帧 PASS |
| task-27 回放结果包 | **已生成（replay_only）** | 同 RunId `task27_replay_result_package.json`；只能按回放口径消费，不得当实时结果 |
| task-26 G0 输入 | **CLOSED_WITH_ACCEPTED_BREAK** | `s4t26_g0_inputs_20261026_r22`（exit 0）；activation producer provenance 为已登记断点，不表示可复现 |
| 门禁证据对齐 | **PASS** | `s4t26_gate_reconcile_20261027_r10`（exit 0，0 项未闭合） |
| 绑定字节口径 | **已登记** | `docs/stage4/S4B_binding_byte_basis_registry_20261027_r01.json`（4/4 声明值复算一致）；契约内已有 `binding_byte_basis` 声明 |
| 共享 IO 契约 r06 | **待独立复审**（仍 `DRAFT_PENDING_REVIEW`） | 契约自述“r05/r06 均未复审，冻结前必须另行独立复审并引用固定提交 + 被审 SHA” |
| RAW 系统 G0 | **未闭合** | `docs/stage4/S4B_raw_system_g0_gap_registry.json`：OPEN_REQUIRES_DESIGN_OR_REVIEW 10、PARTIALLY_CLOSED_OFFLINE 4、NOT_RUN_HARDWARE_REQUIRED 4、BLOCKED_PENDING_HARDWARE 1、CLOSED_OFFLINE 1 |
| 帧周期 P | `NOT_RUN` | 需板上真实采集；方案与校验器已在 `docs/stage4/S4B_frame_period_P_measurement_plan.md` |
| 4-D 端到端延迟 | `NOT_RUN` | 需板上注入帧 + 真实链路 |
| G3 实物验证 | `NOT_RUN` | 本轮全程未操作板卡/JTAG/COM4/Vivado |
| `ENABLE` | `0` | 未解除；候选 RAW region 未冻结 |
| 真实 C/PL BGR→RGB | `NOT_IMPLEMENTED` | 仅离线 Python 参考实现；运行时路径未接 |

## 3. 冻结范围（可下游消费）

冻结后阶段5 只可按下列口径消费：

1. `s4t26_gate_rerun_20261027_r02/task27_replay_result_package.json` —— **`replay_only`**，不得标实时；
2. `docs/stage4/s4b_shared_input_result_contract.json` r06 —— 仅在其独立复审通过并改状态后生效，此前按草案处理；
3. 冻结参考：T25/T29 张量、材料化黄金四个 `.bin`、`s4t26_golden_rebind_20261026_r02/golden_materialization_manifest.json`（SHA `47e4cc36…`）。

## 4. 不得声称的事

- 不得声称 activation producer 可复现（provenance 断点已登记）；
- 不得声称 P / 4-D / 延迟 / 帧率 已验证；
- 不得声称 RAW 系统 G0 已闭合、`ENABLE` 可置 1；
- 不得用离线回放结果替代真摄像头/真链路结果。

## 5. 解除条件（转 FULL_FROZEN 所需）

| 编号 | 需完成 | 归属 |
|---|---|---|
| F-1 | 共享 IO 契约 r06 独立复审 PASS 并改状态 | 阶段4 总控 + 独立 Reviewer |
| F-2 | RAW G0 10 项设计/复审缺口逐项关闭 | 阶段4 总控 |
| F-3 | 板级 P 实测、4-D 端到端、G3 实物验证 | 需硬件窗口与正式 OFFER |
| F-4 | `ENABLE=0` 解除与候选 region 冻结 | 依赖 F-2/F-3 |

## 6. 证据索引

- 门：`report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r02/`
- G0：`report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r22/`
- 对齐：`report/evidence/S4-CTRL/s4t26_gate_reconcile_20261027_r10/`
- 断点决策：`docs/stage4/s4t26_producer_break_decision_20261027_r01.json`
- 口径登记：`docs/stage4/S4B_binding_byte_basis_registry_20261027_r01.json`
- 身份审计（保留断点事实）：`report/evidence/S4-CTRL/s4t26_producer_audit_20261027_r04/`（仍 `BLOCKED/1`，属设计如此：它记录“不可复现”这一事实）
