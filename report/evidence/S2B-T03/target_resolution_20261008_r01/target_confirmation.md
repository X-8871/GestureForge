# S2B-T03 目标器件确认与工作树校正

日期：2026-10-08（UTC+8）。基线：`3375cb4d0d52854e85142851dda03de05a0291c0`。

## 身份依据

Wong 在当前会话明确提供资料目录 `D:\FPGA\AX7Z020\AX7Z020`，并确认“`xa7z020clg400-1I`，这个是我们板子的型号”。随后提供芯片照片。照片原文件为 `C:/Users/22061/AppData/Local/Temp/codex-clipboard-e38853e1-c1ad-420a-b31d-d3decadbc985.jpg`；本目录 `chip_identity.jpg` 保存相同原始字节，SHA-256为 `d062f1268b5f6eaafc78eb0b66cbc21e61d2bece65812068aef6e4a2f7778549`。

照片清楚显示 `XA7Z020` 与 `CLG400`，支持系列和封装；`-1I` 后缀依据上述用户确认，未声称从照片识别。该确认补充阶段0已接受的资料关系，无需再次让用户确认型号或相同资料入口。

## 真实工具结果与工程范围

Vivado 2026.1 的 `get_parts -quiet {xa7z020clg400-1I}` 返回唯一同名字面器件。五项属性读回为 `NAME=xa7z020clg400-1I`、`FAMILY=azynq`、`DEVICE=xa7z020`、`PACKAGE=clg400`、`SPEED=-1I`。具体命令与原始MCP响应见 `vivado_query.json`。

第一次探索查询尝试读取不存在的 `TEMPERATURE_GRADE` 属性，返回 `Common 17-54`、退出码1；该失败响应完整保留。第二次只查询已有五项属性，要求解析结果与用户字符串逐字符相等，退出码0。此处失败是属性查询错误，没有配置设计失败或硬件失败。

本工作树 `vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 仅将项目、`synth_1` 和 `impl_1` 三个Part字段从 `xc7z020clg400-2` 校正为 `xa7z020clg400-1I`。原目录的增量DCP和仿真FileSet改动未移植。`check_project.py` 从冻结基线Git blob构造仅含三项替换的期望XML，核对实际XML完整语义及原始照片哈希；成功结果见 `project_check_attempt02_result.json`，对应命令 `python -X utf8 -B report/evidence/S2B-T03/target_resolution_20261008_r01/check_project.py`，退出码0。

首次工程检查错误地使用了 `./Options` 路径，实际XPR字段位于 `./Configuration`，因此报错；当时源码保存为 `check_project_attempt01.py`，空标准输出为 `project_check_result.json`，原始stderr字节为 `project_check_attempt01_stderr.bin`。首次外层命令在Python后执行cat，未单独保存Python退出码，外层退出0不代表检查成功。默认Python stderr编码非UTF-8，失败字节原样作为二进制保存；第二次显式启用UTF-8并单独记录真实Python退出码。修复只改检查器的XML路径和删除无用导入，没有改变工程校正范围。

证据目录、绑定XPR和board说明通过精确 `-text` 规则保留字节；STATE是跨会话说明，另行审查而不列为运行依赖。历史S2B-T01审计保留其当时事实，不能用其旧“型号待核查”措辞推翻这次确认。

## 验收边界

该任务交付器件身份及工程目标校正。没有PS Block Design、Vitis平台、整网顶层更新、板级时钟/IO约束、时序、位流或上板结果；阶段2B物理接口G0与实际UART/DDR前置检查仍待相应任务。只启动本次Tcl会话进行轻量查询，无重型综合/实现或板卡访问。运行耗时和峰值内存尚未作完整测量，不能宣称资源或加速收益。
