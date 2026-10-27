# 阶段4 冻结补充记录：真实板级 PS 张量诊断完成（2026-10-27 r01）

- 时间：2026-10-27 17:46（UTC+8）
- 性质：对 `s4_stage4_freeze_signed_20261027_r01.md`（OFFLINE_SCOPE_FROZEN）的**硬件范围补充**。
  本记录把「真实板级执行」从 NOT_RUN 升级为 EXECUTED_WITH_EXPLICIT_GATES，其余口径不变。

## 1. 判定依据（全部为本轮真实产物）

| 项 | 结果 |
|---|---|
| 运行状态 | `ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED`，`hardware_execution = EXECUTED_WITH_EXPLICIT_GATES` |
| 证据目录 | `report/evidence/S4-B/s4b_ps_tensor_hw_20261027_r01/`（result/events/jtag_calls/jtag_result/trace/weights/uart 原始字节） |
| 八道门禁 | `report/evidence/S4-B/s4b_hw_gates_20261027_r13` — adapter `validate_hardware_gates` = allowed:true, missing:[] |
| 授权链 | main OFFER `84c840f`（心跳 16:48:52）→ w4 CLAIM `3b496fb` → handoff `s4b_hw_handoff_20261027_r06` |
| 部署身份（逐字符一致） | bit `555a70c2…` / ELF `bfe88660…` / MAP `4a0f9cf8…` / XSA `ea52da1b…`（与 Wong 确认的阶段4集合一致） |
| 权重 | `f6feb6d4…`（5,903,100 B，GFINT8W1，OP_WEIGHTS PASS @17:43:08） |
| 输入张量 | `da26d385…`（519,168 B INT8_CHW_416，raw_reference test_fist_000，绑定 `s4b_hw_tensor_binding_20261027_r01`） |
| **推理结果** | UART 回执 frame 0 / sequence 2 / epoch 1 / response_code 0：**raw_candidate 2 → 检出 1 框**；head13=5,070 B（`07b59ca3…`）、head26=20,280 B（`7524ce5c…`） |
| trace 对账 | 双读快照 PASS_DECODED_DOUBLE_READ_SNAPSHOT + **PASS_EXACT_TRACE_UART_JOIN**（session_id 1396845568 = 预留区间首值） |
| 冷依据 | 物理 `physical_power_cycle`（Wong 17:15 JTAG 冷启动断电重启）+ 会话预停 `apu.rst --stop system`（prehalt_1722.log） |
| 会话 | hw_server 3121（winnat 释放后），xsdb peer 逐字匹配冻结工具要求；force-mem-accesses=1（ps7_init.tcl 先例，仅客户端映射放行） |
| 收尾 | run_active_zero、cpu0 停在安全点（Hardware Breakpoint 0x1d08）、cpu1 Stopped——板卡处于安全状态 |

## 2. 本记录不宣称的事（诚实边界）

- `complete_stage4_or_RGB_preprocess = NOT_CLAIMED`：PS INT8 CHW 张量诊断**不证明** RGB 预处理、raw/PL 新架构或阶段4 G5。
- 真摄子项仍为 `DEFERRED_PENDING_MODULE`；P1–P6 板级注入端到端不在本轮 scope。
- 上板真拍含框回放需要 Wong 在场（真机画面步骤），留待阶段5 前置完成。

## 3. 冻结判定

- 离线范围：维持 `OFFLINE_SCOPE_FROZEN`（r01 已签名，冻结集 8/8 PASS）。
- 硬件范围：**真实执行已完成且证据齐全** → 阶段4 按下列口径**冻结**：
  1. 交付物 = 阶段4 离线冻结集 + 本轮真实板级诊断证据包；
  2. 主张 = 「PS 张量诊断链在真实板上按冻结工具链执行成功，含权重上传、单帧推理、检测框输出、trace 双读对账」；
  3. 未闭合项 = 真摄子项（DEFERRED）、G5 板级（NOT_CLAIMED，按上限诚实登记）、真拍回放（阶段5 前置）。
- 签发：Workbuddy 阶段4总控（本窗口，Wong 授权硬件窗口 + main OFFER `84c840f` + w4 CLAIM `3b496fb` 全链真实）。

## 4. 环境备注

- Wong 需执行 `net start winnat` 恢复 Hyper-V 端口保留（跑完恢复；本轮 3121 会话窗口的记录已固化，不依赖 winnat 状态）。
- 失败尝试全部归档于 `tmp/4/S4-B-REAL-02B/s4b_ps_tensor_hw_20261027_r01_aborted_*`（4 次，均未污染正式证据）。
