# TIMING-17 名义 PCLK 约束重分析

## RunId 与输入绑定

- RunId：`t05_timing17_nominal_pclk_reaudit_20261026_r02`
- 时间：2026-10-26 14:19（UTC+8；Vivado 日志退出时刻 14:19:35）
- 工作树基线：`D:\codex-worktrees\dbdf`，分支 `codex/stage3-video`，HEAD `110ddf1b5b3c2e2087afb7260a031a042a393a2c`。
- 候选约束：工作树 `board/stage3/hardware/an5642_j11_cmos2.xdc`（本轮未提交差异，SHA-256 `d1d3e976f84e0aa5a67ff695d07c83983cf32887c463d6bf25250821f64aa595`）。注释把 84 MHz 标为名义 STA 假设：依据初始化配置注释和既有传感器寄存器回读，PCLK 没有仪器实测；不能据此宣称正式时钟签核。
- 输入 routed DCP：`report/evidence/S3-T05/t05_timing36_project_impl_20261026_r02/outputs/design_1_wrapper_routed.dcp`，SHA-256 `e5f5a429a1eff9e6602f3bca92cefdcca562f1ee39a8e2a0aba0351c58562a84`。DCP 来自隔离工程 R02，其构建来源提交为 `5c6b2034862cc96f4f2f3b9929d874e034ba4af3`，详见该运行的 `delivery_manifest.json`。
- 第一次分析 r01 因断言未容纳 Vivado 1 ps 周期量化而停止；r01 失败文件保留，未覆盖。

为使证据包自包含，本 RunId 内另存了字节级同哈希副本 `input_design_1_wrapper_routed.dcp`；本次 Vivado Tcl 实际读取的仍是上述原始路径。

计数对照基线为同一隔离实现的 `timing_summary_routed.rpt`（SHA-256 `26b75e38fa477b00a3fd8ee32d7cea91744a4a911de27150c31a455ced3a91f4`）和 `methodology_routed.rpt`（SHA-256 `0f1c98c7d854aa77dcc7ab46018b516e79d1b90426ec64de54f52b1484d124b8`）；两者未应用本次 PCLK 候选约束。

## 操作范围

Vivado 2026.1 Build 6511674 打开上述已路由 DCP，在独立进程内读取候选 XDC、运行 `update_timing`，并输出 clock、methodology、timing summary、clock interaction 四份报告。Vivado 将 `11.904762 ns` 舍入为 `11.905 ns`（约 83.998 MHz），Tcl 已按该量化值验证。进程退出码为 0。没有综合、实现、重新路由、生成 bitstream、写回 DCP/XDC 或连接/操作硬件。加载 routed DCP 报告峰值内存约 1.64 GB。

## 结果

与同一 routed DCP 原始时序摘要比较，名义输入时钟被接受后：

- `check_timing no_clock`：240 → 0。
- `unconstrained_internal_endpoints`：520 → 0。
- 仍缺 9 个输入延迟和 5 个输出延迟；方法学报告有 12 条 TIMING-18，不能把它们当作已约束。
- 全局 WNS = -4.785 ns（1 个 setup failing endpoint），WHS = -0.015 ns（1 个 hold failing endpoint）；Vivado 明确报告 `Timing constraints are not met`。
- TIMING-16 的 -4.785 ns 路径从 `alinx_ov5640_0/inst/fifo_ready_reg/C`（CMOS1_PCLK）到 `fifo_ready_maxis_reg/D`（`clk_fpga_1`）。报告还列出 CMOS1_PCLK 与 `clk_fpga_1` 被关联计时，但无共同主时钟、无共同节点、无共同周期（TIMING-6/7/8 各 1）。时钟域关系与 CDC 语义须进一步核实，不能通过随意加 false-path/clock-group 来消除告警。
- `report_clock_interaction` 将 `CMOS1_PCLK → clk_fpga_1` 归类为 `Partial False Path (unsafe)`；需查清该部分例外的来源和同步器结构，再决定时钟域建模，不能把此标签当成安全豁免。
- `CMOS1_PCLK` 时钟本身的 WNS 为 +6.947 ns，但它不能代表全设计通过；关键跨时钟 setup/hold 和 I/O 延迟缺口仍在。

## 判定与后续

本结果表明名义 create_clock 能消除当前 DCP 中相应的无时钟/未约束内部端点计数，同时暴露出跨时钟路径违例；它只适用于所测隔离 routed DCP 和当前候选约束，不等于正式工程重建、完整 STA signoff 或板卡实测。TIMING-17 不能仅凭计数降为 0 判为关闭；仍须先由设计证据澄清 CMOS1_PCLK 与 `clk_fpga_1` 的关系，并补足输入/输出延迟依据，再在可复现正式构建中重跑完整方法学与时序检查。

本轮不关闭 TIMING-36/30 正式工程修复、I/O delay、VDMA `SOFLateErr` 根因、task-11 完整顺序等价、G3 当前板级身份/画面/运行期地址，也不关闭阶段3 G5。该 DCP 是 TIMING-36 隔离实现 R02 的输出，不是当前板上部署位流的身份凭证。
