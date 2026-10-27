# 阶段4 冻结签发（离线范围）

- 任务：`S4-FREEZE-SIGN`（阶段4 冻结签发）
- 负责人：Workbuddy 阶段4总控
- 签发时刻：2026-10-27 14:30（UTC+8）
- 授权依据：Wong 2026-10-27 明示「尽快完成阶段四冻结，决策你来决定，优先最快」，并告知**硬件窗口暂时不能授权**
- 判定：**`OFFLINE_SCOPE_FROZEN`（离线范围冻结，已签发）**
- 校验结果：`report/evidence/S4-CTRL/s4_frozen_set_verify_20261027_r04/` → `FROZEN_SET_VERIFIED` / `exit 0` / **8 项全通过**

---

## 1. 为什么是「离线范围冻结」而不是整体冻结

硬件窗口不能授权，意味着下面三件事在当前节点**结构上不可达**，与是否努力无关：

| 缺口 | 不可达的原因 |
|---|---|
| `hardware_session_handoff` | 必须由 main 在 main 的 STATE 提交 `S4-B-REAL-02B::s4b_hardware_session_handoff` OFFER，且**心跳 1 小时内**有效；阶段4 不得写 main。OFFER 后还需 w4 在同一小时内 CLAIM |
| `exclusive_session` | 必须在执行时现场取证（`hw_server` PID + 3121 + UART，**30 分钟**窗口）；窗口不授权则无法取证，提前生成必过期 |
| 板级 P / 4-D / G3 | 需要真实上板运行，窗口不授权即 `NOT_RUN` |

因此「整体冻结」在硬件窗口关闭期间不可能达成。把它写成已达成，就是伪造。
本签发只冻结**离线链**——这条链本身是完整、可复算、可被下游消费的。

---

## 2. 冻结集（8/8 校验全部通过）

| 编号 | 对象 | 冻结状态 | 证据 |
|---|---|---|---|
| F1 | 共享输入/结果契约 `s4b_shared_input_result_contract.json` | `FROZEN_OFFLINE_ONLY` / `s4-shared-io/1.3.0` r07，含 `freeze_record` 与 `post_freeze_rebinds` | 契约自检 27/27 |
| F2 | stage4 地址图 + 共享地址图 | 双 `APPROVED`，各附 `approved_by=Wong`、`review_binding`（SHA 可复算） | `s4b_address_approval_review_20261027_r01` |
| F3 | task-26 权威门 | `PASS` / `exit 0` / 六项检查全 PASS；桥接器 `c6117bb4…` 与工作树一致；preflight 自哈希自洽 | `s4t26_gate_rerun_20261027_r04` |
| F4 | task-27 回放包 ×2 | 均 `replay_only`；带框包 `detections=1`（fist 0.769708） | `s4t27_replay_package_freeze_20261027_r01` / `s4t27_replay_positive_20261027_r01` |
| F5 | 硬件门禁记录 | **6/8 成立**（含 `g0_approval`、`cold_basis`），经 adapter 判定接受 | `s4b_hw_gates_20261027_r04` |
| F6 | 门禁记录目录清单 | `manifest` 覆盖完整（6 记录 + index） | 同上 |
| F7 | BGR888→RGB 通道重排 | RTL 参数在位；xsim 双跑对照（ch0=R / 关闭=B） | `s4b_bgr_remap_20261027_r01` |
| F8 | 声明卫生 | 人读文档中无「G3/G5 已通过」「整体冻结」等过度声明（否定句豁免） | 同校验 |

校验器：`verification/verify_stage4_frozen_set.py`（只读、可复跑、异常 exit 2 不伪装成未通过）。

---

## 3. `cold_basis` 的取得方式与边界

本轮用 **`basis_kind = independently_proven_cold_lifecycle`（等价独立证明）**，不是物理断电：

- 实时复算：`hw_server` 进程数 0、3121 端口无监听、无 `hw_axi` 进程；
- 全仓交叉核验：排除 2026-10-23 复审负控夹具（`fake_*` / `api_root_probe`）后，**真实板上执行记录为 0**；
- 推论：阶段4 从未建立 JTAG 会话 ⇒ AXI 总线上不存在本阶段遗留事务 ⇒ 等价于冷启动。

**边界（必须保留）**：

- 它证明的是「无遗留 AXI 事务」，**不是**「刚发生过物理断电」；
- **一旦出现任何 AXI 事务或启动过 `hw_server`，本证明立即失效**，必须重新评估；
- 若后续要求物理断电凭据，应另出 `physical_power_cycle` 记录，两者不可互相替代。

交叉核验时曾把 2 条 `EXECUTED_WITH_EXPLICIT_GATES` 与 8 条 `FAILED_OR_INCOMPLETE` 当作真实执行，
逐条核查后确认全部位于复审夹具路径下。该过程已写入证据的 `honesty_note`，不隐藏。

---

## 4. 冻结范围内可以做什么 / 不可以说什么

**可以**：

- 阶段5 / 阶段6 按契约版本 `s4-shared-io/1.3.0` r07 **只读消费**结果语义与显示字段；
- 以两个回放包做离线回归、数值对拍、下游接入验证；
- 引用 task-26 门的离线 PASS 说明「离线链路数值一致性成立」。

**不可以**：

- 声称板上行为、PL 真实运行、UART 实收、真实摄像头采集质量；
- 声称 P / 4-D / G3 / G4 / G5 任何一项通过；
- 把回放结果当实时结果；
- 把 `cold_basis` 的等价证明说成物理断电凭据；
- 把 producer provenance 的已登记断点说成可复现。

---

## 5. 解除条件（转入整体冻结前必须满足）

| 编号 | 条件 | 责任方 |
|---|---|---|
| R-1 | 硬件窗口授权 | Wong |
| R-2 | main 提交 `S4-B-REAL-02B::s4b_hardware_session_handoff` OFFER（心跳 1h） | main / DSH |
| R-3 | w4 提交 CLAIM（`scripts/stage4_s4b/make_claim_line.py` 自动取 blob_oid/sha256） | 阶段4 |
| R-4 | 现场取证 `exclusive_session`（30 min 内） | 阶段4 |
| R-5 | 执行 `S4-B-REAL-02B` 板级诊断（装载→RUN→停泊→双读导出→解码） | 阶段4 |
| R-6 | 板级 P 实测、4-D 端到端、G3 实物验证 | 阶段4 + 硬件窗口 |
| R-7 | `raw_address_ownership` 提案 D1–D4 裁决（注意其 B ≠ 方向方案的 B） | Wong |

R-2 到 R-4 必须在**同一小时内**串行完成；R-4 到 R-5 必须在 30 分钟内。

---

## 6. 复跑命令

```bash
cd D:/codex-worktrees/w4

# 冻结集完整性（本签发的判定依据）
python -B verification/verify_stage4_frozen_set.py \
  --evidence-dir report/evidence/S4-CTRL/s4_frozen_set_verify_<新RunId>

# 契约自检
python -B scripts/stage4_s4ctrl/verify_shared_io_contract.py \
  --evidence-dir report/evidence/S4-CTRL/s4t26_contract_verify_<新RunId>

# RAW G0 缺口复算
python -B scripts/stage4_s4b/audit_raw_system_g0_gaps.py \
  --evidence-dir report/evidence/S4-CTRL/s4t26_gap_audit_<新RunId>

# 硬件门禁就绪（硬件窗口开启前应保持 BLOCKED，只余 handoff / exclusive_session）
python -B scripts/stage4_s4b/check_hardware_gate_readiness.py \
  --run-id s4b_hw_gate_readiness_<新RunId> \
  --preparation "D:/codex-worktrees/w4/tmp/4/S4-B-REAL-02B/s4b_ps_adapter_g3_20261027_r01/adapter_preparation.json" \
  --hardware-run-id s4b_ps_tensor_hw_20261027_r01 \
  --gate-dir report/evidence/S4-B/s4b_hw_gates_20261027_r04 \
  --evidence-dir report/evidence/S4-B/s4b_hw_gate_readiness_<新RunId>
```

---

## 7. 未做（明确记录）

- 未接触板卡 / JTAG / COM4 / Vivado / `hw_server`；未下载、未烧录、未开阶段7；
- 未在 main 写任何行；未改 main / dbdf / w2b / w5 / w6 / 厂商原件；
- `ENABLE=0` 未变；
- 未把任何 `NOT_RUN` 写成已执行，未把任何断点写成通过。
