# 阶段6 STATE（S6-A/S6-B/S6-E 交互控制；离线部分）

## 目标
阶段6 交互控制：五类动作判定、多框选择/同分排序、目标保持与重获、抖动/稳定窗口、冷却与再触发、
持续保持只触发一次；产出 G0 行为表 + S6-B/S6-C 实现与确定性证据 + 6-E 验收用例集。硬件（摄像头/板测）不在本轮。

## 当前事实（2026-10-24，6-E 离线轮）
- 契约：`S6A-G0-v1.8`；**24 项参数按草案值获 Wong 批准**（2026-10-23，批准记录在 main：
  CTRL-DSH-HANDOFF/decisions/`stage6_approval_receipt_20261023_r01.md`）；行为表含 `approval_record` +
  24 项 `approval_status=APPROVED_20261023` 与 `approval_ref`；**参数值未修改**。
- `T6-A02`=500ms 保持；`B16 S_DEDUP` 设计上不可达（H-10 全局冷却门覆盖）不计入覆盖；`T6-S01`=200ms/`T6-S02`=6
  （30fps 第 8 帧 233.1ms，按 `T6-S03`「取较晚」）；`U6-12` 保留 M4 并计入覆盖；`U6-16` STABLE 获取内锁存；
  `U6-15`=`A_SWITCH_UI`+`A_SWITCH_CHANNEL`；`U6-13` 口径固化、**数值 `NOT_RUN`**；`T6-STALE_LIMIT`=200ms（阶段4/5/6 同一常量）。
- 关键机制事实：S6-A 自检 17 项（C4 批准纪律、C8 已批准包扫描、C11 清单/STATE、C16 语义可达性）；S6-B 26 条确定性用例 + 4 项探针；
  `claim_verify` 逐条真实退出码且 verdict 由全部 claim 计算；`export_selfproof` 必须显式 `--s6a-run`。

## 谓词绑定口径（与行为表逐字一致）
> M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段。

## 冻结链与轮次关系
- F4/G4（`6b8e5f2a`/`f5b749ed`，tag r3）→ F5/G5（`caa9728a`/`61caac0d`，tag r4，**已降级为非冻结记录**）→
  F6c/G6（`0a2abc49`/`a2d232da`，tag r5）→ **F6d/G6b（`2f16d668`/`538b7923`，tag r6，当前有效冻结）**。
- **本轮（6-E 离线）产出 r13/r08 修订内容**：不新打冻结 tag、**不称已冻结/已审查**；终审批次 E 的关闭项逐条落实，独立复评由项目总控另派。
- **A1 失实陈述更正（终审 E §五）**：G6b STATE 曾写「规格文档拆分当时/现口径、**8 条历史修订行写回当时状态并标注历史语境**」——
  终审 E 复核为**实际 0 条写回、7/8 无标记**，该表述属「把未做写成已做」。**本轮 r13 已真正落实**（8 行写回 `PENDING_APPROVAL`（当时状态）+ 逐行机读标记 `【历史语境】`）。
- 旧 tag（r1..r6 与 per-profile tag）保留不动；旧 RunId r01..r12 / r01..r07 **不就地改写**。

## 6-E 离线轮完成项（A 组：结清被推迟的遗留清单）
- **A2 规格改准**：L9/L171/L185/L282/L320/L321 改为已批准口径（L128/L397 保留机读历史标记）；另修 L10/L184/L313/L47/L186 附近口径。
- **A3 历史行写回**：8 条修订行（L14/21/28/30/32/34/36/38）写回当时状态 `PENDING_APPROVAL` 并逐行加 `【历史语境】`。
- **A4 机读假命题清除**：`fix_record.json` 的 `all_parameters_pending_approval: true` 删除，改为 `all_parameters_approved_20261023: true`；
  陈旧 `new_run_id` 改准为 r13；覆盖矩阵位置标签与 C4 标签改准；S6-B 侧 `reachability_notes.derived_from`、
  `case_matrix`/`build_case_matrix.py` 的现行陈述改为 APPROVED 口径；矛盾文本（`limitations` 指标口径、「草案值 草案值」）已修。
- **A5 扫描器收紧**：`approved_package_scan.py` 改**大小写不敏感**（修死正则）、收窄逐行豁免（机读历史标记/非批准类状态/禁止性规则描述）、
  注入/探针/失败证据按**文件级**豁免；对旧包 r12 仍报 5 处命中（判别力反例），对 r13/r08 为 `CLEAN`。
- **A6 双向必失败注入**：`--inject-self-test` 改为两向 —— B1..B7 必判失败形态**全部命中**、C1..C4 必须放行对照**全部不命中**；纳入 claim `S6A-C8`/`S6B-C5` 与套件用例。
- **A7 批次 C 三项**：① `fresh_selfcheck_pair.json` 由 claim `S6A-C6` 对**清单当前**状态实跑生成并入库（S6-B 侧由 `--fresh-pair` 在不动点内跑）；
  ② 套件两条必 FAIL 例改为**只在临时副本**内运行（不再改写真实附录）；③ 套件 `skipped` 改为 **fail-closed**（`INCOMPLETE_SKIPPED` + 退出码非 0），
  新增 `--simulate-skip` 必 FAIL 自测，套件产物 `tool_self_tests.json` 直接入库。
- **A8 复跑**：见「证据入口」中三包清单 `checks` 的真实退出码（r13 4/4、r08 6/6、S6-E 4/4 全 PASS 且 exit 0）。
- **快照自证（提交前，2026-10-24）**：S6-A 剖面 `--worktree-snapshot --s6a-run r13` → `ALL_SELF_PROVEN [0,0,0]` exit 0；
  双剖面（+`--s6b-run r08`）→ `ALL_SELF_PROVEN [0,0,0,0]` exit 0；报告见两条 `_selfproof` 目录（提交后另以 `--commit <交付提交>` 追加提交主体）。

## 6-E 离线轮完成项（B 组：真实推理验收用例与窗口材料）
- **用例集 v1**（`S6E-ACC-v1`，26 条：动作 11 / 未知 3 / 恢复 8 / 离线自检 4），绑定已批准 24 项与 `stale=200ms`；
  覆盖运行手册 §4 全部 11 类；`T6-A03` 数值保持 `NOT_RUN`（机器断言禁止填造）。
- **真实 vs 离线边界**：`ACT-*`/`UNK-*`/`REC-*` 一律要求**真实推理结果**（`REC-07` 要求真实连续时间 ≥30 min），
  `synthetic_substitution_allowed=false`；`OFS-*` 仅离线自检且**不构成** 6-E 验收。
- **校验器**：`verification/s6e_acceptance_check.py`（E1..E11 + 6 类必 FAIL 注入；基线 ALL_PASS、6/6 捕获）。
- **上板窗口申请材料**：`report/evidence/S6-E/s6e_acceptance_20261024_r01/board_window_request.md`（**未申请**，八类门禁逐项状态、11 字段模板、时长预算、停止条件与恢复）。

## 阻碍 / 开放
- `T6-A03` 交互延迟数值 `NOT_RUN`（缺阶段4 实测帧周期 P，不得填造）。
- G3 板测未做；6-D 集成待阶段4/5 接口冻结（`BLOCKED`）；6-E 验收未执行；阶段7 暂不开工作树。
- 独立复评未做：本轮 r13/r08/S6-E 为**未冻结修订内容**，等待项目总控派增量复核。

## 下一步
项目总控派增量复核（只审 F6d → 本轮差异）；阶段4 产出真实推理结果并冻结结果契约后，按 `board_window_request.md` 申请 6-E 板级窗口。

## 证据入口
（C11 口径：凡带扩展名的反引号 token 按**项目根**解析；此处只用全路径，避免被当作本证据目录内文件。）
- S6-A（本轮）：`report/evidence/S6-A/s6a_g0_20261024_r13/`、`report/evidence/S6-A/s6a_g0_20261024_r13/S6A_run_summary.md`、
  `report/evidence/S6-A/s6a_g0_20261024_r13/delivery_manifest.json`、`report/evidence/S6-A/s6a_g0_20261024_r13/claim_verification.json`、
  `report/evidence/S6-A/s6a_g0_20261024_r13/tool_self_tests.json`、`report/evidence/S6-A/s6a_g0_20261024_r13/fresh_selfcheck_pair.json`
- S6-B（本轮）：`report/evidence/S6-B/s6b_core_20261024_r08/`、`report/evidence/S6-B/s6b_core_20261024_r08/s6b_run_summary.md`、
  `report/evidence/S6-B/s6b_core_20261024_r08/delivery_manifest.json`、`report/evidence/S6-B/s6b_core_20261024_r08/claim_verification.json`、
  `report/evidence/S6-B/s6b_core_20261024_r08/tool_self_tests.json`、`report/evidence/S6-B/s6b_core_20261024_r08/s6b_fresh_evidence_pair.json`
- S6-E（本轮）：`report/evidence/S6-E/s6e_acceptance_20261024_r01/`、`report/evidence/S6-E/s6e_acceptance_20261024_r01/S6E_run_summary.md`、
  `report/evidence/S6-E/s6e_acceptance_20261024_r01/board_window_request.md`、`report/evidence/S6-E/s6e_acceptance_20261024_r01/s6e_acceptance_check.json`、
  `report/evidence/S6-E/s6e_acceptance_20261024_r01/delivery_manifest.json`、`report/evidence/S6-E/s6e_acceptance_20261024_r01/preserved_failures/`
- 上一冻结（保留不改写）：`report/evidence/S6-A/s6a_g0_20261023_r12/`、`report/evidence/S6-B/s6b_core_20261023_r07/`
- 本轮自证记录（提交前快照）：`report/evidence/S6-A/s6a_g0_20261024_r13_selfproof/`、`report/evidence/S6-B/s6b_core_20261024_r08_selfproof/`

## 11 字段交接行
任务：阶段6 交互控制（6-E 离线轮：结清遗留清单 + 冻结 6-E 验收用例） | 负责人：阶段6 总控 stage6-lead4 | 工作树/分支：D:\codex-worktrees\w6 / stage6-interact-prep |
起始提交：d8bc70e | 允许修改范围：w6 内 docs/stage6、src/stage6、verification、report/evidence/**、.codex/STATE.md |
未提交改动归属：本轮 r13/r08/S6-E 与工具修改归本轮（提交后冻结） | 让出声明：未让出 | 心跳(UTC+8)：2026-10-24 02:1x |
证据入口：见上 | 恢复命令：`python -B verification/s6e_acceptance_check.py --project-root D:/codex-worktrees/w6 --inject-self-test`；`python -B verification/approved_package_scan.py --project-root D:/codex-worktrees/w6 --run-dir report/evidence/S6-A/s6a_g0_20261024_r13 --inject-self-test` |
状态/下一接手方：DELIVERED_PENDING_REVIEW（未冻结修订内容；待项目总控派增量复核）