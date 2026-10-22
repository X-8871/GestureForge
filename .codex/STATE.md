# 阶段6 状态入口（w6 / stage6-interact-prep）

更新：2026-10-23 01:35（UTC+8）。按 `AGENTS.md` 与主 STATE 恢复；**本文件是阶段6 工作树专属状态**，主状态 `D:\FPGA_Competition\.codex\STATE.md` 只读。阶段技术事实以本文件与本树证据为准。

## 阶段目标与范围

- 目标：稳定手势判定 → HDMI 切图/界面/显示状态；冻结多框目标选择、丢失与重获、稳定窗口、保持期触发语义、冷却、再触发条件、无手/未知/超时错误与恢复行为（计划 L102–L108）。
- 范围：`w6` 独占写入；G0 v1.3 复评 → 状态机实现与确定性测试（6-B/6-C）→ 无摄像头两级联调（6-D）→ 真摄像头验收（6-E，延期）。
- 硬边界：**无硬件授权**——不碰板卡/JTAG/COM4/`hw_server`/HDMI 实物/摄像头，不烧录；`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读；两个 mailbox 只读；不 push；同时只跑一个重型任务。
- 注入/回放结论适用范围仅限回放/注入输入；真手势验收延期至摄像头到货。

## 上游绑定与冻结状态（2026-10-23 核实）

- 已冻结、可直接引用：`S2A-T01` 规格（`7c2c8684…`）、阶段计划 L102–L108、`D2`（`df95a843…`）、`D6`（`735cbc78…`）。
- **未冻结（仅草案/隔离使用）**：阶段4 `s4a_stage4_g0_fields.json`（`DRAFT_NOT_FROZEN`，`73c3dad` 版本 `3524d02a…`）；阶段5 `S5A v2`（`ca5968d4…`，离线定稿未验收）。
- 阶段4/阶段5 接口未冻结 → 阶段6 集成验收依赖 `BLOCKED`；不得据此做集成验收。

## 本轮已完成（S6-A v1.3 / r04 修订，PENDING_REVIEW）

- 针对**第三轮复评** `S6A_r03_20261022_r01`（`CHANGES_REQUIRED`，R3-B01/R3-B02 + N01..N05 + 观察项）按 task-5 逐条关闭（执行方 stage6-lead3）：
  - **R3-B01**：§12 `T6-S02` 行改用「连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`」、`T6-L02` 行改用 `t_now − t_last_target_continues ≥ T6-L02`；§3/§12/§13 给出 `t_last_target_continues` 定义（最近一次 `TARGET_CONTINUES` 成立时刻；被抑制/失败不更新）；JSON 增 `time_anchors` 并同步 M10/B10；自检 **C12 增加禁用标识符扫描**（`matched_frames`/`t_last_match`/`t_submit+`，仅放行邻近标注「已废弃」的历史说明）。
  - **R3-B02**：`predicates.used_by` 与全部 `predicates_used` **全量双向一致**——`B03` 补 `[TARGET_CONTINUES]`、`B17` 补 `[WINDOW_MATCH]`、`TARGET_CONTINUES.used_by` 补 `B14`、`M1.predicates_used` 收敛为仅 `[TARGET_CONTINUES]`；M5/B13 的谓词绑定叙述按 JSON 现状改写（逐字口径见下方「M5/B13 叙述口径」行）。自检 **C12 增加全量双向断言**与 M5/B13 字段现状断言。
  - **M5/B13 叙述口径（R3-B02，与 JSON `predicate_binding_policy.statement` 逐字一致）**：M5 与 B13 只有条件文本 + global_cooldown_gate 绑定，没有 predicates_used 字段。
  - **观察项**：STABLE 定论为「**本次获取内锁存**」——进入后不因 `WINDOW_MATCH` 中断、`score` 跌破 `T6-P02` 或抖动耗尽而退回 `CANDIDATE`；离开路径仅 M2/M10/M5；冷却门开启后下一条窗口推进帧即可触发。写入 §4、JSON `stable_latching`，新增自检 **C17**，登记 `U6-16` 待 Wong/G0 确认。
  - **N01..N05**：H-10 统一 `t_last_submit` 并删除已废弃写法；HC-27 去自比较（改帧时刻序列推导）、HC-28/29 由逐帧 score/几何序列真推导；旧包失败证据由 `verification/s6a_rerun_legacy_failures.py` 用最终脚本重跑（r01/r02/r03）并纳入构建器；coverage C7 样例数 27→29、版本号统一 v1.3/r04；旧哈希成因措辞改为「LF→CRLF + 末尾补 CRLF」。
- 自检加固证明：**先用 r04 加固自检在 r03 的 git 字节上跑出失败（exit 1，失败项 C7/C12/C17）**——C12 一次性汇总报告 R3-B01（文档与样例中的禁用标识符）与 R3-B02（M1 过声明、`TARGET_CONTINUES`/`WINDOW_MATCH` 双向不一致、缺 `predicate_binding_policy`）；C17 报缺 `stable_latching`；C7 报旧样例缺扩宽后的 `t_last_target_continues_ms` 字段名。落盘 `selfcheck_r03_failure.json/.txt`、`r03_package_under_test.json`；再对 r04 跑出 **17 项 `ALL_PASS`**（`selfcheck_result.json` 含完整 C11 清单/STATE 核对）。
- 24 项参数值与批准状态**未改**，全部 `PENDING_APPROVAL`；未在测试集调参；未触碰硬件；S6-B WIP 未提交。

## 未决与阻塞

- **PENDING_REVIEW**：S6-A v1.3 复评由项目总控另派独立 Reviewer；复评通过前不得宣称 G0 通过，也不启动 S6-B。
- **待 Wong/G0 确认**：`U6-16`（STABLE 锁存口径）；`U6-12`（`T6-S04`/M4 可达性）；`U6-13`（阶段4 实测帧周期 `P_meas`，`T6-A03` `NOT_RUN`）；`U6-14`（逐类 UX 可见时长）；`U6-15`（`A_DISPLAY_STATE`）；`U6-01..U6-11`。
- **BLOCKED**：阶段4/阶段5 接口未冻结；阶段4 实测帧周期未取得；真摄像头验收延期；独立 Reviewer 无法由本会话创建（委派深度 0，由项目总控安排）。
- **S6-B WIP（不提交）**：`docs/stage6/s6b_frozen_interface_v1.json`、`src/stage6/s6_params.py`、`src/stage6/s6_core.py` 为复评前的未提交草稿，不进本轮提交、不作为证据；复评通过后须按 v1.3 语义返工（尤其 STABLE 锁存与 `WINDOW_MATCH` 计数）。

## 证据入口（r04）

- 本轮：`report/evidence/S6-A/s6a_g0_20261022_r04/`（`delivery_manifest.json`、`inputs_manifest.json`、`hashes_sha256.txt`、`selfcheck_result.json`、`selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`、`selfcheck_old_package_failure.json`/`selfcheck_old_package_failure_stdout.txt`、`selfcheck_r02_blk1_failure.json`/`selfcheck_r02_blk1_failure_stdout.txt`、`selfcheck_r03_failure.json`/`selfcheck_r03_failure_stdout.txt`、`old_package_under_test.json`、`r02_package_under_test.json`、`r03_package_under_test.json`、`fix_record.json`、`fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`、`S6A_run_summary.md`）。
- r01/r02/r03 证据保持原样：`report/evidence/S6-A/s6a_g0_20261022_r01/`、`..._r02/`、`..._r03/`（不覆盖）。
- 规格：`docs/stage6/`；自检：`verification/s6_g0_selfcheck.py`（C1–C17）；清单构建器：`verification/s6a_build_evidence.py`；旧包重跑：`verification/s6a_rerun_legacy_failures.py`；缓存：`tmp/6/**`（不入库）。

## 下一步

1. 项目总控派独立 Reviewer 复评 S6-A v1.3（只读上表证据；本包状态 `PENDING_REVIEW`）。
2. 复评通过且 Wong 批准参数与 `U6-16` 后开 S6-B（纯核心状态机 + 动作层隔离 + 确定性测试）；S6-B 必须按 v1.3 的 H-4/H-10/W_min/`TARGET_CONTINUES`/`WINDOW_MATCH`、M3/M10 绑定与 **STABLE 锁存**实现。
3. 阶段4 接口冻结后做 6-D；摄像头到货后做 6-E。

## 11 字段交接行（2026-10-23 01:35）

任务=`S6-A 修订 v1.3（r04）：关闭第三轮复评 R3-B01/R3-B02 + N01..N05 + STABLE 锁存观察项` | 负责人=`DSH 阶段6 总控 stage6-lead3` | 工作树/分支=`D:\codex-worktrees\w6` / `stage6-interact-prep` | 起始提交=`d8bc70e43572a8e44ddcd4b3489166e28a1c6151`（修订基线 `2ce290f`） | 允许修改范围=`w6 工作树内 docs/stage6/**、verification/s6_g0_selfcheck.py、verification/s6a_build_evidence.py、verification/s6a_rerun_legacy_failures.py、report/evidence/S6-A/**、.codex/STATE.md、tmp/6/**`（`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读） | 未提交改动归属=`本轮随本行同批提交；S6-B WIP（docs/stage6/s6b_frozen_interface_v1.json、src/stage6/**）为未提交草稿，不属本轮提交` | 让出声明=`未让出：w6 写权仍由 DSH 阶段6 总控独占；无 OFFERED` | 心跳(UTC+8)=`2026-10-23 01:35` | 证据入口=`report/evidence/S6-A/s6a_g0_20261022_r04/`（`selfcheck_result.json`=17 项 ALL_PASS 含完整 C11；r03 失败证据 `selfcheck_r03_failure.json`；真实退出码见 `delivery_manifest.json.checks`） | 恢复命令=`git -C D:/codex-worktrees/w6 status --short; git -C D:/codex-worktrees/w6 log --oneline -3; python -B D:/codex-worktrees/w6/verification/s6_g0_selfcheck.py --json D:/codex-worktrees/w6/docs/stage6/s6a_stage6_g0_behavior_v1.json --doc D:/codex-worktrees/w6/docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r04/hand_computed_cases.json --upstream D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r04/upstream_bindings.json --out D:/codex-worktrees/w6/tmp/6/S6-A/s6a_g0_20261022_r04/selfcheck_rerun.json --project-root D:/codex-worktrees/w6 --evidence-dir D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r04 --manifest D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r04/delivery_manifest.json --state D:/codex-worktrees/w6/.codex/STATE.md` | 状态/下一接手方=`DELIVERED_PENDING_REVIEW / 项目总控派 Reviewer 复评；通过后再开 S6-B`

## 环境与恢复要点

- Python `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe`（3.12.10）；git 2.56.0.windows.2；`TEMP/TMP=D:\tmp`。
- `index.lock` 路径由 `git rev-parse --git-path index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/w6/index.lock`；失联判定须「心跳超时 + 无重型进程 + 无 index.lock」三者同时成立。
- 恢复/重跑证据一律写新 RunId 到 `tmp/`；**不得**覆盖 r01/r02/r03 的任何证据；不得在正式测试集上调整任何阈值。
- 工作树换行约定：MD/JSON 为 CRLF、`.py`/STATE 为 LF（`core.autocrlf=true`）；写回时保持，避免整文件差异与清单哈希口径漂移。