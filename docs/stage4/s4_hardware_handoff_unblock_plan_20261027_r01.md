# 阶段4 硬件会话解除清单（2026-10-27 r01）

- 场景：Wong 告知**板卡已上电连接**。本文件回答"现在能不能跑、还差什么、谁给"。
- 判定人：Workbuddy 阶段4总控。本文件只做**索引与模板**，不构成任何授权，不含板级结果。
- 判定权归属：八类门禁由 `scripts/stage4_s4b/s4b_ps_tensor_adapter.py::validate_hardware_gates` 裁决；
  本文件的机检结论只是把它的 `missing` 转述成人能读的清单。

## 1. 一句话结论

**板卡可见 ≠ 可以开跑。** 现在开跑会产出无法被任何下游消费的证据，且违反 runbook 明文规则。

runbook `docs/stage4/S4B_ps_tensor_injection_runbook.md`「正式硬件交接与门禁」原文：

> 硬件交接来自 main 与 w4 的真实已提交 STATE 记录。**工作树写权交接与板卡上电报告不能替代它**。

## 2. 当前实测状态

| 项 | 观测 | 证据 |
|---|---|---|
| JTAG 线缆 | FTDI `VID_0403&PID_6014` 在设备枚举中（FT2232H，A 通道 JTAG / B 通道 UART） | 只读 PnP 枚举 |
| 串口 | `COM4` 存在 | 注册表 `HARDWARE\DEVICEMAP\SERIALCOMM` |
| `hw_server` | 未运行 | 进程表 |
| 注入单元离线就绪 | `OFFLINE_PREPARATION_VALID`，ELF `bfe88660…`、派生源 `7c3b57a9…` | `tmp/4/S4-B-REAL-02B/s4b_ps_adapter_g3_20261027_r01/adapter_preparation.json`；prepare 与 validate 均 exit 0 |
| 八类门禁 | **0/8**（全部 `record_missing`） | `report/evidence/S4-B/s4b_hw_gate_readiness_20261027_r04/gate_readiness.json` |
| main OFFER | **不存在**（main STATE 无 `S4-B-REAL-02B::s4b_hardware_session_handoff`） | 机检读 `D:\FPGA_Competition` HEAD |
| w4 CLAIM | **不存在** | 机检读 w4 HEAD |
| 地址图 | `DRAFT_PENDING_REVIEW` | `docs/stage4/S4B_stage4_address_map.json` |
| RAW owner 方案 | `DECISION_REQUESTED` | `docs/stage4/s4b_raw_address_ownership_proposal_20261024_r01.json` |

机检结论：`BLOCKED / exit 1`，13 项阻断（8 项记录缺 + 5 项依赖未满足）。

## 3. 解除顺序（严格串行，缺一环则后环无效）

```
D1 地址图 APPROVED  ─┐
D2 owner 方案裁决   ─┼─→ g0_approval 才可能成立
                     │
D3 main OFFER  ──→ D4 w4 CLAIM ──→ hardware_session_handoff 才可能成立
                     │
D5 其余五类记录（operator_authorization / exclusive_session /
   command_delivery_review / timing_freeze / range_reservation / cold_basis）
                     │
D6 执行（validate → 装载 → RUN → one-shot 停泊 → 双读导出 → 解码）
```

**D1 / D2 是当前最深的两处卡点**：地址图未批准时，`g0_approval` 无论怎么写都只能是
`DRAFT`，硬写成 `APPROVED` 就是伪造；owner 方案停在 `DECISION_REQUESTED` 需要 Wong 拍板。

**D3 必须由 main 侧签发**，阶段4 不写 main STATE（runbook 明令）。这是唯一一个
不属于阶段4 动作范围的依赖。

## 4. main OFFER 需要写成的形状

main STATE 中需存在**唯一**一行，任务标记精确为 `S4-B-REAL-02B::s4b_hardware_session_handoff`，
并满足 adapter `_verified_hardware_handoff` 的绑定要求：

| 字段 | 要求 |
|---|---|
| 任务标记 | 精确 `S4-B-REAL-02B::s4b_hardware_session_handoff`，全 STATE 唯一 |
| 发送者 | DSH（项目总控） |
| scope | 精确 `S4B_PS_TENSOR_DIAGNOSTIC` |
| 接收者 | 当前 w4 写权负责人（`Workbuddy 阶段4总控`） |
| 状态 | `OFFERED` |
| 证据入口 | 只能为 `hardware_run_id=<完整RunId>`（不得是目录路径或摘要） |
| 心跳 / 恢复命令 | 近期时间戳 + 可执行恢复命令 |
| 一致性 | 当前 HEAD 与工作树仍保有同一未撤销行 |

## 5. w4 CLAIM 需要写成的形状

w4 STATE 中需存在唯一一行 `S4-B-REAL-02B::s4b_hardware_session_claim`，`CLAIMED`，
接收者 / 工作树 / scope / RunId 与 OFFER 完全一致，证据入口**精确包含下列六键**：

```text
offer_commit=<main OFFER 提交>;offer_blob_oid=<main STATE blob OID>;offer_sha256=<该 blob SHA-256>;offer_source_commit=<OFFER 起始提交>;hardware_run_id=<同一完整RunId>;scope=S4B_PS_TENSOR_DIAGNOSTIC
```

前缀相似值、后缀、重复键、多余键均被拒。

## 6. 八类记录清单

| 门禁 | 关键判据 | 现在缺什么 |
|---|---|---|
| `operator_authorization` | `status=AUTHORIZED`、`task_id=S4-B-REAL-02B`、RunId 一致、`authorized_by` ∈ {Wong, 阶段4 负责人}、scope、精确 diagnostic 操作集、有效期窗口、`artifact_identity_sha256` 匹配 | 全部（无记录） |
| `hardware_session_handoff` | 见 §4/§5 的绑定与六键 | 全部（无 OFFER/CLAIM） |
| `exclusive_session` | `status=PASS`、`exclusive=true`、`hw_server_pid` 正整数、`xsdb_peer` 为 `localhost:3121`、`uart_port` 非空、`verified_at` 在 30 分钟内 | 执行时现场取证，预检不得代替 |
| `g0_approval` | `status=APPROVED`、`address_map_status=APPROVED`、`shared_address_status=APPROVED`、`timebase_status=APPROVED`、map/ranges/identity 三个 SHA 匹配 | 地址图与共享地址均未批准 |
| `command_delivery_review` | `status=PASS`、`reviewed_adapter_sha256 == 当前 adapter 字节`、`review_sha256` 64 hex | 当前 adapter `9c74f520…` 无绑定复审 |
| `timing_freeze` | `status=APPROVED`、timebase 与 threshold 均 APPROVED、`approval_id` | 全部 |
| `range_reservation` | 非零 seed + session 闭区间，与旧预留不重叠 | 全部 |
| `cold_basis` | `status=PASS`、`old_axi_lifecycle_cleared=true`、`basis_kind` ∈ {physical_power_cycle, independently_proven_cold_lifecycle} | 全部（需物理断电重建或等价独立证明） |

## 7. 执行时的顺序与停止点（照 runbook，不得简化）

1. `validate` 准备清单 + 八类门禁；权重 / 519,168 B 张量 / tensor binding 必须核验；
2. 从固定 blob 取四工具导入闭包并核验，才导入隔离副本；`JtagController` 执行目标/CPU 门禁、
   system-stop、OCM init→ready/fail、INIT_RESULT/DDR 检查→完整 bit→postconfig→DDR app；
3. 严格匹配 READY 身份的 SOURCE/XSA/MODEL/DIAG/TRACE_ABI；日志必须为空；
4. 成功 RUN 必须进入 r13 one-shot 停泊；stop 前紧邻重读安全 CSR，变化则不 stop；
5. 停后全区双读（header 36 words + records 46000 words），两份一致才生成 dump 并解码；
6. 失败 `automatic_recovery=NONE`：保留 CPU/CSR/owner/pending 与原始日志，不自动 ACK / reset / 释放 / 重试。

## 8. 不得声称

- 不得因"板卡已上电"称硬件会话已成立；
- 不得把本文件当授权或执行证据；
- 不得声称 P / 4-D / G3 / G4 / G5 任何一项通过；
- `ENABLE` 保持 `0`，候选 RAW region 未冻结。
