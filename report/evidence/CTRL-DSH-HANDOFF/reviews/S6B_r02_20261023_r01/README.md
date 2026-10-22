# S6-B/S6-C r02 独立复评记录（CHANGES_REQUIRED）

- 被审版本：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，提交 **`87a6bdc`**（链路 r01=`43f7995` → S6-A r07=`bdcf896` → 本提交）
- 评审方：DSH 项目总控派出的**独立 Reviewer（S6-B r02 轮）**；隔离目录 `tmp/review/S6B_r02_20261023_r01/`；审查前后 w6 `git status --porcelain` 为空、HEAD 恒为 `87a6bdc`
- 时间（UTC+8）：2026-10-23 03:40–03:57
- **结论：`CHANGES_REQUIRED`（阻断 2；非阻断 10）**
- 边界：只覆盖 S6-B/S6-C r02，不代表 G0/G2/G3/G4/G5。

## 1. 阻断（均为"声明已关闭、实测未关闭"）

**`BLK-r02-1`｜`N-05` 未关闭：D7 的 `acquisition_id` 规则与实现相反**
- 位置：`src/stage6/s6_core.py:85-87`（D7）、`:599-613`（`_transition`）、`:447-452`（仅目标切换递增）。
- 事实：D7 称"M11/M4/M8 与目标切换都会递增"，实测**只有目标切换递增**；自跑 C3（M11 路径）两次获取两次触发 → `acquisition_id = 0, 0`；`C5-target-jump` → 1；"M4 结束获取后再获取" → 仍 0。证据中该字段 **0 次命中**。
- 影响：B11/B15 的 `must_log` 不成立，"一次获取一次触发"无法溯源；集成方按 D7 会误判。r01 给的两条关闭路径（递增 / 显式声明+落盘）都没走通，还新增了与实现相反的规范说明。
- 关闭条件：(a) 在 M11/M4/M8 递增（**或**与 S6-A/G0 改口径为"仅目标切换递增"并同步 `must_log`）；(b) `acquisition_id` 真正进证据（见 BLK-r02-2）；(c) 重生成证据与清单。

**`BLK-r02-2`｜`N-04` 未关闭：声明的 `action_records` 未进交付证据**
- 位置：`verification/s6b_run_cases.py:132-150`（`run_case` 产出 `action_records`）与 `:269-287`（`observed` 未含它）。
- 事实：DSH 复核确认 `action_type` 2 次、`target_id` 3 次（均在文本中）、**`acquisition_id`/`t_trigger_ns` 各 0 次**；`run_report.json` 与 23 个 JSONL 中四个 `ACTION_*` 事件名 0 次。record 在内存里确有字段，**序列化时被丢弃**。
- 影响：B01/B11/B15/B28 的 `must_log` 无法从交付证据核对；r02 的关闭声明与提交信息均属失实。
- 关闭条件：`observed` 增列 `action_records`（或 ack 日志补 4 字段），重生成证据+清单+哈希；顺带清理 8 个从未使用的 `OUT_*` 常量。

## 2. 非阻断 10 项（要点）

`NB-01` `N-01` 未关闭：`s6b_frozen_interface_v1.json`（哈希与 r01 **完全相同**＝未动）、随证据提交的 `case_matrix.json`/`build_case_matrix.py`、`s6_core.py:511` docstring 仍写 v1.4。
`NB-02` `s6b_probe.py:77`、`probe_summary.json:10` 仍写"21 例"（实际 23）。
`NB-03` D8 前提失实：实测 IDLE 在"1 帧选中 + 4×E_TICK"下仍保留 `current_target` 到 800ms 不判 M10。
`NB-04` D9 称在 `limitations_not_executed.json` 登记 `transition_candidates`/`S_CONFLICT_RESOLVED`，该文件**无此条目**。
`NB-05` manifest `limitations[0]` 指向包内 **worktree 快照**自证而非交付提交导出自证。
`NB-06` `s6b_run_summary.md:16` 第三列仍是占位"实测（下方回填）"。
`NB-07` 可复现性：不设 `PYTHONUTF8=1` 时 probe stdout 解码按宿主 cp936 → `U+FFFD` 乱码（设后 5 产物逐字节一致）。
`NB-08` 零散：request 字典重复键、自赋值、`state_declared_s6b_dir_files_in_commit` 名不符实、类名空格差、`C9c` 归类拉伸。
**`NB-09`（S6-A 侧，DSH 已复核）**：S6-A 行为表仍有旧断言——`reachability_note`、`reachability.consequence`（"M4…**不得计入覆盖声明**"，1 处）、`parameter_notes.T6-S04`（"**M4 不可达**" 2 处）、spec 第 376 行仍写"**不可达（U6-12）**"（MD 1 处 + JSON 1 处）⇒ r07 的 M4 修正**不完整**，而 S6-B 称"已同步"。
`NB-10` F6 的 S6-B 模式**故意跳过** S6-A r07 的 inputs/evidence 复算（已登记为降级口径，建议显式写进报告）。

## 3. 已核验关闭 / 成立

- **`BLK-1` 关闭（评审独立复现）**：四处口径一致（M4 可达并计入覆盖；不可达只剩 `B16 S_DEDUP`(A02<K01) 与 M7）；自构造"5 帧高分 + 2 帧 score=0.28" → `f2 M1`、**`f7 M4`**，与 `C4-jitter-reset` 日志一致；给"维持优先"加 P01 门的稳健性反例下仍 `M4@f7`。
- `N-03`/`N-06`/`N-07`/`N-09` 关闭（注入未映射类→构建 exit 1；删 `T6-03`/`T6-A03`/`T6-S02`→均 **exit 2**；旧 `NO_HAND`+detections 行为→仅 `C6b` FAIL；改用例→**exit 2** 且发生在跑状态机之前）。
- 复跑：驱动 exit 0、23/23、140ms，`run_report.json`+23 JSONL 与提交版 **24/24 逐字节相同**；probe 0（0/2/1/1）；两检查器 exit 0；`T6-S01=900ms` → exit 1、133 断言失败。
- `F6` 新 `--s6b-run`：确用目标提交内文件跑 4 项；复跑 `87a6bdc → SELF_PROVEN [0,0,0,0]`、`43f7995 → NOT_SELF_PROVEN [0,2,2,2]`（负对照有效）；反例证明工具**只做换行口径对齐**（1 字节非换行差异 → 登记 `unresolved`，字节不变）。
- 证据：53 条绑定 + 42 条哈希全部复算一致；24 项参数未变；`expected` 仍由 `build_case_matrix.py` 独立推导；无"已审查/已通过"式自夸。

## 4. 处置

- 已派 `task-10`：修两阻断 + `NB-01..NB-08`/`NB-10`，并把 **`NB-09` 的 4 处 S6-A 残留**作为小修订（r08，等第 7 轮复评结论落地后再提交，避免同轮两份结论交叉）。
- **新增硬规则**：任何"已关闭/已落盘/已同步"的声明，必须在同一证据包里附**验证命令 + 真实退出码 + 可观察输出**（`claim_verification` 附录），否则不得宣称关闭。
- 本记录只搬结论与边界；S6-B 实现与证据仍在 w6。