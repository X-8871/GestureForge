# 阶段5 状态（HDMI 结果显示：离线准备 + S5-T01 合成源 bring-up + S5-T03 真彩契约改绑与用例骨架）

## 收尾快照（2026-10-26 18:03 UTC+8；优先于旧交接行）

- **阶段5未验收，G0/G1/G3/G4/G5 未通过。** 当前 HEAD `673d371cae8a9775e31b9e3a911fe9646dcac658`，盘点前工作树干净。task-24 r06 代码审查 PASS、40/40 离线测试通过；对应证据构建器曾因 quiet-window 发现 PID 24196 而最终 exit 1，未触碰该进程，不能把该轮表述为完整证据包装通过。
- **未闭合阻碍**：camera/replay 运行时未实现；阶段4 UR-1 回放字段扩展确认与结果包未就绪；动态坐标映射、实时 stale 过期、HUD 视觉、真实注入长跑、T5-10 板上回归、capture_fps 和显示延迟物理测量均 `NOT_RUN`。UR-3 显示侧规格决策已完成，200 ms stale 上限已批准，但实测仍未做。
- 旧 `SUSPENDED_BOARD_DETACHED` 是此前快照。Wong 现在报告已现场断电重启且 JTAG/A9 恢复；本轮未连接验证，也没有阶段5板测窗口授权，因此只记为用户报告，不能恢复板测结论。阶段5实物项仍暂停。
- 本轮只更新本状态文档，无代码、证据或硬件操作。Codex 仍持本树写权；Wong 表示稍后交接给 DSH，当前没有正式 `OFFERED/CLAIMED`。

## 当前交接行（11字段，2026-10-26 18:03 UTC+8）
任务=`阶段5状态收尾：暂停开发/硬件活动，更新未验收状态与跨阶段阻碍，准备后续 DSH 交接` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w5` / `stage5-display-prep` | 起始提交=`673d371cae8a9775e31b9e3a911fe9646dcac658` | 允许修改范围=`本轮仅 .codex/STATE.md；不改业务代码、证据或硬件` | 未提交改动归属=`盘点前本树干净；本轮 STATE 收尾摘要归当前 Codex` | 让出声明=`已按 Wong 指令停止活动；无本轮板卡/显示测试；用户报告 JTAG/A9 恢复但未独立验证；阶段5 G0/G1/G3/G4/G5 未通过；当前尚未正式向 DSH OFFER` | 心跳(UTC+8)=`2026-10-26 18:03` | 证据入口=`report/evidence/S5-T03/s5t03_repeat_validation_fix_20261024_r06/；docs/stage5/s5a_g0_ur3_decision_20261025_r01.md；report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03/` | 恢复命令=`git -C D:/codex-worktrees/w5 rev-parse HEAD; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`IN_PROGRESS（活动暂停；camera/replay、阶段4接口与实际渲染/硬件 G3/G5 阻塞）/ 等 Wong 正式交接给 DSH；交接前写权属 Codex`

更新：2026-10-25 20:04（UTC+8）。工作树 `D:\codex-worktrees\w5`／分支 `stage5-display-prep`；规则见 `D:\FPGA_Competition\AGENTS.md`。
当前：Codex 依据主仓 `DSH-20261024-006` 接管。task-24 r06 的独立复审 **PASS**，关闭拒绝原因日志、repeat 上下文、u32 join-key 和状态不变性问题；完整离线测试 40/40。证据构建器最终退出 1，仅因 quiet-window 检出 PID 24196；未触碰进程。Wong 于 2026-10-25 委托 Codex 项目总控确定 UR-3，并确认跨阶段 stale 常量为 200 ms；阶段5显示侧决策已落盘，引用阶段4活动契约中 `APPROVED_BY_WONG` 的同源常量。实际实时 stale 测量仍 `NOT_RUN`；决策只关闭 UR-3，不代表阶段 G0/G1/G3/G4/G5 通过。
当前证据：`report/evidence/S5-T03/s5t03_repeat_validation_fix_20261024_r06/`（manifest SHA256 `2131101579d295da22dd934a8880e313f6ac934dcce5030c7bf07543c6366249`）；r04/r05 失败包和此前 r01-r03 全部保留。相机/回放运行时仍 `UNIMPLEMENTED`，板级验证 `SUSPENDED_BOARD_DETACHED`。
任务：`task-22`（r02 复审 PASS）→ `task-24`（r06 修复复审 PASS；quiet-window 仍 FAIL）。阶段5 **未验收**：G0/G1/G3/G4/G5 未通过；
合成源/离线骨架结论一律不得升级为真实集成结论；**实现层 camera/回放路径尚未实现**（NB-5）。
**全局事实（2026-10-24 10:29）**：Wong 已重连板卡与摄像头；须重新核验部署身份、运行期地址及真彩目视后才能按授权窗口执行。本轮只做离线修复，未操作硬件。

历史交接（2026-10-24 20:39；由上方收尾快照取代）: 任务=`task-24 join-key fail-closed 与拒绝日志修复；代码/证据复审 PASS，证据构建被 quiet-window 阻断` | 负责人=`Codex 项目总控` | 工作树/分支=`D:\codex-worktrees\w5 / stage5-display-prep` | 起始提交=`30147ab1f958c0dad2795da8e4b1c073ac39adaa` | 允许修改范围=`本轮 docs/stage5、scripts/stage5_t03、verification/s5_display_geometry_reference.py、report/evidence/S5-T03/r04-r06、STATE` | 未提交改动归属=`r04-r06 修复差异及 STATE 归当前 Codex 阶段5任务；此前提交与旧 RunId 不改写` | 让出声明=`DSH-20261024-006 正式 OFFERED；阶段5 Developer 已停写，独立 Reviewer PASS；总控复核/提交中；板级验证仍暂停` | 心跳(UTC+8)=`2026-10-24 20:39` | 证据入口=`report/evidence/S5-T03/s5t03_repeat_validation_fix_20261024_r06/`（r04/r05 为失败记录） | 恢复命令=`git --no-optional-locks -C D:/codex-worktrees/w5 status --short; git -C D:/codex-worktrees/w5 rev-parse HEAD` | 状态/下一接手方=`IN_PROGRESS（task-24 修复复审 PASS；quiet-window FAIL 因 PID 24196；G0/G1/G3/G4/G5 未通过；摄像头/回放运行时 UNIMPLEMENTED；板级 SUSPENDED_BOARD_DETACHED）/ 下一接手方=Codex 总控做精确差异核验与提交`

## 目标与范围
- 已完成：S5-A 契约/G0、S5-B 离线渲染叠框自测、S5-C 与阶段4 数值链回归、S5-D 阶段6 建议；S5-T01 合成源（PS 合成图）板上 bring-up。
- 本轮（S5-T03 v3，全离线）：契约改绑真实彩色（对齐阶段4 r04）+ 坐标映射/帧关联/顺序规则/异常/长跑**用例骨架** + 板级待验清单（已标 `SUSPENDED_BOARD_DETACHED`）。
- 明确不做：CNN 改动、改 2A 冻结规格或 2B 接口正文、改 w4/dbdf/w2b/main、写两个 mailbox、**动硬件**。

## 上游事实（只读核对）
- 阶段3（dbdf）：新模块曾实测恢复真彩色（`S3-T05/t05_new_module_reverify_20261023_r01`）。部署身份**本树独立重算**：
  无补偿 bit `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710`、XSA `1f5b138e…cb0e3`、
  应用 `an5642_j11cmos2_v10_read.elf` `1457cda4…6073`（bit/ELF 全哈希一致、XSA 前缀一致且全哈希与 dbdf 原部署清单一致）。
  **该真彩目视记录只对当次连接下的部署有效**，换板/换模块/换端口/部署变更后须重做。J10 半屏黑＝Wong 2026-10-24 **范围外**（J11/CMOS2）。
  `UR-2` **RESOLVED**（dbdf README 2026-10-24T01:14:18 更正为 `v10_read`，sha256 `e60bab01…`）。
- 阶段4（w4）：已由 DSH 认领；**r04 `7a9507a`（00:52:29）**＝现行输入契约权威（committed-not-frozen）：
  两个彩色标签都 `maps_to_source_kind=camera`、`capture_time_available=true`（回放以 `timing_claim_scope=replay_only` 区分）；
  `frame_sequence_rules`：重复/`frame_id` 回退/乱序/回绕/等价 `frame_id` 未声明**一律拒绝并记 FAIL 且须记原因**；`capture_clock=PENDING_MEASUREMENT`。
- 硬件：**板卡已拔下**；本轮 0 个 vivado/xsdb/hw_server/vitis/xsim、3121 未监听（安静窗口实跑，见 r03 证据）。

## 本轮交付（S5-T03 v3：NB-1..NB-5）
- **NB-1**：等价 `frame_id` 改 **fail-closed**（未显式声明即拒绝并记 FAIL，新增计数 `duplicate_frame_id_results`；放行只看 `repeat_declared`/`repeat_index` 递增）；
  含 3 条定向用例 + **判别力对照**（复刻 r02 语义时断言变红）+ `equiv` 流 40 帧；**未削弱 B-2**。
- **NB-2**：漂移登记改为**扫描判据**（`scripts/stage5_t03/scan_hash_drift.py`：`report/evidence/**/*manifest*.json` 命中集合 == 登记集合，双向相等）；
  登记 **19 个清单文件 / 10 个包目录**；**未改写任何旧包**。
- **NB-3**：计数单位 JSON↔流水线**逐字相等**（JSON 15 键＝14 计数＋`definition`；流水线 14 键）；清单由 JSON 生成完整 14 条。
- **NB-4**：`revised/generated_utc8` 改为本文件最后写入的分钟值 `2026-10-24T02:34:00+08:00`（容差 ≤60 s），实测 mtime 02:34:00/02:34:17/02:34:30 记于 r03 证据。
- **NB-5**：T01 补绑定断言（回放 `capture_time_ns` 非零要求、`carry_fields` 10 字段、`implementation_status`）+ 文档明写**实现层未实现**。
- 文档：`docs/stage5/s5t03_input_contract_binding_v1.json`（v3 内容）+ `S5T03_input_contract_binding_colour_v1.md`（§9b/§11）、
  `s5t03_offline_skeleton_params_v1.json`、`S5T03_offline_case_skeleton_v1.md`、`S5T03_board_verification_pending_v1.md`（v3）。
- 证据：`report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03/`、`…/s5t03_takeover_20261024_r03/`。

## 实测（本轮离线，合成动态流）
- 用例骨架 **34 项 / 0 失败 / 0 错误**（115.4 s，Python 3.12.10，种子 20261024）：
  坐标手算、越界/零面积、2 px 偶数线宽、120 帧五元组、四类拒绝（重复键/`frame_id` 回退/`result_seq` 回退/**等价 `frame_id` 未声明**）、
  等价帧**声明放行**、过期三边界、零框≠过期、超时/错误/丢帧/无效分列、HUD13、长跑、计数单位逐字一致、**漂移登记覆盖扫描**、落盘日志独立复算。
- 240 帧 mixed：绘制 177 帧/467 框、stale_cleared 7、dup 8、**out_of_order 8（全拒绝+FAIL）**、`duplicate_frame_id_results=0`（等价帧由定向用例与 `equiv` 流覆盖）、
  zero_hand 7、timeout 14、error 7、drop 7、invalid 7、zero_area 89；长跑 106 573 帧、区间数 106 572 × 16.89 ms＝1 800 001 080 000 ns（余量 +1.08 ms）。
- 独立复算器两日志 **exit 0**；漂移扫描 **COVERED / exit 0**；安静窗口 **QUIET**；两个 r03 包交付检查器 **CHECKS_OK / exit 0**。
- 既有合成源证据未被改写：`git diff --name-only 654c72e -- report/evidence/S5-A|S5-B|S5-C|S5-T01` 为空（r03 证据实跑记录）。

## 未决与风险
- `UR-1`（对 r04 重发）：阶段4 确认显示侧回放扩展字段命名（`replay_source_*`/`stage3_capture_evidence_entry` 等）并入契约。
- `UR-3`：**已由 Wong 委托 Codex 项目总控于 2026-10-25 作出阶段5显示侧决定**，见 `docs/stage5/s5a_g0_ur3_decision_20261025_r01.md`。成品 `age_frame` 上限 200 ms、类别 RGB 色表、字号缩放、stale 域均已定义；阶段4活动共享契约的 `stale_age_limit_ns=200000000` 已为 `APPROVED_BY_WONG`，S4-A r06 的 DRAFT 标签是历史快照；实际运行 stale 测量仍 `NOT_RUN`。阶段6 `T6-A03` 仍是另一指标且 `NOT_RUN`。camera/replay 实现、真实渲染和硬件验收仍未完成。
- `UR-4`：Wong 于 2026-10-25 报告板卡已接上；本机只读检查未枚举 COM/USB 设备且 3121 无监听，故目前只能记为**用户报告重连、主机连接未确认**。尚未获本轮阶段级板测授权或窗口 OFFER；不操作硬件。获授权后先重做真彩目视/部署身份核对，再按 `CDX-20261023-018` §3 走窗口流程。
- 哈希轨迹（S5A-G0-v2 JSON，仅措辞/来源说明类修订）：`8eac7007…` → `10d24a39…`（N-1）→ `e3347c4e…` → **`af51a4bf…`**（NB-4）；阈值/几何/语义自 N-1 后未再变。
- 限制：实现层 camera/回放路径、板上动态映射/过期边界/HUD 视觉、真实注入长跑、T5-10 板上回归、`capture_fps` 实测、显示延迟物理测量 —— 一律 **NOT_RUN**；
  P1 现行「宿主预计算框」不得当作板上动态映射；无 ILA 不免除适用标准。

## 证据入口
- `report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r03/`（`summary.md`、`results_skeleton.json`、`console/{unittest,impact_scan,quiet_window,file_mtimes,recompute_from_log,not_modification_check}.*`、`logs/**`、`delivery_manifest.json`）
- `report/evidence/S5-T03/s5t03_takeover_20261024_r03/`（安静窗口/接管核对、部署身份只读重算、板卡拔下记录）
- 历史：`S5-T03/…_r01|_r02`（被取代，保留不改写）、`S5-A|S5-B|S5-C|S5-CTRL|S5-T01/**`（合成源结论原样保留）
- 本轮提交：内容 `a465b48` + `5fd3336`（NB 轮最终基线）；证据与 STATE 同批提交（见 `git log -1`）。

## 交接行（11 字段，2026-10-24 02:40）
任务=`task-24 阶段5 NB 轮（NB-1 fail-closed / NB-2 扫描式漂移登记 / NB-3 逐字一致 / NB-4 时间戳 / NB-5 绑定断言+实现状态）完成，固定新基线待复审` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`654c72e` | 允许修改范围=`docs/stage5/**`、`scripts/stage5_t03/**`、`report/evidence/S5-T03/**`、`tmp/5/**`、`.gitattributes`、`.codex/STATE.md` | 未提交改动归属=`本树全部为本轮产物，与 STATE 同批提交（tmp/ 忽略项；无他人改动混入）` | 让出声明=`**板卡已被 Wong 拔下 ⇒ 板级工作暂停**；本轮 0 个硬件进程、3121 未监听、未加载位流/未烧录；工作树写权仍由本阶段总控独占；**本轮固定基线后不再写，等待复审**` | 心跳(UTC+8)=`2026-10-24 02:40` | 证据入口=`report/evidence/S5-T03/**`、`docs/stage5/S5T03_*`、`docs/stage5/s5t03_*` | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`IN_PROGRESS（S5-T03 v3 已交付并固定基线；待 DSH 项目总控派独立复审；下一轮按无板卡工作流用阶段4 回放结果包实现回放路径并做离线动态显示回归）/ 本阶段总控`

## 正式 OFFERED 交接行（2026-10-26 21:07 UTC+8；优先于以上历史交接及写权陈述）

任务=阶段5正式写权交接 | 负责人=Codex 项目总控 | 工作树/分支=D:\codex-worktrees\w5 / stage5-display-prep | 起始提交=673d371cae8a9775e31b9e3a911fe9646dcac658（交接前基线；正式 OFFER 版本为包含本行的提交） | 允许修改范围=本次仅 .codex/STATE.md 的交接记录与提交；后续阶段5业务修改按接手任务及既有授权执行 | 未提交改动归属=本次开始时仅有1项 .codex/STATE.md 差异，原有收尾快照及历史交接调整完整保留，与本正式交接行同批提交；未混入其他文件 | 让出声明=Wong 已明确授权本次交接；Codex 项目总控在本行及原有 STATE 差异提交完成后立即停止写 w5，不再暂存或提交；核验时无 index.lock，未发现 Git/Vivado/XSDB/hw_server/Vitis/XSCT/XSim 进程；本行不构成硬件窗口授权或阶段验收通过 | 心跳(UTC+8)=2026-10-26 21:07 | 证据入口=.codex/STATE.md（本行所在提交）；report/evidence/S5-T03/s5t03_repeat_validation_fix_20261024_r06/delivery_manifest.json；docs/stage5/s5a_g0_ur3_decision_20261025_r01.md | 恢复命令=git -C D:/codex-worktrees/w5 log -1 --format=%H -- .codex/STATE.md; git -C D:/codex-worktrees/w5 status --short; git -C D:/codex-worktrees/w5 rev-parse HEAD | 状态/下一接手方=OFFERED / DSH 项目总控

本行是正式让出记录；DSH 项目总控须以提交后的实际 HEAD 重新核验并明确 CLAIMED，方可推进认领状态。此前阶段5未验收及未执行项继续按原文保留。

## 接管交接行（11 字段，2026-10-26 21:21 UTC+8；**优先于以上全部**，已 CLAIMED）

任务=`S5-T03 阶段5 写权接管（handoff_check --claim 通过）与「离线 replay/display 骨架」交付；本轮不接板卡、不宣称任何关口通过` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`c2deb2f10bdc1a92858295ffe6818cf871a5df5f`（含 OFFERED 行的 OFFER 提交；`git log -1 --format=%H -- .codex/STATE.md` 实测） | 允许修改范围=`.codex/STATE.md`、`scripts/stage5_t03/**`、`docs/stage5/**`、`report/evidence/S5-T03/**`、`tmp/5/**` | 未提交改动归属=`接管证据 + 渲染/replay/长跑/多几何实现与测试 + 全部 S5-T03 RunId，均归 DSH 阶段5 总控并与本轮提交同批；无他人改动混入` | 让出声明=`**未让出：本阶段总控独占 w5 写权（CLAIMED→IN_PROGRESS）**；本轮不接板卡：未加载位流/ELF、未占用 JTAG/COM4、未启动 hw_server、未烧录；板级工作维持 SUSPENDED_BOARD_DETACHED` | 心跳(UTC+8)=`2026-10-27 00:05` | 证据入口=`report/evidence/S5-T03/s5t03_takeover_20261026_r01/`（接管）；`…/s5t03_offline_replay_display_20261026_r06/`（短跑 240 帧）；`…/s5t03_offline_long_run_replay_20261026_r04/`（**长跑 106573 帧 / 虚拟 1800.001 s**）；`…/s5t03_multi_geometry_render_20261026_r02/`（**多几何逐像素**：1280×720 / 720×1280 / 683×384 / 683×384→1920×1080 k=2） | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short; python -B D:/FPGA_Competition/verification/handoff_check.py --worktree D:/codex-worktrees/w5 --json` | 状态/下一接手方=`IN_PROGRESS（离线 replay/display 骨架已交付：短跑 240 帧 0 失败、长跑 106573 帧/虚拟 1800.001 s/全部不变量为真、**多几何 4/4 逐像素一致**（含奇数补边 416×233/off(0,91)/下 92 与 k=2/1366×768/off(277,156)）；四模块套件 **75 项 OK**、三包各自独立套件日志；第 1/2/3 轮复审 PASS、第 4 轮唯一阻断项（三包摘要与自身权威文件矛盾）已闭环：摘要改为**按各包 results.json/manifest/日志派生**并显式声明"冲突以 JSON 为准"；历史包只**追加权威声明**、不改历史数字；`manifest.files[]` 全部回填；三包套件日志各自独立（75 项 OK，SHA 互异）；第 5 轮定向复核进行中；**JSON 契约 v1 已冻结**（`docs/stage5/s5t03_json_contract_v1.{json,md}` + 只读校验器 `scripts/stage5_t03/validate_s5t03_json.py`，三最终包校验 exit 0，13 项契约测试含负向判别，**88 项套件 OK**，证据 `…/s5t03_json_contract_20261026_r01/`）；真实回放/板上/摄像头项仍 NOT_RUN；G0/G1/G3/G4/G5 均未通过）/ 本阶段总控`

接管事实（`handoff_check --claim`，真实退出码）：
- 原文记录：exit 1，`PASS 7 / FAIL 2`（a 起始提交、g 证据入口）——原样留证于 `console/claim_verbatim.json`。
- **更正后记录：exit 0，`HANDOFF_OK`，`PASS 9 / FAIL 0`**（`console/claim_corrected.json`）。
- 两处更正经 Wong 2026-10-26 批准，依据与影响见接管证据 `summary.md` §3：①`base_commit` 由"交接前基线 673d371"改为**含 OFFERED 行的 OFFER 提交 c2deb2f**（OFFERED 行自注"正式 OFFER 版本为包含本行的提交"）；②证据入口改为本接管证据目录（含 checker 要求的 `manifest.json`，非删除/绕过校验）。Codex 的 OFFERED 行与历史交接行**原样保留，未覆盖、未删除**。
- 核验现场：无 `index.lock`、未提交改动 0 项、无重型进程、心跳未超时、`status=OFFERED` 允许接管。

本轮已交付（离线 replay/display 骨架渲染路径；详见 `s5t03_offline_replay_display_20261026_r03/summary.md`）：
- 新增 `scripts/stage5_t03/s5t03_render.py`（栅格化：边框像素**只取** `R.border_pixel_sets`；UR-3 类别色与字号；标签越界翻转/安全区；HUD 13 行 `UNAVAILABLE`→`NA`）与 `s5t03_replay_display.py`（合成流→管线→渲染→**三层产物**；阶段3 输入帧绑定装载；三例过期边界；关键帧有界选择；demo 生成），新增 13 项测试。
- 证据 `…_r03`：`results.json`（权威）+ `frame_assertions.jsonl`（240 行）+ `keyframes/`（14 张）+ `demo.mp4`（`demo_only`）+ `manifest.json` + `console/`；**240 帧 0 失败**、`recompute_matches_online=true`、14 项计数与既有骨架 r03 基线**逐项相同**；边界 `==limit` 不过期 / `limit+1` 过期 / 显式 `stale_flag` 过期三例 PASS。
- 输入帧：阶段3 `frame_full.bin`（BGR888 1280×720 stride 3840）SHA `939fce22…` **实测与绑定一致**，仅作**输入帧**；**推理结果为合成流** ⇒ 真实回放接入仍 `NOT_RUN`。
- 测试：`test_s5t03_skeleton` + `test_s5t03_replay_display` → **Ran 53 tests, OK, exit 0**。
- 未做（NOT_RUN，不得冒充）：真实回放接入（无阶段4 冻结回放结果包）、板上动态映射/绘制、摄像头真实采集、真实集成 30 分钟与 T5-10 板上回归、HUD 屏上视觉确认。
- 历史 RunId 保留不删：`…_r01`（ffmpeg 构建不支持 glob 的 demo 失败记录）、`…_r02`（最终代码前版本）。
