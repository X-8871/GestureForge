# 冻结增量复核（定向解冻后的增量轮 C）— 结论 `CHANGES_REQUIRED`

- 复核对象：`D:\codex-worktrees\w6`（分支 `stage6-interact-prep`，HEAD = **G4 = `f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d`**，`git status --short` 空、`git diff HEAD` 空）
- 被审增量：**F = `0725d9cf48aeed21d3ea445ef01575c16b68d950` → F4 = `6b8e5f2a23ce6f7dec41fc9992141b3423612081`**（117 文件，+18447 / −52）
- 复核写入：`tmp/review/FREEZE_DELTA_C_20261023_r01/`（含传输克隆 `clone/`、脚本 `s0*.py`、日志 `clone_checks.log`）；**未写 w6**（终检 `git status --short` 仍为空）
- 结论适用范围：**仅 F→F4 增量与重新冻结的四个硬条件**；不重评已审语义、不代表 G0/G2/G3/G4/G5 或实物验收
- 刻意未执行：全量 `tool_self_tests.py`（约 20 分钟/次）、任何综合/实现/上板/烧录

---

## 一、B-1（假证书）是否真关闭 —— **是，机制与判别力均成立**

| 要求 | 落地位置 | 判定 |
|---|---|---|
| `results.append` 在循环体内 | `verification/claim_verify.py:182`（`for claim in claims:` 第 172 行；原 `return 1` 前的 `if readonly_guard` 早退已删除，改为逐条 `ok = (exit_code == expect) and not _changed` 并把违反记入 `readonly_violation`） | ✅ |
| 断言①「`claims` 数量 == 定义数 + 1」 | `:169-170,213-215`（`declared=len(claims)`、`expected_count=declared+1`、`count_ok`，不符则打印 `[COUNT-ASSERT]`） | ✅ |
| 断言②「verdict 由**全部** claim 计算；空列表/数量不符 → `NOT_ALL_VERIFIED`」 | `:218-219`（`all_ok = bool(results) and count_ok and all(...)`） | ✅ |
| 「verdict 由全部 claim 计算」不可再用单条通过蒙混 | `:237` 输出 `verdict`；`:254` 退出码随之 | ✅ |

**我自己跑的两条必 FAIL 例（在传输克隆内，非 w6）**

| 注入 | 真实退出码 | 产物判定 | 逐条细节 |
|---|---|---|---|
| `--simulate-defect count_mismatch` | **1** | `NOT_ALL_VERIFIED`，`count_ok=false`，`claims_recorded=6`（期望 7） | stdout 含 `[COUNT-ASSERT] claims 数量不符：记录 6，期望 7（定义 6 + 1）` |
| `--simulate-defect empty` | **1** | `NOT_ALL_VERIFIED`，`count_ok=false`，`claims_recorded=0` | stdout 含 `[COUNT-ASSERT] … 记录 0，期望 7`；`{"verdict": "NOT_ALL_VERIFIED", "claims": []}` |

**克隆内附录计数 ↔ 入库一致性（硬条件①，我自己跑）**

| 包 | 克隆内实测（退出码） | 入库（F4/G4 树内） | 一致？ |
|---|---|---|---|
| S6-A `s6a_g0_20261023_r10` | `exit 0`；`ALL_CLAIMS_VERIFIED`；declared=6 / recorded=**7** / count_ok=True；C1..C6 全 VERIFIED + `self_test_false_claim` exit 1 | 同（declared 6 / recorded 7 / count_ok true / ALL_CLAIMS_VERIFIED） | ✅ |
| S6-B `s6b_core_20261023_r05` | `exit 0`；`ALL_CLAIMS_VERIFIED`；declared=4 / recorded=**5**；C1..C4 VERIFIED + 假声明 exit 1 | 同（4 / 5 / true） | ✅ |

⇒ **上一轮的「1 条 claim 却写 ALL_CLAIMS_VERIFIED」已彻底消除**：两份附录在干净传输克隆里可复现、计数正确、verdict 由全部 claim 计算，且对"数量不符/空列表"两处人工缺陷都有真实的必 FAIL 判别力。

---

## 二、增量范围 F → F4 —— **未发现越界语义/阈值改动**

`git diff --name-status 0725d9cf 6b8e5f2` = 117 文件：109 个 `report/evidence/**`（新 RunId r10/r05 及其 `_selfproof`、G/G2 追加的 r09/r04 `_selfproof`）+ 8 个非证据文件：

| 文件 | 改动 | 判定 |
|---|---|---|
| `verification/claim_verify.py` | B-1 修复 + 两条断言 + `--simulate-defect` + POSIX 相对路径 | 已声明 |
| `verification/s6_g0_selfcheck.py` | **C11 区分文件/目录**（`.json/.md/.txt/.jsonl` → 按项目根文件校验，其余仍按目录）；另：`S6A-G0-v1.8` 允许 `{r09, r10}` 两个 RunId（`check_identity`） | C11 已声明；**RunId 放宽未在字面清单内**（见 N-C5，语义无影响） |
| `verification/s6a_build_evidence.py` | claim 步骤移入 FIXPOINT 循环（附录须先于清单） | 属 B-1 修复的必要顺序修复 |
| `verification/s6b_build_evidence.py` | `known_limitations` 增 2 条 + 空行 | 已声明（限制登记） |
| `verification/tool_self_tests.py` | 自证用例固定指向**交付提交**（`tag r3 → r2` 的 `^`），新增 2 条必 FAIL 例，`--run-dir` 默认改 r10 | 已声明（但引入阻断项 BLK-C2） |
| `verification/s6b_fresh_evidence_twice.py`（新增） | S6-B 新鲜证据两步 | 已声明 |
| `.codex/STATE.md` | 取代关系与偏离记录 | 已声明（记录不准，见 N-C1） |
| `docs/stage6/s6a_stage6_g0_behavior_v1.json` | **仅 2 处**：`run_id` r09→r10、`status_label` v1.6(r07 收尾版)→v1.8(r10 冻结版) | 已声明 |

**24 项参数逐字段比对（F vs F4）**：ID 集合相等，**有差异的参数 0 条**，`PENDING_APPROVAL` **24/24 → 24/24**，F4 非 PENDING 项 = `[]`。
**行为表深比对**：全树差异 **2 条**（`run_id`、`status_label`）；`transitions[M4].reachability` 等 7 个容器 ID 集合与字段**均未变**（M4=REACHABLE 在 F 已成立，本轮无再改）。
`src/stage6/**`、`docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` **零改动**。

⇒ **无越界阈值/参数/行为表语义改动**；`run_id` 变化属新 RunId 的指针更新，`status_label` 属 N-4 登记。

---

## 三、中间态、tag 完整性与 amend 偏离

### 3.1 tag / 可达性核对表（全部 tag 为 annotated，`%(objectname)` 是 tag 对象；下表为 peel 结果）

| tag | tag 对象 | `tag^{commit}` | 相对旧版 | 判定 |
|---|---|---|---|---|
| `s6a-g0-v1.8-r09` | `db805635` | **`1e2a66c`（G）** | 未移动 | ✅ |
| `s6b-core-r04` | `57eb012d` | **`1e2a66c`（G）** | 未移动 | ✅ |
| `stage6-freeze-20261023` | `90dda337` | **`1e2a66c`（G）** | 未移动 | ✅ |
| `stage6-freeze-20261023-r2` | `242b96aa` | `8ecd92cb`（G2） | 新增 | ✅ |
| `stage6-freeze-20261023-r3` | `6aa82ce2` | **`f5b749e`（G4）** | 新增 | ✅（指 G4） |

### 3.2 提交可达性（w6 与传输克隆）

| 提交 | 身份 | `cat-file -t`（w6 / 克隆） | 自 HEAD=G4 可达 |
|---|---|---|---|
| `0725d9cf…` | F | commit / commit | ✅ |
| `1e2a66c…` | G | commit / commit | ✅ |
| `33b1fee…` | F2 | commit / commit | ✅ |
| `8ecd92cb…` | G2 | commit / commit | ✅ |
| `efb9f191…` | F3 | commit / commit | ✅ |
| `6b8e5f2…` | F4 | commit / commit | ✅ |
| `f5b749e…` | G4 | commit / commit | ✅ |
| `66f45dd4…` | **被 amend 掉的旧 F3** | commit / **exit 128（克隆内不存在）** | ❌ |

### 3.3 amend 偏离的**真实**成因（reflog 实证，与 STATE 记述不符）

```
2026-10-23 08:24:07  66f45dd  commit:        fix(stage6): F3 = claim C5 reads the in-package self-test artifact …
2026-10-23 08:25:07  efb9f191 commit (amend): 同一 subject      ← F3 被 amend
```
- 被 amend 的是 **F3**：`66f45dd`（旧）→ `efb9f191`（新，即当前 F3）。**F2 从未被 amend**（reflog 无此记录），且 `--commit F2` 在传输克隆里 **`ALL_SELF_PROVEN [0,0,0]` / `[0,0,0,0]`，退出码 0** ⇒ **F2 一直可达且可自证**。
- 真正失去可达性的是 `66f45dd`；而 **F3（`efb9f191`）的树内** r10/r05 清单 `source_commit = 66f45dd…`（构建在 amend 之前、HEAD=66f45dd 时取的值），因此 `export_selfproof --commit F3` 在克隆内 **`NOT_SELF_PROVEN [0,2,2]`（S6-A）/ `[0,0,2,2]`（S6-B），退出码 1** —— 这与 STATE 所述"包内 source_commit 解析失败"的现象一致，**只是受影响的包在 F3 而非 F2**。
- 各中间态清单里的 `source_commit` 实测轨迹：F2 树 = `1e2a66c`(G)→G2 树 = `1e2a66c`→F3 树 = `66f45dd`(**不可达**)→**F4 树 = `efb9f191`(F3，可达)**；G4 树同 F4。
- **F4 与其两个 `_selfproof` 的引用全部可达**：F4/G4 树内 `source_commit = efb9f191…`（可达）；r10/r05 `_selfproof` 主体在 G4 = `commit_6b8e5f2a23…`（=F4，可达）；在 F4 时的 `_selfproof` 主体 = `commit_33b1fee…`（=F2，可达且实测可自证）。⇒ **"引用不可达提交"的模式在冻结提交 F4/G4 上已消除**；残留仅存在于被取代的中间提交 F3。

### 3.4 偏离记录判定（问题 N-C1，非阻断但必须改准）

STATE（G4）写：「…说明：**F3 的一次 amend 曾使 F2 失去可达性** ⇒ 包内 `source_commit` 解析失败（传输克隆 exit 2）；本轮最终以 F3 为基线重建，故 F2/F3/F4/G4 **全部可达**。」
- 未"悄悄略过"：amend 与"source_commit 解析失败"都写出来了 ✅
- 但**归属错误**：F2 从未失去可达性（实测自证通过）；失去可达性的是 amend 前的 F3 `66f45dd`，而该哈希在冻结记录里**完全没有出现** ⇒ 记录不可审计。
- STATE 另把 `efb9f191`（=**amend 之后**的 F3）称作"被 amend 前的中间态"，措辞相反。
- **可复现性影响**：F4/G4 **无影响**（所有引用可达、双侧自证实测通过）；F3 本身无法自证（已由 F4 取代，非冻结提交）。任务卡前言所述"包内 source_commit=F2"亦与实证不符（F2 树的清单 `source_commit` 是 `1e2a66c`）。

**取代关系记录**：STATE 确实写明了 `F/G → F2/G2（tag r2）→ F4/G4（tag r3）`，并声明"旧 tag 保留指向各自提交不删不动"；实测 tag 未被移动 ⇒ **取代链本身记录到位**，只需修正 amend 归属。

---

## 四、四个硬条件核查

| # | 硬条件 | 我的实测（传输克隆 `git clone --no-local --branch stage6-interact-prep`） | 判定 |
|---|---|---|---|
| ① | 克隆内两份附录可复现且计数正确 | S6-A：7 = 6+1，`ALL_CLAIMS_VERIFIED`，exit 0；S6-B：5 = 4+1，`ALL_CLAIMS_VERIFIED`，exit 0（与入库逐字段一致） | ✅ |
| ② | `--commit F4` 双侧 `ALL_SELF_PROVEN` | `--commit F4` → `[0,0,0]` exit 0；`--commit F4 --s6b-run …r05` → `[0,0,0,0]` exit 0 | ✅ |
| ③ | `--commit G4` 双侧 `ALL_SELF_PROVEN` | `--commit G4` → `[0,0,0]` exit 0；`--commit G4 --s6b-run …r05` → `[0,0,0,0]` exit 0 | ✅ |
| ④ | **只需核对**入库 `tool_self_tests.json` 的 10 条记录与 `selfproof_valid_commit` 是否解析到 F4 | 入库产物（r10 与 r05 **同字节**，sha256 `92a07149…`）：10 条记录，其中 **`selfproof_valid_commit` = `"skipped": true`、`exit_code: null`**，note 写「未解析到交付提交（tag `stage6-freeze-20261023-r2` 缺失）：该例跳过并标注，不得据此认为套件全绿」。**未解析到 F4** | ❌ **未达成** |

补充（同一条件的能力侧）：`w6/tmp/6/tool_self_tests.json`（mtime **08:32**，非入库）显示该套件在 HEAD=G4 下的真实运行结果为 **10/10 `ALL_AS_EXPECTED`**，且 `selfproof_valid_commit` **已解析到交付提交 `6b8e5f2a23`、exit 0** —— 即工具侧修复有效，但**该结论只在 `tmp/`，没有随包入库**，而入库的是更早（08:14）的 `skipped` 版本。STATE `:163` 的「套件在 HEAD=G4 时 10/10」指的就是这个 `tmp/` 运行。

---

## 五、无回归 / 无夸大 —— 发现两处**新的机读自相矛盾**与一处文档失真

### 🔴 BLK-C1（阻断）：冻结 r10 包内 `fresh_selfcheck_pair.json` 的 verdict 是 **`FAILED`**，且被清单绑定

- 位置：`report/evidence/S6-A/s6a_g0_20261023_r10/fresh_selfcheck_pair.json`（**入库、被 `delivery_manifest.json` 以 `sha256=fd6fda19c5f1969c279892c62652862133133e70de2ec4080d01da52eda7b246` 绑定**）
- 内容：`first/second` 均 `exit_code: 1`、`status: FAILED`、`c11: FAIL`、`errors: ["C11: 清单哈希不符：claim_verification.json"]`，`verdict: "FAILED"`
- 矛盾面（同一冻结包内）：
  1. `claim_verification.json` 的 **S6A-C6** 声明「构建结束后新鲜自检两次（间隔 30s）**均 ALL_PASS**」并记 `exit_code 0 / VERIFIED`，其 "observable" 只指 `tmp/6/fresh_selfcheck_pair.json`（**不入库**）；
  2. `check_evidence_mode_output.txt` 四项全 PASS；
  3. 我在干净传输克隆内实跑同一条工具：`{"verdict": "BOTH_ALL_PASS", "first": [0,"PASS"], "second": [0,"PASS"]}`（exit 0）⇒ 入库的 `FAILED` 是**陈旧记录**（生成于 08:11，早于 08:28 的 FIXPOINT 重建）。
- 影响：冻结包以自身绑定的证据宣称"构建后新鲜自检失败"，对外部消费者无法在包内自洽解释；S6-A 侧的"新鲜两步"结论在包内**没有**绿色证据（S6-B 侧的 `s6b_fresh_evidence_pair.json` 为 `BOTH_CHECKS_OK`，正常）。
- 关闭条件：在**不就地改写 RunId** 的前提下，把与入库清单绑定的该文件替换/更正为真实的 `BOTH_ALL_PASS` 产物（新 RunId 或带哈希的更正记录 + 重生成清单），并在 `limitations_not_executed.json` 登记"该文件曾为陈旧 FAILED"；同时按 BLK-C2 修好工具后重跑。

### 🔴 BLK-C2（阻断）：新自测套件会**写坏冻结的 run-dir**（与本轮"第 5 次同源教训"同类）

- 位置：`verification/tool_self_tests.py:142-149`——两条新增必 FAIL 例调用 `claim_verify.py` 时传入 **真实 `--project-root root` + 真实 `--run-dir run_rel`**；而 `claim_verify.py:240-251` **总是**把 `claim_verification.json/.md` 写回该 run-dir。同文件 `:100-127` 的"正常跑"例却明确用 `tempfile` 副本并注释「绝不触碰真实附录」——**两条新例绕过了该不变式**。
- 实证（我的传输克隆，非 w6）：按套件同样的参数跑 `--simulate-defect count_mismatch/empty` 后，`clone` 的 `git status --short` 出现
  `M report/evidence/S6-A/s6a_g0_20261023_r10/claim_verification.json`、`…md`、`M report/evidence/S6-B/s6b_core_20261023_r05/claim_verification.json`、`…md`；r10 附录被留在 `NOT_ALL_VERIFIED / claims=[]`。⇒ **跑一次套件就会破坏两个冻结附录与其清单绑定**。
- w6 侧的吻合轨迹（只读 mtime/content 观测 + 推断，非我执行）：`tmp/6/tool_self_tests.json` mtime **08:32**（说明套件在 HEAD=G4 下于 w6 真实跑过一次，该产物含 `empty` 例的 `{"verdict":"NOT_ALL_VERIFIED","claims":[]}` 输出）→ `tmp/6/fresh_selfcheck_1/2.json` 08:33/08:34 与 `fresh_selfcheck_pair.json` **08:34** 均报 `C11 清单哈希不符：claim_verification.json`（**与包内 FAILED 文件逐字节相同**）→ `report/evidence/S6-A/…r10/claim_verification.json` mtime **08:34**（晚于 F4/G4 提交的 08:29/08:31:50）却仍是 08:28:56 的内容（= HEAD 版本）。**推断**：该次套件运行改写了工作区附录，随后被恢复（`git status` 现为干净）。⇒ 这与 BLK-C2 的机制一致，是 BLK-C1 的最可能成因；同时说明"冻结时各跑一次套件"这一既定流程与"冻结后禁止再改 run-dir"**结构性冲突**。（机制本身已在克隆内独立证实，不依赖该推断。）
- 关闭条件：两条必 FAIL 例改为在 `tempfile` 副本内运行（与"正常跑"例同口径），或让 `claim_verify` 支持 `--out-dir` 使附录可写到临时目录；随后在 HEAD=G4 上重跑套件确认 run-dir 哈希**不变**（`git status` 干净）。

### 🔴 BLK-C3（阻断）：硬条件④的入库证据不成立，且套件判定对 `skipped` **fail-open**

- 入库 `tool_self_tests.json` 把未执行的自证例记为 `verdict: "AS_EXPECTED"`（`tool_self_tests.py:89-92`），而套件总体判定只要求"每条都 AS_EXPECTED"（`:163`）⇒ **一条关键用例被跳过也能给出 `ALL_AS_EXPECTED` / exit 0**；`claim_verify.py` 的 S6A-C5 又只断言 `d['verdict']=='ALL_AS_EXPECTED' and not bad` ⇒ 整条机读链把"未执行"变成"绿"。这正是本轮被解的 B-1 同型问题（把未验证写成通过）。
- 同时 STATE `:163` 的「套件在 HEAD=G4 时 10/10」**与入库产物矛盾**（入库为 9 执行 + 1 跳过），其依据是不入库的 `tmp/6/tool_self_tests.json`。
- 关闭条件：① 在 HEAD=G4（含 tag r3）上重跑套件并把产物入库，使 `selfproof_valid_commit` 解析到 F4 且 `exit_code 0`；② 套件 verdict 区分"跳过"（如 `INCOMPLETE`/`skipped>0` 不得为全绿），S6A-C5 增加"0 跳过"断言；③ 若坚持保留跳过分支，则必须在 `limitations_not_executed.json` 明确"该条未执行"并停止使用"10/10"表述。

### 非阻断

| 编号 | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| N-C1 | `.codex/STATE.md`（定向解冻段） | amend 归属错误：写成"F3 的 amend 使 **F2** 失去可达性"；未给出真正的 `66f45dd…`；并把 `efb9f191`（amend 后）称"被 amend 前" | 冻结记录不可审计 | reflog 08:25:07 `commit (amend)` 66f45dd→efb9f191；克隆内 `--commit F2` 双侧 exit 0、`cat-file -t 66f45dd` exit 128 | 改为"amend 前的 F3 `66f45dd…` 失去可达性；F2 始终可达"并保留哈希 |
| N-C2 | `report/evidence/S6-A/…r10/fix_record.md:14` | N-r08-1 的关闭证据写作 `transport_clone_check.json`，但该文件**全树只有 `tmp/6/transport_clone_check.json`**（工具默认 `--out tmp/6/…`），未入库 | "已入库"式引用失真 | `find` 全盘仅 tmp 命中；`transport_clone_check.py` 默认 out | 入库该产物或改引可入库证据 |
| N-C3 | `…r10/delivery_manifest.json` | 2 条 check 为 `NOT_RUN（reason=首版清单生成后立即实跑）`，而 `check_evidence_mode_output.txt` 四项全 PASS | 低估而非夸大（r09 同型，非本轮引入） | 清单 vs 检查器 stdout | 收敛后重写这两条状态 |
| N-C4 | `…r10/fix_record.json`、`S6A_run_summary.md`、`tool_self_tests.py` | `revision_discipline.new_run_id` 仍是 `s6a_g0_20261022_r07`；摘要/记录标题仍写 "v1.8 / r09"；`--delivery-commit` 帮助文本仍写"默认取 r2 的父提交 = F2"（代码已优先 r3，`r3^`=F4），跳过分支的 note 也硬编码"r2 缺失" | 机读/人读字段指向错版本 | 三处字面 | 同步为 r10 / r3 |
| N-C5 | `verification/s6_g0_selfcheck.py` `check_identity` | `S6A-G0-v1.8` 的 `expected_runs` 放宽为 `{r09, r10}`（未在任务卡字面清单内；属追加 RunId 的必要让步） | 身份检查略放松 | diff `:202-215` | 总控在声明中补登记（或改为 `expected_runs` 列表 + 显式理由） |
| N-C6 | `…r05_selfproof/transport_clone_selfproof.json` | 位于 S6-B 目录但 `task_id` 写 `S6-A` | 观感 | 文件内容 | 下轮统一 |

**"无回归/无夸大"其余项判定**：24 项参数逐字段全等且全 `PENDING_APPROVAL` ✅；无把 `NOT_ALL_SELF_PROVEN` 写成通过（G4 两份自证主体均为 F4，`verdict=SELF_PROVEN`）✅；`tool_self_tests.json` **确已随两个包入库**（非仅 tmp）✅；w6 未被本轮复核改动 ✅。

---

## 六、结论与清单

**`CHANGES_REQUIRED`**（针对"F→F4 增量与重新冻结是否可用"）

**成立项（无需再改）**：B-1 机制与判别力真关闭（含两条必 FAIL 实例）；24 项参数/行为表语义无越界改动；tag 指向与旧 tag 未移动；F/G/F2/G2/F3/F4/G4 全部可达；F4/G4 双侧自证实测全绿；两份附录在克隆内可复现且计数正确。

**必须关闭（阻断）**

| 编号 | 位置 | 问题 | 影响 | 依据 | 关闭条件 |
|---|---|---|---|---|---|
| BLK-C1 | `…r10/fresh_selfcheck_pair.json`（清单绑定 `fd6fda19…`） | verdict=`FAILED`（陈旧），与包内 S6A-C6「均 ALL_PASS」及 `check_evidence_mode_output` 全 PASS 矛盾；克隆内实跑为 `BOTH_ALL_PASS` | 冻结包自证"失败" | 文件内容 + 克隆实跑 exit 0 + w6 08:34 同字节 | 用真实的 `BOTH_ALL_PASS` 产物替换并重绑清单（新 RunId / 更正记录），并登记曾为陈旧 FAILED |
| BLK-C2 | `verification/tool_self_tests.py:142-149` | 两条必 FAIL 例对**真实 run-dir** 运行 `claim_verify`，改写冻结附录 | 跑套件即破坏冻结证据；BLK-C1 的直接成因 | 克隆内 `git status` 出现 4 个附录被改；r10 被留为 `NOT_ALL_VERIFIED/[]`；w6 mtime 08:32→08:34 | 两条例改在 `tempfile` 副本运行（或给 `claim_verify` 加 `--out-dir`）；重跑套件后 run-dir 哈希不变 |
| BLK-C3 | 入库 `tool_self_tests.json`（r10/r05 同字节 `92a07149…`）；`tool_self_tests.py:89-92,163`；`claim_verify.py` S6A-C5 | 硬条件④未达成：`selfproof_valid_commit` 为 `skipped/null`；套件把跳过记 `AS_EXPECTED` 且总判定只要求 AS_EXPECTED（fail-open）；S6A-C5 只读 verdict | 机读链把"未执行"记为绿；STATE「10/10」与入库证据矛盾（依据在不入库的 tmp） | 入库产物 10 条逐条；`tmp/6/tool_self_tests.json` 08:32 显示真实 10/10 且解析到 `6b8e5f2a23` | 重跑并入库（`selfproof_valid_commit`→F4、exit 0）；verdict 区分 skipped、C5 增"0 跳过"断言；或正式登记该例未执行并停用"10/10" |

**非阻断**：N-C1（amend 归属失真，必须改准）、N-C2（`transport_clone_check.json` 只存在 tmp）、N-C3（清单 2 条陈旧 NOT_RUN）、N-C4（r07/r09/r2 陈旧字面）、N-C5（v1.8 RunId 放宽未登记）、N-C6（S6-B 自证 task_id 写 S6-A）。

**对 amend 偏离的最终判定**：**已披露但记述不准确**；F4/G4 的可复现性**不受影响**（我已在克隆内实测确认两侧全绿、所有引用可达）；受影响的只有记录可审计性与被取代的中间态 F3。**须按 N-C1 改准，不得以"F2 不可达"作为本轮重建的叙事依据**。

---

## 七、命令与真实退出码

| # | 命令（cwd 见备注） | 退出码 | 要点 |
|---|---|---|---|
| 1 | `git -C w6 rev-parse HEAD` / `status --short` / `diff HEAD` | 0 / 0 / 0 | HEAD=`f5b749e…`(G4)；status 与 diff 均空（**复核前后一致 = 未写 w6**） |
| 2 | `git -C w6 rev-parse <tag>^{commit}` × 5 | 0 | r09/s6b-core/freeze→`1e2a66c`；r2→`8ecd92cb`；r3→`f5b749e` |
| 3 | `git -C w6 cat-file -t <F/G/F2/G2/F3/F4/G4>` | 0 | 均 `commit` |
| 4 | `git -C clone cat-file -t 66f45dd…` | **128** | 被 amend 掉的旧 F3 不在传输克隆内 |
| 5 | `git -C w6 fsck --unreachable` / `--dangling` | 0 / 0 | 8540 / 4253 行（多为 blob） |
| 6 | `git -C w6 reflog --all --date=iso` | 0 | 08:25:07 `commit (amend)`：`66f45dd`→`efb9f191` |
| 7 | `git -C w6 diff --name-status 0725d9cf 6b8e5f2` | 0 | 117 文件（109 证据 + 8 非证据） |
| 8 | 行为表深比对 + 24 参数逐字段（`s02_delta_scope.py`） | 0 | 行为表 2 处差异；24 参数 0 差异、24/24 PENDING |
| 9 | `git clone --no-local --branch stage6-interact-prep`（w6 → `clone/`） | 0 | 传输克隆；HEAD=`f5b749e`；5 tag 齐 |
| 10 | 克隆内 `s6a_fresh_selfcheck_twice.py --run-dir …r10 --gap-seconds 30` | **0** | `{"verdict": "BOTH_ALL_PASS", "first": [0,"PASS"], "second": [0,"PASS"]}` |
| 11 | 克隆内 `claim_verify --package s6a --run-dir …r10` | 0 | 7=6+1，`ALL_CLAIMS_VERIFIED`，`count_ok=true` |
| 12 | 克隆内 `claim_verify --package s6b --run-dir …r05` | 0 | 5=4+1，`ALL_CLAIMS_VERIFIED`，`count_ok=true` |
| 13 | 克隆内 `claim_verify … --simulate-defect count_mismatch` | **1** | `NOT_ALL_VERIFIED`，recorded 6 / 期望 7，`count_ok=false` |
| 14 | 克隆内 `claim_verify … --simulate-defect empty` | **1** | `NOT_ALL_VERIFIED`，recorded 0，`{"verdict":"NOT_ALL_VERIFIED","claims":[]}` |
| 15 | 克隆内 `export_selfproof --commit F4` / `--commit F4 --s6b-run …r05` | 0 / 0 | `ALL_SELF_PROVEN [0,0,0]` / `[0,0,0,0]` |
| 16 | 克隆内 `export_selfproof --commit G4` / `--commit G4 --s6b-run …r05` | 0 / 0 | `ALL_SELF_PROVEN [0,0,0]` / `[0,0,0,0]` |
| 17 | 克隆内 `export_selfproof --commit F2` / `--s6b-run …r05` | 0 / 0 | `ALL_SELF_PROVEN [0,0,0]` / `[0,0,0,0]`（**F2 可达且自证**） |
| 18 | 克隆内 `export_selfproof --commit efb9f191(F3)` / `--s6b-run …` | **1** / **1** | `NOT_SELF_PROVEN [0,2,2]` / `[0,0,2,2]`（树内 `source_commit=66f45dd` 不可解析） |
| 19 | 克隆内 `export_selfproof --commit 66f45dd` | **1** | `RuntimeError: checkout … 失败：unable to read tree` |
| 20 | 克隆内 `git status --short`（跑过两条 simulate 例之后） | 0 | 4 个冻结附录被改写（**BLK-C2 的实证**） |
| — | `pwsh` 直接内联 Python 单行 | 1 | **我方脚本的引号转义问题**，与仓库无关（已改写入 `.py` 文件执行） |

**只读性**：全部验证写入 `tmp/review/FREEZE_DELTA_C_20261023_r01/`（含自建 `clone/`）；**w6 复核前后 `git status --short` 均为空、`git diff HEAD` 为空**；`claim_verify`/`export_selfproof` 的写操作只发生在我的克隆内。