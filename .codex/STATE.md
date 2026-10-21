# 阶段4 状态（摄像头推理 · 离线准备）

更新：2026-10-21 21:35（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`／起始 `8ee2530`（自 `main`）。规则见 `D:\FPGA_Competition\AGENTS.md`。
**本树只做阶段4 的离线准备，不是阶段4 正式开工、更不是阶段4 验收。** 真实摄像头联调与上板验收必须等阶段3 完成且 2B 让出硬件。

## 目标与范围

- 阶段4 正式目标（计划「阶段4：摄像头推理」）：摄像头→全帧缩放/补边/颜色/量化→PL 检测网络→PS 解码/NMS→UART；每条结果含 frame_id、检测数量、每框类别/分数/原图坐标、采集与结果时间、推理耗时、状态；无手=零框；候选框超限/丢帧/过期结果显式记录；≥1000 次有效推理形成基线，推理耗时与端到端延迟分别定义。
- 本树范围（离线、可独立验收）：
  - **S4-A** 阶段4 G0 草案：结果字段与 frame_id 语义、推理耗时 vs 端到端延迟定义、丢帧/超限/过期记录口径、沿用 2A 的 `score_threshold=0.25`／NMS IoU=0.45／每图≤15 框。
  - **S4-B** PS 侧解码/NMS + UART（s2bu 风格）集成骨架：复用 2A D9 语义，输入取自 2A 冻结张量/heads，可离线跑通的最小可执行链。
  - **S4-C** 离线回放与对拍工具：用 2A 冻结 109 样本与 CPU golden 做逐值/逐框比较，随机验证留种子、统计留样本数与口径。
  - **S4-D** 阶段5/6 规格草案（叠框布局与补边逆映射、坐标误差门槛口径、分数 vs 置信度用词、FPS/延迟测量起止事件；交互状态机与阈值表）。
- 明确不做：真实摄像头/HDMI 联调、上板、烧录、CNN 重训、改动 2A 冻结规格、改动 2B 接口正文、访问或争用 `hw_server`/JTAG/COM4。
- 只读禁止：主工作树 `D:\FPGA_Competition`、`w2b`、`dbdf`、`96a3`、厂商原件 `D:\FPGA\AX7Z020` 均不写、不改、不提交；不直写 `codex_mailbox/`、`dsh_mailbox/`。

## 上游冻结绑定（只读）

- 2A G0 规格：`docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md`（`G0_FROZEN`，SHA-256 `7C2C8684…71F230`）。tiny416／五类 `fist,palm,one,two_up,three`／RGB 416×416 CHW INT8。
- 机器清单：`report/evidence/S2A-T01/tiny416_model_manifest.json`（`9dd2477b…79453a`，22.2 MB，38 层形状/scale/地址、两头布局、CSR/memory 协议、算子测试计划）；`report/evidence/S2A-T01/fixed_test_samples.json`（`ccf741c1…a755eed`，109 样本，种子 20260922）。
- CPU 参考：`report/evidence/S2A-T25/cpu_layer_golden_index.json`（`cbda3f25…f0f6950d`，109×38 逐层整数张量索引，逐样本 `raw_stream_sha256`）；`report/evidence/S2A-T29/cpu_decode_nms_reference.json`（109 样本框参考、两头 `tensor_sha256`/scale、覆盖统计）。
- 张量分片：`report/evidence/S2A-T25/tensors/sample_000..108.zlib`（109 个、共 372.6 MB）**只存在于主树，git worktree 未物化**；本树脚本以绝对只读路径引用。
- D9 解码器（2A 冻结语义）：`verification/s1_t02_d9_yolo_decode.py` + `verification/s1_t02_d6_detection_metrics.py`；比较容限 score/坐标 ≤`1e-6`、离散字段必须完全相同（规格第 75 行）。
- 2B 物理/运输（仅接口定义冻结，**2B 尚未最终验收**）：`s2b-physical/1.0.0`（`w2b/docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md`）、`s2bu/1.1`（`…/s2b_board_transport.md`，40 B `S2BU` 头、op1/2/3/4、`<Q8I>` 响应）。若其正文变更，本树做适用回归。
- 2B 现有 PS 解码 C 参考（只读复用来源）：`D:\FPGA_Competition\w2b\verification\s2a_ps_decode_nms_reference.c/.h`。
- 阶段3 现状（dbdf）：实时直通成立、色彩未过（DVP MSB 缺失）、2026-10-21 19:53 起 `OFFERED` 待认领 ⇒ **真实摄像头输入当前不可用**。

## 已完成准备

- 开工核验（2026-10-21 21:24）：w4 干净、HEAD `8ee2530`、无 `index.lock`；主树 406 项脏属他人，本树未触碰；五棵树均无锁。
- 硬件边界核验：`hw_server` PID 28624（20:29 起）归 2B，未访问；无 vivado/xsim/重型进程；空闲物理内存 2.6 GB ⇒ 本树仅做轻量 Python/MinGW gcc。
- 工具可用性：Python 3.12.10、NumPy/OpenCV（按 2A runtime 记录）、`d:\mingw64\bin\gcc.exe`。

## 未决与风险

- T25 分片未在本树；若主树被移动/清理，S4-C 需改用其他冻结绑定并如实记录限制。
- 阶段3 色彩未过 ⇒ 阶段4 真实输入可用时间未知；本树不因此停滞。
- 2B 未验收；`s2bu/1.1` 正文若变更，UART 骨架需回归。
- 2A 规格第 75 行要求两头 INT8 字节完全相同后才解码；离线对拍必须先过字节比较再比框。
- D9 API 把 `score_threshold` 限制在 `[0.25,0.50]`；阶段4 G0 沿用 0.25，不改 2A 冻结值。

## 证据入口与下一步

- 证据：`report/evidence/S4-CTRL/<task_id>/<run_id>/`；临时产物：`tmp/4/<task_id>/<run_id>/`（`tmp/` 已 gitignore）。
- 下一步：按 S4-A→(S4-B/S4-C/S4-D) 顺序推进；每个小任务：差异核对→最小验证→只暂存本轮文件→在 `stage4-infer-prep` 提交→报告提交哈希/证据/限制/未验证项。

## 交接行（11 字段，2026-10-21 21:35）

任务=`S4-CTRL 阶段4 离线准备（G0 草案／PS 解码-NMS+UART 骨架／离线回放对拍／阶段5-6 规格草案）` | 负责人=`DSH 阶段4 离线准备总控` | 工作树/分支=`D:\codex-worktrees\w4` / `stage4-infer-prep` | 起始提交=`8ee2530` | 允许修改范围=`本树全部（docs/、verification/、scripts/、board/、vitis/、report/evidence/S4-CTRL/**、tmp/4/**、.codex/STATE.md）；主树/w2b/dbdf/96a3/厂商原件只读` | 未提交改动归属=`本树无他人未提交改动；主树 406 项与 w2b 151 项均非本树，不动` | 让出声明=`未让出：本树写权由本窗口独占；不接管阶段3 OFFERED、不争用 2B 硬件` | 心跳(UTC+8)=`2026-10-21 21:35` | 证据入口=`report/evidence/S4-CTRL/`、`tmp/4/` | 恢复命令=`git -C D:/codex-worktrees/w4 status --short; git -C D:/codex-worktrees/w4 rev-parse --short HEAD; git -C D:/codex-worktrees/w4 rev-parse --git-path index.lock; git -C D:/FPGA_Competition status --short \| wc -l` | 状态/下一接手方=`IN_PROGRESS / 本阶段4 离线准备总控（不越阶段边界；阶段4 正式开工须 Wong 授权且等阶段3 与 2B 让出硬件）`