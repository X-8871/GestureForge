# 本目录状态：仅离线准备，**尚未实测**（勿当作阶段 B 证据）

- 任务：`task-17` 阶段3 色彩复测；工作树 `D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，基线 HEAD `f94c25f`。
- 本目录**当前只有阶段 A 的离线产物**：
  - `run_log.txt`：执行器在 `preflight` / `judge` 阶段写入的运行日志（离线）；
  - `preflight.json`：离线前置检查结果（`OFFLINE_GO`，7 件冻结产物哈希一致，`hardware_window_confirmed=false`）；
  - `judge_manual.json`：对**上次归档**彩条帧的离线判定往返（`DEFECT_REPRODUCED`，退出码 1），用于验证判定器。
- **未执行**：`link` / `baseline` / `bars` 三个硬件阶段。本轮**未接触硬件**（无 JTAG/COM4/hw_server/烧录）。
- 硬件阶段的前置条件（同时成立才放行，否则执行器退出 3）：
  1. Wong 的开工信号；
  2. 硬件窗口书面让出/时间窗确认（`dsh_mailbox/DSH-20261023-013` 已发出请求，Codex 侧回执到位后据此填写
     `report/evidence/S3-T17/hw_authorization.json`，模板见 `../t17_color_retest_prep_20261023_r01/evidence_template/`）。
- 阶段3 颜色子项在实测证据与独立审查完成前保持 `DEFERRED_PENDING_MODULE`，**不得**据本目录宣称颜色通过。