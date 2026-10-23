# S3-T17 关闭项：提交后复跑（G5，冻结提交 F4 `4939dfa`）

- 全部命令**均不设置 `PYTHONUTF8`**（执行器自带 `export PYTHONUTF8=1` 者除外，属其自身行为）；stdout 重定向到文件。
- 本轮**未接触硬件**；颜色子项仍 `DEFERRED_PENDING_MODULE`；本记录不代表阶段A 通过或独立审查通过。

| # | 项目 | 命令（要点） | 真实退出码 | 结论 / JSON |
|---|---|---|---|---|
| 1 | **Q-A 护栏拒绝**（提交后复测） | `cd D:/FPGA_Competition && bash <dbdf>/scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_guard_probe_g5` | **2** | `T17_GUARD_CWD_MISMATCH=1`、`T17_RUN_ABORTED=1`；**dbdf 内未产生任何文件**（该 RunId 目录不存在） |
| 2 | 判定器自测（含 2 条 CLI 回归） | `python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest …` | **0** | `SELFTEST_PASS`（`g5_analyzer_selftest.json`） |
| 3 | **自证工具 CLI 回归**（含旧形态突变对照） | `python -B scripts/stage3_t17/verify_t17_blob_identity.py --selftest …` | **0** | `SELFTEST_PASS`：`cli_verify_gbk_exit0_json` rc=0/JSON=True；`mutant_old_form_detected` **rc=1/JSON=False**（`g5_verify_selftest.json`） |
| 4 | 离线前置（切片 HEAD） | `python -B scripts/stage3_t17/check_t17_preflight.py --worktree <dbdf>` | **0** | `OFFLINE_GO`，HEAD=`4939dfa`，基线关系 descendant |
| 5 | **克隆自证**（`-c core.autocrlf=false`） | clone F4 后 `verify_t17_blob_identity.py --repo-root <克隆> --commit HEAD` | **0** | **120 文件 / 0 不一致 / 0 缺失 / 0 CRLF**，`BLOB_BYTE_IDENTITY_OK`（`g5_clone_with_autocrlf_off.json`） |
| 6 | **交付态只读复核**（record 绑定 F4） | `handoff_check.py --worktree <dbdf> --record …handoff_record_stage3_delivered.json` | **0**（json 与文本） | `HANDOFF_OK`，PASS 8 / FAIL 0 / SKIP 1；record 的运行时刻已改为该次运行的**实际值**（check-e 自报） |

**关于「运行时刻」（Q-4 后续）**：交付态 record 的 `base_commit` 现绑定 **F4 `4939dfa`**，其 `yield_statement`
记录本次运行时刻（取自 `handoff_check` 自身 check-e 输出，可逐字复核）。HEAD 再前进后（例如本次 G5 提交后）
复跑该 record 会因检查项 a 的前缀比较得 **exit 1（PASS 7 / FAIL 1(a) / SKIP 1）**——这是**设计行为**，
不是哈希或状态不一致；复跑前把 `base_commit` 更新为当前 HEAD（或由主仓写权方把检查项 a 改为祖先判定）。

**U+21D2 口径（保持 `task-20` 结论）**：工具源码与工具 README **0 处**；证据/文档正文按原样保留中文箭头，
不追求「全部替换」——只有**代码**里的该字符会造成 GBK 崩溃（R-1/R-2）。

**未做项**：四个硬件阶段（`link`/`baseline`/`bars`/`restore`）全未执行；阶段B 仍等
**Wong 开工信号 + Codex 书面让出**；未改主仓 `handoff_check.py`；未做独立审查。