# S3-T17 阶段A 快修轮：提交后复跑（G4，冻结提交 F3 `605f960`）

- 本文件在 **F3 提交之后**生成；F3 内容见 `quickfix_record.md`。所有命令**均不设置 `PYTHONUTF8`**、
  并把 stdout **重定向到文件**（即评审指出的常规调用方式），逐条记录**真实退出码**与 `--json-out` 是否落盘。
- 本轮**未接触硬件**；颜色子项仍 `DEFERRED_PENDING_MODULE`。

## 1. 验收表（README 命令逐条复跑）

| # | 命令（要点） | 真实退出码 | JSON 落盘 | 证据文件 |
|---|---|---|---|---|
| 1 | `bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_quickfix_preflight_20261023_r01` | **0**（`T17_PREFLIGHT_EXIT=0`） | 是 | `../t17_quickfix_preflight_20261023_r01/preflight.json` |
| 2 | `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest --repo-root … --fixture-dir <tmp绝对路径> --json-out …` | **0**（`SELFTEST_PASS`，7 夹具 + **2 CLI 回归**全匹配） | 是 | `g4_selftest.json/.stdout.txt` |
| 3 | `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame <归档整帧> --json-out …` | **1**（`DEFECT_REPRODUCED`） | **是** | `g4_archived.json/.stdout.txt` |
| 4 | `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame <只修一路夹具> --json-out …` | **3**（`INCONCLUSIVE_ATYPICAL`） | **是** | `g4_partial.json/.stdout.txt` |
| 5 | `python -B scripts/stage3_t17/check_t17_preflight.py --worktree … --json-out …` | **0**（`OFFLINE_GO`，关系 descendant） | 是 | `g4_preflight.json/.stdout.txt` |
| 6 | `git -c core.autocrlf=false clone --shared --no-checkout -b codex/stage3-video D:/FPGA_Competition <空目录>` → `python -B <空目录>/scripts/stage3_t17/verify_t17_blob_identity.py --repo-root <空目录> --commit HEAD --json-out …` | **0**（83 文件 / 0 不一致 / 0 缺失 / 0 CRLF，`BLOB_BYTE_IDENTITY_OK`） | 是 | `g4_clone_with_autocrlf_off.json/.stdout.txt` |
| 6b | 同上但**不加** `-c core.autocrlf=false`（如实对照） | **1**（83/83 不一致、83 含 CRLF） | 是 | `g4_clone_without_flag.json/.stdout.txt` |
| 7 | `python -B D:/FPGA_Competition/verification/handoff_check.py --worktree … --record …delivered.json` | **0**（json 与文本均 0；`HANDOFF_OK`，PASS 8 / FAIL 0 / SKIP 1） | 是 | `g4_handoff_delivered.json/.stdout.txt` |
| 8 | 自证（对内容提交 F3）：`verify_t17_blob_identity.py --repo-root <dbdf> --commit 605f960`（排除 G4 新增产物） | 见 `g4_blob_identity_f3.json` | 是 | `g4_blob_identity_f3.json` |

要点：**第 3/4 项在修复前会崩溃且分别丢 JSON／给出错误退出码 1**（见 `R2a_repro.*`、`R2b_repro.*`），
现在语义正确（1 = 复现缺陷、3 = 非典型）且 JSON 均落盘。

## 2. `--selftest` 的两条 CLI 级回归（评审 R-2 关闭要求③）

子进程 + 管道 stdout + `PYTHONIOENCODING=gbk`（比"不设 PYTHONUTF8"更严），断言真实进程码与 JSON 落盘：

| 回归 | 期望退出码 | 实际退出码 | JSON 落盘 | 判定 verdict | 匹配 |
|---|---|---|---|---|---|
| `cli_archived_defect_exit1_json`（归档缺陷帧） | 1 | **1** | **True** | `DEFECT_REPRODUCED` | True |
| `cli_partial_blue_only_exit3_json`（只修一路） | 3 | **3** | **True** | `INCONCLUSIVE_ATYPICAL` | True |

（明细见 `g4_selftest.json` 的 `cli_regressions` 字段。）

## 3. 本轮自查中发现并修正的**新**缺陷（如实登记）

**交付态 record 字段越界 → `handoff_check` 判 `exit 2`**：提交 F3 时我给
`handoff_record_stage3_delivered.json` 增加了 `verification_head`/`verification_time_utc8`/`base_commit_semantics`
三个**非规范键**，而 `handoff_check.py` 对未知字段直接报 `HANDOFF_INPUT_ERROR`（**exit 2**，不是 0/1），
即该 record 一度**不可用于复核**。已在 G4 修正：只保留 13 个规范键，把「运行时刻 HEAD + 前缀语义」写进
`yield_statement`；修正后 json/文本两次复跑均 **exit 0**（PASS 8 / FAIL 0 / SKIP 1）。
takeover `README.md` §5 已记入该教训（**不要新增 record 字段**）。

## 4. 未做项与边界

- 未动硬件：无 JTAG/COM4/hw_server/位流加载/烧录；四个硬件阶段（`link`/`baseline`/`bars`/`restore`）全未执行；
  阶段B 仍等 **Wong 开工信号 + Codex 书面让出**（013/014 未见回执）。
- 未改主仓 `verification/handoff_check.py`（检查项 a 仍为前缀比较）；未加 `.gitattributes`；未做独立审查。
- 本记录不代表阶段A 通过、颜色通过或 G3/G4/G5；复审由 DSH 项目总控另派。