# 终审批次 B（S6-B/S6-C r03 实现）独立复评记录（CHANGES_REQUIRED）

- 被审内容：提交 **`e3aeb09` / `05126fd`**（S6-B 侧逐字节一致）；整树另有 11 个文件差异全在 S6-A/STATE/自证侧
- 评审方：DSH 项目总控派出的**终审 Reviewer B**（只读；未在 w6 写入）；隔离目录 `tmp/review/FINAL_B_20261023_r01/`
- 时间（UTC+8）：2026-10-23 04:45–05:10
- **结论：`CHANGES_REQUIRED`（阻断 2；非阻断 12）**
- 边界：只覆盖 S6-B/S6-C r03，不代表 G0/G2/G3/G4/G5。

## 1. 阻断

**`BLK-r03-1`｜`BLK-r02-1` 未真正关闭：`acquisition_id` 在 M8 / M2 / M12 出口不递增**
- 事实：现仅在 **M11/M4/目标切换**递增；而 **M8** 与 **M2/M12** 同样清空 `current_target`、**真的结束一次获取**，却不递增 → 新获取复用旧 id。评审对抗序列实测：M8 路径两次触发 `[0,0]`；`M5→M2→M12→新目标→M5` 得 `[0,0]`；门锁期窗口完成后再触发也沿用旧 id（3 项断言 FAIL）。
- 另有：D7 把 **M8** 误标为"会话/重启复位"（v1.7 的 M8 = `COOLDOWN→IDLE` 目标丢失出口；复位是 `RESET`）。
- 影响：B11"新的 `acquisition_id`"、B15 的逐获取核对不成立（行为上"二次触发只允许来自新获取"仍成立）。
- 关闭：**(a)** 在 M8/M2（必要时 M13）也分配新 id 并补覆盖用例；**或 (b)** 把 D7 与 S6-A `must_log` 明确改为"仅 M11/M4/切换递增"并显式登记"经 M2/M8 出口重获会复用 id"的开放偏差。两者都需重生成证据与哈希。

**`BLK-r03-2`｜交付提交 `e3aeb09` 通不过自己的 F6 自证**
- 事实：清单把 `.codex/STATE.md` 绑为 `450ab45d…`，而**该提交内**是 `8c5cc087…`(LF)/`bb4ffbc3…`(CRLF)——任何换行口径都不匹配（`05126fd` 才匹配）。干净克隆实测：`check_stage_delivery --mode evidence` = **exit 2**（唯一错误 `files[54]`）；`export_selfproof --commit e3aeb09` = **`NOT_SELF_PROVEN [0,0,0,2]`**；而包内清单把该检查标 **PASS/exit 0**（理由引用 04:28:52 的旧 worktree 快照）。交付的 `_selfproof` 总体判定为 **`NOT_ALL_SELF_PROVEN`**（`05126fd → SELF_PROVEN [0,0,0,0]`）。包内还绑定了 04:10 的**陈旧** `export_selfproof.json|md`（标 v1.6/r07、声称 `ALL_SELF_PROVEN`）。
- 关闭：使**交付提交内** STATE.md 与清单绑定一致，并让 evidence/自证在**干净克隆**上 exit 0；清单自证行改为引用**交付提交本身**；替换/删除陈旧自证文件。

## 2. 已关闭（摘）

- **`BLK-r02-2` 真关闭**：`run_report.json` 的 `observed.action_records`（18 条）含 `action_type`/`target_id`/`acquisition_id`/`t_trigger_ns`；四个 `ACTION_*` 经 `event`/`effective_event` 进证据（SUBMITTED 17/EFFECTIVE 16/FAILED 1/UNOBSERVED 2）；core 的 4 个 `OUT_*` + `SUP_DEDUP` + `STATES` 已删。
- `NB-03`/`NB-04`/`NB-06` 关闭；24 项参数与 r02 逐项相同；23/23 可复现；探针 4/4；`claim ALL_CLAIMS_VERIFIED` 与实测一致；无"声明存在但缺失"文件；无自夸；范围均限定"注入输入 + 虚拟单调时钟"。
- **对抗语义 46 断言：43 PASS / 3 FAIL**（3 项 FAIL 全指向 `BLK-r03-1`）。零框、跨目标全局冷却门（第二次提交仅在门开后 Δ=1100ms）、门在 `TIMEOUT` 帧开启不触发（顺延）、`K01`±1ns、`L02`±1ns、30fps 第 8 帧 233.1ms、M2/M13/M12、同帧 M4/M10 取 M10、STABLE 锁存、动作幂等与 `T6-A02` 去重（=A02 不去重、-1ns 去重、A02<K01 不可达）均与独立推导一致。

## 3. 非阻断 12 项（要点）

`NB-r03-01` 版本口径未统一（代码钉 v1.7，docstring/`s6b_frozen_interface_v1.json`（已改字节但仍写 v1.6）/`case_matrix`(v1.6,v1.4)/`build_case_matrix`/`reachability_notes`/摘要标题/包内自证仍 v1.6）。
`NB-r03-02` 探针 note 仍"21 例"。
**`NB-r03-03`** `NB-07` **仅部分修**：`s6b_probe.run_driver` 仍不设 UTF-8 → 直接跑探针写出 **26 个 U+FFFD** 且与清单不符；设 `PYTHONUTF8=1` 后逐字节一致。
`NB-r03-04` 清单仍写"三项退出码"且 `source_commit=87a6bdc` 不含所绑源码（9/10 source 只匹配 `e3aeb09`/`05126fd`）。
`NB-r03-05` `NB-08` 残留（`s6_core` request 字典 `acquisition_id` 重复键×2、`s6_params:181` 自赋值、`state_declared_s6b_dir_files_in_commit` 名不符实）。
`NB-r03-06` C8 的 RESET 帧 step 日志与 18 条 `action_ack` 日志缺 `acquisition_id`。
`NB-r03-07` B18/B22/B23/B25 的 `must_log` 事件名在证据中 0 次、B13"剩余冷却时间"未记。
`NB-r03-08` `x or t_now_ns` 判空在 `t=0` 时把 dwell 锚点改为 M1 帧时刻。
`NB-r03-09` 包内陈旧 v1.6 自证被清单绑定。
**`NB-r03-10`（S6-A 侧）**：行为表 v1.7 的 `transitions[M4].reachability` 仍为 `UNREACHABLE…`，与 `reachability.transitions.M4 = REACHABLE` **冲突** ⇒ S6-B 称"已同步修正"对该字段不成立（**第 9 处 M4 残留**）。
`NB-r03-11` `claim_verify` 的 `exit_code` 自算非实测（与终审 A 的 `BLK-r08-2` 同源）。
`NB-r03-12` 轮次边界被打破（审查期间 HEAD 前移到 `1839766`，就地改写 r03 证据包）。

## 4. post-baseline 提示（供排程）

- `1839766` 的 `s6_core.py` 与 `e3aeb09` **逐字节相同 ⇒ `BLK-r03-1` 未修**。
- `1839766` 的 r03 `delivery_manifest` 对 STATE.md 已按自身 LF 绑定，换行对齐后 evidence 检查 **exit 0**（`BLK-r03-2` 的绑定面已修）。
- **但** `1839766` 的 r03 两份清单对**同一个** `docs/stage6/s6a_stage6_g0_behavior_v1.json` 声明了**互为另一换行形态**的哈希（delivery=LF `bc90945c` / inputs=CRLF `58e4892e`），**无任何工作区状态可同时满足** → `--mode inputs` = **exit 2**，而 checks 仍标 PASS/0。
- 建议：把 `1839766` + 工作区未提交的口径修复作为**新轮次 r04** 冻结后独立复审，**不要就地覆盖 r03 RunId**。

## 5. 处置

- 已派 `task-13`（S6-B r04 + 合并修正）：`BLK-r03-1` 按 **(a)** 修（每次获取结束都分配新 id）、`BLK-r03-2`、`NB-r03-01..12`（含 **`NB-r03-10` 的 M4 第 9 处**、探针 UTF-8、`claim_verify` 真退出码）。
- 与 `task-12`（S6-A r09 + 工具）合为**同一个修复轮**；之后按两段式冻结（F 内容 / G 自证记录 + tag）+ 传输克隆自证 + 增量复核。