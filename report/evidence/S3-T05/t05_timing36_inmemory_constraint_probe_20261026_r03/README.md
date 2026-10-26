# TIMING-36/30 隔离内存约束诊断 r03

## 结果

在同一 routed DCP 上先记录原报告，再调用 Vivado `reset_timing` 清空当前会话的时序约束；随后重载该 DCP 导出的完整 timing XDC 副本，副本只省略了 `rgb2dvi_clocks.xdc` 中一条 `PixelClk → SerialClk ×5` 约束。全程没有写回 DCP 或 XDC。

前后报告显示：

| 检查项 | 原始 DCP | 内存重载后 |
|---|---:|---:|
| TIMING-36 | 1 | 0 |
| TIMING-30 | 1 | 0 |
| TIMING-17 | 240 | 240 |
| TIMING-18 | 1 | 1 |
| `SerialClk` 端口时钟 | `I`，2.000 ns | `I`，2.000 ns |
| 错误生成时钟对象 | 存在 | 不存在 |

这支持“该 XDC 关系是本版 DCP 中 TIMING-36/30 的直接来源；省略它不会丢失端口现有的 `I` 时钟”这一**内存级诊断**。它不是正式约束修复：没有改产品/工程源文件，也没有重跑综合、实现或路由。下一步应将修正应用到可复现的实际 Vivado 工程/IP 约束输入，在新 RunId 执行适用实现、完整时序覆盖核查及独立复审。

## 固定输入与工具

- routed DCP：`D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp`
- DCP SHA-256：`17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`
- 基线导出 XDC：`../t05_dcp_readonly_20261024_r01/v3_constraints_exported.xdc`
- 基线 XDC SHA-256：`b6ecb117565c2b8ce3b59757461c0cb590d9d47ea5d1e3fc432713ed7e8cbcd6`
- Vivado：2026.1 Build 6511674；器件 `xc7z020clg400-2`；BASIC 许可证（未读取许可证内容）
- `reset_timing` 的定义：AMD [UG835 Vivado Tcl Command Reference](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/reset_timing)。该命令清除当前内存时序约束/视图，需随后显式 `read_xdc`；本试验只在独立 batch 进程的内存设计中执行。

## 复现与限制

在工作树根目录以 `vivado.bat -mode batch -nojournal -source report/evidence/S3-T05/t05_timing36_inmemory_constraint_probe_20261026_r03/probe_reset_timing_reload_xdc.tcl` 执行；Tcl 固定 DCP 与基线 XDC。`validate_probe_outputs.py` 对基线哈希、单行变更、工具退出码、时钟对象及方法学表格作只读断言。

内存重载的约束导出不替代真实工程约束集核验、route、STA 完整性、板级输入/输出延迟或 G2/G3/G4/G5。TIMING-17、TIMING-18、I/O delay、task-11、VDMA 根因和板级复核仍未关闭；阶段3不得冻结。
