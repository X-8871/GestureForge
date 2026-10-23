# 部署 routed DCP 只读重跑结论（2026-10-24，RunId `t05_dcp_readonly_20261024_r01`）

## 0. 被开版本与命令（可复跑）

| 项 | 值 |
|---|---|
| DCP 路径 | `tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp` |
| DCP sha256 | `17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`（6,975,438 B；与同目录部署 `.bit` `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710` **同一 impl_1 目录**） |
| 器件/工具 | `xc7z020clg400-2`、Vivado 2026.1、Design State = **Routed** |
| 命令 | `git-bash: bash tmp/3/S3-T05/t05_dcp_readonly_20261024_r01/run_dcp_readonly.sh <routed.dcp> <out_dir> <tcl>` ⇒ `vivado -mode batch -source <tcl> -tclargs <dcp> <out>` |
| 只读边界 | 仅 `open_checkpoint` + `report_*` / `check_timing` / `write_xdc`（导出）/ `get_property`；**未**改设计、**未**重跑综合/实现、**未**写回 DCP、**未**碰板卡 |
| 前置冲突核对 | 开跑前 `Get-Process vivado|xsim|xsdb` = **空**（无他方会话争用） |

## 1. 三次运行的**真实退出码**（含失败，不掩盖）

| 运行 | 真实退出码 | 说明 |
|---|---|---|
| v1 | **1** | `report_clocks`/`report_exceptions` 成功并留存；`report_methodology -checks timing` 报 `ERROR: [Vivado_Tcl 2-1516] Invalid Methodology rule name 'timing'` ⇒ 该参数在本版非法；原始日志与部分报告**保留**（`v1_failed_partial_*.rpt`） |
| v2 | **1** | 全部报告与 `ATTR_*` 查询**均已产出**；失败点仅在脚本尾部我自造的查询 `get_exceptions`（本版**无此命令**：`invalid command name "get_exceptions"`）⇒ 属**查询编写缺陷**，非设计/工具失败；报告留存（`v2_*.rpt`） |
| v3 | **0** | 修正尾部查询后干净通过：`STEP_OK=OPEN/REPORT_CLOCKS/REPORT_EXCEPTIONS/REPORT_METHODOLOGY/REPORT_TIMING_SUMMARY/CHECK_TIMING/WRITE_XDC`、`DCP_REPORT_ALL_DONE=1`、`VIVADO_EXIT=0`；报告 `v3_*.rpt` |

## 2. `Timing 38-249` 归因：**已确认**（原为假设）

`report_clocks` 在本 DCP 上的实测（`v3_clocks.rpt`）：

```
Generated Clock     : design_1_i/rgb2dvi_0/U0/SerialClk
Master Source       : design_1_i/rgb2dvi_0/U0/PixelClk
Master Clock        : axi_dynclk_0_PXL_CLK_O
Multiply By         : 5
Generated Sources   : {design_1_i/rgb2dvi_0/U0/SerialClk}
```

同时批处理日志逐字给出（三次 update_timing 各一次）：

```
CRITICAL WARNING: [Timing 38-249] Generated clock design_1_i/rgb2dvi_0/U0/SerialClk has no logical paths from master clock axi_dynclk_0_PXL_CLK_O.
```

辅助事实（只读属性）：`ATTR_SERIALCLK_PERIOD=2.000`、`WAVEFORM=0.000 0.800`、`IS_GENERATED=1`、
`ATTR_SERIALCLK_SOURCE_PINS=design_1_i/rgb2dvi_0/U0/SerialClk`（源引脚即其自身输出）、`SOURCES`（空）。
方法论报告中另有 **`TIMING-30 Sub-optimal master source pin selection for generated clock = 1`** ——与本告警同源。

**结论（取代此前的“假设”）**：
- ×5 关系**确实已声明**（`Multiply By 5`）；
- 告警的实质是**生成时钟的 master source 取在 IP 端口 `PixelClk` 上，而主时钟对象 `axi_dynclk_0_PXL_CLK_O`
  到该生成时钟之间**没有逻辑路径** ⇒ 属**主源引脚选择/时钟对象关联**问题（TIMING-30 同类），
  **不是**「×5 未声明」。
- 工具给出的 Resolution 原文：*「Review the path between the master clock and the generated clock with the
  schematic viewer and correct the -source option. If it is correct and the master clock does not have a timing
  path to the generated clock, define the generated clock as a primary clock by using create_clock.」*
  ⇒ **本任务不执行该建议**（会新增约束，属需独立评审的变更）；仅登记为后续可选项。

## 3. 其余口径确认（本版实测）

| 项 | 实测 | 与既有口径 |
|---|---|---|
| 时序汇总（DCP 上重测） | `WNS 1.055 / TNS 0（0 of 21479）`、`WHS 0.059 / THS 0（0 of 21344）`、`WPWS 0.529 / TPWS 0(0 of 9587)` | **与既有 `report_timing_summary_impl.rpt` 完全一致**；本次**只换来源（部署 DCP 实测），数值不变** |
| `check_timing -verbose` | `no_clock (240)`、`unconstrained_internal_endpoints (520)` | 与既有报告一致 |
| 方法论（部署 DCP） | `TIMING-17 = 240`（Critical Warning，Non-clocked sequential cell）、`TIMING-36 = 1`（Invalid Generated Clock due to missing edge propagation）、`TIMING-9 = 1`、`TIMING-18 = 1`（**Missing input or output delay**）、`TIMING-30 = 1` | 与 `t04_sof_fix…/impl_1/design_1_wrapper_methodology_drc_routed.rpt` 的 240/1 一致；**TIMING-18 正是 I/O delay 缺口的方法学体现** |
| C2：`cmos1_pclk` 是否有时钟 | `ATTR_CMOS1_PCLK_CLOCKS=`（**空**） | **确认** C2：采集域无 `create_clock`（与 `no_clock (240)` 一致） |
| 例外来源 | `report_exceptions` 列出的例外（`cdc_tig` false path、`s_axi_aclk` max_dpo、`src_arst` false path、gray-code CDC max_dpo 等，含 `max_dpo=1000`） | **全部来自厂商 IP 自带约束**；用户 `an5642_j11_cmos2.xdc` **未**定义任何例外 ⇒ 仍不存在“自行添加虚假例外求通过” |
| 导出约束 | `v3_constraints_exported.xdc`（13,263 B） | 供复审核对 create_clock/例外归属 |

## 4. 本文件**不**证明什么（边界）

- **不**表示 TIMING-17/36 已闭合（240/1 仍在，且**未**修改任何约束）；
- **不**表示 I/O 时序已验证（TIMING-18 与之对应；I1–I3 仍按 Wong 2026-10-24 决定为**已记录局限**）；
- **不**构成 G2/G3/G4/G5 或阶段冻结；**未**做 RTL 仿真/等价性、**未**做板级测量；
- 未执行 38-249 的 Resolution 建议（新增 create_clock 属需评审的约束变更）。
