# XC7Z020-2 同源全核心 OOC 补验 r03

记录时间：2026-10-09T00:01:48+08:00。状态：`OOC_SYNTHESIS_COMPLETED_PENDING_REVIEW`。

实际 tier `BASIC`，Part `xc7z020clg400-2`，top `s2a_stage2a_core_ooc`。14项RTL来自commit `999238284157bed77cdb3a37e3e6eea52daeefc4` / tree `b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67`，逐项字节与历史OOC SHA一致。13项直接导出Git blob；wrapper只在LF偏移2220/5430（第59/137行）显式恢复两个CR，按历史SHA复核。未读取共享src。批准输入是r02补充前精确快照，原批准路径及base commit保留在source_manifest。

Vivado `2026.1`；OOC、flatten_hierarchy=none、maxThreads=2、无XDC/时钟约束。本RunId标准batch启动1次、synth_design尝试 `1` 次、完成 `1` 次、重跑0次。进程退出码 `0`，launcher耗时 `142.7437219` 秒，batch脚本耗时 `139` 秒，OOC脚本耗时 `139` 秒。

## 到达阶段与边界

| 阶段 | 实际状态 |
|---|---|
| batch_tier_and_part_preflight | PASS |
| source_precheck_in_vivado | PASS |
| synthesis | PASS |
| required_reports | PASS |
| generalized_and_explicit_latches | PASS |
| final_static_capacity | PASS |
| industrial_power_environment_grade | PASS |
| checkpoint | PASS |
| implementation_timing | NOT_RUN |
| industrial_temperature_timing | NOT_RUN |
| board_validation | NOT_RUN |
| 109_sample_network_regression | NOT_RUN |

## 本次最终静态资源

| 资源 | 已用 | 目录容量 | 比例 |
|---|---:|---:|---:|
| LUT | 40550 | 53200 | 76.22% |
| FF | 3082 | 106400 | 2.90% |
| BRAM | 32 | 140 | 22.86% |
| DSP | 186 | 220 | 84.55% |

容量内判断：`True`。相对旧 `xa7z020clg400-1I` 最终报告的已用数差值：Slice LUTs*: +0、Slice Registers: +0、Block RAM Tile: +0、DSPs: +0。旧数只用于明确标注的比较，不作为本次测量。

LUT和DSP占用分别为76.22%和84.55%；整板PS/AXI/DDR/视频及后续物理优化未计入本核心报告，剩余静态容量不等于集成或布局布线余量已获验证。

锁存器检查：`{"GENERALIZED_PRIMITIVE_SUBGROUP_LATCH_COUNT": 0, "IS_LATCH_COUNT": -1, "IS_LATCH_UNAVAILABLE_SENTINEL": -1, "LDCE_COUNT": 0, "LDPE_COUNT": 0, "UNIQUE_LATCH_COUNT": 0}`。IS_LATCH属性状态 `UNAVAILABLE`；-1仅表示该属性未提供，广义LATCH/LDCE/LDPE另列真实检查。

## 时钟与环境风险

无时钟端点 `3332`，未约束内部端点 `12003`，无输入延迟 `79`，无输出延迟 `104`。最差路径报告有 `20` 条数据路径，最大已报告数据路径延迟 `97.069` ns；未放置标记 `True`。clocks报告实际表行数 `0`。

没有冻结目标时钟、受约束WNS/TNS或布局布线通过结论。industrial只设置功耗/环境等级；器件目录温度字母 `` 按实际返回记录，不推断工业温度时序。

## 日志与环境恢复

原生日志逐行统计 ERROR `0`、CRITICAL WARNING `0`、WARNING `65`；完整行/消息ID计数见execution_record.json。MCP通道未获自动批准和官方CLI综合结果分别记录。有效BASIC签名条目由主控选择至进程级私有副本，实际tier与Synthesis checkout由本次日志核对。原许可文件保持不动，私有许可字节/密钥/HostID不入包。

| warning消息ID | 行数 | 分类 |
|---|---:|---|
| Synth 8-6014 | 3 | 未连接或未使用RTL告警 |
| Synth 8-13373 | 19 | 其他RTL综合告警，保留原文供审查 |
| Synth 8-3917 | 39 | 其他RTL综合告警，保留原文供审查 |
| Synth 8-3323 | 1 | 其他RTL综合告警，保留原文供审查 |
| Timing 38-493 | 1 | 无约束/OOC时钟风险 |
| Timing 38-242 | 1 | 无约束/OOC时钟风险 |
| Vivado 12-25344 | 1 | 无约束/OOC时钟风险 |

时钟warning与本次无约束OOC范围一致；RTLwarning原文保持供独立审查，本次未重跑功能回归。

MCP初始化socket诊断：`["[vmcp] could not open socket on 127.0.0.1:7654 -> couldn't open socket: address already in use"]`；7654端口已占用导致该batch的MCP监听未建立，官方CLI综合与退出按真实记录单独判断。

Vivado日志自报峰值内存 `2259.402` MB；本次Vivado原生日志自报峰值，不是全机/全进程峰值。 工具调用总量 `None`；以主控执行记录已提供字段为准；未提供总量时记为未测，不推断插件加速收益。

主控可得调用统计：`{"heavy_launch_exec_command_count": 1, "write_stdin_continuation_count": 2, "mcp_channel_unavailable_attempt_count": 2, "complete_supplement_total_tool_count": "未完整测量，包含源准备/资料/校验/审查工具调用"}`。Windows进程内存另有一次主控样本，不混作进程族/全机峰值。

r01在Python环境预检失败；r02通过14源预检后被ENTERPRISE过期许可阻碍。两个失败RunId、原始日志和A审计均保持冻结。

## 检查点与恢复

DCP `41a990b6768696d0dfd5f04c388ff0843b7101a5aa38c059b99bc0e8c9826c90`，`14936828` bytes，本地保留供独立复核，现有Gitignore命中，不纳入源码提交；清单保留哈希及用途。源码恢复入口为prepare_sources.py：从冻结commit/tree读取14个Git blob，按历史SHA验证并明确恢复wrapper两个CR。重新综合须新RunId、隔离目录/namespace与实际BASIC许可选择，不覆写r01/r02/r03。带时间/元数据的DCP重新生成不承诺相同二进制哈希。

## 限制

- 仅评价本次XC7Z020/CLG400/-2同源核心OOC综合、资源、锁存器与无约束时钟风险；待独立审查。
- 无XDC/冻结时钟；布局布线、受约束时序和工业温度时序未运行，无频率达标结论。
- 静态资源在目录容量内不保证布局布线可容纳；PS/AXI/DDR/显示等整板逻辑未计入本核心。
- 本次没有板卡操作、DDR/引脚检查或109样本整网回归；既有功能证据按原冻结版本单独引用。
- r01/r02失败与A审计保持原始文件不动；新结果不覆盖失败记录。
- 私有许可原件/副本/密钥/HostID不在本清单内，不读取其字节或绑定其哈希。
- CHECKS_OK仅表示机器绑定或包装通过，不代表G0/G4/G5、工业时序或实物验收。
