# 阶段4 状态（摄像头推理 · 离线准备）

更新：2026-10-21 22:30（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`／起始 `8ee2530`（自 `main`）。规则见 `D:\FPGA_Competition\AGENTS.md`。
**本树只做阶段4 的离线准备，不是阶段4 正式开工、更不是阶段4 验收。** 真实摄像头联调与上板验收必须等阶段3 完成且 2B 让出硬件。

## 目标与范围

- 阶段4 正式目标（计划「阶段4：摄像头推理」）：摄像头→预处理/量化→PL 检测→PS 解码/NMS→UART；每结果含 frame_id、检测数量、每框类别/分数/原图坐标、采集与结果时间、推理耗时、状态；无手=零框；候选超限/丢帧/过期显式记录；≥1000 次有效推理基线；推理耗时与端到端延迟分别定义。
- 本树范围（离线、可独立验收）：S4-A G0 草案、S4-B PS 解码/NMS+UART 骨架、S4-C 离线回放对拍、S4-D 阶段5/6 规格草案。
- 不做：真实摄像头/HDMI 联调、上板、烧录、CNN 重训、改 2A 冻结规格、改 2B 接口正文、访问或争用 `hw_server`/JTAG/COM4。
- 只读禁止：主工作树 `D:\FPGA_Competition`、`w2b`、`dbdf`、`96a3`、厂商原件均不写不改不提交；不直写 `codex_mailbox/`、`dsh_mailbox/`。

## 已完成的准备（全部已提交、全部经独立审查 PASS）

| 任务 | 交付物 | 最终证据 RunId | 审查 |
|---|---|---|---|
| S4-A G0 草案 | `docs/stage4/**`、`scripts/stage4_s4a/**` | `report/evidence/S4-A/s4a_draft_20261021_r05/` | rev-spec PASS |
| S4-B 解码/NMS+UART 骨架 | `vitis/stage4/**`、`scripts/stage4_s4b/**`、`verification/test_s4_ps_decode.py` | `report/evidence/S4-B/20261021_r13/` | rev-b PASS |
| S4-C 离线回放对拍 | `verification/s4_replay_compare.py`、`verification/test_s4_replay_compare.py`、`scripts/stage4_s4c/**` | `report/evidence/S4-C/s4c_replay_20261021_r05/` | rev-c PASS |
| S4-D 阶段5/6 规格草案 | `docs/stage5/**`、`docs/stage6/**` | `report/evidence/S4-D/s4d_spec_draft_20261021_r03/` | rev-spec PASS |

- 关键数字（真实退出码）：S4-A 自检 8/8 exit 0；S4-B gcc 0 error/0 warning、C 自检 11/11、链 104 PASS/0 FAIL、unittest 27 OK、官方检查器 CHECKS_OK；S4-C 全量 109/109 PASS、mismatch 0、最大误差 0.0、反例 exit 1；S4-D 自检 11/11（覆盖 49/49）、CHECKS_OK。
- 审查记录：`report/evidence/S4-CTRL/S4-C01/s4_ctrl_20261021_r02/reviews/*_independent_review.json`（绑定被审哈希；**不得**放进各任务 RunId 目录，否则破坏官方清单的目录一致性）。收尾记录：`report/evidence/S4-CTRL/S4-C01/s4_ctrl_20261021_r02/S4CTRL-20261021-002-stage4-offline-prep-closing-record.md`。

## 上游冻结绑定（只读）

- 2A G0 规格 `7c2c8684…`；模型清单 `9dd2477b…`；109 样本清单 `ccf741c1…`；T25 逐层索引 `cbda3f25…` + 分片恢复清单 `5352b2ef…`（109 个 / 390,700,998 B，逐片 SHA 校验通过）；T29 解码参考 `24361a13…`；D9 `94dacdac…`／D6 `4dcf0f7d…`。
- **关键裁决**：`candidate_count` = 阈值筛除后、15 框截断前、NMS 前（与 2B 冻结实现 `s2a_ps_decode_nms_reference.c` 及 T29 黄金一致）；`candidate_limit = 12675`（2B 宏 `S2A_T62_MAX_CANDIDATES` = tiny416 理论最大候选数，超限属 ERROR 硬错误、**不定义截断**）；弃用草案值 4096。
- 2B `s2b-physical/1.0.0`／`s2bu/1.1` 仅接口定义冻结、**2B 尚未验收**；阶段3 `dbdf` 19:53 起 `OFFERED`（实时直通成立、色彩未过）⇒ 真实摄像头输入不可用。

## 未决与风险

- **需 Wong 决策**：阶段4 的时间/丢帧/过期/状态字段超出 `s2bu/1.1` payload（正文只能由 2B 改）→ 选项 A 新增扩展帧 / 选项 B 仅 PS 侧记录；离线期按 B 推进，S4-B 已预留扩展但未启用；**不得据 B 宣称满足计划第 88 行**。
- 候选上限推导依赖 2B 的 C 文件（本合同未钉扎其 SHA），该文件变更须重新推导并回归。
- 阶段5 画面语义默认 B（最新结果叠加）、显示误差门槛、阶段6 阈值与时间参数 → 各自 G0 固定；`stale_age_limit`(200 ms 草案) 与 S5 `age_frame` 上限须同源一次固定。
- 遗留加固（非阻断）：`evidence_annotation` 未纳入自检；S4-C `--actual` exit 语义；C11 锚点强度；**禁止原地改写既有 RunId 产物**（S4-B r12 曾发生，已记入收尾记录）。

## 硬件与资源边界

- `hw_server` PID 28624（20:29 起）与 JTAG/COM4 归 2B，**未访问、未重启、未争用**；无 vivado/xsim 重型进程；本树只用轻量 Python + MinGW gcc；未接真实串口。

## 证据入口与下一步

- 证据：`report/evidence/S4-A|S4-B|S4-C|S4-D/<run_id>/`；跨方记录：`report/evidence/S4-CTRL/S4-C01/**`；临时产物：`tmp/4/<task>/<run_id>/`（gitignore）。
- 下一步（均需授权/上游条件）：① 等 Wong 对 UART 扩展决策；② 阶段3 完成后取得真实输入并做阶段4 正式 G0 冻结；③ 正式联调时用 S4-C 的 `--actual` 对拍板上 heads；④ 阶段5/6 各自开树并由其 G0 固定参数。

## 交接行（11 字段，2026-10-21 22:30）

任务=`S4-CTRL 阶段4 离线准备（A: G0 草案 / B: PS 解码-NMS+UART 骨架 / C: 离线回放对拍 / D: 阶段5-6 规格草案）` | 负责人=`DSH 阶段4 离线准备总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`8ee2530` | 允许修改范围=`本树全部（docs/、verification/、scripts/、vitis/、report/evidence/**、tmp/4/**、.codex/STATE.md）；主树/w2b/dbdf/96a3/厂商原件只读` | 未提交改动归属=`本树无他人未提交改动；主树与 w2b 的脏改动均非本树，未触碰` | 让出声明=`未让出：本树写权由本窗口独占；不接管阶段3 OFFERED、不争用 2B 硬件` | 心跳(UTC+8)=`2026-10-21 22:30` | 证据入口=`report/evidence/S4-A/s4a_draft_20261021_r05/`、`report/evidence/S4-B/20261021_r13/`、`report/evidence/S4-C/s4c_replay_20261021_r05/`、`report/evidence/S4-D/s4d_spec_draft_20261021_r03/`、`report/evidence/S4-CTRL/S4-C01/` | 恢复命令=`git -C D:/codex-worktrees/w4 status --short; git -C D:/codex-worktrees/w4 rev-parse --short HEAD; git -C D:/codex-worktrees/w4 rev-parse --git-path index.lock` | 状态/下一接手方=`IN_PROGRESS（离线准备四项完成并冻结；阶段4 正式开工须 Wong 授权且等阶段3 完成、2B 让出硬件）/ 本阶段4 总控；UART 扩展决策待 Wong`