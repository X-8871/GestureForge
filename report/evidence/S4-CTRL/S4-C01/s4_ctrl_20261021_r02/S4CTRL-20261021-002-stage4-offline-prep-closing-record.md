# S4CTRL-20261021-002 阶段4 离线准备收尾记录

- 编号：`S4CTRL-20261021-002`
- 提出方：DSH 阶段4 离线准备总控（工作树 `D:\codex-worktrees\w4`，分支 `stage4-infer-prep`）
- 时间：2026-10-21 22:30（UTC+8）
- 性质：阶段4 **离线准备**收尾记录。**不是阶段4 正式开工、不是阶段4 验收、不是 G0 冻结**；不产生板上/实物结论。
- 前置：`S4CTRL-20261021-001`（跨方事项与请 Wong 决策项，指向同一决策）

## 1. 准备范围与完成状态

| 任务 | 交付物 | 最终证据（唯一权威 RunId） | 独立审查 |
|---|---|---|---|
| S4-A 阶段4 G0 草案（结果字段/时间口径/异常记录） | `docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md`、`docs/stage4/s4a_stage4_g0_fields.json`、`scripts/stage4_s4a/verify_s4a_draft.py` | `report/evidence/S4-A/s4a_draft_20261021_r05/` | rev-spec **PASS**（3 轮 CHANGES_REQUIRED 后） |
| S4-B PS 解码/NMS + s2bu 风格 UART 离线骨架 | `vitis/stage4/**`、`scripts/stage4_s4b/**`、`verification/test_s4_ps_decode.py` | `report/evidence/S4-B/20261021_r13/` | rev-b **PASS**（冻结源码哈希集 + r13） |
| S4-C 离线回放与对拍工具（109 样本 vs CPU golden） | `verification/s4_replay_compare.py`、`verification/test_s4_replay_compare.py`、`scripts/stage4_s4c/**` | `report/evidence/S4-C/s4c_replay_20261021_r05/` | rev-c **PASS**（初轮 + r05 增量） |
| S4-D 阶段5/6 规格草案 | `docs/stage5/**`、`docs/stage6/**` | `report/evidence/S4-D/s4d_spec_draft_20261021_r03/` | rev-spec **PASS**（2 轮 CHANGES_REQUIRED 后） |

独立审查记录（Lead 侧，绑定被审哈希）：`report/evidence/S4-CTRL/S4-C01/s4_ctrl_20261021_r02/reviews/S4-A_r05_independent_review.json`、`S4-B_r13_independent_review.json`、`S4-C_r05_independent_review.json`、`S4-D_r03_independent_review.json`。Reviewer 原始产物在 `tmp/4/review/<reviewer>/**`（未纳入版本库）。
教训：审查记录**不得**放进各任务 RunId 目录——官方清单检查器会因“运行目录文件未列入 files”报 CHECKS_FAILED；本次已迁到控制目录并复跑检查器（S4-B r13 与 S4-D r03 均恢复 `CHECKS_OK`）。
偏差登记：S4-C 证据未附官方格式 `delivery_manifest.json`（使用其自带 `s4c_run_manifest.json`，已由 rev-c 独立核验文件绑定与退出码）；如需统一格式，阶段4 正式开工时另行补齐。

## 2. 关键结果（真实执行，含退出码）

- **S4-A**：自检 `python -B scripts/stage4_s4a/verify_s4a_draft.py` → **exit 0（8/8 PASS）**；上游带 SHA 绑定 8 项 + 109 分片逐片 SHA + 16 项上游常量比对全部一致。Lead 侧变异自证：M0 exit 0，M1–M7/M11/M12/M21 全部 exit 1。
- **S4-B**：gcc 严格编译 **exit 0（0 error/0 warning）**；C 自检 **exit 0（11/11）**；离线链 **exit 0（104 PASS/0 FAIL/0 SKIP）**；`unittest test_s4_ps_decode` **exit 0（27 tests OK）**；官方清单检查器 **exit 0（CHECKS_OK）**。C vs 冻结 D9：离散字段完全相同、score/xyxy 最大绝对误差 **0.000e+00**；与 T29 黄金 0 mismatch；两头 INT8 进出等于冻结 `tensor_sha256`。
- **S4-C**：全量 109 样本对拍 **exit 0**，**109/109 PASS、mismatch 0、最大误差 0.0**，字节层 109/109 分片与两头摘要全 MATCH；反例（1 字节篡改）**exit 1** 且精确到字段与偏移；`unittest` **exit 0（36 tests OK）**。
- **S4-D**：自检 **exit 0（11/11，覆盖 49/49）**；官方清单检查器 **exit 0（CHECKS_OK）**；逆映射端点对齐往返偏差 0.000e+00；状态机 M15 分支经变异 Y1–Y6 证明无死状态。

## 3. 提交

`6a666ff`（STATE 重写）→ `ec10d1c`（S4-A r02）→ `7e5717f`（S4-A r05）→ `348fa67`（S4-C）→ `fc058f9`（S4-D）→ `c4b407b`（S4-B）→ 本次收尾提交（STATE + 收尾记录 + 审查记录）。全部在 `stage4-infer-prep`，**未 push**。

## 4. 硬件与边界（全程遵守）

- `hw_server`（`-s tcp::3121`，现场核验 PID 28624）与 JTAG/COM4 归 2B，本阶段**未访问、未重启、未争用**；未接真实串口；未启动 Vivado/xsim/综合/仿真；所有验证仅用轻量 Python 与 `d:\mingw64\bin\gcc.exe`。
- 未写主工作树 `D:\FPGA_Competition`、`w2b`、`dbdf`、`96a3` 与厂商原件；未认领阶段3 的 `OFFERED`；未直写两个 mailbox。

## 5. 未决项（需 Wong / 项目总控决策）

1. **UART 扩展决策（重大接口语义，S4CTRL-20261021-001 第 1 条）**：阶段4 需记录的时间/丢帧/过期/状态字段超出 `s2bu/1.1` 现有 payload，而该正文只能由 2B 修改。选项 A（新增扩展帧，需协调 2B）或 B（仅 PS 侧记录）。**离线期按 B 推进**，S4-B 已为扩展预留位置但**未启用**；不得据 B 宣称满足阶段计划第 88 行。
2. 阶段5 画面语义默认「最新结果叠加(B)」、显示像素误差门槛、FPS/延迟测量起止事件、阶段6 三项目标阈值与全部时间参数 → 各阶段 G0 固定。
3. `stale_age_limit`(草案 200 ms) 与 S5 的 `age_frame` 上限必须**同源一次固定**（S4-D 已写入该约束）。
4. 阶段4 正式开工须等阶段3 完成（当前 `OFFERED`，实时直通成立、色彩未过）且 2B 让出硬件。

## 6. 遗留加固清单（均为非阻断，编辑会使已 PASS 字节集失效，故本轮不改）

- S4-A：`evidence_annotation` 块未被自检守护；2B C 参考 `S2A_T62_INVALID_ARGUMENT(-1)` 与 CSR `BAD_ARGUMENT(1)` 的映射可加注；自检第 6 项为子串检查（已披露）。
- S4-B：r12 清单曾**原地重写**（26→27 文案）—— 后续禁止原地改写既有 RunId 产物，必须另起 RunId；`measurement_scope` 保留一枚说明性 `note` 键；候选超限分支不可达仅源码级确认。
- S4-C：`--actual` 输入类错误的 exit 语义（1 vs 2）需二选一写明；旧 manifest 路径字符串；容限边界 float64 细节；D9/D6 的 CRLF↔LF 等价结论未落证据（Lead 结论：同一文本、不同行尾，无语义分叉）；acceptance 键名与步骤名不对应。
- S4-D：C11 属锚点存在性检查（可加负向断言）；M15 出口集合第二项略冗余；帧日志建议加 `acquisition_triggered` 标记。

## 7. 未执行项（NOT_RUN，不写成通过）

真实摄像头/HDMI 联调、板卡上电与 PL 加载、真实串口/UART 收发、JTAG/DAP、PL 推理时间与期限/吞吐实测、Vivado/xsim/综合/仿真、109 样本之外的整网重跑、2B 实板验收、阶段3 色彩修复、G3/G4/G5 与阶段4 验收。

## 8. 本文件的使用限制

本文件是阶段4 工作树内的控制记录，**不代表工作树写权交接**，不授予任何方修改对方信箱、主 STATE、阶段 STATE、业务代码或操作硬件的权限；不覆盖、不修改、不删除旧记录。