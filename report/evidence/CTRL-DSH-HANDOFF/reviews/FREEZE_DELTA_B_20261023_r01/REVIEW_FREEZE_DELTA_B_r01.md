# 冻结增量复核（收尾轮 B）— 结论 CHANGES_REQUIRED

- 复核对象：`D:\codex-worktrees\w6`（分支 `stage6-interact-prep`，HEAD = G = `1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e`，工作区 0 改动）
- F（交付内容）= `0725d9cf48aeed21d3ea445ef01575c16b68d950`（父提交 = `1839766`）
- G（自证记录）= F 的子提交
- tag：`s6a-g0-v1.8-r09`、`s6b-core-r04`、`stage6-freeze-20261023` → 三者 `rev-list -n1` 均为 G
- 复核写入：`tmp/review/FREEZE_DELTA_B_20261023_r01/`（隔离目录）；**未改动 w6**（复核结束 `git status --short` 仍为空）
- 结论适用范围：仅 F/G 冻结增量；不代表 G0/G2/G3/G4/G5、语义正确、实物验收

---

## 一、检查 1：冻结增量范围（`1839766` → F）

`git -C w6 diff --stat 1839766 F`：114 files, +18575 / -345。
`git -C w6 diff --name-status 1839766 F`：`src/stage6/**` 2 个、`verification/**` 18 个（其中 8 个新增）、`docs/stage6/**` 2 个、`.codex/STATE.md`、其余 91 个为 `report/evidence/S6-A/s6a_g0_20261022_r09/**` 与 `report/evidence/S6-B/s6b_core_20261023_r04/**` 新增证据。

### 声明项逐项核对

| 声明修复 | 落地位置 | 判定 |
|---|---|---|
| S6-B `write_manifest()` + FIXPOINT-B + `[CLOSING]` | `verification/s6b_build_evidence.py:420/473/481/488/492/494` | 一致 |
| `acquisition_id` 在 M8/M2/M12 递增 | `src/stage6/s6_core.py` `_transition`（M11/M4/M8 合并 `+=1`；M12 独立 `+=1`；M2 独立 `+=1`；M13 不递增） | 一致 |
| 三例覆盖用例 | `s6b_run_cases.py:170-175`（`acquisition_ids` 断言）+ `claim_verify.py` `s6b_claims` 的 `id_check`（`[0,1]`/`[0,2]`/`[0,1,2]`） | 一致 |
| `action_records` 落盘 | `s6b_run_cases.py:159/307`、`claim_verify.py:118-128` | 一致 |
| C16 扩范围 + 语义判定 + 两表示法交叉断言 | `verification/s6_g0_selfcheck.py`（C16 detail："11 个交付文件经语义扫描一致"）；交叉断言见 `claim_verify.py` `s6a_claims` S6A-C3 | 一致 |
| `m4_reachability` 去硬编码 | `verification/s6_g0_selfcheck.py:963`「复算完全由输入决定，而不是常量」、`:982` | 一致 |
| 活文档（STATE）移出硬哈希集合 | `verification/export_selfproof.py:301-304`（`state_snapshot_sha256` 信息性快照 + `live_document_note`）；`verification/s6_g0_selfcheck.py` C11 只做存在性 | 一致 |
| 新工具 `transport_clone_check.py` | 新增 | 一致 |
| 新工具 `tool_self_tests.py` | 新增 | 一致 |
| 新工具 `hash_convention_check.py` | 新增 | 一致 |
| 版本 v1.8 / r09 | `s6_params.py:EXPECTED_ARTIFACT_VERSION`、`s6_core.py:EXPECTED_CONTRACT_VERSION`、行为表 `artifact_version` 均 `S6A-G0-v1.8` | 一致 |
| r04 / r09 证据 | 两份新 RunId 目录 | 一致 |

### 未在任务卡字面清单中的改动（逐项判定）

| 文件 | 改动 | 是否超出声明范围 |
|---|---|---|
| `src/stage6/s6_core.py` NB-r03-05 | 删除 `current_target` 无意义自赋值、删除 `s6_params.py:181` 自赋值 | **非越界**：FINAL_B_r03 README 第 33 行 `NB-r03-05`、第 51 行派单「`NB-r03-01..12`」明确要求 |
| `src/stage6/s6_core.py` NB-r03-08 | `candidate_dwell_start_ns` 由 `x or t_now_ns` 改为 `is None` 判空（t=0 锚点） | **非越界但属语义改动**：FINAL_B_r03 `S6B_review_r03.md` 第 122 行 `NB-r03-08` 要求「改用 `is None` 判空并回归 M4 相关用例」。**任务卡未列名，建议总控在声明中补登记**；仅影响 `t_start=0` 的回放锚点，交付用例与 M4 可达性结论不变 |
| `verification/m4_residual_regression.py`（新增） | 用终审 A 的 3 条真实残留行逐条注入，要求 C16 必须 FAIL | 非越界：服务已声明的「C16 语义判定」并为其提供判别力证据 |
| `verification/s6a_fresh_selfcheck_twice.py`（新增） | 构建后连跑两次新鲜自检（间隔 30s） | 非越界：服务已声明的 `[CLOSING]`/清单时序修复 |
| `verification/s6b_no_dead_constants.py`（新增） | 死常量检查（S6-B claim S6B-C3 的真实命令） | 非越界：小工具，无产品语义影响 |
| `verification/claim_verify.py`（+433/−） | 由「自算退出码」改为**真实 subprocess 退出码** | 属已声明修复，但**实现有缺陷**——见第二节阻断项 |

### 阈值/参数语义面

- 24 项参数**逐字段**与 `1839766` 比对：**0 处差异**（`parameters` 双向 ID 集合相等，24/24）。
- `transitions` 容器唯一变化 = `transitions[M4].reachability` 由 `UNREACHABLE_UNDRAFT` → `REACHABLE` 及对应 `reachability_note`，即已声明的 NB-r03-10「第 9 处 M4 残留」，**非阈值改动**。
- 行为表 ID 集合全部相等：`transitions` 14、`behavior_rows` 28、`predicates` 4、`states` 7、`actions` 12、`open_decisions` 16、`hard_invariants` 10 → **无意外增删**。

**范围结论：未发现超出声明的语义或阈值改动。**（唯一需总控补登记的是 NB-r03-08）

---

## 二、检查 2：无回归与真实标签

| 项 | 结果 |
|---|---|
| 24 项参数逐字段全等 | ✅ 0 差异 |
| 24 项全 `PENDING_APPROVAL` | ✅ F 与 `1839766` 均 24/24，非 PENDING 项数 = 0 |
| 行为表 ID 集合无意外增删 | ✅ 7 个容器全部相等 |
| 三 tag 均指 G | ✅ `s6a-g0-v1.8-r09` / `s6b-core-r04` / `stage6-freeze-20261023` → 全部 `1e2a66c…` |
| G 只含"自证记录 + STATE 的 F/G 关系" | ✅ `git show --stat G` = 9 文件：`.codex/STATE.md` + `S6-A/…_r09_selfproof/{export_selfproof.json,.md 改, transport_clone_selfproof.json,.md 增}` + `S6-B/…_r04_selfproof/` 同构 4 件。**无产品代码、无阈值、无工具改动** |
| 是否把 `NOT_ALL_SELF_PROVEN` 写成通过 | ✅ 未发现。G 内所有自证报告的主体标签均为 `commit_0725d9cf…`（= F），`subjects[].verdict` 全部 `SELF_PROVEN`，无任何文件把 G 自身声明为已自证 |

### 🔴 阻断项 B-1：冻结树内存在**空转的机读通过声明**（`claim_verify.py` 不可达 `results.append`）

**位置**：`verification/claim_verify.py:172-182`（F 引入）

```python
172    if readonly_guard:
173        print("[RO-GUARD] ...")
174        return 1
175        results.append({          # ← 在 return 之后、且在 if 块内 ⇒ 永不可达
...
182        })
```

**证明**（AST，非人工目测）：`for claim in claims:` 循环体顶层语句为 `[Assign×4, Expr, If]`，**不含 `results.append`**；`if` 块（line 172）在 `Return` 之后仍有 1 条语句 `Expr@175`。基线 `1839766` 的 `claim_verify.py` 使用 `make_claim(...)` 风格，**无**此模式 ⇒ 缺陷由 F 引入。

**后果（已由冻结产物坐实）**：
- 冻结的 S6-A r09 附录 `claim_verification.json`（`generated_at_utc8=2026-10-23 07:22:50`）**只含 1 条 claim**（`self_test_false_claim`，即那条"故意为假"的自测），却声明 `"verdict": "ALL_CLAIMS_VERIFIED"`。而冻结的 `s6a_claims()` 静态定义 6 条（S6A-C1..C6）⇒ 应产出 7 条。
- 冻结的 S6-B r04 附录（`generated_at_utc8=2026-10-23 05:36:24`）**含 5 条**（S6B-C1..C4 + self_test），**冻结的 `claim_verify.py` 无法复现它**（按现工具只会得 1 条）⇒ **冻结工具与其自身入库产物不一致**，07:22:50 与 05:36:24 之间该文件的 append 位置被改坏。
- `fix_record.md` 把 `BLK-r08-2` 的关闭证据写成 `claim_verification.json`，而该文件恰恰显示修复只完成一半（退出码真实了，claim 列表却空了）。
- S6-B `delivery_manifest.json` 的 `checks[0] = "claim_verification.verdict == ALL_CLAIMS_VERIFIED" → PASS` 只读 `verdict` 字段 ⇒ 对该缺陷**不敏感**，缺陷状态下仍判 PASS。

**判定**：这属于"机读声明把实质未验证写成通过"。它**不影响 F 的核心证据**（S6-A C1–C17 ALL_PASS 见 `selfcheck_result.json`；S6-B 26/26 用例 PASS；4 项探针；两个检查器 exit 0；传输克隆对 F 双侧 `ALL_SELF_PROVEN`），但**使 `ALL_CLAIMS_VERIFIED` 不能作为 F 的验证证据使用**，也使冻结树内工具无法重建自己的附录。

---

## 三、检查 3：三条已知限制的判断

### 限制 ①：G 自身自证 `NOT_ALL_SELF_PROVEN`
- **位置**：G 的新增 STATE 段（`.codex/STATE.md` 两段式冻结小节）声明了两个 `report/evidence/.../transport_clone_selfproof.json` 路径。
- **实际根因（与所述不符）**：所述"被 C11 映射到 run 目录查存在性"**不准确**。静态复现 C11 的 STATE 分支（`s6_g0_selfcheck.py:1163-1187`）得：
  - F：`declared_files=37 / declared_dirs=3`，`missing_*=[]` ⇒ **PASS**
  - G：`declared_files=37 / declared_dirs=5`，`missing_files=[]`，**`missing_dirs=['report/evidence/S6-A/…_r09_selfproof/transport_clone_selfproof.json','report/evidence/S6-B/…_r04_selfproof/transport_clone_selfproof.json']`** ⇒ **FAIL**
  - 真实机制：C11 把任何以 `report/evidence/` 开头的反引号 token 一律当作**目录**（`declared_dirs`）并要求 `(project_root/token).is_dir()`；G 新声明的是**文件**，故判"目录不存在"。真正的"映射到 run 目录"分支（裸文件名 → `evidence_dir/name`）在 G 上 `missing_files` 为空，**并未触发**。
- **影响**：G 无法自证（S6-A 与 S6-B 剖面同因）。F 不受影响（F 的 STATE 不含该声明）。tag 打在 G 上 ⇒ 取 tag 得到的提交本身不自证，但其自证记录如实标注主体为 F。
- **是否必须下轮修**：**必须**（否则 tag 提交永远不自证，且同型写法会被继续使用）。
- **关闭条件**：C11 对 `report/evidence/` token 区分文件/目录（或有扩展名的按文件校验、或统一按存在性校验），使 `--commit G` 得 `ALL_SELF_PROVEN`；或在 STATE 中不以 `report/evidence/…` 形式声明这两个文件。修复后重跑 G 自证并更新记录。

### 限制 ②：`tool_self_tests.py` 的 `--commit HEAD` 用例导致 "8/8" 在 HEAD=G 不可复现
- **位置**：`verification/tool_self_tests.py:69-72`（`selfproof_valid_commit`，`expect_exit=0`，命令硬编码 `--commit HEAD`）。
- **判定：如实，且我独立复现了成因链条**（读码，未跑全量套件）：套件共 8 例。HEAD=F 时该例 exit 0 ⇒ 8/8 成立；HEAD=G 时该例调用 `export_selfproof --commit G` → C11（限制①）FAIL → exit 1 ≠ 0 → 记 `UNEXPECTED` → 套件 verdict `UNEXPECTED`、工具 exit 1。⇒ 与 Wong 实测 7/8（唯一 `UNEXPECTED` 即此例）完全一致。
- **影响**：冻结 tag 指向 G，而"8/8"只在 HEAD=F 成立，故该结论在冻结点不可复现。`limitations_not_executed.json`（r09 第 120 行 / r04 第 36 行）已登记该套件"约 20 分钟/次、冻结时各跑一次、附录引用产物而不重跑"，但**未登记"HEAD 变更后不可复现"**；`tmp/6/tool_self_tests.json` 亦不入库。因此冻结树内无法自证 8/8。
- **是否必须下轮修**：**必须**（低成本）。
- **关闭条件**：把该例的 `--commit HEAD` 改为固定 `--commit <F>`（或显式传入被测提交），并把产物摘要入库或把套件纳入可复跑清单；随后在冻结 HEAD 上复现 8/8。

### 限制 ③：S6-B 版"新鲜证据两步"工具未建
- **位置**：仅存在 `verification/s6a_fresh_selfcheck_twice.py`（S6-A）；全树搜索无 S6-B 对应工具。替代物 = S6-B `s6b_build_evidence.py` 的 `[CLOSING]` 断言（`:488-494`）+ 单次 inputs/evidence exit 0 + r04 快照自证。
- **判定：如实**。"两步"的实质是"构建结束后无残留写入者 + 清单写在被绑定文件之后"；S6-B 用 `[CLOSING]`（重跑 evidence 模式，出现未声明文件即中止）+ 导出复制重跑覆盖了同一风险面，但**未记录"间隔 T 秒两次一致"**这一维度。
- **影响**：S6-B 的"构建后无写入者"缺一条时间维度证据；不影响 26/26 用例、探针与两个检查器的结论。注意 STATE 中 S6-A 的 `BOTH_ALL_PASS` 亦只由 `tmp/6/fresh_selfcheck_pair.json`（不入库）佐证。
- **是否必须下轮修**：**非必须**（等价机制存在），但建议补齐以统一双侧口径。
- **关闭条件**：新增 `s6b_fresh_selfcheck_twice.py`（或给 S6-A 工具加 `--package`）并在 r05 证据中记录两次真实退出码与 C11 状态；或正式登记"以 `[CLOSING]` 替代，不追两步"。

---

## 四、结论

**CHANGES_REQUIRED**（针对"本次冻结是否可用"）

- 未发现越界阈值/参数改动（24 项逐字段全等、全 PENDING_APPROVAL），tag 指向正确，G 内容纯净，无"NOT_ALL_SELF_PROVEN 被写成通过"。
- 但冻结树内存在 **B-1 空转的机读通过声明**（`claim_verify.py` 不可达 append ⇒ S6-A r09 附录 `ALL_CLAIMS_VERIFIED` 只覆盖 1 条平凡自测；冻结工具无法复现 S6-B 附录），且该文件正是 `BLK-r08-2` 的声明关闭证据 ⇒ 冻结不可用。
- **F 的有效性判断：F 的交付内容不受影响**（核心证据链独立于 `claim_verify`：C1–C17 ALL_PASS、S6-B 26/26、4 探针、两个检查器 exit 0、传输克隆对 F 双侧 `ALL_SELF_PROVEN`）。受影响的只是 F 内"验证附录"这一件产物与其工具的可复现性。修复 B-1 后重生成两份附录即可。

### 阻断/非阻断清单

| 级别 | 项 | 关闭条件 |
|---|---|---|
| 阻断 | B-1 `claim_verify.py:175` 不可达 `results.append` | 移入循环体；重跑 `--package s6a`（应 7 条）与 `--package s6b`（应 5 条），两份附录与冻结工具一致且 `exit_code` 为真实值 |
| 非阻断 | N-1 限制①根因表述不准（实为 C11 把 `report/evidence/*.json` 当目录） | 修 C11 的文件/目录判别；修正 STATE/记录中的归因 |
| 非阻断 | N-2 限制②"8/8"不可复现且未登记 | 固定被测提交 + 登记不可复现条件 |
| 非阻断 | N-3 NB-r03-08 属语义改动但未在任务卡声明中列名 | 总控补登记（已由 FINAL_B_r03 派单 `NB-r03-01..12` 授权） |
| 非阻断 | N-4 行为表 `status_label` 仍写"v1.6（r07 收尾版）"（基线遗留，非 F 引入） | 下轮统一 |
| 非阻断 | N-5 限制③ S6-B 无"两步"工具 | 补齐或正式登记替代口径 |

---

## 五、命令与真实退出码

| # | 命令 | 退出码 |
|---|---|---|
| 1 | `git -C w6 rev-parse HEAD` / `--abbrev-ref HEAD` / `status --short` | 0 / 0 / 0（输出为空 = 0 改动） |
| 2 | `git -C w6 rev-list -n1 <tag>` ×3 | 0（三者均 `1e2a66c…`） |
| 3 | `git -C w6 show --stat G` | 0 |
| 4 | `git -C w6 diff --stat 1839766 F` | 0 |
| 5 | `git -C w6 diff --name-status 1839766 F` | 0 |
| 6 | `git -C w6 diff --name-status F G` | 0 |
| 7 | 24 项参数逐字段 + ID 集合比对（`cmp2.py`，`PYTHONUTF8=1`） | 0（0 差异 / 全等） |
| 8 | `transitions` 明细比对（`cmp3.py`） | 0（仅 M4 两字段） |
| 9 | C11 STATE 分支静态复现（`c11_static.py`） | 0（F=PASS，G=FAIL） |
| 10 | `claim_verify` 不可达 append 的 AST 证明（`ast_proof.py`） | 0（循环体不含 append；if 块 return 后有 1 条语句） |
| 11 | 自证 verdict 提取（`verdicts.py`）、claim 汇总（`claims.py`）、清单行（`manifest_rows.py`） | 0 |
| 12 | `git -C w6 grep -n` 多组 token 检索（write_manifest / FIXPOINT-B / [CLOSING] / action_records / m4_reachability / NOT_ALL_SELF_PROVEN / tool_self_tests） | 0（个别 `grep -l` 组合返回 1 = 无匹配，非失败） |
| 13 | `git -C w6 diff … -- verification/{check_stage_delivery,export_selfproof,claim_verify,s6b_*}.py` | 0 |
| — | 自查中的 `cmp_params.py` 首次运行 | 1（**我方脚本 bug**：`parameters` 是 list 而非 dict；已修正，与仓库无关） |
| — | `final_probe.py` 的 AST 单行 | 1（**我方脚本 bug**：`ast.Dict` 无 `.value`；所需数据已由前序命令取得，未重跑） |

**刻意未执行**：`tool_self_tests.py` 全量套件（`limitations_not_executed.json` 登记约 20 分钟/次）、任何合成/实现/上板流程、`export_selfproof.py --commit G` 实跑（限制①已用静态复现 + 前一位复核者的实测共同确定）。

**只读性**：全部验证写入 `tmp/review/FREEZE_DELTA_B_20261023_r01/`；复核前后 `git -C w6 status --short` 均为空。