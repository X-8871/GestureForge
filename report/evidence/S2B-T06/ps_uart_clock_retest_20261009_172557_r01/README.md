# S2B-T06 clock 修正版 UART/DDR 实板重测

2026-10-09（UTC+8）本 Run 对已初始化 PS 仅下载并运行 clock 诊断修正版 smoke。PS 初始化真实成功发生在 `../ps_jtag_retry_20261009_165853_r02/ps_smoke_result.json`（SHA `f02143baec914d6436d2fbb672831ea8a9d4aa3c2fda27de37836989809fa8f8`）；本 Run 的 `ps_initialization=REUSED_PRIOR_SUCCESS`，没有重新执行初始化、冷启动或 reset，不继承旧版 smoke 功能结果。正式离线接口仍为 platform/1.0.1 与 smoke/1.0.0，修正只涉及配置时钟诊断字段；旧冻结实现SHA并非新C的SHA。

实际新 smoke ELF SHA `9be608b847da26988f42105e2ab856c454d6dd7090c87b7dc95064f4cc05e847`，下载原路径为 `report/evidence/S2B-T06/ps_uart_clock_fix_20261009_172254_r02/build/s2b_ps_smoke.elf`，未移动。永久精简离线包在 `../ps_uart_clock_fix_delivery_20261009_173128_r01/`，89原件字节mapping与R12独立PASS保留先前长路径构建失败、原缓存目录包装退出2及collector技术失败；新离线包退出0不改写这些失败。新C/md快照在本Run `source_snapshot/`，清单绑定实际源码、ELF、layout、build_details和永久副本。代码R09、warm方案与旧初始化依据、runner R11、永久包R12的收据均保留。runner实际固定输入21项，另两项环境profile/UART SHA，不能采用先前22的误计数。

17:41:48.877至17:41:58.145的 `ps_smoke_result.json` 为 `HARDWARE_GATES_SAVED`。只下载一个新smoke ELF，默认SDK下载路径不force、不bypass；当前CPU0旧end PC/指令、INIT_RESULT=2/rc0、BOOT_MODE=0/OCM_CFG=0x18与CPU1停止门禁满足后执行。新end断点HitCount 0→1、SMOKE_RESULT=2，最终CPU0 PC `0x0010AD58` / CPU1 `0xFFFFFF34`、session内两核Stopped、cleanup空。结果SHA `c3f968f1661eb79e592689553874b551b996def8f18c3c2f289d8185b266acb0`。runner 57 API/8宿主查询/9.2678325秒；外层10.8597605秒、退出0。判定依赖实际门禁与UART，CLI0不单独构成功能通过。

COM4 CP210x，115200/8N1/无流控/DTR与RTS=false；正常stop_flag关闭，270.5159856秒。原始UART 1453字节，SHA `7c6bcaf7ff15c8e73212e261fccb903bdbd567279cf4218a08ad824e477875c2`，`uart_readable.txt`为精确字节副本。`analyze_uart.py`真实执行退出0，`uart_acceptance.json=PASS_UART_DDR_RETEST`，完整23行、clock_hz=100000000、16条PATTERN_PASS、4194304 verified_words/0 mismatch。100MHz为BSP配置值，未用仪器测量；只验证专属1MiB DDR `[0x01100000,0x01200000)`，非全容量、带宽或长期稳定性。原runner中的UART验收NOT_RUN是分析前范围，后续分析单独保存。

`CAPTURE_CLOSED.exit_code=0`是脚本字段，父进程ExitCode=null另行记录。共享hw_server native39576/launcher37840归属经PID/创建时间/路径/SHA复核后，于17:43:28.426释放；`hw_server_close.stdout.json` SHA `f91b10f9a9722ef823c9d0654fc8f28c3e4f7031e0e9a789389a47f7cfce742c`记录两进程退出、3121无监听，未resume/reset CPU。原启动日志在r01，本闭合记录被三Run绑定。

`root_execution_history_initial_partial.json`保存初次collector因新用户消息后部分functions.store值缺失产生的null元数据。`root_execution_history.json` SHA `e19c858c71971e92a94443c0486d05c5ade882a15b180e9abf7d7a6972e33717`透明记录限制；未伪造完整store恢复。真实SDK调用命令与返回在ps_smoke_result.json，采集进程完整command_line及CAPTURE_OPEN/CLOSED和原raw完整；外层时间/退出码依据实际工具chunk266fc5/session95920，未重跑。清单command字段用JSON字符串或argv数组表示保存字符，完整执行依据仍在原件。

最后Stopped只为session断开前观测，峰值内存及全部上层工具调用量未测。本Run执行一次；本次PS初始化与UART/DDR smoke实板功能通过不代表阶段2B完整PS/PL/AXI/缓存/物理地址归属冻结或G4/G5通过。阶段阻碍保留；CHECKS_OK只表示包装核验。

包装实际执行见 `packaging_checks_r01.json` 与原始stdout/stderr：evidence退出0/CHECKS_OK；inputs退出2，仅因阶段物理接口BLOCKED、仪器频率/电压及全DDR扩展测试NOT_RUN保留，无schema或文件哈希错误。日志列入最终清单后再次只读核验，不因此修改业务验收状态。
