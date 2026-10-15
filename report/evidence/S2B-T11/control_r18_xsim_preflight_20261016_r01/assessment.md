# CSR 恢复矩阵 XSim 入口预检

本Run仅完成XSim入口发现、隔离工程建立、完整源码快照和脚本导出；没有执行HDL编译、展开或仿真。功能结论为 `NOT_RUN`，不能代替R18矩阵通过、G0或实物验收。

- Vivado MCP启动的本次独立会话为 `vivado-20261016-030606-21c4364e`，root PID为21680；目标器件读回 `xc7z020clg400-2`，仿真top为 `tb_s2b_control_csr`。没有操作其他工作树会话或板卡。
- 采用与现有CSR runner一致的7份SV源码，未修改RTL/testbench、随机种子、128项随机事务、25组集成或所有PASS/覆盖标记。源码未含后端选择条件编译。watchdog为100000个testbench周期，导出Tcl另以2 ms有限运行防止停滞。
- XSim编译/展开均关闭relax，展开线程为off（单线程），debug为typical，未启用全部信号记录；没有请求或产生代码覆盖结论。模拟时钟和判定仍由原testbench控制。
- 技能环境doctor退出0、没有硬失败；它按无扩展名包装器读取版本而触发WinError 193，并检查Linux库目录和/bin/sh，这些警告原文保留。另用本机Windows `.bat` 包装器查询xvlog、xelab、xsim，三个版本均为2026.1且退出0。
- 导出 `compile.bat` 在xvlog之后执行 `call type xvlog.log > compile.log`。本机微型复现 `errorlevel_probe.cmd` 得到 `BEFORE_TYPE=1`、`AFTER_CALL_TYPE=0`，证实该打印命令可覆盖原错误码。执行阶段必须独立保存原生工具返回值并解析完整日志，不直接依赖该批处理返回0。原始生成脚本保持不动。
- 预检完毕后close_project和Vivado MCP stop均返回成功；后续针对本次root PID21680的查询结果为PID_ABSENT。该证据只涉及本次PID在采样时不存在，不对其他会话或历史进程作结论。

后续若采用此后端，须在独立运行目录以同一快照完成编译、展开和仿真，使用受控Job及2 GiB低内存停止保护，分别捕获阶段退出码/完整日志，核验唯一 `PASS CONTROL_CSR`、随机/集成计数和两组四相位覆盖，再独立审查。尚未测量XSim展开/运行耗时或峰值内存，不声称性能改善。
