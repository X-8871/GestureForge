# S6-E 离线准备 r08：checker 来源固定

- RunId：`s6e_jtag_readonly_prep_20261028_r08`；状态：`PREPARED_NOT_RUN`；时间：2026-10-28 UTC+8。
- w6 基线：`D:\codex-worktrees\w6` / `stage6-interact-prep` / `d04258fd0e88c220e3678950def82de192922f09`。
- 当前 scanner SHA-256：`f9af18ed4d9382254a9e81479186d13fa1247b92c14e4083fb609f85bfb238e1`；当前 test SHA-256：`76bed296affd86d355fcb6011eb3e0f9fe62777302c7f272b11364d414e5c43c`。

## 离线测试日志来源

本包 `offline_tests.log` 是 r07 同名日志的逐字节副本，SHA-256 均为 `f31531fc5d0069db35f8d960c9da4ad77b7def5c2d6fc89119098944bb964def`。r07 固定命令实际运行 40/40 PASS、exit 0、5.262 秒；本 r08 不重跑测试。该结果绑定上述当前 scanner/test SHA，原始记录仍保留在 `s6e_jtag_readonly_prep_20261028_r07`。

## 实际 checker 来源与命令

主仓当前版证据检查器：

- 完整路径：`D:\FPGA_Competition\verification\check_stage_delivery.py`
- 执行工作目录：`D:\FPGA_Competition`；`--project-root` 指向 `D:\codex-worktrees\w6`。
- 文件最后变更提交：`803fd98335c557e997fdc77c27b46c3edc504170`；main HEAD：`d6cb313898fc71f78a45a48ce6f4f6b6ab799ee7`。
- main HEAD blob OID：`7be1af75609e9fa29ca9afe5f8024d31545a3224`；blob SHA-256 与该路径磁盘字节 SHA-256 均为 `00350ac813e928c052e43a5237fdf7a9be79d75c952cf691318eeb1e9fceeb8e`。
- 实际命令：

```text
C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\FPGA_Competition\verification\check_stage_delivery.py --mode evidence --manifest report/evidence/S6-E/s6e_jtag_readonly_prep_20261028_r08/delivery_manifest.json --project-root D:\codex-worktrees\w6
```

主仓当前版 hash-basis 检查器：

- 完整路径：`D:\FPGA_Competition\verification\check_manifest_hash_basis.py`
- 执行工作目录：`D:\FPGA_Competition`；`--repo` 指向 `D:\codex-worktrees\w6`。
- 文件最后变更提交：`8f8e2e574f67aba8d36a6c7986756136f5ff3ebe`；main HEAD：`d6cb313898fc71f78a45a48ce6f4f6b6ab799ee7`。
- main HEAD blob OID：`2565d9a54d26ffc1392b5a3156ee8a9f004d5a21`；blob SHA-256 与该路径磁盘字节 SHA-256 均为 `10e3fe7121cc46665cfcd553dc5237833fe3134bc0dd00a8652d79fa290e85f6`。
- 实际命令：

```text
C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B D:\FPGA_Competition\verification\check_manifest_hash_basis.py --repo D:\codex-worktrees\w6 --paths report/evidence/S6-E/s6e_jtag_readonly_prep_20261028_r08/delivery_manifest.json --mode declared-only --json
```

旧 w6 checker 失败事实：`D:\codex-worktrees\w6\verification\check_stage_delivery.py`，w6 HEAD blob `79d1d8c7c2b43b7d58a5380b64685fe0b059bc23`，磁盘 SHA-256 `d043812712b1faf56f64351f55bac92c4781178fb0f5626c059fcd3948e57bae`，来源提交 `0725d9cf48aeed21d3ea445ef01575c16b68d950`。它在工作目录 w6 检查 r07 manifest 时因不识别新增 `hash_basis` 字段返回 exit 1，产生 5 个未知字段错误；没有文件哈希不一致。主仓当前 checker 随后对 r07 返回 `CHECKS_OK`/exit 0。本包会复测当前 checker 对 r08 的真实调用并记录退出码。

## 未关闭状态

- 现场租约仍被 `DSH-20261024-004-stage3-window-j10-scope-w4-takeover.md` 的无时间通知阻断；不猜测其与 DSH-010 释放记录的顺序。
- 主 STATE/w6 STATE 正式 S6E-JTAG-RO OFFER/CLAIM 行均缺失；当前执行器配置的 r06 Reviewer receipt 仍不存在。
- 硬件扫描 `NOT_RUN`：不启动 `hw_server`/`xsdb`，不连接或操作板卡。离线结果不代表 G3/G4/G5 或阶段验收。
