# S3-T17 阶段A 快修记录（task-19：R-1/R-2 + N-1/N-3 + README）

- 输入：快修复审 `report/evidence/CTRL-DSH-HANDOFF/reviews/S3_T17_FIX_20261023_r01/REVIEW_REPORT_S3_T17_FIX_r01.md`
  （被审 F2 `60b00de` / G3 `f77f363`）判 `CHANGES_REQUIRED`；原三阻断 B-1/B-2/B-3 已被复审确认实质关闭。
- 执行方：DSH 阶段3 总控（`stage3-lead`，看板 `task-19`）。**本轮未接触硬件**。
- 复现与修复的时点：复现均在 `f77f363`（含崩代码）；修复后实测在工作树（F3 提交前）完成，
  **不带 `PYTHONUTF8`、stdout 重定向到文件**（即评审的常规调用方式）；提交后的复跑见 G4 目录
  `report/evidence/S3-T17/t17_quickfix_20261023_r01/reverify_after_fix.md`。

## 一、R-1/R-2 复现（失败证据原样保留）

| 编号 | 命令（不带 PYTHONUTF8，重定向） | 真实退出码 | JSON 落盘 | 现象 |
|---|---|---|---|---|
| R-1 | `python -B scripts/stage3_t17/verify_t17_blob_identity.py --repo-root dbdf --commit HEAD --json-out <f>` | **1** | **否** | `UnicodeEncodeError: 'gbk' codec can't encode character '\u21d2'`（第 75 行 `CORE_AUTOCRLF` 打印）；退出码 1 与本工具 MISMATCH 同值 => 易被误读为哈希失配 |
| R-2a | `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame <归档缺陷帧> --json-out <f>` | **1**（巧合正确） | **否** | 崩在 `print("不可辨位：…")`（`WHITE_BIT_NOT_SET（白条字段位为 0 => 缺位）`） |
| R-2b | 同上，`--frame <只修蓝夹具 fixture_C_blue_only.bin>` | **1（应为 3）** | **否** | **把「非典型」误报成「复现缺陷」** |

原始输出（GBK 编码，按原样保留）：`R1_repro.stdout.txt`、`R2a_repro.stdout.txt`、`R2b_repro.stdout.txt`
（对应的 UTF-8 可读副本：`R1_repro.utf8.txt`、`R2a_repro.utf8.txt`、`R2b_repro.utf8.txt`，仅转码不改内容）；
对照（带 `PYTHONUTF8=1` 时的正确语义）：`R2b_with_utf8_expected.json`（verdict=`INCONCLUSIVE_ATYPICAL`，退出码 3）。

## 二、修复（三条同时做，互为兜底）

1. **入口强制 UTF-8 + LF**：四个 Python 工具（`analyze_…`、`verify_…`、`check_…preflight`、`make_…manifest`）
   模块级调用 `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace", newline="\n")`
   => 即使显式设置 `PYTHONIOENCODING=gbk` 也被覆盖，管道/重定向下不再崩，且输出为 UTF-8+LF。
2. **代码内不再含 U+21D2**：`scripts/stage3_t17/**` 内 `=>` 全部换为 ASCII `=>`（实查剩余 0 处，`.pyc` 除外且已清理）。
   说明与**更正（评审 Q-3）**：一次机械替换波及受管范围内 22 个文件；发现后我对其中 **17 个证据文件**执行了
   `git checkout` 并复核为逐字节回到提交态（该 17 个文件的 `CONTENT_DIFF_COUNT=0` 成立），但**另有 4 个证据文件
   + `.codex/STATE.md` 未还原**：takeover README(2 行)、prep README(9 行)、`t17_judgement_table.json`(9 行)、
   `t17_judgement_table.md`(2 行) 与 `.codex/STATE.md`(8 行) 的**纯机械 `⇒`→`=>` 行**被一并带走。
   因此原文「已提交证据逐字节还原、`CONTENT_DIFF_COUNT=0`」**整体不成立**，已按复审要求选 **(a)**：
   在 `task-20` 中把这些**纯机械替换行**用 `git checkout` 逐行还原回提交字节，本轮**有意修改**的行另附逐行 diff
   （见 `report/evidence/S3-T17/t17_closeout_20261023_r01/q3_mechanical_restore.md`）。
3. **JSON 先落盘、打印失败不影响结论**：`analyze_…` 先写 `--json-out`，再打印人类摘要；
   打印阶段异常被捕获并记为 `SUMMARY_PRINT_FAILED=…`，不改退出码、不丢 JSON。

## 三、修复后实测（工作树，不带 PYTHONUTF8，重定向）

| 项 | 命令 | 真实退出码 | JSON 落盘 |
|---|---|---|---|
| 判定器自测（含新增 CLI 回归） | `analyze… --selftest --repo-root … --fixture-dir <tmp绝对路径>` | **0** | `selftest_after_fix.json` |
| 归档缺陷帧 | `analyze… --frame <bars_raw_frame_full.bin> --json-out …` | **1** | **是**（`fix_archived.json`，`DEFECT_REPRODUCED`） |
| 只修一路（应为非典型） | `analyze… --frame <fixture_C_blue_only.bin> --json-out …` | **3** | **是**（`fix_partial.json`，`INCONCLUSIVE_ATYPICAL`） |
| 自证工具（工作树当时有未提交改动） | `verify… --repo-root dbdf --commit HEAD --json-out …` | **1** | **是**（`fix_verify.json`；不一致=5 为**本轮自身未提交改动**，非崩溃；提交后复跑见 G4） |

`--selftest` 新增的两条 **CLI 级回归**（`cli_regressions`，子进程 + 管道 stdout + `PYTHONIOENCODING=gbk`）：
- `cli_archived_defect_exit1_json`：期望 exit 1，实际 **1**，JSON 落盘 **True**，匹配 **True**；
- `cli_partial_blue_only_exit3_json`：期望 exit 3，实际 **3**，JSON 落盘 **True**，匹配 **True**。
（旧版本这两条都会崩溃；但**覆盖边界要如实说明**（评审 Q-5）：这两条回归断言的是「GBK 下**真实退出码 + JSON 落盘**」，
而**不是**「删掉 `_force_utf8_streams()` 就必然失败」——第三重防护（JSON 先落盘 + 打印 try/except）会在缺少入口兜底时
仍然兜住崩溃，使 `--selftest` 依旧 rc=0。故：`analyze…` 的 CLI 回归覆盖「结论/JSON 在 GBK 下不受损」，**不覆盖**
「入口兜底存在性」；后者由 `verify_t17_blob_identity.py` 的新回归覆盖（该工具**没有**第三重防护，旧形态必崩，见 §五）。）

## 四、文本级处理

- **N-1（依据不实，已改正；Q-1/Q-2 再更正）**：**可复现口径** —— dbdf 内 `cmos_8_16bit*.v` 实查 **47 份**
  （45 份恰为同名 `cmos_8_16bit.v`，另 `cmos_8_16bit_ref.v`、`cmos_8_16bit_gh.v` 各 1），**47/47 全部含**
  `pdata_o <= {pdata_i_d0,pdata_i}`；复现命令：dbdf 根执行
  `find . -name 'cmos_8_16bit*.v' -not -path './.git/*' | wc -l` ⇒ **47**，再逐份 grep 该语句。
  其中**已入库参考 1 份**：
  `report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v`
  （blob SHA-256 `08a325356fdb46fcbd87e1b594a2b5d3c30954b68d18e4ea22d36e914cd414b9`，3318 B）内的拼接语句。
  **行号更正（Q-1）**：该文件**不引用行号**——它含混合行尾，按 `\n` 计 **83 行**、Python `splitlines()` 计 **167 行**，
  原文的『第 157 行』即由该计数假象产生；按 `\n` 行计该语句在第 **79** 行。此前「盘上 56 份」含**跨树**计数且未写命令/范围，**不可复现**，已作废。
  `byte_order_evidence` 第 4 条已从「推断」升级为「**厂商源码 + 网表双重依据**」并给出路径/哈希；
  `naming_limitation` 保留（命名仍不宜直接引用），但其依据表述已改正；`t17_artifacts_verified.json`
  的 `sources_referenced` 新增该校验条目。
- **N-3（写明运行时刻）**：takeover `README.md` §5 与 `handoff_record_stage3_delivered.json`
  新增 `verification_head=60b00de` / `verification_time_utc8` / `base_commit_semantics`：
  交付态 exit 0 **只在运行时刻 HEAD=60b00de 成立**；在 `f77f363` 复跑因检查项 a 前缀比较得
  exit 1（PASS 7/FAIL 1(a)/SKIP 1），属设计行为；复跑前须更新 `base_commit`。
- **README（纯克隆依赖）**：`scripts/stage3_t17/README.md` 新增「编码前提」（工具已强制 UTF-8，无需 `PYTHONUTF8`）
  与「纯克隆的已知依赖」：全新克隆缺 7 件未入库 `tmp/**` 冻结产物 => `preflight` 返回 1（失败项为「缺产物」，
  **不是** HEAD 判据问题），并给出只看 HEAD 判据的用法。

## 五、边界与未做项

- 未动硬件：无 JTAG/COM4/hw_server/位流加载/烧录；四个硬件阶段（`link`/`baseline`/`bars`/`restore`）全未执行。
- 未改主仓工具 `verification/handoff_check.py`；未加 `.gitattributes`（DSH 决定）；未做独立审查。
- 本记录不代表阶段A 通过、颜色通过或 G3/G4/G5；颜色子项仍 `DEFERRED_PENDING_MODULE`。