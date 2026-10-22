# S6-A r08 + 工具 独立终审（终审批次 A · 第 8 轮）

- **审查对象**：工作树 `D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**被审提交 `f3c537d`**
  （`f3c537d1b37646ec779e3eb6fecdc4330bb1d7e3`）。按内容判定的被审内容 = S6-A r08 主体 `902be77`、
  证据重建提交 `e3aeb09`、标签前的 `05126fd`、以及 `report/evidence/S6-A/s6a_g0_20261022_r08/**`、
  `..._r08_selfproof/**`、`docs/stage6/**`、`verification/{s6_g0_selfcheck.py,s6a_build_evidence.py,claim_verify.py,export_selfproof.py,s6a_r08_probe.py}`、`.codex/STATE.md`。
- **时间**：2026-10-23 04:37–05:05（UTC+8）。**只读**；验证只写隔离目录
  `D:\FPGA_Competition\tmp\review\FINAL_A_20261023_r01\`（自建）与系统临时目录；**未在 w6 内创建或修改任何文件**。
- **独立性**：与被审开发者、与第 1–7 轮评审者无关联。`REVIEW_r07.md` 只作**待证伪的断言**使用；
  全部结论由本轮自取提交字节（`git cat-file --batch` 导出到 `committed/<rev>/`）、自写脚本、自造反例与自跑退出码得出。
- **结论边界**：只覆盖 S6-A r08 与相关工具；**不代表 G0/G2/G4/G5**；**不评价 S6-B 实现语义**（另有终审 B）。
  涉及 S6-B 的两处只做「提交结构 / 自证规则」层面的记录（已标注）。

## 结论

# `CHANGES_REQUIRED`

- **阻断 1（`BLK-r08-1`）：`BLK-r07-1` 未真关闭** —— r07 点名的 8 处里只有 **5 处**改了；
  **第 4、5、8 处仍断言「M4 不可达 / 不计入覆盖」**（`limitations_not_executed.not_run[7]`、
  `coverage_matrix.runbook_coverage[item 4].status`、`.codex/STATE.md:61`），而包的其余部分（`reachability.M4`、
  `U6-12`、`parameter_notes`、清单 limitations、HC-23、摘要、文档 §18、C16）都说「M4 可达并计入覆盖」。
  同时新增的 **C16「全包禁语断言」既不是全包（不扫描这 3 个文件）也不是措辞稳健（只匹配字面量）**，
  我用注入实测证明它**无法防复发**（详见 §2）。
- **阻断 2（`BLK-r08-2`）：本轮新硬规则的交付物 `claim_verification.json/.md` 不可信** ——
  其 C1 断言「全包不再出现『M4 不可达』类表述 / 禁语命中 = 无」**与包内事实相反**（3 处仍在）；
  needle 列表对包内 3 条真实残留**全部漏判**；附录里标为「真实退出码」的 `exit_code` **是生成器内部的
  pass/fail 合成值，不是被声称命令的实测退出码**（C1 的命令就是检测器自身，C2 的命令从未被执行）；
  且扫描在**项目路径含 `tmp` 组件时被静默整文件跳过**（我的隔离目录正是如此 → 假 PASS）。
  另外构建器只在「run_dir 已存在 `selfcheck_result.json`」时才因声明失败中止，**首版构建会以 exit 0 发布
  `NOT_ALL_VERIFIED` 附录**（实测）。
- **非阻断 8 项**：`N-r08-1`…`N-r08-8`（F2 口径仍不统一且新增了**假陈述**；`source_commit=05126fd` **不可达**
  ⇒ 传输克隆下 r08 证据检查 exit 2、F6 自证不可复现；F4/F5/F11 残留；S6-B r03 `_selfproof` 交付件
  `NOT_ALL_SELF_PROVEN` 与提交信息相反；HC-23 的 recompute 退化为常量；无标签、冻结命名未定）。
- **已确认关闭**：`N-r07-1`（换行顺序，含旧工具假阴性复现）、`N-r07-2`（r08 `_selfproof` 自洽且以交付提交为主体）、
  `BLK-r07-1` 的**机器层面**矛盾（C7 与 C16 不再相反）、`BLK-1(b)` 的核心语义。
- **无回归**：24 项参数逐字段差异 **0**、`PENDING_APPROVAL` 24/24、ID 集合 14/10/28/16/7 **无增删**、
  样例 32→32（只有 HC-23 内容变）、`artifact_version` 一致推进到 `S6-A-G0-v1.7`/`S6A-HC-v1.7`。
- **并发推进（重要）**：审查期间（04:48:43）另一写入方在 `w6` 提交了 **`1839766 chore(stage6): freeze S6-A v1.7/r08 + S6-B r03`**
  （改动了 `verification/*` 与证据），工作树现有 **42 项未提交改动**，`HEAD=1839766`。
  本轮全部结论以 `f3c537d` 的**提交字节**为准；我另按 `git show 1839766:<path>` 复核：**上述 3 处残留在新提交里仍在**
  （grep 命中 1/1/1），故阻断结论**未被新提交取代**。

---

## 1. 我实际执行的命令与真实退出码

隔离副本一律在评审目录内；被审文件只读；`--project-root` 一律绝对路径。

| # | 命令（要点） | 真实退出码 | 结果 |
|---|---|---|---|
| 1 | `git archive`/`git cat-file --batch` 导出 `f3c537d`、`902be77`、`e3aeb09`、`05126fd`、`bdcf896`、`87a6bdc` 的相关子树到 `committed/` | 0 | 以**提交字节**为准（非工作树） |
| 2 | **干净克隆 A**（`git clone -c core.autocrlf=true`，`checkout f3c537d`）内：`python -B verification/export_selfproof.py --project-root <envA> --commit f3c537d --commit e3aeb09` | **0** | `ALL_SELF_PROVEN`；两主体均 `SELF_PROVEN [0,0,0]`；`aligned=7, unresolved=[]`、`order_note=先工作区口径、后清单口径（N-r07-1 修正）` |
| 3 | 同环境用 **r07 版工具**（`bdcf896:verification/export_selfproof.py`，我另存为 `old_tool/export_selfproof_old.py`）跑 `--commit f3c537d` | **1** | `NOT_SELF_PROVEN [1,0,2]`；`C11: 清单声明的源码/输入哈希不符：.codex/STATE.md`；`worktree_bytes.aligned=7` → **假阴性可复现，且新工具已消除** |
| 4 | **传输克隆 F**（`git clone file:///D:/FPGA_Competition`，只含可达对象）内：`git cat-file -t 05126fd` / 跑 `export_selfproof --commit f3c537d` | 128 / **1** | `fatal: Not a valid object name 05126fd`；自证 `NOT_ALL_SELF_PROVEN`，inputs/evidence 均 **exit 2**，`errors=["source_commit 未解析为本地 Git commit 对象"]` |
| 5 | **隔离副本 parity**（= `git clone --shared` + `checkout f3c537d` + 覆盖 w6 工作树字节）内按序复跑：`check_stage_delivery --mode inputs` → `--mode evidence` → `s6_g0_selfcheck.py`（`--manifest`+`--state`）→ `s6a_r08_probe.py` → `claim_verify.py --package s6a` | **0 / 0 / 0 / 0 / 0** | 自检 `ALL_PASS` **17 项**、`C7 = 32 例`、C11「实际文件 40 / 清单双向 39+9 / STATE 37 文件 + 3 目录」；探针 `PROBE_OK` 10/10 |
| 6 | **逐字节比对**：复跑产物 vs 入库（O1 归一：CRLF→LF） | 0 | `check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`、`selfcheck_c11_stdout.txt`、`probe_summary.json`、**11 个 `probe_*_stdout.txt`** 全部**逐字节相同**；`selfcheck_result.json` 仅 `inputs.*_path` 为副本绝对路径（哈希字段全等）；`claim_verification.json/.md` 仅 `generated_at` 与命令串里的 project-root 不同（声明、退出码、观察全等） |
| 7 | **反例 A**（envC，干净克隆 autocrlf=true）：把清单声明的 `r08/coverage_matrix.json` 改 **1 个非换行字节**（`1`→`9`）后提交 `ccb617a` → 自证 | **1** | `NOT_SELF_PROVEN [1,0,2]`；`unresolved=['…/coverage_matrix.json']`（**登记而不改写**）；`C11: 清单哈希不符`；evidence 模式 exit 2 |
| 8 | **反例 B**（envC）：只把清单声明的 `verification/s6_g0_selfcheck.py` 的 blob 整体 **LF→CRLF**（内容不变，blob 84366→86116 B，去换行后完全相同）提交 `4e010a4` → 自证 | **0** | `SELF_PROVEN [0,0,0]`、`unresolved=[]` ✅ |
| 9 | **单元反例**（直接调用提交内 `align_by_manifest_hashes` / `normalize_line_endings`，合成树：声明 LF 而文件 CRLF / 声明 CRLF 而文件 LF / 内容真差一字节） | 0（断言全过） | `aligned=2, unresolved=['c.txt']`，**c.txt 字节未改写**；`normalize_line_endings`：`aligned=1, content_differs=['e.txt']`，**e.txt 未改写** |
| 10 | **中间提交自证**：`export_selfproof --commit 902be77` | **1** | `NOT_SELF_PROVEN [1,0,0]`；`C11: STATE 声明的证据目录不存在：['report/evidence/S6-B/s6b_core_20261023_r03']` |
| 11 | **注入 T2a/T2b**（改 `parameter_notes.T6-S04` 后跑自检，无 `--manifest`） | **1 / 0** | T2a 出厂字面量 → `C16 FAIL`（`行为表 JSON中仍出现禁语『M4 不可达』`）；**T2b 包内真实残留措辞「M4 被 M10 遮蔽、不可达」→ `ALL_PASS`（C16 PASS）** |
| 12 | **注入 T3a/T3a2**（把出厂字面量写进 `limitations_not_executed.json`） | **0** | `ALL_PASS`；**C16 根本不扫描该文件** → 全包禁语断言不成立 |
| 13 | **注入 P1**（把字面量写进 `limitations_not_executed.json` 后跑 `claim_verify`） | **0** | 仍 `ALL_CLAIMS_VERIFIED`；实因**绝对路径含 `tmp` 组件 → 7 个被扫文件全被跳过**（扫描集为空，C1 平凡通过） |
| 14 | **无路径守卫的忠实复算**（同 needle/同白名单/同 11 个文件，去 `tmp` 守卫） | — | needle 命中 **0**；而同一套 needle 对出厂字面量命中 `['M4 不可达','不得计入覆盖']` → **对包内 3 条真实残留全漏判** |
| 15 | **构建器中止路径 T5**（合成：`selfcheck_result.json` 存在且 C16 改判 FAIL）→ `claim_verify` 后跑 `s6a_build_evidence.py` | **1 → 1** | `[claim-verify] exit=1` 后**立即中止**（未进入 inputs/evidence/迭代）✅ |
| 16 | **首版构建 T6**（删除 `selfcheck_result.json`，同上）→ `claim_verify` 后跑构建器 | **1 → 0** | 构建器**照常完成** `EVIDENCE_BUILT`，发布 `claim_verification.json` = **`NOT_ALL_VERIFIED`**，且清单 `checks` **完全不引用**该附录 → 无守卫 ❌ |
| 17 | 清单/哈希/STATE 双向核对（修正版）+ 虚假「已审查/已通过」扫描 | 0 | 见 §6/§7 |

> 我**没有**做的事：未改任何被审文件；未在 `w6` 内写入；未切换共享分支；未在被审工作树上跑探针（探针会写证据目录）
> —— 改为在隔离副本内复刻并逐字节比对；未接触板卡/JTAG/COM4/`hw_server`/HDMI/摄像头；未 push；
> 反例提交只落在我自己的 `envC` 克隆里。

## 2. `BLK-r07-1` 逐处核查（提交 `f3c537d` 字节）：**5 处改、3 处未改**

| # | 位置 | r08 状态 | 判定 |
|---|---|---|---|
| 1 | `docs/stage6/s6a_stage6_g0_behavior_v1.json` `parameter_notes.T6-S04` | 「草案 500ms ≥ T6-L02 300ms **不构成不可达依据**…M4 可达并计入覆盖；不计入覆盖的只有 B16 S_DEDUP 与 M7」 | ✔ 已改 |
| 2 | `r08/delivery_manifest.json` `limitations[3]` | 「M4 可达并计入覆盖；不计入覆盖的只有 B16 S_DEDUP（A02<K01）与 M7（构造上）（r08/BLK-1、BLK-r07-1）」 | ✔ 已改 |
| 3 | `r08/hand_computed_cases.json` **HC-23** | `expected.m4_reachable_under_draft` **= true**；新增 `target_continues_requires_score_gate=false`、`historical_earliest_m10_ms_if_score_gate=200`、`m4_earliest_ms=500`、`reachable_if_s04_lt_l02=true`；`topic`/`derivation` 已改写 | ✔ 已改（但见 `N-r08-7`：recompute 已成常量） |
| 4 | `r08/limitations_not_executed.json` `not_run[7]`（item = `M4/T6-S04 运行时行为验证`） | reason = 「当前草案 T6-S04=500ms ≥ T6-L02=300ms，**M4 被 M10 遮蔽、不可达**；已登记 reachability 与 U6-12，未运行任何状态机。」 | ❌ **未改** |
| 5 | `r08/coverage_matrix.json` `runbook_coverage[item 4].status` | 「DONE_WITH_PREDICATE_BINDING（…；**M4/M7 显式登记不可达**，U6-12）」 | ❌ **未改** |
| 6 | `r08/S6A_run_summary.md` | 「…T6-A03 NOT_RUN、**M4 可达并计入覆盖**、阶段4/5 依赖 BLOCKED…」 | ✔ 已改 |
| 7 | `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` §18 | 「…**M4 可达并计入覆盖**；不计入覆盖的只有 B16 S_DEDUP（A02<K01）与 M7（构造上）（r08/BLK-1）」；旧句「`T6-S04`/M4 在当前草案下不可达（U6-12）」**已删除** | ✔ 已改 |
| 8 | `.codex/STATE.md:61`（S6-B/S6-C 小节） | 「**不可达项（不计入覆盖）**：B16 `S_DEDUP`…、**M4/`T6-S04`（U6-12）**、M7（构造上）；见 `reachability_notes.json`」 —— 而它引用的 `s6b_core_20261023_r03/reachability_notes.json` 明写「**M4 可达并计入覆盖**」 | ❌ **未改（且与自引文件矛盾）** |

**机器层面的矛盾已消除**：入库 `selfcheck_result.json` 为 `ALL_PASS`，`C7 = 32 例`、`C16 = PASS`
（`detail = M4 可达并计入覆盖（M7 构造上不可达）；全包无 M4 不可达类禁语`），`errors=[]`；
HC-23 与 C16 结论一致。**但文本层面仍有 3 处与结论相反**，且包自身在
`revision.changes`、`coverage_matrix.review_fix_coverage`、文档 §8 修订记录、STATE L39–45 里
**四处**声称「M4 可达性口径**统一到 8 处**」——该陈述**不成立**。

### 2.1 新增 C16 禁语断言**无判别力**（我自造反例）

- 断言实现（`s6_g0_selfcheck.py` `check_reachability`）：只对 `doc_text`（.md 全文）与
  `json.dumps(data)`（行为表 JSON）查 6 条**字面量**，另对 `cases[*].expected.m4_reachable_under_draft is False` 判失败。
  ⇒ **不扫描** `delivery_manifest.json`、`coverage_matrix.json`、`limitations_not_executed.json`、`STATE.md`、摘要。
- **我的独立全包语义扫描**（`logs/final_scan.txt`）：对「r08 目录 40 文件 + `_selfproof` + `docs/stage6` + STATE +
  6 个验证器源码」共 18 处原始字面量命中，其中 **15 处是检测器 needle / 探针注入文本 / 附录元陈述 / 失败 stdout**
  （例如 `s6_g0_selfcheck.py:1526` 的 needle 元组、`s6a_r08_probe.py:94` 的注入串、`probe_summary.json:134` 的注入描述、
  `claim_verification.json:11` 的声明本身），**只有 3 处是交付语义数据里的真实残留**：
  `coverage_matrix.json:34`、`limitations_not_executed.json:54`、`.codex/STATE.md:61` ⇒ **全包禁语命中 ≠ 0**。
- **T2a**：把出厂探针字面量（`M4 不可达…不得计入覆盖声明`）写进 `parameter_notes.T6-S04` → `C16 FAIL`、exit 1 ✅
  （即“探针 `m4_unreachable_phrase` 通过”只能证明这一条字面量）。
- **T2b**：把**包内真实残留措辞**（`M4 被 M10 遮蔽、不可达`）写进同一位置 → **`ALL_PASS`、exit 0** ❌
  （needle 列表无 `M4 不可达` 子串匹配 → 漏判）。
- **T3a/T3a2**：把出厂字面量写进 `limitations_not_executed.json` → **`ALL_PASS`、exit 0** ❌（该文件不在扫描范围）。
- 结论：C16 与内容口径一样，**只覆盖「文档 + 行为表 + 手算样例」**，不是「全包」。

### 2.2 `claim_verification` 的同类漏判

包内 `claim_verification.json` 的 `S6A-C1-no-m4-unreachable` 声明「全包不再出现『M4 不可达』类表述
（含 JSON/文档/手算样例/**清单文本**/**STATE**/自检与构建器）」，`expected = 禁语命中 = 0`，
`observations = 禁语命中：无`，`verdict = VERIFIED`。**实测相反**：

| 包内真实残留行 | needle 命中 |
|---|---|
| `limitations_not_executed.json not_run[7].reason`：「…M4 被 M10 遮蔽、不可达…」 | **无（漏判）** |
| `coverage_matrix.json` item4.status：「…M4/M7 显式登记不可达，U6-12」 | **无（漏判）** |
| `.codex/STATE.md:61`：「不可达项（不计入覆盖）：…M4/`T6-S04`（U6-12）…」 | **无（漏判）** |
| （对照）出厂探针字面量 | `['M4 不可达','不得计入覆盖']` ✅ |

⇒ `ALL_CLAIMS_VERIFIED` 只说明「按一组过窄字面量、且在我这台机器上因路径守卫被整体跳过时，没有命中」。

### 2.3 附录的「真实退出码」不是真实退出码

`claim_verify.py` 的 `verify_s6a()` / `verify_s6b()` **不执行任何 per-claim 命令**：
`make_claim(..., exit_code, ..., ok)` 的 `exit_code` 是 `0 if ok else 1` 的**进程内合成值**；
C1 的 `command` 字段写的就是 `claim_verify.py` 自身（自指），C2 的 `command` 写的是
`python -B verification/s6_g0_selfcheck.py … --out <tmp>` —— 生成器从未运行它（`<tmp>` 也是占位符）。
`.md` 却打印「**真实退出码：0**」。这与本轮新硬规则「命令 + **真实退出码** + 可观察输出」不符。

### 2.4 附录扫描的路径敏感假 PASS，以及构建器中止的缺口

- `claim_verify.py` 的跳过条件 `if any(part in ("logs","tmp") for part in path.parts)` 用的是**绝对路径**。
  项目只要位于任何名为 `tmp` 的目录下（我的评审目录 `D:\FPGA_Competition\tmp\...` 即是），
  **所有被扫文件都被静默跳过**，C1 平凡通过（P1 实测：`ALL_CLAIMS_VERIFIED`、exit 0，而同一文件里就有 `M4 不可达`）。
  这是「只会产生假 PASS」的方向，对守卫类工具是危险方向。
- 构建器守卫：`if claim_run["exit_code"] != 0 and (run_dir/"selfcheck_result.json").is_file(): return 1`。
  **T5**：`selfcheck_result.json` 存在 + 声明失败 → `claim_verify exit=1` → 构建器 **exit 1 立即中止** ✅。
  **T6**：删除 `selfcheck_result.json`（= 新 RunId 首版构建）→ `claim_verify exit=1` → 构建器 **exit 0 正常完成**，
  并发布 `claim_verification.json` = **`NOT_ALL_VERIFIED`**（`S6A-C2` NOT_VERIFIED）；清单 `checks`
  **完全不引用**该附录 ⇒ 首版构建会带着未通过的验证附录交付。❌

## 3. `N-r07-1`（自证工具换行顺序）—— ✔ **真关闭**

- **顺序已改为**「先 `normalize_line_endings`（工作区口径）、后 `align_by_manifest_hashes`（清单口径）」，
  并落库 `order_note = "先工作区口径、后清单口径（N-r07-1 修正）"`（`export_selfproof.py` L183–L191）。
- **干净克隆 + `autocrlf=true`**（envA）复跑：`f3c537d` **SELF_PROVEN [0,0,0]**、`e3aeb09` **SELF_PROVEN [0,0,0]**，
  总判 `ALL_SELF_PROVEN`，exit 0 —— **不再出现假阴性**。
- **因果性证明**：同一 envA、同一提交，用 **r07 版工具**跑 → `NOT_SELF_PROVEN [1,0,2]`，
  `C11: 清单声明的源码/输入哈希不符：.codex/STATE.md`，`worktree_bytes.aligned=7`（stage B 把 stage A 刚对齐的
  7 个文件又翻回去）→ **r07 描述的假阴性可复现，且正是本轮修掉的那一步**。
- **r07 的两个反例已重复**：反例 A（1 个非换行字节）→ `NOT_SELF_PROVEN [1,0,2]`，`unresolved` 登记、
  **不改写内容**，`C11 清单哈希不符`；反例 B（只改行尾，blob LF→CRLF）→ `SELF_PROVEN [0,0,0]`、`unresolved=[]`。
  单元级同样成立（`c.txt`/`e.txt` 字节未被改写）。
- 残留（换行之外）：**未修** `--commit` 命名在传输克隆下的失败路径（见 `N-r08-1`）。

## 4. `N-r07-2`（自证报告自洽 + 交付提交主体）—— ✔ 关闭（S6-A r08）；S6-B 侧见 `N-r08-5`

- `report/evidence/S6-A/s6a_g0_20261022_r08_selfproof/export_selfproof.{json,md}`（`f3c537d` 交付字节）：
  `verdict = ALL_SELF_PROVEN`，主体 = **`commit e3aeb09…` → `SELF_PROVEN [0,0,0]`** + `worktree snapshot` → `SELF_PROVEN [0,0,0]`；
  全文 **0 处** `NOT_SELF_PROVEN`、**0 处** `"FAIL"` ⇒ **不再内嵌陈旧 FAIL**（r07 的 N-r07-2 症状消失）。
- 与清单内嵌记录一致：`delivery_manifest.checks[0]`（`status=PASS`, `exit_code=0`）reason 记录的 `subjects`
  是构建时刻的（仅快照）集合、总判 `ALL_SELF_PROVEN`；交付时刻报告多了一个同样 `SELF_PROVEN` 的提交主体，
  **无判定冲突**（仅有「引用的是旧主体集合」的陈述性陈旧，非缺陷）。
- **但**：报告命名的是 `e3aeb09`，**没有**命名交付它的 `f3c537d`（报告先于提交生成，结构上不可能自指）。
  我已独立证明 `f3c537d` 本身 `SELF_PROVEN [0,0,0]`（envA、envC 均然），故 F6 事实成立，但**入库证据不覆盖最后一步**。

## 5. `N-r07-3`…`N-r07-6` 逐条

| 项 | 判定 | 依据 |
|---|---|---|
| `N-r07-3`（F2 修订基线三处统一） | ❌ **未关闭，且新增假陈述** → `N-r08-1` | `delivery_manifest.source_commit = 05126fd`（清单 `limitations[0]` 称之为「修订基线 05126fd」并声称「F2 口径**三处统一**：manifest / STATE 11 字段 / JSON baseline **均指向同一提交**」）；实际 `STATE` 11 字段 = 「本轮修订基线 `bdcf896`」、JSON `baseline.revision_base_commit = bdcf896` ⇒ **manifest ≠ STATE = JSON**，该「三处统一」为假陈述 |
| `N-r07-4`（F4 `29<30`） | ❌ **未关闭** → `N-r08-2` | `r08/delivery_manifest.json:292` `keep_reason` 仍为「r04 失败运行 stdout 原文（C7 归因：样例数 **29<30**，缺 HC-30）」（相邻 `:286` 已改对；r07 点名的正是这一行） |
| `N-r07-5`（F5 STATE 陈旧行） | ❌ **未关闭** → `N-r08-3` | `STATE:68` 仍写「**S6-A 状态：v1.4/r05 为 PENDING_REVIEW**」；`L19`/`L30` 仍题「**本轮已完成**（v1.4/r05、v1.5/r06）」；`L70` 仍题「**证据入口（r07）**」且 `L72` 「本轮：…r07/…」；`L8` 仍写「S6-A 契约（**v1.6 / r07**）」；11 字段「允许修改范围」仍列 `…r07/**`、恢复命令仍指向 `…r07/…` |
| `N-r07-6`（F11 `v1.5` 令牌） | ❌ **未关闭** → `N-r08-4` | `coverage_matrix.json:33` `location` = 「§5 B01–B28（**v1.5**）…」；`limitations_not_executed.json:49` = 「**行为表 v1.5** 规定无实测 P 时…」（均为非历史语境，与 r07 点名位置相同） |

## 6. 无回归 / 绑定 / 声明—实际一致性（全部用提交字节）

| 检查点 | 实测 | 判定 |
|---|---|---|
| 24 项参数逐字段（`kind/name_zh/unit/comparison/draft_value/draft_source/approval_status/approval_owner`）r07→r08 | **差异 0**；非 `PENDING_APPROVAL` = **0**（24/24） | ✅ |
| ID 集合 | `transitions 14→14`、`hard_invariants 10→10`、`behavior_rows 28→28`、`open_decisions 16→16`、`states 7→7`；**新增/删除均空**；顶层键无增删 | ✅ |
| 手算样例 | `32→32`；新增/删除空；**内容有变的仅 `HC-23`**（`expected`/`topic`/`derivation`，与声明的 `BLK-r07-1` 范围一致） | ✅ |
| 版本令牌 | `artifact_version S6A-G0-v1.6→v1.7`、`hand_cases_version S6A-HC-v1.6→v1.7`、`run_id = s6a_g0_20261022_r08`；`revision.review_verdict = CHANGES_REQUIRED（1 阻断 + 6 非阻断）`、`parameter_value_changes=false` | ✅ |
| 清单双向（48 = 39 运行目录 + 9 外部绑定） | 全部存在；哈希（原字节/LF/CRLF 任一命中）**0 不符**；运行目录**唯一未声明文件 = `delivery_manifest.json` 自身**（设计使然）；**声明缺失 = 0** | ✅ |
| `hashes_sha256.txt` | **38/38** 一致；未列入者恰为 `delivery_manifest.json`、`hashes_sha256.txt` | ✅ |
| STATE 声明的证据路径（git 树判定） | `…_r07/`、`…_r08/`、`…s6b_core_20261023_r02/` **均存在** | ✅ |
| 复跑一致性 | 两个检查器 stdout、`selfcheck_c11_stdout.txt`、`probe_summary.json`、11 个探针 stdout **逐字节相同**；`selfcheck_result.json` 17 项 id/name/status/detail 全等（仅 `inputs.*_path` 为环境字段）；探针 10/10 `AS_EXPECTED` | ✅ |
| 旧包失败证据绑定 | `old_package`/`r02`/`r03`/`r04_package_under_test.json` 已由我 §6 第 5 行的 48/48 清单哈希复算覆盖（三者均在运行目录内声明），5 个绑定哈希全部命中（原字节/LF/CRLF 三口径任一）；C11 detail 亦记「外部绑定 9 个文件哈希复算通过」 | ✅ |
| 虚假「已审查/已通过/已冻结」 | 全量扫描（r08 目录 40 文件 + `_selfproof` + 文档 + JSON + STATE）：命中**全部**是**可核对的历史事实**（r04/r05/r06 确已 PASS，见各 `REVIEW_*.md`）或**否定语境**（「不代表…」「不得自称已审查」）；`not_claimed` 明写「本轮未完成独立审查」 | ✅ 无夸大 |
| C7 与 C16 一致性 | 两者均一致断言 M4 可达（机器层面不再矛盾） | ✅（附 `N-r08-7`） |

## 7. 提交结构与冻结命名（只判内容不判标签）

用 `git show --name-status` / `git diff --name-status` 核对：

- **`902be77`（r08 主体）= 中间提交，不自证。** 其 STATE 已声明 `…/s6b_core_20261023_r03`（当时不存在）。
  实测 `NOT_SELF_PROVEN [1,0,0]`，`C11: STATE 声明的证据目录不存在：['report/evidence/S6-B/s6b_core_20261023_r03']`。
  ⇒ **不得**被登记为 r08 交付提交。
- **`e3aeb09` 内容 = S6-B r03 内容 + STATE 修正 + r08 证据重建 —— 核实属实。**
  `git diff --name-status 05126fd e3aeb09` 恰为 11 个文件：`.codex/STATE.md`(1 行)、
  r08 目录的 `S6A_run_summary.md`/`claim_verification.json`/`claim_verification.md`/`delivery_manifest.json`/
  `hashes_sha256.txt`/`inputs_manifest.json`/`selfcheck_c11_stdout.txt`/`selfcheck_result.json`、
  以及两个包的 `_selfproof/export_selfproof.{json,md}`；**不含** `src/stage6/**` 与 S6-B 证据本体（它们在 `05126fd` 里）。
  ⇒ 其**标题**（`fix(stage6): S6-B r03 …`）与实际内容（同一提交里折叠了 r08 证据重建）**不一致**；但它**本身自证**
  （`SELF_PROVEN [0,0,0]`，我独立复跑）。
- **`05126fd` = amend 前的 S6-B r03 提交，且不被任何分支/标签包含（仓库**完全没有 tag**）。**
  传输克隆内 `git cat-file -t 05126fd` → `fatal: Not a valid object name`；
  而 S6-B r03 的 `_selfproof` 报告把 **`05126fd` 列为已核验主体**，r08 的 `delivery_manifest.source_commit`
  也是 `05126fd` ⇒ 任何人从干净（传输）克隆复跑 `check_stage_delivery` 都会得到
  `errors=["source_commit 未解析为本地 Git commit 对象"]`、exit 2，`f3c537d` 被判 `NOT_SELF_PROVEN`
  —— **F6 规则对 r08 交付包不可由第三方复现**（作者本机因对象库含不可达对象而通过）。

**明确结论（不改写历史的前提下）**：

1. **勘误写在**：`.codex/STATE.md`（新增「本轮勘误」小节，逐条给出 `e3aeb09`/`05126fd`/`902be77` 的
   内容与标签差异、真实命令与退出码）、`report/evidence/S6-A/s6a_g0_20261022_r08_selfproof/export_selfproof.md`
   的 `subject_note`（写明「r08 交付内容由 `e3aeb09` 承载；`902be77` 为中间提交、不自证；
   `05126fd` 为 amend 前对象、不可从远端取得」）、以及 `r08/coverage_matrix.json.review_fix_coverage`
   —— **不**用 `rebase`/`amend`/`filter-branch` 改写既有提交。
2. **最终冻结提交** 应是一个**内容上**满足下列三条的提交：① 三处 M4 残留清零（`BLK-r08-1`）；
   ② `source_commit` 指向**可达**提交、且 `_selfproof` 报告的提交主体**可达**；③ 由**传输克隆**复跑
   `export_selfproof --commit <冻结提交>` 得 `SELF_PROVEN`。命名建议：打**附注标签**
   `s6a-g0-v1.7-r08`（+ `s6b-core-r03`）指向该提交；由于报告不能自指，
   采用「冻结提交 F 自证 + 紧随的 G 提交把 F 追加为报告主体」两段式（现有做法），
   但**标签必须打在 G 上**，并在 STATE 写明「F 为交付内容、G 为自证记录」。
3. 目前 `stage6-interact-prep` **无任何 tag**，`HEAD` 已是 `1839766`（04:48:43，审查期间由另一写入方产生；
   其信息自称 freeze）。**该提交仍含上述 3 处残留**（`git show 1839766:<path>` grep 命中 1/1/1），
   故不满足冻结条件①。

## 8. 本轮问题清单（`位置 | 问题 | 影响 | 依据 | 关闭条件`）

### 阻断

**`BLK-r08-1` `BLK-r07-1` 未关闭：包内仍有 3 处断言 M4 不可达 / 不计入覆盖，且新禁语断言挡不住**
- **位置（`f3c537d` 提交字节）**：① `report/evidence/S6-A/s6a_g0_20261022_r08/limitations_not_executed.json` `not_run[7].reason`；
  ② 同目录 `coverage_matrix.json` `runbook_coverage[item 4].status`；③ `.codex/STATE.md:61`（该行还与其自引的
  S6-B `reachability_notes.json`「M4 可达并计入覆盖」矛盾）。
- **影响**：`BLK-1(b)`/`BLK-r07-1` 的「M4 可达并计入覆盖」在被审包内**不可自洽复核**：覆盖声明与
  `reachability.M4`/U6-12/C16 相反；后续 G0 批准或 S6-B/6-C 覆盖统计若按前者执行会漏掉 M4/`T6-S04`；
  且包内（`revision.changes`、`coverage_matrix.review_fix_coverage`、文档 §8、STATE L39）四处声称
  「统一到 8 处」为**假陈述**。新 C16 断言不覆盖这 3 个文件、且只匹配 6 条字面量 ⇒ 无法防复发。
- **依据**：§2 的逐处表 + 12 次注入（T2a/T2b/T3a/T3a2）+ `r08/selfcheck_result.json`（C16 PASS）。
- **关闭条件**：把 3 处改为「M4 在本轮草案参数下**可达**、M4/`T6-S04` **保留并计入覆盖**（不可达仅 B16/M7）」；
  把 C16 的禁语扫描扩到**清单/coverage/limitations/摘要/STATE**（或新增一条「全包扫描」断言），
  并把 needle 从字面量改为**语义判定**（例如匹配 `M4[^。\n]{0,20}不可达`、`不可达项（不计入覆盖）.*M4`、
  `M4.{0,10}显式登记不可达`），**白名单只放行显式标注为历史语境的整行**；
  用我给出的三条真实残留行做回归（必须 FAIL）后，重跑自检仍 `ALL_PASS` 17 项、两个检查器 exit 0。

**`BLK-r08-2` `claim_verification` 附录不可信（新硬规则的交付物本身不满足其规则）**
- **位置**：`verification/claim_verify.py`（`forbidden` 列表 L178–179、扫描范围 L181–188、跳过条件
  `if any(part in ("logs","tmp") for part in path.parts)`、`make_claim` 的 `exit_code` 合成 L62–73）；
  `report/evidence/S6-A/s6a_g0_20261022_r08/claim_verification.json`（`S6A-C1…`）与 `.md`（「真实退出码：0」）；
  `verification/s6a_build_evidence.py:300`（中止守卫）。
- **问题**：① C1 的断言「全包不再出现…禁语命中 = 0」**与包内事实相反**（3 处残留，且 3 条真实残留
  对 needle 全部漏判）；② 附录字段名/打印为「真实退出码」，实际是生成器内部的 `0 if ok else 1` 合成值，
  且 C1 的命令是检测器自身（自指）、C2 的命令从未执行；③ 项目路径含 `tmp` 组件时**全部被扫文件被静默跳过**，
  C1 平凡通过（假 PASS 方向）；④ 构建器只在 run_dir 已有 `selfcheck_result.json` 时中止，
  **首版构建会以 exit 0 发布 `NOT_ALL_VERIFIED` 附录**，且清单 checks 完全不引用该附录。
- **影响**：新硬规则「任何『已关闭/已落盘/已同步』声明必须附命令 + **真实退出码** + 可观察输出」
  在 r08 交付包里被**形式满足、实质未满足**；读者会以为「全包禁语 = 0」已被独立验证。
  本轮所有下游 PASS 结论若引用该附录，都是无依据的。
- **依据**：§2.2/§2.3/§2.4；P1（路径守卫）、misc A（去守卫后 needle 命中 0）、T5（有结果时中止 ✅）、
  T6（无结果时 exit 0 + `NOT_ALL_VERIFIED` ❌）。
- **关闭条件**：needle/扫描范围按 `BLK-r08-1` 收紧；`exit_code` 改为**实际 subprocess 退出码**
  （每条声明真的跑一次并把 `returncode` 落库），不再由布尔合成；路径守卫改用**相对 run_dir 的路径**判定；
  构建器改为「`claim_verify` 失败即中止（含首版）」；清单 `checks` 增加一条引用
  `claim_verification.verdict` 的检查（非 `ALL_CLAIMS_VERIFIED` 即 FAIL）；修完重跑并覆盖入库附录。

### 非阻断

| 编号 | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| `N-r08-1` | `r08/delivery_manifest.json.source_commit`、`inputs_manifest.json.source_commit`= `05126fd`；`limitations[0]` 的「三处统一」；`r08_selfproof` 未含 `f3c537d`；S6-B r03 `_selfproof` 未含可达提交 | `05126fd` **不被任何 ref 包含**（仓库无 tag）；「三处统一」与 STATE/JSON 的 `bdcf896` 不符 | 传输克隆下 r08 inputs/evidence **exit 2**（`source_commit 未解析为本地 Git commit 对象`）⇒ `f3c537d` 第三方复跑 `NOT_SELF_PROVEN`，F6 不可复现；且 `f3c537d` 自身未入任何报告主体 | §1 第 4 行（envF）、§7 | `source_commit` 改为可达提交；报告主体只用可达提交（或显式登记 `05126fd` 为不可达历史对象）；给冻结提交打附注标签；从传输克隆复跑 `SELF_PROVEN` |
| `N-r08-2` | `r08/delivery_manifest.json:292` `keep_reason` | 仍写「样例数 **29<30**，缺 HC-30」 | 与同包 `:286`、`fix_record`、`selfcheck_r04_failure.json`（「不足 32：29」）矛盾 1 处 | §5 `N-r07-4` | 改为「29 < 32（缺 HC-30/31/32）」并重建清单/重跑 C11 |
| `N-r08-3` | `.codex/STATE.md` L8/L19/L30/L68/L70/L72 与 11 字段行 | 「v1.4/r05 为 PENDING_REVIEW」；两个「本轮已完成」标题未标注历史；「证据入口（r07）」；契约仍写 v1.6/r07；允许范围/恢复命令指向 `…_r07/` | 接手方会按 r05/r07 恢复；STATE 是 r08 清单的 9 个外部绑定之一 | §5 `N-r07-5` | L68 改 v1.7/r08；r05/r06 小节标「历史」；补 r08「证据入口」小节；11 字段与恢复命令指向 r08 |
| `N-r08-4` | `coverage_matrix.json:33`、`limitations_not_executed.json:49` | 非历史语境的 `v1.5` 令牌 2 处 | 版本表述不一致 | §5 `N-r07-6` | 改为 v1.7 或显式标注为历史口径 |
| `N-r08-5`（**S6-B 记录层，不评语义**） | `report/evidence/S6-B/s6b_core_20261023_r03_selfproof/export_selfproof.json`（由 `f3c537d` 交付） | `verdict = NOT_ALL_SELF_PROVEN`；`worktree snapshot` 主体 `exit=2`，`errors=["files[54].path SHA-256 不匹配…"]`（S6-B r03 清单绑定了构建时的 `STATE.md`，之后 STATE 变更 → 快照口径失效） | 与 `e3aeb09`/`f3c537d` 提交信息「the sibling `_selfproof/` report (ALL_SELF_PROVEN 0,0,0,0)」**相反**；交付树里带着一个「未全自证」的报告 | §4 + `D` 明细 | 提交信息与文件二者对齐；报告对「快照口径失效」写明原因；冻结时重跑并覆盖 |
| `N-r08-6` | `s6a_r08_probe.py` 头部/`probe_summary.json.artifact` | `artifact = "s6a_r07_discrimination_probe"`、`purpose` 写「再允许 **r07** 出 ALL_PASS」 | 仅标签陈旧，不影响判定（入库与复跑一致） | §1 第 5/6 行 | 改为 r08 |
| `N-r08-7` | `verification/s6_g0_selfcheck.py` `recompute(kind="m4_reachability")`（L737–755） | `m4_reachable_under_draft` **硬编码 True**，`s04/l02` 只用于对照值 | HC-23 的「C7 机器断言」退化为「比较常量」，不再独立推演可达性（事实本身我已独立确认可达：P=100/40/33.3 ms 下 M4 分别于 500/520/532.8 ms 先命中、M10 始终不命中） | §2 表 #3 + r07 的自推导 | 要么删掉该样例、把可达性交由 `reachability`+C16 承担；要么把 recompute 改为按 §3 谓词逐帧推演（输入参数真参与判定） |
| `N-r08-8` | 分支 `stage6-interact-prep`；`HEAD=1839766` | **无任何 tag**；审查期间另一写入方推进到 `1839766`（04:48:43）且仍有 42 项未提交改动；`1839766` 仍含 §2 的 3 处残留 | 冻结版本不可由标签定位；并发写入期间任何「已冻结」表述都不可靠 | §7、`git branch -a --contains`、`git tag -l` | 按 §7 结论打附注标签并复核残留清零；写入方与 Reviewer 之间明确交接时点 |

## 9. 工作区漂移与我的写入范围

- **审查开始（04:37）**：`HEAD=f3c537d`，`git status --short` **为空**。
- **审查期间（04:48:43）**：另一写入方提交 **`1839766 chore(stage6): freeze S6-A v1.7/r08 + S6-B r03`**
  （改动 `verification/{s6_g0_selfcheck,check_stage_delivery,s6a_build_evidence,s6b_build_evidence}.py` 与两包证据；
  信息自称已加 STATE 勘误与 C16 历史白名单）。核验时 `HEAD=1839766`、未提交改动 **42 项**、`index.lock` **不存在**。
- **对被审内容的影响**：本轮结论**全部以 `f3c537d` 及更早提交的字节为准**（我已 `git cat-file` 导出固定），
  并且在 `1839766` 上复核：§2 的 3 处残留**仍在**。
- **我的写入**：仅 `D:\FPGA_Competition\tmp\review\FINAL_A_20261023_r01\**`（envA/envC/envF/parity 四个隔离克隆、
  `committed/<rev>/` 提交字节导出、`logs/`、本报告）与系统临时目录。**未在 `w6` 内创建或修改任何文件**；
  未切换共享分支；未 commit/push 任何共享仓库（反例提交只在 `envC`）；未接触硬件。

## 10. 我未做的事（限制，如实登记）

- 未修改任何被审文件；未在 `w6` 内写入；未在被审工作树上运行会写证据目录的探针（改为隔离副本复刻 + 逐字节比对）。
- **未评价 S6-B 实现语义、6-C 用例覆盖与 S6-B 探针**（越界；`N-r08-5` 只记录自证文件与提交信息的矛盾）。
- 未复核 r01–r06 证据目录全部文件的语义（只按本轮绑定、哈希与失败证据核对）。
- `claim_verify` 的 C1 在我这台机器上因路径守卫**无法被真正执行**（§2.4 已如实说明），
  因此「`ALL_CLAIMS_VERIFIED` 与我的实测一致」这句话只在「退出码层面」成立、**在声明实质层面不成立**。
- 未运行任何需要审批或越权的操作（受限子代理，无法扩权）。
- **结论只覆盖 S6-A r08 与相关工具**；不代表 G0/G2/G4/G5，也不代表实物或板上验收。