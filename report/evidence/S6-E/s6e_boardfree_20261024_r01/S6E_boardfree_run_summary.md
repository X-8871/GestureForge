# S6-E 无板卡轮运行摘要（延迟方法学 + 6-E 窗口申请包就绪化）

- 所属：阶段6 `task-28`（无板卡轮）；RunId：`s6e_boardfree_20261024_r01`；工作树 `D:\codex-worktrees\w6`。
- 状态：**离线产物已交付；回放预演（`task-28` 第 1 项）`BLOCKED`**（依赖阶段4 回放结果包 `task-26` 与阶段5 离线显示回归 `task-27`，两者尚未完成）。
- 全局事实：**板卡已由 Wong 拔下（2026-10-24）⇒ 板级工作暂停且不设期限**，6-E 实物验收暂停；恢复须先重做受连接判据（真彩目视 + 部署身份）。
- 边界：本轮**未动硬件**、未 push、未自称已审查/已通过；**不得**把回放/离线结论写成 6-E 通过或实物验收通过。

## 1. 本次交付（`task-28` 第 2、3 项）

| 项 | 产物 | 说明 |
|---|---|---|
| 2 | `docs/stage6/S6E_latency_methodology_v1.md` | 回放口径端到端延迟测量方法学：`t_trigger`/`window_complete`/`t_submit`/`t_effective` 定义、时间源声明、M1–M6 测量步骤、**禁用填造**结构约束 |
| 2 | `docs/stage6/s6e_latency_measurement_template_v1.json` | 机读**占位模板**（`S6E-LAT-v1`）：所有 `*_ns` 字段为 `null`、`T6-A03` 值 `NOT_RUN`、`t6_a03_limit_ms=null` |
| 2 | `verification/s6e_latency_template_check.py` | 校验器 L1..L7 + **5 类必 FAIL 注入**（填数值/改 `T6-A03` 值/填上限/改 `value_status`/删「回放不构成实时证据」） |
| 3 | `board_window_readiness.md`（本目录） | 6-E 单次窗口申请包**就绪度核对**：八类门禁与 P1–P7 前置**如实**列出现状，结论 **`NOT_READY`** |

- 申请包本体（范围/时长/前置/停止条件/恢复入口 + 11 字段模板）为 `task-23` 产出：
  `report/evidence/S6-E/s6e_acceptance_20261024_r01/board_window_request.md`（状态 `NOT_REQUESTED_BOARD_DETACHED`，**未申请、不排期**）。

## 2. 真实命令与退出码

| 检查 | 命令（绝对 `--project-root`） | 实测退出码 |
|---|---|---|
| 延迟模板校验（基线 L1..L7） | `python -B verification/s6e_latency_template_check.py --project-root D:/codex-worktrees/w6` | **0**（基线 0 错误：ALL_PASS） |
| 延迟模板注入自测（5 类必 FAIL） | 同上 `--inject-self-test` | **0**（AS_EXPECTED：5/5 注入全被捕获） |
| `check_stage_delivery --mode inputs` | 见 `delivery_manifest.json.checks` / `check_inputs_mode_output.txt` | **0** |
| `check_stage_delivery --mode evidence` | 见 `delivery_manifest.json.checks` / `check_evidence_mode_output.txt` | **0** |

## 3. `T6-A03` 与「禁填造」口径

- `T6-A03` 数值**保持 `NOT_RUN`**：口径已批准（`t_effective − window_complete`），数值须阶段4 在同一部署身份上实测帧周期 P 后填写。
- 模板在**结构上**禁止填造：`P_meas_*` 与全部延迟 `*_ns` 均为 `null`；`acceptance_gate.t6_a03_limit_ms` 为 `null`；
  任何填写必须同时给出 `filled_from_run_id` + `evidence_class` + 可复核命令。
- **回放不构成实时证据**：回放时钟 ≠ 墙钟，回放延迟只对回放输入有效，不得用于填写 `T6-A03` 或宣称上限达标。

## 4. `task-28` 第 1 项（回放预演）：`BLOCKED`

- 依赖：阶段4 **回放结果包**（`task-26`，其前置为 `task-25` 的回放输入包）+ 阶段5 **离线显示回归**（`task-27`）。
- 当前状态：两者均 **`pending`**（未产出）⇒ 无法驱动状态机跑 `S6E-ACC-v1` 的动作/未知/恢复用例。
- 解阻条件：`task-26`、`task-27` 交付后，用其结果驱动状态机跑冻结用例集，产出**预演结果**并标注「回放预演、非实物验收」；
  预演**不改变**八类门禁状态，`ACT/UNK/REC` 一律维持 `REAL_INFERENCE_REQUIRED`/`REAL_CAPTURE_REQUIRED` 且 `synthetic_substitution_allowed=false`。

## 5. 不宣称

- 6-E 验收**未执行**；`OFS-01..04` 的离线自检**不构成** 6-E 验收。
- `T6-A03` 数值 `NOT_RUN`；G3 板测未做；6-D 集成依赖阶段4/5 接口冻结（`BLOCKED`）；阶段7 未开。
- 本包 `ALL_PASS`/`CHECKS_OK` 只表示模板结构约束、清单绑定与机器断言通过；**不代表**任何实物或验收结论。