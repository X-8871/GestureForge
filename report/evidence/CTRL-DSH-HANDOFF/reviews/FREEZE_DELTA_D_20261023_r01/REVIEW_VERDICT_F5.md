# 独立复核：批准应用轮增量（F5/G5/G5b）

- 复核人：独立 Reviewer（批准应用轮增量；只读，仅写本目录 `D:\FPGA_Competition\tmp\review\FREEZE_DELTA_D_20261023_r01\`）
- 时间：2026-10-23 09:24–09:5x（UTC+8）
- 对象：`D:\codex-worktrees\w6`（`stage6-interact-prep`），HEAD=`c7ae6b4991bc769bdbd9683036a3c210b153c620`（G5b），工作区 0 改动
- 版本：F4=`6b8e5f2a23ce6f7dec41fc9992141b3423612081`、G4=`f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d`、F5=`caa9728af84b0a5b79bed17427eec0091b922923`、G5=`61caac0d8ce7be6f2ef8dfcd2380f3943cd6029f`、G5b=`c7ae6b4991bc769bdbd9683036a3c210b153c620`
- 未跑重型套件（未跑 `tool_self_tests.py` 20 分钟级套件；未跑 S6-B 26 例驱动）

## 结论

**`CHANGES_REQUIRED`。**

- 批准**应用本身**（24 项参数状态、批准记录引用、C4 断言语义、反向自测、参数值零差异）**正确**；F5 可被引用为「**批准已应用到规范行为表**（参数按草案值获批、值未修改）」。
- 但 **F5 目前不能被引用为「已批准冻结版」**，原因有两条阻断：
  - **B-D1**：F5 未通过项目自定的 F6 冻结自证（S6-A 剖面 `[1,0,2]`、exit 1），却仍被打上"冻结"tag `stage6-freeze-20261023-r4`，且 STATE 把该失败误定性为"非产品缺陷的工具链缺陷、不再消耗轮次"。该失败可确定性复现，根因是**行为表 `run_id` 未随新 RunId 更新**（仍指 r10），并非换行/导出环境噪声。
  - **B-D2**：本轮**新增**的 r11/r06 证据与人类规格文档仍大量声明"全部阈值 `PENDING_APPROVAL`/待批准"，规格文档甚至把历史修订记录回改成"当时已批准"（失实）；S6-B 侧不但没有"不得存在 PENDING"的等价断言，反而在新快照里输出 `all_parameters_pending_approval: true`。

## 一、命令与真实退出码（全部在传输克隆 `clone/w6_transport`（HEAD=G5b）或 w6 只读执行）

| # | 命令 | 真实结果 |
|---|---|---|
| 1 | `git clone --no-local --depth 15 --no-single-branch D:/codex-worktrees/w6 clone/w6_transport` | exit **0**（41 s；远端 3 条 `Filename too long` 警告属 S2B-T16 无关路径） |
| 2 | 克隆内 `for h in F4 G4 F5 G5 G5b: git cat-file -t` | 全部 `commit`，exit 0 |
| 3 | 克隆内 `git rev-list -n1 <tag>` r1/r2/r3/r4 | `1e2a66c` / `8ecd92c` / `f5b749e`(=G4) / `61caac0`(=G5)，exit 0 |
| 4 | 克隆内 `git merge-base --is-ancestor` F4→G4→F5→G5→G5b | 4/4 OK，exit 0 |
| 5 | 克隆内 S6-A 自检（r11 清单）：`python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261023_r11/hand_computed_cases.json --upstream …/upstream_bindings.json --out <review>/clone_selfcheck_r11.json --project-root <clone> --evidence-dir <clone>/report/evidence/S6-A/s6a_g0_20261023_r11 --manifest …/delivery_manifest.json --state .codex/STATE.md` | `{"status":"ALL_PASS"}`，C1–C17 全 PASS（C4 detail："24 项与动作映射均为 APPROVED_20261023 且批准索引齐全"）；**exit 0** |
| 6 | 克隆内 `check_stage_delivery --mode evidence --manifest <clone>/…/r11/delivery_manifest.json` | `{"status":"CHECKS_OK"}`，**exit 0** |
| 7 | 克隆内 `check_stage_delivery --mode inputs --manifest <clone>/…/r11/inputs_manifest.json` | `{"status":"CHECKS_OK"}`，**exit 0** |
| 8 | 克隆内 `python -B verification/approval_regression.py --project-root <clone> --run-dir report/evidence/S6-A/s6a_g0_20261023_r11 --out <review>/clone_approval_regression.json` | `{"verdict":"AS_EXPECTED","baseline":[0,"PASS"],"injected":[1,"FAIL"]}`，**exit 0** |
| 9 | 克隆内 `python -B verification/export_selfproof.py --project-root <clone> --commit caa9728af84b0a5b79bed17427eec0091b922923 --out <review>/clone_export_selfproof.json` | `{"verdict":"NOT_ALL_SELF_PROVEN","subjects":[["commit caa9728a…","NOT_SELF_PROVEN",[1,0,2]]]}`，**exit 1**（run_id=`s6a_g0_20261023_r10`） |
| 10 | w6：`git diff --name-status 6b8e5f2a caa9728a` | 见 §二（范围清单） |
| 11 | w6：`git diff 6b8e5f2a caa9728a -- report/evidence/S6-A/s6a_g0_20261023_r10 report/evidence/S6-B/s6b_core_20261023_r05` | **空输出，exit 0**（r10/r05 未被就地改写） |
| 12 | w6：`git status --short` | **空**（工作区 0 改动） |
| 13 | w6：`git show --name-only G5` / `G5b` | G5 = 8 个 `_selfproof` 记录；G5b = `.codex/STATE.md`（+4 行） |
| 14 | w6：`git reflog -n 30` 过滤 F4/G4/F5/G5/G5b | 5 条均为 `commit:`（**无 amend 记录**）；amend 仅存在于历史中间提交 `efb9f19`/`1839766`/`e3aeb09`/`43f7995` |
| 15 | 独立抽验脚本（自研）`python -B scripts/04_param_values.py <w6>` | `n_f4=24 n_f5=24 id_sets_equal=True value_diffs=[] field_removed=[] field_changed=[]`；**exit 0** |

## 二、增量范围核对表（F4→F5，`git diff --name-status`）

| 类别（父级允许项） | 实际文件 | 判定 |
|---|---|---|
| 行为表 status/approval_status/approval_ref/approval_record/semantics_status | `docs/stage6/s6a_stage6_g0_behavior_v1.json`（158+/97−） | ✅ 只含 `status/status_label/status_note`、28 行 `semantics_status`、`map_status`、`feedback_visibility_duration`、24 项 `approval_status/approval_ref`、新增 `approval_record`、U6-12/13/15/16 的 `decision/approved_caliber/value_status`、`B16 reachability_note`、`reachability.not_counted_note`、`parameter_notes.T6-S04` 指针改写 |
| 规格文档 37 处 `PENDING_APPROVAL`→`APPROVED_20261023` + 批准说明 | `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md`（43+/37−） | ⚠️ 替换本身在允许范围，但见 **B-D2**（残留 12 处"待批准"、8 条历史记录被回改） |
| `behavior_rows.semantics_status` | 同上 JSON（28 处） | ✅ 仅状态令牌 |
| C4 断言 + `approval_regression.py` | `verification/s6_g0_selfcheck.py`（31+/13−）、**新增** `verification/approval_regression.py`（89 行）、`verification/claim_verify.py`（+7：新 claim `S6A-C7`） | ✅ 语义与批准记录 §2.2 一致 |
| 新 RunId 证据与清单 | **新增** `report/evidence/S6-A/s6a_g0_20261023_r11/**`（45 文件）、`report/evidence/S6-B/s6b_core_20261023_r06/**`（含 26 例矩阵/日志） | ⚠️ 文件为新增（非改写旧 RunId），但内容含 **B-D2** |
| `B16` 不可达登记 | JSON `behavior_rows.B16.reachability_note`、`reachability.not_counted_note` | ✅ 与 receipt §1 一致 |
| S6-B 接受已批准口径 | `src/stage6/s6_params.py`（8+/7−） | ⚠️ 口径放宽本身允许；但 `all_parameters_pending_approval` 语义被改坏（见 B-D2） |
| STATE | `.codex/STATE.md`（54+/0−） | ✅ 记录本轮 |
| **不在允许清单字面内** | `report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/**`(4)、`report/evidence/S6-B/s6b_core_20261023_r05_selfproof/**`(4) 被改写 | 见 N2（非阻断） |

**参数值/阈值/行为语义改动：无。** 我对 24 项逐项比对（`draft_value`/`comparison`/`unit`/`kind`）：`value_diffs=[]`、无字段删除、无（除批准类字段外的）字段变化。
行为语义侧唯一新增的"可达性"文本即 `B16` 登记与 `not_counted_note`（允许项）；参数阈值文本、迁移条件、时间锚点、动作映射类型集合均未变。

### 独立抽验的参数值（与 F4 逐字节一致）

| ID | F4 | F5 | 一致 | approval_status | approval_ref |
|---|---|---|---|---|---|
| `T6-K01` | 1000 ms | 1000 ms | ✅ | APPROVED_20261023 | `report/evidence/CTRL-DSH-HANDOFF/decisions/stage6_approval_receipt_20261023_r01.md` |
| `T6-C01` | 2 帧 | 2 帧 | ✅ | APPROVED_20261023 | 同上 |
| `T6-S02` | 6 帧 | 6 帧 | ✅ | APPROVED_20261023 | 同上 |

（抽样方式：`random.Random(20261023).sample(24 ids, 3)`；24 项全部 `value_identical=True`。）

## 三、批准与 C4 语义（第 2 项）

- **批准记录真实存在且有原文与日期**：`stage6_approval_receipt_20261023_r01.md` 在 **main** 分支提交 `2189890748372739158c6fbc9bc7a0da010b39d4`（2026-10-23 09:07:36 +0800，`docs(decision): record Wong approval …`）内已入库；内容含用户原文「**按你建议**」「**阶段7暂时不开**」与日期 2026-10-23；工作区字节与该提交一致（diff 空）。
- **approval_ref 指向 approval_record**：24/24 参数的 `approval_ref` 均等于 `approval_record.receipt`（C4 断言 + 我独立复算：`params !=ref: []`、`params !=APPROVED: []`）。JSON `approval_record` 含 `decided_by=Wong`、`date=2026-10-23`、`user_words`、`receipt`、`sheet`、`scope`、`stale_age_limit=200ms`。
- **我自己制造的 PENDING 例（不依赖出库工具，在克隆的副本内注入）**：

| 注入 | 自检结果 | C4 | 真实退出码 |
|---|---|---|---|
| A `parameters[2]`(T6-A03) `approval_status="PENDING_APPROVAL"` | `FAILED`（2 项 FAIL） | **FAIL**：`T6-A03 的 approval_status 仍含 PENDING：PENDING_APPROVAL` | **1** |
| B `actions.map_status="PENDING_APPROVAL"` | `FAILED` | **FAIL**：`动作映射仍标为待批准：PENDING_APPROVAL` | **1** |
| C 删除 `parameters[5]`(T6-S02) 的 `approval_ref` | `FAILED` | **FAIL**：`T6-S02 缺少 approval_ref（批准记录索引）` | **1** |
| D 基线（同一复制流程、不注入） | C4 PASS（仅 C11 因我裁减副本而 FAIL，属流程伪影） | PASS | 1（仅 C11） |
| E 克隆全树基线（§一#5） | `ALL_PASS` | PASS | **0** |

→ C4 具备真实判别力（三类反向注入均被捕获且退出码非 0），批准纪律的**反向**要求兑现。

- **S6-B 侧是否存在"不得存在 PENDING"的等价断言？——没有，且这是不可接受的缺口。**
  - S6-B 侧没有任何 approval 断言（`grep -n approval verification/s6b_*.py verification/check_stage_delivery.py` 无命中）；
  - 反而在**本轮新增**的 r06 证据里机读输出：`params_snapshot.json` L5 `behavior_status = G0_PACKET_APPROVED_20261023`，L242 `"all_parameters_pending_approval": true`、L243 `"thresholds_are_draft_not_approved": true`（同文件自相矛盾）；
  - 根因：`src/stage6/s6_params.py:264` 把该布尔放宽为 `in (PENDING_APPROVAL, APPROVED_20261023)`，`verification/s6b_run_cases.py:323` 原样写进快照 → 字段名（"全部参数待批准"）在批准后成为假命题。
  - 关闭条件：S6-B 侧增加"必须为 APPROVED_20261023 / 不得含 PENDING"的断言（fail-closed），并把该布尔改名为 `all_parameters_approved_20261023` 或按真实状态取值后重生成 r06。

## 四、链与标签完整性（第 3 项）

| 项 | 结果 |
|---|---|
| `git cat-file -t` F4/G4/F5/G5/G5b（**传输克隆**内） | 5/5 `commit` |
| tag → 提交 | r1→`1e2a66c`(G)、r2→`8ecd92c`(G2)、r3→`f5b749e`(**=G4**)、r4→`61caac0`(**=G5**)；tag 均为 annotated（`type=tag`）；**旧 tag 未移动**；per-profile tag `s6a-g0-v1.8-r09`/`s6b-core-r04` 仍指 `1e2a66c` |
| 祖先链 | F4→G4→F5→G5→G5b 4/4 成立；first-parent 日志与任务描述一致 |
| `git show --stat G5` / `G5b` | G5 **只含** 8 个 `_selfproof` 记录（r11+ r06 各 4）；G5b **只含** `.codex/STATE.md`（4 行）——符合"只含自证记录/STATE" |
| amend/rebase | reflog 中 **F4/G4/F5/G5/G5b 均为普通 commit，无 amend**；amend 仅出现在历史中间提交（`efb9f19`=F3、`1839766`、`e3aeb09`、`43f7995`），均在 F4 之前且 STATE 已有勘误记录。F4/G4/F5/G5/G5b 哈希与任务给定值逐字符一致 ⇒ 内容不可被改写（内容寻址） |
| 旧哈希可达性（克隆内） | F2 `33b1fee`、F3 `efb9f19`、G `1e2a66c`、G2 `8ecd92c`、r09-F `1839766` 全部 `commit`；被 amend 取代的 `66f45dd`/`aabce4c`/`05126fd` 不可达（历史中间态，非任何被引用提交） |

## 五、如实性与可复现（第 4 项）

- **r10/r05 未被就地改写**：`git diff 6b8e5f2a caa9728a -- report/evidence/S6-A/s6a_g0_20261023_r10 report/evidence/S6-B/s6b_core_20261023_r05` → 空输出、**exit 0**。（注意其**兄弟目录** `_selfproof` 被改写，见 N2。）
- **克隆侧**：S6-A 自检 `ALL_PASS` exit 0；`--mode evidence` `CHECKS_OK` exit 0；`--mode inputs` exit 0。STATE 所称"**55/55** 声明文件哈希全匹配"独立吻合 —— r11 清单恰 55 项（运行时目录 44 + 外部绑定 11），C11 detail 写明"manifest 双向一致（运行目录 44 个文件 + 外部绑定 11 个文件哈希复算通过）"。
- **工具链缺陷描述（STATE L220）判定：与事实不符，且被误定性/被"结案"。**
  - STATE 写"报 `[1,0,2]`（**3 文件**哈希不符）"：实测为 **4 个文件**（`files[0]` spec md、`files[1]` behavior json、`files[7]` claim_verify.py、`files[9]` s6_g0_selfcheck.py），报错文字为"原字节/CRLF→LF/LF→CRLF 三种口径均不匹配"。
  - STATE 写"而同一提交在普通克隆中全部通过 ⇒ 归入认证工具链单列开放"：克隆内通过的是 **r11 包**（新 RunId），自证工具复算的是 **r10 包**（被取代的上一轮）；两者不是同一对象，此对照不成立。
  - 真相（可复现、确定性）：`verification/export_selfproof.py:180-181` 用**行为表 JSON 的 `run_id`** 定位 S6-A 证据目录，而该字段在 F4/F5/HEAD 一直是 `s6a_g0_20261023_r10`；F5 修改了 r10 清单所绑定的 4 个源文件字节 ⇒ r10 清单如实报不符。这是"交付物 `run_id` 未随新 RunId 同步"的一致性问题，**不是**换行/导出环境的工具链偶发。
  - 未被"掩盖"的部分：失败自证报告（`…r11_selfproof/export_selfproof.json`、`…r10_selfproof/…`）已随 G5 入库，`verdict=NOT_SELF_PROVEN`、`[1,0,2]` 白纸黑字。被"误定性"的部分：把它称作"非产品缺陷、工具链单列开放、不再消耗轮次"，并在同一 STATE 段宣布"本轮冻结实测（F5/G5）"。
  - 由此的实质后果见 **B-D1**：项目永久规则（STATE L9）与 lead 自定判定线（STATE L97）对 F5 均不成立。
- **"优先级 2 未做"三项登记：如实、到位 ✅** —— STATE L212-216 与 r11 `limitations_not_executed.json` 的 `open_gaps_batch_c`（L133-135）均登记：① r10 陈旧 `fresh_selfcheck_pair.json`（r11 已重生成）；② 套件两条必 FAIL 例对真实 run-dir 跑 `claim_verify`（会改写冻结附录）；③ 套件 `skipped` 曾计 `AS_EXPECTED`（fail-open）。三项都写明"未做、不得作为通过凭据"。

## 六、阻断问题（关闭条件）

### B-D1 F5 未达自定冻结条件（S6-A 剖面 `[1,0,2]`），却被标为冻结并结案
- 位置：`verification/export_selfproof.py:180-181`；`docs/stage6/s6a_stage6_g0_behavior_v1.json:run_id`；`.codex/STATE.md` L9/L97/L218-220；tag `stage6-freeze-20261023-r4`。
- 证据：§一#9（克隆内**独立复现**，exit 1，`[1,0,2]`）；`…r11_selfproof/export_selfproof.json`（NOT_SELF_PROVEN）；`…r11_selfproof/transport_clone_selfproof.md`（表：selfcheck=1、inputs=0、evidence=2）。
- 影响：F5 不满足"任何冻结/交付提交必须自证（三项 exit 0）"与"S6-A `[0,0,0]` + S6-B `[0,0,0,0]`"，却在 tag r4 上被引用为冻结；下游若按 tag 取"已批准冻结版"，其 F6 依据实际不存在。（S6-B `--s6b-run` 模式会跳过 S6-A 清单复算，故 S6-B 剖面 `[0,0,0,0]` 不覆盖该缺口。）
- 关闭条件：把行为表 `run_id` 指向 r11（或在 JSON 明确区分契约 RunId 与证据 RunId，并让 `export_selfproof` 显式接受 S6-A 运行目录），使 `--commit <交付提交>` 的 S6-A 剖面 = `[0,0,0]`、exit 0；同步修正 STATE/limitations 的定性文字；随后重做 F/G（F6/G6）并重打 tag（或把 r4 明确降级为非冻结记录）。

### B-D2 "已批准"冻结点上仍存在与批准相反的文本（含机器可读假值）与失实的历史修订记录
- 规格文档（人类权威）残留 12 处：L9（`G0_PACKET_APPROVED_20261023`**（待批准）**）、L10（"一律登记为**待批准**…在获批前…"）、L128（"**不是已批准、不是已冻结**"）、L130（表头"参数（待批准）"）、L171（"动作映射为提案，待批准" ↔ `map_status=APPROVED_20261023`）、L185（U6-14"待批准" ↔ APPROVED）、L280（"## 14. 阈值与指标登记（**全部待批准**）"）、L282（"**不是**已批准门槛"）、L320/L321（T6-A01/T6-A03"（待批准）"）、L397（"全部阈值待批准"）。
- 规格文档历史修订记录被回改成失实：L14(v1.8/r09)、L21(v1.7)、L28(v1.6)、L30(v1.5)、L32(v1.4)、L34(v1.3)、L36(v1.2/r03, **2026-10-22**)、L38(v1.1/r02, **2026-10-22**，且写"24 项仍全部 `APPROVED_20261023`")——批准发生在 2026-10-23，历史行当时口径应为 `PENDING_APPROVAL`。
- 本轮**新增**证据仍宣告 PENDING：
  - S6-A r11：`S6A_run_summary.md`（标题"v1.8 / r09"、L6）、`delivery_manifest.json:378`、`coverage_matrix.json:28/57/58/122/127/132/224`、`fix_record.json:81`、`fix_record.md:5`、`limitations_not_executed.json:44`；另 `limitations_not_executed.json:19` 仍引 S6-B **r03/23 例**（本包实际 r06/26 例）。
  - S6-B r06：`inputs_manifest.json:9/15/27`、`delivery_manifest.json:9/398`、`limitations_not_executed.json:15/55`、`reachability_notes.json:5`（`derived_from` v1.6）、`s6b_run_summary.md:7`。
  - 最重的机读假值：`params_snapshot.json` L242 `all_parameters_pending_approval=true`、L243 `thresholds_are_draft_not_approved=true`（同文件 L5 已是 `G0_PACKET_APPROVED_20261023`）。
- 根因：`verification/s6a_build_evidence.py:270`、L418-423（硬编码摘要/限制文案）、`verification/s6b_build_evidence.py:71-77`（`interface_reason()`）、`src/stage6/s6_params.py:264` + `verification/s6b_run_cases.py:323`（布尔语义）均未随批准同步。
- 关闭条件：更新上述构建器与字段语义 → 以**新 RunId** 重生成两包（不就地改写 r11/r06）；规格文档拆分"当时口径/现口径"（12 处改准，8 条历史行写回 `PENDING_APPROVAL` 或显式标注为历史语境）；给 C4 增加"批准版交付包内不得出现 `PENDING_APPROVAL`/待批准陈述"的机读断言，并补 S6-B 侧等价断言（fail-closed）。

## 七、非阻断观察

- **N1** `approval_ref` 目标不在冻结分支：receipt 在 **main**（`2189890`）已入库，但 w6 树内不存在（克隆内 `receipt exists in clone tree: False`）；C4 只校验"非空 + 与 `approval_record.receipt` 一致"，不校验存在性。STATE L192 已披露"（主仓库；w6 内引用见行为表 approval_record）"，属已披露口径，但 F5 的批准链仍依赖跨分支外部文件。
- **N2** F4→F5 还改写了上一轮的 `r10_selfproof/`、`r05_selfproof/` 8 个记录（主体由 F2 改为 F4、刷新时间戳/换行口径），不在父级允许清单字面内；因 `_selfproof` 按 N-r07-2 设计可提交后回填、且 r10/r05 证据目录逐字节未变，判非阻断，建议把该规则写清。
- **N3** 陈旧文档串：`src/stage6/s6_params.py:11`、`src/stage6/s6_core.py:9` 仍写"强制校验每个参数仍为 `PENDING_APPROVAL`"。
- **N4** `export_selfproof.py` 的 Markdown 模板串台：S6-B 剖面的报告标题也写成"# S6-A 冻结自证报告"，`r06_selfproof/transport_clone_selfproof.md` 中"RunId"显示 S6-A 的 r10。
- **N5** 版本令牌不一致：文档标题/`status_label` 写 v1.9，而 `artifact_version` 仍 `S6A-G0-v1.8`（C1 白名单接受 v1.8，故机检通过）。
- **N6** `.codex/STATE.md` 231 行，超出 AGENTS.md"建议不超过 80 行"。

## 八、确认良好项（供 lead 直接引用）

1. 24/24 参数 `approval_status=APPROVED_20261023`、无 PENDING、`approval_ref` 齐备且等于 `approval_record.receipt`；顶层 `status=G0_PACKET_APPROVED_20261023`。
2. 参数值相对 F4 **零差异**（我独立逐项复算 24 项，非采信自述）；抽样 `T6-K01=1000`、`T6-C01=2`、`T6-S02=6` 逐字节一致。
3. 行为表/迁移/时间锚点/动作类型集合无未授权语义改动；`B16` 登记与 receipt 决定一致。
4. 链/标签完整：5 提交齐备、r1/r2/r3 未移动、r4→G5、祖先链成立、被引用提交无 amend/rebase。
5. `G5` 只含自证记录、`G5b` 只含 STATE；w6 工作区 0 改动；r10/r05 证据目录未被就地改写。
6. 克隆内 S6-A 自检 `ALL_PASS`、`--mode evidence`/`--mode inputs` `CHECKS_OK`（均 exit 0）；"55/55" 独立吻合。
7. C4 反向判别力真实（我三类注入均 FAIL、exit 1；出库工具 `AS_EXPECTED`）。
8. 优先级 2（批次 C）三项在 STATE 与 r11 limitations 如实登记。
9. 失败自证报告本身已入库、未删除、未粉饰数值（问题在定性，不在隐瞒原始事实）。

## 附：本目录产物

`01_chain_w6.txt`、`01b_chain_clone.txt`、`02_delta_scope_w6.txt`、`03_versions_w6.txt`、`04_param_values.txt/.json`、`05_selfproof.txt`、`06_clone_checks.txt`、`07_inject.txt`、`08_chain_supplement.txt`、`09_citations.txt`、`clone_selfcheck_r11.json`、`clone_export_selfproof.json/.md`、`clone_approval_regression.json`、`inject_*_selfcheck.json`、`scripts/*.sh|py`。