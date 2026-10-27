# 阶段4 冻结判定记录（2026-10-27 r01）

- 判定人：Workbuddy 阶段4总控（依 Wong 2026-10-27 授权自主裁决）
- 工作树/分支：`D:\codex-worktrees\w4` / `stage4-infer-prep`
- 本记录只做**判定与索引**，不改任何冻结数值、不声称板级通过。

## 1. 结论（先给结果）

阶段4 **可以冻结的部分**：离线推理链（task-26 双样本门 + task-27 回放结果包）。
阶段4 **不能整体冻结**：RAW 系统 G0 仍有 10 项设计/复审缺口 + 4 项硬件依赖，板级 P、4-D、G3 均 `NOT_RUN`。
评测项 F-1（共享 IO 契约复审）已于本轮关闭，F-2/F-3 仍开放。

因此本轮判为 **`OFFLINE_SCOPE_FROZEN`（离线范围冻结）**，不宣称 G3/G4/G5 整体通过。

## 2. 逐项判定

| 关口/项 | 判定 | 依据 |
|---|---|---|
| 离线推理门（task-26） | **PASS（离线）** | `s4t26_gate_rerun_20261027_r04`：status PASS / exit 0，6/6 检查 PASS，两样本四个 head 与材料化黄金逐字节一致，单字节负控与 PNG 检查 PASS，task-25 回放帧 PASS。r02 为上一版桥接器字节的同类通过，保留；r01 为失败留档 |
| task-27 回放结果包 | **已生成（replay_only）** | 同 RunId `task27_replay_result_package.json`；只能按回放口径消费，不得当实时结果 |
| task-26 G0 输入 | **CLOSED_WITH_ACCEPTED_BREAK** | `s4t26_g0_inputs_20261026_r34`（exit 0，`accept_producer_break=true` 已写入 command/字段）；同一字节无开关的 `r33` 仍 `BLOCKED/2`，证明默认 fail-closed |
| 门禁证据对齐 | **PASS** | `s4t26_gate_reconcile_20261027_r17`（exit 0，0 项未闭合；记录 `g0.run_id=r34` / `selection_mode=explicit_run_id`） |
| 绑定字节口径 | **已登记** | `docs/stage4/S4B_binding_byte_basis_registry_20261027_r01.json`（4/4 声明值复算一致）；契约内已有 `binding_byte_basis` 声明 |
| 共享 IO 契约 | **r07 已按规则重绑两处过期绑定，仍 `DRAFT_PENDING_REVIEW`** | 重绑：桥接器 `ad71cae0…`(06c9ab8) → `c6117bb4…`(r12 现行 raw)；w5 显示字段 `10d24a39…`(b6d11d4) → `af51a4bf…`(a54f09f)。冻结前仍需独立复审并引用被审 SHA |
| RAW 系统 G0 | **未闭合** | `docs/stage4/S4B_raw_system_g0_gap_registry.json`：OPEN_REQUIRES_DESIGN_OR_REVIEW 10、PARTIALLY_CLOSED_OFFLINE 4、NOT_RUN_HARDWARE_REQUIRED 4、BLOCKED_PENDING_HARDWARE 1、CLOSED_OFFLINE 1 |
| 帧周期 P | `NOT_RUN` | 需板上真实采集；方案与校验器已在 `docs/stage4/S4B_frame_period_P_measurement_plan.md` |
| 4-D 端到端延迟 | `NOT_RUN` | 需板上注入帧 + 真实链路 |
| G3 实物验证 | `NOT_RUN` | 本轮全程未操作板卡/JTAG/COM4/Vivado |
| `ENABLE` | `0` | 未解除；候选 RAW region 未冻结 |
| 真实 C/PL BGR→RGB | `NOT_IMPLEMENTED` | 仅离线 Python 参考实现；运行时路径未接 |

## 3. 冻结范围（可下游消费）

冻结后阶段5 只可按下列口径消费：

1. `s4t26_gate_rerun_20261027_r04/task27_replay_result_package.json` —— **`replay_only`**，不得标实时；
2. `docs/stage4/s4b_shared_input_result_contract.json` r07（1.3.0）—— 仅在其独立复审通过并改状态后生效，此前按草案处理；
3. 冻结参考：T25/T29 张量、材料化黄金四个 `.bin`、`s4t26_golden_rebind_20261026_r02/golden_materialization_manifest.json`（SHA `47e4cc36…`）。

## 4. 不得声称的事

- 不得声称 activation producer 可复现（provenance 断点已登记）；
- 不得声称 P / 4-D / 延迟 / 帧率 已验证；
- 不得声称 RAW 系统 G0 已闭合、`ENABLE` 可置 1；
- 不得用离线回放结果替代真摄像头/真链路结果。

## 5. 解除条件（转入整体冻结状态前必须满足）

| 编号 | 需完成 | 归属 |
|---|---|---|
| F-1 | ~~共享 IO 契约 r07 独立复审 PASS 并改状态~~ **已完成（2026-10-27）** | 阶段4 总控 + 独立 Reviewer |
| F-2 | RAW G0 10 项设计/复审缺口逐项关闭 | 阶段4 总控 |
| F-3 | 板级 P 实测、4-D 端到端、G3 实物验证 | 板卡已上电（2026-10-27），但 main OFFER / w4 CLAIM / 八类门禁 0/8，仍需正式交接 |
| F-4 | `ENABLE=0` 解除与候选 region 冻结 | 依赖 F-2/F-3 |

## 6. 证据索引

- 门：`report/evidence/S4-CTRL/s4t26_gate_rerun_20261027_r04/`（含 `task27_replay_result_package.json`）
- G0：`report/evidence/S4-CTRL/s4t26_g0_inputs_20261026_r34/`（含 r29 无开关对照）
- 对齐：`report/evidence/S4-CTRL/s4t26_gate_reconcile_20261027_r17/`
- 断点决策：`docs/stage4/s4t26_producer_break_decision_20261027_r01.json`
- 口径登记：`docs/stage4/S4B_binding_byte_basis_registry_20261027_r01.json`
- 身份审计（保留断点事实）：`report/evidence/S4-CTRL/s4t26_producer_audit_20261027_r04/`（仍 `BLOCKED/1`，属设计如此：它记录“不可复现”这一事实）

## 7.5 硬件会话状态（2026-10-27 12:05）

Wong 告知板卡已上电。只读观测确认线缆与串口存在（FTDI `VID_0403&PID_6014`、`COM4`、`hw_server` 未运行），
但按 runbook「工作树写权交接与板卡上电报告不能替代 OFFER/CLAIM」，**未开跑**。

- 机检：`report/evidence/S4-B/s4b_hw_gate_readiness_20261027_r04/` → `BLOCKED / exit 1`，13 项阻断。
- 注入单元离线就绪：`OFFLINE_PREPARATION_VALID`（prepare 与 validate 均 exit 0）。
- 解除清单：`docs/stage4/s4_hardware_handoff_unblock_plan_20261027_r01.md`（含 main OFFER 模板与 w4 CLAIM 六键）。
- 仍未做：加载位流、开串口、启动 hw_server/xsdb、复位、读日志；`ENABLE=0` 未变。

## 7. 本轮复审后的修补（2026-10-27 07:50）

独立 Reviewer 首轮判 `CHANGES_REQUIRED`，已修：

| 编号 | 问题 | 修法 |
|---|---|---|
| P1 | G0 的 `command` 字段丢开关，证据无法自证“用了开关” | 记录 `sys.argv[1:]` 并新增 `accept_producer_break` 字段；r23/r24 同字节双留证 |
| P2 | 对齐器 `--g0-run` 接受任意路径，可把已登记断点洗成 PASS | 限定为证据根下的 RunId 名、校验 `run_id/checker_version/checks` 自洽；产物记录 `g0.run_id`、`selection_mode`、`preflight_sha256` |
| P3 | 产物键名 `g0_r13` 与实际选用的 G0 不符 | 重命名为 `g0` 并记录真实 RunId；历史运行改标 `historical_run_cited` |
| P4 | 桥接器未禁止写入黄金目录内部；目录异常退 1 | 增加“不得位于黄金目录之内”判定；目录读取异常统一 `exit 2` |
| P5 | 契约两处绑定过期 | r07 重绑并登记 `replaces`（见上表） |
