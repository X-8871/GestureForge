# S6-A r04 独立复评报告（第 4 轮 · 独立 Reviewer）

- **审查对象**：工作树 `D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**被审提交 `b20b670`**
  （`b20b6705e8c7dd6c43cc2195860e3fc84e1c4ec7`，提交信息 `fix(stage6): S6-A v1.3/r04 closes third-round review R3-B01/R3-B02, N01..N05 and STABLE latch`）
- **基线**：r03=`2ce290f`、r02=`3b59674`、r01=`1fe4648`
- **审查时间**：2026-10-23 01:41 起（UTC+8）
- **写入范围**：仅 `D:\FPGA_Competition\tmp\review\S6A_r04_20261023_r01\`（自建）。被审工作树未写入任何文件；
  收尾核验 HEAD 仍为 `b20b6705e8c7…`，`git status --short` 仍只有评审前既存的 2 项未跟踪
  （`?? docs/stage6/s6b_frozen_interface_v1.json`、`?? src/stage6/`）。
- **独立性声明**：本轮评审与前三轮评审者无关联。上轮结论（R3-B01/R3-B02 等）仅作为**待证伪的断言**使用，
  全部结论由本轮自行复算/自写脚本/故障注入得出；未照抄历史结论。上一轮 `REVIEW_r03.md` 在磁盘上只有 8 行摘要、
  无 `review_result.json`，其明细无法从证据目录复核，故本报告只按任务卡给出的 R3-B01/R3-B02 描述作为起点。

## 结论

# `PASS`

- **阻断问题：0 项。**
- 非阻断问题：5 项（`N-r04-01` … `N-r04-05`），均不影响本包任何结论或关闭判定，列为下一修订建议。
- **结论边界**：本结论只覆盖 r04 的 S6-A G0 包（规格 + 行为表 JSON + 自检/构建器 + r04 证据目录），
  **不代表 G0/G2/G4/G5**，不涉及 6-B/6-C/6-D/6-E、状态机实现、摄像头、HDMI、板卡、hw_server。
  自检 `ALL_PASS` 只表示规格一致性/算术/证据存在性复算通过，不表示接口语义正确或实物验收通过。

---

## 1. 我实际执行的命令与真实退出码

所有命令在 `D:\codex-worktrees\w6` 下执行，`--project-root` 一律用绝对路径 `D:/codex-worktrees/w6`；
所有 `--out` 均落到隔离评审目录，未写入被审目录。

| # | 命令（要点） | 真实退出码 | 结果 |
|---|---|---|---|
| 1 | `python -B verification/s6_g0_selfcheck.py --json docs/stage6/s6a_stage6_g0_behavior_v1.json --doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases report/evidence/S6-A/s6a_g0_20261022_r04/hand_computed_cases.json --upstream …/upstream_bindings.json --project-root D:/codex-worktrees/w6 --evidence-dir …/s6a_g0_20261022_r04 --manifest …/delivery_manifest.json --state .codex/STATE.md --out <隔离目录>/my_selfcheck_r04.json` | **0** | `status=ALL_PASS`，**17 项检查全 PASS，errors=0** |
| 2 | `python -B verification/check_stage_delivery.py --mode inputs --manifest …/inputs_manifest.json` | **0** | `CHECKS_OK`（与提交的 `check_inputs_mode_output.txt` **逐字节相同**） |
| 3 | `python -B verification/check_stage_delivery.py --mode evidence --manifest …/delivery_manifest.json` | **0** | `CHECKS_OK`（与提交的 `check_evidence_mode_output.txt` **逐字节相同**） |
| 4 | 自写 `my_bidir.py`（独立实现全量双向比较 + 文本级绑定审计） | 0 | 见 §3 |
| 5 | 自写 `diff_r03_r04.py`（`git cat-file blob 2ce290f:` / `b20b670:` 二进制取字节后逐字段比较） | 0 | 见 §5 |
| 6 | 自写 `fault_injection.py`（16 个注入用例 + 1 个基线对照，均调用**最终版**自检） | 0（脚本本身） | 见 §4（各用例自检退出码 0/1 分别记录） |
| 7 | 自写 `legacy_rerun.py`（用 r01/r02/r03 真实 git 字节 + 最终版自检重跑） | 0（脚本本身） | r01 **exit 1**、r02 **exit 1**、r03 **exit 1**，见 §6 |
| 8 | 自写 `upstream_and_cases.py`（上游哈希自算、`hashes_sha256.txt` 交叉核对、HC-27/28/29 审查） | 0 | 见 §7 |
| 9 | 自写 `claims_and_files.py` / `claim_contexts.py` / `final_details.py`（声明纪律与文件存在性） | 0 | 见 §8 |

> 说明：`s6a_rerun_legacy_failures.py` 本身会写入 `<root>/tmp/6/S6-A/<run_id>/legacy/`，
> 为严格遵守“只写隔离目录”，我**没有直接运行它**，而是完整复刻其提取+调用逻辑（同样的 `git cat-file blob` 二进制提取、
> 同样的自检参数），全部落盘到隔离目录；因此 §6 是对它行为的**独立复现**，而非转述其结果。

## 2. 自算哈希（SHA-256，我自己对文件字节计算）

被审源码/规格/状态：

| 文件 | 我自算 SHA-256 |
|---|---|
| `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` | `f33e9a72ebbfed9a69d57ce2c7cdedf3803fa77496df7112c915b18a75ba79ba` |
| `docs/stage6/s6a_stage6_g0_behavior_v1.json` | `c6c11ed324ac6857f0cd4513c9cee7efa053052bd1c1e0c51e112dae4d0ec137` |
| `verification/s6_g0_selfcheck.py` | `b4fd70261f096c8a9c59ab328f6d1a6605d884b316dd483939e1629970b56bb9` |
| `verification/s6a_build_evidence.py` | `c6621484d730b5a190812da2d1f88eb4599851ba9310238a6a281b7cb67a4587` |
| `verification/s6a_rerun_legacy_failures.py` | `770716fd356e706c5180a294cb67cadb377ffffcdff6bf970bb9305f5805f0d9` |
| `.codex/STATE.md` | `76346fbcaeb4d4b19a779b37e0998d09e62fca964a9773247f21b11028aec41f` |

- 我自算的两个关键哈希与入库 `selfcheck_result.json.inputs` **完全一致**：
  `behavior_json_sha256=c6c11ed3…`、`human_doc_sha256=f33e9a72…`、`hand_cases_sha256=e53a965a…`。
- 对 r04 证据目录 23 个文件逐一自算，与 `hashes_sha256.txt`（21 条，按设计不含 `delivery_manifest.json` 与自身）
  交叉核对：**解析 21 条，缺失 0，不符 0**。
- 对 `delivery_manifest.json` 中全部带 `path+sha256` 的条目（29 条 = 运行目录文件 + 6 个外部绑定文件）自算复核：
  **声明但缺失 0，哈希不符 0**。

## 3. 必须核查项 1、2：R3-B01 / R3-B02 是否真关闭

### 3.1 R3-B01（§12 两行未绑谓词）

| 检查点 | 我的核验方式 | 结果 |
|---|---|---|
| §12 `T6-S02` 行 | 读原文 §12 表 | ✅ 已为「连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`」 |
| §12 `T6-L02` 行 | 读原文 §12 表 | ✅ 已为「`t_now − t_last_target_continues ≥ T6-L02`」 |
| 锚点是否有真定义 | 搜全文 | ✅ 三处定义：§3（"丢失时间锚点"条）、§12（"R3-B01 定义"条）、§13（丢失时间条件条）；JSON 另有 `time_anchors.t_last_target_continues` |
| 是否与 M10/B10 一致 | 逐字比对 M10 条件 / B10 条件 / §12 行 / `time_anchors` | ✅ 四处口径一致（均为「距上一次 `TARGET_CONTINUES` 成立 ≥ `T6-L02`，取较早满足者，不得用 `WINDOW_MATCH` 判丢失」） |
| 残留 `matched_frames`/`t_last_match`/`t_submit+` | 全文/JSON 逐 token 定位 + 上下文判定 | ⚠️ **字面仍出现**，但**无一处是规范性用法**：文档 4 处、JSON 4 处全部位于「已废弃」禁令句或 r04 修订说明内（例：§12「**不得**再使用已废弃的 `t_last_match`（已废弃）」；§18「原 `t_last_match`/`matched_frames`/`t_submit+` 写法已废弃」）。**判定：R3-B01 实质关闭** |
| C12 禁用标识符扫描是否有判别力 | 自行构造文本片段注入（§4） | ✅ f2/f3/f4/f5 全部被 C12 捕获（exit 1）；f6 证明“已废弃”白名单确实生效 |

**我自己构造的文本片段试验（关键）**：
- 注入 `连续匹配帧数 ≥ T6-S02` → C12 FAIL：`文档仍含未绑定谓词的表述：'连续匹配帧'；'匹配帧数'`
- 注入 `t_now − t_last_match ≥ T6-L02`（§12 丢失时间行）→ C12 FAIL：`仍含已废弃标识符 't_last_match'（未标注"已废弃"）`
- 注入规范句 `锚点名称：matched_frames 表示匹配帧计数。` → C12 FAIL
- 注入 `丢失判定锚点取 t_last_match 的值作为条件输入。` → C12 FAIL
- 把“废弃”放在距 token **>60 字符**处 → **仍 FAIL**（±60 字符窗口不能靠远距离关键词绕过）
- 紧邻写 `已废弃写法 t_last_match 不再使用` → **PASS**（白名单按设计放行历史说明）

### 3.2 R3-B02（`used_by` ↔ `predicates_used` 双向一致 / M5·B13 叙述）

我**自写**独立实现（不使用被审自检代码）做全量双向比较，覆盖 `transitions` + `behavior_rows` 全部条目：

```
used_by[TARGET_CONTINUES] 条目ID(11) = [B03,B04,B09,B10,B12,B14,M1,M10,M15,M8,M9]  + §12 文本白名单项
used_by[WINDOW_MATCH]     条目ID( 9) = [B07,B08,B09,B14,B17,M15,M3,M4,M9]          + §12 文本白名单项
TARGET_CONTINUES: only_forward=[] only_reverse=[]  -> 双向一致
WINDOW_MATCH:     only_forward=[] only_reverse=[]  -> 双向一致
所有权声明谓词的条目（15 个）逐个与 used_by 反向集合相等；无空列表、无未定义谓词、无幽灵条目引用
```

| 检查点 | 结果 |
|---|---|
| 全量双向一致（含 behavior_rows 与 transitions） | ✅ 无 only-forward / only-reverse |
| M1 只声明 `TARGET_CONTINUES` | ✅ `M1.predicates_used == ['TARGET_CONTINUES']` |
| M5/B13 JSON 字段现状 | ✅ `M5`、`B13` **均无** `predicates_used` 字段；`M5.global_cooldown_gate=true`；两者各有 `predicate_binding_note` |
| M5/B13 叙述与 JSON 一致 | ✅ 基本一致：`predicate_binding_policy.statement` 逐字出现在文档 §4 与 STATE；`items_without_predicates_used == ["M5","B13"]`（自检 C12 断言）。**措辞小瑕见 `N-r04-02`** |
| C12 双向断言是否弱 | ✅ **不弱**：6 个注入用例全部捕获（见 §4 f7–f11、f13-C12），含 only_forward、only_reverse、M1 过度声明、B13 加字段、未定义谓词 |

## 4. 故障注入矩阵（证明自检判别力，全部写隔离目录）

基线对照（未注入）：**exit 0 / ALL_PASS** → 证明注入框架本身不引入噪声。

| 用例 | 注入内容 | 自检 exit | 捕获检查项 | 判定 |
|---|---|---|---|---|
| f1 | §12 T6-S02 行改回“连续匹配帧数” | 1 | C12 | ✅ 捕获（R3-B01 回归可测） |
| f2 | §12 T6-L02 行改回 `t_last_match` | 1 | C12 | ✅ |
| f3 | 插入 `matched_frames`（无“废弃”） | 1 | C12 | ✅ |
| f4 | 插入规范性 `t_last_match` | 1 | C12 | ✅ |
| f5 | “废弃”距 token >60 字符 | 1 | C12 | ✅ 白名单窗不可远距离绕过 |
| f6 | “已废弃”紧邻 token | 0 | — | ✅ 白名单按设计放行 |
| f7 | `WINDOW_MATCH.used_by` 加幽灵 `B02` | 1 | C12 | ✅ only_forward 被捕获 |
| f8 | `TARGET_CONTINUES.used_by` 删 `B14` | 1 | C12 | ✅ only_reverse 被捕获 |
| f9 | `M1.predicates_used` 加 `WINDOW_MATCH` | 1 | C12 | ✅ |
| f10 | 给 `B13` 加 `predicates_used` | 1 | C12 | ✅ 叙述不实被捕获 |
| f11 | `M8.predicates_used` 加未定义谓词 | 1 | C12 | ✅ |
| f12 | 给不使用谓词的 `M2` 加**空列表** `predicates_used: []` | **0** | — | ⚠️ **未捕获**（见 `N-r04-03`；当前 JSON 无此情况，非现存缺陷） |
| f13 | 新增 `STABLE→CANDIDATE` 迁移并同步 `exit_paths` | 1 | C2,C3,C12,**C17** | ✅ C17 demote 断言有效 |
| f14 | `stable_latching.latched=false` | 1 | C17 | ✅ |
| f15 | `exit_paths` 与迁移表漂移 | 1 | C17 | ✅ |
| f16 | `T6-K01.approval_status=APPROVED` | 1 | C4 | ✅ 待批准纪律有效 |

## 5. 必须核查项 3：STABLE 锁存定论 + 我自己的状态机推演

### 5.1 规格是否给出唯一答案

- ✅ 唯一答案：**「本次获取内锁存」（`WITHIN_ACQUISITION`）**，文档 §4 段 + JSON `stable_latching` + `latched=true` + `scope=WITHIN_ACQUISITION` 三处一致；`pending_confirmation=U6-16` 明示待 G0 确认，并写明「若改则不锁存属实质语义变更」。
- ✅ **离开路径完备**：我从迁移表自算 `from ∈ {STABLE, *}` 的迁移 = `['M2','M5','M10']`，与 `stable_latching.exit_paths` 声明集合相等；`STABLE→CANDIDATE` 迁移数 = 0。
- ✅ **C17 真断言**：检查 `latched is True`、`scope == WITHIN_ACQUISITION`、`statement` 非空且被文档复述、退出路径==迁移表推导、无 `STABLE→CANDIDATE`、`not_demoted_by` 非空、`U6-16` 存在于 `open_decisions` 与文档。f13/f14/f15 三个注入全部被 C17 捕获，**不是空壳检查**。

### 5.2 我自己推演的四情形（进入 STABLE 之后）

| 情形 | 我的逐步推演（求值序 P1→P2→P3→P4→P5，逐帧首次命中即停） | 状态 | 动作 | 唯一性 |
|---|---|---|---|---|
| ① 窗口失效但 `TARGET_CONTINUES` 仍成立 | P1 M2 不成立（异常数未达阈）→ P2 M10 不成立（`TARGET_CONTINUES` 成立且 `t_last_target_continues` 新）→ P3 M5：(a) 本次获取未触发且门已开 → **M5 命中**；(b) 门未开 → H-10 抑制、无迁移；(c) 本获取已触发（经 M9 回来）→ M5 前提不成立、无迁移。M3/M4 只作用于 CANDIDATE，不适用 | 停留 `STABLE` 或 `TRIGGERED→COOLDOWN` | 仅 (a) 触发一次 | ✅ 唯一 |
| ② score 跌破 `T6-P02` | `WINDOW_MATCH` 不成立（`score ≥ P02` 是 `WINDOW_MATCH` 的必要条件），但 `TARGET_CONTINUES` **不含** `score` 条件 → M10 不成立 → **不退回 CANDIDATE**（锁存）；若几何也中断 → 低 `T6-L01` 帧或 `T6-L02` 时 → M10→LOST | `STABLE`（几何仍连续）或 `LOST` | 同上，触发与否只看 M5 前提 | ✅ 唯一 |
| ③ 抖动（连续不满足 `WINDOW_MATCH` 超过 `T6-J01`） | 抖动重置的是**窗口证据**（§9），不产生任何 `STABLE` 出边（M4 仅 CANDIDATE）；`t_last_target_continues` 仍被逐帧更新 → M10 不成立 | 停留 `STABLE` | 同上 | ✅ 唯一 |
| ④ 冷却门开启 | M5 为 P3 且在同优先级中**最先**求值（M5/M6/M8/M9/M15/M3/M4），门开后的下一条**窗口推进帧**即触发 M5→TRIGGERED→M6→COOLDOWN；M5 条件不含 `WINDOW_MATCH`，故**无需重新累积窗口证据**（与 §4 锁存段、`suppressed_trigger_release` 一致） | `TRIGGERED`→`COOLDOWN` | 恰好一次 | ✅ 唯一 |

### 5.3 与 M2/M10/M5、B13/B14、冷却全局门、B18/B21/B22/B23 的自洽性

- M2（`*`，P1）、M10（`*`，P2）确实是 STABLE 的另外两条出边，P1/P2 先于 P3 求值 → 异常/丢失优先于触发，自洽。
- `cooldown_policy.applies_to_states` 含 `STABLE`；B13 全局门 + B14 三分支只决定展示状态出口、不解除门 → 与锁存段「门未开时停留 STABLE」自洽。
- 锁存态「门开后不重新累积窗口即触发」与 B15/§10「一次获取只触发一次」不冲突（该获取确实尚未触发；M9 回来的维持态则因“本获取已触发”永不二次触发）→ 自洽。
- 非窗口推进帧不得触发：H-4（TIMEOUT/ERROR/DROPPED 不推进序列）、B18（stale 不得触发）、B21（TIMEOUT/ERROR/DROPPED **无动作**）、B22（重复幂等丢弃、不推进任何计数与状态）、B23+§13（倒序/缺帧/重启「都不得触发动作」）共同保证。**M5 条件本身未复述这一限定，见 `N-r04-01`。**

## 6. 必须核查项 4：自检加固的真实性（旧包重跑）

`verification/s6a_rerun_legacy_failures.py` 的提取实现（读源码确认，非转述）：
`git_blob()` 用 `subprocess.run(["git","-C",root,"cat-file","blob",f"{commit}:{relpath}"], capture_output=True)`
取 **binary stdout**，随后 `target.write_bytes(payload)`，SHA-256 直接对 git 字节计算
（`extraction: "git cat-file blob <commit>:<path> 的二进制输出直接 write_bytes（无文本/换行转换）"`）。
**✅ 确认未经过任何文本/换行/编码转换。**

我用真实 git 字节 + 最终版自检重跑（隔离目录），并与提交证据逐字对比：

| 旧包 | 提交 | 我的重跑 exit | 我的 FAILED | 提交证据 FAILED | 失败项一致 | 失败详情逐字一致 | 5 个文件哈希与提交证据一致 |
|---|---|---|---|---|---|---|---|
| r01 | `1fe4648` | **1** | `C2,C3,C4,C5,C6,C7,C9,C11,C12,C13,C14,C15,C16,C17`（14 项） | 同 | ✅ | ✅ | ✅ 5/5 |
| r02 | `3b59674` | **1** | `C7,C12,C13,C17`（4 项） | 同 | ✅ | ✅ | ✅ 5/5 |
| r03 | `2ce290f` | **1** | `C7,C12,C17`（3 项） | 同 | ✅ | ✅ | ✅ 5/5 |

- **r03 确实失败**，且失败原因正是上轮 R3 项：`C12`（`M1.predicates_used ['TARGET_CONTINUES','WINDOW_MATCH'] vs ['TARGET_CONTINUES']`；`TARGET_CONTINUES.used_by` 仅 used_by 有 `B03`、仅 predicates_used 有 `B14`；`WINDOW_MATCH` 同类不一致）+ `C17`（缺少 `stable_latching` 块）+ `C7`（`lost_time` 样例缺 `t_last_target_continues_ms`）→ **与提交的 `selfcheck_r03_failure.json` 逐字相同**。
- r01/r02 同理逐字相同（r01 14 项、r02 4 项）。
- r04 自身：我的完整重跑与入库 `selfcheck_result.json` **17 项状态一致、17 项 detail 逐字一致**。
- 顺带确认 `delivery_manifest.json.checks` 记录了三条真实命令与真实 `exit_code: 0`（未伪造退出码）。

## 7. 其他核验

- **上游哈希**：文档 §17 表 9 条中 8 条 MATCH；`w4/docs/stage4/s4a_stage4_g0_fields.json` 与我自算值不符（我算得 `657ea2fb…`，表内记 `3524d02a…`）——但文档 §1 **已明确披露**该工作副本漂移（“由 `3524d02a…` 变为 `657ea2fb…`”），我的实测值与该漂移声明**恰好吻合**；`upstream_bindings.json` 亦按“提交版本 + 漂移记录”登记（C8 报为“漂移（非失败，已记录）”）。→ **声明准确，非缺陷。**
- **HC-27/28/29（N02）**：29 个样例，ID `HC-01..HC-29` 无缺无重。
  - 我对全部样例做“形如 `X>=X` 自比较”探测，命中 `HC-08 '500<500'`、`HC-11 '200>200'`（**等值边界断言，合法**）、`HC-27 's02>=s02'`——逐字查看后确认 `HC-27` 的出现位置是**推导说明里描述“已不再使用”的句子**（「不再使用 (s02>=s02)/(s02+1>=s02) 自比较」），其 `expected` 由帧时刻序列（前 5 帧 40 ms、第 6 帧 `S01−1 ns`、第 7 帧 `S01+1 ns`）推导 → **N02 声称的自比较确已去除**。
  - `HC-28`/`HC-29` 为逐帧 `score`/几何序列真推导：我手算复核 `HC-28`（8 帧 IoU 0.60≥0.30 → `TARGET_CONTINUES` 8 帧；score 0.28<0.30 → `WINDOW_MATCH` 0 帧；`m3_fires=false`）✅ 与 expected 一致；`HC-29`（前 6 帧 score 0.35≥0.30 → `WINDOW_MATCH`=6，第 7–9 帧 score 0.28 → 不构成 `WINDOW_MATCH`；streak=0 → 不判 LOST；`m3_fires=true`）✅ 一致。
  - `C7.check_hand_cases` 会**拒绝** `expected` 中任何不可复算的键（`无法独立复算（禁止不可复算的预期）`），且 `recompute()` 只读 `case["recompute"]` 输入、不读 `expected` → 符合 H-7，不是自我比较。
- **参数纪律**：`r03 → r04` 24 项参数 **逐字段差异 = 0**（`kind/name_zh/unit/comparison/draft_value/draft_source/approval_status/approval_owner` 全等），非 `PENDING_APPROVAL` 项 = 0。✅
- **ID 集合无回归**：参数/迁移/不变量/行为行/事件/状态 集合**全等**；仅 `open_decisions` 新增 `U6-16`、顶层新增 `predicate_binding_policy`/`stable_latching`/`time_anchors`——**与声明的新增项完全一致，无未声明增删**。行为行 28 行、迁移 14 条、状态 7 个、顺序均相同。
- **声明文件存在性**：`delivery_manifest.json` 29 条声明全部存在且哈希相符；文档 §18 点名的运行目录文件全部存在（三个 `*_stdout.txt` 由文档的 `` `xxx.json`/`.txt` `` 简写覆盖），实际 23 个文件与文档/STATE 声明一致。**无“声明存在但缺失”。**
- **是否自称“已审查/已通过/G0 通过”**：逐条查看全部命中上下文，**未发现任何虚假完成声明**。命中项全部是**否定或免责**语境：
  - 文档「不宣称：G0 已通过；阈值已冻结；接口已集成验收…」「不代表…独立审查通过或 G0/G4/G5」
  - JSON `not_claimed`/`status_note`「不构成阶段6 G0 通过」
  - STATE「复评通过前**不得宣称** G0 通过，也不启动 S6-B」
  - `limitations`「r04 不因修订视为通过，**不得自称已审查/已通过**」
  - `coverage_matrix` 的 `DONE*` 是**运行手册条目覆盖状态**（且带 `DONE_PENDING_APPROVAL`/`DONE_WITH_BLOCKED_DEPENDENCY` 等限定），并在同文件 `not_claimed` 中声明「不代表 G0 复评通过、不代表独立审查通过」；不存在裸“S6-A DONE”之类越界声明（该字符串在 r01 曾触发 C11 失败，r04 已不含）。
- **状态**：文档 §18 末行明示「本轮**未完成独立审查**…独立审查须在后续轮次由项目总控安排」——**如实登记，未冒充审查通过**。

## 8. 非阻断问题（`CHANGES_REQUIRED` 之外的下一修订建议）

格式：`位置 | 问题 | 影响 | 依据 | 关闭条件`

### `N-r04-01`（最值得处理）M5 条件文本未复述“仅窗口推进帧”限定
- **位置**：`docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` §4 M5 行；`docs/stage6/s6a_stage6_g0_behavior_v1.json` `transitions.M5.condition`
- **问题**：`M5.condition` = 「STABLE 且本次获取尚未触发 且 全局冷却门已结束」；而 §4 锁存段与 JSON `stable_latching.suppressed_trigger_release` 都写「门开启后的下一条**窗口推进帧**即可触发」。M5 的形式化条件里没有这个“窗口推进帧”限定词，`C12.required_binding` 也不含该文本断言。
- **影响**：在“锁存 STABLE + 冷却门开启时恰逢一帧 `TIMEOUT`”这一角落序列上，M5 的字面条件与 B21「`TIMEOUT/ERROR/DROPPED` **无动作**」正面冲突；实现者若只读 M5 行，可能让异常帧触发动作（触碰阶段6 目标“异常输入不触发不当动作”）。**当前不改变结论**：B18/B21/B22/B23 与 §13「都不得触发动作」合并已能推出“只有窗口推进帧可触发”，即规范全集仍有唯一解。
- **依据**：`final_details.txt` §「M5 条件 vs stable_latching 叙述」；`json_dump.txt` M5 条目；文档 §4/§13、B18/B21/B22/B23 原文。
- **关闭条件**：把「（且本帧为窗口推进帧：`state ∈ {OK,NO_HAND}`、`stale=false`、非重复、非倒序）」补进 M5 的条件文本（文档 §4 与 JSON 同步），并在 `C12.required_binding` 或 C12 新增文本断言中固定该限定。

### `N-r04-02` `predicate_binding_policy.statement` 对 B13 措辞不够精确
- **位置**：JSON `predicate_binding_policy.statement`；文档 §4 复述行
- **问题**：statement 写「M5 与 B13 只有条件文本 + `global_cooldown_gate` 绑定，没有 `predicates_used` 字段」。实测 `M5.global_cooldown_gate=true` 而 **`B13` 并无 `global_cooldown_gate` 字段**（其抑制语义由 H-10 承载，见 `item_notes.B13` 与 `B13.predicate_binding_note`）。
- **影响**：同一句被 C12 要求逐字出现在文档与 STATE，读者可能以为 B13 也带该字段；C12 只断言「两者都无 `predicates_used`」，不会发现此措辞偏差。**不影响绑定正确性**（`used_by` ↔ `predicates_used` 已双向全等）。
- **依据**：`final_details.txt` §「B13 字段现状」。
- **关闭条件**：statement 改为例如「M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段」，同步 §4 与 STATE。

### `N-r04-03` C12 未拒绝“空列表” `predicates_used: []`
- **位置**：`verification/s6_g0_selfcheck.py` `check_predicates()`（全量双向段）
- **问题**：策略规定「不使用谓词的条目不得出现 `predicates_used` 字段」，但检查只对 `M5`/`B13` 显式断言字段缺失；其它条目若写成 `predicates_used: []`，既不入 `reverse` 也不被拒。注入用例 f12（给 `M2` 加 `[]`）**exit 0 / ALL_PASS**。
- **影响**：当前 JSON **无任何空列表**（我已全量扫描），故**非现存缺陷**；仅未来可能出现“形式上声明了字段”的模糊写法而检查放过。
- **依据**：`fault_injection.txt` f12；`my_bidir.txt` §2「结构异常扫描」为空。
- **关闭条件**：C12 增加「任何条目 `predicates_used` 不得为空列表；不使用谓词的条目不得出现该字段」的普适断言（而非仅 M5/B13）。

### `N-r04-04` C7 `window_match_vs_continues` 的窗口时长口径与规格 §9 不一致
- **位置**：`verification/s6_g0_selfcheck.py` `recompute()` 第 ~760 行 `window_span_ms = (len(frames) - 1) * period_ms`；`hand_computed_cases.json` HC-29 `derivation`
- **问题**：规格 §9 定义窗口完成时刻为「第 `T6-S02` 个 `WINDOW_MATCH` 结果到达且时长条件同时满足的那一帧」，窗口时长应自**窗口首帧**算到**该完成帧**；实现在意的是**整个输入序列**的跨度。HC-29 序列 9 帧 × 40 ms，实现得 span = 8×40 = **320 ms**（推导文字也写「span=8×40=320 ms」），而第 6 个 `WINDOW_MATCH` 帧处的真实窗口时长 = 5×40 = **200 ms**。
- **影响**：HC-28/HC-29 两种口径下 `m3_fires` 同为 `true`/`false`，**结论未受影响，29 样例复算仍全部成立**；但该公式偏松，若后续加入“周期更小、序列更长”的样例（如周期 10 ms、序列 21 帧），可能把「窗口时长不足」误判为满足而放过错误预期；HC-29 推导文字给出的 320 ms 与 §9 定义不对应。
- **依据**：`final_details.txt` §「C7 span 语义 vs 规格 §9」；`s6_g0_selfcheck.py:760`；`hand_computed_cases.json` HC-29。
- **关闭条件**：把 span 改为「窗口首帧 → 第 `T6-S02` 个 `WINDOW_MATCH` 帧（且时长条件同时满足的那一帧）」的跨度，并修正 HC-29 推导文字；或为该偏松口径在 `limitations` 中显式声明并说明仅适用于当前样例参数。

### `N-r04-05`（范围观察）工作树内未跟踪的 S6-B WIP 草稿
- **位置**：`docs/stage6/s6b_frozen_interface_v1.json`、`src/stage6/s6_core.py`（1321 行）、`src/stage6/s6_params.py`（296 行）
- **问题**：三者均为**未跟踪**（`git status --short` 显示 `??`，`git log --` 无任何提交），文件自述 `status: WIP_NOT_FOR_COMMIT`，STATE 亦声明「S6-B WIP，不提交、不作为证据，复评通过后须按 v1.3 语义返工（尤其 STABLE 锁存与 `WINDOW_MATCH` 计数）」。另 `s6_core.py` 文档串引用了 `docs/stage6/S6B_stage6_state_machine_design_v1.md`，该文件**不存在**。
- **影响**：**不影响 r04 判定**（不属被审提交；文档 §18「本轮未实现状态机…6-B `NOT_RUN`」指被审修订的事实，且 WIP 已自述排除）。风险仅在后续误把这些草稿当 S6-B 进展或实现依据。
- **依据**：`final_details.txt` §「结尾状态」；文件头 `WIP` 声明；STATE 第 34 行。
- **关闭条件**：无需为 r04 关闭；建议 S6-B 立项时统一处置（删除或纳入新 RunId 并按其语义返工），且不得作为 S6-B 已完成证据。

## 9. 我未做的事（限制，如实登记）

- 未修改任何被审文件；未在 `w6` 内创建 `tmp/6/**`（我复刻了旧包重跑逻辑而不直接运行该脚本以保持写隔离）。
- 未创建/未参与任何状态机实现，未上板，未接触摄像头/HDMI/JTAG/hw_server（H-9 与我自身边界一致）。
- 未复核 r01/r02/r03 各自证据目录**全部**文件的语义（只按 C11/清单与本次重跑所需范围核对），未复核 S6-B/6-C/6-D/6-E。
- 未运行需要审批或越权的操作；本会话为受限子代理，无法扩权，也不需要。
- 上一轮评审明细（`REVIEW_r03.md` 仅 8 行、且该目录下无 `review_result.json`）无法从磁盘复核，故未验证历史轮次结论的正确性，只将其作为待证伪断言。

---

## 附：本轮证据文件（均在隔离评审目录）

`my_selfcheck_r04.json`（我的完整重跑）、`my_selfcheck_r04_stdout.txt`、`my_selfcheck_r04_summary.txt`、
`my_check_inputs.txt` / `my_check_evidence.txt`（交付检查真实输出）、`my_bidir.txt`（自写全量双向+文本级审计）、
`r03_vs_r04.txt`（参数/ID/文档逐项差异）、`fault_injection.txt` + `faultinj/`（16 注入用例全部产物）、
`legacy_rerun.txt` + `legacy_rerun/`（r01/r02/r03 重跑与哈希）、`upstream_and_cases.txt`、
`claims_and_files.txt`、`claim_contexts.txt`、`final_details.txt`、`json_dump.txt`、`hash_artifacts.py` 输出，
以及上述全部自写脚本（`*.py`）。