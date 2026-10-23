# 阶段5 状态（HDMI 结果显示：离线准备 + S5-T01 合成源 bring-up + S5-T03 真彩契约改绑与用例骨架）

更新：2026-10-24 01:58（UTC+8）。工作树 `D:\codex-worktrees\w5`／分支 `stage5-display-prep`；规则见 `D:\FPGA_Competition\AGENTS.md`。
任务：`task-22`（阶段5 接续，**全离线**）。阶段5 **未验收**：G0/G1/G3/G4/G5 未通过；合成源结论与离线骨架结论一律不得升级为真实集成结论。
本轮为**复审修复轮**（`CHANGES_REQUIRED`：B-1/B-2 + N-1..N-7），修复后固定新基线，待 DSH 项目总控另派复审。

## 目标与范围
- 已完成：S5-A 契约/G0、S5-B 离线渲染叠框自测、S5-C 与阶段4 数值链回归、S5-D 阶段6 建议；S5-T01 合成源（PS 合成图）板上 bring-up。
- 本轮（S5-T03 v2，全离线）：契约改绑真实彩色（对齐阶段4 r04）+ 坐标映射/帧关联/顺序规则/异常/长跑**用例骨架** + 板级待验清单。
- 明确不做：CNN 改动、改 2A 冻结规格或 2B 接口正文、改 w4/dbdf/w2b/main、写两个 mailbox、**动硬件**。

## 上游事实（本轮只读核对）
- 阶段3（dbdf）：**新模块实测恢复真彩色**（`S3-T05/t05_new_module_reverify_20261023_r01`）。当前部署身份**本树独立重算**：
  无补偿 bit `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710`、XSA `1f5b138e…cb0e3`、
  应用 `an5642_j11cmos2_v10_read.elf` `1457cda4…6073`；**bit/ELF 全哈希与 015 r03 一致、XSA 前缀一致且全哈希与 dbdf 原部署清单一致**。
  源帧 1280×720、stride 3840 B、帧 2 764 800 B、DDR 转储 B/G/R（登记，未改判）。J10 半屏黑 = Wong 2026-10-24 **范围外**（当前 J11/CMOS2）。
  `UR-2` **已 RESOLVED**：dbdf README 于 2026-10-24T01:14:18 更正为 `v10_read`（sha256 `e60bab01…`），本树 01:50 只读复核通过。
- 阶段4（w4）：已由 DSH 认领；**r04 `7a9507a`（2026-10-24T00:52:29）**＝现行输入契约权威（committed-not-frozen）：
  两个彩色标签都 `maps_to_source_kind=camera`、`capture_time_available=true`（回放以 `timing_claim_scope=replay_only` 区分）；
  `frame_sequence_rules`：重复/`frame_id` 回退/乱序/回绕**一律拒绝并记 FAIL 且须记原因**；`capture_clock=PENDING_MEASUREMENT`。
  **结果契约未冻结 ⇒ 真实彩色接入 NOT_RUN**；硬件使用权不随工作树交接。
- 硬件：阶段3 板级窗口自 2026-10-24 00:35 起**占用中** ⇒ 本轮不动硬件（0 个 hw_server/xsdb/vitis/xsim、3121 未监听、未加载位流、未烧 QSPI）。

## 本轮交付（S5-T03 v2）
- 绑定：`docs/stage5/s5t03_input_contract_binding_v1.json`（内容 v2，`BINDING_ALIGNED_WITH_STAGE4_R04_NOT_FROZEN`）
  + `S5T03_input_contract_binding_colour_v1.md`（§0 取代关系、§9 修订登记、§10 计数单位）。
  阶段3 部署/几何/坐标/关联键/回放规则与 `frame_integrity` 逐帧要求均已绑定；**未改 S5A-G0-v2 阈值/几何/语义**。
- 骨架：`docs/stage5/s5t03_offline_skeleton_params_v1.json`（`FROZEN_BEFORE_RUN_REVISED_20261024`，种子 `20261024`，含 `counter_units`/`log_artifacts`）
  + `S5T03_offline_case_skeleton_v1.md` + `scripts/stage5_t03/**`（含新增独立复算器 `recompute_from_log.py`）。
- 板级待验：`docs/stage5/S5T03_board_verification_pending_v1.md`（P1–P7、B1–B10、窗口 A/B 材料、防误报清单，已加顺序规则与计数单位判据）。
- 证据：`report/evidence/S5-T03/s5t03_takeover_20261024_r02/`、`…/s5t03_offline_skeleton_20261024_r02/`（含 `logs/events_*.jsonl[.gz]`）。

## 实测（本轮离线，合成动态流）
- 用例骨架 **29 项 / 0 失败 / 0 错误**（119.8 s，Python 3.12.10，种子 20261024）：坐标手算、越界/零面积、2 px 偶数线宽、
  120 帧五元组、**重复/乱序/`frame_id` 回退/`result_seq` 回退一律拒绝并记 FAIL**、过期三边界（每结果只计一次）、
  零框≠过期、超时/错误/丢帧/无效记录分列、HUD13、长跑、计数单位声明、落盘日志独立复算。
- 240 帧 mixed：绘制 177 帧/467 框、stale_cleared 7、dup 8、**out_of_order 8（全部拒绝、verdict=FAIL）**、
  zero_hand 7、timeout 14、error 7、drop 7、invalid 7、zero_area 89（计数可由事件日志复算）。
- 长跑（离线虚拟时钟）：106 573 帧、区间数 106 572 × 16.89 ms = 1 800 001 080 000 ns（**余量 +1.08 ms**）、每帧恰一次提交、时间戳单调。
- 独立复算器：对落盘日志两次实跑 **exit 0** 且与在线计数逐项一致；交付检查器两个 r02 包 **CHECKS_OK / exit 0**。
- 既有合成源证据未被改写：`git diff --name-only 654c72e -- report/evidence/S5-A|S5-B|S5-C|S5-T01` 为空（exit 0）。

## 未决与风险
- `UR-1`（**对 r04 重发**）：请阶段4 确认显示侧回放扩展字段命名（`replay_source_*`/`stage3_capture_evidence_entry`/`source_frame_id`/`source_capture_time_ns`）并入契约。
- `UR-3`：Wong/正式 G0 —— 成品延迟上限、颜色表与字号、阶段4 `stale_age_limit` 正式冻结；并请裁定 **N-1** 登记的 stale 判定域口径。
- `UR-4`：DSH —— 阶段4 结果冻结后按 `CDX-20261023-018` §3 发阶段5 硬件 OFFER（scope `S5-T02::s5_display_dynamic_mapping`，窗口 A≈2h + B≈1h）。
- **N-1 已按裁定处理**：只改 S5A-G0-v2 JSON 的 stale 判定域**措辞**（行为不变、无 state 守卫），并登记差异；
  该 JSON 哈希 `8eac7007…` → `10d24a39…`。
- **取代与影响（如实登记）**：r01 两个证据包被 r02 取代（其清单绑定源文件在更正中已变，对当前字节不再匹配；不删除、不就地改写）；
  `report/evidence/S5-A/s5a_g0_20261021_r03` 因 N-1 对 S5A-G0-v2 JSON 的绑定漂移，其余未动。
- 限制：板上动态映射/过期边界/真实注入 30 分钟联调、T5-10 板上回归、`capture_fps` 实测、显示延迟物理测量一律 **NOT_RUN**；
  P1 现行「宿主预计算框」不得当作板上动态映射；无 ILA 不免除适用标准。

## 证据入口
- `report/evidence/S5-T03/s5t03_takeover_20261024_r02/`（handoff_check 原始 JSON、部署与 UR-2 复核、硬件快照、C1–C4 退出码）
- `report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r02/`（`summary.md`、`results_skeleton.json`、`console/**`、`logs/**`、`delivery_manifest.json`）
- 历史：`report/evidence/S5-A|S5-B|S5-C|S5-CTRL|S5-T01/**`（合成源结论原样保留）、`S5-T03/…_r01/**`（被取代，保留）
- 本轮提交：内容提交 `b6d11d4`（F2）；证据与 STATE 同批提交（见 `git log -1`）。

## 交接行（11 字段，2026-10-24 01:58）
任务=`task-22 复审修复轮：S5-T03 v2 契约重绑阶段4 r04 + 顺序规则拒绝并记 FAIL + 长跑口径/计数单位/日志落盘/独立复算 + N-1 措辞修订（固定新基线，待复审）` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`654c72e` | 允许修改范围=`docs/stage5/**`、`scripts/stage5_t03/**`、`report/evidence/S5-T03/**`、`tmp/5/**`、`.gitattributes`、`.codex/STATE.md` | 未提交改动归属=`本树全部为本轮产物，与 STATE 同批提交（tmp/ 忽略项；无他人改动混入）` | 让出声明=`硬件未占用：0 个 hw_server/xsdb/vitis/xsim、3121 未监听、未加载位流、未烧 QSPI；**阶段3 板级窗口 2026-10-24 00:35 起占用中**，阶段5 板级须另行申请 OFFER；工作树写权仍由本阶段总控独占；**本轮固定基线后不再写，等待复审**` | 心跳(UTC+8)=`2026-10-24 01:58` | 证据入口=`report/evidence/S5-T03/**`、`docs/stage5/S5T03_*`、`docs/stage5/s5t03_*` | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`IN_PROGRESS（S5-T03 v2 已交付并固定基线；待 DSH 项目总控派独立复审；真实彩色接入待阶段4 结果冻结，板级待窗口）/ 本阶段总控`