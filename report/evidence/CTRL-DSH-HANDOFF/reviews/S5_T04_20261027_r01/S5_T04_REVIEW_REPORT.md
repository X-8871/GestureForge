# S5-T04 阶段5 离线冻结 —— 独立复审报告（r01）

- 复审方：DSH 独立 Reviewer（rev-s5），只读
- 复审时间：2026-10-27 19:13–19:33 UTC+8
- 被审工作树：`D:\codex-worktrees\w5`（分支 `stage5-display-prep`），**未写入**
- 冻结前基线：`2a2d2cc01cd31444a1a854115d99a31cbe8499bf`
- 被审冻结提交：`26b743901b4ec76107ca2cd6a010337a5ae40bf2`
- 最终 HEAD：`2797cc3e072a8dfa1287f3e54cd606b46de16f99`
- 附注 tag：`stage5-offline-freeze-20261027`（annotated tag 对象 `cd57a53` → `26b7439`）
- 复审产物：`D:\tmp\review\S5_T04_20261027_r01\`（日志 `logs/**`、隔离副本 `work/**`）

## 结论

**PASS —— 无阻断项。** 冻结字节集真实、可复现、覆盖口径与文书一致；校验器判别力经评审方独立注入验证为真（非恒真）；"不主张"边界诚实。
另有 **4 项非阻断** 问题与 1 项文档漂移，建议下一轮重冻结时一并修正（不影响本次离线冻结基线可用性）。

| # | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| F1 | `verification/verify_stage5_frozen_set.py` 契约（第 16–17 行 docstring）vs 实现（第 132–141 行） | docstring 声称"路径越界 ⇒ exit 2"，实现只做 `root / path` 拼接、**无 containment 检查**：repo scope 成员的 `../x` 或绝对路径会解析到 `--root` 之外并被接受（评审实测 exit **0**） | "fail-closed 含路径越界"的表述夸大；被篡改的 `frozen_set.json` 可把校验指向树外字节。本次 r05 冻结集内**无**越界路径（评审扫描 `..`/绝对路径 = 0），且冻结集由 Git 提交 + `delivery_manifest` 哈希双重绑定，实际风险受限 | 评审注入：`path_escape_relative` exit 0（契约期望 2）、`path_escape_absolute` exit 0；`logs/injections.json` | 校验器对 repo scope 增加"必须相对路径且 resolved 必须位于 root 内"检查（或修正 docstring 措辞），重跑注入自测并重建清单；属下一轮重冻结范围。若项目把该条当契约属性，需在 G5 前关闭 |
| F2 | `report/evidence/S5-T04/s5_freeze_20261027_r05/README.md` §6（第 78 行） | 写"`git archive` 导出后，在导出副本内复跑冻结集校验器与 `check_stage_delivery`"；但包内 F6 证据（`results_f6export.json` / `console/f6b_*.txt`）实际只在 **独立 checkout（有 `.git`）** 内跑 checker，归档导出副本内只跑校验器 | 读者可能误以为 checker 可在无 `.git` 的归档副本通过。评审实测：归档副本内 checker exit **2**（"project-root 不是可核验的 Git 仓库根目录"）；不构成假 PASS（包内 console 如实分列 A/B） | `logs/f6a_evidence.txt`（exit 2）、`logs/f6b_evidence.txt`（exit 0）、包内 `console/f6b_checkout_verify_and_checker.txt` | 下一轮把 §6 改为"归档导出内跑校验器；独立检出内跑校验器 + checker"，或在包内追加一行说明；不改被冻结成员 |
| F3 | `frozen_set.json` → `superseded_runs`（成员字段） | 只登记 `r00_runner_crash`、`r01` 两条；实际被取代的 `r02_incomplete_builder_path`、`r03`、`r04` 的取代原因只出现在 `STATE.md`、tag 消息与提交消息中 | 机器可读留痕不完整；人读可恢复，但脚本无法从冻结集得知 r02–r04 的取代关系 | `logs/coverage.txt`（superseded_runs 全文）、`STATE.md` 第 50 行 | 下一轮 `build_stage5_frozen_set.py` 的 `superseded_runs` 补齐 r02/r03/r04（含原因）；本次不强改已冻结成员 |
| F4 | `report/evidence/S5-T04/s5_freeze_f6export_20261027_r00_crlf_fail/results_f6export.json`、`…_r00b_tracked_dirs_fail/results_f6export.json` | 两目录内部 `run_id` 均为 `s5_freeze_f6export_20261027_r01`（与目录名不符）；且 r00 中 `checker_checks_ok=true` 而 `checker_exit_code=2`（驱动器用字符串包含判断 `CHECKS_OK` 的缺陷） | 读者可能误读为 r01 失败；不影响最终 F6 判定（最终判定要求 checker exit 0）。两目录 verdict 均为 `F6_SELFCHECK_FAIL`，目录名带 `_fail`，且该 RunId 硬编码缺陷已由提交 `e9ce522` 修复并在 STATE 登记 | `logs/*` 与上述文件；`git log` 显示各自仅 1 次提交（未改写） | 遵守"不改写被取代证据"纪律，不做内容修改；在 r05 包或下一轮 README 增加一条指认说明（"这两目录内部 run_id 是修复前默认路径缺陷的残留"） |
| F5 | `scripts/stage5_t04/build_stage5_frozen_set.py` 第 13 行 docstring | 写"证据包顶层目录登记为 `dir_digest`"，实际实现为 `file_set`（r05 冻结集 19 个目录成员全为 `file_set`，`dir_digest` 路径本次未被使用） | 纯注释漂移，无功能影响；`dir_digest` 分支在本冻结中未被数据覆盖 | `logs/analyze_frozen_set.txt`（by_kind: file 58 / file_set 19，无 dir_digest） | 下一轮修正注释；无需重冻结 |

> 说明：F1 是唯一涉及"校验器自身契约"的问题。鉴于（a）r05 冻结集内不存在越界路径（评审独立扫描为 0），（b）冻结集自身由 Git 提交与清单哈希绑定，（c）该校验器不是冻结集成员、可由下一轮重建清单后修正，本项判为**非阻断**，但建议在 G5 前关闭。

## 一、基线与提交（PASS）

| 检查 | 命令要点 | 真实退出码 | 结果 |
|---|---|---|---|
| 三提交存在且为 commit | `git cat-file -t 2a2d2cc / 26b7439 / 2797cc3` | 0 / 0 / 0 | 均 `commit` |
| 关系正确 | `git merge-base --is-ancestor 2a2d2cc 26b7439`；`… 26b7439 2797cc3` | 0 / 0 | 线性祖先链：`2a2d2cc → 26b7439 → 521e7f9 → 3575dc3 → 2797cc3` |
| tag 指向 | `git rev-parse stage5-offline-freeze-20261027^{commit}`；`git cat-file -t <tag>` | 0 / 0 | `26b7439…`；tag 对象 `cd57a53`（annotated） |
| 工作区干净 | `git --no-optional-locks status --porcelain -uall` | 0 | 空（含未跟踪项也为空） |
| 无 index.lock | `git rev-parse --git-path index.lock` + 存在性检查（并查 common dir） | ls 2（不存在） | `D:/FPGA_Competition/.git/worktrees/w5/index.lock` ABSENT；common dir 亦 ABSENT |
| 未 push | `git ls-remote origin refs/heads/main refs/tags/stage5-offline-freeze-20261027` | 0 | 远程只返回 `refs/heads/main`，**无该 tag**；本地无 remote-tracking tag 引用 |
| HEAD 之后无未申报改动 | `git diff --name-status 26b7439 2797cc3` | 0 | 仅 `.codex/STATE.md` + r05 包文书/清单 + 新增 F6 包，共 18 条；**冻结集 `frozen_set.json` blob 两侧同为 `11e1aeb`（逐字节相同）** |
| HEAD 上校验器可复现 | `verify_stage5_frozen_set.py --root w5 --frozen-set …/r05/frozen_set.json` | **0** | `FROZEN_SET_VERIFIED` 77/77 |

## 二、校验器判别力（评审方自建注入，PASS）

`--help` 实测：`--selftest SELFTEST` 需带值，且必须同时给 `--frozen-set`（未给 ⇒ exit 2）。

在**评审自己的隔离副本**（`git archive 26b7439` 全量导出，3207 文件，无 `.git`）内，先跑出 `FROZEN_SET_VERIFIED`（exit 0），再自行构造 19 组注入：

| # | 评审注入 | 观察退出码 | 契约期望 | 判定 |
|---|---|---|---|---|
| 1 | 干净基线 | 0 | 0 | PASS |
| 2 | 改 file 成员 1 字节 | **1** | 1 | PASS |
| 3 | 删 file 成员 | **2** | 2 | PASS |
| 4 | 改 file_set 内登记文件 1 字节 | **1** | 1 | PASS |
| 5 | 删 file_set 内登记文件 | **2** | 2 | PASS |
| 6 | file_set 目录内新增未登记文件 | 0 | 0（契约语义：只校验登记文件） | PASS（记录语义） |
| 7 | 只改冻结集里的期望 sha（文件不动） | **1** | 1 | PASS |
| 8 | 不给 `--frozen-set` | **2** | 2 | PASS |
| 9 | `--frozen-set` 不存在 | **2** | 2 | PASS |
| 10 | `--frozen-set` 指向目录 | **2** | 2 | PASS |
| 11 | 冻结集 JSON 损坏 | **2** | 2 | PASS |
| 12 | `--root` 不存在 | **2** | 2 | PASS |
| 13 | file 成员路径实际是目录 | **2** | 2 | PASS |
| 14 | 未知 kind | **2** | 2 | PASS |
| 15 | host 引用指向不存在路径 | **2** | 2 | PASS（证明 host 默认真校验、不是静默跳过） |
| 16 | 路径越界（`../` 相对） | **0** | 2 | **FAIL（F1）** |
| 17 | 路径越界（repo scope 绝对路径） | **0** | 2 | **FAIL（F1）** |
| 18 | `--skip-host-references` | 0，且逐条打印 9 条 SKIPPED | 0 / 9 | PASS |
| 19 | 复跑被审方 `--selftest` | 0，steps clean=0 / tamper=1 / missing=2 | 0/1/2 | PASS |

**判别力结论：真实，非恒真。** 内容篡改稳定给 1、结构/缺失稳定给 2、干净给 0；两处失配仅限其 docstring 承诺的"路径越界"维度。

## 三、覆盖真伪（PASS，无范围洞）

- 成员口径：**77 成员 = 58 `file` + 19 `file_set`**；分组 **14 / 3 / 44 / 7 / 9** 与文书、清单、tag 消息完全一致。
- 文件口径：`file` 成员 + `file_set` 逐件条目合计 **196**，与"覆盖 196 个已跟踪文件"一致。
- **评审独立重算全部 196 个文件哈希（33.72 MiB）**：0 不符、0 缺失（不是抽样——全量）。
- 范围洞核对：19 个 `file_set` 目录逐一与基线提交 `2a2d2cc` 下 `git ls-tree` 对照 ⇒ **missing=0、extra=0**（目录内所有已跟踪文件都被登记）。
- `docs/stage5`：基线跟踪 17 个文件，冻结 13 个；未登记 4 个（`S5T01_stage5_board_bringup_runbook.md`、`S5T02_onboard_dynamic_mapping_taskcard.md`、`S5_stage5_display_spec_draft.md`、`s5t01_injection_plan_example.json`），均被 `not_frozen` 的"草案/任务卡/历史入口"条目覆盖，**无无理由排除的定稿规格**。
- 离线实现：`scripts/stage5_t03` 25/25 已跟踪文件全部登记；`verification/` 侧 2 个几何参考/测试文件登记。校验器/构建器本身不属冻结成员，但由 `delivery_manifest.json`（`role=source`，哈希 `4e3456…`）与 Git 提交绑定（评审在 HEAD 上复核 25 条清单哈希 0 不符）——设计上有意避免自指，属可接受。
- 冻结集自身：`frozen_set.json` sha256 = `109254238e2aede8ab9005ed153e768e611c3ba325a5b1b75b312b415408b1bf`（与文书一致）；它不是自身成员（README §7 已明写）。
- **绑定核对**：`host::stage3_input_frame_full_bin` 登记 sha256 = `939fce22b7e86aa…`，与 `dbdf` 实际 `frame_full.bin` 逐字节一致，回放绑定 JSON 同样含 `939fce22…`；`host::wong_stale_200ms_approval_receipt` 登记 sha256 = `d8edb848…`，评审读原文确认其批准"跨阶段 `stale_age_limit` = 200ms"；冻结成员 `s5a_g0_ur3_decision_20261025_r01.{json,md}` 引用同一回执路径与 sha256，并明确 `runtime_measurement_status=NOT_RUN`。绑定成立。
- 可复现性：在独立检出（`26b7439`）内重跑构建器 ⇒ 77 成员、`members` 数组与已提交冻结集**逐字节相同**（仅 `baseline_commit`/`generated_utc8` 元数据不同）。

## 四、F6 自证独立复验（PASS）

| 步骤 | 评审自己的命令 | 真实退出码 | 结果 |
|---|---|---|---|
| A 归档导出 | `git -C w5 archive --format=tar 26b7439` → 我的目录解包（3207 文件，**无 `.git`**） | 0 | — |
| A 校验 | 归档副本内 `verify_stage5_frozen_set.py --root <arch> --frozen-set <arch>/…/frozen_set.json` | **0** | `FROZEN_SET_VERIFIED` 77/77 |
| A 检查器 | 同上副本 `check_stage_delivery --mode evidence` | **2** | `CHECKS_FAILED: project-root 不是可核验的 Git 仓库根目录`（符合预期；包内也未把 checker 记在 A 上，见 F2） |
| B 独立检出 | `git clone --shared --no-checkout w5 <dir>` → `git checkout --detach 26b7439`（全量检出，独立 `.git`，status 干净） | 0 / 0 | HEAD=26b7439 |
| B 校验 | 检出副本内校验器 | **0** | 77/77 |
| B 检查器（evidence） | `check_stage_delivery --mode evidence --project-root <checkout> --manifest <checkout>/…/delivery_manifest.json` | **0** | `CHECKS_OK` |
| B 检查器（inputs） | 同上 `--mode inputs` | **2** | `inputs 模式至少需要一个 role=input 的文件`；包内已如实登记为 `NOT_APPLICABLE`（未伪称通过） |
| 回归（归档副本） | 10 模块 unittest | **1** | 142 tests，**1 failure**：`test_existing_synthetic_evidence_untouched` 因该测试 `git diff <BASE_COMMIT>` 依赖 `.git`（归档无元数据）而失败 ⇒ 环境性，不是内容回归 |
| 回归（独立检出） | 同上 10 模块 | **0** | **Ran 142 / failures 0 / errors 0 / skipped 2，168.6 s**，含 `frames=106573` |
| 历史缺口 | `scripts.stage5_s5b|s5c` | **1** | **Ran 83 / failures 18 / 11.1 s**，与披露一致 |

## 五、回归复跑（PASS）

- 主套件：`Ran 142 tests in 168.639s`，`OK (skipped=2)`，exit 0；长跑模块实跑 **106,573 帧**（与 106,573 主张一致）。执行方留存为 167.307 s，量级一致。
- 复跑环境：独立 `--shared` 检出 + `--no-checkout` 后全量 checkout 到 `26b7439`，非 w5 工作树；`python -B`，未在 w5 落任何字节。
- 历史模块：83 项 / 18 失败 / exit 1 复现；冻结套件模块清单不含 s5a/s5b/s5c，未计入冻结回归。
- 说明：归档导出副本可跑校验器（通过），但不能完整跑套件（1 项依赖 `.git`）；若将来要求"仅凭归档复跑全套件"，需在复跑脚本内提供 Git 元数据或以独立检出为准（当前 README 恢复入口指向工作树，无此问题）。

## 六、边界诚实性（PASS）

- README §2 逐条九项"不主张"，§7 限制；`frozen_set.json` 有机器可读 `non_claims`；`results_freeze.json` 有 `not_run`；`STATE.md` 明写"不主张 G0–G5/板级/实物/实时"。
- 全文扫描未发现任何"板上通过/实物通过/G5 通过/实时已验证"类正面断言（唯一命中是"任何 G0/G1/G3/G4/G5 通过：不主张"这条否定句）。
- `task-27` 在 README §8.2、`results.not_run`、`STATE` 三处一致记为 **NOT_RUN**。
- 18 项历史失败在 README §4/§8 与 `console/legacy_suite_known_gap.txt` 披露，标注非门禁，且模块不在冻结回归清单。
- 上游局限（阶段3 `PARTIAL_OPEN`/`task-11 BLOCKED_NOT_RUN`/`TIMING-17`；阶段4 `complete_stage4_or_RGB_preprocess=NOT_CLAIMED`）只引用不改写。

## 七、留痕与取代（PASS，含 F3/F4 提示）

- 7 个失败/被取代目录全部存在且已提交：`r00_runner_crash`（10 文件，无清单，符合"运行器崩溃未产出清单"）、`r01`（16）、`r02_incomplete_builder_path`（3，仅 console，符合"未完成"）、`r03`（16）、`r04`（16）、`f6export_…_r00_crlf_fail`（9）、`…_r00b_tracked_dirs_fail`（9）。
- **未改写**：对上述 7 目录执行 `git log --diff-filter=MDR --all` ⇒ 空；每个目录仅 1 次"新增"提交，无后续修改/删除/改名。
- **旧 RunId 未被覆盖（提交内）**：r02 的 console 如实记录了构建器曾以默认 `--out` 覆盖 `r01/frozen_set.json`（写入值 sha `91f8d9…`）；但已提交的 r01 冻结集是原始 76 成员 blob `64c7b8a`（工作树 sha `7d593bb…`），在引入提交 `be0bf3d` 与 HEAD 上**同一 blob** ⇒ 覆盖在提交前已回退，事件由 r02 证据 + 修复提交 `b4cbb44` 保留。属"如实留痕"，不是静默覆盖。
- 取代原因与目录实际一致（r00 崩溃、r01 CRLF/`.gitattributes`、r02 默认 out 覆盖风险、r03 硬编码 RunId、r04 `__pycache__` 污染目录摘要；F6 前两轮 CRLF/目录跟踪失败），与 STATE 第 50 行描述一致。
- 仅 F3/F4 两处留痕一致性提示（非阻断，见上表）。

## 三问回答

1. **`26b7439` + `2797cc3` 能否作为阶段5 离线冻结基线？**
   **能。** `26b7439` 为被冻结字节的身份（tag 指向、工作区干净、77/77 全量哈希可复现、两路独立导出/检出 exit 0、构建器可复现 members）；`2797cc3` 只在其上追加 F6 证据、STATE 与 README 文字纠正，`frozen_set.json` 与所有冻结成员逐字节未变（HEAD 上校验器仍 exit 0）。建议下游引用"字节身份 = `26b7439`（tag）、文书身份 = `2797cc3`"，二者均不可变。
2. **"不主张"边界是否诚实？是。** 机器可读 `non_claims` + 文书写死九条 + `task-27 NOT_RUN` + 18 项失败披露且不计入门禁 + 无任何实物/板级正面断言；`UR-3` 明确 `runtime_measurement_status=NOT_RUN`。
3. **校验器判别力是否真实？是。** 评审独立构造 19 组注入，0/1/2 三态可区分且稳定；唯一与自身 docstring 不符的是"路径越界"未拦截（F1，非阻断，本次冻结集内无此路径）。

## 复审未覆盖 / 限制

- 未连接、未加载位流、未烧录、未操作任何硬件；未评价板级 B1–B10 与任何 G3/G4/G5。
- 未重跑被审方的冻结证据运行器本身（`run_stage5_freeze_evidence.py`），只独立复验其产物、校验器、套件、F6 两路与构建器可复现性。
- `scope=host` 引用在本机原路径解析（评审实测 9/9 匹配）；换机需 `--skip-host-references`，跳过项不得视为已验证（评审已实测其会逐条打印 9 条）。
- 未核查上游 w4/dbdf 历史结论的语义正确性，只核对其字节哈希与引用关系。
- 复审写入仅限 `D:\tmp\review\S5_T04_20261027_r01\`（约 1.1 GB：两套 275 MB 导出 + 日志）；w5 复审前后 `git status` 均为空、无 `index.lock`、HEAD/tag 未变。

## 评审日志索引（`D:\tmp\review\S5_T04_20261027_r01\logs\`）

`analyze_frozen_set.txt`（全量重算哈希）、`coverage.txt`（范围洞/清单绑定/绑定核对）、`injections.json` + `injections_console.txt`（19 组注入）、`verifier_help.txt`、`f6a_verify.txt` / `f6a_evidence.txt` / `f6a_inputs.txt`、`f6b_verify.txt` / `f6b_evidence.txt` / `f6b_inputs.txt`、`repro_build.txt`、`regression_suite.txt`（归档副本，1 项环境失败）、`regression_f6b_suite.txt`（独立检出，142/0/2）、`legacy_suite.txt`（83/18）、`verify_live_head.txt`、`ls_remote.txt`。