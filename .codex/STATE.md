# 阶段5 状态（HDMI 结果显示·离线准备）

更新：2026-10-22 13:15（UTC+8）。工作树 `D:\codex-worktrees\w5`／分支 `stage5-display-prep`；规则见 `D:\FPGA_Competition\AGENTS.md`。
**本树只做阶段5 的离线准备**（规格定稿 + 离线渲染/叠框自测 + 与阶段4 数值链路回归勾连）；**不是阶段5 正式开工，更不是验收**（G0/G1/G3/G4/G5 均未通过）。真实 HDMI 显示与摄像头联调必须等阶段3 完成、阶段4 正式跑通且 2B 让出硬件。

## 目标与范围（离线、可独立验收）
- A 阶段5 契约/G0 定稿；B 离线渲染/叠框自测工具与用例；C 与阶段4 数值链路回归勾连；D 阶段6 草案修订建议（只建议）。
- **明确不做**：真实 HDMI/摄像头联调、上板、烧录、CNN 改动、改 2A 冻结规格、改 2B 接口正文、改 w4 已交付、写主树/w4/dbdf/w2b/96a3/厂商原件、写两个 mailbox 目录。

## 上游绑定（只读）
- 主 STATE `D:\FPGA_Competition\.codex\STATE.md`（阶段5 入口行 HL-T13）；起始提交 `acd2df6`。
- 阶段4 冻结树 `D:\codex-worktrees\w4`（`73c3dad`，四项准备各经独立审查 PASS）：v1 草案（按原文复制，出处 `docs/stage5/PROVENANCE_s4d_v1_baseline.md`）、S4-A G0 草案（`3524d02a…`，DRAFT_NOT_FROZEN）、S4-B `20261021_r13` PASS、S4-C `s4c_replay_20261021_r05` PASS（109/109、误差 0，`c5d25c64…`）。
- **Wong 已定**：① 超 `s2bu/1.1` payload 的结果/耗时/丢帧/过期/状态字段按**方案 B 只记 PS 侧**（扩展帧待与 2B 协商）；② 画面语义固定**最新结果叠加**。
- 阶段3（只读）：实时直通与帧同步成立，**颜色受阻且根因收敛为硬件**（DVP `cmos_d[9]` 无信号），阶段未验收 → 显示实测不可开始。

## 已完成（本轮全部交付）
- **S5-A**：`docs/stage5/S5A_stage5_display_g0_spec_v2.md` + `docs/stage5/s5a_stage5_display_g0_fields.json`（契约 `S5A-G0-v2`）+ `verification/s5_display_geometry_reference.py`（唯一几何/口径来源，`4d9fe369…`，与 D2 冻结实现逐值对拍）+ 自检 26/26 PASS、退出码 0；证据 `report/evidence/S5-A/s5a_g0_20261021_r03/`（**权威**；r01/r02 为加固前历史）。
- **S5-B**：`scripts/stage5_s5b/**`；21 用例、583/583 断言、种子 20261021、随机 round-trip N=64/几何、手算样例 3、五元组 129、HUD 13/13、26 PNG + 21 JSON、双 pass 逐文件 SHA256 一致；证据 `report/evidence/S5-B/s5b_20261021_r07_a|_b`（权威；r06 为历史）。
- **S5-C**：`scripts/stage5_s5c/**`；109/109 样本、104 框、最大 score/坐标误差 0、最大像素往返 0.499 px（门槛 1.0）、S4-B 3/3 与 S4-C 一致、8 个篡改探针全部检出（真实退出码 1）、正对照 0、unittest 27 项 0；证据 `report/evidence/S5-C/s5c_regression_20261021_r04`（权威；r03 为历史）。
- **S5-D**：`docs/stage6/S6D_stage6_revision_suggestions_from_stage5.md`（5 条建议，未改 w4 草案）。
- **独立审查**：第 1 轮 `CHANGES_REQUIRED`（3 项，均文档/证据标注层）→ 第 2 轮聚焦关闭 **PASS**（F-01/F-02/F-03 全部 CLOSED，无新增阻断项）；记录 `report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r01|_r02/`。
- **收尾记录与机器清单**：`report/evidence/S5-CTRL/S5-A01/s5_ctrl_20261022_r02/S5CTRL-20261022-002-stage5-offline-prep-closing-record.md`；交付清单 `report/evidence/S5-A/s5a_g0_20261021_r03/delivery_manifest.json`（`check_stage_delivery.py --mode evidence` **exit 0 / CHECKS_OK**，确定性 SHA `6b3176cf…`；清单 `source_commit` 为起始基线 `acd2df6`，交付以逐文件 SHA-256 绑定）。
- **本阶段提交链**：`0b942ed`（交付本体 425 文件）→ `ff8d78c`（`.gitattributes -text` + 记录）→ `256fc98`（`--renormalize` 143 文件重存）→ 收尾定稿提交（HEAD 以 `git log --oneline -1` 为准）；修复后复验清单绑定 **12/12** 文件 blob==工作树字节、检查器 exit 0、工作区干净。

## 未决与风险
- 待正式 G0/Wong：成品允许延迟上限、颜色表/字号；契约 `discrete_fields_must_match` 拆分（F-01 根因）；阶段4 `stale_age_limit` 仍 `DRAFT_PROPOSED`（阶段5 已按**同源同一常量 200 ms** 使用，正式冻结须同步）。
- 过程缺陷（已登记）：S5-C 的 r01/r02 曾被 Developer 删除（违反证据保留口径、不可恢复，`report/evidence/S5-C/EVIDENCE_RETENTION_INCIDENT.md`）；`dev-s5b`/`dev-s5c` 子代理在恢复重跑时失败退出，S5-B r07 与 S5-C r04 由 Lead 代执行（Reviewer 已独立复现）；首次交付清单被检查器拒绝（exit 2、41 条 schema 违规）已保留为失败证据并注明（`DELIVERY_MANIFEST_SUPERSEDED.md`）；首次提交后发现 EOL 归一化导致 4/12 清单绑定文件 blob≠工作树，已按项目惯例加 `.gitattributes -text` 并重新入库，修复后 blob==工作树字节。
- 硬件：本轮期间本机出现他人 `hw_server`（观测 PID 4812）；2B 书面占用 `CDX-20261021-004/005` **未正式让出** → 本树未启动/重启/结束任何硬件服务，未占 JTAG/COM4。
- **NOT_RUN（需硬件）**：真实 HDMI/摄像头联调、上板、30 分钟无死锁（T5-09）、真实 FPS/延迟（T5-08）、截图/视频、阶段6 联动；S5-B/C 部分用例为 PARTIAL（口径与像素索引级已断言）。

## 证据入口
- `report/evidence/S5-A/s5a_g0_20261021_r03/`（含 `delivery_manifest.json`）、`report/evidence/S5-B/s5b_20261021_r07_a|_b/`、`report/evidence/S5-C/s5c_regression_20261021_r04/`、`report/evidence/S5-CTRL/`（控制记录 + 两轮审查）。
- 临时产物与历史运行：`tmp/5/<task_id>/<run_id>/`（按 `.gitignore` 不入库）。

## 下一步
本阶段离线准备**完成并可交接**。

## S5-T01 上板 bring-up（进行中·受硬件前置阻断）
- 任务卡已建（`task-4`）；硬性前置 = 2B 经 `codex_mailbox` **书面让出 JTAG/COM4** + DSH 宣布空档。**2026-10-22 13:40 更新：Wong 显式授权（13:25「可以上板，codex 已暂停」）→ 门禁 `GO`/exit 0，依据=operator_authorization 且已留痕（不伪造信箱记录）；但两次只读 JTAG 探测均 **0 目标**（JTAG 线 FTDI 与 COM4 在场、无残留服务）⇒ 疑**板卡未上电**，等待上电；未下载位流/ELF、未写寄存器。原判定 `BLOCKED_NOT_RELEASED` 依据＝信箱无书面让出**：门禁 `scripts/stage5_t01/check_hardware_gate.py` 实测 **exit 1**，唯一阻断原因＝信箱无新的让出通知（最近为 `CDX-20261022-006` 占用恢复，明确表示不构成硬件释放；DSH `DSH-20261022-009` 已向 2B 请求让出）。进程枚举**成功**且**无** `hw_server`/Vivado 进程，但**不作为让出依据**。
- 未连接板卡、未启动 `hw_server`、未写任何寄存器（含 `0x503D`）；未烧录 QSPI；未碰他人工作树与两个 mailbox 目录。
- 离线准备件（已交付且可离线验证）：运行书 `docs/stage5/S5T01_stage5_board_bringup_runbook.md`、fail-closed 门禁 `scripts/stage5_t01/check_hardware_gate.py`、注入计划校验器 `scripts/stage5_t01/validate_injection_plan.py`（**8 记录/25 框/0 失败、exit 0**）与示例 `docs/stage5/s5t01_injection_plan_example.json`。
- 前置证据：`report/evidence/S5-T01/s5t01_prereq_20261022_r02/`（`hardware_gate.json`、`run_manifest.json`、`summary.md`）；r01 因门禁进程枚举缺陷（已修、fail-closed）标为被取代。
- 硬件释放后执行：门禁附 `--release-id <让出编号>` 要求 exit 0 → 只读核对板上位流指纹与送显缓冲所有权 → 声明 `overlay_path`（默认 P1 PS 软件叠框，冻结位流零改动）→ 按运行书 §6 验收表出证据；收尾把 `0x503D` 写回 `0x00` 并退出 `hw_server`（不驻留）。阶段5 正式开工入口需同时满足：① Wong/正式 G0 固定成品指标与契约清单拆分；② 阶段3 颜色验收通过；③ 阶段4 正式跑通；④ 2B 明确让出 JTAG/COM4 与 `hw_server`。跨方事项 X-01/X-02/X-03 见收尾记录 §6，由项目总控转达。

## 交接行（11 字段，2026-10-22 13:15）
任务=`HL-T13 阶段5 离线准备（已完成，提交链 `0b942ed`→`a4baab4`）+ S5-T01 上板 bring-up（离线准备就绪、受 2B 书面让出硬件阻断）` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`acd2df6`（S5-T01 以 `a4baab4` 为基线） | 允许修改范围=`docs/stage5/**`（含 `S5T01_*`）、`scripts/stage5_*/**`、`report/evidence/S5-*/**`、`tmp/5/**`、`.codex/STATE.md` | 未提交改动归属=`本树全部为本轮产物，与 STATE 同批提交（tmp/ 为忽略项；无他人改动混入）` | 让出声明=`已认领：S5-T01 由本阶段总控独占写入（IN_PROGRESS）；当前无让出` | 心跳(UTC+8)=`2026-10-22 13:15` | 证据入口=`report/evidence/S5-A/s5a_g0_20261021_r03/`、`report/evidence/S5-B/s5b_20261021_r07_a/`、`report/evidence/S5-C/s5c_regression_20261021_r04/`、`report/evidence/S5-CTRL/S5-A01/s5_ctrl_20261022_r02/` | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`IN_PROGRESS（S5-T01 上板 bring-up，BLOCKED 待 2B 书面让出 JTAG/COM4 + DSH 宣布空档；离线准备件已就绪）/ 本阶段总控；阶段3 灰度 provisional freeze（颜色 DEFERRED_PENDING_MODULE）`