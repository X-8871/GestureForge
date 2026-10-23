# 阶段5 状态（HDMI 结果显示：离线准备 + S5-T01 合成源 bring-up + S5-T03 真彩契约改绑与用例骨架）

更新：2026-10-24 01:20（UTC+8）。工作树 `D:\codex-worktrees\w5`／分支 `stage5-display-prep`；规则见 `D:\FPGA_Competition\AGENTS.md`。
任务：`task-22`（阶段5 接续，**全离线**）。阶段5 **未验收**：G0/G1/G3/G4/G5 未通过；合成源结论与离线骨架结论一律不得升级为真实集成结论。

## 目标与范围
- 已完成：S5-A 契约/G0、S5-B 离线渲染叠框自测、S5-C 与阶段4 数值链回归、S5-D 阶段6 建议；S5-T01 合成源（PS 合成图）板上 bring-up。
- 本轮（S5-T03，全离线）：输入契约改绑真实彩色 + 坐标映射/帧关联/异常/长跑**用例骨架** + 板级待验项清单。
- 明确不做：CNN 改动、改 2A 冻结规格或 2B 接口正文、改 w4/dbdf/w2b/main、写两个 mailbox、**动硬件**。

## 上游事实（本轮只读核对）
- 阶段3（dbdf）：**新模块实测恢复真彩色**（缺位签名不符、彩条满量程；`S3-T05/t05_new_module_reverify_20261023_r01`）。
  当前部署身份**本树独立重算**：无补偿 bit `7cb3306809…`=`7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710`、
  XSA `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3`、
  应用 `an5642_j11cmos2_v10_read.elf` `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073`（3/3 与 015 r03 一致）。
  源帧 1280×720、stride 3840 B、帧 2 764 800 B、DDR 转储 B/G/R（登记，未改判）。J10 半屏黑 = **Wong 2026-10-24 范围外**（当前 J11/CMOS2）。
- 阶段4（w4）：已由 DSH 认领（`HANDOFF_OK` 9/0）；仍是**草案**（`S4-B r03`：`source_kind ∈ {file_injection,camera,synthetic}`；
  关联键 `contract_result_key=(session_id,frame_id,result_seq)`、`stage4a_join_key`、`ps_log_primary_key`、`uart_observable_key`）。
  **结果契约未冻结 ⇒ 真实彩色接入 NOT_RUN**；硬件使用权不随工作树交接。
- 硬件：阶段3 板级窗口自 2026-10-24 00:35 起**占用中** ⇒ 本轮不动硬件（无 JTAG/COM4/hw_server/位流/烧录；3121 未监听）。

## 本轮交付（S5-T03）
- 契约改绑：`docs/stage5/s5t03_input_contract_binding_v1.json` + `S5T03_input_contract_binding_colour_v1.md`
  ——范围标签 `camera_live_colour`→`source_kind=camera`（已对齐草案）、`camera_capture_replay_colour`→
  `file_injection|synthetic`（**`PROPOSED_PENDING_STAGE4_G0_CONFIRMATION`**，不新造枚举）、`synthetic_dynamic_reference`→`synthetic`；
  绑定阶段3 bit/XSA/ELF、1280×720/stride 3840/B-G-R、原图归一化坐标口径、阶段4 关联键、回放标注规则；**不改 S5A-G0-v2 任何阈值**。
- 冻结参数与用例骨架：`docs/stage5/s5t03_offline_skeleton_params_v1.json`（`FROZEN_BEFORE_RUN`，种子 `20261024`）+
  `S5T03_offline_case_skeleton_v1.md` + `scripts/stage5_t03/**`（`s5t03_display_pipeline/ s5t03_dynamic_stream/ test_s5t03_skeleton/ run_s5t03_evidence`）。
- 板级待验：`docs/stage5/S5T03_board_verification_pending_v1.md`（前置 P1–P7、待验 B1–B10、判定口径、窗口 A/B 申请材料、防误报清单）。
- 证据：`report/evidence/S5-T03/s5t03_takeover_20261024_r01/`（接管核对）、`…/s5t03_offline_skeleton_20261024_r01/`（骨架+清单）。

## 实测（本轮离线，合成动态流）
- 用例骨架 **24 项 / 0 失败 / 0 错误**（193.6 s，Python 3.12.10，种子 20261024）：坐标手算 5 例、越界/零面积、2 px 偶数线宽、
  120 帧五元组（顺序/迟到/跳帧/重复/乱序）、过期三边界（`==limit` 不过期、`limit+1` 过期且只计一次、显式 `stale_flag`）、
  零框≠过期、超时/错误/丢帧/无效记录分列、HUD13、长跑。
- 240 帧 mixed 计数：绘制 177 帧/468 框、stale_cleared 7、dup 8、ooo 8、zero_hand 7、timeout 14、error 7、drop 7、invalid 7、zero_area 89（计数全部可由事件日志复算）。
- 长跑（**离线虚拟时钟**）：106 573 帧、每帧恰一条 `overlay_commit`、虚拟时长 1 800 001 080 000 ns（30.000018 min）、时间戳单调、计数可复算。
- 交付检查器 `check_stage_delivery --mode evidence`：两个包均 **CHECKS_OK / exit 0**；`--mode inputs` 按 README **NOT_APPLICABLE**（上游接口未冻结，不伪造）。
- 既有合成源证据未被改写：`git diff --name-only 654c72e -- report/evidence/S5-A|S5-B|S5-C|S5-T01` 为空（exit 0）。

## 未决与风险
- `UR-1` 阶段4 写入方：在 S4-B G0 确认 `camera_capture_replay_colour` 的 `source_kind` 与 `carry_fields`。
- `UR-2` 阶段3 写入方：dbdf `t05_new_module_reverify_20261023_r01/README.md` 标题行写 `v9_read`、同文处置段写 `v10_read`（本树按重算绑定 v10 并请求更正）。
- `UR-3` Wong/正式 G0：成品允许延迟上限、颜色表与字号、阶段4 `stale_age_limit` 正式冻结。
- `UR-4` DSH：阶段4 结果冻结后按 `CDX-20261023-018` §3 发阶段5 硬件 OFFER（scope `S5-T02::s5_display_dynamic_mapping`，窗口 A≈2h + B≈1h）。
- 限制：阶段5 板级动态映射/过期边界/真实注入 30 分钟联调、T5-10 板上回归、`capture_fps` 实测、显示延迟物理测量一律 **NOT_RUN**；
  P1 现行「宿主预计算框」不得当作板上动态映射；无 ILA 不免除适用标准。

## 证据入口
- `report/evidence/S5-T03/s5t03_takeover_20261024_r01/`（含 handoff_check 原始 JSON、部署哈希重算、硬件快照）
- `report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r01/`（`summary.md`、`results_skeleton.json`、`console/**`、`delivery_manifest.json`、`hashes_sha256.txt`）
- 历史：`report/evidence/S5-A|S5-B|S5-C|S5-CTRL|S5-T01/**`（合成源结论原样保留，未重跑）
- 本轮提交：内容提交 `ba31126`；证据与 STATE 同批提交（见 `git log -1`）。

## 交接行（11 字段，2026-10-24 01:20）
任务=`task-22 阶段5 接续（全离线）：S5-T03 输入契约改绑真实彩色 + 坐标映射/帧关联/异常/长跑用例骨架 + 板级待验清单完成` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`654c72e` | 允许修改范围=`docs/stage5/**`、`scripts/stage5_t03/**`、`report/evidence/S5-T03/**`、`tmp/5/**`、`.gitattributes`、`.codex/STATE.md` | 未提交改动归属=`本树全部为本轮产物，与 STATE 同批提交（tmp/ 忽略项；无他人改动混入）` | 让出声明=`硬件未占用：0 个 hw_server/xsdb/vitis/xsim、3121 未监听、未加载位流、未烧 QSPI；**阶段3 板级窗口 2026-10-24 00:35 起占用中**，阶段5 板级须另行申请 OFFER；工作树写权仍由本阶段总控独占` | 心跳(UTC+8)=`2026-10-24 01:20` | 证据入口=`report/evidence/S5-T03/**`、`docs/stage5/S5T03_*`、`docs/stage5/s5t03_*` | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`IN_PROGRESS（S5-T03 离线部分完成；真实彩色接入待阶段4 结果冻结，板级待窗口）/ 本阶段总控`