# 阶段6 STATE（S6-A/S6-B 交互控制；离线部分）

## 目标
阶段6 交互控制：五类动作判定、多框选择/同分排序、目标保持与重获、抖动/稳定窗口、冷却与再触发、
持续保持只触发一次；产出 G0 行为表 + S6-B/S6-C 实现与确定性证据。硬件（摄像头/板测）不在本轮。

## 当前事实（2026-10-23）
- 契约：`S6A-G0-v1.8`（已批准版）；**24 项参数按草案值获 Wong 批准**（批准记录在 main：
  CTRL-DSH-HANDOFF/decisions/`stage6_approval_receipt_20261023_r01.md`；原文「按你建议」「阶段7暂时不开」）。
  行为表含 `approval_record` + 24 项 `approval_status=APPROVED_20261023` 与 `approval_ref`；**参数值未修改**。
- 逐项决定：`T6-A02` 保持 500ms；`B16 S_DEDUP` 设计上不可达（H-10 全局冷却门覆盖）不计入覆盖；`T6-S01`/`T6-S02` 批准
  （30fps 第 8 帧 233.1ms，按 T6-S03「取较晚」）；`U6-12` 保留 M4 并计入覆盖；`U6-16` STABLE 获取内锁存；
  `U6-15`=`A_SWITCH_UI`+`A_SWITCH_CHANNEL`；`U6-13` 口径固化但**数值 `NOT_RUN`**（待阶段4 实测帧周期 P）；
  `T6-STALE_LIMIT`=200ms，阶段4/5/6 同一常量。
- 证据轮次：S6-A 最新 `report/evidence/S6-A/s6a_g0_20261023_r12/`；S6-B 最新 `report/evidence/S6-B/s6b_core_20261023_r07/`。
  历史轮次 r01..r12 / r01..r07 全部保留，不就地改写。
- 关键机制事实：S6-A 自检 17 项（含 C4 批准纪律、C16 语义可达性扫描、C11 清单/STATE）；S6-B 26 条确定性用例 + 4 项判别力探针；
  `claim_verify` 逐条真实退出码且 verdict 由全部 claim 计算；`export_selfproof` **必须显式 `--s6a-run`**（BLK-D1 后取消隐式查找）。

## 谓词绑定口径（与行为表逐字一致）

> M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段。

## 两段式冻结链
- F4/G4（`6b8e5f2a`/`f5b749ed`，tag r3）→ **F5/G5（`caa9728a`/`61caac0d`，tag r4）**：批准应用轮；
  **r4 已降级为非冻结记录**（F5 未过自定 F6 自证，根因：行为表 `run_id` 未同步 ⇒ 工具复算旧包）。
- **F6/G6（本轮）**：修复 BLK-D1（显式 `--s6a-run` + `run_id`→r12）与 BLK-D2（已批准口径下的 PENDING 文本、
  历史行还原、`params_snapshot` 真值、S6-B 侧 approval 断言）；tag `stage6-freeze-20261023-r5` 打在 G6。
- 旧 tag（r1/r2/r3/r4 与两个 per-profile tag）保留不动。

## 两段式冻结（本轮最终）：F6c / G6
- **F6c = 交付内容**：`0a2abc4956242c118b7d5ef6d4a1fe1b1ff28351`（修复 BLK-D1 + BLK-D2 后重建的两包与工具）。
- **G6 = 自证记录**（本提交）：报告主体为 F6c + 传输克隆自证记录；**tag `stage6-freeze-20261023-r5` 打在 G6**。
- **冻结链**：F4/G4（tag r3）→ F5/G5（tag r4，**已降级为非冻结记录**）→ **F6c/G6（tag r5，当前有效）**。
  中间态：F6（`bf05d450`，缺 `--s6a-run` 参数注册）、F6b（`9b9d572e`）均被 F6c 取代；所有提交与旧 tag 保留不动。
- **r4 处置与定性更正**：F5 未过自定冻结自证（S6-A 剖面 `[1,0,2]`），根因是**交付物缺陷**——
  行为表 `run_id` 未随新 RunId 同步（仍指 `r10`），`export_selfproof` 又按该字段**隐式**定位证据目录 ⇒ 复算旧包。
  上一轮 STATE 的「3 文件 / 普通克隆 55/55 / 非产品缺陷」三处表述作废（55/55 说的是 r11 包，与工具复算的 r10 不是同一对象）。
- **本轮实测（全在传输克隆内）**：`--commit F6c --s6a-run report/evidence/S6-A/s6a_g0_20261023_r12`
  → S6-A `ALL_SELF_PROVEN [0,0,0]` exit 0；加 `--s6b-run report/evidence/S6-B/s6b_core_20261023_r07`
  → S6-B `ALL_SELF_PROVEN [0,0,0,0]` exit 0。
- **BLK-D2 关闭方式**：构建器/字段语义改准（`params_snapshot` 不再写假命题）；规格文档拆分「当时/现口径」，
  8 条历史修订行写回当时状态并标注历史语境；两侧新增机读断言 `approved_package_scan`（已批准包内不得出现 PENDING/待批准 陈述，
  历史语境行除外）各配注入必 FAIL 例，并作为 claim `S6A-C8` / `S6B-C5` 入库。
- 提交 G6 后停写 w6。

## 阻碍 / 开放
- `T6-A03` 交互延迟数值 `NOT_RUN`（缺阶段4 实测帧周期 P，不得填造）。
- G3 板测未做（无摄像头/未上板）；集成（6-D）待阶段4/5 接口冻结；阶段7 暂不开工作树。
- 批次 C 三项开放缺口（已如实登记于两包 `limitations_not_executed.open_gaps_batch_c`，**不得当通过凭据**）：
  ① 陈旧 `fresh_selfcheck_pair.json`；② 套件必 FAIL 例仍跑真实 run-dir；③ 套件 `skipped` 曾 fail-open 且产物未真正入库。

## 下一步
Wong/项目总控派增量复核（只审上一冻结相对差异）；硬件到货后做板测（G3）与集成（6-D）。

## 证据入口
- S6-A：`report/evidence/S6-A/s6a_g0_20261023_r12/`（`S6A_run_summary.md`、`delivery_manifest.json`、`claim_verification.*`）
- S6-B：`report/evidence/S6-B/s6b_core_20261023_r07/`（见 `report/evidence/S6-B/s6b_core_20261023_r07/s6b_run_summary.md` 与 `report/evidence/S6-B/s6b_core_20261023_r07/delivery_manifest.json`）

## 11 字段交接行
任务：阶段6 交互控制（离线部分） | 负责人：阶段6 总控 stage6-lead3 | 工作树/分支：D:\codex-worktrees\w6 / stage6-interact-prep |
起始提交：d8bc70e | 允许修改范围：w6 内 docs/stage6、src/stage6、verification、report/evidence/**、.codex/STATE.md |
未提交改动归属：无（提交后冻结） | 让出声明：未让出 | 心跳(UTC+8)：2026-10-23 09:4x |
证据入口：见上 | 恢复命令：`python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261023_r12/hand_computed_cases.json --upstream report/evidence/S6-A/s6a_g0_20261023_r12/upstream_bindings.json --out tmp/6/state_probe.json --project-root D:/codex-worktrees/w6 --evidence-dir D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261023_r12 --manifest report/evidence/S6-A/s6a_g0_20261023_r12/delivery_manifest.json --state .codex/STATE.md` |
状态/下一接手方：DELIVERED_APPROVED_20261023（待复核）
