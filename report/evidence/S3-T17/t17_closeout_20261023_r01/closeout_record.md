# S3-T17 阶段A 关闭项记录（task-20）

- 输入：快修复审 `report/evidence/CTRL-DSH-HANDOFF/reviews/S3_T17_QFIX_20261023_r01/REVIEW_REPORT_S3_T17_QFIX_r01.md`
  判 `CHANGES_REQUIRED`（R-1/R-2 已确认关闭、阶段B 今晚可用；本轮为 Q-A + Q-1..Q-5）。
- 执行方：DSH 阶段3 总控（`stage3-lead`）。**本轮未接触硬件**；颜色子项仍 `DEFERRED_PENDING_MODULE`。
- 本轮**不改判定逻辑、不改阈值**：改动限于执行器运行位置护栏、文本/证据更正、以及自证工具的 CLI 回归。

## 一、Q-A 运行位置护栏（最优先）

**问题**：`run_t17_color_retest.sh` 原先把 `WT="D:/codex-worktrees/dbdf"` 写死，而 `WT` 决定**全部写入位置**
（`report/evidence/S3-T17/<run-id>/`、`tmp/3/S3-T17/<run-id>/`、脚本路径、ELF 路径）⇒ 从克隆调用会**静默写坏 dbdf 证据**。

**修法**（`scripts/stage3_t17/run_t17_color_retest.sh`）：
1. `WT` 参数化：`WT="${T17_WT:-D:/codex-worktrees/dbdf}"`，并新增选项 `--wt <路径>`；
2. **运行位置护栏**（置于**任何 `mkdir`/写文件之前**）：`norm_dir()` 归一化（优先 `pwd -W`，Git Bash 下得 `D:/…`；大小写不敏感比较），
   逐条判定：`WT` 不存在 ⇒ exit 2；`WT` 不是 git 工作树（`.git` 文件或目录皆可）⇒ exit 2；
   **cwd ≠ WT ⇒ exit 2**（输出 `T17_GUARD_CWD_MISMATCH=1`、`T17_CWD`、`T17_WT`、`T17_RUN_FROM_WORKTREE_REQUIRED=1`、`T17_RUN_ABORTED=1`）；
3. 头注释补齐用法与退出码语义（exit 2 新增「护栏拒绝」含义），两个 README + 模板改为
   「**须在 dbdf 内运行，或显式 `--wt`/`T17_WT`**」，删除「可在克隆内跑」的误导用法。

**实测（真实退出码 + 是否产生文件）**（`bash -n` 先过，退出码 0）：

| 场景 | 命令要点 | 真实退出码 | 关键输出 | 是否产生文件 |
|---|---|---|---|---|
| 从别的工作目录 | `cd D:/FPGA_Competition && bash <dbdf>/scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_guard_probe_20261023_r01` | **2** | `T17_GUARD_CWD_MISMATCH=1`、`T17_CWD=D:/FPGA_Competition`、`T17_WT=D:/codex-worktrees/dbdf` | **无**（`qa_guard_from_other_cwd.stdout.txt`） |
| 从克隆（不给 `--wt`） | `cd <clone_lf_g4> && bash <dbdf>/scripts/… preflight --run-id …` | **2** | `T17_CWD=D:/codex-worktrees/dbdf/tmp/3/S3-T17/clone_lf_g4` | **无**（`qa_guard_from_clone.stdout.txt`） |
| `T17_WT` 指向不存在路径 | `T17_WT=D:/nope/nothere bash <dbdf>/scripts/… preflight --run-id …` | **2** | `T17_GUARD=WT_NOT_FOUND` | **无**（`qa_guard_bad_wt.stdout.txt`） |
| **正向**：在 dbdf 内 | `cd D:/codex-worktrees/dbdf && bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_guard_ok_20261023_r01` | **0** | `T17_PREFLIGHT_EXIT=0`、`OFFLINE_GO` | 落在 **dbdf**（`qa_guard_positive_in_dbdf.stdout.txt`） |

「未产生文件」的判据：护栏用同一 `--run-id t17_guard_probe_20261023_r01` 跑三次后，
`report/evidence/S3-T17/t17_guard_probe_20261023_r01` 与 `tmp/3/S3-T17/t17_guard_probe_20261023_r01`
**在任何位置都不存在**（dbdf、克隆内均实测 `has_QA_dir=False`；各目录文件数在护栏前 81/397、护栏后不因护栏增加）。
（本目录新增的 3 个 `qa_guard_*.stdout.txt` 是**我自己抓取的证据**，非执行器产生。）

## 二、Q-1 行号更正（6 处）

该文件**没有** 157 行：`cmos_8_16bit_ref.v` 含**混合行尾**——按 `\n` 计 **83 行**、Python `splitlines()` 计 **167 行**；
原「第 157 行」正是 `splitlines()` 计数造成的假象。拼接语句按 `\n` 行计在第 **79** 行。
⇒ 已把 6 处（`analyze_t17_bit_integrity.py` docstring、prep `README.md`、`t17_judgement_table.json`、
`t17_judgement_table.md`、`t17_artifacts_verified.json`、`quickfix_record.md`）统一改为
**引用「语句原文 + blob sha256」为主、并注明 `\n` 行计为 79 行与混合行尾的计数陷阱**。

## 三、Q-2 计数口径改为可复现

旧文「盘上 56 份」含**跨树**计数且未写命令/范围 ⇒ **不可复现**，已作废。新口径（dbdf 内，46/47 实查）：

```bash
cd D:/codex-worktrees/dbdf
find . -name 'cmos_8_16bit*.v' -not -path './.git/*' | wc -l      # => 47
# 47 份中 45 份恰为同名 cmos_8_16bit.v，另 cmos_8_16bit_ref.v、cmos_8_16bit_gh.v 各 1
# 对每份 grep 'pdata_o\s*<=\s*{pdata_i_d0\s*,\s*pdata_i}' ⇒ 47/47 全部含该拼接语句
```

其中**已入库参考 1 份**：`report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v`
（blob sha256 `08a325356fdb46fcbd87e1b594a2b5d3c30954b68d18e4ea22d36e914cd414b9`，3318 B）。

## 四、Q-3 已提交证据被机械改写 —— 见 `q3_mechanical_restore.md`

选 **(a)**：`f77f363` 对照下判定为**纯机械**的 **30 行**（takeover README 2、prep README 9、
`t17_judgement_table.json` 9、`.md` 2、`.codex/STATE.md` 8）已**逐行还原为提交字节**；
其余差异均为本轮有意修改，逐行 diff 见 `q3_intentional_diff_f77f363_to_worktree.diff`；
`quickfix_record.md` 内那条失实声明**已就地更正**。

## 五、Q-4 运行时刻改正 + Q-5 覆盖口径改正与新回归

- **Q-4**：交付态 record 的运行时刻改为**实际值 `2026-10-23 11:46:33`**（取自 `handoff_check` 自身
  check-e 输出 `当前时间(UTC+8)=2026-10-23 11:46:33`，见 `…/t17_quickfix_20261023_r01/g4_handoff_delivered.json`）；
  `base_commit` 仍是运行时刻的 `605f960`（该值正确）。原先的「11:52」与证据（11:46:33–40、mtime 11:46:32、
  G4 提交 11:49:08）冲突，已更正并在 record 内注明来源。
- **Q-5**：`analyze_…` 的 CLI 回归**不能**证明「入口兜底存在」——突变试验（仅删 `_force_utf8_streams()` 调用）
  下 `--selftest` 仍 rc=0 PASS，因为**第三重防护**（JSON 先落盘 + 打印 try/except）兜住了崩溃。
  ⇒ 已在 scripts README 与本记录中如实写明**三层防护与各自覆盖边界**；
  并给 `verify_t17_blob_identity.py` **新增 CLI 回归**（该工具**没有**第三重防护）：

| 回归项 | 期望 | 实测 | 判定 |
|---|---|---|---|
| `cli_verify_gbk_exit0_json`（GBK + 管道下跑本工具） | exit 0 且写 JSON | **exit 0、JSON 落盘** | matched |
| `mutant_old_form_detected`（**旧形态突变体**：去入口兜底 + 打印恢复 `U+21D2`） | 非 0 退出或缺 JSON | **exit 1、未写 JSON**，`stderr` 末行 `UnicodeEncodeError: 'gbk' codec can't encode character '\u21d2'` | matched（**证明有判别力**） |

命令与原始输出：`python -B scripts/stage3_t17/verify_t17_blob_identity.py --selftest --fixture-dir tmp/3/S3-T17/t17_verify_selftest_r01`
⇒ **exit 0**（`SELFTEST_PASS`），证据 `q5_verify_selftest.json` / `.stdout.txt`。
（突变体构造按**打印行**定位注入，并把 `mutation_applied` 写入 JSON 自检，避免「突变没打中 ⇒ 假判定」。）

## 六、哈希与清单刷新

| 目录 | 处理 |
|---|---|
| `…/t17_color_retest_prep_20261023_r01/` | `hashes_sha256.txt` **自 F2 起已过期**（非本轮引入）⇒ 按当前内容整体重算 |
| `…/t17_takeover_20261023_r01/` | record/README/交付态复核输出变动 ⇒ 重算 |
| `…/t17_quickfix_20261023_r01/` | `quickfix_record.md` 更正 ⇒ 重算 |
| `…/t17_closeout_20261023_r01/`（本目录） | 新增清单与哈希 |

## 七、未做项与边界

- 未接触硬件：无 JTAG/COM4/`hw_server`/位流加载/烧录；四个硬件阶段全未执行（现场核：无重型进程、3121 无监听、无 `hw_authorization.json`）。
- 阶段B 仍等 **Wong 开工信号 + Codex 书面让出**（013/014 未见回执）；本轮不动板。
- 未改主仓 `verification/handoff_check.py`（检查项 a 仍为前缀比较）；未加 `.gitattributes`；未做独立审查。
- 本轮**未改判定逻辑与阈值**；本记录不代表阶段A 通过、颜色通过或 G3/G4/G5。