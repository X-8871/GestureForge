# 独立复核：阶段6 离线部分终局复核（F6d/G6b 增量）

- 复核人：独立 Reviewer（阶段6 终局终局复核；只读；仅写本目录 `D:\FPGA_Competition\tmp\review\FREEZE_DELTA_E_20261023_r01\`）
- 时间：2026-10-23 10:11–10:35（UTC+8）
- 对象：`D:\codex-worktrees\w6`（`stage6-interact-prep`），HEAD = `538b7923354417915c5dbcbcf7052b88faa0da7e`，工作区 **0 改动**
- 交付内容 **F6d** = `2f16d668a14604ad3d4846e29c8a0f10489ac08b`；自证记录 **G6b** = `538b7923…`；tag `stage6-freeze-20261023-r6` → G6b
- 未跑重型套件（未跑 `tool_self_tests.py` 20 分钟级套件；未跑 S6-B 以外的批量重跑）；未改 w6；只读 w6 与 main 的 F5 复评结论

## 结论

**`CHANGES_REQUIRED`。**

| 项 | 判定 |
|---|---|
| **BLK-D1（F5 自证失败 / `run_id` 未同步）** | **已关闭 ✅**（含我自己的反例：缺参 fail-closed） |
| **BLK-D2①（规格文档 12 处"待批准"改准）** | **未关闭 ❌**（4 处改准、2 处加历史标记、5 处未改未标、另 1 处非批准口径未改） |
| **BLK-D2②（8 条历史修订行写回当时状态 + 可机读历史标记）** | **未关闭 ❌**（0 条写回；7/8 无标记；且冻结 STATE 声称"已写回并标注"= 失实） |
| **BLK-D2③（`params_snapshot.json` 无假命题、字段自洽）** | **已关闭 ✅** |
| **BLK-D2④（旧假命题字段只残留在扫描器正则、不在产物）** | **未关闭 ❌**（`all_parameters_pending_approval: true` 仍在新包 `r12/fix_record.json:16`；且对应扫描模式为**死正则**） |
| **BLK-D2⑤（S6-B 侧等价 approval 断言 + 注入必 FAIL 自测）** | **断言存在、可复现，但判别力窄且 fail-open ❌**（我自造 8 类注入，6 类未被捕获） |
| 增量范围（F5→F6d） | 通过（0 参数值/阈值/行为语义改动） |
| 链条/标签/历史完整性 | 通过（无 amend、旧 tag 未移动、旧 RunId 未被就地改写） |
| 如实性 | **新增失实声明 1 条**（STATE 称 8 条历史行已写回）+ 1 条 claim 强于产物 |

**F6d/G6b 目前不能被引用为「阶段6 离线部分的有效冻结版」**：其 BLK-D1 已真关闭，但 BLK-D2 的关闭条件（上一轮我给出的四条）只完成一半，且本轮**新增**了两处"声明强于产物"。
**历史语境标记只在 2 处（规格文档 L128、L397）可机读区分；7 条历史修订行不可机读区分，且其内容仍写着批准后的口径。**

---

## 一、命令与真实退出码（全部在**我自建**的传输克隆 `clone/w6_transport`（HEAD=G6b=538b792）内，或 w6 只读）

| # | 命令 | 真实结果 |
|---|---|---|
| 1 | `git clone --no-local --depth 15 --no-single-branch D:/codex-worktrees/w6 clone/w6_transport` | exit **0**（41.2 s）；克隆内 HEAD=`538b7923`、工作区 0 改动、8 个 tag 全部随克隆到位 |
| 2 | 克隆内 `git cat-file -t` × 15 个被引用提交（F6/F6b/F6c/F6d/G6/G6b/F5/G5/F4/G4/G2/G/F2/F3/G5b） | 15/15 `commit`，exit **0** |
| 3 | 克隆内 `git rev-list -n1 <tag>`（8 个 tag） | r1→`1e2a66c`、r2→`8ecd92c`、r3→`f5b749e`、r4→`61caac0d`、r5→`a2d232da`、r6→`538b7923`；`s6a-g0-v1.8-r09`/`s6b-core-r04`→`1e2a66c`；全部 `type=tag`（annotated），exit **0**，**旧 tag 未被移动** |
| 4 | 克隆内 `git merge-base --is-ancestor`（真实顺序） | `bf05d450→9b9d572e` 0、`9b9d572e→0a2abc49` 0、`0a2abc49→a2d232da` 0、`a2d232da→2f16d668` 0、`2f16d668→538b7923` 0、`61caac0d→2f16d668` 0；反向 `2f16d668→a2d232da` = **1**（证明 G6 是 F6d 的**父**，非后代） |
| 5 | 克隆内 `python -B verification/export_selfproof.py --project-root <clone> --commit 2f16d668a14604ad3d4846e29c8a0f10489ac08b --s6a-run report/evidence/S6-A/s6a_g0_20261023_r12 --s6b-run report/evidence/S6-B/s6b_core_20261023_r07` | `{"verdict":"ALL_SELF_PROVEN","subjects":[["commit 2f16d668…","SELF_PROVEN",[0,0,0,0]]]}`，**exit 0**（17.9 s）→ S6-A `[0,0,0]` + S6-B `[0,0,0,0]` |
| 6 | 同上但 `--commit 538b7923354417915c5dbcbcf7052b88faa0da7e`（**被引用的 tag r6 本身**） | `ALL_SELF_PROVEN [0,0,0,0]`，**exit 0**（12.4 s） |
| 7 | **反例**：同 #5 但**故意漏传 `--s6a-run`** | `{"verdict":"NOT_ALL_SELF_PROVEN","subjects":[["commit 2f16d668…","NOT_SELF_PROVEN",[]]]}`，**exit 1**，reason=`缺少显式 --s6a-run（BLK-D1 之后不再按行为表 run_id 隐式查找）` → **fail-closed ✅** |
| 8 | 克隆内 `python -B verification/approved_package_scan.py --project-root <clone> --run-dir report/evidence/S6-A/s6a_g0_20261023_r12 --inject-self-test` | `{"verdict":"AS_EXPECTED","hits":0,"self_test":"AS_EXPECTED"}`，exit **0** |
| 9 | 克隆内同上，`--run-dir report/evidence/S6-B/s6b_core_20261023_r07 --inject-self-test` | `{"verdict":"AS_EXPECTED","hits":0,"self_test":"AS_EXPECTED"}`，exit **0** |
| 10 | 我自造注入反例（见 §四）：对**真实 run-dir** 注入 8 类 PENDING 断言、**不带** `--inject-self-test` | 仅 2 类被捕获（exit 1）；**6 类 fail-open（exit 0 / CLEAN）**，其中含 F5 点名的机读假字段与文档状态行 |
| 11 | `git diff --name-status 61caac0d 2f16d668` | 116 项 = **A 104 + M 12 + D 0** |
| 12 | `git diff 61caac0d 2f16d668 -- src/stage6/s6_core.py src/stage6/s6_actions.py src/stage6/s6_predicates.py` | **空**；`--name-only -- src/stage6` 仅 `src/stage6/s6_params.py` |
| 13 | 我自研 `param_delta.py`（逐项比对 24 项参数载荷，除批准类字段） | `value_diffs=0`、`approval_field_changes=0`；24 项值载荷整体 SHA-256 `f5==f6d`（`f5_sha256`=`f6d_sha256`）；顶层变更键仅 `run_id`/`supersedes_run_id`/`upstream`/`not_claimed`（均为 BLK-D2 声明的口径文本） |
| 14 | 抽验 3 项参数（`T6-K01`/`T6-C01`/`T6-S02`） | `byte_identical=True`（见 §五：1000 ms / 2 帧 / 6 帧） |
| 15 | `git diff 61caac0d 2f16d668 -- report/evidence/S6-A/s6a_g0_20261023_r10 report/evidence/S6-B/s6b_core_20261023_r05 report/evidence/S6-A/s6a_g0_20261023_r11 report/evidence/S6-B/s6b_core_20261023_r06` | 4/4 **空输出**，exit **0**（旧 RunId 未被就地改写） |
| 16 | 同上对 4 个旧 `_selfproof` 目录 | **空**（本轮未改写上一轮 `_selfproof`；G6b 改写的 8 个记录属**本轮** r12/r07 的 `_selfproof`，符合 N-r07-2 设计） |
| 17 | `git show --stat 538b7923`（G6b） | 仅 `.codex/STATE.md` + 8 个 `_selfproof` 记录（r12 4 + r07 4）→ **只含自证记录/STATE ✅** |
| 18 | w6 `git reflog` F6/F6b/F6c/G6/F6d/G6b | 6 条全为 `commit:`（**无 amend**）；F6 前有一条 `reset: moving to HEAD`（HEAD→HEAD 空操作，非改写）；amend 仅存在于 F4 之前的 `efb9f19`/`1839766`/`e3aeb09`/`43f7995` |
| 19 | 克隆内 `git fsck --no-progress --no-dangling` | exit **0** |
| 20 | w6 `git status --short` | **空**（复核方未写 w6） |

所有产物落在本目录：`01`…`14_*.txt`、`05*_selfproof*.json/md`、`12_injection_counterexamples.txt`、`scripts/*.py`、`clone/w6_transport/`。

## 二、链条 / 标签 / 历史完整性（对应任务第 3 项）

**实际链条与任务卡预设不一致（以实际为准）：**

```
F6 bf05d450 → F6b 9b9d572e → F6c 0a2abc49 → G6 a2d232da (tag r5) → F6d 2f16d668 → G6b 538b7923 (tag r6)
                                   ↑                              ↑
                          F6d 的父提交 = G6        G6b 的父提交 = F6d
```

- 任务卡写「F6→F6b→F6c→F6d；G6 = `538b7923`？」→ **实际 G6 = `a2d232da`（= tag r5），G6b = `538b7923`（= tag r6）**，且 **F6d 排在 G6 之后**（F6d 的父提交是 G6）。w6 STATE L34-35 如实写明了这条链（F4/G4→F5/G5→F6c/G6→F6d/G6b）与中间态，**未发现被掩盖的改写**。该顺序偏离"F/G 两段式"的字面形态（F6d 是 G6 之后的补充内容提交），但 r5 仍只覆盖 F6c、r6 覆盖 F6d/G6b，二者各自自证通过，**不构成阻断**。
- `cat-file -t` 15/15 通过；tag 全部 annotated；r1..r5 与两个 per-profile tag **指向未变**（tag 对象时间戳 07:27→10:08 单调，r6 为 10:08:55）。
- 被引用提交无 amend（#18）；F6d/G6b 哈希与内容寻址一致（给定哈希逐字符复核通过）。
- `G6b` 只含 STATE + 8 个自证记录（#17）；r12/r07 与旧轮次 r10/r05/r11/r06 **未被就地改写**（#15）。

## 三、增量范围逐项判定（F5→F6d，对应任务第 2 项）

`git diff --name-status 61caac0d 2f16d668`：**A 104 / M 12 / D 0**（无删除）。

| 类别（任务卡允许项） | 实际文件 | 判定 |
|---|---|---|
| `export_selfproof` 的 `--s6a-run` | `verification/export_selfproof.py`（注册新参数、取消隐式查找、`run_id` 取自显式参数、缺参 fail-closed） | ✅ 完全符合 |
| 行为表 `run_id`/`supersedes_run_id` | `docs/stage6/s6a_stage6_g0_behavior_v1.json`：`run_id` r10→**r12**、`supersedes_run_id` r08→**r11** | ✅ |
| selfcheck 注册表 | `verification/s6_g0_selfcheck.py`：`S6A-G0-v1.8` 允许 RunId 追加 `r11`/`r12` | ✅ 仅白名单 |
| `s6_params.py` / `s6b_run_cases.py` 字段语义 | 删 `all_parameters_pending_approval`/`thresholds_are_draft_not_approved`，改 `all_parameters_approved_20261023`/`any_parameter_pending_approval`/`parameter_values_are_draft_values`/`approval_applied`；run_report 同步换名并新增 `approval_ref` | ✅ 字段语义，非阈值 |
| `approved_package_scan.py` 与新 claim | 新增 `verification/approved_package_scan.py`；`claim_verify.py` 新增 `S6A-C8`/`S6B-C5`；`approval_regression.py` 加 `--package s6b` | ✅（属 BLK-D2⑤ 的"两侧断言"要求） |
| 新 RunId 证据与清单 | `report/evidence/S6-A/s6a_g0_20261023_r12/**`（45 文件）+ `…r12_selfproof/**`、`report/evidence/S6-B/s6b_core_20261023_r07/**` + `…r07_selfproof/**`（**全为 A，无改写旧 RunId**） | ✅ |
| 规格文档口径与历史行 | `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md`（5 个 hunk：标题/批准说明、§0、§5、§14 表头、§19 限制） | ⚠️ 范围允许，但**内容未达关闭条件**（§四） |
| STATE 冻结链 | `.codex/STATE.md`（F6d）与 G6b 的 STATE 更新 | ✅ 链条描述如实 |
| 构建器文本 | `s6a_build_evidence.py`、`s6b_build_evidence.py`：把"仍为 PENDING_APPROVAL"改为"已于 2026-10-23 批准" | ✅ 正是 BLK-D2 关闭条件要求的"更新构建器" |
| **超出字面清单** | `verification/m4_residual_regression.py`：注入锚点不存在时**无条件追加**（fail-closed，防注入空转⇒假通过） | ⚠️ 非阻断观察（工具/自测基础设施，**未触及**参数值/阈值/行为语义） |

**参数值/阈值/行为语义改动：无。** 我独立复算：24 项 `draft_value/comparison/unit/kind/draft_source/…` 载荷 `value_diffs=0`；`src/stage6` 仅 `s6_params.py`（快照字段名）被改，`s6_core.py`/`s6_actions.py`/`s6_predicates.py` 逐字节未动；JSON 顶层仅 `run_id`/`supersedes_run_id`/`upstream[].usable_as`/`not_claimed[]` 变更（均为批准口径文本）。**未发现任何未授权的阈值/行为语义改动。**

## 四、两条阻断的逐条证据

### BLK-D1 —— **已关闭 ✅**

| 关闭条件 | 证据 | 判定 |
|---|---|---|
| `export_selfproof` **真正注册** `--s6a-run` | `verification/export_selfproof.py` L274-276 注册；L288-291/L302-303 传入 `self_prove`；L174 形参 `s6a_rel` | ✅ |
| **取消**按行为表 `run_id` 的隐式查找 | L180-184：`if not s6a_rel: return {"verdict":"NOT_SELF_PROVEN","error":"缺少显式 --s6a-run（BLK-D1 之后不再按行为表 run_id 隐式查找）"}`；L256 `run_id = Path(evidence_rel).name` | ✅ |
| 缺参必须 `NOT_SELF_PROVEN` 并说明原因 | 我的反例 #7：`NOT_ALL_SELF_PROVEN`、`NOT_SELF_PROVEN`、**exit 1**、reason 原文如上 | ✅ fail-closed |
| 行为表 `run_id` = `r12` | `run_id="s6a_g0_20261023_r12"`、`supersedes_run_id="s6a_g0_20261023_r11"` | ✅ |
| 克隆内复跑 `--commit F6d`（带两参）→ S6-A `[0,0,0]`、S6-B `[0,0,0,0]`、exit 0 | #5：`SELF_PROVEN [0,0,0,0]`，exit **0**；另 #6 对 **G6b** 本体同样 exit 0 | ✅ 自证成立 |

### BLK-D2 —— **未关闭 ❌**（逐子项）

**(1) 规格文档 12 处"待批准"是否改准 → 部分**

F5 点名 11 行（其自述 12 处）在 F6d 的实际状态（`10_spec_12_points.txt`）：

| 行 | F6d 实际内容（节选） | 判定 |
|---|---|---|
| L9 | `> **状态：\`G0_PACKET_APPROVED_20261023\`（待批准）。**` | ❌ **未改未标**（自相矛盾的状态行，位于文档最顶部） |
| L10 | "一律登记为**已批准**（2026-10-23；值仍为草案值）" | ✅ 改准 |
| L128 | "已批准（2026-10-23）、不是已冻结"；同行尾 "…**其中全部数值参数为待批准**。　【历史语境：上述为当时状态（该版本产出时尚未批准）】" | ✅ 指针改准 + 残留"待批准"**带标记** |
| L130 | 表头 "参数（已批准 2026-10-23）" | ✅ 改准 |
| L171 | `**表 A-1（动作映射为提案，待批准）**。` （JSON `actions.map_status=APPROVED_20261023`） | ❌ **未改未标** |
| L185 | "（r02 补，N-06；具体可见时长待批准）…属待批准项（U6-14）" | ❌ **未改未标** |
| L280 | `## 14. 阈值与指标登记（**全部已批准 2026-10-23**）` | ✅ 改准 |
| L282 | "下表全部为 `APPROVED_20261023`：`草案值` 指…，**不是**已批准门槛。批准权在 Wong（由项目总控转呈）。" | ❌ **未改未标**（无"待批准"token，但仍是批准前口径且自相矛盾） |
| L320 | "受 `T6-A01` 约束（待批准）。" | ❌ **未改未标** |
| L321 | "其上限为 `T6-A03`（**待批准**，草案未给值…）" | ❌ **未改未标** |
| L397 | "…全部阈值待批准；…　【历史语境：上述为当时状态（该版本产出时尚未批准）】" | ✅ 保留 + **带标记** |

→ 4 行改准、2 行加标记、**5 行未改未标**（L9/L171/L185/L320/L321），另 L282 的非批准口径未改。

**(2) 8 条历史修订行 → 未写回、7/8 无标记（`03_spec_history_lines.txt`、`10_spec_12_points.txt`）**

8 条 = L14、L21、L28、L30、L32、L34、L36、L38（修订记录中含 `APPROVED_20261023` 的行）。

| 行 | 是否写回当时状态 | 是否有可机读历史标记 | 依据 |
|---|---|---|---|
| L14（v1.8/r09） | ✗ | ✔（"历史语境除外"，**该字样 F5 已存在**，源自 r08 的 C16 白名单约定，非本轮新增） | F5==F6d 逐字节相同 |
| L21（v1.7/r08） | ✗（仍 `APPROVED_20261023`） | ✗ | F5==F6d 逐字节相同；F4 同位置为 `PENDING_APPROVAL` |
| L28（v1.6/r07） | ✗ | ✗ | 同上 |
| L30（v1.5/r06） | ✗ | ✗ | 同上 |
| L32（v1.4/r05） | ✗ | ✗ | 同上 |
| L34（v1.3/r04） | ✗ | ✗ | 同上 |
| L36（v1.2/r03，**2026-10-22**） | ✗ | ✗ | 同上 |
| L38（v1.1/r02，**2026-10-22**，写"24 项仍全部 `APPROVED_20261023`"） | ✗ | ✗ | 同上 |

关键取证：**F4（`6b8e5f2`）在同一逻辑位置的文本是 `PENDING_APPROVAL`**（F4 对应行为 "> - 全部 24 项参数值与 `PENDING_APPROVAL` 未改；…" 与 "…24 项仍全部 `PENDING_APPROVAL`。"），F5 改成 `APPROVED_20261023`，**F6d 与 F5 逐字节相同**（对这 7 行 `F5==F6d True` 全部成立）⇒ "写回当时状态"**没有发生**。
另：扫描器 HISTORICAL 正则的版本行分支 `v1\.\d+（r\d+` 与实际文本 `v1.5 / r06`（带空格+斜杠）**不匹配**，故即使扫描器愿意，也认不出这些历史行。

**由此产生的新失实声明**：冻结 STATE（G6b 的 `.codex/STATE.md` L43-44）写
> "规格文档拆分「当时/现口径」，**8 条历史修订行写回当时状态并标注历史语境**"

—— 与产物不符（0 条写回、7/8 无标记）。这属"把未做写成已做"，是本轮**新增**的如实性问题。

**(3) `params_snapshot.json` 无假命题、字段自洽 → 已关闭 ✅**

- r07 `params_snapshot.json`：L5 `behavior_status="G0_PACKET_APPROVED_20261023"`；L242 `all_parameters_approved_20261023: true`；L243 `any_parameter_pending_approval: false`；L244 `parameter_values_are_draft_values: true`；L245 `approval_applied: true` → **无假命题、与顶行自洽**。
- r07 `run_report.json`：L8 `parameters_approved_20261023: true`、L9 `any_parameter_pending_approval: false`、L10 `approval_ref=<receipt>`（新增）。
- 我全文复扫：`all_parameters_pending_approval`/`thresholds_are_draft_not_approved`/`parameters_pending_approval` 在 **r07 内 0 命中**。

**(4) 旧假命题字段只残留在扫描器正则 → 未关闭 ❌**

- 旧字段名的**全部**残留位置：
  - `verification/approved_package_scan.py:25/26/27`（扫描器正则，属允许的残留）✅
  - 历史冻结包 `S6-A r02..r11/fix_record.json:16`、`S6-B r01..r06/params_snapshot.json:242-243`、`run_report.json:8`（**历史产物，不可改写，可接受**）
  - ❌ **`report/evidence/S6-A/s6a_g0_20261023_r12/fix_record.json:16`：`"all_parameters_pending_approval": true`** —— 属**本轮新增**包（diff 为 A），同一 `revision_discipline` 块内 `"new_run_id": "s6a_g0_20261022_r07"` 也是陈旧身份（与文件自身 `run_id: s6a_g0_20261023_r12` 矛盾）。这正是 F5 定性为"**最重的机读假值**"的那条。
- **扫描器对该字段无判别力**：`ASSERT_PATTERNS[3/4/5]` 是小写字段名，而前置门槛 `TOKENS = re.compile(r"PENDING|待批准")` **区分大小写**，小写 `pending` 永远过不了门槛 ⇒ 三条模式为**死正则**（`04_pending_scan.txt` §C 给出判定）。因此 claim `S6A-C8`（"已批准版包内不得出现 PENDING/待批准 陈述"）在**该字段确实存在**的情况下仍报 `CLEAN/AS_EXPECTED/VERIFIED`。

**(5) S6-B 侧等价 approval 断言 + 注入必 FAIL 自测 → 断言存在，但判别力窄、fail-open ❌**

- ✅ **断言确实存在**：`verification/approved_package_scan.py`（两侧通用）+ `claim_verify.py` 的 `S6B-C5-approved-package-scan`（S6-B 侧此前 0 条 approval 断言，缺口已补）；r07 `claim_verification.json` 该条 `exit_code=0`、`verdict=VERIFIED`、output `{"verdict":"AS_EXPECTED","hits":0,"self_test":"AS_EXPECTED"}`。
- ✅ **工具自带注入自测可复现**：#8/#9 我在克隆内实跑，`--inject-self-test` → `AS_EXPECTED`、**exit 0**（说明设计约定"注入命中即 AS_EXPECTED"；注入未命中才非 0）。**注意**：任务卡预期的"`--inject-self-test` 真实退出码必须非 0"与该工具约定不同——该工具把"注入必 FAIL"内化，用 exit 0 + `AS_EXPECTED` 表达"正常+判别力成立"。
- ❌ **我自造的真实注入反例（不带工具内建自测，直接对真实 run-dir 注入；`12_injection_counterexamples.txt`）**：

| 注入形态 | exit | verdict | 捕获 |
|---|---|---|---|
| B1 `"approval_status": "PENDING_APPROVAL"` | 1 | `PENDING_TEXT_FOUND` | ✅ |
| B2 `本包全部阈值与指标仍为待批准状态` | 1 | `PENDING_TEXT_FOUND` | ✅ |
| B3 `"all_parameters_pending_approval": true`（F5 点名的最重机读假值） | 0 | `CLEAN` | ❌ **fail-open** |
| B4 `"thresholds_are_draft_not_approved": true` | 0 | `CLEAN` | ❌ **fail-open** |
| B5 `"parameters_pending_approval": true` | 0 | `CLEAN` | ❌ **fail-open** |
| B6 `状态：\`G0_PACKET_APPROVED_20261023\`（待批准）。`（文档实际 L9） | 0 | `CLEAN` | ❌ **fail-open** |
| B7 `受 \`T6-A01\` 约束（待批准）。`（文档实际 L320） | 0 | `CLEAN` | ❌ **fail-open** |
| B8 `"pending_confirmation": …`（开放项，预期放行） | 0 | `CLEAN` | ✅（预期放行） |

（S6-A/S6-B 两个 run-dir 结果一致；基线无注入 → `CLEAN` exit 0。）
⇒ "注入必 FAIL 自测"只证明了**它自己挑的那一种句式**有判别力；对 BLK-D2 的原始病灶（机读假字段）与文档状态行**没有**判别力。SKIP 正则含 `注入|probe|self_test` 等宽词，会把"仅仅提到注入"的现行陈述一并放行（见 §五 N-e）。

## 五、如实性与新问题（任务第 4 项）

**未做项登记（✅ 基本如实）**
- 批次 C 三项：r12 `limitations_not_executed.open_gaps_batch_c` 如实登记三项（陈旧 `fresh_selfcheck_pair.json`；套件必 FAIL 例跑真实 run-dir；套件 `skipped` 曾计 `AS_EXPECTED` 且产物未真正入库），STATE L51-52 同步登记，并写明"不得当通过凭据"。我核对 `tool_self_tests.json`：10 例中确有 1 例 `skipped=True` 而 verdict 仍记 `AS_EXPECTED` ⇒ 缺口③**确实存在且未被修**，登记与事实一致。
- `T6-A03` 数值 `NOT_RUN`、G3 板测未做、集成依赖 `BLOCKED`、独立复评未做：STATE L49-50 与两包 `limitations_not_executed` 均如实登记。
- **未跑项**：`tool_self_tests.py`（20 分钟级套件）本轮**未跑**（任务卡禁止），我采用的是**引用其入库产物**（`tool_self_tests.json`，`ALL_AS_EXPECTED`，含 1 例 skipped）；`claim_verify`/S6-B 26 例**未全量重跑**（由 #5/#6 的自证复跑覆盖，其内部实跑 S6-B 驱动 + 两检查器）。

**新引入的"声明强于产物"**
1. **STATE 声称"8 条历史修订行写回当时状态并标注历史语境"**（G6b STATE L43-44）—— 实际 0 条写回、7/8 无标记（§四(2)）。
2. **claim `S6A-C8` 的 statement 强于其断言**：statement 是"已批准版包内**不得出现** PENDING/待批准 陈述"，但其扫描器对 §四(4) 的死正则与 §四(5) 的 6 类形态 fail-open；`r12/fix_record.json:16`、文档 L9/L171/L185/L320/L321 都在 statement 覆盖范围内却报 `CLEAN`。
3. 我**未发现** `_selfproof` 里声明不存在的目录/文件：`export_selfproof` 的 `evidence_dir`/`file_count` 与实际一致（45）；`unresolved=[]`；C11 在 F6d 与 **G6b 本体**各自证中均 `ALL_PASS`（#5/#6）⇒ 无此类缺陷。

**非阻断观察（建议记录，不单独阻断）**
- **N-a** 本轮口径替换产生新的自相矛盾文本：r12 `limitations_not_executed.json:44` "指标**未获批准**（`APPROVED_20261023`）"；r07 `inputs_manifest.json:27` "…已于 2026-10-23 批准（值仍为草案值）**草案值**。"（重复词）。
- **N-b** 残留未标记的 PENDING 文本（超出 §四(4) 的字段类）：r12 `coverage_matrix.json:122/127/132`（`§14 T6-01（PENDING_APPROVAL）` 位置标签）、`:206`（`"C4": "待批准纪律（24 项）"`）；S6-B r07 `reachability_notes.json:5`（`derived_from: "S6A-G0-v1.6 draft parameters (PENDING_APPROVAL)"`）、`cases/case_matrix.json:168` 与生成器 `cases/build_case_matrix.py:516`（"参数全部为 PENDING_APPROVAL 草案值"——**现行陈述、已被冻结进 `expected_freeze` 绑定**，仅因同行含"注入"被 SKIP 放行）。
- **N-c** 版本/身份令牌陈旧：行为表 `status_label` 仍写 "v1.9（r11 批准版）"（`artifact_version=S6A-G0-v1.8`、`run_id=r12`）；r12 `S6A_run_summary.md` 标题仍 "v1.8 / r09"；r07 `s6b_run_summary.md` 标题仍 "v1.6 契约，S6-A r07"。（F5 的 N5 未关闭）
- **N-d** `_selfproof` 报告的 `state_snapshot_sha256`（`d7763f5f…`）≠ G6b 提交的 STATE.md 实际哈希（`c2b21eae…`）⇒ 该"信息性快照"取的是 10:08:29 的 STATE，之后 STATE 又被编辑（26 s 后提交）。虽是信息性字段且 G6b 本体自证仍绿（#6），但"快照"与产物不同版本，建议注明或改为同提交口径。
- **N-e** 扫描器 SKIP 过宽：`注入|probe|self[_ -]?test|历史语境|当时|…` 会豁免"只是提到注入/自测"的**现行**陈述（N-b 的 `case_matrix.json:168` 即实例）；`ALLOW` 也把 `上游依赖` 之类宽词当放行。
- **N-f** `export_selfproof.py` 未强制 `--s6b-run`：只传 `--s6a-run` 时仍可判 `ALL_SELF_PROVEN`（[0,0,0]）。本轮两侧记录分剖面入库，不影响 BLK-D1 结论，但"ALL_SELF_PROVEN"字面强于剖面覆盖面，建议在 verdict 文案中区分剖面。
- **N-g** r12 `delivery_manifest.json` 内嵌的自证检查 `reason` 仍写上一轮的 `subjects={'commit 0a2abc49…': 'SELF_PROVEN'}`（F6c 身份，构建期字符串），与 r12/F6d 不一致。
- **N-h** N1（`approval_ref` 目标 `…/decisions/stage6_approval_receipt_20261023_r01.md` **不在 w6 树内**，仅在 main）仍成立：STATE L8-9 以"批准记录在 main"披露，但两包 `limitations_not_executed` 未把它登记为开放项，C4/扫描器仍不校验其存在性。N2（F4→F5 改写上一轮 `_selfproof`）本轮**未复发**，且 N-r07-2 规则已在 `export_selfproof`/limitations 写明。
- **N-i** 超出任务卡字面允许清单的工具改动：`verification/m4_residual_regression.py`（注入锚点缺失时无条件追加，fail-closed）。不触及产品语义，判非阻断。

## 六、抽验的参数值（与上一冻结 F5 逐字节一致）

| ID | 含义 | F5 `61caac0d` | F6d `2f16d668` | 载荷逐字节一致 | 批准状态 |
|---|---|---|---|---|---|
| `T6-K01` | 冷却时长 | 1000 ms（`>=`） | 1000 ms（`>=`） | ✅ `sha_f5==sha_f6d` | APPROVED_20261023 |
| `T6-C01` | 进入候选的连续同目标帧数 | 2 帧（`>=`） | 2 帧（`>=`） | ✅ | APPROVED_20261023 |
| `T6-S02` | 稳定窗口帧数 | 6 帧（`>=`） | 6 帧（`>=`） | ✅ | APPROVED_20261023 |

- 抽样方式：F5 轮次用同 3 项；本轮我额外对 **全部 24 项**做载荷哈希比对：`f5_sha256 == f6d_sha256`（`07_param_delta.txt`）⇒ 24/24 值、比较符、单位、kind 零差异；`approval_field_changes=0`。

## 七、关闭条件（下一轮需要做到）

1. **规格文档**：把 L9（`（待批准）`）、L171、L185、L320、L321 与 L282 的批准前口径改准；若刻意保留当时口径，必须逐行加**机读**历史标记并让扫描器能识别（当前 `v1.5 / r06` 形式不被正则接受）。
2. **8 条历史修订行**：写回当时状态或加机读历史标记；同时修正 G6b STATE L43-44 的失实表述（或改为与产物一致的措辞）。
3. **清除产物中的机读假命题**：`S6-A r12/fix_record.json:16` 的 `all_parameters_pending_approval`（连同该块的陈旧 `new_run_id`）；清理 N-b 列出的残留（`coverage_matrix.json` 122/127/132/206、`reachability_notes.json:5`、`case_matrix.json:168`/`build_case_matrix.py:516`）与 N-a 的自相矛盾文本（`limitations_not_executed.json:44` 等）——须以**新 RunId** 重生成，不得就地改写 r12/r07。
4. **让断言真正覆盖其 statement**：修正 `approved_package_scan.py` 的大小写门槛（死正则）、收紧 SKIP/ALLOW；并**增加一条能捕获"机读假字段 + 文档状态行"形态的注入自测**（我给出的 B3/B6/B7 可直接作为必 FAIL 例）。修好前，`S6A-C8`/`S6B-C5` 的 statement 应降级为实际覆盖范围。
5. 附注（非阻断）：N-c 版本令牌、N-d STATE 快照口径、N-g manifest 内嵌陈旧自证 reason。

## 附：本目录产物

`01`…`14_*.txt`、`02_scan_r12.json`/`02_scan_r07.json`/`02_scan_r12_plain.json`、`04_pending_scan.txt`、`05_selfproof_clone.json/md`、`05b_selfproof_no_s6a.json`、`05c_selfproof_G6b.json/md`、`06_behavior_fields.txt`、`07_param_delta.txt`、`08_chain_clone.txt`、`09_claims_and_limits.txt`、`10_spec_12_points.txt`、`11_evidence_points.txt`、`12_injection_counterexamples.txt`、`13_batch_c.txt`、`14_final_checks.txt`、`inj_*.json`、`scripts/*.py`、`clone/w6_transport/`（传输克隆，41 s）。