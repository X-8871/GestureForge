# S6-A r05 独立复评报告（第 5 轮 · 独立 Reviewer）

- **审查对象**：工作树 `D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，**被审提交 `1632761`**
  （`1632761b2d60d8c1328aa82be97d53eef30e1072`，提交信息 `fix(stage6): S6-A v1.4/r05 closes 4th-review non-blocking items N-r04-01..05`）
- **基线**：r04=`b20b670`（`b20b6705e8c7dd6c43cc2195860e3fc84e1c4ec7`，上轮 `PASS`）；更早 r03=`2ce290f`、r02=`3b59674`、r01=`1fe4648`
- **契约版本**：r04=v1.3 → r05 自称 v1.4
- **审查时间**：2026-10-23 02:10 起（UTC+8）
- **写入范围**：仅 `D:\FPGA_Competition\tmp\review\S6A_r05_20261023_r01\`（自建）。**未写入、未修改被审工作树任何文件**；
  未直接运行 `verification/s6a_r05_probe.py` 与 `verification/s6a_rerun_legacy_failures.py`（两者会向被审证据目录与 `tmp/6/**` 落盘），
  改为在隔离目录**复刻其提取/注入逻辑**运行（见 §5/§6.4）。收尾核验：`git status --porcelain` 中 tracked 修改 = 0；被审 20 个文件评审始末哈希一致。
- **独立性声明**：本轮与第 1–4 轮评审者无关联。上轮 `REVIEW_r04.md`（`PASS` + 5 项非阻断）仅作为**待证伪的断言**使用；
  全部结论由本轮自写脚本、自推状态机序列、自造注入/演示用例得出。**未照抄历史结论。**

## 结论

# `PASS`

- **阻断问题：0 项**（`CHANGES_REQUIRED` 之外无阻断）。
- **上一轮 5 项非阻断（`N-r04-01` … `N-r04-05`）：5/5 实质关闭**，逐项证据见 §3。
- **本轮新增非阻断 4 项**（`N-r05-01` … `N-r05-04`）+ 7 条观察（§7/§8）。均不影响本包任何结论、关闭判定或版本一致性。
- **结论边界**：本结论只覆盖 **r05 的 S6-A G0 包**（规格 + 行为表 JSON v1.4 + 自检/构建器/探针 + r05 证据目录 35 文件），
  **不代表 G0/G2/G4/G5**，不涉及 S6-B/6-C/6-D/6-E、状态机实现、摄像头、HDMI、板卡、hw_server。
  自检 `ALL_PASS` 与检查器 `CHECKS_OK` 只表示规格一致性/算术/证据存在性/清单绑定复算通过。

---

## 1. 我实际执行的命令与真实退出码

所有命令工作目录 `D:\codex-worktrees\w6`；`--project-root` 一律用绝对路径 `D:/codex-worktrees/w6`；
所有输出（`--out`、注入副本、演示产物）落在隔离评审目录。

| # | 命令（要点） | 真实退出码 | 结果 |
|---|---|---|---|
| 1 | `python -B verification/s6_g0_selfcheck.py --json docs/…v1.json --doc docs/…v1.md --cases …/r05/hand_computed_cases.json --upstream …/r05/upstream_bindings.json --out <隔离>/my_selfcheck_r05.json --project-root D:/codex-worktrees/w6 --evidence-dir …/r05 --manifest …/r05/delivery_manifest.json --state .codex/STATE.md` | **0** | `ALL_PASS`，**17/17 PASS，errors=0** |
| 2 | `python -B verification/check_stage_delivery.py --mode inputs --manifest …/r05/inputs_manifest.json` | **0** | `CHECKS_OK`；与入库 `check_inputs_mode_output.txt` **逐字节相同** |
| 3 | `python -B verification/check_stage_delivery.py --mode evidence --manifest …/r05/delivery_manifest.json` | **0** | `CHECKS_OK`；与入库 `check_evidence_mode_output.txt` **逐字节相同** |
| 4 | 自写 `my_checks.py`（全量比对：自检结果、哈希清单、manifest 双向、参数/ID 逐字段、M5/latch/policy、声明纪律） | 1（**仅末行 print 触发 GBK 控制台编码错误**，结果文件已写出；核验本身无失败） | 见 §2–§8 |
| 5 | 自写 `my_legacy.py`（`git cat-file blob` 二进制提取 b20b670 的 5 文件 → 用 r05 自检重跑） | 0（脚本）；其中**被演示自检 = 1** | FAILED=`['C7','C12']`，与入库 `selfcheck_r04_failure.json` **逐字相同** |
| 6 | 自写 `my_probe.py`（复刻探针 7 个注入 + 基线，另加我自造 10 例） | 1（**仅因我自造的 X10 与我的预期不符**，见 §6.4/O6；17/18 AS_EXPECTED） | 见 §6.4 |
| 7 | 自写 `demo_span_later_of.py`（§9/§15「取较晚」演示） | 0（脚本）；**被演示自检 = 1** | `C7: HC-29.m3_fires 预期 True 与复算 False 不符`（§7 `N-r05-04`） |
| 8 | 自写 `my_checks3.py` / `my_extract.py` / `my_details.py`（diff 删除行清点、记录类文件、§18 文件存在性、计数核对） | 0 | 见 §5/§7/§8 |
| 9 | 自写 `my_bytes_check.py`（42 个被改动文件 worktree vs `git cat-file blob 1632761:` 逐字节/归一化比较） | 1（同为末行 print 编码问题） | **内容真正不同 = 无**（仅 CRLF↔LF，git 归一化相同） |
| 10 | 自写 `compare_probe.py`（我的 8 个探针用例 vs 入库 `probe_summary.json` 逐字段） | 0 | **8/8 逐字段完全一致** |

## 2. 自算哈希（SHA-256，我自己对文件字节计算）

被审源码/规格/状态/关键证据（**工作区 CRLF 字节**，即证据所绑定的口径）：

| 文件 | 我的 SHA-256 |
|---|---|
| `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md` | `01154560fbe8597fc269db7185ad303b0f407899fb828fb3bba270c40b011572` |
| `docs/stage6/s6a_stage6_g0_behavior_v1.json` | `fe28145f13108034d09b0aa19f1051fcdf69ff959dd5200bfd7c597124119b93` |
| `verification/s6_g0_selfcheck.py` | `8287265570e1ecbe6f11e1fa21bc0dd0b6d1a4a0e7f494a740fbf23a980b3160` |
| `verification/s6a_build_evidence.py` | `f09b19970581d8b4f5986a91c75961db7f61e4f087fb199b6e0668f2b84d229f` |
| `verification/s6a_r05_probe.py` | `3aa02b83775383e949a35479aefb1fdbb846567caab7deaee6f211b814f571d6` |
| `verification/s6a_rerun_legacy_failures.py` | `afd7cf83447432a585842b7945951d7509d64cfaf0e1b63f36ce6909c55eb968` |
| `.codex/STATE.md` | `b0a888e4ca972e68307da723c4141dd57b3ea8d5b35c963ff7fb50eb105a690d` |
| `…/r05/hand_computed_cases.json` | `2a81adfc8236caff11cf6a3c1e08fe60cec137d3710f86e813aec9deb258b63e` |
| `…/r05/delivery_manifest.json` | `092f8387ff4641f63c551cd1be310b15408d5e96845cc48564a08295da75d078` |
| `…/r05/selfcheck_result.json` | `69afe2830718247da44d2c6c3f84d699d52af78a18120815cea00dd1a46c5048` |
| `…/r05/probe_summary.json` | `2473a17f5f36db123318ca89f406167cf3447f44e02d51f3704f753dda05c4b2` |
| `…/r05/selfcheck_r04_failure.json` | `488d9aa71e24e8a183aaca7adbaff0c34f0dff47021cdafc4d2683b0bed7722e` |
| `…/r05/r04_package_under_test.json` | `7ef4904c80234dfa0041a4b0a8889cbce8f4fb295daab78215e625d58f086601` |

- 我自算的 `behavior_json_sha256` / `human_doc_sha256` / `hand_cases_sha256` 与入库 `selfcheck_result.json.inputs` **三项全等**。
- 运行目录实际 **35 个文件**；`hashes_sha256.txt` 解析 **33 条**，**声明缺失 0、哈希不符 0**（按设计不含 `delivery_manifest.json` 与自身）。
- `delivery_manifest.json` 声明 **41 条**（运行目录 34 + 外部绑定 7）：**缺失 0、哈希不符 0、未声明但存在 0、声明但缺失 0**。
- **字节口径说明（观察 O1）**：工作区文件为 CRLF、`git cat-file blob 1632761:…` 为 LF（`core.autocrlf=true`，`docs/stage6/**` 与 `report/evidence/S6-A/**` 未在 `.gitattributes` 标 `-text`）；
  我逐文件核了被审提交的 **42/42** 个改动文件，**内容真正不同者 0**（仅换行差异，git 归一化后完全相等）。与 r04 口径一致（r04 入库 hash 亦等于其 git 字节的 CRLF 重建值），**非本轮回归**。

## 3. 必须核查项 1：上一轮 5 项非阻断的关闭核对

| 项 | 关闭条件（r04 报告） | 我的核验方式与实测 | 判定 |
|---|---|---|---|
| `N-r04-01` | M5 条件文本（文档 §4 + JSON 同步）补「本帧为窗口推进帧（`state∈{OK,NO_HAND}`、`stale=false`、非重复、非倒序）」，并与 `stable_latching.suppressed_trigger_release` 一致；在 C12 固定该限定 | JSON `M5.condition` 末段=`（且本帧必须为窗口推进帧：state ∈ {OK,NO_HAND}、stale=false、非重复、非倒序）`，另新增 `M5.window_advance_required`；文档 §4 M5 行同义（含 `state ∈ {OK, NO_HAND}`）；`stable_latching.suppressed_trigger_release` 增「若门恰在异常/重复/倒序/过期/缺帧帧开启，该帧不得触发…必须等到下一条窗口推进帧」；**C12 三处断言**（JSON 5 个 marker、文档 §4 M5 行 5 个 marker、release「窗口推进帧+不得触发」）**我逐一注入验证均 FAIL**（§6.4 probe+mine） | ✅ 关闭 |
| `N-r04-02` | `predicate_binding_policy.statement` 改为「M5 带 `global_cooldown_gate` 标记、B13 由 H-10 承载；两者均无 `predicates_used`」，与 JSON 实际字段一致，文档 §4 与 STATE 同步 | statement=`M5 带 \`global_cooldown_gate\` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 \`predicates_used\` 字段。`；实测 `M5.global_cooldown_gate=true`、`M5` 无 `predicates_used`；`B13` **无** `global_cooldown_gate` 字段、**无** `predicates_used`（与 statement 相符）；statement 逐字出现在文档 §4 与 `.codex/STATE.md`（我字符串包含判定=True）；C12 断言 `global_cooldown_gate`/`H-10`/`predicates_used` 三要素（我 X9 注入旧措辞 → C12 FAIL） | ✅ 关闭 |
| `N-r04-03` | C12 普适拒绝显式空列表/非列表 `predicates_used`（不只 M5/B13） | 代码为 `if not isinstance(declared, list) or not declared: issues.append(...)`，作用于 `transitions + behavior_rows` 全量；**我自注入 3 例**：`M2=[]`（C12 FAIL）、`M6=[]`（C12 FAIL）、`M6="TARGET_CONTINUES"` 字符串（C12 FAIL），detail 均为「必须是非空列表（显式空列表/非列表均不合法，N-r04-03）」；另 JSON 新增 `empty_list_rule` 记录该规则 | ✅ 关闭 |
| `N-r04-04` | C7 `window_span_ms` 改为「窗口首帧 → 第 `T6-S02` 个 `WINDOW_MATCH` 帧」跨度（HC-29=200 ms=5×40） | 代码 `window_indices[s02-1] - window_indices[0]` × `period_ms`（用 `T6-S02`，非硬编码 6）；HC-29 `expected.window_span_ms=200.0`，推导文字同步改写为 200 ms 并保留宽松口径 320 ms 作对照；HC-28 严格口径 0 ms；**两口径 `m3_fires` 一致**（HC-28 false/false、HC-29 true/true），并由 `span_conventions_agree` 真断言（我 X6 注入 `s01=250` 使两口径分歧 → C7 FAIL）。**残留口径差异见 `N-r05-04`（非阻断）** | ✅ 关闭（附 `N-r05-04`） |
| `N-r04-05` | `src/stage6/s6_core.py` 不再引用不存在的设计文档（只核对引用是否已改；WIP 不在被审提交内） | `s6_core.py` 现存 `docs/stage6/*` 引用仅为 `S6A_stage6_g0_behavior_spec_v1.md` 与 `s6a_stage6_g0_behavior_v1.json`，**两者均存在**；`S6B_stage6_state_machine_design_v1.md` 引用已消失；`s6_params.py` 引用 `s6b_frozen_interface_v1.json`（存在）；三者为未跟踪 WIP，`git diff --name-only b20b670 1632761` **不含** `src/stage6/**` | ✅ 关闭（引用层面） |

### 3.1 我自行推演的 HC-30 核心场景（锁存 STABLE + 门恰在 TIMEOUT 帧开启）

**我的独立推演**（不读 HC-30 的 `expected`，仅按 M5 + 限定词、H-4、B18/B21/B22/B23、§13、H-10、§10 ONCE_PER_ACQUISITION）：

- 门条件 `t_now − t_last_submit ≥ T6-K01`：`t_last_submit=0 ms`、`K01=1000 ms`、`P=100 ms` → `t_now ≥ 1000 ms` → **门在第 11 帧开启**（两场景相同）。
- 场景 A（第 11 帧 `TIMEOUT`）：H-4/§9 规定 `TIMEOUT` 不推进窗口序列且 `B21` 规定 `TIMEOUT/ERROR/DROPPED` **无动作** → 第 11 帧不是窗口推进帧，M5 不成立、**无动作**；第 12 帧（`OK`，t=1100 ms）是窗口推进帧且 `M2` 不成立（近 3 帧异常数 1 < `U00_N`=3）→ **M5 命中，动作帧=12**。
- 场景 B（第 11 帧 `OK`）：门开启的同一条窗口推进帧即可触发 → **动作帧=11**。
- 两场景**全程各恰好 1 次**动作（本获取尚未触发，首发即计 1；`B15`/§10 禁止本获取二次触发）。
- ⇒ 押中 HC-30 `expected` 全部七个键：`gate_open_frame{11,11}`、`first_action_frame{12,11}`、`total_actions{1,1}`、`action_at_gate_open_frame{false,true}` 及三个 `true`。**规格对本角落序列给出唯一答案，且与用例一致。**

## 4. 必须核查项 2：自检工具改动的正确性（`s6_g0_selfcheck.py` diff r04→r05）

### 4.1 无削弱（机械清点）

`git diff -U0 b20b670 1632761 -- verification/s6_g0_selfcheck.py`：**新增 105 行、删除 8 行**。8 个被删除行**全部**为被更强形式替换：

| 被删除行 | 替换物 | 强弱判定 |
|---|---|---|
| 模块 docstring 版本行（v1.3→v1.4） | 同义更新 | 中性 |
| C7 docstring 行「新增可复算类型；HC-16/17/20 不再重述结论」 | 扩写为 30 例 + 跨度口径 + 角落序列 | 增强 |
| C12 docstring 行「M5/B13 无 predicates_used…」 | 追加 M5 限定与非空列表要求 | 增强 |
| `allowed_versions = (…"v1.3")` | 追加 `"v1.4"`（历史白名单，见 O6） | 中性（必要） |
| `window_span_ms = (len(frames)-1)*period_ms` | 「窗口首帧→第 T6-S02 个 WINDOW_MATCH 帧」+ 宽松口径对照 | 增强（严格收紧，见 §7 `N-r05-04`） |
| `if len(seen) < 29:` / `raise …不足 29` | `< 30` / `不足 30` | 增强 |
| C7 返回文案 | 追加 HC-30 说明 | 中性 |

- **被删除行中唯一的断言逻辑是 29→30 阈值行，且被替换为更严的 30。** 无任何 `raise`/`issues.append`/判定条件被删而未被更强形式取代。
- `run_checks()` 的检查项集合仍为 **C1…C17（17 项）**，未增删检查项、未降级任何检查（无 `except`、无提前 `return`、无 try 包裹）。
- ✅ **结论：只增强，未削弱既有检查。**

### 4.2 新增断言的真实性（我自跑，记录真实退出码）

`verification/s6a_r05_probe.py` 共 **8 条 `INJECTIONS`，其中注入（`target≠None`）**7** 条** + 基线 1 条。
我用**同一最终版自检**复刻全部 7 条注入（连同基线）并另加 10 条自造注入，落盘隔离目录：

| 用例 | 注入 | 自检 exit | 捕获项 | 关键 detail（截断） |
|---|---|---|---|---|
| baseline | 无 | **0** | — | `ALL_PASS` |
| m5_window_advance_removed | 删 JSON M5 限定段 | **1** | C12 | M5 条件未复述 5 个 marker |
| empty_predicates_used | `M2=[]` | **1** | C12 | 必须是非空列表…`[]` |
| b13_predicates_used_added | `B13=['TARGET_CONTINUES']` | **1** | C12 | 非双向一致 + B13 实际没有该字段 |
| undeclared_predicate_name | `M8=['TARGET_LOST']` | **1** | C12 | 与要求不符 + 未定义谓词 |
| suppressed_release_not_window_advancing | release 去掉「窗口推进帧」 | **1** | C12 | release 未复述「窗口推进帧」 |
| case_timeout_frame_action | HC-30 门开启帧改为有动作 | **1** | C7 | `action_at_gate_open_frame` 预期 True 与复算 False 不符 |
| case_span_wrong | HC-29 期望跨度改 320 | **1** | C7 | `HC-29.window_span_ms 预期 320.0 与复算 200.0 不符` |
| **X1**（我加） | 删**文档 §4 M5 行**限定 | **1** | C12 | 文档 §4 M5 行未复述 5 个 marker |
| **X2**（我加） | 仅删 JSON M5 的「非倒序」 | **1** | C12 | 仅 `'非倒序'` 一项未复述 |
| **X3**（我加） | `M6="TARGET_CONTINUES"`（字符串） | **1** | C12 | 非空列表断言捕获非列表 |
| **X4**（我加） | `M6=[]` | **1** | C12 | 非空列表断言 |
| **X5/X6**（我加） | HC-29 期望 150 / `s01=250` | **1**/**1** | C7 | `window_span_ms` / `m3_fires` 不符 |
| **X7/X8**（我加） | HC-30 `total_actions=2` / 第 12 帧改 TIMEOUT | **1**/**1** | C7 | `total_actions` / `first_action_frame`（12 vs None）不符 |
| **X9**（我加） | statement 回退旧措辞 | **1** | C12 | 缺 `global_cooldown_gate`/`H-10` + 文档未复述 |
| **X10**（我加） | 版本回退 v1.3+r04 | **0** | — | 见 §8 `O6`（自检既有白名单设计，非削弱；我的预期错误） |

- **8 个探针用例与入库 `probe_summary.json` 逐字段完全一致**（`expected_exit`/`actual_exit`/`expected_check`/`failed_checks`/`captured`/`verdict`）。
- ✅ 探针的 7 条注入**都真能 FAIL 且由预期检查项（C12/C7）捕获**；基线**真实 exit 0**。

## 5. 必须核查项 3：自检复跑 / 交付检查 / 旧包重跑

1. **r05 全量自检复跑**（绝对 `--project-root` + `--evidence-dir/--manifest/--state`）：**exit 0 / ALL_PASS**；
   与入库 `selfcheck_result.json` **17 项 id+status+detail 逐字一致（差异数 0）**，`inputs` 四项哈希/路径一致，`id_inventory` 相等。
   入库 C11 detail：`实际文件 35 个；manifest 双向一致（运行目录 34 个文件 + 外部绑定 7 个文件哈希复算通过）；STATE 声明 35 个文件与 2 个目录全部存在`；C17 detail：`退出路径 ['M10','M2','M5']，无 STABLE→CANDIDATE 迁移，U6-16 待确认`。
2. **`check_stage_delivery --mode inputs/--mode evidence`**：均 **exit 0 / CHECKS_OK**，输出与入库 `*_mode_output.txt` **逐字节相同**。
3. **r04 原始字节重跑**（我用 `git cat-file blob b20b670:<path>` 二进制提取 5 文件 → r05 自检）：**exit 1**，
   `FAILED=['C7','C12']`，**失败的 id、顺序与 detail 字符串与入库 `selfcheck_r04_failure.json` 完全逐字相同**（17 项 id/status 亦全同）：
   - `C7: 手算样例数量不足 30：29`
   - `C12: predicate_binding_policy.statement 缺少事实要素 'H-10'（N-r04-02）；M5 条件未复述…×5；文档 §4 M5 行未复述…×5；stable_latching.suppressed_trigger_release 未复述…'不得触发'（N-r04-01）`
   - 我自算的 5 个 git 字节哈希与入库 `r04_package_under_test.json` **5/5 一致**（json `119f21a7…`、doc `13262360…`、cases `c90d746b…`、bindings `141b85f7…`、STATE `76346fbc…`）。
   - ⚠️ **归因偏差见 §7 `N-r05-02`**：C7 在 r04 字节上的失败原因是「29<30（缺 HC-30，属 N-r04-01 的新用例）」，**不是** N-r04-04 的跨度口径（r04 的 `HC-29.expected` 根本没有 `window_span_ms` 键）。
4. 探针/构建器落盘 stdout 真实性：8 个 `probe_*_stdout.txt` 均为真实自检 stdout（基线为 `ALL_PASS`，其余为对应 `FAILED` + detail），与我的复刻一致。

## 6. 必须核查项 4：无回归与无夸大

| 检查点 | 我的实测 | 判定 |
|---|---|---|
| 24 项参数值 | r04(b20b670) vs r05(1632761) 逐字段比较：**差异数 0**（`kind/name_zh/unit/comparison/draft_value/draft_source/approval_status/approval_owner` 全等），数量 24→24 | ✅ |
| `PENDING_APPROVAL` | r05 非 PENDING_APPROVAL 参数 = **0**；参数集全等 | ✅ |
| ID 集合 | `transitions` 14→14、`hard_invariants` 10→10、`behavior_rows` 28→28、`open_decisions` 16→16、`parameters` 24→24、`states` 7→7：**新增=[] 删除=[]**（无 ID 增删，故无"未声明新增"） | ✅ |
| 声明的新增（非 ID 键） | 顶层键无增删；新增键仅 `transitions.M5.window_advance_required`、`stable_latching.window_advance_required`、`predicate_binding_policy.empty_list_rule`、`revision.retained_from_r04`（替代 `retained_from_r03`），均落在声明的 5 项修复内（`empty_list_rule` 在 `fix_record.json` 明写），簿记字段（`artifact_version`/`run_id`/`baseline.revision_base_commit`/`supersedes_run_id`/`not_claimed`）随修订滚动 | ✅ |
| `artifact_version` 一致性 | JSON=`S6A-G0-v1.4`；文档 v1.4 修订记录 + §18 证据行（2 处 "v1.4"）；证据：`fix_record.json` 2、`coverage_matrix.json` 3、`limitations_not_executed.json` 3、`S6A_run_summary.md` 1；STATE 亦记 v1.4/r05 | ✅（观察 O2/O3） |
| 声明文件存在性 | manifest 41/41 存在且哈希相符；STATE 声明 35 文件 + 2 目录全部存在（C11 PASS）；文档 §18 点名 31 个文件名**全部存在**（4 个 `*_failure_stdout.txt` 以 `` `xxx.json`/`.txt` `` 简写覆盖） | ✅ 无缺失 |
| r01..r04 证据未被触碰 | `git diff --name-only b20b670 1632761 -- report/evidence/S6-A/s6a_g0_20261022_r0{1,2,3,4}` = **空**（四个目录均无改动） | ✅ |
| 是否自称「已审查/已通过/G0 通过」 | 逐条查看全部命中上下文：**未发现虚假完成声明**。命中均为否定语境（「不宣称：G0 已通过」「不代表…独立审查通过或 G0/G4/G5」「不得自称已审查/已通过」「本记录不构成已审查/已通过」）或**经核实为真的历史引用**（见 O5） | ✅ |
| 状态口径 | 文档 §18 明示「本轮**未完成独立审查**…独立审查须在后续轮次由项目总控安排」；JSON `review_status=PENDING_REVIEW`、`status=G0_PACKET_PENDING_APPROVAL`；fix_record/limitations/run_summary 均记 `PENDING_REVIEW`/`DELIVERED_PENDING_REVIEW` | ✅ 如实登记 |
| 与 r04 的证据绑定口径 | r04 入库 hash（json `c6c11ed3…`、doc `f33e9a72…`）经我重建 = 其 git 字节的 CRLF 形式；r05 同口径 | ✅ 无回归 |

## 7. 本轮新增非阻断问题（格式：`位置 | 问题 | 影响 | 依据 | 关闭条件`）

### `N-r05-01` 探针用例计数表述夸大 1（"8 个注入" 实为 7）
- **位置**：`verification/s6a_r05_probe.py` 模块 docstring；`verification/s6a_build_evidence.py`（docstring、`keep_reason_for`、summary 行 3 处）；`…/r05/fix_record.json` `revision_discipline.self_check_before_after`；`…/r05/S6A_run_summary.md` 两行；`…/r05/delivery_manifest.json` `keep_reason`；提交信息（`injects 8 faults`）。
- **问题**：`INJECTIONS` 共 8 条，其中真正改动输入的注入只有 **7** 条（第 1 条 `baseline_no_injection` 不改坏任何输入）。而各处写作「8 个注入用例」「**基线 + 8** 个注入用例 / 基线 + 8 用例」（后者等于 9 个用例），与实物 8 条用例（基线 + 7 注入）不符。
- **影响**：仅自述计数不实；不改变任何结论——7 条注入的真实退出码、被捕获检查项与探针落盘 stdout 我都已逐条复现为真。
- **依据**：我自算 `INJECTIONS` 条目=8 / `target≠None`=7；入库 `probe_summary.json.results`=8；`probe_*_stdout.txt`=8（`my_details.txt`、`compare_probe.py`）。
- **关闭条件**：统一改为「基线 1 例 + 注入 7 例（探针共 8 例）」，同步 probe docstring、构建器 3 处、`fix_record`、`run_summary`、`delivery_manifest.keep_reason`。

### `N-r05-02` r04 重跑失败证据的归因不准（把 N-r04-04 说成由 C7 在 r04 字节上捕获）
- **位置**：提交信息（`C7 catches N-r04-04`）；`verification/s6a_rerun_legacy_failures.py` `LEGACY["r04"].purpose`（「与 N-r04-04（样例数不足 30 / 缺 HC-30 与窗口跨度断言）」）；`…/r05/S6A_run_summary.md` 证据行（「C7 捕获 N-r04-04」）；`…/r05/fix_record.json` `self_check_before_after`。
- **问题**：实测 r05 自检在 r04 字节上 C7 的**唯一**失败是「手算样例数量不足 30：29」，成因是 **缺 HC-30（N-r04-01 新增的用例）**；r04 的 `HC-29.expected` 键仅为 `continues_false_streak/lost/m3_fires/trigger`，**不含 `window_span_ms`**，故 N-r04-04 的跨度口径在 r04 字节上不可测——真正证明其判别力的是探针 `case_span_wrong`。
- **影响**：描述性归因偏差，不影响本包任何结论或关闭判定（探针证据真实，我已复现）。
- **依据**：`my_legacy.txt`（我独立提取 git 字节重跑：exit 1、`FAILED=['C7','C12']`、detail 与入库逐字相同；r04 样例 29、无 HC-30、HC-29.expected 无 `window_span_ms`）；`my_probe.txt` 的 `case_span_wrong`（exit 1，C7 `HC-29.window_span_ms 预期 320.0 与复算 200.0 不符`）。
- **关闭条件**：把 r04 重跑证据的归因改为「C7 捕获样例数 29<30（缺 N-r04-01 新增的 HC-30），C12 捕获 N-r04-01/N-r04-02」；N-r04-04 的判别力只引用探针 `case_span_wrong`。

### `N-r05-03` HC-30 的部分断言键为常量、`total_actions` 结构上封顶
- **位置**：`verification/s6_g0_selfcheck.py` `recompute(kind="latched_stable_gate_on_timeout")`（≈L825-869）返回的 `no_action_on_timeout_frame` / `timeout_frames_not_window_advancing` / `latched_within_acquisition`（**恒 True，不依赖输入**）；`total_actions` 由 `acted` 标志封顶为 1。
- **问题**：三个布尔键恒真、无判别力；`total_actions` 结构上不可能 >1，故「全程恰好 1 次」实为「至少 1 次」；用例在动作帧后即结束，未建模动作后的二次触发抑制。
- **影响**：不改变结论。HC-30 的真实判别力由 `gate_open_frame`/`first_action_frame`/`action_at_gate_open_frame` 三个计算键承载（我以 X7/X8 注入证明可捕获）；但读者可能误以为 `ONCE_PER_ACQUISITION` 已由该用例覆盖（实际由 `trigger_once_hold`/B15 覆盖）。
- **依据**：源码 L825-869；`my_probe.txt` X7（`total_actions` 2 vs 1 → C7 FAIL）、X8（第 12 帧改 TIMEOUT → `first_action_frame` 12 vs None → C7 FAIL）。
- **关闭条件**：在 HC-30 推导文字或自检 `limitations` 中注明该用例只覆盖「门开启帧非窗口推进帧则不动作、下一条窗口推进帧动作」；或让 `total_actions` 不封顶并延长场景到动作帧之后。

### `N-r05-04` C7 的 `m3_fires`/`window_span_ms` 只取第 `T6-S02` 个 `WINDOW_MATCH` 帧的跨度，未实现 M3/§9/§14 `T6-S03` 的「取较晚满足者」
- **位置**：`verification/s6_g0_selfcheck.py` `recompute()` ≈L763-781（`window_span_ms` 与 `m3_fires`）。
- **问题**：实现把**第 `T6-S02` 个 `WINDOW_MATCH` 帧**当作窗口结束帧，并要求**该帧**跨度 ≥ `T6-S01`；而 §9 窗口条件、§14 `T6-S03`（`later_of`）与 M3 都规定「同时满足帧数与时长，**取较晚**满足者」。当 `P < T6-S01/(T6-S02−1)`（草案值下 = 40 ms，例如 30 fps 的 33.3 ms）时**计数先于时长满足**，实现会报 `m3_fires=false`，而规格要求完成帧在更后面、`m3_fires=true`。
- **影响**：**当前 30 个样例（P=40 ms、S01=200 ms）两口径恰好重合**，17 项 ALL_PASS 与 29/30 例复算全部成立；该改动相对 r04 是**严格收紧**（`m3_fires_r05 ⊆ m3_fires_r04`），**不会**把既往 FAIL 洗成 PASS。风险在后续：若 G0 批准 `P_meas < 40 ms` 或新增该参数区间样例，自检会对符合 §9/§15 的预期误报 FAIL（"预期不可复算"）；S6-B 若照此口径实现，30 fps 下会漏判 STABLE。**故判为非阻断。**
- **依据**：源码 L763-781；文档 §9「按 `T6-S03` 语义取**较晚**满足者」、§14 `T6-S03 | later_of | 同时满足帧数与时长，取较晚满足者`、§4 M3 行、**§15 表格「30 | 33.3 ms | 166.7 ms | 200 ms（下界）| 时长 | 第 8 帧 233.1 ms」**；我构造 `P=33.3 ms`、8 个连续 `WINDOW_MATCH` 帧、按 §9/§15 预期 `m3_fires=true`（第 8 帧 233.1 ms 完成）→ r05 自检 **exit 1**：`C7: HC-29.m3_fires 预期 True 与复算 False 不符`（`inject/Y1_demo.txt`、`inject/Y1_hc29_33fps_cases.json`）。
- **关闭条件**：窗口完成帧改为「第一个满足 (帧序−窗口首帧)·P ≥ `T6-S01` 且计数已 ≥ `T6-S02` 的帧」，`window_span_ms` 取该帧跨度；**或**在自检 `limitations` 与 HC-28/29 推导中显式声明该模型为「以第 `T6-S02` 个 `WINDOW_MATCH` 帧为窗口结束帧」的近似，且仅适用于 `P ≥ T6-S01/(T6-S02−1)` 的样例。

## 8. 观察项（不计为问题）

- **O1（哈希口径）**：证据绑定**工作区 CRLF 字节**；`git cat-file blob 1632761:…` 为 LF（`core.autocrlf=true`；`docs/stage6/**`、`report/evidence/S6-A/**` 未在 `.gitattributes` 标 `-text`）。我对被审提交 42 个改动文件逐一比较：**内容真正不同者 0**（git 归一化后完全相等）；r04 同口径，非本轮回归。建议后续为 `docs/stage6/**` 与 `report/evidence/S6-A/**` 加 `-text`，使 git 字节与证据哈希一致。
- **O2（文档版本令牌）**：文档全文不含完整令牌 `S6A-G0-v1.4`（用「v1.4 / r05」），与 r04 相同（r04 亦无 `S6A-G0-v1.3`）；版本一致性由 JSON/证据/STATE 三处承载。建议后续在文档表头显式写出契约版本号。
- **O3（残留标签）**：`coverage_matrix.json` 的 `location` 字段仍写「§5 B01–B28（**v1.3**）」，是全包唯一残留 v1.3 字样（位置标签而非版本声明）。
- **O4（并发写入）**：我复核期间（02:10→02:20）工作树出现**新的未跟踪写入**（`report/evidence/S6-B/`、`verification/s6b_run_cases.py`；另有既存 `src/stage6/`、`docs/stage6/s6b_frozen_interface_v1.json`），`git status --porcelain` 中 **tracked 修改 = 0**；被审 20 个文件评审始末哈希一致，r05 证据目录 35 文件 mtime 均停在 `02:08:13`、哈希复核无变化 → **不影响本次结论**；但提示总控：S6-B 开发已在同一工作树并行进行，须与评审/提交串行（"一个文件同一时刻只有一个写入方"）。
- **O5（`review_verdict` 与「本包已通过」措辞）**：JSON `revision.review_verdict` 与文档 v1.4 修订记录首句写的是**被引用的 r04 复评**为 `PASS`（0 阻断 / 5 非阻断）；我已核对 `report/evidence/CTRL-DSH-HANDOFF/reviews/S6A_r04_20261023_r01/REVIEW_r04.md` 确为 `PASS`、被审提交确为 `b20b670`，**事实成立**；`review_status` 仍为 `PENDING_REVIEW`，同段末与 §18 均声明「本包不因收尾而视为通过」「本轮未完成独立审查」。仅"本包"一词在 r05 段落下有被误读为 r05 已通过的空间，下轮可改写为「r04 包（b20b670）已通过第 4 轮独立复评…」。
- **O6（C1 版本白名单）**：`allowed_versions` 为历史白名单（v1…v1.4），故把 JSON 改回 `S6A-G0-v1.3` + `run_id=r04` 时 C1 仍 PASS（我的 X10 注入 exit 0）。这是自检**既有设计**（旧包重跑需让 r01..r04 通过 C1 才能考 C7/C12/C17），r05 只是追加 v1.4，**非削弱**；版本真实性由 C11 清单/哈希绑定保证。该结果非缺陷，记录以免后续误判。
- **O7（旧包证据路径）**：`selfcheck_*_failure.json` 内的 `inputs.*_path` 指向未入库的 `tmp/6/S6-A/…/legacy/…` 副本；可复现性由 `r04_package_under_test.json` 中的 git ref + sha256 保证——我已按该 ref 独立复现（§5.3）。

## 9. 我未做的事（限制，如实登记）

- 未修改任何被审文件；**未在 `w6` 内创建或修改任何文件**（故未直接运行 `s6a_r05_probe.py` / `s6a_rerun_legacy_failures.py`——它们会向被审证据目录与 `tmp/6/**` 落盘；我改为在隔离目录**复刻同逻辑**运行并比对入库产物，见 §5.4/§6.4）。
- 未创建/未参与任何状态机实现；未上板、未接触摄像头/HDMI/JTAG/COM4/hw_server；未烧录、未 program。
- 未复核 S6-B/6-C/6-D/6-E 与 `src/stage6/**` WIP 的**语义**（仅核对 `docs/stage6/*` 引用是否悬空，按 `N-r04-05` 的关闭范围）。
- 未复核 r01/r02/r03 证据目录全部文件的语义（只按本次重跑与清单范围核对）；未验证历史各轮评审报告结论的正确性（只把 r04 报告当作待证伪断言，并核对其 `PASS` 与被审提交一致）。
- 未运行任何需要审批或越权的操作；本会话为受限子代理，无法扩权。
- 结论只覆盖 r05（提交 `1632761`）；**不代表 G0/G2/G4/G5**。

---

## 附：本轮证据（全部在 `D:\FPGA_Competition\tmp\review\S6A_r05_20261023_r01\`）

`REVIEW_r05.md`（本报告）、`my_checks.txt`（全量比对）、`my_extract.txt`（HC-28/29/30、r04 失败证据、probe 汇总、绑定口径）、
`my_legacy.txt`（r04 git 字节重跑）、`my_probe.txt` + `probe/`（复刻 8 例 + 我加 10 例，含各例 result/stdout）、`my_probe_compare.txt`、
`my_checks3.txt`（diff 删除行清点、fix_record/limitations/coverage/run_summary/manifest、§17）、`my_details.txt`（各例 detail、§18 文件存在性、计数核对）、
`my_bytes_check.txt`（42 文件 worktree vs git 字节）、`my_hashes_full.txt`、`final_recheck.txt`、`doc_s9_s14.txt`、
`inject/Y1_demo.txt` + `Y1_*`（§9「取较晚」演示）、以及上述全部自写脚本 `*.py`。