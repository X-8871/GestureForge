# S6-E 运行摘要（6-E 离线：验收用例集冻结 + 上板窗口申请材料）

- 任务：`S6-E`（阶段6 6-E 轮的**离线部分**）；RunId：`s6e_acceptance_20261024_r01`；工作树：`D:\codex-worktrees\w6`（分支 `stage6-interact-prep`）。
- 状态：**用例集已冻结、验收未执行**（`case_set_status=FROZEN_PENDING_EXECUTION`、`execution_status=NOT_RUN`）；**未动硬件**；本摘要不构成通过。
- 依据：`CDX-20261022-015`（r03 总入口）、`CDX-20261022-012`（阶段6 运行书 §4/§6）、`CDX-20261023-018/019`、`decisions/stage6_approval_receipt_20261023_r01.md`、`decisions/stage_3_4_direction_20261024_r01.md`。

## 1. 产物

- 机器可读用例集：`docs/stage6/s6e_stage6_acceptance_cases_v1.json`（`S6E-ACC-v1`，26 条用例）。
- 人读版：`docs/stage6/S6E_stage6_acceptance_cases_v1.md`。
- 机器校验器：`verification/s6e_acceptance_check.py`（E1..E11 + 6 类必 FAIL 注入自测）。
- 上板窗口申请材料（**当前未申请**）：`board_window_request.md`（同目录）。
- 本轮真实失败保全：`preserved_failures/`（首轮套件 UNEXPECTED、新鲜证据对在清单过期窗口内的 FAILED 记录，原样保留）。

## 2. 真实命令与退出码

| 检查 | 命令（绝对 `--project-root`） | 实测退出码 |
|---|---|---|
| 用例集校验（基线 E1..E11） | `python -B verification/s6e_acceptance_check.py --project-root D:/codex-worktrees/w6` | **0**（基线 0 错误：ALL_PASS） |
| 注入自测（6 类必 FAIL） | 同上 `--inject-self-test` | **0**（AS_EXPECTED：6/6 注入全被捕获） |
| `check_stage_delivery --mode inputs` | 见 `delivery_manifest.json.checks` / `check_inputs_mode_output.txt` | **0** |
| `check_stage_delivery --mode evidence` | 见 `delivery_manifest.json.checks` / `check_evidence_mode_output.txt` | **0** |

注入自测覆盖的 6 类缺陷（每类都必须被判失败，否则工具判 `UNEXPECTED`）：
`I1` stale 常量漂移（200→150）、`I2` `T6-A03` 填造数值、`I3` 已批准参数集合缺项、
`I4` `UNK-01` 证据类别降级为离线自检、`I5` 用例清空、`I6` 绑定非法参数名。

## 3. 用例集要点（与 `S6E-ACC-v1` 一致）

- **26 条用例**：动作 11 条（ACT-01..11）、未知场景 3 条（UNK-01..03）、恢复 8 条（REC-01..08）、离线自检 4 条（OFS-01..04）。
- **运行手册 §4 的 11 类矩阵类别全部覆盖**（由 E11 断言）。
- 绑定**已批准 24 项参数**（E3/E4 断言集合相等且无未批准项）；跨阶段 `stale_age_limit_ms=200`（E5 与行为表 `T6-STALE_LIMIT.draft_value` 相等）；`T6-A03` 数值必须为 `NOT_RUN` 且该块不得含数值（E6）。
- **必须真实推理结果**：`ACT-01..11`、`UNK-01..03`、`REC-01..06`、`REC-08` 一律 `REAL_INFERENCE_REQUIRED`；`REC-07`（≥30 min 无有效手势）为 `REAL_CAPTURE_REQUIRED`（真实连续时间，不得加速回放冒充）。这些用例一律 `synthetic_substitution_allowed=false`（E7 断言）；合成结果、脚本直接喂类别/`NO_HAND`、离线回放**不得**作为其通过凭据。
- 可先离线自检：`OFS-01..04`（状态机确定性、批准状态机读一致、跨阶段常量、`T6-A03` 未填造）；离线通过**不构成** 6-E 验收。
- 统计口径：`T6-01 ≥0.9`（≥50，每类 ≥10，推荐 ≥100）、`T6-02 ≤0.05`（≥200 独立样本）、`T6-03 ≤1 次/1800 s`；分母不得剔除失败与 `unobserved`；Clopper-Pearson 单列；独立性按人/场景/会话。

## 4. 上板窗口申请材料要点

- 状态 `NOT_REQUESTED`：本轮**不申请、不占用、不保留**窗口；由 DSH 在依赖齐备后按 `CDX-20261023-018` §3 发 OFFER。
- **全局事实（2026-10-24）**：Wong 已将**板卡拔下**（残留会话 0、3121 无监听、COM4 空闲）⇒ **一切板级工作暂停且不设期限**，阶段6 6-E 实物验收暂停；恢复须 Wong 重连后**先重做**受连接判据（真彩目视、部署身份核对）。本材料因此为**就绪待签**，不排期。依据 `decisions/board_detached_boardfree_plan_20261024_r01.md`。
- 与此并行、不需要板卡的工作是**回放预演**（用阶段4 回放结果包 + 阶段5 离线显示回归驱动状态机），其结论必须标注**「回放预演、非实物验收」**。
- 八类门禁：`operator_authorization`、`hardware_session_handoff`、`exclusive_session`、`g0_approval`、`command_delivery_review`、`timing_freeze`、`range_reservation`、`cold_basis`（本材料逐项给出当前状态，缺一不得执行）。
- 建议任务串 `S6-E-REAL::s6_hardware_session_handoff`、scope `S6E_REAL_INFERENCE_ACCEPTANCE`；含 11 字段交接行模板、执行步骤与时长预算（S0–S8，单窗口建议 ≤3 h；REC-07 的 30 min 不可压缩）、6 条停止条件、恢复入口与应留证据。
- 前置未满足项：阶段4 真实推理结果未产出（P1）、阶段5 显示契约未冻结（P2）、`P_meas` 未实测（P5）、Wong 开工信号与独占窗口（P6）、部署身份现场核对（P7）。

## 5. 未执行与不宣称

- 6-E 验收**未执行**（`execution_status=NOT_RUN`）；未申请硬件窗口；未创建 main OFFER/CLAIMED 行；未分配 `hardware_run_id`。
- `T6-A03` 数值仍 `NOT_RUN`（缺阶段4 实测帧周期 P，禁止填造）。
- G3 板测未做；6-D 集成依赖阶段4/5 接口冻结（`BLOCKED`）。
- 阶段3 的板级开工授权**不**自动扩展到阶段6；阶段7 仍未开。
- 本包的 `CHECKS_OK` / `ALL_PASS` 只表示用例集内部一致性、参数绑定与机器断言通过，**不代表** 6-E 验收、独立审查或实物通过。
- 批准记录（`decisions/stage6_approval_receipt_20261023_r01.md`）位于 main 树内，**不在** w6 工作树；本包不绑其哈希，只在 limitations 披露该引用。