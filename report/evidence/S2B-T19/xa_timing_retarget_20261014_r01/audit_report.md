# XA 跨器件离线时序诊断记录

记录日期：2026-10-14（UTC+8）

本次诊断开始：2026-10-14 23:01:51（UTC+8）

RunId：`xa_timing_retarget_20261014_r01`

## 诊断结论

总控在自有 Vivado 会话 `vivado-20261014-133318-6fec06f6` 中执行 `source run.tcl`。输入为当前 XC `visibility=1` 包的 routed DCP，SHA-256 为 `cd0a10f90659a5a9a9cc184f08750ed6057a39e6eefe63f60173d031465df101`；命令请求将其按 `xa7z020clg400-1I` 打开。检查点实际打开成功，恢复为 `Fully Routed`，时序、methodology、route status 报告均生成成功，路由错误为 0。

**XA/-1I 时序结论为 FAIL。** 时钟 `clk_fpga_0` 为 20.000 ns（50 MHz）；WNS 为 -3.841 ns，TNS 为 -6030.530 ns，3127/15427 个端点违反 setup；WHS 为 +0.101 ns，THS 为 0。原始时序报告明确写出 `Timing constraints are not met.`。脚本和 MCP 命令原生退出码均为 0，只说明检查点打开及报告生成命令完成，不代表时序通过。

## 当前 XC 实板适用性

用户已确认照片中的同一块实物是 `XC7Z020-2CLG400I`，其当前 Vivado part 为 `xc7z020clg400-2`。这也与当前 `AGENTS.md` 和 `board/s2b_inference_platform.json` 一致。因此，本次 XA/-1I 的负时序结果**不适用于当前 XC/-2 实板，不构成当前 XC 平台失败或新的阻断项**。

当前 XC visibility=1 包的原时序报告单独记录 WNS +0.229 ns、WHS +0.095 ns、TNS/THS 均为 0，且报告称所有用户指定时序约束满足。该只读参考文件及 SHA-256 已列入 manifest；本任务没有重跑或改写该报告。原 visibility=1 manifest 含有用户确认前的照片器件差异备注；本报告按最新用户确认及当前工程记录判定适用性，不把旧备注恢复为当前身份冲突。

## 跨器件打开警告与证据限制

- 源检查点记录的 part 为 `xc7z020clg400-2`，请求打开的 part 为 `xa7z020clg400-1I`。Vivado 报告 part 不同，并报告 checkpoint family `zynq` 与选择器件 family `azynq` 不同；binary netlist 无法读取，回退到 EDIF 后继续恢复 routed 状态并完成报告。该警告属于本次跨器件诊断条件，不能把结果当作 XA 器件的实际实现或当前 XC 的新构建结果。
- `result.tcldict` 的 `previous_project` 为 `null`，因为关闭后的 Vivado project 对象在结果字符串化时失效；这不表示原来没有打开工程。该结果保留 `previous_part=xc7z020clg400-2`。
- 工具响应报告 elapsed 58.779 s；Tcl 记录 58,733 ms。MCP trace 中源文件默认编码造成部分中文显示乱码，原始 `mcp_response.json` 未改写；本次 `open_code` 与 `report_code` 均为 0，没有进入相应中文错误分支。
- 日志重复显示 2842.824 MB 高水位；这是同一 Vivado session 的累计值，不是本次操作独立峰值。OS 进程峰值未测。
- 本封装任务未再次启动 Vivado、Vitis、JTAG 或硬件操作，也没有复制 DCP 或报告源包。

## 输入与原始产物绑定

| 项目 | 路径 | SHA-256 |
|---|---|---|
| 诊断脚本 | `report/evidence/S2B-T19/xa_timing_retarget_20261014_r01/run.tcl` | `c01f9c0923fd02f628c1be852548c429d23d5360b285c896604b9debe3102057` |
| 源 routed DCP | `report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/artifacts/s2b_inference_wrapper_routed.dcp` | `cd0a10f90659a5a9a9cc184f08750ed6057a39e6eefe63f60173d031465df101` |
| XC visibility=1 来源 manifest | `report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/delivery_manifest.json` | `0f32ff262d24dc49ff66e65d38653c27b0aaf53fffb263def51cf927412ca1ad` |
| 当前 XC 时序参考 | `report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/reports/s2b_inference_wrapper_timing_summary_routed.rpt` | `0155605e5805b13793592ab0dc9546a3a70d1135eb735b49adfbaed619742908` |
| 当前板级器件字段 | `board/s2b_inference_platform.json` | `c0b46d89b0ce063bd033586e1ba044bee4088c1bb91a2ea7b33bd285e24bc863` |
| 最新硬件身份规则 | `AGENTS.md` | `e6ca63f0f599e58638ef30f4343ef530fd8907a3be44a68829282e9c67ec4db4` |

当前运行目录的原始 `result.tcldict`、`timing_summary.rpt`、`methodology.rpt`、`route_status.rpt`、`constraints.xdc`、`mcp_response.json` 与 `run.tcl` 均原样保留，并逐个绑定在 [`delivery_manifest.json`](delivery_manifest.json) 中。机器可读结论见 [`summary.json`](summary.json)。

源 DCP 位于独立的 XC visibility=1 包，未复制到本 Run 目录。其精确路径和 SHA-256 记在 `summary.json`，并由此目录登记的上游来源 manifest 绑定。检查器的 evidence 模式要求 `diagnostic`/`artifact` 文件必须位于当前 Run 目录，因此不把外部 DCP 伪列为本目录文件；检查器仍会验证来源 manifest、机器汇总及本目录全部原始文件。

## 命令记录

| 操作 | 结果 | 原生退出码 / 耗时 |
|---|---|---|
| Vivado MCP 会话 `vivado-20261014-133318-6fec06f6` 执行 `source run.tcl` | `open_code=0`、`report_code=0`、状态 `REPORTS_COMPLETE_NOT_DEPLOYMENT_APPROVAL`；XA时序仍为FAIL | MCP 0 / 58.779 s；Tcl计时 58,733 ms |
| 离线解析 `timing_summary.rpt` 并按 setup/hold 指标判定时序约束 | `XA_TIMING_FAIL`，WNS -3.841 ns，TNS -6030.530 ns，3127个setup端点失败 | 1 / 0.173 s |
| evidence模式清单探测（首次因外部DCP角色约束失败） | `CHECKS_FAILED`：`.dcp` 必须标为 `diagnostic` 或 `artifact` | 2 / 0.340 s |
| evidence模式清单探测（第二次将DCP标为diagnostic后失败） | `CHECKS_FAILED`：`diagnostic` 文件必须位于当前 `evidence_dir` | 2 / 0.337 s |
| evidence模式目录核验（去掉外部DCP文件项，路径/SHA保留在summary与来源manifest） | `CHECKS_OK`（仅清单与目录包装核验） | 0 / 0.327 s |
| 审计命令历史补记前的目录核验：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T19/xa_timing_retarget_20261014_r01/delivery_manifest.json` | `CHECKS_OK`（仅清单与目录包装核验） | 0 / 0.318 s |
