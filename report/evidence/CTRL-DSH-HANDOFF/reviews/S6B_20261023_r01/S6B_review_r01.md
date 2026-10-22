# S6-B / S6-C 实现轮独立复审报告（r01）

- 复审角色：独立 Reviewer（S6-B/S6-C 实现轮），只读审查
- 工作树：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，被审提交 `43f7995`（父 `04ea58e` = S6-A r06）
- 审查开始时工作树干净（`git status --porcelain` 空），审查期间未在被审工作树写入任何文件
- 隔离验证目录：`D:\FPGA_Competition\tmp\review\S6B_20261023_r01\`（含 `iso/` 完整只读副本）
- 环境：Python 3.12.10；git 2.56.0.windows.2；UTC+8
- 结论：**CHANGES_REQUIRED**（1 项阻断，10 项非阻断；被审代码语义经 38 项自构造对抗序列复现全部符合）

## 1. 被审版本绑定（SHA-256 实测）

| 文件 | SHA-256 |
|---|---|
| `src/stage6/s6_core.py` | `b0d5fd0a657b24ef4d14d144542bdb0f153c6933fd3416a8ea27fb7d9cf9f97a` |
| `src/stage6/s6_actions.py` | `789e509c10a965442c43f474a08756d67ecb08a5c737d4564f8728e123ff24c5` |
| `src/stage6/s6_params.py` | `4e5aff5ff5810601ee845d440d0f5a3de005b1295dc71b051b56e7ce566a65d2` |
| `verification/s6b_run_cases.py` | `a2f285c51e4203fd7da9051bcbcf2feee67c34e682d56d80754cbaabf3e8c809` |
| `verification/s6b_probe.py` | `68af9bfe7b8ba15e10763a164f7f905e38eb225a55858f4a0ffcd8ff3542e1ba` |
| `verification/s6b_build_evidence.py` | `5021dbe4dddcc7cc226d038930bbd8162bb6d6d0833d7c5d32123d609488ce74` |
| `docs/stage6/s6b_frozen_interface_v1.json` | `b654fcb157c5722c4a4bebac996cc48e2d56c7be1b0e081b89765963f27e83e9` |
| `docs/stage6/s6a_stage6_g0_behavior_v1.json`（冻结输入） | `32ec34cdb2e776f68edded39636de83e0e73b730b7301b483c4e1e28967a1337` |

证据包自校验：`hashes_sha256.txt` 38 条条目全部复算一致；`delivery_manifest.json` 49 条文件绑定存在且哈希一致；`inputs_manifest.json` 1 条一致。

## 2. 真实命令与退出码（全部实测）

| # | 命令（隔离副本内，`<iso>` = `tmp/review/S6B_20261023_r01/iso`） | 退出码 | 备注 |
|---|---|---|---|
| 1 | `python -B verification/s6b_run_cases.py --project-root <iso> --run-dir report/evidence/S6-B/s6b_core_20261023_r01` | **0** | 22/22 PASS；`run_report.json` 与 22 个 JSONL 与提交版**逐字节相同**；耗时 0.11 s |
| 2 | `python -B verification/s6b_probe.py --project-root <iso> --run-dir ...` | **0** | 4 探针：baseline 0 / expected_tampered **2** / wrong_semantics **1** / threshold_tampered **1** |
| 3 | `python -B verification/check_stage_delivery.py --mode inputs --manifest .../inputs_manifest.json --project-root D:/codex-worktrees/w6` | **0** | CHECKS_OK；输出与 `check_inputs_mode_output.txt` 逐字节相同（检查器无写操作，运行后 `git status` 仍为空） |
| 4 | `python -B verification/check_stage_delivery.py --mode evidence --manifest .../delivery_manifest.json --project-root D:/codex-worktrees/w6` | **0** | CHECKS_OK；输出与 `check_evidence_mode_output.txt` 逐字节相同 |
| 5 | 注入 `T6-S02=4`（原 6）后运行 | **1** | 28 项断言失败；C1 观测 `window_complete_ns` 500000000→**300000000**、`submitted_at_frames` [7]→**[5]** |
| 6 | 注入 `T6-S01=100` 后运行 | **1** | 6 项失败（C9c / C9-s01-minus-1ns / C11-global-gate） |
| 7 | 注入 `T6-P02=0.7` 后运行 | **1** | 9 项失败（C5-held-priority 等） |
| 8 | 必需参数 `T6-S02` / 非必需 `T6-A03` / 指标 `T6-03` → `APPROVED` | **2 / 2 / 2** | 全部拒载：`ParamError: 参数 X 的 approval_status 不是 PENDING_APPROVAL` |
| 9 | 顶层 `status` 改为 `G0_PACKET_APPROVED` | **2** | 拒载（只接受待批准口径） |
| 10 | 删除必需参数 `T6-S02` / 删除非必需参数 `T6-A03` | **2 / 0** | 必需项删除拒载；**非必需项删除仍 22/22 PASS**（见 N-06） |
| 11 | 篡改 `expected` 后运行（冻结门） | **2** | `预期在冻结后被修改：C1-fist-stable …… 拒绝运行`（真实拒绝，未运行状态机） |
| 12 | 仅篡改用例输入（score 0.90→0.31，阈值内；expected 未改） | **0** | 未被冻结门拦截，行为等价（见 N-09）；改为 0.90→0.10（低于 P01）→ **1** 由断言捕获 |
| 13 | 旧口径注入 A2：`window_complete_ns` 改记在第 `T6-S02` 个 WINDOW_MATCH 帧（M3 取较晚不变） | **1** | C9c FAIL：`window_complete_ns 预期 233100000，实际 166500000`；C1、C9-s01-equal 仍 PASS；还原后 **0** |
| 14 | 自构造对抗序列脚本 `adv_scenarios.py`（38 项断言） | **0** | 38/38 PASS（明细见第 5 节） |

## 3. 逐项核查结论

### 3.1 核心语义对齐 v1.5（逐条）
- **H-4（NO_HAND 不推进 `WINDOW_MATCH`、零框不得完成窗口）**：成立。NO_HAND 帧计入 `no_hand_frames` 与时间，`window_match_count` 从不因 NO_HAND 增加（我构造 1 匹配 + 9 零框：峰值仍为 1）；"5 匹配 + 3 零框 + 3 匹配"仍停留在 CANDIDATE、无 M3、无动作。零框帧按 §9/B08 作为"窗口推进但不满足 WINDOW_MATCH"的中断累计抖动并在 >`T6-J01` 时重置窗口证据——与规格一致（不是 H-4 违规）。
- **H-10（冷却全局门）**：成立且是"任何状态/任何获取"。我构造"目标 A 触发 → 丢失 → 目标 B 在 K01 内重新达标（M3 已进 STABLE）"：**零次提交**，记录 `S_COOLDOWN`；门开启那一帧若为非推进帧（TIMEOUT）**不触发**；门开启后的下一条推进帧才触发（第 28 帧）。K01±1 ns 边界：`t_last_submit+999999999` 的推进帧被抑制、`+1000000000` 恰好触发（含等号）。
- **M3 只按 `WINDOW_MATCH`、完成帧=计数与时长"取较晚"**：成立。30 fps（P=33.3 ms）下第 6 帧仅 166.5 ms<200 ms，完成帧为第 8 帧 **233100000 ns**、第 9 帧触发；把完成时刻改回旧口径后 C9c 必 FAIL（见第 2 节 #13），断言有判别力。
- **M10 只按 `TARGET_CONTINUES`**：成立。score=0.28（<P01/<P02）但几何完全相同的 3 帧经 §8 迟滞维持：距上次 WINDOW_MATCH 已达 300 ms（=L02）仍**不**确认丢失（`miss_streak=0`）。同时 `L02±1 ns`：`+299999999` 不丢失、`+300000000` 恰好 M10。
- **STABLE 本次获取内锁存**：成立。门未结束时低分帧（含不满足 WINDOW_MATCH 的帧）长时间停留 STABLE，不退回 CANDIDATE、不出现 M4；门开启后无需重新累积窗口即可触发。
- **一次获取一次触发**：成立。同一获取内（M15/M9 路径）不再触发；第二次只发生在丢失→重获的新获取且门已结束（C3：第 7、19 帧两次，`action_id` ACT-0001/ACT-0002）。
- **求值序 P1→P5**：与规格一致（P1 M2/M13 → P2 M10 → P3 当前状态 → P4 M1 → P5 M12）。我构造了"同一帧 M4 与 M10 同时满足"的序列（dwell=500 ms、miss_streak=5、抖动耗尽）：实测取 **M10**、状态 LOST，与 §4"M10 优先"一致。
- **M5 的"本帧必须为窗口推进帧"**：成立。门开启时刻分别投喂 stale / 重复 frame_id / 倒序 frame_id / TIMEOUT：**均不触发**且状态停留 STABLE，下一条真正的推进帧才触发（对应 N-r04-01 / HC-30）。
- **异常窗口与恢复**：滑动窗口 3 条内异常数 <3 不进恢复态；第 3 个异常 → M2；恢复态清理目标与窗口证据；恢复期再次异常 → M13（自环）且计数起点重置（此后仅 4 条合法结果不恢复）；连续 5 条合法结果 → M12→IDLE。

### 3.2 阈值不写死
- 注入 `T6-S02=4`：结果随 JSON 改变（C1 完成时刻 500→300 ms、触发帧 7→5）且用例失败 → 阈值确实来自 JSON。
- 静态扫描 `s6_core.py`：仅有结构性字面量（`/2.0`、`0.0/1.0` 归一化边界、`len(box)!=4`），**无阶段6 阈值字面量**；所有阈值均经 `ParamPack.threshold_bundle()`（纳秒/帧/float 三口径）。
- 装载强制：把任一在表参数（含非核心参数 `T6-A03`、指标 `T6-03`）改为 `APPROVED` 均**拒载（exit 2）**；顶层 status 非待批准口径拒载。
- 缺口：`REQUIRED_PARAMETER_IDS` 仅 20 项，删除 `T6-A03` 仍能装载并 PASS，"强制 24 项"只对"在表参数的批准状态"成立（N-06）。

### 3.3 动作层
- 幂等"设置具名状态"：`ACTION_SUBMITTED`(2)/`ACTION_EFFECTIVE`(2)/`S_DEDUP`(1)/可见状态变化(1) 与预期一致；同一具名状态二次提交 `visible_state_change=false`。
- `submit`/`effective` 二分：`fail` 不产生 ACTION_SUBMITTED 且不更新 `t_last_submit`（随后重试成功，`action_failed=1`、成功 1 次）；`unobserved` 单列（`action_unobserved=1`、`action_effective=0`），不虚报成功。
- `action_id` 与来源帧：`ACT-0001/0002` 与 `submitted_at_frames` 一致；被抑制的重复尝试不分配新 `action_id`。
- `T6-A02` 去重与 `S_DEDUP` 不可达声明**自洽**：动作层直接调用时 `t+100 ms` 命中 S_DEDUP、`t+500 ms`（恰 A02）不再抑制；而核心驱动路径下两次提交最短间隔 = `K01=1000 ms > A02=500 ms`，故 S_DEDUP 分支确实不可达（分支仍可用，非"未实现"）。

### 3.4 用例与 expected 独立性
- 22 条用例覆盖 CDX-20261022-012 §4 全部 11 类（`runbook_matrix_coverage` 11 类、映射 21 条，**C9c 未被任何类收录**，见 N-03）。
- expected 独立性：`build_case_matrix.py`（位于 `w6/tmp/6/S6-B/`，被 gitignore，02:32）只 import `json/pathlib`，**不 import 也不运行状态机**，expected 以字面量人工推导写入；`expected_derivation_note` 与 `limitations.expected_corrections` 记录了人工修正过程。我抽样手算复现了 C1/C3/C4/C6/C7/C8/C9-s01-equal/C9-s01-minus-1ns/C9c/C10 的 expected，全部与规格独立推导一致（未发现回填痕迹）。
- 冻结门：篡改 expected → **exit 2 拒绝运行**（真实）；`expected_freeze.json` 的 `cases_file_sha256`/`behavior_json_sha256` 我复算一致，但驱动运行时只校验逐例 expected，不校验输入哈希（N-09）。
- C9c 判别力：旧口径注入 → C9c 必 FAIL（166500000 vs 233100000）；C1/C9-s01-equal 不受影响，说明该断言精确对应 r06 的"取较晚"口径。

### 3.5 证据与声明
- `run_report.json` 22/22 **可复现**：隔离副本复跑退出码 0，`run_report.json` 与 22 个 JSONL 与提交版逐字节相同。
- 4 探针实测退出码与声明一致（0/2/1/1）；`delivery_manifest.checks` 四项真实退出码均为 **0**（我独立重跑并逐字节比对捕获文件）。
- 无"声明存在但缺失"的文件：证据包 17 个顶层文件 + `cases/` + `logs/`（22 个 JSONL），清单内所有文件存在且哈希一致。
- `reachability_notes.json` 的 M4 条目**无依据且与同包自证据矛盾**（阻断项 BLK-1）；B16 S_DEDUP、M7 条目自洽。
- 结论范围声明明确且到位：`run_report.scope_statement`、`limitations.replay_scope`、`delivery_manifest.limitations`、`probe_summary.scope_statement` 均限定"注入输入 + 虚拟单调时钟"，并显式排除摄像头/HDMI/板卡/≥30 分钟真实回放。

### 3.6 无越界/无夸大
- 24 项参数仍全部 `PENDING_APPROVAL`（`params_snapshot.all_parameters_pending_approval=true`，我直接读 JSON 复核）。
- 未发现 S6-B 自称"已审查/已通过/G0 通过"；全文扫描仅命中 S6-A r05 的 PASS（正确署名）与检查器 `check_statuses.PASS`（机器检查项）。
- `docs/stage6/s6b_frozen_interface_v1.json` 状态为 `S6B_IMPLEMENTATION_BASELINE_PENDING_REVIEW`，并写明"不是新的接口冻结、不代表 G0/G2/G4/G5"——**如实**；但其 `contract.s6a_contract_version` 与 `status_note` 仍写 `S6A-G0-v1.4`（N-01）。

## 4. 问题清单

### 阻断

**BLK-1｜M4 可达性/覆盖声明与同包自证据矛盾（证据失实）**
- 位置：`report/evidence/S6-B/s6b_core_20261023_r01/reachability_notes.json`（`M4-candidate-timeout` 条目）、`limitations_not_executed.json`（`reachability_not_counted_as_coverage`）、`s6b_run_summary.md` 第 43 行、提交 `43f7995` 提交信息末行。
- 问题：声明"`T6-S04`(500 ms) ≥ `T6-L02`(300 ms) → 候选停留达 S04 前 M10 已先命中 → M4 在草案参数下不可达/不计入覆盖"；但**同包的 `C4-jitter-reset` 用例 expected 为 `transitions:["M1","M4"]`、实测日志 `M4@f7`（reason「抖动容忍耗尽且候选停留 ≥ T6-S04（M10 未命中）」）**，且该用例被 `runbook_matrix_coverage` 的"短暂抖动"类收录、在运行摘要覆盖清单中列为"短暂抖动：1 条"。
- 影响：证据包对可达性与覆盖的陈述**自相矛盾且失实**；以"不可达"为依据的 U6-12（删除 M4/`T6-S04` 或改 `T6-S04<T6-L02`）会删掉一条**实际可达且已被用例覆盖**的迁移；"不计入覆盖"的覆盖边界声明同样失效。
- 依据：规格 §3 谓词定义（`TARGET_CONTINUES` **不含** `score≥T6-P02`）与 §4 M4 行；`logs/C4-jitter-reset.jsonl`；`cases/case_matrix.json` C4 expected；我构造的 S8（同帧 M4/M10 竞争取 M10）与 S9（低分几何连续不判丢失）复现了同一机制。
- 关闭条件：(a) 重新推导可达性（补上"低分/位移导致的 WINDOW_MATCH 中断但 TARGET_CONTINUES 成立 → L02 锚点持续刷新、miss_streak 不增"的路径），在 `reachability_notes.json`/`limitations_not_executed.json`/`s6b_run_summary.md` 中把 M4 标为**可达并计入覆盖**（或给出 M4 不可达成立所需的额外前提，如"仅当 TARGET_CONTINUES 同时停止"）；(b) 同步修正 U6-12/规格 M4 行（属 S6-A 侧，需转 S6-A 责任方，不在本次评价范围）；(c) 证据包相关文件与哈希/清单重生成（新 RunId 或与总控约定同 RunId 重建），并保证 `hashes_sha256.txt`/`delivery_manifest.json` 复算一致。

### 非阻断

| 编号 | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| N-01 | `src/stage6/s6_core.py`（docstring、`decision_notes` D4/D6 等 6 处）、`src/stage6/s6_params.py`（模块 docstring 只到 r05/v1.4）、`case_matrix.json.expected_derivation_note`、`reachability_notes.json.derived_from`、`s6b_run_summary.md` 标题、`docs/stage6/s6b_frozen_interface_v1.json`（`contract.s6a_contract_version`、`status_note`） | 版本标注仍写 `S6A-G0-v1.4`/r05，而实际契约是 `S6A-G0-v1.5`（r06，`EXPECTED_CONTRACT_VERSION` 与 JSON 均为 v1.5） | 阅读者会把 r06 的"窗口完成取较晚"口径误认成 v1.4 语义；接口文件与上游版本不自洽 | JSON `artifact_version=S6A-G0-v1.5`；规格头部"修订记录（v1.5 / r06）"；`s6_core.py:59` | 统一改为 `S6A-G0-v1.5`/r06，或在接口文件登记版本映射 |
| N-02 | `probe_summary.json` baseline note、`s6b_run_summary.md` 第 42 行、`verification/s6b_build_evidence.py:214` | 文案写"21 例/21 条"，实际 22 条 | 低（自述与实测数目不符） | `run_stdout.txt`、`run_report.case_count=22` | 改为 22 |
| N-03 | `cases/case_matrix.json.runbook_matrix_coverage` | 11 类仅映射 21 条，`C9c-30fps-later-of` 未被任何类收录 | 类↔用例机器可读映射与"22 条/11 类"表述不一致 | 我复算：映射 21、唯一 21、未映射 `C9c-30fps-later-of` | 把 C9c 归入"时间边界"类（或低 FPS 类）并同步 |
| N-04 | 证据 `logs/*.jsonl` + `run_report.json`；`src/stage6/s6_core.py`（`OUT_*`/`SUP_CONFLICT` 常量定义但从未使用） | 规格 §3/§5 要求记录的输出事件与字段未落盘：`ACTION_SUBMITTED/EFFECTIVE/FAILED/UNOBSERVED` 只出现在文字里（证据中 ACTION_FAILED/UNOBSERVED=0 次）；`action_type`/`target_id`/`acquisition_id`/`t_trigger_ns` 在证据中 **0 次出现**（run_report 不含 `action_records`）；B09 的"IoU/位移依据"与 B10 的"帧条件 or 时间条件"分类未记录；§4 要求的 `transition_candidates`/`S_CONFLICT_RESOLVED` 未实现（0 次出现） | H-2/B01/B02 的"必须记录"只能间接核对；集成排障时无法仅凭证据判定提交了哪个动作/目标 | `grep -ro` 统计；`run_report.cases[].observed` 键列表；`note_action_ack` 返回的日志字段 | 逐帧日志补记动作事件与 `action_type/target_id/trigger_frame_id/t_trigger`（或 report 增列 `action_records`）；补 B09/B10 依据字段；`S_CONFLICT_RESOLVED` 实现或登记为不适用 |
| N-05 | `src/stage6/s6_core.py`（`_transition` M11 不递增 `acquisition_id`；仅目标切换时递增） | 丢失确认后重获的新获取与旧获取共用同一 `acquisition_id`（C3 两次获取均为 0） | 无法用 `acquisition_id` 区分两次获取；B11/B15 的"新获取的 `acquisition_id`"记录不成立（触发一次行为本身正确） | C3 行动记录生成路径；`_on_advancing_with_dets` 的 `M11` 分支 | M11 时递增，或显式声明该字段语义并落盘 |
| N-06 | `src/stage6/s6_params.py` `REQUIRED_PARAMETER_IDS`（20 项） | 删除非必需参数 `T6-A03` 仍装载并 22/22 PASS（实测 exit 0）；"强制 24 项"只对在表参数的 `approval_status` 成立 | 参数清单被删项时实现不会察觉，声明与强制范围不一致 | 我的注入 #10；JSON 24 项 | 24 项全部纳入存在性强制，或改写声明为"对在表参数强制批准状态" |
| N-07 | `src/stage6/s6_core.py` `_validate`/`step` | `state=NO_HAND` 却携带 `detections` 时静默忽略（实测 `invalid=0`、`no_hand_frames=1`），未按 §11.3"字段不自洽"计非法 | 上游结果不自洽时被当作合法零框，不产生异常计数 | §11.3；我的实测 | 明确声明"由调用方保证 state 与 boxes 自洽"（写入 deviation/D 系列）或加自洽校验 |
| N-08 | `src/stage6/s6_core.py` `_evaluate` P2 状态集合 | `IDLE`（已选出 `current_target`）不做 M10 求值：实测距锚点 900 ms（>L02）仍停留 IDLE；规格 M10 写作"任意有目标状态" | 影响有限（C01=2 帧即可离开 IDLE），但属未声明的解释取舍 | §4 M10 行；我的实测 | 在 `decision_notes` 显式声明"IDLE 不算有目标状态"，或与规格对齐 |
| N-09 | `verification/s6b_run_cases.py`（只校验逐例 expected） | `expected_freeze.json` 记录 `cases_file_sha256` 且我复算一致，但运行时不校验；篡改用例输入（阈值内）仍 exit 0 | 输入篡改仅由断言兜底（行为改变型篡改 exit 1 已被捕获）；属稳健性观察 | 我的注入 #12 | 运行时同时校验 `cases_file_sha256`（可选） |
| N-10 | `delivery_manifest.json.source_commit` | 指向 `6560b69…`，该提交**不在被审谱系**（非 `43f7995`、非其父 `04ea58e`），且其树与 HEAD 树不同 | 字段无法用于定位被审代码（其余 49 条文件哈希与当前文件一致，内容绑定仍有效） | `git cat-file`/`git merge-base --is-ancestor` 返回 NO；树哈希 `7477bdf…` vs `3269c78…` | 改写为被审提交哈希，或注明其为"构建时 HEAD（随后被 amend）" |

## 5. 自构造对抗序列（38 项，全部 PASS）

脚本：`tmp/review/S6B_20261023_r01/adv_scenarios.py`（独立实现驱动，不复用 `s6b_run_cases.py` 的断言器），结果：`adv_scenarios_result.json`。期望值全部由规格与草案参数人工推导。

覆盖：S1 H-4 零框（1 匹配+9 零框、5+3+3 混合）、S2 H-10 全局门（切目标冷却内零提交+S_COOLDOWN、锁存不退回、门开启帧为 TIMEOUT 不触发、门后首个推进帧触发、K01±1 ns）、S3 L02±1 ns、S4 门开启时刻的 stale/重复/倒序不触发+后续推进帧触发、S5 异常滑动窗口（2<3 不进恢复/第 3 个进 M2/恢复期清理/M13 重置计数/5 条 M12）、S6 30 fps 233.1 ms、S7 动作层（幂等、A02 界、不虚报、action_id/来源帧、S_DEDUP 不可达推导）、S8 同帧 M4/M10 取 M10、S9 "M10 只按 TARGET_CONTINUES"（低分几何连续 300 ms 不判丢失）。

## 6. 工作区漂移清单

- 被审工作树 `w6`：审查前后 `git status --porcelain` 均为空，HEAD 始终 `43f7995`；我未在其中写入任何文件。
- 存在的**已忽略**产物（非本轮我产生，mtime 02:13–02:33，早于审查开始 02:41）：`src/stage6/__pycache__/`、`verification/__pycache__/`、`tmp/6/S6-A/*`、`tmp/6/S6-B/*`（含 `build_case_matrix.py`、`patch_*.py`、`verify_s6b.py`、`s6b_core_20261023_r01/`）。均为 gitignore 覆盖，不影响被审内容。
- 建议（非阻断）：`tmp/6/S6-B/build_case_matrix.py` 是 expected 的独立推导产物，建议随证据包提交或至少登记哈希，便于后续轮次复核 H-7（当前仅存在于被忽略目录，我按只读方式核验其不 import 状态机）。
- 隔离副本：`iso/` 内曾为判别力注入临时改动 `s6_core.py`，已用字节级还原并复核与 `w6` 原件**字节一致**；被审工作树未受影响。

## 7. 结论与范围

- 结论：**CHANGES_REQUIRED**。被审代码（`s6_core.py`/`s6_actions.py`/`s6_params.py`）语义经 38 项自构造序列与 22 条用例复现，未发现行为级阻断缺陷；阻断项在**证据与声明**（BLK-1），另 10 项非阻断。
- 本轮结论**仅覆盖 S6-B/S6-C**（实现 + 确定性用例矩阵 + 证据包），不代表 G0/G2/G3/G4/G5，不含实物/板卡/摄像头/HDMI，不代表 S6-A 规格本身的正确性（另有第 6 轮评审）；BLK-1 的根因涉及 S6-A 的 `reachability.M4`/U6-12 行，需转该轮处理。

附：审查过程脚本与原始输出位于 `D:\FPGA_Competition\tmp\review\S6B_20261023_r01\`（`adv_scenarios.py`、`adv_scenarios_result.json`、`adv_tamper.py`、`adv_discriminate*.py`、`case_expectations.txt`、`key_case_events.txt`、`rc_inputs.json`、`rc_evidence.json`、`iso/`）。