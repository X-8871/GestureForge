# 阶段6 6-E 端到端延迟测量方法学 v1（回放口径；**禁用填造**）

- 契约令牌：`S6E-LAT-v1`；RunId：`s6e_boardfree_20261024_r01`；状态：**仅方法学与占位模板**（`TEMPLATE_ONLY_NOT_RUN`）。
- 机器可读模板：`docs/stage6/s6e_latency_measurement_template_v1.json`；校验器：`verification/s6e_latency_template_check.py`。
- 依据：`CDX-20261022-012`（阶段6 运行书 §6/§7）、`docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` §15、`report/evidence/CTRL-DSH-HANDOFF/decisions/stage6_approval_receipt_20261023_r01.md`。
- **本文件不填任何延迟数值**；`T6-A03` 数值保持 `NOT_RUN`（须阶段4 真实实测帧周期 P）。模板在结构上**不得填造**：所有 `*_ns` 占位必须为 `null`，校验器对任何数值即判失败。

## 1. 定义（与已批准口径逐字一致）

| 量 | 定义 |
|---|---|
| `t_trigger` | 触发该动作的**那条结果**的显式输入时刻（其 `time_source` 必须声明） |
| `t_submit` | 动作**提交**时刻（`ACTION_SUBMITTED`） |
| `t_effective` | 动作**生效**时刻（显示侧回执 `ACTION_EFFECTIVE`；未观察不得算成功） |
| `window_complete` | **第一个**同时满足「连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`」与「时长 ≥ `T6-S01`」的**窗口推进帧**的显式输入时刻（`T6-S03` 取较晚，B-04/N-r05-04） |
| `latency_action` | `t_effective − t_trigger`（受 `T6-A01` ≤ 1000 ms 约束） |
| `latency_interaction` | `t_effective − window_complete`（受 `T6-A03` 约束；**上限数值 `NOT_RUN`**） |
| `W_min` | `max(T6-S01, (T6-S02 − 1) · P)` —— **只是下界，不得进入延迟统计** |

- 两者**必须分别报告**，不得互相替代；日志必须给出该次获取所用的 `P_meas` 与 `window_complete`。
- 过期口径：`age_result > 200 ms` 判过期（严格 `>`；`= 200 ms` 不判过期）。

## 2. 时间源与回放口径（关键限制）

- `time_source ∈ { board_monotonic, injected, replay }`，**必须逐条声明**。
- **回放时钟 ≠ 墙钟**：回放的时间缩放、基准与推进方式必须显式记录；**回放口径的延迟不得作为实时/实物证据**，不得用于填写 `T6-A03`。
- 真实测量必须满足：`time_source = board_monotonic`、`P_meas` 来自**同一部署身份**（bit/XSA/ELF 哈希一致）的实测、且采集与显示在同一 PS 单调时基上。
- 加速回放只能验证相应时序条件，**不得**冒充物理运行（运行书 §5.4）。

## 3. 测量方案（步骤，回放/上板同构）

| 步 | 内容 | 必填字段 | 备注 |
|---|---|---|---|
| M1 | 绑定部署身份与时间基准 | `bit_sha256`/`xsa_sha256`/`elf_sha256`、`time_source`、`clock_note` | 每次使用前重新核对现场 |
| M2 | 实测帧周期 `P_meas`（连续 ≥1000 帧，取中位数与 p95） | `P_meas_ns`、`P_meas_p95_ns`、`P_meas_source`、`P_meas_measured_at_utc8` | **回放不得填**；上板窗口内测量 |
| M3 | 逐试验记录四个时刻（`t_trigger`/`window_complete`/`t_submit`/`t_effective`） | 四个字段 + `trigger_frame_id` + `acquisition_id` | 同帧关联；缺失即该试验计失败 |
| M4 | 计算两条延迟并分别汇总 | `latency_action_*`、`latency_interaction_*` | 分母含全部预定义试验，`unobserved` 单列且不剔除 |
| M5 | 分位数与样本口径 | `p50`/`p95`/`p99`、`samples`、`per_class` | 点估计不用来宣称上限达标 |
| M6 | 与门槛比对 | `t6_a01_limit_ns`（=1 000 000 000 ns）、`t6_a03_limit_ns` | `t6_a03_limit_ns` 在 `T6-A03` 获批数值前必须为 `null` |

## 4. 禁止填造（结构约束）

1. 模板内**所有 `*_ns` 字段**必须为 `null`，直到 M2 在**同一部署身份**上真实测到 `P_meas`；
2. `P_meas` 缺失时 `latency_interaction_*` 一律不得填写（`W_min` 只是下界，不得当实测）；
3. 任何填写必须同时给出 `filled_from_run_id`、`evidence_class` 与可复核命令/退出码；
4. 校验器（`s6e_latency_template_check.py`）对「填了数值 / 改了 `T6-A03` 状态 / 删掉回放限制声明」一律判 **FAIL**（含必失败注入自测）。

## 5. 不宣称

- 本文件与模板**不含任何测量结果**：`T6-A03` 数值仍 `NOT_RUN`，G3 板测未做，6-D 集成依赖阶段4/5 接口冻结（`BLOCKED`）。
- **板卡已由 Wong 拔下**（2026-10-24）⇒ 板级工作暂停；`P_meas` 与实时延迟须在 Wong 重连后的**单次窗口**内测量。
- 回放口径的延迟结果只对**回放输入**有效，**回放不构成实时证据**，不得用于 6-E 通过或实物验收结论。