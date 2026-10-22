# 终审批次 A（S6-A r08 + 工具）独立复评记录（CHANGES_REQUIRED）

- 被审版本：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，提交 **`f3c537d`**（另核 `1839766`、`e3aeb09`、`05126fd`、`902be77`）
- 评审方：DSH 项目总控派出的**终审 Reviewer A**（只读；未在 w6 写入）；隔离目录 `tmp/review/FINAL_A_20261023_r01/`
- 时间（UTC+8）：2026-10-23 04:45–05:06
- **结论：`CHANGES_REQUIRED`（阻断 2；非阻断 8）**
- 边界：只覆盖 S6-A r08 与相关工具，不代表 G0/G2/G4/G5，不评价 S6-B 实现语义。

## 1. 阻断

**`BLK-r08-1`｜`BLK-r07-1` 未真关闭：8 处只改了 5 处**
- 真实残留 3 处（`f3c537d` 提交字节，且**在 `1839766` 中仍在**）：① `r08/limitations_not_executed.json` 的 `not_run[7].reason`「…M4 被 M10 遮蔽、不可达…」；② `r08/coverage_matrix.json` 的 `runbook_coverage[item4].status`「…M4/M7 显式登记不可达，U6-12」；③ `.codex/STATE.md:61`「不可达项（不计入覆盖）：…M4/`T6-S04`（U6-12）…」（该行还与其自引的 S6-B `reachability_notes.json`「M4 可达并计入覆盖」矛盾）。
- 已改的 5 处：`parameter_notes.T6-S04`、清单 `limitations[3]`、HC-23（true）、摘要、文档 §18。
- **新 C16 断言无判别力**：扫描范围仅"文档 .md + 行为表 JSON + 手算样例"，**不含**清单/coverage/limitations/摘要/STATE；needle 仅 6 条字面量。评审注入**包内真实残留措辞** → `ALL_PASS`（漏判）；把出厂字面量写进 `limitations_not_executed.json` → `ALL_PASS`。
- 另：包内四处（`revision.changes`、`coverage_matrix.review_fix_coverage`、文档 §8、STATE L39）称"统一到 8 处"属**假陈述**。
- 关闭条件：3 处改为"M4 可达、`M4/T6-S04` 保留并计入覆盖（不可达仅 B16/M7）"；C16 扫描扩到清单/coverage/limitations/摘要/STATE 并改语义判定（白名单仅放行显式历史语境整行）；用评审给的 3 条真实残留行做回归（须 FAIL）；重跑自检仍 17 项 `ALL_PASS`、两检查器 exit 0。

**`BLK-r08-2`｜新硬规则交付物 `claim_verification` 不可信**
- 位置：`verification/claim_verify.py`（`forbidden` L178-179、扫描范围 L181-188、跳过条件 `if any(part in ("logs","tmp") ...)`、`make_claim` 的 `exit_code` 合成 L62-73）；`r08/claim_verification.json` 的 `S6A-C1-no-m4-unreachable`；`verification/s6a_build_evidence.py:300` 中止守卫。
- 问题：① C1 的"禁语命中 = 无"**与包内事实相反**（对 3 条真实残留全部漏判）；② 标为"真实退出码"的 `exit_code` 是 `0 if ok else 1` 的**合成值**，per-claim 命令从未执行（C2 的命令还含占位符 `<tmp>`）；③ **路径含 `tmp` 组件时全部被扫文件被静默跳过**（评审隔离目录正好如此 → 假 PASS 方向）；④ 构建器仅在 run_dir 已有 `selfcheck_result.json` 时中止：**新 RunId 首版不中止**，会发布 `NOT_ALL_VERIFIED` 且清单 checks 不引用该附录。
- 关闭条件：needle/范围按 `BLK-r08-1` 收紧；`exit_code` 改**真实 subprocess 退出码**；跳过判定改 **run_dir 相对路径**；构建器**首版也中止**；清单 checks 增加引用 `claim_verification.verdict` 的检查；重跑并覆盖入库附录。

## 2. 已确认关闭（摘）

- **`N-r07-1` 真关闭且有因果证明**：干净克隆 + `autocrlf=true` 下 `f3c537d`/`e3aeb09` 均 `SELF_PROVEN [0,0,0]`；**同一环境用 r07 版工具**跑同一提交 → `NOT_SELF_PROVEN [1,0,2]`（假阴性可复现且正是本轮修掉那步）。r07 两反例重复通过（改 1 个非换行字节 → `NOT_SELF_PROVEN` 且**内容未改写**；只改行尾 → `SELF_PROVEN`）。
- **`N-r07-2` 关闭**：`r08_selfproof/export_selfproof.*` = `ALL_SELF_PROVEN`，主体为交付提交，**0 处**陈旧 `FAIL`。
- 无回归：24 参数逐字段差异 0、`PENDING_APPROVAL` 24/24、ID 集合无增删、样例 32=32（仅 HC-23 变）、清单 48 条 0 缺失 0 哈希不符、`hashes_sha256.txt` 38/38、无虚假"已审查/已通过"。
- 复跑比对：自检 `ALL_PASS 17 项 / C7=32`、两检查器 exit 0、探针 10/10，多个产物**逐字节相同**。

## 3. 非阻断（要点）

`N-r08-1` **`delivery_manifest.source_commit = 05126fd` 是"不可达"对象**（不被任何 ref 包含、仓库无 tag）：传输克隆内 `git cat-file -t 05126fd` → `fatal: Not a valid object name`，自证 `NOT_ALL_SELF_PROVEN`、inputs/evidence **exit 2**（`source_commit 未解析为本地 Git commit 对象`）⇒ **F6 规则对 r08 交付包无法由第三方复现**；且"F2 三处统一"为假陈述（STATE 与 JSON baseline 实为 `bdcf896`）。
`N-r08-2` `keep_reason` 仍写"样例数 29<30"（F4 未关）。
`N-r08-3` STATE 陈旧行（v1.4/r05、证据入口 r07、允许范围/恢复命令指向 r07）（F5 未关）。
`N-r08-4` `coverage_matrix:33`、`limitations:49` 仍含非历史语境 v1.5（F11 未关）。
`N-r08-5` `f3c537d` 交付的 S6-B r03 `_selfproof` 实为 `NOT_ALL_SELF_PROVEN`（worktree snapshot 主体 exit=2、`files[54]` 哈希不匹配），与提交信息"ALL_SELF_PROVEN 0,0,0,0"**相反**。
`N-r08-6` `s6a_r08_probe.py`/`probe_summary.artifact` 仍写 r07 标签。
`N-r08-7` `s6_g0_selfcheck.py` 的 `recompute(kind="m4_reachability")` **硬编码 True** → HC-23 的"C7 机器断言"退化为常量比较（可达性事实评审已独立确认）。
`N-r08-8` 仓库**无任何 tag**；审查期间 HEAD 前移至 `1839766`（3 处残留在其中仍在 ⇒ 阻断未被取代）。

## 4. 提交结构结论（只判内容不判标签）

- `902be77` = 中间提交、**不自证**（STATE 声明了当时不存在的 S6-B r03 目录，实测 `[1,0,0]`）→ 不得登记为 r08 交付提交。
- `e3aeb09` **内容 = S6-B r03 + STATE 修正 + r08 证据重建**属实（`git diff --name-status 05126fd e3aeb09` 恰 11 个文件，不含 `src/stage6/**` 与 S6-B 证据本体），其自身 `SELF_PROVEN [0,0,0]`，但**标题与内容不一致**。
- `05126fd` = amend 前内容，**不可达、无标签**，却被 S6-B r03 `_selfproof` 列为已核验主体、被 r08 清单当 `source_commit`。
- 建议：勘误写进 ①w6 STATE 勘误小节（逐条内容 vs 标签 + 真实命令/退出码）②`r08_selfproof/export_selfproof.md` 的 `subject_note` ③`r08/coverage_matrix.review_fix_coverage`；**不 rebase/amend/filter-branch**。冻结采用**两段式**（F=交付内容、G=自证记录，**标签打在 G 上**），并在 STATE 写明二者关系；冻结三条硬条件：3 处残留清零、`source_commit` 与 `_selfproof` 主体均为**可达**提交、由**传输克隆**复跑 `export_selfproof --commit <冻结提交>` 得 `SELF_PROVEN`。

## 5. 处置

- 已派 `task-12`：`BLK-r08-1`/`BLK-r08-2` + `N-r08-1..8`；并授权在**自证记录提交**上打本地附注 tag（不 push）以解决"不可达对象"问题。
- 终审 B（S6-B r03 实现）仍在跑；两批结论齐后一次性修 → 重建 → 双侧自证 → 冻结提交 + 增量专项复核。