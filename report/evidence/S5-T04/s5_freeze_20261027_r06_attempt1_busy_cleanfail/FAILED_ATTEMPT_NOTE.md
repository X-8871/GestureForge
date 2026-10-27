# r06 首次尝试（未交付，保留为失败证据）

- 目录：`report/evidence/S5-T04/s5_freeze_20261027_r06_attempt1_busy_cleanfail/`
- 时间：2026-10-27 22:30–22:36 UTC+8
- 结果：`final_exit=1`；`build=0 verify=0(FROZEN_SET_VERIFIED 93) selftest=0(SELFTEST_PASS) suite=0(159) checker_M1/M2=0`
- 失败原因（两项，均为运行器自身门禁，非冻结集内容问题）：
  1. `quiet=BUSY`：外部 Agent 的 `hw_server.exe`（PID 25508）在跑；本卡为离线字节冻结，未连接/未加载位流/未烧录/未占用 JTAG，`vivado.exe` 缺失（未驱动硬件）。
  2. `clean=False`：本轮工具修订（`verification/verify_stage5_frozen_set.py`、`scripts/stage5_t04/{build_stage5_frozen_set,run_stage5_freeze_evidence}.py`）尚未提交。
-  推导：该包  无  字段（运行器未写），由 checks 推导——quiet BUSY(=FAIL) 与 worktree tracked_dirty(=FAIL) 任一失败即 ；本行即机器留痕说明（m5）。
- 处置：**不覆盖、不改写**该目录；先提交工具修订，再以 `r06` 正式重跑（安静窗口判据已在 r06 修订中分档：自有重型工具 fail-closed，外部 `hw_server` 只记录并留证）。本目录不构成冻结交付，仅作失败留痕。