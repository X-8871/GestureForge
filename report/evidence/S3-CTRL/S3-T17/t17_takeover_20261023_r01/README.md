# S3-T17 阶段3 工作树接管证据（OFFERED→CLAIMED，2026-10-23）

- 任务：`task-17`（共享看板 rev2，owner `stage3-lead`）；本包对应阶段 A-① 接管核验。
- 工作树/分支/HEAD：`D:\codex-worktrees\dbdf` / `codex/stage3-video` / `f94c25ff2bd539e2ca45b450334ddc8bb8cde6e7`。
- **`handoff_check --claim` 真实结果：`HANDOFF_OK`（PASS 9 / FAIL 0 / SKIP 0），退出码 0**（`--json` 与文本两种模式均 0）。
- 工具：`python -B D:\FPGA_Competition\verification\handoff_check.py --worktree D:\codex-worktrees\dbdf --record ... --claim --json`。

## 1. 接管前置核验（机器可核）

| 项 | 结果 |
|---|---|
| 工作树/分支/HEAD | 与 record 声明逐项一致（检查 a PASS） |
| `index.lock` | 由 `git rev-parse --git-path index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/FPGA_Competition1/index.lock`，**不存在**（b PASS） |
| 未提交改动 | 接管时 2 项：`?? NA/`、`?? clockInfo.txt`，均登记归属（c PASS） |
| 重型进程 | `vivado/xsim/xelab/xvlog/hw_server/cs_server/xsdb` 全部未发现（d PASS） |
| 心跳 | `2026-10-23 09:56`（UTC+8），距核验时刻 1.2 分钟（e PASS） |
| 状态机 | `status=OFFERED`，`--claim` 接管条件满足（f PASS） |
| 证据入口 | 本目录含 `manifest.json`（g PASS） |
| 允许范围 | 9 条范围，4 条拟改动路径全部在范围内、无越界（h PASS） |
| 让出契约 | `yield_statement`/`next_owner` 非空非占位（i PASS） |

另核：`git worktree list` 显示本树 `f94c25f [codex/stage3-video]`；3121 端口无监听（接管时）。

## 2. 让出链（据实登记，含两处过期声明）

1. Codex 阶段三总控 2026-10-21 15:05 曾把本树 OFFERED 给 DSH；
2. Codex 阶段三总控 2026-10-21 19:53 以 `S3CTRL-20261021-003-handoff-to-dsh-stage3.md` + 提交 `29c7cf0`（20:01）再次 OFFERED 并声明已停写；
3. DSH 阶段三总控 2026-10-21 21:36（提交 `22b8b64`）CLAIMED→IN_PROGRESS，工作至 2026-10-22 15:19（`f94c25f`），该轮交接行状态为 **DONE**（上一轮任务收尾，颜色子项 `DEFERRED_PENDING_MODULE`）；
4. 该轮写入方已停写、无活动写入者：心跳 `2026-10-21 23:35` 已超时、无 `index.lock`、无重型进程；
5. DSH 项目总控（主 `.codex/STATE.md` 写权持有方）2026-10-23 把本树登记为 **OFFERED 待认领** 并派新任务卡 `task-17` ⇒ 本轮由新任务卡重开，起始状态取 OFFERED，DSH 阶段3 总控独占写入。

**如实登记的两处不一致/过期声明**（不改写历史）：
- 本树交接行上一轮状态写 `DONE`，主 STATE 与本 record 用 `OFFERED`（前者=上一轮任务状态，后者=本轮治理层登记）；
- 主 `.codex/STATE.md` 阶段3 行记 `HEAD 29c7cf0` 与「无人 CLAIM」，与实际不符：**实际 HEAD 为 `f94c25f`**，且第 3 步确已 CLAIM。

## 3. 本包文件

| 文件 | 说明 |
|---|---|
| `handoff_record_stage3_r01.json` | 接管 record（11 字段折算的 JSON；含完整让出链与不一致登记） |
| `handoff_check_claim.json` / `.stdout.txt` | `--claim` 的 JSON 与文本原始输出（真实退出码 0） |
| `handoff_check_confirm.json` / `.stdout.txt` | 本轮全部写入完成后对**最终树状态**的复核运行（真实退出码见 `exit_codes.txt`） |
| `exit_codes.txt` | 各次运行的**真实**退出码 |
| `git_facts.txt` | 工作树/分支/HEAD/锁/worktree 列表/未提交改动 原始输出 |
| `manifest.json` | 输入哈希、命令、核验事实、限制 |
| `hashes_sha256.txt` | 本目录全部产物哈希（生成于最后一次写入之后） |

## 4. 限制

- 只读机器核验，不代表 G0/G4/G5、接口语义、测试或实物验收。
- 未做任何电气测量；上次「DVP 字节 MSB 丢失」的**电气定位仍未证**（数值自洽已由 DSH 项目总控复核）。
- 阶段 B（到货后实测）未执行：需 Wong 开工信号 + 硬件窗口书面确认，二者未到不动板。