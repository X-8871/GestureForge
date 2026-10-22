# S6-A r06 独立复评报告（第 6 轮 · 独立 Reviewer）

- **审查对象**：工作树 `D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**被审提交 `04ea58e1`**
  （`04ea58e1e363e956b8a46ae5711ec8aecb27bfd4`，提交信息 `fix(stage6): S6-A v1.5/r06 fixes N-r05-04 (30fps later-of window completion) and N-r05-01..03`）
- **基线**：r05=`1632761`（`1632761b2d60d8c1328aa82be97d53eef30e1072`，上轮 `PASS`）；更早 r04=`b20b670`、r03=`2ce290f`、r02=`3b59674`、r01=`1fe4648`
- **契约版本**：r05=v1.4 → r06 自称 v1.5
- **审查时间**：2026-10-23 02:37 起（UTC+8）
- **写入范围**：仅 `D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01\`（自建）。**未写入、未修改被审工作树任何文件**；未直接运行
  `verification/s6a_r06_probe.py` 与 `verification/s6a_rerun_legacy_failures.py`（前者会向被审证据目录写 `probe_*_stdout.txt`），
  改为在隔离目录**复刻其全部 9 次运行**并与入库产物**逐字节**比对（§4.3）。收尾核验：`git status --porcelain` 为空、被审文件与提交一致（§7）。
- **独立性声明**：本轮与第 1–5 轮评审者无关联。`REVIEW_r05.md` 仅作为**待证伪的断言**使用；全部结论由本轮自写脚本、自推公式、自造注入与自跑退出码得出。
- **核对口径**：一律以 `git show 04ea58e1:<path>` / `git cat-file blob` 的**已提交字节**为准（§1 哈希表）；工作区当前内容仅用于判定漂移。

## 结论

# `PASS`

- **阻断问题：0 项。**
- **本轮重点 `N-r05-04`：关闭**（口径正确、等价性成立、两条捕获证明由我独立跑出真实 exit 1），残留**文本层**不一致见 `F1`（非阻断）。
- **`N-r05-03`：关闭；`N-r05-01` / `N-r05-02`：部分关闭**（各残留 1 处声明位置未改 + 归因数值与自家证据不符，均为非阻断描述性问题，见 §3.2/§3.3）。
- **无回归**：24 项参数逐字段差异 0、ID 集合无增删、既往断言键**值变 0**、v1.5 版本一致（§5）。
- **本轮新增 11 项非阻断/观察**（`F1`–`F11`，§6）。均不影响本包任何结论、关闭判定或版本一致性。
- **结论边界**：本结论只覆盖 **r06 的 S6-A G0 包**（规格 + 行为表 JSON v1.5 + 自检/构建器/探针 + r06 证据目录 36 文件），**不代表 G0/G2/G4/G5**，
  不涉及 S6-B/6-C/6-D/6-E 的语义与实现（仅按 `F6` 核对 STATE 声明与提交内容的一致性与可复现性）。
  自检 `ALL_PASS` 与检查器 `CHECKS_OK` 只表示规格一致性/算术/证据存在性/清单绑定复算通过。

---

## 1. 我实际执行的命令与真实退出码

工作目录 `D:\codex-worktrees\w6`；`--project-root` 一律为绝对路径 `D:/codex-worktrees/w6`；所有 `--out`、注入副本、比对产物落在隔离评审目录（**w6 内零写入**）。

| # | 命令（要点） | 真实退出码 | 结果 |
|---|---|---|---|
| 1 | `python -B verification/s6_g0_selfcheck.py --json docs/…v1.json --doc docs/…v1.md --cases …/r06/hand_computed_cases.json --upstream …/r06/upstream_bindings.json --out <隔离>/my_selfcheck_r06.json --project-root D:/codex-worktrees/w6 --evidence-dir …/r06 --manifest …/r06/delivery_manifest.json --state .codex/STATE.md` | **0** | `ALL_PASS`，**17/17 PASS，errors=0**，**C7 = 31 例**；与入库 `selfcheck_result.json` **17 项 id/name/status/detail 逐字相同（差异 0）**，`id_inventory`/`inputs`/`limitations`/`scope_statement` 全等 |
| 2 | `python -B verification/check_stage_delivery.py --mode inputs --manifest …/r06/inputs_manifest.json` | **0** | `CHECKS_OK`；与入库 `check_inputs_mode_output.txt` **逐字节相同**（`cmp -s`） |
| 3 | `python -B verification/check_stage_delivery.py --mode evidence --manifest …/r06/delivery_manifest.json` | **0** | `CHECKS_OK`；与入库 `check_evidence_mode_output.txt` **逐字节相同** |
| 4 | 我复刻 r06 探针 **9 次运行**（8 例 + 旧口径对照；沿用它自己的 `INJECTIONS` 函数，但 `--out`/注入副本写隔离目录） | 脚本 0 | **9/9 与入库 `probe_summary.json` 的 `actual_exit` + `failed_checks` 全等；9 个 `probe_*_stdout.txt` 与我的 stdout 逐字节相同**（§4.3） |
| 5 | 注入（我自造）：**HC-31 预期整组回退旧口径** → r06 自检 | **1** | `FAILED=['C7']`；`HC-31.m3_fires 预期 False 与复算 True 不符` ← **必须 FAIL，实测 FAIL** |
| 6 | 历史模型：`<git cat-file blob 1632761:verification/s6_g0_selfcheck.py>` 在 **r06 样例**上运行 | **1** | `FAILED=['C1','C7']`；C7 首失败 `HC-28.completion_index 无法独立复算（禁止不可复算的预期）` ← **必须 exit 1，实测 exit 1** |
| 7 | 我自造 5 例边界（附带原 31 例，共 36 例）→ r06 自检 | **1** | 前 35 例（31 入库 + 我自造 ZX-A..ZX-D）**全部一致**；仅 **ZX-E** 在我故意构造的「完成帧超出所给序列」上报值口径上分歧（`F7`） |
| 8 | 追加判别力注入：`HC-31.later_of_applied=false` / `m3_fires_count_only=true` / `HC-29.later_of_applied=true` / 删除 HC-31 | **1/1/1/1** | 分别 `C7`：`later_of_applied 预期 False 与复算 True 不符`、`m3_fires_count_only 预期 True 与复算 False 不符`、`HC-29.later_of_applied…`、`手算样例数量不足 31：30` |
| 9 | 诊断注入（探测新口径文本是否被机器断言）：`time_anchors.window_complete` 回退旧口径 / `M3.condition` 去掉「取较晚」 | **0/0** | **ALL_PASS** → 该两处**语义散文未被任何检查断言**（`F1` 依据之一） |
| 10 | 诊断注入（探测修文本是否安全）：把 B07/B27 旧措辞改成显式「取较晚」 | **0** | **ALL_PASS** → 修 `F1` 不破坏任何检查 |
| 11 | 我自写脚本：公式独立推演 / 样例与键差异 / 参数与 ID 比对 / 哈希复算 / STATE 声明 vs 提交 / 归因审计（`s1`–`s14`，见附录） | 0 | 见 §2–§7 |

## 2. 自算哈希（SHA-256，我自己对文件字节计算）

被审提交 `04ea58e1` 的关键文件（**工作区 CRLF 字节 = 证据绑定口径**）：

| 文件 | 我的 SHA-256 |
|---|---|
| `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` | `025b8e884e55f4ee48a148d2460eacf70e0253d4cab77c4db75cc0b53edc2057` |
| `docs/stage6/s6a_stage6_g0_behavior_v1.json` | `32ec34cdb2e776f68edded39636de83e0e73b730b7301b483c4e1e28967a1337` |
| `verification/s6_g0_selfcheck.py` | `2b068ee26f5d0e9b9d020d8f0b99a3768ce73126a21bddac158ffbe84fb8a73d` |
| `verification/s6a_build_evidence.py` | `e197e88f24a20390bda4806740b081b3f8460fa1afd2d7f15698c38af608faa6` |
| `verification/s6a_r06_probe.py` | `8a4dce87403463a5f6e00ed54aa8c0830c568f22a98693cce911f15bfa6e9684` |
| `.codex/STATE.md` | `680ce89c24f5608b969069e6b5a136d5f51c93a6f801a95c01cd2af4c8a1d897` |
| `…/r06/hand_computed_cases.json` | `3220a8b24fe45272efd8dd7c3daf2519803824b587326a32e2a14114d97ff1ce` |
| `…/r06/delivery_manifest.json` | `c202d068823a6d7a9664998fdf25b1d844cc616690aa2f7925808ab2d559c456` |
| `…/r06/inputs_manifest.json` | `a968e3a41322a277361e2f37a7dc5f1be653ce2f7b6f157aee218aab34ebc3a3` |
| `…/r06/selfcheck_result.json` | `a4d79d607f779c4cb7a67badce99b4416c1f2d9871aa146d54fc0f821bd52634` |
| `…/r06/probe_summary.json` | `77ddba3e21ebe32ec02175719fff541c653c094f1d37119f7be6633fa3951dc6` |
| `…/r06/fix_record.json` | `1e69aaa0cbbe5df60565830372e5d4fe246599af8df3d40ce67c745e58d5f1ae` |
| `…/r06/coverage_matrix.json` | `f3c1615f0374e7b231c214f8a48925ff000359744d662eabd8db89873ec0f052` |
| `…/r06/limitations_not_executed.json` | `0f977265ac40505de5d785a9afe5ffb64a0ec49d0d65a15dd07632b4cf6abf03` |
| `…/r06/upstream_bindings.json` | `ddff737bce766325634e55149c99c61f9ff6684bc2e53fb044b7da00fee66818` |
| `…/r06/selfcheck_r04_failure.json` | `79ef5c612705eef4432ad3364dd8ded736810575a53cf1a44bc1d4ed0c51de72` |
| 其余 20 个 r06 证据文件 | 见 `s14_final.txt`（36/36 已自算，逐文件列出） |

- 我自算的 `behavior_json_sha256` / `human_doc_sha256` / `hand_cases_sha256` 与入库 `selfcheck_result.json.inputs`、与 `delivery_manifest.json` 的对应条目 **三项全等**。
- 运行目录实际 **36 文件**；`hashes_sha256.txt` 解析 **34 条**（设计上不含 `delivery_manifest.json` 与自身）：**声明缺失 0、哈希不符 0**。
- `delivery_manifest.json` 声明 **42 条**（运行目录 35 + 外部绑定 7）：**声明但缺失 0、存在但未声明 0**（仅自身不计）、**哈希不符 0**；7 个外部绑定文件在提交中全部存在。
- r05 基线同 4 个源文件（我自算 git 字节）：`8b4abfca…`(doc) / `d01aaff3…`(json) / `82872655…`(selfcheck) / `f09b1997…`(builder) —— 证明基线身份明确。
- **字节口径**：`docs/stage6/**` 在工作区为 CRLF、`git cat-file blob` 为 LF（`core.autocrlf=true`）；`.py`/`STATE` 两侧相同（我逐项核过，见 `s4_compare.txt`）。与 r04/r05 同口径，**非本轮回归**（观察 `F11` 附注）。

## 3. 必须核查项：`N-r05-01..04` 的关闭核对

### 3.1 `N-r05-04`（本轮重点）— **关闭**

**(a) 实现口径**（`verification/s6_g0_selfcheck.py` `recompute(kind="window_match_vs_continues")`，提交字节 L764–L803）：
完成帧 = `completion_index = max(count_index, first_index + ceil(T6-S01/P − 1e−9))`，`window_span_ms = (completion_index − first_index)·P`，
`m3_fires = 计数≥S02 且 completion_index ≤ 末帧序`，另有 `later_of_applied = completion_index > window_indices[S02−1]` 与旧口径对照 `m3_fires_count_only`。

**(b) 等价性（我自己推演，不引用自检注释）**：计数谓词与时长谓词都随帧序**单调不减**，故「第一个同时满足两者」= **两者各自首次满足帧的取大**：
计数首次满足帧 = 第 `T6-S02` 个 `WINDOW_MATCH` 帧序 `C`；时长首次满足帧 = 窗口首帧 `f0` 之后第 `ceil(T6-S01/P)` 个间隔，即 `f0+ceil(T6-S01/P)`。
`max(C, f0+ceil(·))` 与 `ceil + max` 写法**等价**；`window_span_ms` 取该帧跨度与关闭条件逐字一致。我用**独立写法的逐帧显式扫描**（`s5_derive.py` 的 `literal()`）与自检写法对比 8 个情形：**7/7 现实情形一致**（第 8 例是我故意构造的越界情形，见 `F7`）。

**(c) 我的四（五）情形推演结果**（S01=200 ms、S02=6；`literal` 与 `checker` 两实现给出相同三元组）：

| 情形 | P | 序列 | 我的完成帧 | 我的 span | `m3_fires` | `later_of_applied` | `m3_fires_count_only` | 与入库样例 |
|---|---|---|---|---|---|---|---|---|
| 30 fps 时长支配 | 33.3 ms | 9 帧全 WM | **第 8 帧（idx 7）** | **233.1 ms** | true | true | **false** | = **HC-31** ✅ |
| 恰好 200.0 ms（两条件同帧） | 40 ms | 9 帧全 WM | **第 6 帧（idx 5）** | **200.0 ms** | true | **false** | true | = **HC-29** ✅ |
| P=40 ms（同上，边界） | 40 ms | 6 帧全 WM | 第 6 帧 | 200.0 ms | true | false | true | = HC-01/HC-29 ✅ |
| P=50 ms 计数支配 | 50 ms | 9 帧全 WM | 第 6 帧（idx 5） | 250.0 ms | true | false | true | 入库无此例；**我自造 ZX-C 被自检接受** ✅ |
| 时长 −1 单位 | 39.8 ms | 9 帧全 WM | 第 7 帧（idx 6） | 238.8 ms | true | true | false | = HC-02 口径 ✅ |
| §15 表 10 fps / 5 fps | 100 / 200 ms | 9 帧全 WM | 第 6 帧 / 第 6 帧 | 500 / 1000 ms | true | false | true | = §15 表 ✅ |
| 计数不足（0 个 WM） | 40 ms | 9 帧 | 无 | 0.0 | false | false | false | = HC-28 ✅ |

- **口径唯一性**：`window_match_vs_continues`（新）与 `stable_window`（HC-01..06，r04 起就按「第一个同时满足」循环求解）**两条独立代码路径结论一致**；`HC-06`（P=33.3，入库 expected `frames_required=8`、`actual_completion_ms=233.1`）与 `HC-31` 一致；§15 三行表格全部复现。**唯一分歧只在文本层（`F1`）。**
- 我自造 ZX-A（33.3）/ZX-B（40）/ZX-C（50）/ZX-D（39.8）四例的 expected 全由**我的独立推演**给出，被 r06 自检逐项接受（自检在第 36 例 ZX-E 才报错）。

**(d) 两条捕获证明（我自己跑，记录真实退出码）**：

| 证明 | 命令要点 | 真实退出码 | 捕获项与 detail |
|---|---|---|---|
| HC-31 预期回退旧口径 | r06 自检 + 我改写的 cases（`window_span_ms=166.5, m3_fires=false, completion_index=5, later_of_applied=false, m3_fires_count_only=true`） | **1** | `C7: HC-31.m3_fires 预期 False 与复算 True 不符` ✅ |
| r05 版自检跑 r06 样例 | `git cat-file blob 1632761:verification/s6_g0_selfcheck.py`（二进制提取）在 r06 json/doc/cases 上运行 | **1** | `FAILED=['C1','C7']`；C7 首失败 `HC-28.completion_index 无法独立复算` ✅（入库 `probe_summary.json` 记的 `failed_checks=['C1','C7']`、`c7_detail` 与我的逐字相同） |

**(e) 旧口径对照字段固定性与判别力**：`m3_fires_count_only` 固定在 **HC-28 / HC-29 / HC-31 的 `expected`** 中（值 false/true/false）。
它是自检用**旧公式**从同一帧序列**独立重算**后再比对，**不是自比较、不是输入重述**；且具备判别力——我把它改成 `true`（HC-31）→ `C7` FAIL，把 `later_of_applied` 改成 `false` → `C7` FAIL。C7 另有 `completion_index`（独有键）与 `window_span_ms=233.1` 两项共同固定新口径。

**(f) 与 §9/§14 `T6-S03`/§15/JSON 锚点的一致性**：JSON `time_anchors.window_complete`（「第一个…取较晚满足者」）、`transitions.M3.condition`、`low_fps_latency.window_completion_definition`、文档 §14 `T6-S03 | later_of`、§15 口径段与表格、HC-06/HC-31 —— **全部一致**。
**残留**：文档 §9 第二条与 B07/B27 的 `condition/output` 仍用 r04 期措辞（`F1`，非阻断）。

### 3.2 `N-r05-01`（注入计数表述）— **部分关闭**

- 实际实物：`INJECTIONS` 共 **8** 条，其中 `target≠None`（真注入）**7** 条、基线 **1** 条；加「旧口径对照」共 **9 次运行**。
- 入库 `probe_summary.json`：`composition = "基线 1 例 + 注入 7 例（共 8 例）+ 旧口径对照 1 例（共 9 次运行）"`、`injection_count=7`、`total_runs=9`、`results=9` → **机器可读，且与脚本实际 `INJECTIONS` 数量一致（我自己数）** ✅
- 已改正位置：probe 头注/清单、builder 头注与 summary 行、`fix_record.json/.md`、`S6A_run_summary.md`、`coverage_matrix.json`、`limitations_not_executed.json`、文档 v1.5 修订记录、JSON `revision.changes`、STATE 的 r06 段 ✅
- **残留 1 处（关闭条件点名过的位置）**：builder `keep_reason_for["probe_summary.json"] = "注入探针汇总（基线 exit 0 + 8 个注入用例…）"`，
  该串被原样写入 **r06 入库 `delivery_manifest.json` 的 `keep_reason`**；STATE 的 r05 历史段亦保留旧表述（后者与 `fix_record.notes` 声明的「r05 包不改写」自洽）。

### 3.3 `N-r05-02`（r04 重跑归因）— **部分关闭**

- 新归因「样例数 29<30（缺 HC-30）」已写入文档/JSON/`fix_record`/`limitations`/`coverage_matrix`/manifest `keep_reason`/STATE r06 段 ✅；`N-r04-04` 判别力已改引探针 `case_span_wrong` ✅
- **残留 A（原问题原文，2 处仍在生效）**：`C7 捕获 N-r04-04` 仍出现在
  ① `verification/s6a_build_evidence.py` 的 `summary_lines`；② 其生成的 **r06 入库 `S6A_run_summary.md`** 同一行 —— 正是 r05 要求改写的措辞，实测该断言在 r04 字节上**不成立**。
- **残留 B（数值与自家证据不符）**：r06 自检阈值为 **31**，其 R04 字节上的真实 C7 detail 为「手算样例数量不足 **31**：29」（入库 `selfcheck_r04_failure.json` 与 `_stdout.txt` 均如此）；
  但多处（含 `fix_record.json` 的 evidence 项）写作「**29<30**」甚至「C7 detail = 手算样例数量不足 **30**：29」，与同包证据矛盾。

### 3.4 `N-r05-03`（HC-30 动作计数）— **关闭**

- 自检返回并断言：`actions_within_supplied_sequence`（给定序列内计数）+ `action_count_is_lower_bound=true` + `action_count_scope="within_supplied_sequence"` + `action_count_discriminators=[gate_open_frame, first_action_frame, action_at_gate_open_frame]`；
  `hand_computed_cases.json HC-30.expected` 同步（旧键 `total_actions` 已从 expected 移除）。**与推导一致** ✅
- 覆盖边界已写进 HC-30 的 `derivation`（「只是给定 12 帧序列内的动作计数下界…真正的判别力在 gate_open_frame / first_action_frame / action_at_gate_open_frame」）✅
- 残留（不影响关闭）：自检仍**同时返回**旧别名键 `total_actions`（内部变量名，结构上仍封顶为 1），三个恒真布尔键也保留（观察 `F11`）。

## 4. 必须核查项：复跑一致性

1. **r06 全量自检**（绝对 `--project-root` + `--evidence-dir/--manifest/--state`）：**exit 0 / ALL_PASS 17 项 / C7 样例 31**；
   与入库 `selfcheck_result.json` 的 **17 项 id+name+status+detail 逐字差异 = 0**，`inputs` 九字段全等，`id_inventory` 全等。
   入库 C11 detail：`实际文件 36 个；manifest 双向一致（运行目录 35 个文件 + 外部绑定 7 个文件哈希复算通过）；STATE 声明 36 个文件与 4 个目录全部存在`。
2. **两个 `check_stage_delivery` 模式**：均 **exit 0 / CHECKS_OK**，stdout 与入库 `*_mode_output.txt` **逐字节相同**。
3. **探针 9 次运行**：我用它自己的 `INJECTIONS` 复刻（`--out`/注入副本落隔离目录），**`actual_exit` + `failed_checks` 与入库 `probe_summary.json` 9/9 全等**，且 **9 个 `probe_*_stdout.txt` 与我的 stdout 逐字节相同**（2748/3403/2885/3107/3203/2923/2851/2605/2898 B）。
4. **旧包失败证据**：r06 提交内的 `selfcheck_r04_failure.json` = `FAILED['C7','C12']`，C7「不足 31：29」、C12 报 M5 缺「窗口推进帧」5 marker + `H-10` + release 断言 —— 与「r06 加固自检在 r04 字节上捕获」的用途一致（`r04_package_under_test.json` 绑 git ref + sha256）。
5. **提交后复跑**：在 HEAD 前进到 S6-B 提交后我再跑一次全量自检，**exit 0、17 项与先前及入库结果全等**（见 §7 漂移说明）。

## 5. 无回归与无夸大

| 检查点 | 我的实测 | 判定 |
|---|---|---|
| **24 项参数值 + `PENDING_APPROVAL`** | r05(`1632761`) vs r06(`04ea58e1`) 逐字段：`kind/name_zh/unit/comparison/draft_value/draft_source/approval_status/approval_owner` **差异数 0**；非 `PENDING_APPROVAL` 参数 = 0（两版皆然） | ✅ |
| **ID 集合差异** | `transitions` 14→14、`hard_invariants` 10→10、`behavior_rows` 28→28、`open_decisions` 16→16、`parameters` 24→24、`states` 7→7：**新增=[] 删除=[]**；`revision.deleted_transitions` 仍只记 r02 的 M14（历史字段） | ✅ |
| **声明新增是否恰好** | JSON 顶层键无增删；新增键仅 `time_anchors.window_complete` 与 `revision.retained_from_r05.{run_id,artifact_version,note}`（3）；删除键为 `revision.retained_from_r04.*`（3）与随轮滚动的 `revision.changes[4].*`（3）——全部落在声明的 4 项修复/簿记内 | ✅ |
| **样例集差异** | 样例 30→31，**新增恰为 HC-31**、删除 0；HC-28/29/30 的 `expected` **只增删键、既往键值变 = 0**（`span_conventions_agree` 被移除并替换为 `completion_index`/`later_of_applied`/`m3_fires_count_only`/`sequence_span_ms`/`lost`/`continues_false_streak` 等更强字段）；`hand_cases_version` v1.4→v1.5；`parameter_assumptions_unfrozen` 全等 | ✅ |
| **`artifact_version` 一致性** | JSON=`S6A-G0-v1.5`；`fix_record.json`/`coverage_matrix.json`/`limitations_not_executed.json`=`S6A-G0-v1.5`；`hand_computed_cases.json`=`S6A-HC-v1.5`；文档「v1.5 / r06」2 处 + 历史 v1.4 修订记录 1 处；STATE 出现 v1.5 四处；**文档不含完整令牌 `S6A-G0-v1.5`**（与 r04/r05 相同，观察 `F11`） | ✅（附观察） |
| **声明但缺失的文件** | r06 证据 36/36 存在且哈希相符；manifest 42 条全部存在；`hashes_sha256.txt` 34/34；STATE 声明 36 文件全部存在（C11）；文档 §18 提到的 2 个阶段4 上游文件不在证据目录**属上游清单**，其绑定由 C8（11 项哈希一致）复算 | ✅（`F6` 另述目录级依赖） |
| **r01..r05 证据未被触碰** | `git diff --name-status 1632761 04ea58e1 -- …/r0{1,2,3,4,5}` = **空** | ✅ |
| **是否自称「已审查/已通过/G0 通过」** | 我全量扫描 r06 文档/STATE/36 证据文件：**未发现虚假完成声明**。命中皆为否定语境（「不因收尾而视为通过」「不得自称已审查/已通过」「不代表独立审查或 G0/G4/G5」）或**经我核实为真的历史引用**（`REVIEW_r05.md` 确为 `PASS`、被审提交确为 `1632761`、4 项非阻断） | ✅ |
| **状态口径** | JSON `status=G0_PACKET_PENDING_APPROVAL`、`revision.review_status=PENDING_REVIEW`、`semantic_changes=true`（如实声明语义变更）、`parameter_value_changes=false`；文档 §18 明示「本轮未完成独立审查」；`limitations_not_executed.json` 把「独立复评」列为 `NOT_RUN` + `BLOCKED` | ✅ |
| **无夸大（探针/自检口径）** | 各处 `ALL_PASS`/`CHECKS_OK` 均附「不代表状态机行为/独立审查/G0/G4/G5」的范围声明；`probe_summary.scope_statement` 亦同 | ✅ |

## 6. 本轮非阻断问题与观察（格式：`位置 | 问题 | 影响 | 依据 | 关闭条件`）

> 全部为非阻断；`F6` 建议在 G0 冻结/G5 之前消除。

### `F1` 窗口完成口径的**文本残留**：§9 第二条与 B07/B27 仍写 r04 期措辞
- **位置**：`docs/…spec_v1.md` **L177**（§9「窗口完成时刻」）、doc **L114**（B07 行）、**L134**（B27 行）；JSON `behavior_rows.B07.condition`（`完成时刻=第 N 个 WINDOW_MATCH 结果到达时刻`）、`behavior_rows.B27.output`（`窗口完成时刻=第 N 个 WINDOW_MATCH 结果到达时刻（实测）`）。
- **问题**：这三处仍是 r04/N-r04-04 时期的表述。§9 L177 明写「**第 `T6-S02` 个** `WINDOW_MATCH` 结果到达**且时长条件同时满足**的那一帧」——在 30fps 下第 6 个 WM 帧只有 166.5 ms，该句**字面读法得不到任何完成帧**，与 §15「第 8 帧 233.1 ms」/HC-31/`time_anchors.window_complete` 冲突；B07/B27 的「第 N 个」虽可用「N=完成时的 WM 计数」兼容解读，但与同文件 `time_anchors`/`M3.condition` 的显式措辞不统一，仍是**同一口径上的歧义源**。JSON 为声明权威、文档头也要求「冲突时回改本文」。
- **影响**：不影响任何结论、检查或版本绑定（行为口径由 HC-06/HC-28/29/31 + C7 与三处 JSON 锚点固定；S6-B 侧已按 later_of 落地）。风险在后续实现者按 §9 L177/B07 字面实现，复现 r05 的 30fps 漏判。
- **依据**：`s9_regress.txt`「window_complete 上下文」与本文 §3.1(f)；我自算哈希对应的提交字节；诊断注入 `inj_anchor_old`/`inj_m3_no_later` → 自检 **exit 0（该散文未被断言）**；`inj_b07_fixed`/`inj_b07_b27_fixed` → **exit 0（修正不破坏任何检查）**。
- **关闭条件**：把 doc §9 L177、B07/B27 行与 JSON `B07.condition`/`B27.output` 改为与 `time_anchors.window_complete` 逐字同义的「第一个同时满足帧数与时长（取较晚满足者）的帧」；或显式标注旧措辞为历史。修完重跑 r06 自检应仍 `ALL_PASS`（我已验证）。

### `F2` `delivery_manifest.limitations[0]` 与本清单 `source_commit` 自相矛盾
- **位置**：`report/evidence/S6-A/s6a_g0_20261022_r06/delivery_manifest.json`；来源为 `verification/s6a_build_evidence.py` 的**硬编码**字符串。
- **问题**：清单 `source_commit = 1632761…`（r05），而 `limitations[0]` 写「source_commit 为修订基线 **b20b670**」（r04）。r05 清单当时写 b20b670 是对的，本轮未同步。
- **影响**：仅文字自相矛盾；不影响哈希/绑定（`source_commit` 字段与实际一致）。任何按同脚本重建清单者会复现该矛盾。
- **依据**：`s12_cases.txt`「manifest.limitations[0] 与 source_commit」；`git show 04ea58e1:verification/s6a_build_evidence.py` 中的字面串。
- **关闭条件**：builder 改为按变量拼接修订基线的提交哈希（或改写为「source_commit 见本清单字段」），重建并重跑 C11。

### `F3` `N-r05-01` 残留：builder/清单 `keep_reason` 仍写「8 个注入用例」
- **位置**：`verification/s6a_build_evidence.py` `keep_reason_for["probe_summary.json"]`；其产物 `…/r06/delivery_manifest.json` 同串 `keep_reason`。
- **问题**：实物为基线 1 + 注入 7（共 8 例运行），该处仍称「基线 exit 0 + **8 个注入用例**」，正是 r05 关闭条件点名的位置。
- **影响**：自述计数不实 1 处；不改变任何结论（`probe_summary.composition`/`injection_count` 已正确且我复跑 9/9 一致）。
- **依据**：`s10_wording.txt` 的 `[8 个注入]` 命中（builder x1、r06 manifest x1）；`s8_probe.txt`（INJECTIONS 8 / 真注入 7）。
- **关闭条件**：该串改为「基线 1 例 + 注入 7 例（共 8 例）」并重建清单。

### `F4` `N-r05-02` 残留：旧归因仍在生效 + 新归因数值与自家证据不符
- **位置**：① `verification/s6a_build_evidence.py` `summary_lines` 与其产物 `…/r06/S6A_run_summary.md`（`（r04，C12 捕获 N-r04-01/02、**C7 捕获 N-r04-04**）`）；② `fix_record.json` 的 N-r05-02 `evidence`（`（C7 detail = 手算样例数量不足 30：29）`）及文档/`limitations`/`coverage_matrix`/manifest 的「29<30」。
- **问题**：① 我实测 r04 字节上 C7 的唯一失败是**样例数不足**（不涉及跨度口径），该归因仍不成立；② r06 自检阈值为 **31**，同包 `selfcheck_r04_failure.json` 明写「不足 **31**：29」，「29<30」与之矛盾。
- **影响**：描述性归因偏差（与 r05 对同一问题的定级一致：非阻断）。
- **依据**：`s10_wording.txt` `[C7 捕获 N-r04-04]`/`[29<30]`/`[29<31]` 三节的命中清单；`…/r06/selfcheck_r04_failure.json` C7 detail。
- **关闭条件**：① 把该行改为「C7 捕获样例数 29<31（缺 N-r04-01 新增的 HC-30 与 HC-31）」；② 统一为与 r06 阈值一致的「29<31」；③ `fix_record` 引用的 detail 串改为与 `selfcheck_r04_failure.json` 逐字一致。

### `F5` 提交版 `STATE.md` 的 r05 残留与自相矛盾（活文档，非历史证据）
- **位置**：`.codex/STATE.md` L8（「S6-A 契约（v1.4，已过第 4 轮复评 PASS）」）、L18–L26（r05 段仍称「`span_conventions_agree` 断言两种口径一致」——该断言在 r06 已从 expected 移除）、L50（「**S6-A 状态**：v1.4/r05 为 `PENDING_REVIEW`」）、L66 标题「（2026-10-23 02:03）」vs 同行心跳 02:44、同行「起始提交 …（**修订基线 `b20b670`**）」（r06 基线应为 `1632761`）、同行恢复命令仍指向 `…/r05/hand_computed_cases.json` 等 r05 路径。
- **问题**：STATE 是 r06 清单绑定的 7 个外部文件之一，也是「下一接手方」入口；上述内容描述的不是当前包（v1.5/r06）。
- **影响**：不触发任何检查（C11 只查 `S6-A DONE` 缺失、`DELIVERED_PENDING_*` 存在与声明文件存在性），也不影响 S6-A 结论；但会误导接手方按 r05 包恢复、并让 STATE 与 JSON `baseline.revision_base_commit` 相互矛盾。
- **依据**：`s11_misc.txt`（STATE 全文与 `git diff 1632761 04ea58e1 -- .codex/STATE.md`）；C11 的 STATE 断言范围见提交字节 L1078–L1114。
- **关闭条件**：更新 L8/L50 为 v1.5/r06；在 11 字段行写 r06 心跳时间戳、修订基线 `1632761` 与 r06 恢复命令；把 r05 段明确标为历史（或删除其对现行自检的机制描述）。

### `F6` 提交版 `STATE.md` 声明的证据目录在**被审提交内不存在** → 被审提交单独检出时 C11 不通过
- **位置**：`.codex/STATE.md` L58（`` `report/evidence/S6-B/s6b_core_20261023_r01/` ``）；C11 的 `declared_dirs` 逻辑（提交字节 L1100–L1111）。
- **问题**：C11 要求 STATE 声明的目录在工作树存在（我实测 4 个声明目录含该目录），但 `git ls-tree -r 04ea58e1 -- report/evidence/S6-B` = **0 个文件**（`git status` 当时显示 `?? report/evidence/S6-B/`）。因此 **r06 的「ALL_PASS 17 项（含完整 C11）」在被审提交单独检出/干净克隆上不可复现**：`missing_dirs` 会触发 `STATE 声明的证据目录不存在`。
- **影响**：不影响 S6-A 任何结论、算术或绑定；影响**可复现性/冻结口径**：S6-A 包的 C11 通过依赖同一工作树里未提交的 S6-B 产物。审查期间（约 02:53）该目录已随后续提交 `43f7995` 入库，故当前 HEAD 下该依赖已被满足。
- **依据**：`s10_wording.txt` C 节（4 个声明目录 × 提交内文件数：S6-B=0）；`s11_misc.txt`（`git diff --name-status 04ea58e1 HEAD` 全为 `A`，含 40 个 S6-B 文件）；提交字节 L1099–L1111 的 `missing_dirs` 逻辑。
- **关闭条件**：在**同一提交**内提交 STATE 所声明的证据目录；或让 STATE 只声明已入库路径（未提交产物单列且不进入 C11 解析范围）。冻结/G5 前应确认「最终修订提交」自身即可通过完整 C11。

### `F7` C7 在「完成帧超出所给序列」时仍报出未观测帧的 `completion_index`/`window_span_ms`
- **位置**：`verification/s6_g0_selfcheck.py` 提交字节 L772–L803（`completion_index` 不设上界，`m3_fires` 才用 `completion_index <= len(frames)-1` 拦截）。
- **问题**：如 P=25 ms、8 帧（S01=200/S02=6），需第 9 帧才完成：自检给出 `completion_index=8`、`window_span_ms=200.0`、`later_of_applied=true`、`m3_fires=false`；而「第一个满足两条件的帧」在**所给序列内不存在**，逐帧字面扫描应得「无完成帧」（我自造 ZX-E 期望 `-1/0.0` → 被拒，`C7: ZX-E-25.0.completion_index 预期 -1 与复算 8 不符`）。`m3_fires` 两读法一致（false），故仅是**次要报告字段**语义未定义。
- **影响**：无样例覆盖、不影响 31 例与任何结论；读者可能把 `completion_index=8`（超出序列）误当已观测完成帧。
- **依据**：`s5_derive.txt` 情形 E（literal vs checker）；`s7_results.txt` `ext_cases`（exit 1，唯一差异即此）。
- **关闭条件**：当 `completion_index > len(frames)-1` 时把 `completion_index` 记 `-1`、`window_span_ms` 记 `0.0` 并在 C7/文档注明；或新增一个小节说明该字段为「所需完成帧（可越界外推）」。

### `F8`（观察）`ceil(S01/P − 1e−9)` 的浮点鲁棒性是**有意设计且优于朴素浮点比较**
- **位置**：提交字节 L775–L777。
- **说明**：我探到一处两类实现的分歧：`P=33.3, S01=99.9` → 精确算术应为 3 个间隔（3×33.3=99.9），朴素浮点乘 `i*P` 会得 `99.89999999999999 < 99.9` 而多要 1 个间隔；自检的 `ceil(q−1e−9)` 给出**正确的 3**，与 §12「除过期外全部含等号」一致。反向风险仅在 `S01/P` 数学上落在整数上方 1e−9 以内时出现，对 ms 量级与现存/草案参数**不可达**（我实测 4 组：仅上述一组分歧，且自检为正确方向）。
- **影响**：无。记录以免后续误判为缺陷。

### `F9`（观察）`window_match_vs_continues` 模型的既有简化与本轮字段副作用
- 该模型把**整段给定序列**视为一个窗口（不含 `T6-J01` 抖动重置、非 WM 帧不重置计数）；抖动/重置语义由 `kind="jitter"`（HC-12）单独建模，r04/r05 同此，**非本轮回归**。
- `window_span_ms` 本轮起**不参与判定**（`m3_fires` 改用 `completion_index`）；当 WM 计数 < `T6-S02` 时由 r05 的「部分跨度」改为固定 `0.0`（无样例覆盖，HC-28 为 0 个 WM 两版同为 0.0）。
- **影响**：无样例、无结论受影响。记录为后续建模留痕。

### `F10`（观察）「旧口径对照」运行的首个 C7 失败发生在 HC-28 而非 HC-31
- **位置**：`…/r06/probe_summary.json` 的 `historical_model_check.c7_detail`；`verification/s6a_r06_probe.py` 头注与 `fix_record` 的文字。
- **说明**：`check_hand_cases` 在首个不匹配处即抛错，故 r05 旧脚本在 HC-28 就因缺 `completion_index` 等新键而报「无法独立复算」，**未走到 HC-31**。因此「旧口径把 HC-31 算成 166.5 ms」这一机制由探针 `case_span_wrong`（及我自造的 HC-31 回退注入）直接证明，该历史运行证明的是「旧模型脚本无法接受 r06 样例」。两处结论皆为真，只是描述与捕获点的对应关系不够精确。
- **影响**：无（`c7_detail` 已如实入库，读者可见）。**关闭条件**：把该处描述改为「首个失败在 HC-28（新键不可复算）；HC-31 的口径差异由 `case_span_wrong` 直接证明」。

### `F11`（观察）其他零星残留
- `limitations_not_executed.json`：r06 的说明仍放在键名 **`r03_notes`** 下；`not_run[0].reason` 仍写「S6-A **v1.4** 已收尾」。
- 自检 `latched_stable_gate_on_timeout` 仍**同时返回**旧别名 `total_actions`（内部名，封顶 1）与三个恒真布尔键（`no_action_on_timeout_frame`/`timeout_frames_not_window_advancing`/`latched_within_acquisition`）——`N-r05-03` 选择的是「注明覆盖边界」而非「去封顶」，故可接受。
- 文档仍不含完整版本令牌 `S6A-G0-v1.5`（与 r04/r05 同，属既有 `O2`）；`docs/stage6/**` 工作区 CRLF / git LF 的哈希口径差异属既有 `O1`；`coverage_matrix.location` 的「v1.3」残留标签本轮已清除。
- `verification/s6a_r05_probe.py` 仍留在树中（r05 历史脚本，r06 清单不再引用它；不属缺陷）。
- 「本包已通过第 5 轮独立复评」措辞（文档 v1.5 记录、JSON `review_verdict`、STATE）——事实我已核实为真（`REVIEW_r05.md` = `PASS`，被审 `1632761`，4 项非阻断）；仅「本包」在 v1.5 段落下仍有被误读为「r06 已通过」的空间（r05 的 `O5` 同类），建议改写为「r05 包（1632761）已通过第 5 轮独立复评…」。

## 7. 工作区漂移清单

- **审查开始（约 02:37）**：HEAD=`04ea58e1`（被审提交）；`git status --short` 有 **6 条未跟踪**：
  `?? docs/stage6/s6b_frozen_interface_v1.json`、`?? report/evidence/S6-B/`、`?? src/stage6/`、`?? verification/s6b_build_evidence.py`、`?? verification/s6b_probe.py`、`?? verification/s6b_run_cases.py`；**已跟踪修改 0**。
- **审查期间（约 02:53）**：上述 S6-B 产物被**提交为 `43f7995`**（`feat(stage6): S6-B pure core + action layer + 6-C deterministic matrix (22 cases / 11 classes)`），HEAD 前移。
  `git diff --name-status 04ea58e1 HEAD` = **42 个 `A`（全部为 S6-B 新增：`docs/stage6/s6b_frozen_interface_v1.json`、40 个 `report/evidence/S6-B/**`、`src/stage6/s6_core.py|s6_actions.py|s6_params.py`、`verification/s6b_build_evidence.py|s6b_probe.py|s6b_run_cases.py`）**，**没有任何 r06 文件被修改或删除**（无 `M`/`D`）。
- **漂移判定**：`git diff --quiet 04ea58e1 -- <文件>` 对 8 个关键被审文件逐一返回 0（`docs/stage6/*v1.json`、`*spec_v1.md`、`selfcheck.py`、`build_evidence.py`、`s6a_r06_probe.py`、`.codex/STATE.md`、`r06/selfcheck_result.json`、`r06/hand_computed_cases.json` 与提交**逐字节一致**）；`git status --porcelain` 现为空。
  ⇒ **被审内容零漂移，漂移是纯增量的 S6-B 先未提交、后提交**。我在 HEAD 前移后**复跑全量自检**（exit 0，17 项与先前及入库结果全等），确认结论不受影响。按任务约定，**不据此判缺陷**；仅 `F6` 记录了「被审提交单独检出时 C11 的目录依赖」这一由漂移暴露的事实。
- 未评价 S6-B/6-C 的实现与语义（越界）；未接触板卡/JTAG/COM4/`hw_server`/HDMI/摄像头；未 push；未改 `main`/`w4`/`w5`/`dbdf`/`w2b`。

## 8. 我未做的事（限制，如实登记）

- 未修改任何被审文件；**未在 `w6` 内创建或修改任何文件**。为此未直接运行 `s6a_r06_probe.py`（会向被审证据目录写 stdout 文件）与 `s6a_rerun_legacy_failures.py`（会向证据目录与 `tmp/6/**` 落盘），改为在隔离目录复刻同逻辑并与入库产物逐字节比对（§4.3）。
- 未复核 S6-B/6-C/6-D/6-E 的语义与实现；未复核 r01/r02/r03 证据目录全部文件的语义（只按本次重跑与清单范围核对）。
- 未验证历史各轮评审报告结论的正确性（只把 `REVIEW_r05.md` 当作待证伪断言，并核对其 `PASS`、被审提交与 4 项非阻断）。
- 未运行任何需要审批或越权的操作；本会话为受限子代理，无法扩权。
- 结论只覆盖 r06（提交 `04ea58e1`）；**不代表 G0/G2/G4/G5**。

---

## 附：本轮证据（全部在 `D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01\`）

`REVIEW_r06.md`（本报告）、`blobs/`（`git cat-file`/`git archive` 提取的被审字节：8 个 r06 文件、7 个 r05 文件、r06 证据 36 文件、r05 证据 35 文件）、
`runs/my_selfcheck_r06.json`（全量自检结果）、`runs/my_selfcheck_r06_after_s6b.json`（HEAD 前移后复跑）、`runs/my_inputs_mode_output.txt`、`runs/my_evidence_mode_output.txt`（逐字节与入库相同）、
`runs/my_extended_cases.json`（原 31 例 + 我自造 ZX-A..ZX-E）、`runs/inj_*.json`（10 个注入副本）+ 各自 `_result.json`/`_stdout.txt`、`runs/probe/`（我复刻探针 9 例的结果/stdout，与入库逐字节相同）、
`runs_repro.txt`、`runs_inject.txt`、`cmp_out.txt`、`s1_json_overview.txt`、`s2_cases.txt`、`s3_kinds.txt`、`s4_compare.txt`、`s5_derive.txt`、`s7_results.txt`、`s8_probe.txt`、`s9_regress.txt`、`s10_wording.txt`、`s11_misc.txt`、`s12_cases.txt`、`s13_probe.txt`、`s14_final.txt`，
以及全部自写脚本 `s1`–`s14*.py`、`extract.sh`、`run_repro.sh`、`run_cmp.sh`、`run_inject.sh`。