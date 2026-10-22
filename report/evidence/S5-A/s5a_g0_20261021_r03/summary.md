# S5-A 自检证据 RunId `s5a_g0_20261021_r03`

- 契约：`S5A-G0-v2`（STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED）
- 工作树：`D:\codex-worktrees\w5` 分支 `stage5-display-prep` HEAD `acd2df6`
- 自检：`python -B -m unittest verification.test_s5_display_geometry_reference -v` → **退出码 0**（Ran 26 tests in 0.005s）
- 复制基线逐字节一致：5/5
- 状态：**PASS**

## 限制与未执行

- 纯离线：无硬件、无 hw_server/JTAG/COM4、无 Vivado/xsim、无摄像头与 HDMI 实物。
- 只验证几何/口径/契约自洽与手算样例；不构成阶段5 开工、G1/G3/G4 或验收通过。
- 阶段4 S4-A 契约仍为 DRAFT_NOT_FROZEN；阶段5 契约引用其字段名不等于阶段4 已冻结。
- 真实 FPS/延迟统计、30 分钟无死锁、截图/视频留证均未执行。
- T5-09 连续 30 分钟无死锁（需硬件与阶段3/4 完成）
- 真实 HDMI 显示与摄像头联调（阶段5 正式开工后）
- 成品允许延迟上限/颜色表/字号（待正式 G0 与 Wong）

## 证据文件

- `console/unittest_s5a.txt`（真实 stdout/stderr 与退出码）
- `console/git_state.txt`（分支/HEAD/status/index.lock）
- `run_manifest.json`（哈希绑定、命令、退出码、检查项、限制）
- `summary.md`（本文件）
