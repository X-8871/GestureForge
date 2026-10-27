# S4-T30 最终轮增量核对（三点关闭判定）

- 对象：**`43a9a4cce046f38a33f2fcffd8570267e341917b`**（父 `bd511e1c75ca1078e659d4b595cdf1fbf0003bbc`；17 文件；作者=提交者 `2026-10-27T20:30:05+08:00`；未 push）
- 复审方：DSH 阶段3 总控（只读）；工作区 `D:\tmp\review\S4_T30_20261027_r01\`（仓库外）
- **未写 w4**：核查前后 `status` sha256 / `index` sha256 / HEAD 逐字节不变；未跑写仓库命令；未动硬件

## 结论：**DELTA_PASS**（三点全部关闭；2 条非阻断建议）

| 点 | 判定 | 依据（真实退出码） |
|---|---|---|
| **1. `hash_basis_commit` 钉成 40 位 SHA** | **真修 ✓ 关闭** | 两清单均为 `bd511e1c75ca1078e659d4b595cdf1fbf0003bbc`；`git rev-parse --verify bd511e1…^{commit}` → **exit 0**；逐项 `git cat-file blob bd511e1:<path>` 复算 **r01 13/13、r02 10/10**；`source_commit` 逐项同为 `bd511e1`；复算表**三列齐**（`commit_blob_sha256`/`baseline_blob_sha256`/`disk_sha256`，entries 13/10、`failures=[]`、`baseline_commit` 分别 e39f6de/d5a86bf）；门禁独立实跑 **6/6 exit 0**：`--commit bd511e1` strict/declared、`--commit 43a9a4c` strict/declared、默认 HEAD strict/declared（均 2 manifests / 23 checked / 0 mismatched） |
| **2. NB-1 时间戳真断言** | **真修 ✓ 关闭** | `check_evidence_timestamps.py` 真做 `value > commit_time` 比较、违规 `return 1`；记录 exit **0/0**。**我的自建注入**（仓库外 scratch repo，把 `post_freeze_rebinds[-1].at_utc8` 设为 `2026-10-27T23:59:59`，提交时刻 20:30）：正控 **exit 0**、注入 **exit 1** 并输出"[FAIL] 时间戳断言：2/3 合法；违规=…时间戳晚于提交时刻（写不出未来事实）" |
| **3. schema 归属诚实** | **真修 ✓ 关闭（附字面口径说明）** | `SCHEMA_ATTRIBUTION.md` 存在且明写"本包不使用 check_stage_delivery schema…实跑 **exit 2**…**不得**对本包声称 CHECKS_OK"；`check_stage_delivery_schema_mismatch.exit_code.txt` = **exit=2**；stdout 为真实 `{"status":"CHECKS_FAILED","mode":"evidence",…}` 含缺字段/未知字段原因；"CHECKS_OK/通过 check_stage_delivery"字样仅出现在**禁止句**内（非声明） |

**漂移前提（重点）**：`git diff --name-only bd511e1c75ca1078e659d4b595cdf1fbf0003bbc 43a9a4cce046f38a33f2fcffd8570267e341917b` = 17 文件，与两清单所列 17 项**交集 = 空** ⇒ 所列文件在本提交前后未变；基座钉在 `bd511e1`（字面 SHA、不依赖工具默认 HEAD），故**不会随 HEAD 前移而漂移**（默认 HEAD 复跑仍 exit 0）。

## 新增要核

| 项 | 结果 |
|---|---|
| `hash_basis_commit` 语义自洽 | ✓ `source_commit` 全部 = `bd511e1`；声明值 == `git cat-file blob bd511e1:<path>`；三列复算齐 |
| 移除跨 RunId 引用 | 实际为 **r02 12→10**（移除对 r01 `README.md`/`landing_manifest.json` 的 2 条跨 RunId 引用）；r01 保持 13（含 7 条上游 docs/scripts/STATE 源文件）。两 README 互相引用（r01→r02、r02→r01）⇒ **未静默丢覆盖面** |
| 23 与包内文件数 | r01 目录 18 文件、r02 目录 35 文件，清单共列 23 项 ⇒ 清单为**精选产物**（非全量）；README 未声明选择规则 → **非阻断建议**：补一句"清单为精选产物，逐文件全量见目录" |
| **README 与清单不一致（非阻断）** | r01 README 仍写"`files[].sha256` 已全部改为 **e39f6de** 的 blob 基座"/"r01 = 被审提交 e39f6de 的 blob 基座快照"，实测 **13/13 = bd511e1** blob（仅 10/13 = e39f6de）；两 README 均**未出现** `bd511e1`/`hash_basis_commit` 字样 ⇒ 机器可读部分已钉对，人读表述未同步。建议补一句"`hash_basis_commit=bd511e1`（钉住），`baseline_commit` 列 = e39f6de/d5a86bf"（不改数据） |

## 新问题检查（全部通过）

| 检查 | 结果 |
|---|---|
| 提交范围 | 17 文件**全在授权路径**，越界 0 ✓ |
| 25 项未提交 | 与提交清单**交集为空** ✓（dirty=25，均为原持有方/历史件）；无 `index.lock`；未 push（442 提交未推送）✓ |
| 语义未变 | 地址图 **`7c20ac89…`**（now=prev=reviewed 三者一致）；契约 **`25bc30d5…`**（=prev）；缺口表 **`c65c2819…`**（=prev）；契约 `1.3.0/FROZEN_OFFLINE_ONLY/r07`；**G-01/G-02 仍 `PARTIALLY_CLOSED_OFFLINE`** ✓ |
| 三器复跑（真实退出码） | `verify_d1a_landing` **0**、`verify_shared_io_contract` **0**、`audit_raw_system_g0_gaps` **0** ✓ |
| 无关口断言 | `ENABLE=1` 4 处命中均为否定/待办/边界表述（"须先满足前置"、`not_done`、"未做"、"`ENABLE=0`"）⇒ **0 违规** ✓ |
| S4-T31 准备件 | **不在提交内** ✓（`git ls-tree` 无匹配），且**仍在盘上**（`four_measurements` 计划 + `m1/m2/m3*.tcl` 等 6 项均 `Test-Path=True`、位于 untracked）⇒ 未被删除、未被误提交 ✓ |
| w4 | 前后状态逐字节不变 ✓ |

## 非阻断建议（不影响关闭判定）

1. 同步 README 基座表述（r01 那句 `e39f6de` 基座对 3/13 不成立；两 README 均未写 `hash_basis_commit=bd511e1`）。
2. 两 README 补"清单为精选产物"的选择规则说明（23/53）。
3. `check_evidence_timestamps.py` 目前读**工作区** docs（`CONTRACT.read_text`）而非 `git show <commit>:<path>`；建议改为读提交 blob，避免工作区与提交不一致时断言对象不同。
4. schema 禁止句内出现 `CHECKS_OK`/`通过 check_stage_delivery` 字面字样；若按"全文无字样"口径，可改为"不得声称交付检查通过"等无字样表述。

## 一句话

**三点全部关闭，`S4-T30` 可标为已完成**（技术语义无回归、范围/证据/门禁均通过）；仅余 4 条文档/健壮性非阻断建议，可在后续收尾提交并入。**本结论不代表 G0/G4/G5 或板级验收通过**。

## 附：核对期间分支前移（不改变本结论）

- 我落笔时 w4 HEAD 已由 43a9a4c 前移到 **6014fb5**（其后 4 个提交均为 **S4-T31 离线准备**：25fe0c 四测量载荷/执行计划、8abf831 M4-a 测量 ELF/驱动、c7ed60 registry 打印修复、6014fb5 驱动登记）。
- 已核：**43a9a4c 仍是 HEAD 祖先**（merge-base --is-ancestor **rc=0**），未被改写/丢弃；本次所有内容核验均以 git show 43a9a4c:<path> **逐字节**取件，不受前移影响。
- 已核：清单所列 17 项**未被其后提交改动**——默认 HEAD 门禁复跑仍 **exit 0**（2 manifests / 23 checked / 0 mismatched），且 dirty 与所列 17 项**交集为空** ⇒ 三器读到的文档与 43a9a4c 树一致，结论有效。
- 备注：先前"6 个 S4-T31 准备件刻意未提交"对**被判对象 43a9a4c** 成立（git ls-tree 无匹配、文件仍在盘上）；其后 25fe0c/8abf831 已将部分准备件纳入版本库，属 S4-T31 任务范围，不在本次核对对象内。
