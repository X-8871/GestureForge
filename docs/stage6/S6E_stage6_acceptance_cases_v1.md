# 阶段6 6-E 验收用例集 v1（动作 / 未知场景 / 恢复）

- 契约令牌：`S6E-ACC-v1`；RunId：`s6e_acceptance_20261024_r01`；状态：**用例集已冻结、验收未执行**（`case_set_status=FROZEN_PENDING_EXECUTION`、`execution_status=NOT_RUN`）。
- 机器可读权威：`docs/stage6/s6e_stage6_acceptance_cases_v1.json`（两者冲突以 JSON 为准，并由 `verification/s6e_acceptance_check.py` 机器校验）。
- 本文件只**冻结**验收用例与判定口径；**未执行任何 6-E 试验、未动硬件**，不构成任何指标通过。

## 0. 绑定与边界

- 参数来源：`docs/stage6/s6a_stage6_g0_behavior_v1.json`（契约 `S6A-G0-v1.8`）；**24 项参数**已按草案值获 Wong 批准（2026-10-23，批准记录 `report/evidence/CTRL-DSH-HANDOFF/decisions/stage6_approval_receipt_20261023_r01.md`）；**参数值未修改**。
- 跨阶段 `T6-STALE_LIMIT` = **200 ms**，阶段4/5/6 必须同源引用；比较符严格 `>`：`age = 200 ms` **不**判过期，`200 ms + 1 ns` 判过期。
- `T6-A03` 交互延迟：**口径已批准**（`t_effective − window_complete`），**数值仍 `NOT_RUN`**（缺阶段4 实测帧周期 P），**禁止填造**。
- 边界：6-D 集成依赖阶段4/5 接口冻结（`BLOCKED`）；G3 板测未做；阶段7 未开。

## 1. 证据类别（哪些必须真实推理结果）

| 类别 | 含义 | 不得用它冒充 |
|---|---|---|
| `REAL_INFERENCE_REQUIRED` | 必须用**真实推理结果**（阶段4 在板上对真实摄像头采集帧的推理输出） | 合成结果、脚本直接喂类别/`NO_HAND`、离线回放 |
| `REAL_CAPTURE_REQUIRED` | 必须用**真实摄像头采集 + 连续真实时间** | 回放/加速回放冒充物理运行 |
| `REPLAY_ONLY` | 允许回放，但结论只对回放输入有效并须标注 | 升级为实物/集成结论 |
| `OFFLINE_SELFCHECK` | 可离线自检，**不构成 6-E 验收** | 当作 6-E 通过凭据 |

**关键点（`CDX-20261022-012` §4/§6）**：脚本直接喂 OK/`NO_HAND` **不能**支撑摄像头下的未知误接受率；合成源与离线通过**不得**升级为实物集成通过。

## 2. 统计与样本口径（冻结）

| 指标 | 定义 | 门槛 | 最小样本 | 分母纪律 |
|---|---|---|---|---|
| `T6-01` | 已知手势有效动作成功率 | `≥ 0.9` | ≥50（每类 ≥10，推荐 ≥100） | 含全部预定义试验；超时/错误动作/重复触发/执行失败/`unobserved` 不得剔除 |
| `T6-02` | 独立未知输入误接受率 | `≤ 0.05` | ≥200 独立未知样本 | 执行失败不豁免；样本级判定 |
| `T6-03` | 无有效手势连续 ≥30 min 误动作次数 | `≤ 1` 次/1800 s | 1 段 ≥1800 s | 记录完整时段，不得裁剪成功片段 |

- 置信区间默认 **Clopper-Pearson** 并单列；点估计达标**不等于** 95% 上界达标。
- 独立性按**人 / 场景 / 录制会话**区分；同一段循环 200 次 ≠ 200 个独立样本；相邻帧不得自动当独立试验。
- 保留真实输入、检测输出、状态/动作日志、连续视频及**全部失败**；正式测试前固定阈值，失败需调参时改用开发/验证数据并在新的留出集重新验收。

## 3. 用例总表（26 条）

| 用例 | 组 | 运行手册类别 | 证据类别 | 期望要点 | 绑定参数 |
|---|---|---|---|---|---|
| ACT-01 | 动作 | 每类稳定输入 | REAL_INFERENCE | fist → `A_SWITCH_UI/UI_MENU`，恰好一次且生效可观察 | C01,S01,S02,S03,P01,P02,T6-01 |
| ACT-02 | 动作 | 每类稳定输入 | REAL_INFERENCE | palm → `A_SWITCH_UI/UI_STATS` | 同上 |
| ACT-03 | 动作 | 每类稳定输入 | REAL_INFERENCE | one → `A_SWITCH_CHANNEL/CH_1` | 同上 |
| ACT-04 | 动作 | 每类稳定输入 | REAL_INFERENCE | two_up → `A_SWITCH_CHANNEL/CH_2` | 同上 |
| ACT-05 | 动作 | 每类稳定输入 | REAL_INFERENCE | three → `A_SWITCH_CHANNEL/CH_3` | 同上 |
| ACT-06 | 动作 | 持续保持与冷却后保持 | REAL_INFERENCE | 同获取内**恰好一次**提交（B15） | K01,A02,S01,S02 |
| ACT-07 | 动作 | 持续保持与冷却后保持 | REAL_INFERENCE | 冷却为**全局门**：任意目标/获取冷却内不得提交（B13/H-10） | K01,S01,S02,L01,L02 |
| ACT-08 | 动作 | 手离开再出现 | REAL_INFERENCE | 重获=新获取（新 `acquisition_id`）可再触发一次（B11） | L01,L02,K01,S01,S02 |
| ACT-09 | 动作 | 两类快速切换/短暂抖动 | REAL_INFERENCE | 中断 ≤ J01 不重置、= J01+1 立即重置；未达条件 0 动作（B08） | J01,S01,S02,C01 |
| ACT-10 | 动作 | 多目标/同分/目标跳变 | REAL_INFERENCE | 维持优先、同分按 2A 稳定顺序、跳变重新满足窗口（B03/B05/B12） | P01,P02,P03,P04,P05 |
| ACT-11 | 动作 | 动作失败/未观察/重复ACK | REAL_INFERENCE | 不虚报成功；`unobserved` 单列且不从分母剔除（B28） | A01,A02,T6-01 |
| UNK-01 | 未知 | NO_HAND/场景未知/低分 | REAL_INFERENCE | ≥200 独立未知样本，误接受率 ≤5%（T6-02） | T6-02,P01,P02,STALE |
| UNK-02 | 未知 | NO_HAND/场景未知/低分 | REAL_INFERENCE | 零框合法（不推进匹配、不得完成窗口）；与未知分开计数（B17/B20） | P01,P02,T6-02 |
| UNK-03 | 未知 | NO_HAND/场景未知/低分 | REAL_INFERENCE | 非法结果拒绝、保留原始值、**不得**改写为 NO_HAND（B19） | U00_W,U00_N,U01 |
| REC-01 | 恢复 | TIMEOUT/ERROR/DROPPED/stale | REAL_INFERENCE | 无动作、时间照常推进、可恢复（B21） | U00_W,U00_N,U01,S04 |
| REC-02 | 恢复 | TIMEOUT/ERROR/DROPPED/stale | REAL_INFERENCE | 过期帧不触发、显式标年龄（B18） | STALE,S01,S02 |
| REC-03 | 恢复 | 重复、倒序、缺帧、重启帧号 | REAL_INFERENCE | 不重复计票、不错误延续（B22/B23/B24） | U00_W,U00_N,L02 |
| REC-04 | 恢复 | 重复、倒序、缺帧、重启帧号 | REAL_INFERENCE | 会话切换全量复位、禁止静默续用（B25） | C01,S01 |
| REC-05 | 恢复 | 时间等于阈值、前后1单位 | REAL_INFERENCE | 边界两侧判定与 §12 一致（过期严格 `>`） | STALE,S01,L02,K01,S04 |
| REC-06 | 恢复 | 无新结果但时间持续前进 | REAL_INFERENCE | 失踪/超时按单调时钟生效，不停帧保持候选 | L02,S04,U00_W |
| REC-07 | 恢复 | 无新结果但时间持续前进 | **REAL_CAPTURE** | 连续 ≥30 min 无有效手势误动作 ≤1 次（T6-03） | T6-03,L01,L02,K01,STALE |
| REC-08 | 恢复 | TIMEOUT/ERROR/DROPPED/stale | REAL_INFERENCE | 异常停止与安全恢复（§6 异常停止） | A01,K01,STALE |
| OFS-01 | 离线自检 | 11 类矩阵的离线前置 | OFFLINE_SELFCHECK | S6-B 26 例 + 4 探针 PASS（只称确定性测试 PASS） | S02,S03 |
| OFS-02 | 离线自检 | 规格一致性 | OFFLINE_SELFCHECK | 24 项均 APPROVED 且有批准索引；包内无「仍待批准」陈述 | 全部 24 项 |
| OFS-03 | 离线自检 | 跨阶段常量 | OFFLINE_SELFCHECK | `stale` 三处同源同一常量 200 ms | STALE |
| OFS-04 | 离线自检 | 开放项纪律 | OFFLINE_SELFCHECK | `T6-A03` 数值必须为 `NOT_RUN` | A03 |

## 4. 超时与失败保全（统一要求）

- 每条例外用保存状态、判定口径、超时（见 JSON `timeout_s`）、失败保全与恢复方法；**失败不覆盖、不筛掉**。
- 失败保全统一包含：原始输入/检测输出流、状态与动作日志（JSONL）、连续视频、异常计数、板卡最终状态与命令 + 真实退出码。
- 出现**无有效输入却连续动作、状态机卡死、无法解释的旧帧触发、日志丢失**之一 ⇒ 立即停止本次验收、保全原始证据、按冻结的安全状态恢复，并以**新 RunId** 重测（不得就地续跑、不得继续计作成功运行）。

## 5. 上板窗口申请（摘要）

- 申请材料：`report/evidence/S6-E/s6e_acceptance_20261024_r01/board_window_request.md`。
- 八类门禁（缺一不得执行）：`operator_authorization`、`hardware_session_handoff`、`exclusive_session`、`g0_approval`、`command_delivery_review`、`timing_freeze`、`range_reservation`、`cold_basis`。
- 前置：阶段4 **真实推理结果**产出且其结果记录契约冻结；阶段5 显示契约冻结；6-E 用例集冻结（本文件）；Wong 开工信号与板卡独占窗口由 DSH 发 OFFER。
- 说明：本用例集**未申请窗口**（`NOT_REQUESTED`），窗口由 DSH 在依赖齐备后按 `CDX-20261023-018` §3 办理。
- **全局事实（2026-10-24）**：Wong 已将板卡拔下 ⇒ **板级工作暂停且不设期限**，6-E 实物验收暂停；
  恢复须 Wong 重连后先重做受连接判据（真彩目视、部署身份核对）。不需要板卡的部分以**回放预演**推进，
  结论必须标注**「回放预演、非实物验收」**，不得升级为 6-E 通过或实物验收通过。

## 6. 不宣称

`6-E` 验收未执行；`T6-A03` 数值仍 `NOT_RUN`；G3 板测未做；6-D 集成 `BLOCKED`；真实推理结果尚未产出。本文件所有结论均为**离线用例冻结**。