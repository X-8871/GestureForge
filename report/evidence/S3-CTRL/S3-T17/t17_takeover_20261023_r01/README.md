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

## 4. 哈希口径与 CRLF 修正（本轮实查发现的缺陷，已修）

- **必读前提（评审 N-4）**：`hashes_sha256.txt`、`manifest.json` 的 `inputs[].sha256`、以及
  `t17_artifacts_verified.json` 的 `sources_referenced[].sha256` 一律按 **git blob（LF）字节**计算。
  本仓库系统级 `core.autocrlf=true` ⇒ 按**工作区**口径复核必须 `git -c core.autocrlf=false clone`
  （或 `git cat-file blob <rev>:<path>`），否则克隆工作区为 CRLF、与记录哈希全部不匹配
  （评审实测 `git clone --no-local` 后 45/45 MISMATCH）。**DSH 已决定暂不为本三范围加 `.gitattributes -text`**，
  故该参数是复核的必读前提而非可选建议。
- **发现**：C1 提交（`900cd0a`）后实查发现 2 个文件「提交内 blob 字节 ≠ 记录哈希字节」——
  `t17_color_retest_prep_.../manifest.json`（Python 文本模式写入产生 CRLF）与本目录 `hashes_sha256.txt`
  （PowerShell 显式 CRLF 写入）；原始比对输出保留在 `blob_byte_identity.txt`（`MISMATCH_COUNT=2`，**失败证据不删**）。
  同时发现两处**历史输入**在两种口径下哈希不同：`t05_stage3_closeout_20261022_r01/manifest.json`、
  `t05_color_msb_missing_20261022_r01/manifest.json`——说明该风险在本仓库确实存在。
- **修正**：本轮新产物（`report/evidence/S3-T17/**`、`report/evidence/S3-CTRL/S3-T17/**`、`scripts/stage3_t17/**`）
  统一为 **UTF-8 无 BOM + LF**；打包/判定/前置脚本改为显式 `newline="\n"` 写入；清单与哈希清单按 LF 口径重算。
- **复核命令（任何人可复跑，无需 CRLF 敏感的工作区）**：
  ```bash
  git -C D:/codex-worktrees/dbdf cat-file blob <commit>:report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/manifest.json | sha256sum
  ```
  或用 `git -c core.autocrlf=false checkout` 导出副本后按 `hashes_sha256.txt` 逐项校验。
- **建议（超出本阶段允许范围，未自行执行）**：若需第三方**工作区**口径复核，应由持有相应写权的一方为
  `report/evidence/S3-T17/**`、`report/evidence/S3-CTRL/S3-T17/**`、`scripts/stage3_t17/**` 增加
  `.gitattributes` 的 `-text` 条目（与仓库既有 S2A 各段做法一致）。

## 5. 检查项 a 与交付态复核（评审 N-3 修正后）

- `handoff_record_stage3_r01.json` 的 `base_commit` 是「**起始提交**」`f94c25f`；`handoff_check.py` 的检查项 a 按
  *前缀匹配 HEAD*，因此在 HEAD 已推进（`900cd0a` 及以后）后再用该 record 复跑会判 FAIL ——
  **这是设计行为（该 record 记录接管时刻）**。
- **交付态复核（评审 N-3 关闭，但只在该次运行的 HEAD 上成立）**：交付态使用
  `handoff_record_stage3_delivered.json`，其 `base_commit` 是**运行时刻**的冻结提交（现为 `605f960`，即 F3）。
  实测命令、真实退出码与输出见 `report/evidence/S3-T17/t17_quickfix_20261023_r01/g4_handoff_delivered.{json,stdout.txt}`
  与 `…/t17_fix_20261023_r01/handoff_delivered_readonly.{json,stdout.txt}`（**exit 0**）。
  **该 exit 0 不是恒久成立**：在别的冻结 HEAD（如 `f77f363`）复跑，因检查项 a 为**前缀比较**，得
  **exit 1（PASS 7 / FAIL 1(a) / SKIP 1）** —— 这是设计行为，不是哈希或状态不一致。
  「运行时刻 HEAD + 前缀语义」的说明写在 record 的 `yield_statement` 内。**不要新增 record 字段**：
  `handoff_check.py` 对未知字段直接判 **exit 2**（本轮一度如此，已修正并复跑得 exit 0）。
- 若 HEAD 前进：把该 record 的 `base_commit` 更新为**当前 HEAD** 后再跑；
  **推荐**由持有 `verification/handoff_check.py` 写权的一方把检查项 a 改为祖先判定（本阶段无权改主仓工具）。
- 本目录 `blob_byte_identity_final.json` 的 F 证明对应内容提交 `9d5c638`（`BLOB_BYTE_IDENTITY_OK`，42/0/0）；
  自证提交 `525e4f35` 的即时自证亦为 OK（45/0/0，见 `selfproof_hashes_sha256.txt`）。修复轮见
  `report/evidence/S3-T17/t17_fix_20261023_r01/`。

## 6. 限制

- 只读机器核验，不代表 G0/G4/G5、接口语义、测试或实物验收。
- 未做任何电气测量；上次「DVP 字节 MSB 丢失」的**电气定位仍未证**（数值自洽已由 DSH 项目总控复核）。
- 阶段 B（到货后实测）未执行：需 Wong 开工信号 + 硬件窗口书面确认，二者未到不动板。