# 8×8 / 8-lane 候选的 G4 综合与资源/时钟风险记录

状态：**SYNTHESIS_COMPLETED**；最终 G4/G5 独立审查仍待完成。

## 被测版本与范围

- 候选提交：999238284157bed77cdb3a37e3e6eea52daeefc4
- Git tree：b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67
- 卷积 tile 引擎 SHA-256：76ca735b14802e26f0a4b016989e13b43cf8bd904587ccea37651c757d089300
- 顶层：s2a_stage2a_core_ooc，14 个 RTL 源文件，含 CSR、runtime shell、memory master 与 network backend。
- 器件目录条目：xa7z020clg400-1I。这是本机 Vivado 目录可解析的 part；现有工程也使用该条目。板卡温度等级后缀尚无独立实物资料证明。
- 工具：Vivado 2026.1 Build 6511674；general.maxThreads=2；非工程 OOC 综合；Vivado Tcl 退出码 0；墙钟约 140 秒。
- 源文件闭包逐项绑定到候选 Git commit/tree，并由 source_manifest.json 保存路径、blob、SHA-256 和字节数。

## 综合结果

| 资源 | 使用量 / 器件容量 | 占用 |
|---|---:|---:|
| Slice LUT | 40,550 / 53,200 | 76.22% |
| Slice registers | 3,082 / 106,400 | 2.90% |
| BRAM tile | 32 / 140 | 22.86% |
| DSP48E1 | 186 / 220 | 84.55% |

synth_design 完成；Vivado 日志没有 ERROR；生成的 LDCE/LDPE 锁存器清单为空。按综合资源计数，各项均未超过器件目录容量。DSP 余量为 34 个，LUT 余量为 12,650 个；这是 OOC 综合计数，不是布局布线或系统集成结果。OOC 报告中的 IOB 数不用于判断板级 I/O 资源。

日志另有 67 条普通 warning 和 1 条 Tcl Store 权限回退 critical warning：Vivado 无法写用户本地 Tcl Store，改用安装目录中的 Tcl Store；该告警没有阻止项目 Tcl、综合、报告或 DCP 生成。此记录不把它误标为 RTL 综合错误。

## 时钟风险与边界

本阶段没有冻结目标时钟周期，也没有适用的 XDC；timing summary 和 clocks report 因此用于暴露未约束风险，不能支持时序收敛或频率达标声明。报告记录 3,332 个无时钟寄存器端、12,003 个未约束内部端点、79 个无输入延迟端口和 104 个无输出延迟端口。WNS/TNS 无可用的受约束时钟结果。

本次只覆盖 OOC 合成、静态资源计数和时钟约束缺口。它不包含布局布线、板级 I/O 约束、比特流或上板；阶段2A G3 上板仍不适用。该资源/时钟风险子项可供独立 G4 审查，不能单独宣布阶段2A通过或冻结。

## 原始证据

- run_plan.json
- source_manifest.json
- run_synthesis.tcl、run_vivado_g4.cmd
- execution_record.json
- utilization.rpt、utilization_hierarchical.rpt
- latch_cells.txt
- timing_summary.rpt、clocks.rpt、worst_paths.rpt
- synthesis_summary.txt、launcher_exit_code.txt、vivado.log、vivado.jou
- s2a_stage2a_core_ooc_post_synth.dcp

批次时间：2026-10-06（UTC+8）。新的 109 样本全网候选仿真仍需完成；此报告不使用旧 RunId 的仿真/D9 结果替代它。