# S6-B / S6-C 修正版 r02 独立复审报告

- 复审角色：独立 Reviewer（S6-B/S6-C 修正版 r02），只读审查
- 工作树：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**被审提交 `87a6bdc9951b9fed1baf5dad85a88db288ecda6a`**（链路 `43f7995`(r01) → `bdcf896`(S6-A r07) → `87a6bdc`）
- 审查开始/结束时 `git status --porcelain` 均为空，HEAD 始终 `87a6bdc`；审查期间**未在被审工作树写入任何文件**
- 隔离验证目录：`D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\`（`iso/` 为完整只读副本；`iso/tmp/review_inj/` 为注入工作区；自证导出的 TEMP/TMP 被重定向到 `selftmp*/`）
- 环境：Python 3.12.10（`locale.getpreferredencoding()=cp936`）、git 2.56.0.windows.2、UTC+8
- 结论：**CHANGES_REQUIRED**（2 项阻断 + 10 项非阻断）。BLK-1 **已关闭**（M4 可达性/覆盖声明经我独立复现成立）；N-03/N-06/N-07/N-09 已关闭；N-02/N-10 部分；**N-01/N-04/N-05/N-08 未关闭**（其中 N-05 的 D7 声明与实现相反、N-04 声明的字段未进入交付证据，故列为阻断）。

## 1. 被审版本绑定（SHA-256 实测，与 `delivery_manifest.json` 声明一致）

| 文件 | SHA-256（87a6bdc） | 相对 r01 |
|---|---|---|
| `src/stage6/s6_core.py` | `ab75b0740a6d8ce34d951dcff16690c9f6c2b7b75777dd29f2347d94ec937d80` | 变 |
| `src/stage6/s6_actions.py` | `1875440dc0f93bbea4cbe196c7e1a719a5120d3add0feb9677262e5f0ac4783f` | 变 |
| `src/stage6/s6_params.py` | `d1438a5db0df6fad653956b993b2cd08f7fdfcf0640e49c26871e6c9976d74ea` | 变 |
| `verification/s6b_run_cases.py` | `8babda4d568580048a0b036ee0a8050859e27c0325bfeea42b0ea504a1deb282` | 变 |
| `verification/s6b_probe.py` | `6f6621ddc7979f2c46d1797ff7cfe76e4922d8e36b5b24d15c88591fe50120fe` | 变 |
| `verification/s6b_build_evidence.py` | `eae9b950319697e4f23facd864f2379b09f3e2124f59e32027737bf416eaeed1` | 变 |
| `verification/export_selfproof.py`（F6 新 `--s6b-run`） | `ebeb36a6700d257c3eb941a85c3bcc4f70d44f094c82b74fb1abfad546813fa1` | 变（新功能） |
| `docs/stage6/s6a_stage6_g0_behavior_v1.json`（S6-A r07，输入） | `d8b1ea2d5d7e547da7e98c373bc25bc53accf82153c79a4846611e299caa8b14` | 变（v1.6） |
| `docs/stage6/s6b_frozen_interface_v1.json` | `b654fcb157c5722c4a4bebac996cc48e2d56c7be1b0e081b89765963f27e83e9` | **未变（N-01 未修）** |
| `…/s6b_core_20261023_r02/cases/build_case_matrix.py` | `1b55123784c243aed984413f3e224f5ca534207cdd86790e77b1e561ba20ba43` | 新增（随证据提交） |
| `…/s6b_core_20261023_r02/cases/case_matrix.json` | `c2c57627ac011ad5438be9bf3cbcdca9ade02dac2d9aed08908ad9ba19ff7456` | 新增 |

证据包自校验：`delivery_manifest.json` **53 条**绑定全部存在且哈希复算一致（0 缺失、0 失配）；无"盘上有但未声明"的文件（除清单自身，按约定不声明自己）；`hashes_sha256.txt` **42 条**全部复算一致。

## 2. 真实命令与退出码（全部实测）

| # | 命令（`<iso>` = 隔离副本根） | 退出码 | 备注 |
|---|---|---|---|
| 1 | `<py> -B <iso>/verification/s6b_run_cases.py --project-root <iso> --run-dir …/s6b_core_20261023_r02` | **0** | 23/23 PASS；`run_report.json` + 23 个 JSONL 与提交版**逐字节相同（24/24）**；耗时 140 ms（复现第二次 98 ms） |
| 2 | `<py> -B <iso>/verification/s6b_probe.py --project-root <iso> --run-dir …` | **0** | 4 探针：baseline 0 / expected_tampered **2** / wrong_semantics **1** / threshold_tampered **1** |
| 3 | `check_stage_delivery.py --mode inputs --project-root <iso>` | **0** | CHECKS_OK；stdout 与 `check_inputs_mode_output.txt` 内容逐字节相同（仅提交版末尾多 CRLF） |
| 4 | `check_stage_delivery.py --mode evidence --project-root <iso>` | **0** | CHECKS_OK；同上与 `check_evidence_mode_output.txt` 一致 |
| 5 | 注入 `T6-S01=900 ms`（隔离副本行为表）→ 驱动 | **1** | 133 项断言失败、16 条用例失败 → 阈值确实读 JSON，未写死 |
| 6 | 注入"改一个用例"（`score 0.90→0.31`，阈值内）| **2** | `用例文件在冻结后被修改：expected_freeze.json.cases_file_sha256 与当前不一致——拒绝运行` |
| 7 | 注入"只改用例文案"（description） | **2** | 同上（N-09 已按用例文件整体哈希把关） |
| 8 | 删除必需参数 `T6-03` / `T6-A03` / `T6-S02` | **2 / 2 / 2** | 均 `ParamError: 缺少核心必需参数：[…]` → 24 项存在性强制的声明成立 |
| 9 | 行为表 `artifact_version` 改 `S6A-G0-v1.5` | **2** | `参数装载失败：ParamError: artifact_version 不符：期望 'S6A-G0-v1.6'…` |
| 10 | N-07 旧行为注入（`NO_HAND` 携带 detections 静默忽略） | **1** | 仅 `C6b-no-hand-with-detections` FAIL，3 项断言；注入后按字节还原一致 |
| 11 | N-03 注入：把一条用例 `matrix_class` 改成未映射值 | **1** | `用例 … 的 matrix_class 未映射到 CDX 类别` |
| 12 | N-03 注入：删掉一条 `CDX_CLASS_MAPPING` 条目 | **1** | 构建器拒发（断言有效） |
| 13 | N-03 基线：隔离副本内原样重跑 `build_case_matrix.py` | **0** | 重新生成的 `case_matrix.json` 与提交版**规范化后完全一致**（仅 `run_id` 因目录名不同） |
| 14 | F6 自证：`export_selfproof.py --s6b-run … --worktree-snapshot` | **0** | `ALL_SELF_PROVEN`，四项退出码 `[0,0,0,0]`；与提交版 `export_selfproof.json` **逐字段一致** |
| 15 | F6 自证：`export_selfproof.py --commit 87a6bdc --commit 43f7995 --s6b-run …` | **1** | `87a6bdc → SELF_PROVEN [0,0,0,0]`；`43f7995 → NOT_SELF_PROVEN [0,2,2,2]`（负对照有效） |
| 16 | 反例：12 帧"仅换行不同 + 1 字节非换行不同"分别喂 `align_by_manifest_hashes` / `normalize_line_endings` | **0** | 换行口径**会**对齐；1 字节非换行差异**登记不打补丁**（`unresolved` / `content_differs`），字节未变 |
| 17 | 自构造序列 + 逐帧轨迹（M4 可达性、acquisition_id、D8） | **0** | 见 §3、§4 |

## 3. BLK-1 关闭核验（M4 可达并计入覆盖）——**成立**

- **声明一致性**：`reachability_notes.json`（3 条 note：B16 不可达、**M4 可达并计入覆盖**、M7 构造不可达）、`limitations_not_executed.json.reachability_not_counted_as_coverage`（**仅** B16 S_DEDUP + M7）与 `reachability_counted=["M4…"]`、`s6b_run_summary.md` 第 43 行、`delivery_manifest.json.limitations` 四处口径**一致**。`checked` 字段对 B16 由阈值（`a02_ns < k01_ns`）动态派生。
- **我自己复现 M4**：自构造"5 帧高分 + 2 帧 `score=0.28`"序列 → 轨迹 `f2 M1`、**`f7 M4`**；证据包 `logs/C4-jitter-reset.jsonl` 同为 `f2 M1`、**`f7 M4`**（reason「抖动容忍耗尽且候选停留 ≥ T6-S04（M10 未命中）」）。逐帧轨迹显示 `score=0.28/0.10` 经 §8 第 1 条**维持优先**仍被选中 → `TARGET_CONTINUES` 成立 → `t_last_target_continues` 每帧刷新、`continues_false_streak=0` → M10 永不先命中。**声明的机制（`TARGET_CONTINUES` 不含 `score ≥ T6-P02` → 刷新锚点、miss_streak 不增）与实测一致**。
- **稳健性反例**：把"维持优先"也加 `T6-P01` 门（对 §8 第 4 条的另一种读法）后重跑 → `C4-jitter-reset` 仍 PASS、仍 `M4@f7`。即 M4 可达性不依赖该歧义读法。
- 唯一保留意见（**非阻断**）：该机制实际依赖"维持优先绕过 `T6-P01` 选择门"这一实现事实（`_select` 的 continuing 分支不设分数门），而 §8 第 4 条"全部框低于 `T6-P01` → 无目标"可被反向解读；`reachability_notes.json` 未点明这一前提。建议在 note 中加一句。

## 4. N-01..N-10 逐条

| 编号 | 结论 | 核查要点与实测 |
|---|---|---|
| N-01 版本统一 v1.6 | **未关闭** | 核心/参数/摘要/清单/接口说明均已 v1.6；但 4 处仍写旧版：`docs/stage6/s6b_frozen_interface_v1.json:8` `status_note`（"v1.4"）与 `:50-51` `contract.s6a_contract_version="S6A-G0-v1.4"`/`s6a_review_status="r04…"`（该文件哈希与 r01 完全相同，说明未动）；**随证据提交**的 `cases/case_matrix.json:6` `"contract_version":"S6A-G0-v1.4"`、`:154` `expected_derivation_note`（"行为表 v1.4"）与 `cases/build_case_matrix.py:2/:436/:443`；`src/stage6/s6_core.py:511` docstring"按 v1.4 求值序"。其中 `case_matrix.json`/`s6b_frozen_interface_v1.json` 正是 r01 N-01 点名的位置。 |
| N-02 计数由报告派生 | **部分** | `s6b_run_summary.md` 的条数/类计数确由 `report['case_count']`、`class_counter` 派生（23 条与 18 个 `matrix_class` 行正确）；但 `verification/s6b_probe.py:77` 与 `probe_summary.json:10` 仍写 **"未改动：21 例全部通过"**（同文件 `stdout_tail` 为 `case_count: 23`），即 r01 N-02 点名的位置未改。 |
| N-03 覆盖由用例派生+断言 | **关闭** | `build_case_matrix.py:420-429` 由 `cases` 迭代派生 `coverage`，三重断言（未映射类 / 某 CDX 类为空 / 计数不符）实测**均可使构建失败**（注入 #11/#12 exit 1）；11 类全部非空、23 条不重不漏；`C9c-30fps-later-of` 已计入（归"时间等于阈值、前后 1 个计时单位"）。交付证据含构建器源码，隔离副本重跑产物与提交版规范化一致。 |
| N-04 动作记录与常量登记 | **未关闭（列阻断）** | 见 §5 BLK-r02-2。 |
| N-05 acquisition_id 规则 | **未关闭（列阻断）** | 见 §5 BLK-r02-1。 |
| N-06 24 项必须 | **关闭** | `REQUIRED_PARAMETER_IDS` 恰 24 项且与行为表 24 项 id 集合**完全相同**；删除 `T6-03`/`T6-A03`/`T6-S02` 实测均 exit 2（r01 的非必需项 `T6-A03` 现已强制）。 |
| N-07 NO_HAND 携带 detections | **关闭** | 实现计 `E_FRAME_INVALID` + `invalid` + `no_hand_with_detections`、不计 `no_hand_frames`；新增用例 `C6b-no-hand-with-detections`（expected 三项计数）；旧行为注入 → 仅 C6b FAIL、3 项断言 → **断言有判别力**。 |
| N-08 IDLE 不判 M10 的说明 | **未关闭（非阻断）** | `decision_notes.D8` 已写，但前提失实：实测"1 帧选中 + 4 次 E_TICK"下 `state=IDLE` 且 `current_target=SET` 持续到 800 ms（>L02=300 ms）仍不判 M10 → **IDLE 确实会保留目标**（D8 称"IDLE 不保留 current_target…故该分支不会出现"为假）。行为偏差（规格 M10 为"任意有目标状态"）已被登记，但登记理由错误。 |
| N-09 运行时校验用例文件哈希 | **关闭** | 驱动运行前同时校验 `cases_file_sha256`（含 `cases_file` 身份字段）与逐例 expected；改一个用例（含只改文案）→ **exit 2 拒运行**，且发生在状态机运行之前。 |
| N-10 source_commit | **部分** | 构建器用 `git rev-parse HEAD`（动态）；提交值 `bdcf896…` 是 `87a6bdc` 的**直接父提交**（`merge-base --is-ancestor` 成立），`delivery_manifest.limitations` 如实写明"为本次构建时的 HEAD"。措辞问题见 §6 NB-05。 |

## 5. 阻断项

**BLK-r02-1｜N-05 未关闭：`D7` 的 acquisition_id 规则与实现相反，B11/B15 的 `acquisition_id` 无法成立**

- 位置：`src/stage6/s6_core.py:85-87`（`decision_notes.D7`）、`src/stage6/s6_core.py:599-613`（`_transition`）、`src/stage6/s6_core.py:447-452`（仅目标切换递增）；证据 `report/evidence/S6-B/s6b_core_20261023_r02/run_report.json`+`logs/*.jsonl`（`acquisition_id` 大小写敏感出现 **0 次**）。
- 问题：D7 声明"`acquisition_id` 只在**结束一次获取**时递增——M11（丢失确认→IDLE）、M4（抖动超时→IDLE）、M8（会话/重启复位）与目标切换（D3）"。实测 `_transition` 对 M11/M4/M8 **不递增**，只有目标切换（D3）递增、`_init_state`（RESET）归零：
  - `C3-lost-then-reappear`（M11 路径）两次获取、两次触发 → `action_request.acquisition_id = 0, 0`（**同一 id**）；
  - `C5-target-jump`（目标切换）→ `1`（符合 D3）；
  - "M4 结束获取后再获取"自构造序列 → 新获取触发仍为 `0`。
- 影响：B11 `must_log=["新的 acquisition_id"]` 与 B15 `must_log=["acquisition_id","触发计数"]` 在本实现与交付证据中**均不成立**；"一次获取一次触发"的溯源无法用该字段区分两次获取；集成方按 D7 假设会得到错误结论。N-05 的两条关闭路径（M11 递增 / 显式声明并落盘）**都未走通**，且新增了一条与实现相反的规范性说明。
- 依据：上表 §4 与 §2 #17 的实测输出（`adv_verify.py` 输出）；`s6_core.py:606-613` 代码；证据中 `acquisition_id` 0 次。
- 关闭条件：(a) 在 `_transition` 的 `M11/M4/M8` 分支递增 `acquisition_id`（或在 D7 与 B11/B15 口径中明确改为"仅目标切换递增"并同步改 S6-A 侧 `must_log`，取得 G0 同意）；(b) 让 `acquisition_id` 真正进入交付证据（与 BLK-r02-2 同一改动）；(c) 重生成证据包与哈希/清单。

**BLK-r02-2｜N-04 未关闭：声明的 `action_records` 未进入交付证据（4 个必需字段与 4 个输出事件 0 次）**

- 位置：`verification/s6b_run_cases.py:132-150`（`run_case` 产出 `action_records`）与 `:269-287`（`observed` 未含 `action_records`）；`src/stage6/s6_core.py:668-708`（`note_action_ack` 回执不含动作身份）；证据 `run_report.json` + 23 个 `logs/*.jsonl`。
- 问题：大小写敏感统计：`action_type` **0/0**、`target_id` **0/0**、`acquisition_id` **0/0**、`t_trigger_ns` **0/0**；`ACTION_SUBMITTED` 仅 1 次（出现在一句 reason 文本里）、`ACTION_EFFECTIVE/FAILED/UNOBSERVED` **0 次**。`run_case` 计算了完整 `action_records`（`s6_actions.py:92-111` 的 record 确含上述字段），但 `main()` 序列化 `observed` 时丢弃。提交信息"action records carry acquisition_id"与 D9/`s6_actions.py:98` 注释"动作记录含获取级 id"在**交付证据层面不成立**。
- 影响：B01（`target_id`）、B11/B15（`acquisition_id`）、B02/B28 的 `must_log` 仍只能靠间接核对；集成排障时无法仅凭证据判定"提交了哪个动作/哪个目标/第几次获取"。N-04 的关闭条件（"report 增列 `action_records` 或逐帧日志补记"）未满足。
- 依据：§2 #1 的复跑与 §4 的大小写敏感统计（`run_report.json` 与 `logs/` 均 0）；`sample step log keys` 中无 `action_type/target_id/acquisition_id/t_trigger_ns`。
- 关闭条件：`observed` 增列 `action_records`（或在 `action_ack` 日志补 `action_type/target_id/acquisition_id/t_trigger_ns`，并保留 `action_id`/`submit_result`/`effective_result` 与失败/未观察计数），并重生成证据与哈希/清单；同时删除或启用 `s6_core.py:43-46` / `s6_actions.py:22-25` 的 8 个未使用 `OUT_*` 常量。

## 6. 非阻断项

| 编号 | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| NB-01 | 同 N-01 的 4 处（接口 JSON、随证据提交的 `case_matrix.json`/`build_case_matrix.py`、`s6_core.py:511`） | 仍标 `S6A-G0-v1.4`/项 | 阅读者会把 v1.6 语义误认 v1.4；交付证据内部版本口径不自洽 | 实测 grep | 统一 v1.6，或登记版本映射 |
| NB-02 | `verification/s6b_probe.py:77`、`probe_summary.json:10` | baseline note 仍写"21 例"而实际 23 条 | 自述与实测数目不符（r01 N-02 同点） | `stdout_tail` 为 `case_count: 23` | 改为动态派生（引用驱动输出） |
| NB-03 | `s6_core.py:88-90`（D8） | D8 前提失实：IDLE 会保留 `current_target`（实测 800 ms 不判 M10） | 登记理由错误，读者不会回归该路径 | §2 #17 轨迹 | 改写 D8 为"IDLE 在 M1 前确实可能持有目标，但按 v1.6 求值序 P2 只在 CANDIDATE/STABLE/TRIGGERED/COOLDOWN 判 M10"，或与规格对齐 |
| NB-04 | `s6_core.py:91`（D9） | D9 称"在 `limitations_not_executed.json` 登记为未实现"，实际该文件**无此条目** | 声明与产物不符（登记只在代码注释里） | `transition_candidates`/`S_CONFLICT_RESOLVED` 全仓仅 1 处命中（D9 自身） | 在 `limitations_not_executed.json` 增加"未实现项"条目或修正 D9 措辞 |
| NB-05 | `delivery_manifest.json.limitations[0]` | 写"**三项**退出码见本包 `export_selfproof.json`"，但该文件是 worktree 快照的**四项**结果，且不含交付提交 `87a6bdc` 的导出自证 | 读者会以为包里已有交付提交的自证 | 提交版 `export_selfproof.json` 只有 `worktree_snapshot` subject；我复跑该提交得 `[0,0,0,0]` | 改为"四项"并（建议）在提交后补一份 `--commit 87a6bdc` 的自证报告 |
| NB-06 | `s6b_run_summary.md:16` | 表内第三列仍为占位"实测（下方回填）"，两个 `check_stage_delivery` 的真实退出码未回填 | 摘要自相矛盾（"下方"没有） | 摘要全文 | 回填 0/0，或改为指向 `delivery_manifest.checks` |
| NB-07 | `verification/s6b_probe.py:27-36`、`s6b_build_evidence.py:64-68` | 子进程 stdout 解码固定 `utf-8`，而子进程（驱动）中文输出按宿主 locale（本机 cp936）编码 | 在 cp936 环境下 `probe_expected_tampered_stdout.txt`/`probe_summary.json.stdout_tail` 变成 U+FFFD 乱码；设 `PYTHONUTF8=1` 后 5 个产物与提交版**逐字节一致**（我实测） | 两次探针复跑对比 | 在 `run_driver` 传 `env={**os.environ,"PYTHONUTF8":"1"}` 或对子进程强制 `PYTHONIOENCODING` |
| NB-08 | `s6_core.py:656-663`、`s6_params.py:181`、`export_selfproof.py:248` 等 | 零散：request 字典 `acquisition_id` **重复键**两次；`self.class_action_map = self.class_action_map` 自赋值；`OUT_*` 常量双份定义从未使用；`state_declared_s6b_dir_files_in_commit` 实为"实际文件数"（不解析 STATE），与字段名/注释不符；runbook 类名与 CDX §4 原文"前后1个计时单位"差一空格；`C9c` 归入"时间等于阈值"类属语义拉伸 | 可读性/命名准确性 | 代码与 `CDX-20261022-012` §4 | 清理或改名 |
| NB-09 | `reachability_notes.json` consequence（"S6-A 侧…已同步修正（r07）"） | 部分失实：`s6a_stage6_g0_behavior_v1.json` 仍有 3 处旧断言（`reachability_note`、`reachability.consequence`"M4/T6-S04 与 M7 不得计入行为覆盖声明"、`parameter_notes.T6-S04`"M4 不可达…本行不得计入覆盖"），`S6A_stage6_g0_behavior_spec_v1.md:376` limitations 仍写"M4 在当前草案下不可达（U6-12）" | 跨文件口径冲突（S6-A 侧） | grep 实测 | 转 S6-A 责任方修 4 处；S6-B 侧措辞改为"M4 的 `reachability.transitions.M4`/U6-12 已修正" |
| NB-10 | F6 规则口径 | S6-B 模式下自证**故意跳过** S6-A r07 的 `inputs`/`evidence` 复算（仅保留 STATE 存在性自检），且 S6-A r07 清单绑定的 `verification/export_selfproof.py`、`.codex/STATE.md` 在本提交内已改字节（自证如实登记 `unresolved` 但**不失败**） | F6"自检+inputs+evidence 三项 exit 0"在 S6-B 轮次实际降为"S6-A STATE 自检 + S6-B 三项"；S6-A r07 清单在本提交内不再自洽 | 我复跑 `--worktree-snapshot`，`newline_alignment.unresolved` 两项；`s6b_frozen…`/S6-A 清单哈希实测失配 | 如实性已满足（已登记）；建议在 `export_selfproof.md`/清单里显式写明"本轮不再复算 S6-A 旧轮次清单哈希"这一**降级口径** |

## 7. 无回归 / 无夸大

- 24 项参数值与 `approval_status=PENDING_APPROVAL` 相对 r01 **完全未变**（逐项 diff 为空；`all_parameters_pending_approval=true`）；行为表 JSON 仅因 S6-A r07 升版而哈希改变。
- `expected` 仍由 `build_case_matrix.py` **独立推导**（只 import `json/pathlib`，不 import/不运行状态机；隔离副本重跑产物与提交版规范化一致）→ 无回填痕迹。我手算复核了 `C1/C3/C4/C6b/C9-s01-equal/C9-s01-minus-1ns/C9c/C10/C11` 的帧时刻与计数，与期望一致。
- 结论范围限定到位：`run_report.scope_statement`、`limitations_not_executed.replay_scope`、`delivery_manifest.limitations`、`probe_summary.scope_statement`、`s6b_run_summary.md` 均限定"注入输入 + 虚拟单调时钟"并显式排除摄像头/HDMI/板上/≥30 分钟真实回放。
- 禁止声明扫描：未发现任何"已审查/审查通过/已通过/G0·G2·G4·G5 通过"式自夸；命中项全部是反向声明（"不代表…独立审查通过/验收通过"）。
- 声明存在但缺失的文件：**无**（53 条绑定全部存在，且盘上无未声明文件）。
- 用例数 22(r01)→23(r02，新增 `C6b`) 与"23 条/11 类"表述一致；`runbook_matrix_coverage` 11 类非空、23 条不重不漏。

## 8. F6 自证工具新 `--s6b-run` 模式核验

- 代码：`export_selfproof.py:202-230` —— `s6b_rel` 非空时**不再**跑 S6-A 的两个检查器，改跑 4 项：S6-A 自检（不传 `--manifest`，仅 STATE 存在性）+ S6-B 驱动 + S6-B `inputs` + S6-B `evidence`，全部用 `tree`（导出副本）内的文件与工具。`prepare_commit_repo` 用 `git clone --shared` + `checkout <rev>`，确为"该提交内"文件。
- 我复跑 `87a6bdc`：**SELF_PROVEN，四项 `[0,0,0,0]`**；`43f7995`（r01）：**NOT_SELF_PROVEN `[0,2,2,2]`**（自检 0；S6-B 驱动/两个检查器因该提交内不存在 `s6b_core_20261023_r02` 而 exit 2）→ 工具**非空转**，负对照有效。
- 与提交版比对：`worktree_snapshot` 的 `label/artifact_version/run_id/evidence_dir/evidence_dir_file_count(39)/state_declared_s6b_dir_files_in_commit(84)/selfcheck_status(ALL_PASS)/verdict/newline_alignment` **逐字段一致**，四项 `stdout_tail` 亦一致；`84` 复算无误（`report/evidence/S6-B` 下 r01 40 + r02 44 = 84）。
- "只选换行口径、不改内容"反例（§2 #16）：仅换行不同 → 对齐（唯一"修正"）；**1 字节非换行差异 → 登记 `unresolved`/`content_differs` 且字节不变**。符合声明。

## 9. 工作区漂移清单

- 被审工作树 `w6`：审查前后 `git status --porcelain` **均为空**，HEAD 始终 `87a6bdc`；我未在其中写入任何文件（自证运行的临时目录被 `TEMP/TMP` 重定向到 `tmp/review/S6B_r02_20261023_r01/selftmp*`）。
- `87a6bdc` 未触碰 r01 证据目录（`git show --name-only | grep s6b_core_20261023_r01` = 0 条）；提交只含 `.codex/STATE.md`、`src/stage6/*`、`verification/{s6b_*,export_selfproof}.py` 与 r02 证据。
- 我在隔离目录内对 `iso/src/stage6/s6_core.py` 做过两次注入，均**按字节还原并复核一致**（N-07 旧行为、维持优先加 P01 门）。
- 隔离产物：`iso/`、`inj/`(实际为 `iso/tmp/review_inj/`)、`selfproof_worktree.{json,md}`、`selfproof_commits.{json,md}`、`run_injections.py`、`inject_n03.py`、`inject_n07.py`、`inject_p01floor.py`、`adv_verify.py`、`adv_m4.py`、`test_d8.py`、`test_newline_only.py`、`verify_evidence.py`、`rebuild_matrix.py`、`cmp_dir.py` 及各自 `*_out.txt`。

## 10. 结论与范围

- 结论：**CHANGES_REQUIRED**。BLK-1（M4 可达性/覆盖）**已关闭**并经我独立复现；N-03/N-06/N-07/N-09 关闭；N-02/N-10 部分关闭；**N-01/N-04/N-05/N-08 未关闭**，其中 N-05（D7 与实现相反）、N-04（声明的字段未进证据）列为阻断。
- 被审代码语义在本轮未发现新的行为级阻断缺陷：23 条用例可逐字节复跑、探针 4 项、两个交付检查器、四类注入、1 个旧行为反例、1 个稳健性反例全部符合预期；实现未发现阈值写死（`T6-S01=900 ms` 注入 → exit 1）。
- 本结论**仅覆盖 S6-B/S6-C r02**（实现 + 确定性用例矩阵 + 证据包 + F6 自证扩展），**不代表 G0/G2/G3/G4/G5**，不含实物/板卡/摄像头/HDMI/≥30 分钟回放，也不代表 S6-A 规格本身的正确性；NB-09 的 4 处 S6-A 侧残留需转该轮责任方。