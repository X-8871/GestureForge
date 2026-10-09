# S2B-T06 JTAG 重试 r02：旧版 PS 初始化及 UART/DDR 功能结果

2026-10-09（UTC+8）本 Run 使用源码基线 `117911e63cd7468418f11847ffedc9293dbca075` 的固定离线包；当前连接停核修复 runner 的 SHA 为 `5265f0989a3e69e80677b12548ffe19ebcd48a0bdafb80c270bbf1fa2833bb81`，R-PS-SMOKE-RUNNER-07 独立审查 PASS。复用 r01 的已审物理 profile 与同一 Digilent JTAG-HS1 序列 `210512180081`、唯一 APU；串口另开全新采集。

`source_snapshot/s2b_ps_smoke.md` 为 Git 基线的原字节，SHA `c15290c48ccbc03c55418c2efa0ca2df815eacdeffb60e53363eca4fba490db5`；`source_snapshot/s2b_ps_smoke.c` 为 build_08 的旧 C 原字节，SHA `d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b`。固定初始化 ELF SHA `366ad1f4831eba9db0510c0e5343d34e3b355f72c8f8bcae419903814246024c`，旧 smoke ELF SHA `8b9803682c9585a8dad91daf96f3f102de948466025e0cf28ee4b96e6cfde428`，XSA SHA `a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58`；清单另绑定 inputs_r03、布局和正式离线冻结依据。

17:10 `ps_smoke_result.json` 为 `PS_SMOKE_EXECUTION_SAVED`：下载固定 OCM 初始化 ELF 后，`INIT_RESULT=2`、返回码 0、CPU0 ready PC `0x00001D08`，ready 断点 HitCount=1、fail=0；下载固定旧 smoke ELF 后，`SMOKE_RESULT=2`、CPU0 end PC `0x0010AD58`、end 断点 HitCount=1。CPU1 PC `0xFFFFFF34` 且停止。最终两核 Stopped 仅为本次 session 断开前观测，cleanup 为空；断开后未持续监测。

COM4 CP210x 采集参数为 115200/8N1、无流控、DTR/RTS=false，stop_flag 正常关闭，耗时 212.9239091 秒。原始 UART 1445 字节，SHA `c76cf9255c4ab4259c4eb5efa1501380af7e8397839caaa9d5fc6bf8713f7d60`。`uart_readable.txt` 是原字节副本；`analyze_uart.py` 已真实运行退出 0，`uart_acceptance.json` 为 `PASS_FUNCTIONAL_WITH_CLOCK_REPORT_DEFECT`：完整 23 行、16 条 PATTERN_PASS、两轮×八模式×262144 word，共验证 4194304 word、零不匹配。范围是专属 1 MiB DDR `[0x01100000,0x01200000)`，每模式写回/失效后读回，不代表全容量、长期稳定性或带宽测试。

旧版 UART 行 `clock_hz=0` 是独立诊断缺陷：应用读取 `uart.InputClockHz`，实际 `CfgInitialize`/`SetBaudRate` 使用 `uart.Config.InputClockHz`（生成配置 100000000 Hz）；物理时钟未仪器实测。原始 UART、旧 C 快照和旧 ELF 不改写，功能通过只属于这组旧字节。clock修正版已在 `../ps_uart_clock_retest_20261009_172557_r01/` 独立真实重测通过，raw1453字节、clock_hz=100000000、4194304 word/0 mismatch；新版未继承本Run的通过，也未改写本Run旧错误字段。

`ps_smoke_result.json` 自身仍保存 UART 验收 NOT_RUN，因为 runner 只收集硬件门禁；后续 `uart_acceptance.json` 才记录 UART 原字节分析。CLI/外层退出 0 不是判定依据。`CAPTURE_CLOSED.exit_code=0` 是脚本字段；父进程 `process_exit_code=null` 不等同 0。完整命令和退出码在 `root_execution_history.json` 中，SDK 调用及门禁在 `ps_smoke_result.json`。

本次 runner 记录 73 API / 12 宿主查询，脚本 14.4294993 秒，外层 16.0110689 秒；本 Run 执行一次。峰值内存与全部上层工具调用量未测。`cold_jtag_proven=false` 原始字段保留，当前 BOOT_MODE=0/OCM_CFG=0x18 与原 profile 的冷启动工程判断分别记录。

共享 `hw_server` PID39576/父37840 的启动原日志位于r01；总控按身份核对后于17:43:28（UTC+8）释放，native/launcher已退出、3121无监听。实际闭合原件位于新版Run的 `hw_server_close.stdout.json`，SHA `f91b10f9a9722ef823c9d0654fc8f28c3e4f7031e0e9a789389a47f7cfce742c`；本Run authorization中原计划的B关闭落点保持原样，最终实际落点由本摘要说明。UART已关闭。阶段2B PS/PL物理接口未冻结，G4/G5未通过；当前PS初始化与UART/DDR smoke实板功能通过不代表完整阶段2B通过。清单CHECKS_OK仅表示包装完整，command字段用JSON字符串表示精确原始命令，argv用JSON数组表示。

包装实际执行见 `packaging_checks_r01.json` 及原始 stdout/stderr：evidence退出0/CHECKS_OK，inputs退出2，仅因旧诊断缺陷/阶段BLOCKED与仪器测量/全DDR NOT_RUN保留；无哈希或schema错误。新增核验日志列入清单后执行最后只读复核。
