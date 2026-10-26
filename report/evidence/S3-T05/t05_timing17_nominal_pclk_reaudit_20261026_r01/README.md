# TIMING-17 名义 PCLK 约束重分析（失败记录）

## RunId 与目的

- RunId：`t05_timing17_nominal_pclk_reaudit_20261026_r01`
- 时间：2026-10-26 14:18（UTC+8；Vivado 日志退出时刻 14:18:17）
- 基线：阶段3工作树提交 `110ddf1b5b3c2e2087afb7260a031a042a393a2c`；候选约束来自同一工作树未提交的 `an5642_j11_cmos2.xdc`。
- 输入 routed DCP：`report/evidence/S3-T05/t05_timing36_project_impl_20261026_r02/outputs/design_1_wrapper_routed.dcp`，SHA-256 `e5f5a429a1eff9e6602f3bca92cefdcca562f1ee39a8e2a0aba0351c58562a84`。该 DCP 属于隔离工程 R02，来源提交见该运行自身清单 `source_commit=5c6b2034862cc96f4f2f3b9929d874e034ba4af3`。

为使证据包自包含，本 RunId 内另存了字节级同哈希副本 `input_design_1_wrapper_routed.dcp`；本次 Vivado Tcl 实际读取的仍是上述原始路径。

## 实际操作与结果

本轮只打开已路由 DCP，在 Vivado 进程内读取候选 XDC 并检查 `cmos1_pclk` 对应时钟周期。没有综合、实现、路由、生成 bitstream、写回 DCP/XDC 或连接硬件。

Vivado 2026.1 将 XDC 的 `11.904762 ns` 周期按 1 ps 分辨率舍入为 `11.905 ns`。r01 Tcl 仍按近似 `11.904762 ns` 作严格断言，因此在读取时钟后以 `CMOS1_PCLK_PERIOD_MISMATCH=11.905`、Vivado 退出码 1 停止；未生成后续时序报告。这是断言容差与 Vivado 量化精度不匹配，不是设计或实现失败。原始 Tcl、stdout、stderr、日志和退出码均保留。

## 处置

不复用或改写本 RunId。更正断言以匹配 Vivado 的 1 ps 周期量化后，在新 RunId `t05_timing17_nominal_pclk_reaudit_20261026_r02` 重做只读重分析；r02 结果和限制见其 README。

此失败记录本身不证明候选约束正确、时序通过或阶段3可冻结。
