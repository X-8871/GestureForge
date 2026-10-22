# 阶段6 状态入口（w6 / stage6-interact-prep）

更新：2026-10-22 19:26（UTC+8）。按 `AGENTS.md` 与主 STATE 恢复；**本文件是阶段6 工作树专属状态**，主状态 `D:\FPGA_Competition\.codex\STATE.md` 只读。阶段技术事实以本文件与本树证据为准。

## 阶段目标与范围

- 目标：稳定手势判定 → HDMI 切图/界面/显示状态；冻结多框目标选择、丢失与重获、稳定窗口、保持期触发语义、冷却、再触发条件、无手/未知/超时错误与恢复行为（计划 L102–L108）。
- 范围：`w6` 独占写入；G0 与行为表 → 状态机实现与确定性测试（6-B/6-C）→ 无摄像头两级联调（6-D）→ 真摄像头验收（6-E，延期）。
- 硬边界：**无硬件授权**——不碰板卡/JTAG/COM4/`hw_server`/HDMI 实物/摄像头，不烧录；`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读；两个 mailbox 只读；不 push；同时只跑一个重型任务。
- 注入/回放结论适用范围仅限回放/注入输入；真手势验收延期至摄像头到货。

## 上游绑定与冻结状态（2026-10-22 核实）

- 已冻结、可直接引用：`S2A-T01` 规格（`7c2c8684…`，类别顺序/`score` 0.25/NMS 0.45/≤15 框/同分顺序）、阶段计划 L102–L108、`D2`（`df95a843…`，`no_hand` 非第六类）、`D6`（`735cbc78…`）。
- **未冻结（仅草案/隔离使用）**：阶段4 `s4a_stage4_g0_fields.json`（`DRAFT_NOT_FROZEN`，提交 `73c3dad` 版本 `3524d02a…`）；阶段5 `S5A v2`（`ca5968d4…`，离线定稿未验收）。
- **本轮并发写入事实**：`w4` HEAD 仍 `73c3dad` 但两份阶段4 文件已被未提交修改（工作副本 `3524d02a…`→`657ea2fb…`），并新增 S4B 共享输入契约/S4-C02 证据/`s4_inject_frame.c`；`w5` HEAD 由 `e4533e1`→`875e487`（引用的三份 w5 文件哈希未变）。
- **上游起草方为本阶段独占写入方**：阶段4/阶段5 接口变更须回本阶段 G0 复核；未冻结依赖阻断集成验收。

## 本轮已完成（S6-A，G0 包 + 行为表 v1）

- `docs/stage6/S6A_stage6_g0_behavior_spec_v1.md`（人读 G0 包与行为表 v1，18 节）、`docs/stage6/s6a_stage6_g0_behavior_v1.json`（机器可读 `S6A-G0-v1`：28 行行为、24 个参数/指标、15 条迁移、9 条硬不变量、5 类动作映射）。
- `verification/s6_g0_selfcheck.py`：10 项自检（文档↔JSON 双向标识一致、待批准纪律、五类映射、H-1..H-9、20 例人工手算边界复算、11 项上游哈希复算、禁止声明窄口径扫描）→ 真实退出码 **0**、`ALL_PASS`。
- 关键语义（v1 声明、待批准）：`ACTION_SUBMITTED`（提交成功）≠ `ACTION_EFFECTIVE`（实际生效）；**一次获取只触发一次**（冷却结束后即使仍保持稳定也不触发，M15 路径不是新获取），唯一二次触发来源=新获取；五类动作映射为「设置到具名显示状态」的幂等提案；时间边界除过期用严格 `>` 外全部含等号；超时/失踪计时按单调时钟；`NO_HAND` 合法零框、未知拒绝不得由 `class_id ∈ 五类` 自证。
- 全部阈值与指标（`T6-A01/A02/A03/C01/S01..S04/L01/L02/K01/J01/U00_W/U00_N/U01/P01..P05/STALE_LIMIT/01/02/03`）= `PENDING_APPROVAL`，责任人=项目总控转呈 Wong。
- 首次自检的真实失败（HC-03 手算下界记错、w4 工作副本漂移、C10 否定语境误报）已修复并保留记录；最终态 `ALL_PASS`。

## 未决与阻塞

- **BLOCKED**：阶段6 集成验收依赖（阶段4/阶段5 接口均未冻结，且阶段4 仍在变动）；阶段5 显示侧新增 HUD 字段（提案，需协调）；真摄像头验收（摄像头不可用）；独立 Reviewer（本会话委派深度已用尽，无法创建子代理）。
- **NOT_RUN**：6-B 状态机实现、6-C 确定性测试矩阵、6-D 两级联调、≥30 分钟回放稳定性、`T6-01/02/03` 任何统计。
- 待 Wong/项目总控：`U6-01..U6-11`（三项目标值与样本数、触发语义确认、全部时间/匹配参数、阶段4/5 接口冻结、HUD 字段、动作映射、`T6-A03` 交互延迟上限、`STALE_LIMIT` 正式冻结）。

## 证据入口

- 本轮：`report/evidence/S6-A/s6a_g0_20261022_r01/`（`delivery_manifest.json`、`inputs_manifest.json`、`upstream_bindings.json`、`hand_computed_cases.json`、`coverage_matrix.json`、`selfcheck_result.json`、`limitations_not_executed.json`、`hashes_sha256.txt`、`S6A_run_summary.md`）。
- 缓存：`tmp/6/S6-A/s6a_g0_20261022_r01/`（不入库）。
- 规格：`docs/stage6/`；自检：`verification/s6_g0_selfcheck.py`。

## 下一步

1. 项目总控转呈 Wong 批准 `U6-01..U6-11`（至少先批三项目标值、时间参数与动作映射）。
2. 批准后开 S6-B：实现纯核心状态机 + 动作执行层隔离 + 虚拟单调时钟/JSONL 驱动与断言（预期序列独立推导）。
3. 并行（不依赖批准）：把行为表转成 6-C 用例矩阵骨架与注入序列样例；等待阶段4 冻结接口后做 6-D。
4. 独立 Reviewer 须由项目总控在后续轮次安排（本会话不可创建子代理）。

## 11 字段交接行（2026-10-22 19:26）

任务=`S6-A 阶段6 G0 包 + 交互行为表 v1（含阶段6 专用 STATE）` | 负责人=`DSH 阶段6 总控 stage6-lead` | 工作树/分支=`D:\codex-worktrees\w6` / `stage6-interact-prep` | 起始提交=`d8bc70e43572a8e44ddcd4b3489166e28a1c6151` | 允许修改范围=`w6 工作树内 docs/stage6/**、verification/s6_g0_selfcheck.py、report/evidence/S6-A/**、.codex/STATE.md、tmp/6/**`（`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读） | 未提交改动归属=`本轮随本行同批提交（提交哈希见 git log -1 -- .codex/STATE.md）；w4 未提交改动归阶段4 窗口、w5 归阶段5 窗口、dbdf 2 项散落件归 DSH 阶段三总控，本阶段均未触碰` | 让出声明=`未让出：w6 写权仍由 DSH 阶段6 总控独占；无 OFFERED` | 心跳(UTC+8)=`2026-10-22 19:26` | 证据入口=`report/evidence/S6-A/s6a_g0_20261022_r01/`（`selfcheck_result.json`=ALL_PASS/exit0、`coverage_matrix.json`、`limitations_not_executed.json`） | 恢复命令=`git -C D:/codex-worktrees/w6 status --short; git -C D:/codex-worktrees/w6 log --oneline -3; python -B D:/codex-worktrees/w6/verification/s6_g0_selfcheck.py --json D:/codex-worktrees/w6/docs/stage6/s6a_stage6_g0_behavior_v1.json --doc D:/codex-worktrees/w6/docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r01/hand_computed_cases.json --upstream D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r01/upstream_bindings.json --out D:/codex-worktrees/w6/tmp/6/S6-A/s6a_g0_20261022_r01/selfcheck_rerun.json --project-root D:/codex-worktrees/w6` | 状态/下一接手方=`IN_PROGRESS（S6-A DONE，待 Wong 批准阈值后开 S6-B）/ DSH 阶段6 总控` |

## 环境与恢复要点

- 工作树干净（开工核验）；`index.lock` 路径由 `git rev-parse --git-path index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/w6/index.lock`；失联判定须「心跳超时 + 无重型进程 + 无 index.lock」三者同时成立。
- Python `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe`（3.12.10）；git 2.56.0.windows.2；`TEMP/TMP=D:\tmp`。
- 恢复时写新 RunId 到 `tmp/`；**不得**覆盖 `s6a_g0_20261022_r01` 的任何证据；不得在正式测试集上调整任何阈值。