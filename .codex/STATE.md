# 阶段6 状态入口（w6 / stage6-interact-prep）

更新：2026-10-23 04:20（UTC+8）。按 `AGENTS.md` 与主 STATE 恢复；**本文件是阶段6 工作树专属状态**，主状态 `D:\FPGA_Competition\.codex\STATE.md` 只读。阶段技术事实以本文件与本树证据为准。

## 阶段目标与范围

- 目标：稳定手势判定 → HDMI 切图/界面/显示状态；冻结多框目标选择、丢失与重获、稳定窗口、保持期触发语义、冷却、再触发条件、无手/未知/超时错误与恢复行为（计划 L102–L108）。
- 范围：`w6` 独占写入；S6-A 契约（v1.6 / r07，r05、r06 已分别过第 5/6 轮复评 PASS）→ S6-B 状态机实现与 6-C 确定性矩阵（实现轮复评判 CHANGES_REQUIRED，修正中）→ 6-D 无摄像头两级联调 → 6-E 真摄像头验收（延期）。
- **冻结自证规则（F6，永久）**：任何“冻结/交付”提交必须自证 —— `python -B verification/export_selfproof.py --project-root <abs> --commit <rev>` 导出该提交后，自检与 `check_stage_delivery` inputs/evidence 三项都必须 exit 0；S6-B 最终冻结同样适用。
- 硬边界：**无硬件授权**——不碰板卡/JTAG/COM4/`hw_server`/HDMI 实物/摄像头，不烧录；`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读；两个 mailbox 只读；不 push；同时只跑一个重型任务。
- 注入/回放结论适用范围仅限回放/注入输入；真手势验收延期至摄像头到货。

## 上游绑定与冻结状态（2026-10-23 核实）

- 已冻结、可直接引用：`S2A-T01` 规格（`7c2c8684…`）、阶段计划 L102–L108、`D2`（`df95a843…`）、`D6`（`735cbc78…`）。
- **未冻结（仅草案/隔离使用）**：阶段4 `s4a_stage4_g0_fields.json`（`DRAFT_NOT_FROZEN`，`73c3dad` 版本 `3524d02a…`）；阶段5 `S5A v2`（`ca5968d4…`，离线定稿未验收）。
- 阶段4/阶段5 接口未冻结 → 阶段6 集成验收依赖 `BLOCKED`；不得据此做集成验收。

## 本轮已完成（S6-A v1.4 / r05 收尾，PENDING_REVIEW）

- 输入：S6-A r04（提交 `b20b670`，契约 `S6A-G0-v1.3`）已通过**第 4 轮独立复评** `S6A_r04_20261023_r01`（`PASS`，0 阻断 / 5 非阻断）。r05 按 task-6 第一部分逐条收尾：
  - **N-r04-01**：`transitions.M5.condition` 补「（且本帧必须为窗口推进帧：`state ∈ {OK,NO_HAND}`、`stale=false`、非重复、非倒序）」，新增 `window_advance_required` 并与 §4 锁存段、`stable_latching.suppressed_trigger_release` 一致；自检 C12 增加 M5 / 文档 §4 M5 行 / `suppressed_trigger_release` 三处文本断言；新增手算样例 **HC-30** 覆盖「锁存 STABLE + 全局冷却门恰在 `TIMEOUT` 帧开启」并断言该帧无动作（B21）、门在 `OK` 帧开启时该帧即触发。
  - **N-r04-02**：绑定叙述精确化——「M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段。」（本句与 JSON `predicate_binding_policy.statement` 逐字一致，C12 断言其同时出现在文档 §4 与本文件。）
  - **N-r04-03**：C12 增加普适断言「任何条目的 `predicates_used` 出现时必须为非空列表，显式空列表 `[]` 不合法」；由 `verification/s6a_r05_probe.py` 注入用例 `empty_predicates_used` 证明可捕获。
  - **N-r04-04**（**已被 r06 取代**）：r05 曾按「窗口首帧 → 第 `T6-S02` 个 `WINDOW_MATCH` 帧」取跨度并断言 `span_conventions_agree`；r06 证明该口径在 30fps 下会漏判，已改为按 `T6-S03`「取较晚」推导**完成帧**（`completion_index`），`span_conventions_agree` 字段已移除。
  - **N-r04-05**：清理 `src/stage6/s6_core.py` 对不存在设计文档的引用，改引用现有 v1.4 契约文件；**该 WIP 仍未提交、不作为证据**。
- 判别力证明（r05 当时）：旧包重跑 `selfcheck_r04_failure.json`（当时的口径为「样例数与窗口跨度」）与 `probe_summary.json`（基线 + 注入）均为 FAILED/exit 1；**r06 起该归因已改准为「样例数不足（缺 HC-30/31/32）」，见 r06/r07 记录**。先证明后出 `ALL_PASS`（17 项，含完整 C11）——见「证据入口」。
- 24 项参数值与批准状态**未改**，全部 `PENDING_APPROVAL`；未在测试集调参；未触碰硬件。

## 本轮已完成（S6-A v1.5 / r06 收尾，PENDING_REVIEW）

- 输入：S6-A r05（提交 `1632761`，契约 `S6A-G0-v1.4`）已通过**第 5 轮独立复评** `S6A_r05_20261023_r01`（`PASS`，0 阻断 / 4 非阻断）。
- **N-r05-04（打真实 30fps）**：窗口完成帧按 `T6-S03`「**取较晚满足者**」实现 —— 完成帧 = 第一个「连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`」**且**「(帧序 − 窗口首帧序)·`P` ≥ `T6-S01`」的帧。旧口径只按第 `T6-S02` 个 `WINDOW_MATCH` 帧取跨度，在 `P < T6-S01/(T6-S02−1)`（草案下 40 ms；**30fps=33.3 ms**）时会把本应完成的窗口误判为未完成，与 §15「30fps → 第 8 帧 233.1 ms」冲突。新增样例 **HC-31**（完成帧 7 → 233.1 ms、`later_of_applied=true`、旧口径 `m3_fires_count_only=false`）；保留旧口径对照字段；probe 增加「旧口径对照」运行（用 r05 版自检脚本跑 r06 样例，必须 C7 FAIL）；文档 §15 与 JSON `time_anchors.window_complete`/`low_fps_latency` 同步。
- `N-r05-01` 探针计数表述统一为「基线 1 例 + 注入 7 例（共 8 例）」+ 旧口径对照 1 例；`N-r05-02` r04 重跑失败归因改为「样例数 29<30（缺 HC-30）」且 N-r04-04 判别力只引探针 `case_span_wrong`；`N-r05-03` HC-30 动作计数改为「给定序列内计数」+ 覆盖边界说明。
- 24 项参数值与批准状态**未改**；r05 包不改写（RunId 不可覆盖），更正记于 r06 记录。

## 本轮已完成（S6-A v1.7 / r08 + S6-B r03，PENDING_REVIEW）

- **S6-A r08（task-11）**：第 7 轮复评 1 阻断 + 6 非阻断收尾。`BLK-r07-1`：**M4 可达性口径统一 8 处**——JSON
  `parameter_notes.T6-S04`/`reachability.consequence`/`reachability.M4.review_correction`、
  **HC-23 的 `expected.m4_reachable_under_draft` 由 false 改为 true**（原先 C7 机器断言与 C16 结论相反）、
  清单 limitations 与摘要、文档 §18、STATE；C16 新增**全包禁语断言**（探针 `m4_conflict_phrase` 实测可捕获）。
  `N-r07-1`：自证工具换行对齐顺序改为「先工作区、后清单」，消除干净克隆 + `autocrlf=true` 下的假阴性。
  `N-r07-2`：自证报告移入同 RunId 的 `_selfproof` 兄弟目录，提交后可补入交付提交主体。
  `F2`/`F4`/`F5`/`F11`：`source_commit` 语义三处统一、`keep_reason` 统一为「样例数不足 32：29」、陈旧行与旧令牌清理。
- **S6-B r03（task-10）**：r02 复评 2 阻断 + 10 非阻断收尾。`BLK-r02-1`：`acquisition_id` 改为**真的在 M11/M4 递增**
  （M8 归零、目标切换维持递增），每帧日志与动作记录都带该字段 → C3 两次获取实测 `[0, 1]`。
  `BLK-r02-2`：`action_records` 写进 `run_report.json`（四字段齐全）且四个 `ACTION_*` 事件名进证据；
  4 个 OUT_* 与 SUP_DEDUP/STATES 死常量删除。`NB-01..10` 同步（版本 v1.6、23 例、D8 按实测改写并登记开放偏差、
  未实现项真登记、子进程显式 UTF-8、动作层重复键修复）。
- **新硬规则（本轮起）**：任何「已关闭/已落盘/已同步」声明必须附 `claim_verification` 附录
  （命令 + 真实退出码 + 可观察输出），由 `verification/claim_verify.py` 生成并随包入库。

## S6-B / S6-C（task-6 第二部分，已产出待复评）

- 实现（按 v1.4 契约重写旧 WIP）：`src/stage6/s6_actions.py`（动作层：幂等提交、success/fail/unobserved 二分、`action_id`/来源帧、`T6-A02` 去重）、`src/stage6/s6_core.py`（纯核心：事件入、状态/动作请求/日志出，不读摄像头/墙钟/HDMI）、`src/stage6/s6_params.py`（阈值只从行为表 JSON 读入并强制 `PENDING_APPROVAL`，核心内无阈值字面量）。
- 关键语义落地：H-4（`NO_HAND` 推进时间/结果计数但不推进 WINDOW_MATCH、零框不得完成窗口）、H-10（冷却全局门；门在 STABLE 未开时记 `S_COOLDOWN` 并保持锁存）、M3 只按 `WINDOW_MATCH`、M10 只按 `TARGET_CONTINUES`、STABLE 本次获取内锁存（退出仅 M2/M10/M5）、一次获取一次触发、`window_complete` 与 `W_min` 口径、异常窗口/恢复（M2/M13/M12，恢复期不计窗口）。
- 6-C 矩阵：`verification/s6b_run_cases.py`（虚拟单调时钟 + JSON 用例 + 逐帧 JSONL 日志 + 断言 + 非零退出；运行前校验 expected 冻结哈希）+ S6-B 证据目录内的 cases/case_matrix.json（**22 条 / 覆盖 CDX-012 §4 全部 11 类**，expected 由行为表 v1.5 人工推导）。
- **N-r05-04 同步**：核心的 `window_complete_ns` 改为在 **M3 成立帧**（计数与时长取较晚）写入，不再在第 `T6-S02` 个 `WINDOW_MATCH` 帧写入；新增 30fps 用例 `C9c-30fps-later-of` 断言 `window_complete_ns=233100000`（旧逻辑会给 166.5 ms 帧）。
- 结果：22/22 用例 PASS（r01）。**r02（task-9 修正轮）**：BLK-1(a) 把 M4 修正为**可达并计入覆盖**（`TARGET_CONTINUES` 不含 `score ≥ T6-P02` → 低分中断不推进 `miss_streak`，M10 不先命中；用例 C4-jitter-reset 实测 M4@f7）；N-01 版本统一 v1.6；N-02 计数写实；N-03 11 类覆盖映射由实际用例派生（含 C9c）；N-04 动作记录含 acquisition_id 并登记未实现的 `transition_candidates`/`S_CONFLICT_RESOLVED`；N-05 acquisition_id 规则写入 decision_notes；N-06 `REQUIRED_PARAMETER_IDS` 扩到全部 24 项；N-07 `NO_HAND` 带 detections 计非法（新增用例 C6b）；N-08 IDLE 有目标时不求值 M10 写入 decision_notes；N-09 运行前校验 `cases_file_sha256`（冻结点后改用例即拒运行）；N-10 `source_commit` 动态取 HEAD 并由自证工具绑定交付提交。新 RunId `report/evidence/S6-B/s6b_core_20261023_r02/`：**23/23 用例 PASS**（覆盖 11 类）、探针 4/4 符合预期、两个检查器 exit 0，且 **F6 导出自证 ALL_SELF_PROVEN [0,0,0,0]**（S6-A 自检 STATE + S6-B 驱动 + S6-B inputs/evidence）。
- 不计入覆盖项：B16 `S_DEDUP`（`T6-A02`500 ms < `T6-K01`1000 ms）与 M7（构造上）；**M4/`T6-S04` 保留并计入覆盖**（M4/T6-S04 保留并计入覆盖；覆盖声明覆盖全部可达迁移（B16 与 M7 按登记另行说明）），见 `reachability_notes.json` 与行为表 `reachability.transitions.M4.status`。历史语境除外
- `docs/stage6/s6b_frozen_interface_v1.json` 状态改为 `S6B_IMPLEMENTATION_BASELINE_PENDING_REVIEW`（只读 2A 常量，不是新冻结）。

## 未决与阻塞

- **待 Wong/G0 确认**：`U6-16`（STABLE 锁存口径）；`U6-12`（`T6-S04`/M4 可达性）；`U6-13`（阶段4 实测帧周期 `P_meas`，`T6-A03` `NOT_RUN`）；`U6-14`（逐类 UX 可见时长）；`U6-15`（`A_DISPLAY_STATE`）；`U6-01..U6-11`。
- **BLOCKED**：阶段4/阶段5 接口未冻结；阶段4 实测帧周期未取得；真摄像头验收延期；独立 Reviewer 无法由本会话创建（委派深度 0，由项目总控安排）。
- **S6-A 状态**：v1.4/r05 为 `PENDING_REVIEW`（r04 已 PASS、r05 只关非阻断项）；是否再复评由项目总控决定；不得自称已审查/已通过。

## 证据入口（r07）

- 本轮：`report/evidence/S6-A/s6a_g0_20261022_r07/`（`delivery_manifest.json`、`inputs_manifest.json`、`hashes_sha256.txt`、`selfcheck_result.json`、`selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`、`selfcheck_old_package_failure.json`、`selfcheck_old_package_failure_stdout.txt`、`selfcheck_r02_blk1_failure.json`、`selfcheck_r02_blk1_failure_stdout.txt`、`selfcheck_r03_failure.json`、`selfcheck_r03_failure_stdout.txt`、`selfcheck_r04_failure.json`、`selfcheck_r04_failure_stdout.txt`、`old_package_under_test.json`、`r02_package_under_test.json`、`r03_package_under_test.json`、`r04_package_under_test.json`、`probe_summary.json`、`probe_baseline_no_injection_stdout.txt`、`probe_m5_window_advance_removed_stdout.txt`、`probe_empty_predicates_used_stdout.txt`、`probe_b13_predicates_used_added_stdout.txt`、`probe_b07_old_wording_stdout.txt`、`probe_case_timeout_frame_action_stdout.txt`、`probe_case_span_wrong_stdout.txt`、`probe_case_out_of_sequence_index_stdout.txt`、`probe_historical_model_check_r05_stdout.txt`、`probe_historical_model_check_r06_stdout.txt`、`fix_record.json`、`fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`、`S6A_run_summary.md`；export_selfproof.json 与 export_selfproof.md 由自证工具在清单生成前写入，故由 `delivery_manifest.json` 声明而不在此列举——若在此声明，提交前的工作区快照自证会因该文件尚未生成而 C11 失败）。
- 上一轮：`report/evidence/S6-A/s6a_g0_20261022_r07/`；更早 r01..r06 保持原样（**RunId 证据不可覆盖**）。
- 自证报告（N-r07-2）：位于同 RunId 的 `_selfproof` 兄弟目录（不被清单与 STATE 声明，避免快照自证时该目录尚为空而误判）。
- 验证附录（新硬规则）：两个包各自的 `claim_verification.json`/`claim_verification.md`（S6-A r08 与 S6-B r03 目录内）。
- 冻结自证：`python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 --commit <rev>`（导出该提交后自检 + inputs + evidence 三项必须 exit 0）。
- 规格：`docs/stage6/`；自检：`verification/s6_g0_selfcheck.py`（C1–C17）；清单构建器：`verification/s6a_build_evidence.py`；旧包重跑：`verification/s6a_rerun_legacy_failures.py`；判别力探针：`verification/s6a_r07_probe.py`；冻结自证：`verification/export_selfproof.py`；缓存：`tmp/6/**`（不入库）。

## 提交勘误（erratum，2026-10-23）

- `e3aeb091a0793737d99fbdfd1df4e146cb55eec6`：**标签写作 S6-B r03，实际内容 = S6-B r03 + 修正后的 STATE + 重建的 S6-A r08 证据**
  （在 HEAD 已是 r03 提交时执行了 `git commit --amend --no-edit`，把 r08 侧收尾折入该提交）。按**内容**复跑（实测命令与退出码）：
  `python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 --commit e3aeb091a0793737d99fbdfd1df4e146cb55eec6`
  → `{"verdict": "ALL_SELF_PROVEN", "subjects": [["commit e3aeb09…", "SELF_PROVEN", [0,0,0]]]}`，**退出码 0**（2026-10-23 实测）。
- `05126fdb79ba77de57d9262857af66393b453d66`：amend **之前**的 r03 提交（现已被 amend 取代）。amend 当时实测 `SELF_PROVEN [0,0,0,0]`（退出码 0）；
  **按当前工具复跑为 `NOT_SELF_PROVEN [0,0,0,2]`（退出码 1）**——其清单绑定的 `.codex/STATE.md` 与该提交树内的 STATE 不一致（该中间提交的内部不一致），
  已由 `e3aeb09` 修正。差异如实记录，不追改历史。
- `902be77f5d672d1019f37d4c706276095d09e83f`：**中间提交，不自证**（其 STATE 声明了当时尚未提交的 r03 证据目录 → 单独检出 C11 会 FAIL）；
  非冻结提交，不算缺陷。
- 未改写历史：未对以上提交做 amend/rebase/revert；最终冻结提交见下一段（标签正确 + 自证）。
- **O1 口径与自证路径澄清**：本轮起清单可声明**git 归一化（CRLF→LF）口径**哈希，检查器与自检**同时接受**原字节与归一化字节，
  因此裸 `git archive`（全 LF）导出下 **C11 实测 PASS**（2026-10-23 在 `e3aeb09` 的裸导出上实测）；但裸导出仍需上游文档齐全（C8 依赖仓库内上游文件），
  故**权威自证路径仍是 `verification/export_selfproof.py`**，裸检出只作辅助核对。

## 冻结判定与当前缺口（CANDIDATE_FREEZE）

- **判定线（lead 裁决）**：只有 **S6-A 剖面 `[0,0,0]` 且 S6-B 剖面 `[0,0,0,0]` 同时成立**才算冻结。
- `1839766883436f521383f5432446eb67a01ada56` 当前状态：**`CANDIDATE_FREEZE（未冻结）`**——其 S6-B 剖面未过，缺口如下（命令 + 真实退出码）：
  - `python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 --commit 1839766 --s6b-run report/evidence/S6-B/s6b_core_20261023_r03`
    → `{"verdict": "NOT_ALL_SELF_PROVEN", "subjects": [["commit 1839766…", "NOT_SELF_PROVEN", [0, 0, 2, 2]]]}`，**退出码 1**（S6-B 两个交付检查器判 2）。
  - 同一命令的 S6-A 剖面：`--commit 1839766`（不带 `--s6b-run`）→ `ALL_SELF_PROVEN [0,0,0]`，**退出码 0**。
- **缺口根因（已定位，工作区已修，尚未提交）**：两处失配是**两个不同原因**，不是"内容级"同类：
  1. `inputs_manifest.files[0]`（`docs/stage6/s6a_stage6_g0_behavior_v1.json`）：清单声明工作区**原字节（CRLF）**哈希、导出为 LF →
     接受器此前只有 CRLF→LF 方向，故永远命中不了；已补 **LF→CRLF 反方向**（`hash_variants` 三口径）。
  2. `delivery_manifest.files[42]`（`run_report.json`）：S6-B 自证模式在导出内重跑 driver，driver 会重写该文件；而 driver 的冻结
     `expected_freeze.json` 含 `frozen_at_utc8` 时间戳且每次被强制重冻结，导致 `run_report.json`（内嵌 `expected_freeze_sha256`）
     每次运行都变 → 任何声明值都会失配。已修：冻结**幂等复用**（内容等价不复写）+ `behavior_json_sha256` 按 **O1 归一化（CRLF→LF）** 取哈希
     + 构建器不再强制重冻结。
  3. 同一包内两条曾用**不同口径**，现已统一：清单声明一律取**git 归一化（LF）**值，接受器接受 原字节 / CRLF→LF / LF→CRLF 三种口径。
- **工作区修正后的实测（尚未提交，等待终审 A/B 结论后再 amend `1839766` 或新建 freeze-r2）**：
  - `python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 --worktree-snapshot`
    → `ALL_SELF_PROVEN [0,0,0]`，**退出码 0**。
  - 加 `--s6b-run report/evidence/S6-B/s6b_core_20261023_r03` → `ALL_SELF_PROVEN [0,0,0,0]`，**退出码 0**。
  - 双向反例（真实 `verify_hash`，非复刻）：`python -B verification/hash_convention_check.py` → `ALL_AS_EXPECTED`，**退出码 0**；
    四个接受用例（清单 LF↔文件 LF、清单 CRLF↔文件 CRLF、CRLF→LF、**LF→CRLF**）+ 一个负例（内容不同必须拒绝）见
    `hash_convention_counterexamples.json`（两个证据包内各一份）。
  - 两包在工作区仍全绿：S6-A 自检 ALL_PASS（17 项）+ 两检查器 exit 0；S6-B 23/23 用例 PASS + 探针 4/4 + 两检查器 exit 0；
    冻结哈希连续两次构建一致（`f81483a8…`，幂等生效）。
- **纪律**：修正只在工作区，**未提交**；三个受保护提交（`e3aeb09`/`f3c537d`/`902be77`）与 `1839766` 均未 amend/rebase/revert。

## 构建期结构规则（顺序/只读）

- **冻结后禁止再改动 run-dir 内容**（第 5 次同源教训）：构建器 `FIXPOINT` 必须是最后动作，其后任何往 RunId 目录加/改文件的行为都会让清单失效；构建末尾新增 `[CLOSING]` 断言（重跑 evidence 模式，出现未声明文件即中止构建）。r09 现状：`[CLOSING] run-dir 无未声明文件、清单一致`、新鲜自检两步 `BOTH_ALL_PASS`（产物 tmp/6/fresh_selfcheck_pair.json 反映最终状态）。

## 哈希绑定口径（活文档 vs 交付物）

- **活文档（.codex/STATE.md、进度记录）不进硬哈希集合**；只有交付物（规格/证据/清单/工具）绑哈希。
- STATE 只做「存在性 + 其声明的文件/目录必须存在」检查（F6 本质）；其哈希以信息性快照记在 _selfproof 报告中。

## 两段式冻结：F / G（2026-10-23）

- **F = 交付内容提交**：`0725d9cf48aeed21d3ea445ef01575c16b68d950`（S6-A v1.8/r09 + S6-B r04 + 工具/结构修复）。
- **G = 自证记录提交**（本提交）：把 F 追加为自证报告主体，并附**传输克隆**自证记录；**附注 tag 打在 G 上**。
- **传输克隆双侧自证（真实命令 + 退出码）**：
  1. `git clone --no-local D:/codex-worktrees/w6 <tmp>` → exit 0；
  2. `<tmp>/verification/export_selfproof.py --project-root <tmp> --commit 0725d9cf…` → `ALL_SELF_PROVEN [0,0,0]`，**exit 0**（S6-A 剖面）；
  3. 同上加 `--s6b-run report/evidence/S6-B/s6b_core_20261023_r04` → `ALL_SELF_PROVEN [0,0,0,0]`，**exit 0**（S6-B 剖面）。
  记录：`report/evidence/S6-A/s6a_g0_20261022_r09_selfproof/transport_clone_selfproof.json`、`report/evidence/S6-B/s6b_core_20261023_r04_selfproof/transport_clone_selfproof.json`。
- **来源可达性**：`source_commit` = `1839766…`（F 的父提交，`transport_clone_check.py` 判 `RESOLVABLE`）；自证主体 F 本身可达（G 的 tag 指向）。
- **冻结后纪律**：提交 G 后**停止写 w6**（含 STATE）；需要更新须下轮解冻。

## 定向解冻与重新冻结（2026-10-23，B-1 修复轮）

- **B-1（假证书）已关闭**：`verification/claim_verify.py` 的 `results.append` 原位于 `return 1` 之后（永不可达），
  导致 S6-A r09 附录只剩 1 条 claim 却自称 `ALL_CLAIMS_VERIFIED`。修后 append 在**循环体内**，并新增两条断言：
  ① `claims` 数量 == 定义数 + 1；② `verdict` 由**全部** claim 的退出码计算，空列表/数量不符一律 `NOT_ALL_VERIFIED`。
  两条断言都有**必 FAIL 自测例**（`--simulate-defect count_mismatch|empty` ⇒ 退出码非 0 且判 NOT_ALL_VERIFIED）。
- **同轮关闭**：S6-B 构建器此前只**读**旧附录、从不运行 claim 工具（⇒ 复现不出来）→ 现真正运行；
  claim 命令统一用项目根相对 POSIX 路径（绝对 Windows 路径的反斜杠会破坏 `python -c`）；
  C11 区分**文件/目录**（限制①）；套件自证用例**固定指向交付提交**并解析最新冻结 tag（限制②）；
  新增 S6-B 新鲜证据两步工具（限制③）；`NB-r03-08`（`candidate_dwell_start_ns` 改显式 `is None`，语义改动）已登记；
  行为表 `status_label` 更新为当前版本。
- **新 RunId**：S6-A `s6a_g0_20261023_r10`、S6-B `s6b_core_20261023_r05`（**未**就地改写 r09/r04）。
- **两段式冻结（本轮最终）**：
  - **F4 = 交付内容**：`6b8e5f2a23ce6f7dec41fc9992141b3423612081`（r10/r05 以**可达**的 `source_commit = F3` 重建）；
  - **G4 = 自证记录**（本提交）：报告主体为**F4**（另列工作区快照）+ **传输克隆**自证记录；
  - **tag `stage6-freeze-20261023-r3` 打在 G4**；更早的 tag 全部保留指向各自提交，不删不动。
  - 中间轮：F2/G2（tag `stage6-freeze-20261023-r2`）与 F3（`efb9f191`，被 amend 前的中间态）**均被 F4/G4 取代**；
    说明：F3 的一次 amend 曾使 F2 失去可达性 ⇒ 包内 `source_commit` 解析失败（传输克隆 exit 2）；
    本轮最终以 F3 为基线重建，故 F2/F3/F4/G4 **全部可达**。
- **四条硬条件实测**：① 两份附录由冻结工具可复现且计数正确（S6-A 7 = 6 + 1；S6-B 5 = 4 + 1，`count_ok=True`，
  verdict `ALL_CLAIMS_VERIFIED`）；② 传输克隆 `--commit F4` 双侧全绿（`[0,0,0]` / `[0,0,0,0]`，退出码均 0）；
  ③ `--commit G4` 全绿；④ 套件在 HEAD=G4 时 10/10（含两条新增必 FAIL 例）。
- **已知限制（如实）**：上一轮记录提交 G（`1e2a66c`）自身快照自证不绿（其 STATE 以文件形式声明 `report/evidence/...`
  路径而当时 C11 按目录判定）；套件单次约 20 分钟，冻结时由总控与复核方各跑一次。
- **冻结后纪律**：提交 G4 后停止写 w6（含 STATE）；需要更新须下轮解冻。

## 两段式冻结（第二轮）：F2 / G2（2026-10-23）

- **F2 = 本轮交付内容提交**：`33b1fee30af1974560fa0b94bf6c6662d3e5d1e0`。承载 B-1 修复与三项限制：
  ① `claim_verify.py` 的 `results.append` 移入循环体（此前位于 `return 1` 之后 ⇒ 附录只剩 1 条却自称
  ALL_CLAIMS_VERIFIED）；② 两条新断言（claims 数量 == 定义数 + 1；verdict 由**全部** claim 计算，空列表/数量不符
  一律 NOT_ALL_VERIFIED）；③ S6-B 构建器**真正运行** claim 工具（此前只读旧附录 ⇒ 复现不出来）；
  ④ claim 命令统一用项目根相对 POSIX 路径（绝对 Windows 路径的反斜杠会破坏 `python -c`）；
  ⑤ C11 区分文件/目录（限制①）；⑥ 套件自证用例固定指向交付提交、不再用 HEAD（限制②）；
  ⑦ 新增 S6-B 新鲜证据两步工具（限制③）；⑧ 新 RunId **S6-A `s6a_g0_20261023_r10`** /
  **S6-B `s6b_core_20261023_r05`**（不就地改写 r09/r04）。
- **G2 = 自证记录提交**（本提交）：把 F2 追加为自证报告主体，并附**传输克隆**自证记录；
  **附注 tag `stage6-freeze-20261023-r2` 打在 G2**。旧 tag（`s6a-g0-v1.8-r09`、`s6b-core-r04`、
  `stage6-freeze-20261023`）保留指向 G，不删不动；**G2 取代 G 作为冻结记录**。
- **本轮冻结成立项**：① 两份附录由冻结工具可复现且计数正确（S6-A 7 条 = 6 定义 + 1 假声明；S6-B 5 条 = 4 + 1）；
  ② 传输克隆里 `export_selfproof --commit F2` 双侧全绿（S6-A `[0,0,0]`、S6-B `[0,0,0,0]`，退出码均 0）；
  ③ `--commit G2` 亦全绿（限制①已修）；④ 工具自测套件在 HEAD=G2 时 10/10（含两条新增必 FAIL 例）。
- **已知限制（如实，不阻断冻结）**：① 上一轮记录提交 G 自身快照自证不绿——其 STATE 以文件形式声明
  `report/evidence/...` 路径，而当时 C11 按目录判定；本轮已修，G 保持历史不绿、由 G2 取代。
  ② 套件 `selfproof_valid_commit` 在 tag r2 出现**之前**会「跳过并标注」（该例已固定指向交付提交，不再依赖 HEAD）。
  ③ 已知成本：套件单次约 20 分钟，冻结时由总控与复核方各跑一次。
- **冻结后纪律**：提交 G2 后停止写 w6（含 STATE）；需要更新须下轮解冻。

## 批准应用轮（2026-10-23）：24 项参数由待批准转为已批准

- **批准记录**：CTRL-DSH-HANDOFF/decisions/`stage6_approval_receipt_20261023_r01.md`（主仓库；w6 内引用见行为表 approval_record）
  （用户原文「按你建议」「阶段7暂时不开」，2026-10-23）。行为表新增 `approval_record`，
  24 项参数写入 `approval_status=APPROVED_20261023` 与 `approval_ref`；**参数值零差异**（批准的是草案值）。
- **逐项生效决定**：`T6-A02` 保持 500ms 不修改；
- `B16 S_DEDUP` 登记为**设计上不可达**（同一行为已由 H-10 全局冷却门覆盖），不计入覆盖项；
- `T6-S01`/`T6-S02` 批准（30fps 第 8 帧 233.1ms，按 T6-S03「取较晚」）；`U6-12` 保留并计入覆盖的迁移为 M4；
  `U6-16` STABLE 获取内锁存；`U6-15` = `A_SWITCH_UI`+`A_SWITCH_CHANNEL`；`U6-13` 口径固化、**数值仍 `NOT_RUN`**；
  `T6-STALE_LIMIT` = 200ms，标注**阶段4/5/6 同一常量**。
- **`C4` 语义同步**：由「全部 PENDING_APPROVAL」改为「**不得存在 PENDING，且每项有批准记录索引**」；
  新增 `verification/approval_regression.py` 反向自测（副本内注入 `PENDING_APPROVAL` → C4 必须 FAIL；
  基线 ALL_PASS），实测 `baseline [0, PASS] / injected [1, FAIL]`，并作为 claim `S6A-C7`。
- **新 RunId**：S6-A `s6a_g0_20261023_r11`、S6-B `s6b_core_20261023_r06`（**未**就地改写 r10/r05；旧轮次保留并登记取代）。
- **两段式重新冻结（本轮）**：F5 = 交付内容（本提交）、G5 = 自证记录（F5 为主体）+ 传输克隆自证；
  tag `stage6-freeze-20261023-r4` 打在 G5；旧 tag（r1/r2/r3 与两个 per-profile tag）保留不动。
  四条硬条件：① 两份附录由冻结工具可复现、计数正确且不得存在 PENDING ② 传输克隆 `--commit F5` 双侧全绿
  ③ `--commit G5` 双侧全绿 ④ 不引用未入库的 `tmp/` 产物作为套件结论。
- **边界（照批准记录 §3）**：本批准不等于 G4/G5 通过；`T6-A03` 数值 `NOT_RUN`（待阶段4 实测帧周期 P，不得填造）；
  G3 板测未做；集成（6-D）待阶段4/5 接口冻结；阶段7 暂不开工作树。
- **冻结后纪律**：提交 G5 后停止写 w6（含 STATE）。

## 批次 C 三项开放缺口（本轮未做，如实登记；不得当通过凭据）

- ① 陈旧 `fresh_selfcheck_pair.json` 记录（上一轮 r10 入库为 FAILED；本轮 r11/r06 已重新生成）；
- ② 套件两条必 FAIL 例对**真实 run-dir** 跑 `claim_verify` ⇒ 跑套件会改写冻结附录（应改为仅临时副本）；
- ③ 套件 `skipped` 曾计 `AS_EXPECTED`（fail-open）⇒ 应改为 fail-closed，并把套件产物直接入库。

## 11 字段交接行（2026-10-23 04:20）

任务=`S6-A v1.7（r08）第 7 轮复评 BLK-r07-1/N-r07-1..6 收尾 + S6-B r03 修 acquisition_id 与 action_records 两阻断` | 负责人=`DSH 阶段6 总控 stage6-lead3` | 工作树/分支=`D:\codex-worktrees\w6` / `stage6-interact-prep` | 起始提交=`d8bc70e43572a8e44ddcd4b3489166e28a1c6151`（本阶段开工基线；本轮修订基线 `bdcf896`） | 允许修改范围=`w6 工作树内 docs/stage6/**、verification/s6_g0_selfcheck.py、verification/s6a_build_evidence.py、verification/s6a_rerun_legacy_failures.py、verification/s6a_r07_probe.py、verification/export_selfproof.py、src/stage6/**、verification/s6b_*.py、report/evidence/S6-A/s6a_g0_20261022_r07/**、report/evidence/S6-B/**、.codex/STATE.md` | 未提交改动归属=`S6-A r07 与 S6-B 修正随本轮提交；r01..r06 与 S6-B r01 证据不改写` | 让出声明=`未让出（w6 由本阶段总控独占）` | 心跳(UTC+8)=`2026-10-23 04:20` | 证据入口=`report/evidence/S6-A/s6a_g0_20261022_r08/`（17 项 ALL_PASS；判别力探针 8 例 + 历史口径对照 2 例；冻结自证见 export_selfproof.json）与 `report/evidence/S6-B/s6b_core_20261023_r02/`（23/23 PASS + F6 自证 ALL_SELF_PROVEN） | 恢复命令=`cd /d D:\codex-worktrees\w6 && python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261022_r07/hand_computed_cases.json --upstream report/evidence/S6-A/s6a_g0_20261022_r07/upstream_bindings.json --out tmp/6/S6-A/s6a_g0_20261022_r07/resume.json --project-root D:/codex-worktrees/w6 --evidence-dir D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r07 --manifest D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r07/delivery_manifest.json --state .codex/STATE.md` | 状态/下一接手方=`S6-A r08 + S6-B r03 DELIVERED_PENDING_REVIEW；1839766 = CANDIDATE_FREEZE（未冻结），工作区修正双侧已全绿、待终审后一次性提交（未自称通过）/ 项目总控派 Reviewer 复评`

## 环境与恢复要点

- Python `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe`（3.12.10）；git 2.56.0.windows.2；`TEMP/TMP=D:\tmp`。
- `index.lock` 路径由 `git rev-parse --git-path index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/w6/index.lock`；失联判定须「心跳超时 + 无重型进程 + 无 index.lock」三者同时成立。
- 恢复/重跑证据一律写新 RunId 到 `tmp/`；**不得**覆盖 r01..r04 的任何证据；不得在正式测试集上调整任何阈值。
- 工作树换行约定：MD/JSON 为 CRLF、`.py`/STATE 为 LF（`core.autocrlf=true`）；写回时保持，避免整文件差异与清单哈希漂移。