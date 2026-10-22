# S6-B / S6-C r03 独立终审报告（批次 B）

- 角色：独立 Reviewer（S6-B/S6-C r03，只读）
- 工作树：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**审查开始时 HEAD `f3c537d`**（审查期间第三方提交使 HEAD 前进到 `1839766`，见 §0.1 与 §10）
- 被审内容：提交 **`e3aeb09`**（标签 S6-B r03）与 **`05126fd`**（amend 前），按**提交内容**判定（非工作区当前字节）
- 隔离目录：`D:\FPGA_Competition\tmp\review\FINAL_B_20261023_r01\`（`clone_e3a`/`clone_051`/`clone_e3b` = `git clone --shared` 隔离克隆；`clone_*` 内跑工具；自证的 TEMP/TMP 重定向到 `selftmp/`）
- 环境：Python 3.12.10（`locale.getpreferredencoding()=cp936`）、git 2.56.0.windows.2、UTC+8
- 结论：**CHANGES_REQUIRED**（2 项阻断 + 12 项非阻断）
  - `BLK-r02-2`（action_records/事件/死常量）**已真正关闭**（我逐条实测复现）
  - `BLK-r02-1`（acquisition_id）**仅部分关闭**：C3 `[0,1]`、M11/M4/目标切换递增、字段进证据均已实测成立；但 **D7 声明的规则在 M2/M12/M8 等"结束获取"路径上未实现**，同一 `acquisition_id` 会覆盖两次真实获取 → 列 `BLK-r03-1`
  - **交付提交 `e3aeb09` 通不过自己的 F6 自证**（`check_stage_delivery --mode evidence` = exit 2；`export_selfproof --commit e3aeb09` = NOT_SELF_PROVEN `[0,0,0,2]`），而包内清单却声明该项 PASS/exit 0，交付的 `_selfproof` 报告总体判定为 `NOT_ALL_SELF_PROVEN` → 列 `BLK-r03-2`
- 本结论**仅覆盖 S6-B/S6-C r03**（实现 + 用例矩阵 + 证据包 + 自证），**不代表 G0/G2/G3/G4/G5**，不含实物/板卡/摄像头/HDMI/≥30 分钟回放，也不评价 S6-A 规格本身（另见终审 A）

---

## 0. 审查环境事实（先说清，影响读者如何核对）

1. **工作区/HEAD 在审查期间被第三方持续改写（重要）**：审查开始（04:37）时 `git status --porcelain` 为空；`04:41–04:45` 出现 14 个 `M`（mtime 04:41:37–04:45:03，`python` PID 29244 于 04:44:49 启动）；**04:45:59 新增提交 `1839766`（"chore(stage6): freeze S6-A v1.7/r08 + S6-B r03"），HEAD 由 `f3c537d` 前进到 `1839766`**，该提交**就地改写了 r03 证据包**（`delivery_manifest.json`/`inputs_manifest.json`/`hashes_sha256.txt`/`claim_verification.*`/`S6A_run_summary.md`/自身自证报告等）。至 05:08 工作区仍有 **42 条 `M`/`??`**，并新增 `verification/hash_convention_check.py` 与 `report/evidence/{S6-A/…_r08,S6-B/…_r03}/hash_convention_counterexamples.json`（显然在处置换行/哈希口径问题）。
   → **本报告一律以审查基线提交内容为准**（`git clone --shared` + `checkout <rev>`，或 `git show <rev>:<path>`）：被审内容 = `e3aeb09` / `05126fd`（S6-B 侧逐字节一致），**不得用工作区当前字节或 `1839766` 的 r03 包复核本轮结论**。`1839766` 属**新一轮**（见 §10），须单独复审。
2. `e3aeb09` 与 `05126fd` **并非整树一致**：全树 diff 有 11 个文件不同（`.codex/STATE.md`、S6-A r08 证据 7 个、S6-A r08_selfproof 2 个、`S6A_run_summary.md`）。**S6-B 侧内容（`src/stage6/*`、4 个工具、r03 证据）逐字节一致**，故"按内容判定"成立，但"声称一致"只对 S6-B 侧为真。
3. 提交内 r03 清单的**换行口径**：`.py` 以 LF 形态绑定、`.json/.md/.txt/.jsonl` 以 CRLF 形态绑定（清单哈希即构建时工作区字节）。因此干净克隆必须做换行口径对齐（与 `export_selfproof.align_by_manifest_hashes` 同口径）后，`check_stage_delivery` 才可能全绿。

## 1. 命令与真实退出码（全部实测，隔离克隆内）

| # | 命令（`<iso>` = 隔离克隆根） | 退出码 | 备注 |
|---|---|---|---|
| 1 | `<py> -B <iso>/verification/s6b_run_cases.py --project-root <iso> --run-dir report/evidence/S6-B/s6b_core_20261023_r03` | **0** | 23/23 PASS、0 断言失败、**0.125 s**；`run_report.json` + **23/23 JSONL 与清单声明哈希逐字节一致**（45/45 清单条目 OK，运行后与声明口径副本 diff 为空） |
| 2 | `<py> -B <iso>/verification/s6b_probe.py --project-root <iso> --run-dir …`（**不设 PYTHONUTF8**） | **0** | 4 探针 `0 / 2 / 1 / 1` 全 AS_EXPECTED（0.656 s）；但写出的 `probe_expected_tampered_stdout.txt`、`probe_summary.json` 含 **26 个 U+FFFD**，与清单声明不一致 |
| 3 | 同上，`env PYTHONUTF8=1 PYTHONIOENCODING=utf-8` | **0** | 4 探针同上；**与清单声明逐字节一致**（见 §5 NB-r03-03） |
| 4 | `<py> -B <iso>/verification/check_stage_delivery.py --mode inputs …` | **0** | `CHECKS_OK`；stdout 与提交版 `check_inputs_mode_output.txt` 逐字节一致 |
| 5 | `<py> -B <iso>/verification/check_stage_delivery.py --mode evidence …`（**e3aeb09 干净克隆**） | **2** | `CHECKS_FAILED`，**唯一错误 `files[54] .codex/STATE.md` SHA-256 不匹配**（清单 `450ab45d…`，实际 CRLF `bb4ffbc3…` / LF `8c5cc087…`）→ `BLK-r03-2` |
| 6 | 同上（**05126fd 干净克隆**） | **0** | `CHECKS_OK`（该提交的 `STATE.md` 恰为 `450ab45d…`） |
| 7 | `<py> -B <iso>/verification/claim_verify.py --package s6b --run-dir … --project-root <iso>` | **0** | `ALL_CLAIMS_VERIFIED`；4 条 claim 与我实测一致（差异仅 `command` 内的绝对路径） |
| 8 | `<py> -B <iso>/verification/export_selfproof.py --commit e3aeb09 --commit 05126fd --s6b-run … --worktree-snapshot` | **1** | **43.5 s**；`e3aeb09 → NOT_SELF_PROVEN [0,0,0,2]`；`05126fd → SELF_PROVEN [0,0,0,0]`；`worktree_snapshot → NOT_SELF_PROVEN [0,0,0,2]`；总体 `NOT_ALL_SELF_PROVEN` |
| 9 | 对抗语义序列（自写 `adv_semantics.py`，直接驱动核心/动作层） | **0** | 46 项断言：**43 PASS / 3 FAIL**，3 项 FAIL 全部指向同一缺陷（`BLK-r03-1`），见 §4 |
| 10 | 清单/绑定复算（`chk_committed.py`/`chk_blobs2.py`/`chk_sources.py`） | **0** | 55 条声明**全部存在**、盘上**无未声明文件**；`hashes_sha256.txt` 44 行复算在清单口径下一致 |

## 2. `BLK-r02-1`（acquisition_id）——**部分关闭**，残留列 `BLK-r03-1`

已实测成立的部分：

- `_transition` 对 **M11 与 M4** 真递增（`s6_core.py:601-605`），M1 不递增；`_finish`（`:646`）把 `acquisition_id` 写入**每一帧 step 日志**；`_on_advancing_with_dets`（`:444`）在**目标切换**时递增。
- 交付证据：`C3-lost-then-reappear` 两次获取 → `action_records` 的 `acquisition_id = [0, 1]`（原 `[0,0]`，**我复现成立**）；`C5-target-jump → [1]`；`run_report.json` 命中 18 次、23 个 JSONL 命中 222 次。
- 我构造的 M11 路径（`M10→M11` 后再获取）→ `[0,1]`；M4 路径（CANDIDATE 内抖动耗尽 + 停留 ≥ `T6-S04` 且 M10 未命中）→ M4 帧 `acquisition_id` 由 0 变 1、`current_target` 清空；会话切换 → `RESET` 且归零。
- **B11/B15 的 `must_log` 现在可以从交付证据核对**（LOST→IDLE 重获路径）：字段在 `observed.action_records` 与逐帧日志中均可直接检索。

未关闭的部分（见 `BLK-r03-1`）：D7 的**规则本身**仍与实现相反/不完整。

## 3. `BLK-r02-2`（action_records / 事件 / 死常量）——**已关闭**

- `run_report.json` 的每条用例 `observed.action_records` 含 `action_type` / `target_id` / `acquisition_id` / `t_trigger_ns`（另含 `event` / `effective_event` / `action_id` / `submit_result` / `effective_result` / `suppression`）；共 18 条。
- 四个 `ACTION_*` 经 `event`/`effective_event` 进证据：**SUBMITTED 17 / EFFECTIVE 16 / FAILED 1 / UNOBSERVED 2**（均 ≥1）；`ACTION_SUBMITTED` 等名字在证据文本中分别命中 35/47/2/4 次。
- 死常量：`s6_core.py` 的 4 个 `OUT_*`、`SUP_DEDUP`、`STATES` **均已删除**；`s6_actions.py` 同名常量**均被引用**（claim C3 与我的正则独立复核一致，未使用常量 = 0）。
- B01/B02/B28 的 `must_log`（`action_id`/`trigger_frame_id`/`t_submit`/`submit_result`/`effective_result`/`t_effective`/`ACTION_FAILED`/`ACTION_UNOBSERVED`/尝试计数）可由 `action_records` + `action_summary` 核对。

## 4. 语义对抗（重点）：自构造序列 + 独立推导期望

全部由我按行为表 v1.7 独立推导期望后实测（`adv_semantics.py`，失败 3 项见 §6）：

| 项 | 序列要点 | 期望（独立推导） | 实测 |
|---|---|---|---|
| A 零框 NO_HAND | 8 帧 `state=NO_HAND`、`detections=[]` | `IDLE`、无迁移、`no_hand_frames=8`、0 提交、`window_match_count=0` | 一致 ✔ |
| B 跨目标全局冷却门 | 目标 A 6 帧稳定→M5@600 ms；切到目标 B 再稳定 | 门开前**不得提交**；第二次提交 ≥ 首次 + `T6-K01`；`acquisition_id=1` | 2 次提交、Δt=1100 ms、id=1、迁移 `M1,M3,M5,M9,M5` ✔（注：该路径由 COOLDOWN/M9 承载，**不产生 `S_COOLDOWN`**，与 H-10 一致） |
| C 门开启帧恰为 TIMEOUT | 1600 ms 处放 `E_FRAME_TIMEOUT` | 该帧**不得触发**，触发顺延到下一推进帧 | 提交 `[600 ms, 1610 ms]` ✔ |
| D `T6-K01` ±1 ns | 门锁期间在 CANDIDATE 内完成窗口→STABLE；推进帧落在 `600 ms+999 999 999` 与 `+1 000 000 000` | `K01-1ns` 不触发（记 `S_COOLDOWN`）、`=K01` 触发 | 提交 `[600 ms, 1600 ms]`、`S_COOLDOWN` 4 次 ✔ |
| E `T6-L02` ±1 ns | 距上次 `TARGET_CONTINUES` 成立 `L02-1ns` / `L02` | 前者不判 M10、后者判 M10 | 一致 ✔ |
| F 30 fps 取较晚 | 33.3 ms×9 帧 | M3 在第 **8** 帧、`window_complete_ns=233 100 000`；第 6 帧（166.5 ms）不完成 | 一致 ✔ |
| G 异常滑动窗口 | 3 异常→M2；恢复期再异常→M13；5 合法→M12 | `M2, M13, M12`；末态 IDLE | 一致 ✔ |
| H 同帧 M4/M10 | 3 维持帧 + 3 零框帧，使末帧同时满足 M10 与 M4 | **M10**（P2 先于 P3）；该帧独立观测到 `jitter_exhausted=True` 且 dwell=500 ms ≥ `T6-S04` | `M10` ✔ |
| I STABLE 锁存 | 门锁期间进入 STABLE；随后 score 跌破 `T6-P02`、抖动耗尽、`K01-1ns` 推进帧、`K01` 推进帧 | 锁存期间**只**能由 M2/M10/M5 离开；跌破/耗尽不降级；门开前 1 ns 不触发、门开帧直接 M5（无需重建窗口）；异常→M2 | 全部一致（I2 `('STABLE',None,True)`、I4 不触发、I5 `M5`、I7 `M2`）✔ |
| J 动作层幂等/去重 | 同键在 `A02` / `A02-1ns` 提交；不同 `action_type` | `=A02` 不去重、`=A02-1ns` 判 `S_DEDUP`；幂等提交 `visible_state_change=False`；不同键不去重 | 一致 ✔ |
| J7 `T6-A02` 不可达声明 | `A02 < K01` | 条件成立 → S_DEDUP 在核心路径不可达 | `a02_ns(0.5 s) < k01_ns(1.0 s)` 成立；证据中 `S_DEDUP` 命中 **0** 次，与声明一致 ✔ |
| K acquisition_id | M11 / M4 / 目标切换 / 会话切换 / **M8** | M11、M4、切换各 +1；会话切换归零；**M8 与 M2/M12 亦"结束获取"** | M11 `[0,1]`✔、M4 `+1`✔、切换 `+1`✔、RESET 归零✔；**M8 后新获取仍为 0**、**M2/M12 后新获取仍为原 id** ✘（`BLK-r03-1`） |

## 5. 其余必查项

- **23 例计数**：`case_count=23`、18 个 `matrix_class` 行、11 个 CDX 类别非空；摘要与报告一致。
- **D8（NB-03）**：已按实测改写（IDLE **会**保留 `current_target`、「1 帧选中 + 4×E_TICK」到 800 ms 仍未判 M10），并在 `limitations_not_executed.json.open_behavior_deviations` 登记 → **关闭**。我独立复现了「1 帧选中 + 4×E_TICK 仍不判 M10」的现象。
- **未实现项登记（NB-04）**：`not_implemented` 已含 `transition_candidates` / `S_CONFLICT_RESOLVED` → **关闭**。
- **NB-06**：`s6b_run_summary.md` 两个检查器退出码已回填为"实测 0/0" → 关闭（但该 0/0 对 `e3aeb09` 不成立，见 `BLK-r03-2`）。
- **24 项参数**：与 r02 **逐项完全相同**（值/单位/比较/状态 24/24），`all_parameters_pending_approval=true`、`T6-A03` 仍为 `null`（缺草案值按 NOT_RUN 处理）。
- **结论限定**：`run_report.scope_statement`、`limitations.replay_scope`、`probe_summary.scope_statement`、清单 `limitations`、摘要"结论边界"均限定"注入输入 + 虚拟单调时钟"并显式排除摄像头/HDMI/板上/长时间回放 ✔。
- **禁止声明扫描**：未发现"已审查/已通过/验收通过"式自夸；命中项全部是**反向**声明（"不代表…"）✔。
- **声明存在但缺失的文件**：无（55 条绑定在 `e3aeb09` 内全部存在；盘上无未声明文件）✔。
- **claim_verification 逐条复跑**：`ALL_CLAIMS_VERIFIED` 与我的独立实测**一致**（C1 命中数 18/222、C3 `[0,1]`；C2 四字段齐全 + 四事件各 ≥1；C3 未使用常量 0；C4 两类登记非空且 M4 计入覆盖）。
- **自证复跑**：见 §1 #8 与 `BLK-r03-2`/NB-r03-09。

## 6. 阻断项（CHANGES_REQUIRED）

### BLK-r03-1｜`acquisition_id` 仍未覆盖全部"结束一次获取"的路径，D7 的规则与实现不一致（`BLK-r02-1` 未真正关闭）

- **位置**：`src/stage6/s6_core.py:79-81`（`decision_notes.D7`）、`:594-612`（`_transition`，仅 `M11/M4` 递增）、`:442-449`（仅目标切换递增）、`:622-631`（`M2` 清空目标但不递增）；证据：`report/evidence/S6-B/s6b_core_20261023_r03/run_report.json` + `logs/*.jsonl`（仅覆盖 M11 路径的 C3）。
- **问题**：D7 的规范性规则是"`acquisition_id` 在**结束一次获取**时递增——M11、M4 与目标切换各 +1；M8（会话/重启复位）由 `_init_state` 归零"。但
  1. **M8 不是"会话/重启复位"**：行为表 v1.7 `transitions.M8` = `COOLDOWN → IDLE`「冷却结束且当前目标 TARGET_CONTINUES 不成立/已丢失」；会话/重启复位由 `step()` 的 `RESET`（`_init_state`）承载。代码注释（`:602-603`）与 D7 都把它误标为复位。
  2. **M8 与 M2（异常）/M12 都清空 `current_target`、真的结束一次获取，却不递增**，于是新获取因为 `previous is None` 而**复用旧 id**：我构造的 M8 路径得到两次触发 `[0, 0]`；异常路径（`M5 → M2 → M12 → 新目标 → M5`）得到 `[0, 0]`；门锁期窗口完成后再触发的场景同样得 `0`（3 项对抗断言 FAIL，`adv_semantics_result.json`）。
- **影响**：`acquisition_id` **不是可靠的"获取"标识**——两次真实、独立的获取可能同号；D7 所称"动作记录与日志都带该 id，**可由交付证据逐获取核对**"及 B11 的"新的 `acquisition_id`"、B15 的"`acquisition_id`"在这些路径上不成立（行为上"二次触发只允许来自新获取"仍成立，但溯源/区分不成立）。交付用例矩阵未覆盖"异常/冷却出口后再获取并触发"，故 23/23 PASS 掩盖了该路径。
- **依据**：§4 K 行三项实测 + `s6_core.py` 代码 + 行为表 `trigger_once_while_held.acquisition_definition`（"到该目标丢失确认（M10→M11）或切换到另一目标为止"未覆盖 M2/M8 出口）。
- **关闭条件（任一）**：(a) 在 `_transition` 的 `M8`/`M2`（必要时 `M13`）分支同样分配新的 `acquisition_id`（即"凡 `current_target` 被清空且获取可能重开"就 +1），并补一条覆盖"异常出口/冷却出口后再获取并触发"的用例；(b) 或把 D7 与 S6-A 侧 `must_log` 明确改为"仅 M11/M4/目标切换递增"，**并显式登记"经 M2/M8 出口重获时 id 会复用、不可用于区分获取"这一开放偏差**（与 NB-03 同法登记）。两种路径都需重生成证据与哈希/清单。

### BLK-r03-2｜交付提交 `e3aeb09` 通不过自己的 F6 自证；包内"自证 PASS"与交付的 `_selfproof` 报告相互矛盾

- **位置**：`report/evidence/S6-B/s6b_core_20261023_r03/delivery_manifest.json`（`files[54] = .codex/STATE.md` 绑定 `450ab45d…`；`checks[0]` 声明"冻结自证 … status=PASS, exit_code=0, reason=…[0,0,0,0]"）、同目录 `export_selfproof.json|md`（04:10 旧快照）、`report/evidence/S6-B/s6b_core_20261023_r03_selfproof/export_selfproof.json|md`（`NOT_ALL_SELF_PROVEN`）、`verification/s6b_build_evidence.py:305-321`。
- **问题**（三条实测事实）：
  1. `e3aeb09` 的 r03 清单把 `.codex/STATE.md` 绑定为 `450ab45d…`，而该提交内 `STATE.md` 为 `8c5cc087…`(LF)/`bb4ffbc3…`(CRLF)——**任何换行口径都不匹配**（`05126fd` 才匹配）。原因是 `STATE.md` 在 amend 时被改而清单未重建。→ 干净克隆上 `check_stage_delivery --mode evidence` = **exit 2**（仅此 1 条错误），`export_selfproof --commit e3aeb09` = **NOT_SELF_PROVEN `[0,0,0,2]`**。
  2. 包内清单却声明该检查 **PASS/exit 0**，理由引用的是一次 **04:28:52 的 worktree 快照**（当时的 sibling 报告为 `ALL_SELF_PROVEN`）；而**最终交付**的 sibling 报告（`f3c537d`）总体判定为 **`NOT_ALL_SELF_PROVEN`**，其 `worktree_snapshot` 主体正是 `[0,0,0,2]`。同一提交树内"清单说 PASS / 报告说 NOT_ALL_SELF_PROVEN"互相矛盾。
  3. 包内还绑定了 `s6b_core_20261023_r03/export_selfproof.json|md`——一份 **04:10 的旧快照**：契约记为 `S6A-G0-v1.6`、RunId `s6a_g0_20261022_r07`、清单尚无自证检查行，却声称 `ALL_SELF_PROVEN`。它不是交付提交的自证（见 NB-r03-09）。
- **影响**：F6 规则（"任何冻结/交付提交必须自证：自检 + inputs + evidence 三项 exit 0"）对**交付提交 `e3aeb09` 不成立**；读者按清单会得到"已自证通过"的错误结论。`05126fd` 的 `[0,0,0,0]` 只能证明"内容等价的另一提交"自证通过，**不能替代**交付提交的自证。提交信息"(ALL_SELF_PROVEN 0,0,0,0)"与交付报告的总体判定也不一致。
- **依据**：§1 #5/#6/#8；`chk_committed.py`（`files[54]` want/actual）、`chk_blobs2.py`（`STATE.md` @`05126fd` = `450ab45d…` MATCH(raw)、@`e3aeb09` = `8c5cc087…` 无匹配）、`chk_sources.py`（10 个 source 中 9 个匹配 `e3aeb09`/`05126fd`，`STATE.md` 仅匹配 `05126fd`）。
- **关闭条件**：(a) 让 `STATE.md` 在交付提交内的字节与清单绑定一致（先冻结 `STATE.md` 再构建清单，或构建后不再改 `STATE.md`），并使 `check_stage_delivery --mode evidence` 与 `export_selfproof --commit <交付提交>` 在干净克隆上 **exit 0**；(b) 把清单 `checks` 的自证行改为**引用交付提交本身**的真实退出码，删除/替换包内 04:10 的 v1.6 陈旧自证文件；(c) sibling 报告改用 `--commit <交付提交>` 作主体并使其总体判定与清单一致（若确有降级，按 NB-10 方式显式登记"降级口径"，但不得把 `[0,0,0,2]` 记为 PASS）。

## 7. 非阻断项

| 编号 | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| NB-r03-01 | `s6_core.py:1,12`、`s6_params.py:1`、`docs/stage6/s6b_frozen_interface_v1.json:8,50`、`…/cases/{case_matrix.json:6,build_case_matrix.py:436}`、`…/reachability_notes.json:5`、`…/s6b_run_summary.md:1`、`…/export_selfproof.md:8` | **版本口径未统一**：代码钉 `S6A-G0-v1.7`，但上述位置仍写 `S6A-G0-v1.6`（`case_matrix`/`build_case_matrix` 还留有 `v1.4`；摘要写"S6-A r07"）；`s6b_frozen_interface_v1.json` 已改字节（`9e7b39ed…`→`e5228923…`）但仍标 v1.6/S6-A r07/r04 | 阅读者会把 v1.7 语义误认 v1.6；包内版本不自洽（`run_report` 说 v1.7、`case_matrix` 说 v1.6） | `static_chk.py` 版本扫描 | 统一到实际契约令牌，或登记版本映射 |
| NB-r03-02 | `verification/s6b_probe.py:77`、`…/probe_summary.json` baseline note | 仍写"未改动：**21 例**全部通过"，实际 23 | 自述与实测数目不符（r01 N-02 同点） | `case_count: 23` | 改为动态派生（引用驱动 stdout） |
| NB-r03-03 | `verification/s6b_probe.py:27-36`（`run_driver` 未传 env） | NB-07 只修了 `s6b_build_evidence.run_command`；**直接跑探针**（工具自身文档命令）时子进程中文输出按 cp936 解码 → `probe_expected_tampered_stdout.txt`/`probe_summary.json` 出现 **26 个 U+FFFD** 且与清单不一致；设 `PYTHONUTF8=1` 后 5 个产物逐字节一致 | 按文档命令复跑不能复现入库产物；探针产物含替换字符 | §1 #2/#3 实测 | 在 `run_driver` 也传 `PYTHONUTF8=1`/`PYTHONIOENCODING` |
| NB-r03-04 | `…/delivery_manifest.json.limitations[0]` + 顶层 `source_commit` | 仍写"**三项**退出码"（NB-05 未改）；且 `source_commit=87a6bdc…`，而清单绑定的 10 个 source 中 **9 个不匹配 `87a6bdc`**（匹配 `e3aeb09`/`05126fd`） | `source_commit` 会把人引到**不含**所绑源码的提交；"三项/四项"措辞仍错 | `chk_sources.py` | 写明实际交付提交，或把 `source_commit` 改为可解析到所绑字节的提交；措辞改为四项 |
| NB-r03-05 | `s6_core.py:657,661`（request 字典 `acquisition_id` **重复键 ×2**）、`s6_params.py:181`（`self.class_action_map = self.class_action_map` 自赋值）、`export_selfproof.py:254`（`state_declared_s6b_dir_files_in_commit` 实为"实际文件数"，未解析 STATE） | NB-08 只修了 `s6_actions.py` 的重复键 | 可读性/命名准确性；重复键虽无害但易误改 | `legacy_chk.py` | 清理或改名 |
| NB-r03-06 | `s6_core.py:646`（`_finish`）与 `:306-313`（会话切换早退）、`:668-683`（`note_action_ack`） | 字段覆盖不完整：`C8` 的 `RESET` 帧 step 日志**缺 `acquisition_id`**（该路径不经 `_finish`）；18 条 `action_ack` 日志**均无** `acquisition_id` | "每帧日志都带该字段"的表述有 1 帧例外；回执日志需交叉引用 `action_records` 才能拿到 id | 我对 23 个 JSONL 的逐行统计 | 早退路径与回执日志补记该字段，或修改表述 |
| NB-r03-07 | `s6_core.py`（B18/B22/B23/B25 分支）、`…/run_report.json`+`logs` | `must_log` 事件名未落地：`E_FRAME_STALE`/`E_FRAME_DUPLICATE`(或 `E_FRAME_CONFLICT`)/`E_FRAME_OUT_OF_ORDER`/`E_SESSION_RESET_SUSPECTED` 在证据中命中 **0** 次（实现用 `input_state`/`reason`/`counters` 表达等价信息）；B13 的"剩余冷却时间"未记录 | 按行为表字面 `must_log` 无法按事件名核对 B18/B22/B23/B25/B13 | 我按名字符串统计 | 补事件名或登记"以字段替代"的口径 |
| NB-r03-08 | `s6_core.py:589`（M1）与 `:616`（M15）用 `x or t_now_ns` 判未设置 | 首帧 `t=0` 时 `candidate_dwell_start_ns=0` 被当作"未设置"，锚点被改为 M1 帧时刻（我实测 dwell 由 0 变 100 ms） | M4 的停留判据在 `t_start=0` 的回放里整体后移一帧；交付用例自洽但该写法有隐患 | §4 H 项独立观测 | 改用 `is None` 判空并回归 M4 相关用例 |
| NB-r03-09 | `…/s6b_core_20261023_r03/export_selfproof.{json,md}`（被清单绑定） | 陈旧误导性证据：04:10 快照，契约 `v1.6`、RunId `s6a_g0_20261022_r07`、清单尚无自证行，却声称 `ALL_SELF_PROVEN` | 与包内 v1.7 口径、与最终 `_selfproof`(`NOT_ALL_SELF_PROVEN`) 冲突 | `static_chk.py` 尾段 + 该文件内容 | 用交付提交的自证报告替换，或删除该绑定并重生成清单 |
| NB-r03-10 | `docs/stage6/s6a_stage6_g0_behavior_v1.json` `transitions[M4]` | **（属 S6-A 范围，仅记录）** v1.7 的 `transitions[M4].reachability="UNREACHABLE_UNDER_DRAFT_PARAMS"`+旧 note 与 `reachability.transitions.M4.status="REACHABLE"` 冲突；S6-B `reachability_notes.json` 称"S6-A 侧 reachability.M4/U6-12 已同步修正（r07）"对该 per-transition 字段不成立 | 跨文件口径冲突（S6-A 侧，另有终审 A） | `legacy_chk.py` | 转 S6-A 责任方修；S6-B 侧把该断言限定到 `reachability.transitions.M4` |
| NB-r03-11 | `verification/claim_verify.py:62-73` | 4 条 claim 的 `exit_code` 由 `0 if ok else 1` **自算**，不是被命令的真实退出码（工具里唯一真正的退出码是进程自身的） | "命令 + 真实退出码"的模板在该字段上名不符实 | 代码 + §1 #7 | 记录被调命令的真实退出码，或把字段改名为 `verdict_code` |
| NB-r03-12 | 被审工作树 `w6` | 审查期间被第三方持续改写：`04:41–04:45` 14 个 `M`，**04:45:59 新增提交 `1839766` 就地改写 r03 证据包**，至 05:08 仍有 42 条 `M`/`??` 与新增 `hash_convention_check.py`/`hash_convention_counterexamples.json` | 轮次边界被打破（同一 RunId `s6b_core_20261023_r03` 在 git 历史中出现 ≥2 种内容）；本轮结论只对 `e3aeb09`/`05126fd` 内容有效；`1839766` 须作为新轮次独立复审 | `git status`/`git log`/mtime/进程 | 明确写入归属与新 RunId；不要以"覆盖既有 RunId"的方式重跑证据 |

## 10. 审查基线之后的变化（post-baseline，仅供总控排程，不并入本轮结论）

审查期间新增提交 `1839766`（04:45:59，`chore(stage6): freeze S6-A v1.7/r08 + S6-B r03`）**就地改写了 r03 证据包**。我在隔离克隆上做了 3 项快速核对（`clone_1839766`，仅用于给出下一步线索）：

1. **`BLK-r03-1` 未修**：`1839766` 的 `src/stage6/s6_core.py` 与 `e3aeb09` **逐字节相同**（LF 形态 sha256 前 16 位均为 `6db626c711771079`）→ `acquisition_id` 在 M2/M8 路径仍不分配新 id。
2. **`BLK-r03-2` 的绑定问题已修**：`1839766` 的 `delivery_manifest.json` 对 `.codex/STATE.md` 声明 `692f1ee8…`，恰为该提交 `STATE.md` 的 LF 形态；换行对齐后 `check_stage_delivery --mode evidence` = **exit 0 / CHECKS_OK**（55 个文件按清单口径重写，无 unresolved）。
3. **但 `1839766` 引入新的清单口径冲突**：r03 的 `delivery_manifest.json` 与 `inputs_manifest.json` 对**同一文件** `docs/stage6/s6a_stage6_g0_behavior_v1.json` 声明了**互为另一换行形态**的哈希（delivery = LF `bc90945c…`；inputs = CRLF `58e4892e…`；该提交内文件为 LF）→ **不存在任何工作区字节状态能同时满足两份清单**；实测 `--mode inputs` = **exit 2**（错误：`files[0].path SHA-256 不匹配…归一化亦不匹配`），而 `--mode evidence` = 0。另外该提交的 `checks` 行仍把 inputs/evidence 都标为 PASS/0。

→ 建议：把 `1839766`（及工作区中尚未提交的 hash 口径修复）作为**新一轮 r04** 冻结后**独立复审**；届时需一并回归 `BLK-r03-1`、口径冲突、`run_report` 与两份清单的换行声明一致性，以及"同一 RunId 不就地重跑"的规则遵守情况。

## 8. 无回归 / 无夸大（正面结论）

- **23/23 可复现**：隔离克隆内重跑驱动 exit 0、**0.125 s**，`run_report.json` + 23 个 JSONL 与清单声明**逐字节一致**；运行后与"声明口径"副本 **0 个文件不同**。
- **探针 4 项**退出码 `0/2/1/1` 全 AS_EXPECTED（消歧力真实存在：冻结后改 expected → exit 2；注入错误语义 → exit 1；`T6-S01=900 ms` 注入 → exit 1/133 断言失败，证明阈值确实读 JSON）。
- **24 项参数相对 r02 逐项未变**、全部 `PENDING_APPROVAL`；`expected` 仍由构建器独立推导（我未发现回填痕迹；`case_matrix` 与摘要计数自洽）。
- **结论范围限定到位**，未发现"已审查/已通过"式自夸，**无"声明存在但缺失"的文件**。
- 30 fps 取较晚、零框不推进、全局冷却门（含门在异常帧开启时不触发）、`K01`/`L02` ±1 ns、M2/M13/M12、同帧 M4/M10 取 M10、STABLE 锁存与门开即触发、动作层幂等与 `T6-A02` 去重：**独立推导期望与实测全部一致**。

## 9. 范围声明

本报告仅覆盖 **S6-B/S6-C r03**（`src/stage6/{s6_core,s6_actions,s6_params}.py`、`verification/{s6b_run_cases,s6b_probe,s6b_build_evidence,claim_verify}.py`、`report/evidence/S6-B/s6b_core_20261023_r03{,_selfproof}/**`）。**不代表 G0/G2/G3/G4/G5**，不含实物/板卡/摄像头/HDMI/≥30 分钟回放验证；**不评价 S6-A 规格**（`NB-r03-10` 仅是跨文件一致性观察，权属 S6-A 终审 A）。审查期间未在被审工作树 `w6` 内写入任何文件；全部验证写入 `D:\FPGA_Competition\tmp\review\FINAL_B_20261023_r01\`。

### 附：本目录内可复核产物

- `run_suite_e3a_clone.{json,log}`、`chk_committed_out.txt`、`chk_blobs2_out.txt`、`chk_sources_out.txt`、`legacy_chk_out.txt`、`static_chk_out.txt`
- `exp_utf8_probe_out.txt`、`utf8_probe_sequence.log`、`chk_checks_out.txt`
- `self_e3a.json`、`self_e3a.md`、`self_e3a_out.txt`（e3aeb09/05126fd/snapshot 三项自证）
- `adv_semantics_out.txt`、`adv_semantics_result.json`（46 项对抗断言）
- `clone_e3a/`、`clone_051/`、`clone_e3b/`（审查基线隔离克隆）、`clone_1839766/`（post-baseline 快照，仅 §10 用）、`pristine_*/`（清单口径副本）