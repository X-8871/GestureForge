# S3-T17 阶段A 快修复审报告（Reviewer，task-19 quick-fix round，r01）

- 被审：工作树 `D:\codex-worktrees\dbdf`（分支 `codex/stage3-video`），内容提交 **F3 `605f960`**、自证记录 **G4 `975f3a5`（HEAD）**；修复前置 `f77f363`。
- 上轮复审：`report/evidence/CTRL-DSH-HANDOFF/reviews/S3_T17_FIX_20261023_r01/REVIEW_REPORT_S3_T17_FIX_r01.md`（`CHANGES_REQUIRED`：R-1/R-2 + N-1'/N-3'）。
- 评审性质：**只读**；环境与命令**一律不设 `PYTHONUTF8`**、stdout 重定向到文件；全部验证只写
  `D:\FPGA_Competition\tmp\review\S3_T17_QFIX_20261023_r01\`（自建；含 `git -c core.autocrlf=false` 传输克隆 `clonet`）。
- **未做任何硬件动作**：无 JTAG/COM4/hw_server/位流加载/烧录；四个硬件阶段（`link`/`baseline`/`bars`/`restore`）全未执行。
- **不评价未执行的硬件步骤**；本报告不代表阶段A 通过、颜色通过或 G3/G4/G5。

## 结论：`CHANGES_REQUIRED`

**先给最要紧的一句**：**阶段3 阶段A 的工具链现在可以放心用于今晚阶段B**——R-1/R-2 在我独立复跑下**真的关闭**了（无崩溃、退出码 1/3 正确、`--json-out` 均落盘、显式 `PYTHONIOENCODING=gbk` 也被覆盖）；`preflight`/`judge`/自证/自测/record 复核全部实测通过（见 §1）。**不要用本轮的自证文本/清单去冻结或对外复跑**：交付文本里有 3 处可核验的不实/不可复现陈述（N-1 引用的**行号错**、**「56 份」不可复现**、**自报「已提交证据逐字节还原」不成立**），另有 1 处时间戳与证据冲突（N-3 的 11:52）。这些**不影响今晚跑板**，但属于上一轮 `CHANGES_REQUIRED`（依据陈述不实）的同一缺陷类，必须修完才能作为冻结自证。

## 1. R-1/R-2 是否真关闭（在传输克隆 `tmp\review\S3_T17_QFIX_20261023_r01\clonet` 内，HEAD=975f3a5）

全部命令**不设 `PYTHONUTF8`**、stdout 重定向；下表为**真实退出码**（脚本与原始输出见本目录 `cmd/`）。

| # | 命令（README 口径） | 真实退出码 | JSON 落盘 | 备注 |
|---|---|---|---|---|
| 1 | `bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_qfix_review_preflight_r01` | **0** | 是 | ⚠ 见 §5 注：执行器**硬编码 `WT=D:/codex-worktrees/dbdf`**，从克隆里跑实际检查并写入了 **dbdf**；我随后把本次新建的 `report/evidence/S3-T17/t17_qfix_review_preflight_r01/` 与 `tmp/3/S3-T17/t17_qfix_review_preflight_r01/` **已删除还原** |
| 2 | `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest --repo-root <clone> --fixture-dir <tmp> --json-out …` | **0** | 是 | `SELFTEST_PASS`，7 夹具 + **2 条 CLI 回归全匹配** |
| 3 | `… analyze… --frame <归档整帧 bars_raw_frame_full.bin> --json-out …` | **1** | **是** | `DEFECT_REPRODUCED`（语义正确） |
| 4 | `… analyze… --frame <只修一路 fixture_C_blue_only.bin> --json-out …` | **3** | **是** | `INCONCLUSIVE_ATYPICAL`（语义正确，非 1） |
| 5 | `python -B scripts/stage3_t17/check_t17_preflight.py --worktree <clone> --json-out …` | **1** | 是 | `OFFLINE_NO_GO`：`git.head_ok=true`（relation=descendant），**失败项恰为 7 件未入库 `tmp/**` 冻结产物**（README 已写明的纯克隆依赖） |
| 6 | `python -B scripts/stage3_t17/verify_t17_blob_identity.py --repo-root <clone> --commit HEAD --json-out …` | **0** | 是 | `检查文件=105 不一致=0 提交内缺失=0 工作区含 CRLF=0`，`BLOB_BYTE_IDENTITY_OK` |
| 7 | `python -B D:/FPGA_Competition/verification/handoff_check.py --worktree dbdf --record …delivered.json` | **1** | — | `HANDOFF_FAILED`，**仅检查项 a FAIL**（前缀比较：HEAD=975f3a5 vs 声明 605f960），**不是 exit 2**，即 record 字段无越界 |

**额外：显式 `PYTHONIOENCODING=gbk` 复跑关键三条（执行方声称 `reconfigure` 会覆盖它）——已验证成立**：
`verify_t17_blob_identity.py` **rc=0**（`BLOB_BYTE_IDENTITY_OK`）、`analyze --frame 归档` **rc=1**、`analyze --frame 只修一路` **rc=3**，JSON 全部落盘。
即：`sys.stdout/stderr.reconfigure(encoding="utf-8")` 确实**覆盖** `PYTHONIOENCODING=gbk`，在管道/重定向下不再崩。
另核对：`scripts/stage3_t17/**` 内 **U+21D2 命中 0 处**（四个 .py + README + .sh + .tcl 逐一计数）。

## 2. 回归的判别力（我自己造的反例）

`f77f363` 版两工具取到隔离目录（`git show f77f363:<path>`，md5 见 `cmd/exit_codes.txt`）重跑：

| 反例（f77f363 版工具，不设 PYTHONUTF8） | 真实退出码 | JSON | 现象 |
|---|---|---|---|
| `verify_old.py --repo-root <clone> --commit HEAD --json-out …`（R-1 路径） | **1** | **未落盘** | `UnicodeEncodeError: 'gbk' codec can't encode character '\u21d2'`（`verify_old.py:75`） |
| `analyze_old.py --frame 归档整帧`（R-2 路径） | **1** | **未落盘** | `UnicodeEncodeError`（`analyze_old.py:555`） |
| `analyze_old.py --frame 只修一路`（R-2 路径） | **1（应为 3）** | **未落盘** | 把「非典型」误报成「复现缺陷」 |

⇒ 新加的两条 CLI 回归（断言「exit 1 且 JSON 落盘」「exit 3 且 JSON 落盘」）**若跑在 f77f363 版工具上必然不匹配**，**不是摆设**。

**但任务卡指定的突变试验未通过**：把 F3 版 `analyze_…py` 的 `_force_utf8_streams()` 调用行删掉后跑 `--selftest` → **rc=0 / `SELFTEST_PASS`（要求 FAIL，实测 PASS）**。我进一步加大突变：

| 突变体（基于 F3 版） | `--selftest` 结果 |
|---|---|
| b1：只删 `_force_utf8_streams()` 调用 | **rc=0 `SELFTEST_PASS`** |
| m1：恢复 `⇒`（`WHITE_BIT_NOT_SET` reason）+ 保留 `reconfigure` | **rc=0 `SELFTEST_PASS`** |
| m2：恢复 `⇒` + 删 `reconfigure` | **rc=0 `SELFTEST_PASS`**（手工直跑：归档帧 rc=1、只修一路 rc=3、JSON 均落盘） |

原因（代码事实，非猜测）：F3 给 `analyze_…py` 上了**三重冗余防护**——① 去 ASCII `=>`；② 入口 `reconfigure`；
③ **`--json-out` 先落盘 + 打印段 `try/except` 捕获**（`analyze_t17_bit_integrity.py:598-644`）。
m2 手工直跑的 stdout 实测含 `SUMMARY_PRINT_FAILED=UnicodeEncodeError: 'gbk' codec can't encode character '\u21d2' in position 46`，
**但退出码与 JSON 不受影响**（被 ③ 兜住）。
⇒ 结论：**CLI 回归能发现「旧代码形状」的回归，但无法发现单独移除 `reconfigure`（甚至 `reconfigure`+`⇒` 同时移除）**。
任务卡的「必须 FAIL」按设计不可能发生（突变选得不对），**不构成功能缺陷，但「自测覆盖该路径」的说法不成立**。
（另注：`verify_t17_blob_identity.py` 是「先打印、后写 JSON」且无打印兜底，R-1 路径**没有**任何 CLI 级回归覆盖。）

## 3. N-1 依据核实

**属实的部分**（我独立复算）：
- `report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v` **存在**（clone 工作区 3318 B）。
- blob 内容 sha256 = **`08a325356fdb46fcbd87e1b594a2b5d3c30954b68d18e4ea22d36e914cd414b9`**，3318 B —— 与声明**逐字符一致**（`f77f363` 与 `HEAD` 的 blob 相同）。
- 第 157 行**不是** `pdata_o <= {pdata_i_d0,pdata_i};`：该文件**只有 83 行**，`pdata_o <= {pdata_i_d0,pdata_i};//8位数据转为16位，位拼接` 在**第 79 行**。
  我对 dbdf 内全部 47 份 `cmos_8_16bit*.v` 逐份定位：**45 份在 55 行（59 行文件）、2 份在 79 行（83 行文件），没有任何一份在 157 行**。
  ⇒ 「第 157 行」这一引用**在全部副本上都对不上**，且被重复写进 6 处（`STATE.md`、prep `README.md`、`t17_artifacts_verified.json`、
  `t17_judgement_table.json`、`t17_judgement_table.md`、`quickfix_record.md`）与 `analyze_…py` docstring。
- 「盘上 56 份」**我数不出 56**（口径与我的计数）：
  | 口径 | 我实测 |
  |---|---|
  | dbdf `cmos_8_16bit*.v`（排除 `.git`） | **47**（其中恰好叫 `cmos_8_16bit.v` 的 45 份；**47/47 都含该拼接语句**） |
  | dbdf `cmos_8_16bit*`（任意扩展名） | 57（多出的 10 份是 `xsim.dir/work/cmos_8_16bit.sdb` 仿真库，非源码） |
  | dbdf + 主仓 `D:\FPGA_Competition`（含 `w2b`）unique | 57 |
  | dbdf + 主仓 + `D:\FPGA`（厂商原件）unique | 79 |
  上一轮复审数的也是 47。**56 这个数我无法用任何自然口径复现**（最接近的是 57，但含 10 份 `.sdb` 非源码）。
- 旧文「已被缓存清理/盘上未找到」**已被标明不实并更正，未悄悄删掉**：`t17_judgement_table.json` 的
  `byte_order_evidence[3].note` 明写「先前版本称…**不实**：盘上实有 56 份…」；`t17_artifacts_verified.json` 的 `note` 同；
  `git diff` 亦保留被删旧句（「已被缓存清理」原文可对照），不是静默删除。

⇒ **N-1 的实质已关闭**（依据真的存在、哈希对得上、内容支持「先到字节进高半字」），但**新引入两处不实/不可复现的支撑细节**（行号 157、56 份），
按上一轮 N-1 的关闭标准，这两处仍需改正（改行号；56 改为可复现口径或删掉）。

## 4. N-3 / README / record 核对

- **record 规范键**：`handoff_record_stage3_delivered.json` = **恰好 13 键**（`task/owner/worktree/branch/base_commit/allowed_paths/dirty_owner/
  yield_statement/heartbeat_utc8/evidence_dir/recovery_command/status/next_owner`），无 `verification_head` 等非规范键。
- **我复跑**：
  - as-is（当前 HEAD `975f3a5`，record `base_commit=605f960`）→ **exit 1**，`FAIL` **仅检查项 a** ⇒ **无未知名段导致的 exit 2** ✓
  - 按 record 自身说明把 `base_commit` 更新为当前 HEAD（副本仅放评审临时目录）→ **exit 0**，`HANDOFF_OK（PASS 8 / FAIL 0 / SKIP 1）` ✓
  ⇒ 「交付态 exit 0 只在运行时刻 HEAD=605f960 成立、HEAD 前进后必为 FAIL(a)」的说明**与实测一致**。
- **README**：`takeover README §5`（第 77–86 行）写明「运行时刻 HEAD + 前缀语义」「该 exit 0 不是恒久成立」「不要新增 record 字段（未知字段 → exit 2）」；
  `scripts/stage3_t17/README.md`「必读前提」写明「纯克隆的已知依赖：`preflight` 因 7 件未入库 `tmp/**` 返回 **1**，失败项是缺产物、**不是** HEAD 判据」——
  两项要求**均已写明**，且我用 §1 第 5 项实测复现（`git.head_ok=true`，失败项恰 7 件缺产物）。
- ⚠ **但 record 的运行时刻时间戳自相矛盾**：`yield_statement` 写「运行时刻 HEAD=605f960…（**2026-10-23 11:52**）」，
  而 G4 证据里 `handoff_check` 自报的「当前时间(UTC+8)」是 **11:46:33 / 11:46:36 / 11:46:38 / 11:46:40**，该文件自身 mtime 也是 **11:46:32**，
  G4 提交时间是 **11:49:08**。即「11:52」不可能是该 exit 0 的运行时刻（11:52 时 HEAD 已是 975f3a5，前缀比较必然 FAIL）。建议改为实际运行时刻或删掉分钟级声明。

## 5. 越界核实（本项**不通过**）

- **权威改动清单**：`git diff --name-status f77f363 605f960` = 29 项（`scripts/stage3_t17/` 4 个 .py + README、`.codex/STATE.md`、
  4 个已提交证据文件 + 1 个 record、新目录 `t17_quickfix_20261023_r01/**`）。
- **执行方自报**「一次机械替换曾误改已提交证据文件，已 `git checkout` 逐字节还原并复核 `CONTENT_DIFF_COUNT=0`」——
  **部分属实、整体不成立**：
  - `f77f363` 时**含 `⇒` 的已提交证据文件共 58 份**；其中 **54 份在 `605f960` 逐字节未变**（含被点名的两个例子：
    `handoff_check_claim.json`、`t17_fix_20261023_r01/fix_record.md`，blob sha1 完全相同）✓
  - **4 份被改且 `⇒` 全部消失（10→0、10→0、3→0、2→0）**，其中**纯机械替换**（去掉 `⇒`/`=>` 差异后逐字相同）的行数为
    **9 / 9 / 2 / 2**，即**与 N-1/N-3 语义无关的行也被改写**：
    | 文件 | −/+ 行 | 纯箭头替换行 |
    |---|---|---|
    | `report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/README.md` | 5/8 | 2 |
    | `report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/README.md` | 10/10 | 9 |
    | `…/t17_judgement_table.json` | 13/13 | 9（如 `verdict_rules`、`hardware_localization…` 等纯换字符行） |
    | `…/t17_judgement_table.md` | 3/3 | 2 |
    外加 `.codex/STATE.md`：`⇒` **11 → 0**（另 3 行为纯替换）。
  - 我**无法复现「17」这个数字**（58 份含箭头 / 54 份逐字节未变 / 4 份被改）。
  - 附带（**F2 起既有，非本轮新引入**）：`t17_color_retest_prep_20261023_r01/hashes_sha256.txt`（mtime 10:19）记录的
    `README.md=37a627b2…(10770B)` 对应的是 `525e4f35` 版；`f77f363` 时已是 12857 B ⇒ 该绑定**在 F2 就过期**，F3 又改动了这 4 个文件却未刷新该清单（F3 只刷新了 `t17_quickfix_*/hashes_sha256.txt`，其自身绑定 100% 正确）。
- **F3/G4 未 amend、F/G 分离** ✓：`git reflog show codex/stage3-video` 前 8 条全为 `commit:`，无 `commit (amend)`/rebase/reset；
  `f77f363 → 605f960 → 975f3a5` 线性且两级 `merge-base --is-ancestor` 均为真；`git log --graph` 单线。
  **G4 未改任何受审工具**：`git diff --name-only 605f960 975f3a5 -- scripts/` = **0 项** ⇒ 被审代码在 F3 与 HEAD 逐字节相同。
  仅 2 个文件被 F3 与 G4 同时改动（`handoff_record_stage3_delivered.json`、takeover `README.md`），二者都是 G 份内的记录文件，未触及 F3 的代码与失败证据。
- **无硬件** ✓：dbdf 内 `hw_authorization.json` **0 个**；F3/G4 新增文件与工具中**无** `T17_LINK_EXIT=`/`T17_BASELINE_CAPTURE_EXIT=`/
  `T17_BARS_CAPTURE_EXIT=`/`program_hw_devices`/`write_bitstream` 等实测行（`hw_server`/`xsdb`/`COM4` 命中全是 preflight 进程名单或文档说明）。
- **dbdf 工作区** ✓：`git status --short` = `?? NA/`、`?? clockInfo.txt`（评审前后一致）。
  ⚠ **如实披露**：我按 README 在克隆里跑执行器 `preflight` 时，因执行器**硬编码 `WT=D:/codex-worktrees/dbdf`**（`run_t17_color_retest.sh:36`），
  它在 dbdf 新建了 `report/evidence/S3-T17/t17_qfix_review_preflight_r01/`（`preflight.json`+`run_log.txt`）与空的 `tmp/3/S3-T17/t17_qfix_review_preflight_r01/`；
  我**已按精确路径删除还原**，并用 `find -newermt` 确认 dbdf 内除父目录 mtime 外无其它残留，`git status` 恢复原样。
  由此得到一条**可操作的阶段B 注意事项**：**执行器必须在 dbdf 内运行**；从克隆调用它不会作用在克隆上，而会静默写入 dbdf 的 `report/evidence/S3-T17/**` 与 `tmp/3/**`。

## 6. 关闭条件（本轮必须修，均为文本/证据级，不涉及工具行为）

| # | 位置 | 问题 | 关闭条件 |
|---|---|---|---|
| **Q-1** | prep `README.md`、`t17_artifacts_verified.json`、`t17_judgement_table.{json,md}`、`quickfix_record.md`、`.codex/STATE.md`、`analyze_t17_bit_integrity.py` docstring（6+1 处） | 引用「第 **157** 行」；该文件仅 83 行，语句在**第 79 行**，47 份副本中无一在 157 行 ⇒ 第三方按引用复核必失败 | 行号改为 **79**（或删去行号，只给文件+sha256+语句原文）；保持其余依据不变 |
| **Q-2** | 同上 4 处 + prep `README.md` | 「盘上实有 **56** 份同名厂商源码」不可复现（实测 dbdf `*.v` = **47**，含该语句 47/47） | 改为可复现口径（建议「dbdf 内 `cmos_8_16bit*.v` 47 份，全部含该拼接语句；其中恰好同名 `cmos_8_16bit.v` 45 份」）或删除该数字 |
| **Q-3** | `quickfix_record.md` §二.2，`reverify_after_fix.md` §3 | 自报「已提交的历史证据逐字节还原、`CONTENT_DIFF_COUNT=0`」**不成立**：4 个已提交证据文件 + `.codex/STATE.md` 仍保留机械替换（纯替换行 9/9/2/2 + 3） | 二选一：① 如实更正为「54/58 逐字节还原；4 份因同时有 N-1/N-3 语义编辑而保留 ASCII 化，其中纯替换行 22 行」，并声明这是**有意的 ASCII 归一化**；或 ② 把这 4 份文件回退到 `f77f363` 后**只重放** N-1/N-3 的语义编辑（`⇒` 复原），并同步刷新受影响目录的 `hashes_sha256.txt` |
| **Q-4** | `handoff_record_stage3_delivered.json` `yield_statement` | 声明的运行时刻「2026-10-23 **11:52**」与实际自报运行时间（11:46:33–11:46:40）、文件 mtime（11:46:32）、G4 提交时间（11:49:08）均冲突 | 改为实际运行时刻（≈11:46）或删去分钟级时间；HEAD 值 605f960 正确、无需改 |

**非阻断观察（不必本轮修）**：① `verify_t17_blob_identity.py` 是「先打印后写 JSON」且无打印兜底，R-1 路径没有 CLI 级回归，
将来若再引入非 GBK 字符仍会丢 JSON；② 执行器 `WT` 硬编码（§5 注意事项）；③ prep 目录 `hashes_sha256.txt` 自 F2 起过期。

## 7. 边界与未做项

- 未执行任何硬件阶段；未运行重型综合/实现/仿真；未改 dbdf 任何被审文件（唯一例外是 §5 披露的执行器误写，已删除还原）；
  未改主仓 `verification/handoff_check.py`（其 mtime 仍是 2026-10-19 21:27）。
- 全部证据在本目录：`cmd/`（逐条 stdout/JSON/退出码汇总 `exit_codes*.txt`）、`clonet/`（传输克隆）、`selftest_fixtures/`、
  `oldf77f363/`（旧版工具反例）、`mutations/`（3 个突变体与手工直跑输出）、`noreconf/`、`noreconf_fixtures/`、
  `check4.py`/`check5.py`/`check7.py`/`summary.py` 与 `cmd/*.out.txt`。
- 本报告不代表阶段3 颜色通过、G3/G4/G5、任务验收或独立审查以外的任何结论。