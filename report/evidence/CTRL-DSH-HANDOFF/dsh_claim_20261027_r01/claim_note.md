# main 写权认领说明（DSH 项目总控，2026-10-27）

## 1. 依据

- Codex 项目总控 `CDX-20261026-001-main-stage3-write-offer.md`（2026-10-26 19:05）：将 **main（项目总控与全局状态写权）** 与**阶段3**（`D:\codex-worktrees\dbdf`）OFFERED 给 DSH 项目总控；明示**不含** w4/w5/w6/w2b/96a3，且**不授权**新增编译、下载、烧录或板级活动。
- Wong 2026-10-27 直接指令：给出 `S4-B-REAL-02B::s4b_hardware_session_handoff` 硬件 OFFER 行，要求落盘（接收方 `Workbuddy 阶段4总控`，`hardware_run_id=s4b_ps_tensor_hw_20261027_r01`）。
- 阶段3 事实：已由 **DSH 阶段三总控**于 2026-10-26 以 `report/evidence/S3-T17/t17_takeover_20261026_r01/claim_record_offered_20261026.json` 完成认领（`handoff_check --claim` = `HANDOFF_OK` exit 0），并于 2026-10-26 收尾冻结（独立复审 `rev-s3` 最终 `PASS`；tag `stage3-close-20261026-r2` → `e287392`；判定「阶段3 收尾通过（带记录性局限）」）。**本次认领范围仅 main。**

## 2. 认领时核验（只读）

- `git rev-parse HEAD` = `bdb7a360916641382a04f018c668774543e45b8e`（与 OFFER 起始提交一致）。
- 无 `.git/index.lock`；无 `hw_server`/`xsdb`/Vivado/vitis/xsim 进程；3121 未监听。
- `handoff_check --worktree D:/FPGA_Competition`：提供本目录 `handoff_record.json` 后执行 `--claim`，结果见 `handoff_check_claim.stdout.txt`（真实退出码见该文件与 `handoff_check_claim.json`）。
- 未提交改动：main 424 项，属既有 Codex/用户历史改动与未跟踪产物；**DSH 只提交本轮相关文件**，不清理、不暂存、不回退其余内容。

## 3. 本次落盘内容

1. main `.codex/STATE.md`：主交接行改为 **CLAIMED（DSH 项目总控）**；新增**独立 11 字段硬件 OFFER 行**（`S4-B-REAL-02B::s4b_hardware_session_handoff`，OFFERED → `Workbuddy 阶段4总控`）；阶段3 行按已收尾冻结事实更正（此前主 STATE 行仍写"修复待审/未冻结"）。
2. 本认领记录目录（`dsh_claim_20261027_r01/`）。
3. `dsh_mailbox/DSH-20261027-001-*.md` 回执（含 OFFER 提交 SHA）。

## 4. 边界

- 本认领**不构成**技术验收；**不授权**任何编译、下载、烧录或板级活动（板级仍按 Wong 的窗口授权与既有门禁）。
- Codex 的 10-26 未提交 STATE 改动（阶段行更新与收尾快照）**原样接收并入库**，不修改其技术结论；仅对阶段3 行的时点口径按已冻结事实更正。
- w4/w5/w6/w2b/96a3 写权**不在**本次范围。