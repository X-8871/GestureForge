# 阶段6 状态入口（w6 / stage6-interact-prep）

更新：2026-10-23 03:36（UTC+8）。按 `AGENTS.md` 与主 STATE 恢复；**本文件是阶段6 工作树专属状态**，主状态 `D:\FPGA_Competition\.codex\STATE.md` 只读。阶段技术事实以本文件与本树证据为准。

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

## S6-B / S6-C（task-6 第二部分，已产出待复评）

- 实现（按 v1.4 契约重写旧 WIP）：`src/stage6/s6_actions.py`（动作层：幂等提交、success/fail/unobserved 二分、`action_id`/来源帧、`T6-A02` 去重）、`src/stage6/s6_core.py`（纯核心：事件入、状态/动作请求/日志出，不读摄像头/墙钟/HDMI）、`src/stage6/s6_params.py`（阈值只从行为表 JSON 读入并强制 `PENDING_APPROVAL`，核心内无阈值字面量）。
- 关键语义落地：H-4（`NO_HAND` 推进时间/结果计数但不推进 WINDOW_MATCH、零框不得完成窗口）、H-10（冷却全局门；门在 STABLE 未开时记 `S_COOLDOWN` 并保持锁存）、M3 只按 `WINDOW_MATCH`、M10 只按 `TARGET_CONTINUES`、STABLE 本次获取内锁存（退出仅 M2/M10/M5）、一次获取一次触发、`window_complete` 与 `W_min` 口径、异常窗口/恢复（M2/M13/M12，恢复期不计窗口）。
- 6-C 矩阵：`verification/s6b_run_cases.py`（虚拟单调时钟 + JSON 用例 + 逐帧 JSONL 日志 + 断言 + 非零退出；运行前校验 expected 冻结哈希）+ S6-B 证据目录内的 cases/case_matrix.json（**22 条 / 覆盖 CDX-012 §4 全部 11 类**，expected 由行为表 v1.5 人工推导）。
- **N-r05-04 同步**：核心的 `window_complete_ns` 改为在 **M3 成立帧**（计数与时长取较晚）写入，不再在第 `T6-S02` 个 `WINDOW_MATCH` 帧写入；新增 30fps 用例 `C9c-30fps-later-of` 断言 `window_complete_ns=233100000`（旧逻辑会给 166.5 ms 帧）。
- 结果：22/22 用例 PASS（r01）。**r02（task-9 修正轮）**：BLK-1(a) 把 M4 修正为**可达并计入覆盖**（`TARGET_CONTINUES` 不含 `score ≥ T6-P02` → 低分中断不推进 `miss_streak`，M10 不先命中；用例 C4-jitter-reset 实测 M4@f7）；N-01 版本统一 v1.6；N-02 计数写实；N-03 11 类覆盖映射由实际用例派生（含 C9c）；N-04 动作记录含 acquisition_id 并登记未实现的 `transition_candidates`/`S_CONFLICT_RESOLVED`；N-05 acquisition_id 规则写入 decision_notes；N-06 `REQUIRED_PARAMETER_IDS` 扩到全部 24 项；N-07 `NO_HAND` 带 detections 计非法（新增用例 C6b）；N-08 IDLE 有目标时不求值 M10 写入 decision_notes；N-09 运行前校验 `cases_file_sha256`（冻结点后改用例即拒运行）；N-10 `source_commit` 动态取 HEAD 并由自证工具绑定交付提交。新 RunId `report/evidence/S6-B/s6b_core_20261023_r02/`：**23/23 用例 PASS**（覆盖 11 类）、探针 4/4 符合预期、两个检查器 exit 0，且 **F6 导出自证 ALL_SELF_PROVEN [0,0,0,0]**（S6-A 自检 STATE + S6-B 驱动 + S6-B inputs/evidence）。
- 不可达项（不计入覆盖）：B16 `S_DEDUP`（`T6-A02`500 ms < `T6-K01`1000 ms）、M4/`T6-S04`（U6-12）、M7（构造上）；见 `reachability_notes.json`。
- `docs/stage6/s6b_frozen_interface_v1.json` 状态改为 `S6B_IMPLEMENTATION_BASELINE_PENDING_REVIEW`（只读 2A 常量，不是新冻结）。

## 未决与阻塞

- **待 Wong/G0 确认**：`U6-16`（STABLE 锁存口径）；`U6-12`（`T6-S04`/M4 可达性）；`U6-13`（阶段4 实测帧周期 `P_meas`，`T6-A03` `NOT_RUN`）；`U6-14`（逐类 UX 可见时长）；`U6-15`（`A_DISPLAY_STATE`）；`U6-01..U6-11`。
- **BLOCKED**：阶段4/阶段5 接口未冻结；阶段4 实测帧周期未取得；真摄像头验收延期；独立 Reviewer 无法由本会话创建（委派深度 0，由项目总控安排）。
- **S6-A 状态**：v1.4/r05 为 `PENDING_REVIEW`（r04 已 PASS、r05 只关非阻断项）；是否再复评由项目总控决定；不得自称已审查/已通过。

## 证据入口（r07）

- 本轮：`report/evidence/S6-A/s6a_g0_20261022_r07/`（`delivery_manifest.json`、`inputs_manifest.json`、`hashes_sha256.txt`、`selfcheck_result.json`、`selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`、`selfcheck_old_package_failure.json`、`selfcheck_old_package_failure_stdout.txt`、`selfcheck_r02_blk1_failure.json`、`selfcheck_r02_blk1_failure_stdout.txt`、`selfcheck_r03_failure.json`、`selfcheck_r03_failure_stdout.txt`、`selfcheck_r04_failure.json`、`selfcheck_r04_failure_stdout.txt`、`old_package_under_test.json`、`r02_package_under_test.json`、`r03_package_under_test.json`、`r04_package_under_test.json`、`probe_summary.json`、`probe_baseline_no_injection_stdout.txt`、`probe_m5_window_advance_removed_stdout.txt`、`probe_empty_predicates_used_stdout.txt`、`probe_b13_predicates_used_added_stdout.txt`、`probe_b07_old_wording_stdout.txt`、`probe_case_timeout_frame_action_stdout.txt`、`probe_case_span_wrong_stdout.txt`、`probe_case_out_of_sequence_index_stdout.txt`、`probe_historical_model_check_r05_stdout.txt`、`probe_historical_model_check_r06_stdout.txt`、`fix_record.json`、`fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`、`S6A_run_summary.md`；export_selfproof.json 与 export_selfproof.md 由自证工具在清单生成前写入，故由 `delivery_manifest.json` 声明而不在此列举——若在此声明，提交前的工作区快照自证会因该文件尚未生成而 C11 失败）。
- 上一轮：`report/evidence/S6-A/s6a_g0_20261022_r06/`；更早 r01..r05 均保持原样（**RunId 证据不可覆盖**）。
- 冻结自证：`python -B verification/export_selfproof.py --project-root D:/codex-worktrees/w6 --commit <rev>`（导出该提交后自检 + inputs + evidence 三项必须 exit 0）。
- 规格：`docs/stage6/`；自检：`verification/s6_g0_selfcheck.py`（C1–C17）；清单构建器：`verification/s6a_build_evidence.py`；旧包重跑：`verification/s6a_rerun_legacy_failures.py`；判别力探针：`verification/s6a_r07_probe.py`；冻结自证：`verification/export_selfproof.py`；缓存：`tmp/6/**`（不入库）。

## 11 字段交接行（2026-10-23 03:36）

任务=`S6-A v1.6（r07）第 6 轮复评 F1–F11 收尾（含 F6 冻结自证规则）+ BLK-1 的 M4 可达性修正；随后 S6-B 按 task-9 修正` | 负责人=`DSH 阶段6 总控 stage6-lead3` | 工作树/分支=`D:\codex-worktrees\w6` / `stage6-interact-prep` | 起始提交=`d8bc70e43572a8e44ddcd4b3489166e28a1c6151`（本阶段开工基线；本轮修订基线 `43f7995`） | 允许修改范围=`w6 工作树内 docs/stage6/**、verification/s6_g0_selfcheck.py、verification/s6a_build_evidence.py、verification/s6a_rerun_legacy_failures.py、verification/s6a_r07_probe.py、verification/export_selfproof.py、src/stage6/**、verification/s6b_*.py、report/evidence/S6-A/s6a_g0_20261022_r07/**、report/evidence/S6-B/**、.codex/STATE.md` | 未提交改动归属=`S6-A r07 与 S6-B 修正随本轮提交；r01..r06 与 S6-B r01 证据不改写` | 让出声明=`未让出（w6 由本阶段总控独占）` | 心跳(UTC+8)=`2026-10-23 03:36` | 证据入口=`report/evidence/S6-A/s6a_g0_20261022_r07/`（17 项 ALL_PASS；判别力探针 8 例 + 历史口径对照 2 例；冻结自证见 export_selfproof.json）与 `report/evidence/S6-B/s6b_core_20261023_r02/`（23/23 PASS + F6 自证 ALL_SELF_PROVEN） | 恢复命令=`cd /d D:\codex-worktrees\w6 && python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261022_r07/hand_computed_cases.json --upstream report/evidence/S6-A/s6a_g0_20261022_r07/upstream_bindings.json --out tmp/6/S6-A/s6a_g0_20261022_r07/resume.json --project-root D:/codex-worktrees/w6 --evidence-dir D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r07 --manifest D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r07/delivery_manifest.json --state .codex/STATE.md` | 状态/下一接手方=`S6-A r07（bdcf896）+ S6-B r02 修正 DELIVERED_PENDING_REVIEW（未自称通过）/ 项目总控派 Reviewer 复评`

## 环境与恢复要点

- Python `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe`（3.12.10）；git 2.56.0.windows.2；`TEMP/TMP=D:\tmp`。
- `index.lock` 路径由 `git rev-parse --git-path index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/w6/index.lock`；失联判定须「心跳超时 + 无重型进程 + 无 index.lock」三者同时成立。
- 恢复/重跑证据一律写新 RunId 到 `tmp/`；**不得**覆盖 r01..r04 的任何证据；不得在正式测试集上调整任何阈值。
- 工作树换行约定：MD/JSON 为 CRLF、`.py`/STATE 为 LF（`core.autocrlf=true`）；写回时保持，避免整文件差异与清单哈希漂移。