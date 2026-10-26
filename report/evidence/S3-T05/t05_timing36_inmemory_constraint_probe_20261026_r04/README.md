# TIMING-36/30 隔离内存约束诊断 r04

## 结果

本次在固定 routed DCP 上记录基线报告，再在 Vivado batch 内存中调用 `reset_timing`，重载 DCP 导出的 timing XDC 副本；副本只省略 `rgb2dvi_clocks.xdc` 中一条 `PixelClk → SerialClk ×5` 约束。没有写回 DCP/XDC。

R03 的原始日志、报告与脚本均保留。其 Tcl 把报告中标识的**文本出现次数**记为 `COUNT=2`，Reviewer 指出这与汇总表中该规则的告警数量 `1` 含义不同。R04 新 RunId 改为逐行解析 `report_methodology` 汇总表，stdout 与报告均记录规则数量，未覆盖 R03。

| 汇总表项目 | 重载前 | 重载后 |
|---|---:|---:|
| TIMING-36 | 1 | 0 |
| TIMING-30 | 1 | 0 |
| TIMING-17 | 240 | 240 |
| TIMING-18 | 1 | 1 |
| `SerialClk` 端口时钟 | `I`，2.000 ns | `I`，2.000 ns |
| 错误生成时钟对象 | 存在 | 不存在 |

结果支持以下**内存级诊断**：省略该 generated-clock 行后，TIMING-36/30 消失，端口的自动衍生 `I` 时钟保持 2 ns；TIMING-17/18 不变。它不是正式约束修复：没有修改可复现工程/IP 源文件，也没有重跑综合、实现或路由。后续必须把修正落实到实际工程约束输入，重跑适用实现和时序覆盖核查，并独立审查。

## 固定输入与工具

- routed DCP：`D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp`
- DCP SHA-256：`17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`
- timing XDC：`../t05_dcp_readonly_20261024_r01/v3_constraints_exported.xdc`
- XDC SHA-256：`b6ecb117565c2b8ce3b59757461c0cb590d9d47ea5d1e3fc432713ed7e8cbcd6`
- Vivado：2026.1 Build 6511674；器件 `xc7z020clg400-2`；BASIC 许可证（未读取许可证内容）
- `reset_timing` 语义见 AMD [UG835 Vivado Tcl Command Reference](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/reset_timing)：清除当前内存 timing constraints/view，之后须显式重载所需 XDC。本试验仅在隔离 batch 进程内操作。

## 复现与限制

工作树根目录执行 `vivado.bat -mode batch -nojournal -source report/evidence/S3-T05/t05_timing36_inmemory_constraint_probe_20261026_r04/probe_reset_timing_reload_xdc.tcl`。Tcl 从方法学报告的汇总行提取精确规则数量；`validate_probe_outputs.py` 核对 DCP/XDC 哈希、候选 XDC 的精确单行差异、退出码、日志计数、时钟和报告。

这不替代真实工程约束集核验、实现后 STA、完整路径覆盖、板级 I/O delay 或 G2/G3/G4/G5。TIMING-17、TIMING-18、I/O delay、task-11、VDMA 根因和板级复核仍未关闭；阶段3不得冻结。
