# S6-A r07 独立复评报告（第 7 轮 · 独立 Reviewer）

- **审查对象**：工作树 `D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**被审提交 `bdcf896`**
  （`bdcf8963300475a61f26cbc3ec85a32275b781d2`，`fix(stage6): S6-A v1.6/r07 closes review F1..F11, adds F6 export self-proof rule, corrects M4 reachability (S6-B BLK-1)`）
- **基线**：r06=`04ea58e1`（上轮 `PASS` + 11 项非阻断 `F1`–`F11`）；`43f7995` = S6-B r01（本轮只按 `F6`/`BLK-1` 引用，**不评价 S6-B 实现与语义**）
- **契约版本**：r06 自称 `S6A-G0-v1.5` → r07 自称 **`S6A-G0-v1.6`**（RunId `s6a_g0_20261022_r07`）
- **审查时间**：2026-10-23 03:22 起（UTC+8）；**结论只覆盖 r07（提交 `bdcf896`）**，不代表 G0/G2/G4/G5。
- **写入范围**：仅 `D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01\`（自建）与被审工具的**系统临时目录**。
  **未修改任何被审文件、未在 `w6` 内创建或修改任何文件**（收尾核验：`w6` `git status --porcelain` 为空）。
- **独立性声明**：本轮与第 1–6 轮评审者无关联。`REVIEW_r06.md` 只作**待证伪的断言**使用；全部结论由本轮自算哈希、自写脚本、自造反例与自跑退出码得出。
- **核对口径**：一律以 **`bdcf896` 的提交字节**（`git cat-file blob` / `git show`）为准。审查期间 `w6` 工作树被并发写入方推进（见 §9），故所有复跑都在**隔离副本**中进行。

## 结论

# `CHANGES_REQUIRED`

- **阻断 1 项**：`BLK-r07-1` —— `BLK-1(b)`（M4 可达性）的收尾**未扫全**：同一包内同时存在「M4 可达 / 保留并计入覆盖」（`reachability.M4`、`U6-12`、文档 §4/§12.1/§14、C16）与「M4 不可达 / 不得计入覆盖声明」的**机器可读**表述
  （JSON `parameter_notes.T6-S04`、`delivery_manifest.limitations[3]`），其中 `hand_computed_cases.json` 的 **HC-23 由 C7 机器断言** `m4_reachable_under_draft=false` —— 与 C16 结论直接相反。共 8 处，见 §8。
- **非阻断 6 项**（`N-r07-1`…`N-r07-6`，§8）：`export_selfproof.json` 内嵌陈旧 `FAIL` 记录且未含交付提交主体；自证工具存在**环境依赖的假阴性**（stage B 覆盖 stage A）；`F2` 修订基线三处口径不一；`F4` 残留 1 处 `29<30`；`F5` 残留 2 处 STATE 陈旧行；`F11` 残留 2 处 `v1.5` 令牌。
- **逐项关闭判定**：`F1` ✔关闭、`F7` ✔关闭、`F3` ✔关闭、`F10` ✔关闭、`F6` **实质成立但证据不自洽**、`BLK-1(b)` **核心正确但收尾不全（阻断）**、`F2`/`F4`/`F5`/`F11` **部分关闭**、`F8`/`F9` ✔已登记为有意设计。
- **无回归**：24 项参数逐字段差异 **0**、`PENDING_APPROVAL` 24/24、各 ID 集合 14/10/28/16/24/7 **无增删**、样例 31→32（新增恰为 HC-32）、`artifact_version` 一致。
- **F6 核心事实已被我独立复现**：`bdcf896` 提交自证 **SELF_PROVEN [0,0,0]**；`04ea58e1` **NOT_SELF_PROVEN [1,0,0]**，失败点**正是** `C11: STATE 声明的证据目录不存在：['report/evidence/S6-B/s6b_core_20261023_r01']`；工具**不可被"洗白"**（内容改一字节 → `unresolved` + C11 哈希不符 + exit 1）。
- **结论边界**：`ALL_PASS`/`CHECKS_OK`/`SELF_PROVEN` 只表示规格一致性、算术、证据存在性与清单/STATE 绑定通过这些**机器检查**；不代表状态机行为、独立审查、G0/复评或实物验收。

---

## 1. 我实际执行的命令与真实退出码

隔离副本与 `--out` 一律落在评审目录；`--project-root` 一律**绝对路径**；被审文件只读。

| # | 命令（要点） | 真实退出码 | 结果 |
|---|---|---|---|
| 1 | `bash tmp/review/S6A_r07_20261023_r01/run_repo3.sh`（构建**与 w6@bdcf896 逐字节同口径**的隔离副本 `repo3`：`git clone --shared --no-checkout` + `checkout -f bdcf896` + 覆盖 w6 工作树字节 + 8 个漂移文件还原提交字节；`verify_parity.py` 用 `git ls-tree -z` 取真名逐路径比对：`paths=1874 LF=1186 CRLF=688 content_mismatch=0 missing=0`） | 0 | 副本与提交**同口径**（1874/1874 路径内容一致，差异仅为 O1 换行口径） |
| 2 | 自证（`repo3` 内**提交内**工具）：`python -B verification/export_selfproof.py --project-root <repo3> --commit 04ea58e1 --commit bdcf896 --worktree-snapshot` | **1**（总体 `NOT_ALL_SELF_PROVEN`，设计如此） | `04ea58e1` **NOT_SELF_PROVEN [1,0,0]**、`bdcf896` **SELF_PROVEN [0,0,0]**、worktree snapshot **SELF_PROVEN [0,0,0]** |
| 3 | r07 全量自检：`s6_g0_selfcheck.py … --project-root <repo3> --evidence-dir <r07> --manifest <r07/delivery_manifest.json> --state <repo3/.codex/STATE.md>` | **0** | `ALL_PASS` **17/17**，`C7 = 32 例`；`C11 = 实际文件 39 个；manifest 双向一致（运行目录 38 + 外部绑定 8）；STATE 声明 37 个文件与 3 个目录全部存在` |
| 4 | `check_stage_delivery.py --mode inputs`（r07 `inputs_manifest.json`） | **0** | `CHECKS_OK`；与我重跑 stdout **逐字节相同（O1 口径）** |
| 5 | `check_stage_delivery.py --mode evidence`（r07 `delivery_manifest.json`） | **0** | `CHECKS_OK`；与我重跑 stdout **逐字节相同（O1 口径）** |
| 6 | 在 `repo3` 内重跑 r07 探针：`s6a_r07_probe.py --run-dir <r07> --project-root <repo3>` | **0** | `PROBE_OK`：**10/10 AS_EXPECTED**（基线 1 + 注入 7 + 历史对照 2）；**10 个 `probe_*_stdout.txt` + `probe_summary.json` 与入库逐字节相同（O1 口径，13/13）** |
| 7 | **反例 1**：在 `repo3` 把清单已声明哈希的 `report/evidence/S6-A/s6a_g0_20261022_r07/coverage_matrix.json` **改一个非换行字节**（值 `1`→`9`）并提交 `88403f8` → 自证 | **1** | `NOT_SELF_PROVEN [1,0,2]`；`newline_alignment.unresolved=['…/coverage_matrix.json']`、`aligned 40→39`；`C11: 清单哈希不符：coverage_matrix.json`；evidence 模式 `exit 2`（`files[3]…SHA-256 不匹配`）→ **工具登记而不"修好"** ✅ |
| 8 | **反例 2**：把清单声明 **LF** 口径的 `verification/s6_g0_selfcheck.py` 的**提交 blob 整体改 CRLF（内容不变）**，提交 `48c93b9` → 自证 | **0** | **SELF_PROVEN [0,0,0]**，`aligned 40→41`、`unresolved=[]` → 行尾差异被正确判为**换行口径**，不误判为内容差异 ✅ |
| 9 | 单元反例：直接调用提交内 `export_selfproof.align_by_manifest_hashes` / `normalize_line_endings`（合成树：声明 CRLF 而文件为 LF、声明 LF 而文件为 CRLF、内容真差一字节） | 0（断言全通过） | `aligned=2, unresolved=['c.txt']`；`c.txt` **字节未被改写**；`normalize_line_endings`：`aligned=1, content_differs=['e.txt']`，`e.txt` 未被改写 ✅ |
| 10 | **诊断反例 3**（环境依赖）：在**未对齐换行口径**的普通克隆（全局 `core.autocrlf=true` → `.py`/STATE 为 CRLF，而清单声明 LF）上跑 `--commit bdcf896` | **1** | **假阴性**：`NOT_SELF_PROVEN [1,0,2]`；`C11: 清单声明的源码/输入哈希不符：.codex/STATE.md`（stage A 对齐 6 个 → stage B 用工作树字节又覆盖回 6 个） |
| 11 | 判别力注入（我自己构造，隔离目录）：`reachability.M4.status=UNREACHABLE…` / `M4.reason` 去机制关键词 / `U6-12` 回退「删除 M4」/ `B07.condition` 旧措辞 / 文档 §9 旧措辞 | **1/1/1/1/1** | 全部 `C16`（3 次）与 `C14`（2 次）FAIL，detail 逐条命中预期 ✅ |
| 12 | 旧口径实证：加载 `04ea58e1:verification/s6_g0_selfcheck.py` 的 `recompute()`，对 HC-31/HC-32 直接复算 | 0 | HC-31 旧值与 r07 expected **全等**（7 / 233.1 / true）；**HC-32 旧实现报 `completion_index=7`、`window_span_ms=233.1`**，r07 报 `-1 / 0.0` ✅（证实 `F7` 的旧口径描述为真） |
| 13 | M4 可达性自推导（我自写逐帧模型，只读提交内谓词/迁移/参数） | 0 | P=100/40/33.3 ms 三组：M4 分别在帧 5（500.0 ms）/13（520.0）/16（532.8）命中，`miss_streak=0`、距锚点 0 → **M10 始终不命中 ⇒ M4 可达** ✅ |
| 14 | 无回归/清单一致性脚本（`s_regression.py`、清单双向、`hashes_sha256.txt`、旧包绑定哈希、自称扫描，全用提交字节） | 0 | 见 §7；`hashes_sha256.txt` 37/37 一致；r01–r04 旧包绑定各 5/5 哈希一致 |

> 说明：我的重跑产物在工作树口径下为 **CRLF**，入库 **git blob 为 LF**（`core.autocrlf=true`，既有 `O1` 口径）；按 O1 归一口径比较时 **13/13 逐字节相同**（含 17 项自检 detail、两个检查器 stdout、10 个探针 stdout 与 `probe_summary.json`）。`selfcheck_result.json` 的 `inputs.*_path` 字段因副本绝对路径不同而不同（哈希字段全等），属环境字段，不计为差异。

## 2. 自证工具 `verification/export_selfproof.py` 专项核查

**（a）是否真的用目标提交内的文件 —— 是。**
`prepare_commit_repo()` 用 `git clone --shared --no-checkout` + `checkout <rev>` 得到**真实 Git 仓库根**，`self_prove()` 只从该导出树取脚本与输入（`tree/verification/s6_g0_selfcheck.py`、`tree/.../check_stage_delivery.py`、`tree/docs/...`、`tree/.codex/STATE.md`），`--project-root` 也指向该导出树 —— `check_stage_delivery` 的 `source_commit` 只要求「解析为本地 commit 对象」（提交字节 L751–L769），导出树满足。
**运行内证据**：r06 主体跑出的是 **r06 的自检**（`C14` detail = r06 时代的 "W_min 仅下界、window_complete 为统计基准"，`C7 = 31 例`，缺 r07 的 `required_completion_index`），r07 主体才是 17 项 r07 断言、`C7 = 32 例`。二者不同即证明未混用工作树脚本。

**（b）换行口径只选换行、绝不改写内容 —— 是（两级机制都成立），但两级会互相打架。**
`align_by_manifest_hashes()` 的候选集**只是导出字节的 LF/CRLF 归一**，两者都不匹配即登记 `unresolved`；`normalize_line_endings()` 只在「与源工作树字节仅换行不同」时替换。反例 7/9 证明：**改一个非换行字节 → 登记 + 哈希失败，绝不修好**；反例 8/9 证明：**行尾整体翻转 → 正确判为口径差异**（`aligned` 计数随之变化）。

**（c）不可"洗白" —— 是。**
内容级差异在两处都被保留原字节（`unresolved` / `content_differs`，实测 `aligned` 计数随之下降）；**对清单已声明的文件**，内容差异必然触发 `C11 清单哈希不符` 或 `files[*].path SHA-256 不匹配`。工具**只会过严，不会过松**（未声明文件本就不在检查范围，非本工具的洗白路径）。

**（d）缺陷：环境依赖的假阴性（`N-r07-1`）。**
`normalize_line_endings()`（L184）在 `align_by_manifest_hashes()`（L182）**之后**执行，且对「与工作树仅换行不同」的文件**无条件写回工作树字节**，因此会把 stage A 刚对齐到清单口径的文件再翻回 `--project-root` 工作树的口径。凡工作树换行口径 ≠ `O1`（例如：本机全局 `core.autocrlf=true` 的**普通克隆**：`.py`/STATE 变 CRLF；或 Linux/`autocrlf=false` 的干净克隆：MD/JSON 变 LF），一个**本身自洽**的提交会被判 `NOT_SELF_PROVEN`（反例 10 实测 `[1,0,2]`）。实测口径与作者的开发者工作树一致时（反例 2）结论正确。⇒ 工具在"任何人从干净克隆复现"这一用途上不可靠，但**只会产生假阴性**，不影响本轮任何 PASS 结论。

**（e）`export_selfproof.json` 的不自洽（`N-r07-2`）。**
入库 `export_selfproof.json` 的 **worktree snapshot** 主体里，第 3 项 `check_stage_delivery --mode evidence` 记录 `exit 0` 但内嵌 `check_statuses[0]` 为
`{"status":"FAIL","name":"冻结自证…","reason":"…实测 subjects={commit 04ea58e1…: NOT_SELF_PROVEN, worktree snapshot…: NOT_SELF_PROVEN}"}`，
而同一目录的 `delivery_manifest.json:296-302` 与 `check_evidence_mode_output.txt` 记录同一检查为 **PASS**、且 reason 写着 `snapshot: SELF_PROVEN`。我按入库包忠实复跑（反例：`repo3`）得到的同一步输出是 **PASS**（reason 与 manifest 逐字一致）。⇒ 入库 `export_selfproof.json` 内嵌的是**更早一版清单**的评估结果（陈旧记录），与同包清单/检查器输出矛盾；且该报告主体只有 `r06` 提交与**提交前工作树快照**，**未包含交付提交 `bdcf896` 为主体**（工具设计使然：快照自证是先于提交的 bootstrap）。`bdcf896` 自证事实我已独立跑出（§1 第 2 行），但入库证据不足以"自证交付提交"。

## 3. `F1` 关闭核查 —— ✔ 关闭

- **五处统一**（提交字节）：文档 §9 L184「**第一个同时满足帧数与时长（取较晚）的帧**」、B07 L121、B27 L141 均含统一口径；JSON `behavior_rows.B07.condition`、`B27.output`、`time_anchors.window_complete`、`transitions.M3.condition`、`low_fps_latency.window_completion_definition` **五处均含**且**均不含**「第 N 个」。
- **C14 断言有判别力**：我自己注入 `B07.condition` 旧措辞 → `C14 FAIL`；注入文档 §9 旧措辞 → `C14 FAIL`；入库探针 `b07_old_wording` 我重跑亦 `exit 1 / failed=[C14]`。
- **残留检查**：全文档「第 N 个」仅 2 处，均在**历史/描述语境**（L9 = r07 修订记录在陈述「禁止残留旧措辞」；L22 = v1.1/r02 历史修订记录）；JSON / 手算样例 **0 处**。不计为缺陷。

## 4. `BLK-1(b)` 关闭核查 —— 核心正确，收尾不全（见 `BLK-r07-1`）

**已正确**：
- `reachability.M4 = REACHABLE`，`reason` 含 `TARGET_CONTINUES` / `T6-P02` / `T6-S04` 三关键词与机制链（`t_last_target_continues` 刷新、`miss_streak` 不增 → M10 不先命中），`resolution` 不再按不可达处理，另附 `evidence` / `review_correction`。
- `open_decisions.U6-12` 改写成「M4 可达并**保留**、G0 只决定兜底次序」，`note` 明确「原『去掉 M4/T6-S04』选项已撤销」。
- 文档 §4 L88、§12.1 L244、§14 参数行、§16 U6-12 行均已同步为「可达 / 保留 / 计入覆盖」。
- **C16 有判别力**：我三次注入（`M4.status` 回退不可达、`reason` 去机制关键词、`U6-12` 回退「删除 M4」）→ `C16 FAIL`，detail 分别为「必须声明为 REACHABLE」「未说明 TARGET_CONTINUES 机制」「必须改写为可达且保留」。
- **M4 确实可达（我自推导）**：只按提交内的 §3 谓词定义（`TARGET_CONTINUES` **不含** `score ≥ T6-P02`）、M4/M10 条件与草案参数做逐帧推演 —— 帧 0–2 为 `WINDOW_MATCH`（3 < S02=6，M3 不完成），帧 3 起 `same_class`/`IoU ≥ P03` 使 `TARGET_CONTINUES` 逐帧成立（锚点每帧刷新、`miss_streak=0`）而 `score=0.28 < P02` 使 `WINDOW_MATCH` 逐帧失败：**P=100 ms → M4@帧5（500.0 ms）；P=40 ms → M4@帧13（520.0 ms）；P=33.3 ms → M4@帧16（532.8 ms）**，三种周期下 **M10 始终不命中**。另按只读方式核对 S6-B r01 用例 `C4-jitter-reset` 的 `expected.transitions=["M1","M4"]`（最终 `IDLE`）作为旁证（**未评价 S6-B 实现**）。

**未闭合（阻断）**：见 §8 `BLK-r07-1` 的 8 处相反表述，其中 `hand_computed_cases.json` 的 **HC-23**（`kind="m4_reachability"`，`expected.m4_reachable_under_draft=false`，topic/derivation 仍写「M4 在草案参数下不可达；仅当 S04 < L02 时 M4 才可能先命中」）**由 C7 机器断言**，与 `reachability` + C16 结论直接相反；`docs/stage6/s6a_stage6_g0_behavior_v1.json:1654`（`parameter_notes.T6-S04`）与 `delivery_manifest.json:330` 更明确写「**不得/不计入覆盖声明**」。也就是说：**同一被审包用两个机器检查同时断言"M4 可达且计入覆盖"与"M4 不可达且不计入覆盖"**。

## 5. `F7` / HC-32 关闭核查 —— ✔ 关闭

- **字段齐全且语义正确**（提交字节 L797–L831）：完成帧超出所给序列时报 `completion_index=-1`、`window_span_ms=0.0`、`completion_within_sequence=false`，外推值单列 `required_completion_index`；`later_of_applied` 仍为 `true`（该键表达"取较晚是否真的推迟了完成帧"，与是否越界正交，不误读）。HC-28/29/31 的 `expected` 同步新增 `required_completion_index` / `completion_within_sequence`。
- **我独立复算 HC-32**（P=33.3、7 帧、S01=200、S02=6）：`count_index=5`，时长需 `ceil(200/33.3)=7` 个间隔 → `completion_index=7 > 6` ⇒ 越界 ⇒ 报 `-1/0.0/false`，`required_completion_index=7`，`m3_fires=false`，`sequence_span_ms=199.8` —— 与入库 expected 全等。
- **注入判别力**：我重跑入库探针 `case_out_of_sequence_index`（把 HC-32 预期改回 7/233.1）→ `C7 FAIL`、`exit 1` ✅。
- **旧口径实证**：直接调用 r06 版 `recompute()`，HC-32 得 `completion_index=7 / window_span_ms=233.1`；`probe_summary` 的 r06 条目描述（L151）为真。

## 6. 其余 `F` 项逐条

| 项 | 判定 | 我的核查 |
|---|---|---|
| `F2` 清单基线动态取值 | **部分关闭** | builder 已改为动态取 `source_commit`；但 `delivery_manifest.source_commit=43f7995` 与 `JSON baseline.revision_base_commit=04ea58e1`、`STATE` 11 字段「本轮修订基线 43f7995」**三处口径不一**，且 `source_commit` 内**不含**被其绑定的 r07 源码字节（`limitations[0]` 已如实说明"由该次构建的工作树生成"）。→ `N-r07-3` |
| `F3` 探针计数写实 | **✔ 关闭** | `probe_summary.composition` = 「基线 1 例 + 注入 7 例（共 8 例）+ 历史口径对照 2 例（共 10 次运行）」，`injection_count=7`、`historical_check_count=2`、`total_runs=10`；脚本 `INJECTIONS` 8 条（基线 1 + 真注入 7）与之自洽；清单 `keep_reason` 已无「8 个注入」（提交字节扫描 0 命中）；我重跑 10/10 一致 |
| `F4` r04 归因与样例数口径 | **部分关闭** | `fix_record`/`S6A_run_summary`/`selfcheck_r04_failure.json` 的 keep_reason 均已写「29 < 32，缺 HC-30/31/32」，与同包证据 `C7: 手算样例数量不足 32：29` **一致**；**残留 1 处**：`delivery_manifest.json:280` 的 `selfcheck_r04_failure_stdout.txt` keep_reason 仍写「C7 归因：样例数 **29<30**，缺 HC-30」。→ `N-r07-4` |
| `F5` STATE 陈旧行 | **部分关闭** | L8 已改为「v1.6 / r07」、11 字段行已写 r07 心跳 03:10 与恢复命令、`span_conventions_agree` 已标注为 r06 取代；**残留**：L51 仍写「**v1.4/r05** 为 `PENDING_REVIEW`」，L30/L19 两处「**本轮已完成**（v1.4/r05、v1.5/r06）」标题在 r07 包内仍称"本轮"。→ `N-r07-5` |
| `F10` 旧口径对照失败点描述 | **✔ 关闭** | `probe_summary` r05 条目（L133/L144）与 `fix_record`（L116）已写「首个 C7 失败在 HC-28（新键不可复算）；HC-31 的口径差异由 `case_span_wrong` 直接证明」；我重跑 r05/r06 历史对照实得 `c7_detail = HC-28.…无法独立复算`，`failed_checks=[C1,C7,C16]`，与入库逐字一致 |
| `F11` 键名/令牌/别名清理 | **部分关闭** | `r03_notes → review_fix_notes` ✔、`not_run` 版本改为 v1.6 ✔、`total_actions` 别名已移除（自检仅返回 `actions_within_supplied_sequence`）✔、文档已含完整令牌 `S6A-G0-v1.6`（3 处）✔、复评措辞已精确到「r06 包（`04ea58e1`）」✔；**残留**：`coverage_matrix.json:33` 仍写「§5 B01–B28（**v1.5**）」、`limitations_not_executed.json:49` 仍写「行为表 **v1.5** 规定…」。→ `N-r07-6` |
| `F8`/`F9` 有意设计登记 | **✔ 关闭** | `limitations_not_executed.review_fix_notes`（L114/L115）分别写明 `ceil(S01/P−1e−9)` 的含等号余量与「整段给定序列视为一个窗口（抖动另由 HC-12 建模）」，并标明 r04/r05 同此、`window_span_ms` 自 r06 起不参与判定 |

## 7. 无回归 / 清单 / 版本一致性（全部用提交字节）

| 检查点 | 我的实测 | 判定 |
|---|---|---|
| **24 项参数 + `PENDING_APPROVAL`** | r06(`04ea58e1`) vs r07(`bdcf896`) 逐字段（`kind/name_zh/unit/comparison/draft_value/draft_source/approval_status/approval_owner`）**差异 0**；非 `PENDING_APPROVAL` = 0 | ✅ |
| **ID 集合并集差异是否恰为声明新增** | `transitions 14→14`、`hard_invariants 10→10`、`behavior_rows 28→28`、`open_decisions 16→16`、`parameters 24→24`、`states 7→7`：**新增=[] 删除=[]**；顶层键**无增删**；样例 `31→32`，**新增恰为 HC-32**；`HC-28/29/31.expected` 仅**增键**（`required_completion_index`、`completion_within_sequence`），**既往键值变 0**；`reachability.M4` +`evidence`/`review_correction`、`U6-12` +`note` —— 全部落在声明的 `F1/F7/BLK-1` 范围内 | ✅ |
| **`artifact_version` 一致性** | JSON/`fix_record`/`coverage_matrix`/`limitations` = `S6A-G0-v1.6`，`hand_computed_cases.hand_cases_version` = `S6A-HC-v1.6`，`run_id` 全为 r07；`retained_from_r05.artifact_version = S6A-G0-v1.5`（历史保留字段，正确）；`export_selfproof.json/.md` 中的 v1.5 属 **r06 主体**（正确） | ✅（附 `N-r07-6` 两处令牌） |
| **声明存在但缺失的文件** | 清单 46 条（运行目录 38 + 外部绑定 8）**全部存在**、双向 0 缺失 0 多余、哈希（含换行归一）0 不符；`hashes_sha256.txt` **37/37** 一致；STATE 声明 37 文件 + 3 目录全部存在（C11 detail 与我重跑逐字相同） | ✅ |
| **旧包失败证据绑定** | r01–r04 `*_package_under_test.json` 各 5/5 绑定哈希与 `git cat-file blob` 复算一致；`expected_outcome=FAILED(exit 1)` 与 `observed.exit_code` 一致 | ✅ |
| **是否自称「已审查/已通过/已冻结」** | 全量扫描 r07 文档/JSON/STATE/39 证据文件：命中仅为**经我核实为真的历史引用**（「r06 包（`04ea58e1`）已通过第 6 轮独立复评」= `REVIEW_r06.md` PASS、被审提交确为 `04ea58e1`）与否定语境（「不得自称已审查/已通过」「不代表独立审查或 G0/G4/G5」）；修订记录已把措辞限定到「r05/r06 包」 | ✅ 无夸大 |
| **复跑一致性** | r07 自检 17 项 id+name+status+**detail 全等**、`errors=[]`、`id_inventory`/`limitations`/`scope_statement` 全等；两个检查器与 10 个探针 stdout + `probe_summary.json` **逐字节相同（O1 口径 13/13）** | ✅ |
| **r06→r07 差异范围** | `M`：`.codex/STATE.md`、`docs/stage6/{spec_v1.md,behavior_v1.json}`、`verification/{s6_g0_selfcheck.py,s6a_build_evidence.py}`；`A`：r07 证据 39 文件 + `verification/{export_selfproof.py,s6a_r07_probe.py}`。**r01..r06 证据目录零改动**、无夹带无关文件 | ✅ |

## 8. 本轮问题清单（格式：`位置 | 问题 | 影响 | 依据 | 关闭条件`）

### 阻断

**`BLK-r07-1` `BLK-1(b)` 收尾未扫全：同一包内同时断言 M4「可达/计入覆盖」与「不可达/不计入覆盖」**
- **位置（8 处，均为 r07 提交字节）**：
  1. `docs/stage6/s6a_stage6_g0_behavior_v1.json:1654` —— `parameter_notes.T6-S04` = 「草案 500ms ≥ T6-L02 300ms，**M4 不可达**（U6-12）；本行**不得计入覆盖声明**。」
  2. `report/evidence/S6-A/s6a_g0_20261022_r07/delivery_manifest.json:330` —— `limitations[3]` = 「M4/M7 在当前草案参数/实现结构下**不可达**（U6-12），**不计入覆盖声明**。」
  3. `report/evidence/S6-A/s6a_g0_20261022_r07/hand_computed_cases.json:447`（HC-23）—— `topic`/`derivation` 写「M4 在草案参数下不可达；仅当 S04 < L02 时 M4 才可能先命中」，且 **`expected.m4_reachable_under_draft=false` 由 C7 机器断言**（`recompute(kind="m4_reachability")` 仍按「只比 S04 与 L02 大小」的旧模型计算）。
  4. `report/evidence/S6-A/s6a_g0_20261022_r07/limitations_not_executed.json:54` —— `not_run`「M4/T6-S04 运行时行为验证」reason = 「…M4 被 M10 遮蔽、**不可达**…」。
  5. `report/evidence/S6-A/s6a_g0_20261022_r07/coverage_matrix.json:34` —— item 4 status = 「…**M4/M7 显式登记不可达**，U6-12」（同文件 `:228` 的 C16 行却写「M4 声明 REACHABLE…（BLK-1）」）。
  6. `report/evidence/S6-A/s6a_g0_20261022_r07/S6A_run_summary.md:42` —— 「…T6-A03 NOT_RUN、**M4/M7 不可达**…」。
  7. `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md:376`（§18 限制）—— 「`T6-S04`/M4 **在当前草案下不可达**（U6-12）」。
  8. `.codex/STATE.md:44` —— 「**不可达项（不计入覆盖）**：… M4/`T6-S04`（U6-12）、M7（构造上）」。
- **问题**：r07 已把 `reachability.M4`、`U6-12`、文档 §4/§12.1/§14/§16 与 C16 改成「可达且保留并计入覆盖」，但**未同步**上述 8 处（含两处**机器可读**声明与一处**机器断言样例**）。因此 `BLK-1(b)` 的"关闭"表述在被审包内**不可自洽复核**：`C7`（HC-23）与 `C16` 两个检查同时通过却结论相反。
- **影响**：① 覆盖声明自相矛盾 —— `parameter_notes`/`delivery_manifest.limitations` 明写「不得计入覆盖」，与 `U6-12` 的「保留并计入覆盖」相反，后续 G0 批准或 S6-B/6-C 覆盖统计若按前者执行会漏掉 M4/`T6-S04`；② HC-23 仍是"规则可达性"样例（§12.1 声称 r07 已修正），其 `expected` 由 C7 断言，等于把被 BLK-1 否证的结论固定进冻结包；③ 与 `F1` 的收尾标准不一致（同类文本残留本轮被要求清零）。
- **依据**：本轮 §4 的自推导（P=100/40/33.3 ms 三组 M4 均先命中、M10 始终不命中）+ 提交字节全文扫描（`scan_committed.py` 输出）+ C16/C7 注入实测 + `git diff` 确认这 8 处均未被 r07 修改。
- **关闭条件**：把 8 处统一为「M4 在本轮草案参数下**可达**、M4/`T6-S04` **保留并计入覆盖**（G0 只决定兜底次序）」；对 HC-23 二选一 ——（i）改写其 `topic/derivation/expected`（把 `m4_reachable_under_draft` 改为按 §3 谓词口径的真值，或新增 `kind` 明确区分「仅比 S04/L02 的旧模型」并与 `reachability` 交叉说明），或（ii）将其明确标注为**历史模型对照样例**并从 §12.1 的"已修正"表述中剔除；建议在 `s6_g0_selfcheck.py` 增加一条普适断言（例如：全包文本不得再出现「M4 不可达」「不计入覆盖」的非否定/非历史语境命中）。修完重跑 r07 自检应仍 `ALL_PASS`（17 项）且检查器 `CHECKS_OK`。

### 非阻断

**`N-r07-1` 自证工具存在环境依赖的假阴性（stage B 覆盖 stage A）**
- **位置**：`verification/export_selfproof.py` L112–L143（`align_by_manifest_hashes`，manifest 口径）与 L146–L170（`normalize_line_endings`，**工作树**口径），调用顺序 L182→L184。
- **问题**：stage B 在 stage A 之后、且对「与 `--project-root` 工作树仅换行不同」的文件无条件写回工作树字节；当工作树换行口径 ≠ `O1`（本机全局 `core.autocrlf=true` 的普通克隆使 `.py`/STATE 变 CRLF；Linux 或 `autocrlf=false` 的克隆使 MD/JSON 变 LF）时，会把自己刚对齐到清单口径的文件再翻回去，导致**本身自洽的提交被判 `NOT_SELF_PROVEN`**。
- **影响**：只产生**假阴性**（不会把坏包判成好包），不影响 r07 任何 PASS 结论；但使「任何冻结/交付提交必须自证」这条规则**不能由他人从干净克隆复现**（G5/后续 Reviewer 会得到相反结论）。
- **依据**：反例 10（普通克隆，`--commit bdcf896` → `NOT_SELF_PROVEN [1,0,2]`，`C11: 清单声明的源码/输入哈希不符：.codex/STATE.md`，stage A `aligned=6` 被 stage B 抵消）与反例 2/8（口径一致时 `SELF_PROVEN`）。
- **关闭条件**：让清单声明成为最终权威 —— 在 stage B 之后重跑一次清单对齐（或在 stage B 中跳过 manifest 已声明的文件）；并在工具头注/`newline_note` 写明「`--project-root` 的工作树换行口径必须与清单一致，否则结论不可用」。修完用一个刻意换行口径不同的工作树做回归（应仍 `SELF_PROVEN`）。

**`N-r07-2` 入库 `export_selfproof.json` 内嵌陈旧 `FAIL`，且未把交付提交列为主体**
- **位置**：`report/evidence/S6-A/s6a_g0_20261022_r07/export_selfproof.json`（`subjects[1].checks[2].stdout_tail` 内含 `check_statuses[0].status="FAIL"`、reason 写 `worktree snapshot…: NOT_SELF_PROVEN`）与 `export_selfproof.md`。
- **问题**：同一目录的 `delivery_manifest.json`（`checks[0]`，`:296-302`）与 `check_evidence_mode_output.txt` 记录该检查为 **PASS**、reason 写 `snapshot: SELF_PROVEN`；我按入库包忠实复跑得到 **PASS**。⇒ 入库自证报告内嵌的是**更早一版清单**的评估结果，与同包清单/检查器输出矛盾。另：报告主体为 `commit 04ea58e1` + **提交前工作树快照**，**未包含交付提交 `bdcf896`**（工具 bootstrap 使然）。
- **影响**：不影响 S6-A 规格结论；但 F6 是本轮的头条规则，其**入库证据自相矛盾**（读者会看到 "NOT_SELF_PROVEN" 与 "SELF_PROVEN" 并存），且未直接展示"交付提交自身自证"。我已独立跑出 `bdcf896 → SELF_PROVEN [0,0,0]` 与 `04ea58e1 → C11 S6-B 目录` 两个事实。
- **依据**：§1 第 2 行（`repo3` 复跑：`commit bdcf896 SELF_PROVEN [0,0,0]`，其中 snapshot 主体的 evidence 模式为 `PASS`）；`export_selfproof.json` 与 `check_evidence_mode_output.txt` 的对比。
- **关闭条件**：在清单定稿后**重跑一次自证并覆盖入库产物**（建议 `--commit 04ea58e1 --worktree-snapshot` 之外再加一条对**上一次交付提交**的 `--commit`），使 `export_selfproof.json` 与 `delivery_manifest.checks[0].reason` 的实测记录完全一致；并在报告/文档中写明 bootstrap 限制（"提交前快照 + 后续提交自证"两段式）。

**`N-r07-3` `F2` 残留：修订基线三处口径不一**
- **位置**：`delivery_manifest.json:6`（`source_commit=43f7995…`）与 `:327`（`limitations[0]` 称其为"修订基线"）；`docs/stage6/s6a_stage6_g0_behavior_v1.json:baseline.revision_base_commit=04ea58e1`；`.codex/STATE.md` 11 字段行「本轮修订基线 `43f7995`」。
- **问题**：JSON 视 r06(`04ea58e1`) 为修订基线，清单与 STATE 视 `43f7995`（构建时 HEAD，S6-B r01）为修订基线；且 `source_commit=43f7995` 内**不含**清单所绑定的 r07 源码字节（`limitations[0]` 已如实说明，但字段名仍易误读为"证据来自该提交"）。
- **影响**：仅口径/可追溯性，不影响哈希与检查（`check_stage_delivery` 只要求 `source_commit` 可解析为 commit 对象）；但三方对"修订基线"的理解不同，会误导接手方。
- **依据**：提交字节字段；`s_regression.py` §6 清单核对全通过。
- **关闭条件**：三处统一（建议 JSON/清单/STATE 均写「S6-A 修订基线 = `04ea58e1`」，另用独立字段名如 `built_at_head_commit=43f7995` 记录构建时 HEAD）。

**`N-r07-4` `F4` 残留 1 处旧归因数值**
- **位置**：`report/evidence/S6-A/s6a_g0_20261022_r07/delivery_manifest.json:280` —— `selfcheck_r04_failure_stdout.txt` 的 `keep_reason` = 「…C7 归因：样例数 **29<30**，缺 HC-30」。
- **问题**：同一清单 `:274` 与 `S6A_run_summary.md:30`、`fix_record.json:60` 均已改为「29 < 32，缺 HC-30/31/32」；同包证据 `selfcheck_r04_failure.json` 的 C7 detail 为「手算样例数量不足 **32**：29」。该处是 `F4` 关闭条件点名的位置，**未同步**。
- **影响**：自述计数与自家证据矛盾 1 处；不影响任何机器检查与结论。
- **依据**：提交字节 Python 扫描（`[manifest] 含 '29<30'：1 行`）；`selfcheck_r04_failure.json` 的 `errors[0]`。
- **关闭条件**：该串改为「样例数 29 < 32（缺 HC-30/31/32）」并重建清单/重跑 C11。

**`N-r07-5` `F5` 残留：STATE 陈旧行（活文档）**
- **位置**：`.codex/STATE.md:51`（「**S6-A 状态**：v1.4/r05 为 `PENDING_REVIEW`…」）、`:19`/`:30`（两个标题「## 本轮已完成（S6-A v1.4/r05…）」「## 本轮已完成（S6-A v1.5/r06…）」）。
- **问题**：L8 已更新为 v1.6/r07，但 L51 仍指 v1.4/r05；两处"本轮已完成"在 r07 包内仍称"本轮"，且没有 r07 本轮小节。STATE 是 r07 清单的 8 个外部绑定文件之一，也是"下一接手方"入口。
- **影响**：不触发任何检查（C11 只查 `S6-A DONE` 缺失、`DELIVERED_PENDING_*` 存在与声明文件存在性），不影响 S6-A 结论；会误导接手方按 r05 包恢复。
- **依据**：提交字节 L19/L30/L51；`git show bdcf896:.codex/STATE.md`。
- **关闭条件**：L51 改为「v1.6/r07 为 `DELIVERED_PENDING_REVIEW`」；把 r05/r06 两节改标为「历史（r05/r06）」并补/改 r07 本轮小节。

**`N-r07-6` `F11` 残留：2 处 `v1.5` 令牌**
- **位置**：`coverage_matrix.json:33`（`location` = 「§5 B01–B28（**v1.5**）…」）、`limitations_not_executed.json:49`（「**行为表 v1.5** 规定无实测 P 时…」）。
- **问题**：r07 包内现行契约是 v1.6；该两处是**非历史语境**的版本令牌（r06 轮的同类残留本轮已要求清理）。另 `S6A_run_summary.md:4`/清单 `:6` 已正确写 `43f7995`，无其他问题。
- **影响**：仅版本表述不一致；不影响检查与绑定（`artifact_version` 字段本身一致）。
- **依据**：提交字节扫描 `[coverage] 含 'v1.5'：1 行`、`[limitations] 含 'v1.5'：1 行`。
- **关闭条件**：两处改为 v1.6（或显式标注为 r06 历史口径）。

## 9. 工作区漂移清单

- **审查开始（约 03:22）**：`HEAD=bdcf896`，`git status --short` **为空**（干净）。
- **审查期间（03:24–03:35）**：另一写入方在 `w6` 中修改了 8 个已跟踪文件
  （`.codex/STATE.md`、`src/stage6/{s6_actions,s6_core,s6_params}.py`、`verification/export_selfproof.py`、`verification/s6b_{build_evidence,probe,run_cases}.py`）并新增 `report/evidence/S6-B/s6b_core_20261023_r02/`，随后**提交为 `87a6bdc`**（`fix(stage6): S6-B r02 fixes BLK-1 (M4 is reachable) and N-01..N-10; evidence regenerated with F6 self-proof`）。`HEAD` 现为 `87a6bdc9951b9fed1baf5dad85a88db288ecda6a`，`git status --porcelain` 为空。
- **对被审内容的影响**：`git diff --name-status bdcf896 87a6bdc` 中与 r07 相关的仅 **`.codex/STATE.md`** 与 **`verification/export_selfproof.py`** 两个 `M`（其余为 S6-B 的 `A`/`M`）。⇒ **本轮被审的 r07 文件在提交 `bdcf896` 内零漂移**；我全部结论以 `bdcf896` 的 `git` 字节为准，并在隔离副本内复跑（`repo`/`repo2`/`repo3` + `repo3` 的三个反例提交）。
- **我的写入**：仅 `D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01\**` 与被审工具的**系统临时目录**；**未在 `w6` 内创建或修改文件**（`w6` status 空可证）。未切换共享分支、未 commit/push 任何共享仓库（反例提交只落在隔离副本）。未接触板卡/JTAG/COM4/`hw_server`/HDMI/摄像头；未改 `main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件；未评价 S6-B/6-C 的实现与语义（仅按 `F6`/`BLK-1` 需要的范围**只读**引用 `C4-jitter-reset` 的 `expected.transitions` 作为旁证）。

## 10. 我未做的事（限制，如实登记）

- 未修改任何被审文件；未在 `w6` 内写入；未直接在被审工作树上跑 `s6a_r07_probe.py`（它会向证据目录写 `probe_*_stdout.txt`）—— 改为在**隔离副本**内复刻并**逐字节比对**入库产物（含 O1 换行口径归一，13/13 相同）。
- 未复核 r01–r06 证据目录全部文件的语义（只按本轮绑定、哈希与失败证据核对）。
- 未评价 S6-B/6-C/6-D/6-E 的实现、语义与覆盖（越界）；未验证 `REVIEW_r01..r06` 的结论正确性（只把 `REVIEW_r06.md` 当作待证伪断言，并核对其 `PASS`、被审提交 `04ea58e1`、11 项非阻断）。
- 未运行任何需要审批或越权的操作（本会话为受限子代理，无法扩权）。
- **结论只覆盖 r07（提交 `bdcf896`）**；不代表 G0/G2/G4/G5，也不代表实物或板上验收。

---

## 附：本轮证据（全部在 `D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01\`）

- `REVIEW_r07.md`（本报告）
- `build_repo3.sh` / `verify_parity.py`（与 `w6@bdcf896` 逐字节同口径隔离副本的构建与校验：`paths=1874 content_mismatch=0 missing=0`）
- `run_repo3.sh` / `faithful3_selfproof.json` / `.md` / `.log`（提交内工具复跑：`04ea58e1 [1,0,0]`、`bdcf896 [0,0,0]`、snapshot `[0,0,0]`）
- `my3_selfcheck_r07.json` / `.stdout`、`my3_inputs_mode.txt`、`my3_evidence_mode.txt`（17 项全等、检查器 stdout O1 逐字节相同）
- `my3_probe.stdout` 与 `repo3/report/evidence/S6-A/s6a_g0_20261022_r07/probe_*`（探针 10/10，与入库 13/13 逐字节相同）
- 反例：`unit_align.py`（单元：只选换行/内容登记不改写）、`run_cx2.sh` + `cx1_bad_content.json`（内容 1 字节 → `NOT_SELF_PROVEN [1,0,2]`、`unresolved`）、`run_cx3.sh` + `cx3_bad_newline.json`（行尾 LF→CRLF → `SELF_PROVEN [0,0,0]`、`aligned 41`）、`naive_bdcf896.json`（普通克隆假阴性 `[1,0,2]`）
- 判别力：`inject_c14_c16.py` + `inj_*.json/_result.json`（C16×3、C14×2 全 FAIL）、`r06_values.py`（r06 旧实现对 HC-32 报 `7/233.1`）
- 可达性：`m4_reach.py`（M4 三组周期均先命中、M10 不命中）
- 回归/一致性：`s_regression.py` + `s_regression.txt`、`scan_committed.py`、`align_manifest.py`