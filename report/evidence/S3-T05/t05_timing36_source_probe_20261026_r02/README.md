# TIMING-36 生成时钟源与实际网络只读探测

- RunId：`t05_timing36_source_probe_20261026_r02`
- 执行时间：2026-10-26 12:21:33–12:22:07（UTC+8；Vivado 日志）
- 源工作树 HEAD：`beab61e1a987798774678fc05baae5dcff472b9d`
- 器件 / 设计：`xc7z020clg400-2` / `design_1_wrapper`，DCP 状态 `Routed`
- 工具：Vivado 2026.1，Build `6511674`
- 输入 DCP：`tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp`
- 输入 DCP SHA-256：`17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`
- 命令：`vivado.bat -mode batch -nojournal -source <probe_clocks.tcl>`；路径固定在脚本内，不依赖 `-tclargs`

## 范围与观察

本次只打开既有 routed DCP，查询时钟、引脚和网络，输出 `report_clocks`，然后关闭设计。未修改 XDC、网表或 DCP；未运行综合/实现；未接触板卡。脚本打印 `PROBE_RESULT=COMPLETE_READ_ONLY`，stderr 为空，Vivado 日志正常打印退出信息。执行编排层未返回数值化进程退出码，因此清单将其记为 `null`，不补猜退出码。

查询记录到：

1. `design_1_i/axi_dynclk_0/PXL_CLK_O` 与 `design_1_i/rgb2dvi_0/PixelClk` 同接 `design_1_i/axi_dynclk_0_PXL_CLK_O`；关联时钟 `axi_dynclk_0_PXL_CLK_O` 周期为 10 ns。
2. `design_1_i/rgb2dvi_0/SerialClk` 则接在另一条网络 `design_1_i/axi_dynclk_0_PXL_CLK_5X_O` 上；该引脚关联自动衍生时钟 `I`，周期为 2 ns。
3. routed DCP 导出的 `rgb2dvi_clocks.xdc` 对内部 `SerialClk` 另定义 `-source PixelClk -multiply_by 5` 的生成时钟。DCP 报告显示该生成时钟以 `axi_dynclk_0_PXL_CLK_O` 为 master；`report_methodology` 对应 `TIMING-36=1`，并指出 master clock 到 generated-clock source 没有上升/下降沿传播。`TIMING-30=1` 同时提示该生成时钟 master-source 选择次优。

本地连接关系与警告相符：实际 SerialClk 网络来自 `PXL_CLK_5X_O`，不是由 PixelClk 这条网络传播而来。结合 AMD 对 TIMING-36 的定义，这支持“IP 内部生成时钟约束与集成后实际时钟拓扑不匹配”的根因判断。此为针对该 routed DCP 的归因，不等同于最终修复。

## 修复方向与未闭合边界

下一步候选是在隔离的实现约束集中移除或替换这条 `PixelClk → SerialClk ×5` 约束，并保留由实际 `PXL_CLK_5X_O` 路径传播到 SerialClk 的 2 ns 自动衍生时钟。修改前须在隔离副本证明约束来源和使用范围；修改后必须重新完成适用的综合/实现、`report_clocks`、`report_methodology`、路径覆盖及输出约束检查，并独立复审。不得直接改写厂商源文件，也不得把“警告消失”单独当作时序签核。

本 RunId 只关闭“TIMING-36 实际 clock source/net 关联未定位”这一诊断问题；**TIMING-36 修复仍开放**，TIMING-17、TIMING-18、I/O delay、完整 G2/G3/G4/G5 和其他阶段3未闭合项不受影响。

## 官方方法依据

- [AMD UG906 2026.1：TIMING-36](https://docs.amd.com/r/en-US/ug906-vivado-design-analysis/TIMING-36-Invalid-Generated-Clock-due-to-No-Edge-Propagation)：要求检查 master clock 到 generated clock source 是否存在物理路径，并检查路径时钟弧及边沿传播。
- [AMD UG903 2026.1：About Generated Clocks](https://docs.amd.com/r/en-US/ug903-vivado-using-constraints/About-Generated-Clocks)：`create_generated_clock` 关联 master clock，时钟延迟通过生成时钟 source pin 与 master source pin 间路径追踪。
- [AMD UG903 2026.1：Supported SDC Commands](https://docs.amd.com/r/en-US/ug903-vivado-using-constraints/Supported-SDC-Commands)：列出 `create_generated_clock` 的 `-source`、`-master_clock`、倍频/分频等参数。

完整原始记录见同目录 `clocks.rpt`、`stdout.txt`、`stderr.txt`；`source_provenance.json` 绑定输入 DCP 与运行身份，`validate_probe_outputs.py` 对本结论使用的关键原始行作只读断言，`delivery_manifest.json` 绑定清单内文件哈希。
