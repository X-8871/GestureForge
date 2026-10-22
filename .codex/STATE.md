# 阶段5 状态（HDMI 结果显示·离线准备 + S5-T01 上板 bring-up）

更新：2026-10-22 18:50（UTC+8）。工作树 `D:\codex-worktrees\w5`／分支 `stage5-display-prep`；规则见 `D:\FPGA_Competition\AGENTS.md`。
阶段5 **离线准备已完成**（规格定稿 + 离线渲染/叠框自测 + 阶段4 数值链路回归勾连 + 阶段6 建议）；**S5-T01 上板 bring-up 正在执行**。离线准备与 S5-T01 均**不是阶段5 验收**（G0/G1/G3/G4/G5 未通过）。

## 目标与范围（离线、可独立验收）
- A 阶段5 契约/G0 定稿；B 离线渲染/叠框自测工具与用例；C 与阶段4 数值链路回归勾连；D 阶段6 草案修订建议（只建议）。
- **明确不做**：CNN 改动、改 2A 冻结规格、改 2B 接口正文、改 w4 已交付、写主树/w4/dbdf/w2b/96a3/厂商原件、写两个 mailbox 目录。

## 上游绑定（只读）
- 主 STATE `D:\FPGA_Competition\.codex\STATE.md`（阶段5 入口行 HL-T13）；起始提交 `acd2df6`。
- 阶段4 冻结树 `D:\codex-worktrees\w4`（`73c3dad`，四项准备各经独立审查 PASS）：v1 草案（按原文复制，出处 `docs/stage5/PROVENANCE_s4d_v1_baseline.md`）、S4-A G0 草案（`3524d02a…`，DRAFT_NOT_FROZEN）、S4-B `20261021_r13` PASS、S4-C `s4c_replay_20261021_r05` PASS（109/109、误差 0，`c5d25c64…`）。
- **Wong 已定**：① 超 `s2bu/1.1` payload 的结果/耗时/丢帧/过期/状态字段按**方案 B 只记 PS 侧**（扩展帧待与 2B 协商）；② 画面语义固定**最新结果叠加**；③ **2026-10-22 15:12 选方案 B**：S5-T01 采用 **PS 合成视频源 + 软件叠框**（零新增 PL），因为摄像头模块不在位（I2C 全 0xFF）。
- 阶段3（只读）：实时直通与帧同步成立，**颜色受阻且根因收敛为硬件**（DVP `cmos_d[9]` 无信号），阶段未验收 → 真实采集路径不可用于本阶段结论。

## 已完成（离线准备交付）
- **S5-A**：`docs/stage5/S5A_stage5_display_g0_spec_v2.md` + `docs/stage5/s5a_stage5_display_g0_fields.json`（契约 `S5A-G0-v2`）+ `verification/s5_display_geometry_reference.py`（唯一几何/口径来源，`4d9fe369…`，与 D2 冻结实现逐值对拍）+ 自检 26/26 PASS、退出码 0；证据 `report/evidence/S5-A/s5a_g0_20261021_r03/`（**权威**）。
- **S5-B**：`scripts/stage5_s5b/**`；21 用例、583/583 断言、种子 20261021、随机 round-trip N=64/几何、手算样例 3、五元组 129、HUD 13/13、26 PNG + 21 JSON、双 pass 逐文件 SHA256 一致；证据 `report/evidence/S5-B/s5b_20261021_r07_a|_b`（权威）。
- **S5-C**：`scripts/stage5_s5c/**`；109/109 样本、104 框、最大 score/坐标误差 0、最大像素往返 0.499 px（门槛 1.0）、S4-B 3/3 与 S4-C 一致、8 个篡改探针全部检出（真实退出码 1）、正对照 0、unittest 27 项 0；证据 `report/evidence/S5-C/s5c_regression_20261021_r04`（权威）。
- **S5-D**：`docs/stage6/S6D_stage6_revision_suggestions_from_stage5.md`（5 条建议，未改 w4 草案）。
- **独立审查**：第 1 轮 `CHANGES_REQUIRED`（3 项）→ 第 2 轮聚焦关闭 **PASS**（F-01/F-02/F-03 CLOSED）；记录 `report/evidence/S5-CTRL/S5-R01/s5r01_20261022_r01|_r02/`。
- **收尾与机器清单**：`report/evidence/S5-CTRL/S5-A01/s5_ctrl_20261022_r02/…closing-record.md`；交付清单 `report/evidence/S5-A/s5a_g0_20261021_r03/delivery_manifest.json`（`check_stage_delivery.py --mode evidence` exit 0 / CHECKS_OK，SHA `6b3176cf…`）。
- **提交链**：`0b942ed`→`ff8d78c`→`256fc98`→`637e517`→`a4baab4`（离线准备定稿）。

## S5-T01 上板 bring-up（执行中：PS 合成源叠框已跑通并逐像素核对）
- **更正（2026-10-22）**：先前"JTAG 链为空／疑板卡未上电"的判定**错误并已正式撤回**：① 裸 `targets` 在输出重定向下不打印表格却被我当作判据；② 我方 grep 把链行从自己的输出里过滤掉。按 Wong 配方程序化复核得 **16 目标**、链 = `JTAG-HS1 210512180081 + arm_dap(4ba00477) + xc7z020(23727093)`、两 A9 核 `Running`。更正记录 `report/evidence/S5-T01/s5t01_board_20261022_r01/CORRECTION_chain_not_empty.md`；复核证据 `report/evidence/S5-T01/s5t01_scan_recheck_20261022_r01/`。
- **门禁依据**：Wong 2026-10-22 13:25 显式授权上板（`operator_authorization`，已留痕）；信箱仍无 2B 书面让出，**不伪造**信箱记录。
- 已执行：冻结灰度位流（`44e609cc…c4afb`，**易失**下载）+ 阶段3 v12 图案 ELF（无传感器 ⇒ 图案写失败、`0x503D` **未被改变**，无需恢复）。未烧 QSPI；每次用完清理 `hw_server` 不驻留。
- **P1 应用（方案 B）**：`scripts/stage5_t01/p1_app/s5_overlay.c`（PS 直接把合成图 + **预计算框**写入阶段3 应用送显缓冲 `pFrames[3]`；板上**无逆映射逻辑**）+ 生成器 `gen_overlay_cases.py`（框像素由冻结参考实现算好嵌入）+ 最小补丁 `apply_p1_patch.py`（1 行，仅锚点唯一时插入）+ 构建 `build_p1_app.sh`（0 警告）。ELF：循环版 `9f5e6db1…`(r02)、单用例5 `dd350c8a…`(r02)。
- **视觉证据（Wong 拍摄 7 张，六用例全覆盖）**：`report/evidence/S5-T01/s5t01_board_overlay_20261022_r01/photos/` + 逐用例记录 `case_photo_evidence.json`。
- **逐像素数值核对 13/13 PASS**：`report/evidence/S5-T01/s5t01_board_numcheck_20261022_r01/console/decode_rows.json`（红框左/右边界 x=0,1 与 x=77,78；绿框左边恰 `[513,514]`、底边行 66；斜坡 x=560→111、x=1264→252；三缓冲白角标记）。
- **机上项验收表**：`report/evidence/S5-T01/s5t01_board_numcheck_20261022_r01/acceptance_table.json` = **PASS 6 / PARTIAL 1 / NOT_RUN 3 / NOT_VERIFIED 1 / FAIL 0**。
- **未做/未测（如实）**：`display_fps`/延迟 **NOT_VERIFIED**（置 `FrmCntIrqEn` 后 `SR` 仍 `0x00011000`、计数不推进 ⇒ 需 GIC 中断计数或换帧完成事件；**未报任何数值**）；T5-05 ≥100 帧 frame_id 五元组、T5-09 30 分钟、T5-11 故障计数 **NOT_RUN**；T5-04 边界（`age==limit`/`limit+1`）板上 **NOT_RUN**（离线已覆盖）。
- 缺陷：D-1 背景 u8 回绕黑带 → **已修**（平滑斜坡，数值可证）；D-2 标签与 HUD 压盖 → **已修**（避让 + HUD 置顶；副作用：HUD 覆盖用例5 红框顶边 x 23..123，已记录）。

## 未决与风险
- 待正式 G0/Wong：成品允许延迟上限、颜色表/字号；契约 `discrete_fields_must_match` 拆分（F-01 根因）；阶段4 `stale_age_limit` 仍 `DRAFT_PROPOSED`（阶段5 已按**同源同一常量 200 ms** 使用）。
- 过程缺陷（已登记）：S5-C r01/r02 曾被删除（`report/evidence/S5-C/EVIDENCE_RETENTION_INCIDENT.md`）；`dev-s5b`/`dev-s5c` 重跑失败由 Lead 代执行（Reviewer 独立复现）；首版交付清单被检查器拒绝（exit 2、41 条）保留为失败证据；EOL 归一化导致 4/12 绑定不一致 → 已按 `.gitattributes -text` + `--renormalize` 修复为 12/12。
- 硬件：板卡在线（`xc7z020` idcode `23727093`）；**摄像头模块不在位/不响应**（I2C 全 0xFF）⇒ 本阶段视频源为 PS 合成图；他人硬件服务不得干扰（本树只用自建 `hw_server` 并及时清理）。

## 证据入口
- `report/evidence/S5-A/s5a_g0_20261021_r03/`、`report/evidence/S5-B/s5b_20261021_r07_a|_b/`、`report/evidence/S5-C/s5c_regression_20261021_r04/`、`report/evidence/S5-CTRL/`
- S5-T01：`report/evidence/S5-T01/s5t01_board_overlay_20261022_r01/`（含 `photos/`、`case_photo_evidence.json`）、`report/evidence/S5-T01/s5t01_board_numcheck_20261022_r01/`（含 `acceptance_table.json`、`console/decode_rows.json`）、`report/evidence/S5-T01/s5t01_board_20261022_r01/CORRECTION_chain_not_empty.md`
- 临时产物与历史运行：`tmp/5/<task_id>/<run_id>/`（按 `.gitignore` 不入库）。

## 下一步
1. **§0 门禁修复（BI-1/BI-2 已关闭，待复审）**：v2 登记表驱动 + schema 强校验（缺席/缺 sha256/重复登记/kind 非法/缺 order_key/前缀不符/跨信箱 order_key 重复 全部 BLOCKED）+ 未登记文件**文件名或正文**含交接语义即 BLOCKED；28 项隔离合成测试 **28/28 PASS、exit 0**；真实只读门禁 **exit 0 / GO / RELEASED**（效力待复审）；证据 `report/evidence/S5-T01/s5t01_gate_fix_20261022_r01/`（含 `REVIEW_r01_CHANGES_REQUIRED.md`）。
2. **§3 四 FPS 已实测（r04）**：`display_fps=59.206`、`video_refresh=118.351 事件/s ÷ 2 = 59.175 帧/s`（两独立事件源相对差 0.05%）、`inference_fps=NA`、`commit→首帧完成 0.22–9.1 ms`；`unique_frame_update_fps` 仅用例级（frame_id 级待 T5-05）；证据 `report/evidence/S5-T01/s5t01_board_fps4_20261022_r02/`。
3. HUD/UI 复核（§2.4/§5.4）：HUD **13 字段**（无摄像头 `capture_fps=NA`、无阶段4 `inference_fps=NA`，缺失值不得用 0 伪装）；标签/HUD 布局改**宿主端生成**并量化遮挡（现状：HUD 置顶会覆盖与用例5 红框顶边 x 23..123，需按布局规格判定）。
4. T5-05：≥100 帧顺序结果 + `frame_id` 五元组（唯一能给出 frame_id 级 `unique_frame_update_fps` 的途径）。
5. T5-11 故障计数；T5-09 30 分钟长跑；收尾出 S5-T01 收尾记录与清单。
6. **板卡已明确让出**（`report/evidence/S5-T01/s5t01_board_release_20261022_r01/`）：无 `hw_server`、COM4 未占、未烧 QSPI、`0x503D` 未改。

## 交接行（11 字段，2026-10-22 19:45）
任务=`HL-T13 阶段5 离线准备（完成）+ S5-T01 上板 bring-up（执行中：PS 合成源叠框 13/13 像素、四 FPS 实测 59.2、§0 门禁 BI-1/BI-2 已关闭待复审；HUD 13 字段/≥100 帧/长跑未做）` | 负责人=`DSH 阶段5 总控` | 工作树/分支=`D:\codex-worktrees\w5`/`stage5-display-prep` | 起始提交=`acd2df6`（S5-T01 基线 `a4baab4`） | 允许修改范围=`docs/stage5/**`、`scripts/stage5_*/**`、`report/evidence/S5-*/**`、`tmp/5/**`、`.codex/STATE.md` | 未提交改动归属=`本树全部为本轮产物，与 STATE 同批提交（tmp/ 为忽略项；无他人改动混入）` | 让出声明=`**板卡已让出**：S5-T01 本轮硬件使用结束，JTAG/COM4 交还空档（无 hw_server、COM4 未占、未烧 QSPI）；工作树写权仍由本阶段总控独占（S5-T01 IN_PROGRESS）` | 心跳(UTC+8)=`2026-10-22 19:45` | 证据入口=`report/evidence/S5-T01/s5t01_gate_fix_20261022_r01/`、`report/evidence/S5-T01/s5t01_board_fps4_20261022_r02/`、`report/evidence/S5-T01/s5t01_board_release_20261022_r01/` | 恢复命令=`git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short` | 状态/下一接手方=`IN_PROGRESS（S5-T01：等 §0 复审→HUD 13 字段→T5-05 五元组→T5-11/09→收尾；板卡已让出）/ 本阶段总控`