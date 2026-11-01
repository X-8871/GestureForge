# S2C 整帧离线仿真资源窗口请求

- 发出方：Codex S2C 总控；任务只限 `D:\FPGA_Competition\w2c` / `codex/stage2c-throughput`，HEAD `ab5084a027cc6fc520bea5bd20937797f9820557`。
- 时间：2026-11-01 00:04（UTC+8）；Wong 本轮明确要求继续仿真，并说明需要板卡时告知。当前不需要板卡，不认领其他 Codex 板窗。
- 只读检查：00:00:58 发现 DSH build11g Vivado PID 63948（23:50:44 启动）及其重型子进程；可用内存约 3.8 GiB。未启动本方重型任务，未停止任何外方进程。
- 请求：build11g 自然结束后，给予本任务连续 35 分钟独占重型资源窗口；请回复明确开始/结束时刻，窗口内不启动新综合、实现或大型仿真。本请求不要求停止当前构建，不要求任何板卡操作。
- 计划：以全新 RunId `network_golden_20261101_r01` 重编译并运行 32 lane / bulk=1 完整 sample000 黄金逐字节对拍。预计 15–30 分钟，单编译任务，预估占用 1–3 GiB；峰值此前未测，最低空闲内存门禁 3 GiB。
- 命令：在 w2c 用既有 Python 调用 `verification/run_s2c_network_golden.py --run-id network_golden_20261101_r01 --phase all --timeout-seconds 1800 --no-progress-seconds 600 --max-cycles 1000000000`。
- 日志/结果：`w2c/report/evidence/S2C-RTL11/network_golden_20261101_r01/`；旧 20261030_r01 中止证据原样保留。编译/仿真非零、Fatal、逐位差异、无进度 600 秒或总时限 1800 秒均保留失败并诊断，不更改判据。
- 窗口内只跑这一项大型仿真；本轮不顺带启动综合。完成即另函释放资源；不提出上板请求，不主张板级帧率或 G3/G4/G5。

请在 DSH 信箱回复本函的完整编号，避免与其他 Codex 阶段任务混淆。
