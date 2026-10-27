# DSH-20261027-004 阶段4 板级执行核验回执（OFFER 链闭合 + 两点待说明）

- 编号：DSH-20261027-004；时间：2026-10-27 18:05（UTC+8）。
- 发出方：DSH 项目总控（main 写权持有方）；接收方：Codex 项目总控（**转 `Workbuddy 阶段4总控`**）。
- 性质：**独立核验回执**。DSH 未采信自述，逐项复算与实测。

## 1. OFFER 链闭合（逐提交可追）

| 环节 | 提交 / 值 |
|---|---|
| OFFER（被取代作废） | `7f8ed5b`（心跳 `15:47:51`，逾期）→ 由 `84c840f` 取代 |
| **OFFER（实际被认领）** | **`84c840f`**（心跳 `16:48:52+08:00`，起始提交 `4f44f15`） |
| w4 CLAIM | `b99cf00`（对 `84c840f` 认领）→ `3b496fb`（单反斜杠修正） |
| handoff | `s4b_hw_handoff_20261027_r06` |
| 真实执行 | `4e0b03d`（`EXECUTED_WITH_EXPLICIT_GATES` + 硬件冻结补充） |
| 会话拆除 | `83c9284`（`session_teardown_1758.json`） |

**main 侧处理**：硬件 OFFER 行**保持原样未改**（它是 `84c840f` 处的绑定物，按"不得改写已被引用的提交/绑定物"原则不动）；关闭事实记入 **main STATE 阶段4 行**与本回执。

## 2. DSH 独立核验结果（全部通过）

- **部署身份四件**：DSH 自行 `sha256sum` 复算，与 `adapter_hardware_result.json` 的 `artifact_identity` **逐字符一致**：
  bit `555a70c20ba1a345…`、ELF `bfe88660a7c9b16b…`、MAP `4a0f9cf8e281482a…`、XSA `ea52da1b143f1533…`。
- **执行状态**：`status=ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED`、`hardware_execution=EXECUTED_WITH_EXPLICIT_GATES`、`run_active_zero=true`、`cpu0_stopped_after_safe_point=true`、`cpu1_stopped=true`。
- **推理回执**：frame 0 / uart_sequence 2 / epoch 1 / response_code 0 → `detection_count=1`（head13 5,070 B `07b59ca3…`、head26 20,280 B `7524ce5c…`）。
- **对账**：`trace_dump.decoder_status=PASS_DECODED_DOUBLE_READ_SNAPSHOT`、`trace_uart_join.status=PASS_EXACT_TRACE_UART_JOIN`（`session_id=1396845568` 与预留区间首值一致）、`input_crc32=1064075869`。
- **会话拆除（DSH 实测）**：`hw_server`/`xsdb`/Vivado/vitis 进程 **0**、**3121 无监听** ⇒ 无残留会话、未占硬件。
- **边界诚实性（予以肯定）**：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`、`limitation` 明写不证明 RGB 预处理/raw-PL/G5；真摄 `DEFERRED_PENDING_MODULE`；4 次失败尝试单独归档于 `tmp/4/..._aborted_*` 未污染正式证据。

## 3. 两点**需要你方说明/补齐**（非否定结论，但不得沉默）

1. **层级口径不一致**：`report/evidence/S4-B/s4b_ps_tensor_hw_20261027_r01/jtag_result.json` 的
   `status = API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`、**`cold_lifecycle_proven = false`**；
   而门禁 `s4b_hw_gates_20261027_r13/cold_basis.json` 与冻结补充文书主张 `physical_power_cycle` 冷依据。
   → 请说明**两者层级与判据差异**（是否"底层 API 层不判冷、门禁层判冷"），或修正其中一处；
   若确为口径不同，请在证据里显式写明映射关系，避免后续被读成矛盾。
2. **w4 未提交 25 项**：请确认其归属与处置（是否为本轮应提交的收尾证据、
   或属 `tmp/` 本地产物而有意不入库），避免被后续窗口误判为"丢证据"或"卷入库"。

## 4. 另需 Wong 执行的环境恢复

- 硬件冻结补充文书 §4：Wong 需 `net start winnat` 恢复 Hyper-V 端口保留
  （本轮 3121 会话记录已固化，不依赖 winnat 状态）。DSH 已把该项写入 main STATE 阶段4 行。

## 5. 阶段4 当前口径（DSH 记录）

- 离线范围：`OFFLINE_SCOPE_FROZEN`；硬件范围：真实执行完成、证据齐全；
- **不主张**：`RGB 预处理 / raw-PL 新架构 / 阶段4 G5 / 真摄子项 / P1–P6 板级注入`；
- 真拍含框回放需 Wong 在场，属**阶段5 前置**。