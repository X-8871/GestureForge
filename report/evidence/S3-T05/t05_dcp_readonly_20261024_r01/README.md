# 部署 routed DCP 只读重跑（RunId `t05_dcp_readonly_20261024_r01`）

- 授权：DSH 项目总控（2026-10-24，用于替换 TIMING/I-O 报告里「本版既有报告」的口径并确认 `Timing 38-249` 归因）。
- 被开版本：**当前部署**（无补偿 SOF `7cb330685260ced3…`）的 `design_1_wrapper_routed.dcp`
  （sha256 `17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`），Vivado 2026.1，`xc7z020clg400-2`，Design State=Routed。
- **只读**：只 `open_checkpoint` + `report_*`/`check_timing`/`write_xdc`(导出)/`get_property`；不改设计、不重跑综合/实现、不写回 DCP、不碰板卡。
- 真实退出码：**v1=1（`-checks timing` 参数非法）→ v2=1（尾部自造查询 `get_exceptions` 不存在；报告均已产出）→ v3=0（干净）**；三次的日志与报告都保留（`v1_failed_partial_*`、`v2_*`、`v3_*`）。

## 结论入口
- **`dcp_readonly_findings.md`** —— 归因确认（38-249）、C2 确认、时序/方法论/例外来源与边界。
- 报告快照：`v3_clocks.rpt`、`v3_exceptions.rpt`、`v3_methodology.rpt`、`v3_timing_summary.rpt`、`v3_check_timing.rpt`、`v3_constraints_exported.xdc`；
  失败运行快照：`v1_failed_partial_clocks.rpt`、`v1_failed_partial_exceptions.rpt`；`v2_*` 为 v2 全量产出。

## 边界
本目录**不代表**时序签核通过、I/O 时序已验证、G2/G3/G4/G5 或阶段冻结；未修改任何约束。
