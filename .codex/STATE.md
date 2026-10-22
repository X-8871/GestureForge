# 阶段6 状态入口（w6 / stage6-interact-prep）

更新：2026-10-22 19:58（UTC+8）。按 `AGENTS.md` 与主 STATE 恢复；**本文件是阶段6 工作树专属状态**，主状态 `D:\FPGA_Competition\.codex\STATE.md` 只读。阶段技术事实以本文件与本树证据为准。

## 阶段目标与范围

- 目标：稳定手势判定 → HDMI 切图/界面/显示状态；冻结多框目标选择、丢失与重获、稳定窗口、保持期触发语义、冷却、再触发条件、无手/未知/超时错误与恢复行为（计划 L102–L108）。
- 范围：`w6` 独占写入；G0 v1.2 复评 → 状态机实现与确定性测试（6-B/6-C）→ 无摄像头两级联调（6-D）→ 真摄像头验收（6-E，延期）。
- 硬边界：**无硬件授权**——不碰板卡/JTAG/COM4/`hw_server`/HDMI 实物/摄像头，不烧录；`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读；两个 mailbox 只读；不 push；同时只跑一个重型任务。
- 注入/回放结论适用范围仅限回放/注入输入；真手势验收延期至摄像头到货。

## 上游绑定与冻结状态（2026-10-22 核实）

- 已冻结、可直接引用：`S2A-T01` 规格（`7c2c8684…`）、阶段计划 L102–L108、`D2`（`df95a843…`）、`D6`（`735cbc78…`）。
- **未冻结（仅草案/隔离使用）**：阶段4 `s4a_stage4_g0_fields.json`（`DRAFT_NOT_FROZEN`，`73c3dad` 版本 `3524d02a…`）；阶段5 `S5A v2`（`ca5968d4…`，离线定稿未验收）。
- 阶段4/阶段5 接口未冻结 → 阶段6 集成验收依赖 `BLOCKED`；不得据此做集成验收。

## 本轮已完成（S6-A v1.2 / r03 修订，PENDING_REVIEW）

- 针对**复评** `S6A_20261022_r02`（`CHANGES_REQUIRED`，BLK-1/BLK-2/BLK-3 + NBL-1..5）按项目总控要求关闭：
  - **BLK-1 谓词落地**：`M3` 改用 `WINDOW_MATCH` 计数（低分目标不得进入 STABLE）；`M10/B10` 绑 `TARGET_CONTINUES`（低分但几何连续不判丢失）；`M1/M4/M5/M8/M9/M15`、`B04/B08/B12/B13/B14` 显式绑定并写 `predicates_used`；`predicates.used_by` 补 M3/M10；文档 §4/§5/§9/§10/§12/§13 同步；自检 **C12 增加迁移/行为行断言与裸“匹配”扫描**。
  - **BLK-2 旧包哈希**：改用 `git cat-file blob <commit>:<path>` **二进制字节**重算 r01 5 个哈希并落盘，用同一字节重跑失败证据（exit 1，13 项）；说明 r02 哈希错误源于 PowerShell 文本管道改写行尾/编码。
  - **BLK-3 C11 入库**：入库 `selfcheck_result.json` 改由 `--manifest` + `--state` 完整命令生成（C11 detail 含清单双向与 STATE 核对）；落盘 `selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`。
  - **NBL-1..5**：inputs 清单 checks 两阶段实测回写；冷却锚点统一 `t_last_submit` 并删除“尝试提交”歧义；边界样例引入 `t_now`/几何输入真算并新增 HC-28/HC-29；§15 六列表头；B-05 措辞按实际改动重述。
- 自检加固：**先证明能捕获 r02 的 BLK-1**（`selfcheck_r02_blk1_failure.json`：C12 报“predicates.used_by 未登记 M3”），再对 r03 跑出 `ALL_PASS`（16 项）；r01 旧包失败证据同样由真实字节重跑。
- 24 项参数值与批准状态**未改**，全部 `PENDING_APPROVAL`；未在测试集调参。

## 未决与阻塞

- **PENDING_REVIEW**：S6-A v1.2 复评由项目总控另派独立 Reviewer；复评通过前不得宣称 G0 通过，也不启动 S6-B。
- **BLOCKED**：阶段4/阶段5 接口未冻结；阶段4 实测帧周期 `P_meas` 未取得（`T6-A03` NOT_RUN，U6-13）；真摄像头验收延期；独立 Reviewer 无法由本会话创建（委派深度 0，由项目总控安排）。
- **待 Wong/G0**：`U6-01..U6-15`（含 `S04/M4` 可达性 U6-12、逐类 UX U6-14、`A_DISPLAY_STATE` U6-15）。
- **S6-B WIP（不提交）**：`docs/stage6/s6b_frozen_interface_v1.json`、`src/stage6/s6_params.py`、`src/stage6/s6_core.py` 为复评前的未提交草稿，按总控要求标注 WIP、不进本轮提交、不作为证据；复评通过后须按 v1.2 语义返工。

## 证据入口（r03）

- 本轮：`report/evidence/S6-A/s6a_g0_20261022_r03/`（`delivery_manifest.json`、`inputs_manifest.json`、`hashes_sha256.txt`、`selfcheck_result.json`、`selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`、`selfcheck_old_package_failure.json`/`.txt`、`selfcheck_r02_blk1_failure.json`/`.txt`、`old_package_under_test.json`、`r02_package_under_test.json`、`fix_record.json`、`fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`、`S6A_run_summary.md`）。
- r01/r02 证据保持原样：`report/evidence/S6-A/s6a_g0_20261022_r01/`、`..._r02/`（不覆盖）。
- 规格：`docs/stage6/`；自检：`verification/s6_g0_selfcheck.py`；清单构建器：`verification/s6a_build_evidence.py`；缓存：`tmp/6/**`（不入库）。

## 下一步

1. 项目总控派独立 Reviewer 复评 S6-A v1.2（只读上表证据；本包状态 `PENDING_REVIEW`）。
2. 复评通过且 Wong 批准参数后开 S6-B（纯核心状态机 + 动作层隔离 + 确定性测试）；S6-B 必须按 v1.2 的 H-4/H-10/W_min/`TARGET_CONTINUES`/`WINDOW_MATCH` 与 M3/M10 绑定实现。
3. 阶段4 接口冻结后做 6-D；摄像头到货后做 6-E。

## 11 字段交接行（2026-10-22 19:58）

任务=`S6-A 修订 v1.2（r03）：关闭复评 BLK-1/BLK-2/BLK-3 + NBL-1..5` | 负责人=`DSH 阶段6 总控 stage6-lead2` | 工作树/分支=`D:\codex-worktrees\w6` / `stage6-interact-prep` | 起始提交=`d8bc70e43572a8e44ddcd4b3489166e28a1c6151`（修订基线 `3b59674`） | 允许修改范围=`w6 工作树内 docs/stage6/**、verification/s6_g0_selfcheck.py、verification/s6a_build_evidence.py、report/evidence/S6-A/**、.codex/STATE.md、tmp/6/**`（`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读） | 未提交改动归属=`本轮随本行同批提交；S6-B WIP（docs/stage6/s6b_frozen_interface_v1.json、src/stage6/**）为未提交草稿，不属本轮提交` | 让出声明=`未让出：w6 写权仍由 DSH 阶段6 总控独占；无 OFFERED` | 心跳(UTC+8)=`2026-10-22 19:58` | 证据入口=`report/evidence/S6-A/s6a_g0_20261022_r03/`（`selfcheck_result.json`=ALL_PASS 含完整 C11；r02 BLK-1 失败证据 `selfcheck_r02_blk1_failure.json`；真实退出码见 `delivery_manifest.json.checks`） | 恢复命令=`git -C D:/codex-worktrees/w6 status --short; git -C D:/codex-worktrees/w6 log --oneline -3; python -B D:/codex-worktrees/w6/verification/s6_g0_selfcheck.py --json D:/codex-worktrees/w6/docs/stage6/s6a_stage6_g0_behavior_v1.json --doc D:/codex-worktrees/w6/docs/stage6/S6A_stage6_g0_behavior_spec_v1.md --cases D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r03/hand_computed_cases.json --upstream D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r03/upstream_bindings.json --out D:/codex-worktrees/w6/tmp/6/S6-A/s6a_g0_20261022_r03/selfcheck_rerun.json --project-root D:/codex-worktrees/w6 --evidence-dir D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r03 --manifest D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r03/delivery_manifest.json --state D:/codex-worktrees/w6/.codex/STATE.md` | 状态/下一接手方=`DELIVERED_PENDING_REVIEW / 项目总控派 Reviewer 复评；通过后再开 S6-B`

## 环境与恢复要点

- Python `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe`（3.12.10）；git 2.56.0.windows.2；`TEMP/TMP=D:\tmp`。
- `index.lock` 路径由 `git rev-parse --git-path index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/w6/index.lock`；失联判定须「心跳超时 + 无重型进程 + 无 index.lock」三者同时成立。
- 恢复/重跑证据一律写新 RunId 到 `tmp/`；**不得**覆盖 r01/r02/r03 的任何证据；不得在正式测试集上调整任何阈值。
