# S2B-T06 JTAG 重试 r01：读回成功与下载前拒绝

本 Run 保留 2026-10-09（UTC+8）真实执行，不续用旧 Run，也不把下载前拒绝解释为板上 DDR 失败。源码基线为 `117911e63cd7468418f11847ffedc9293dbca075`；`execution_record.json` 中照片前的 `aae7fb6` 是历史准备基线。

`source_snapshot/s2b_ps_smoke.md` 取自该 Git 基线，SHA 与执行记录 `c15290c48ccbc03c55418c2efa0ca2df815eacdeffb60e53363eca4fba490db5` 完全一致；旧 C 从 `ps_smoke_20261008_r01/build_08/s2b_ps_smoke.c` 保存到 `source_snapshot/s2b_ps_smoke.c`，SHA 为 `d2bb6f0941c2e3765c5a71f889d2e7e1e0428429237f5443510e81cedd16786b`。这两份实际字节解释运行时正在使用的版本，不绑定随后修改的工作区文件。

12:13 的 `ps_state_result.json` 为 `PS_STATE_READBACK_SAVED`：同一 Digilent JTAG-HS1（序列 `210512180081`）唯一 APU 的 CPU0/CPU1 从 Running 停止，PC 分别为 `0xFFFFFF28` / `0xFFFFFF34`，BOOT_MODE 为 0，OCM_CFG 为 `0x18`。原探针字段 `cold_jtag_proven=false` 保持原样；它只采集读回。后续 `physical_profile.json` 联合用户操作、厂商 V2.2 PDF 第 14/15/17/18/26 页及原照片形成工程判断，R-PS-PROFILE-05 独立审查 PASS，只允许固定 PS-only/1 MiB 检查。频率、电压未用仪器测量，DDR 丝印被贴纸遮挡，照片旧跳帽不证明当前现场接线或启动模式。

16:56 的旧 runner `9bd1915bab31672fc913c2677c260234d4231129d50dfb084224a7c78cfe7962` 在当前连接观察双核 Running，`CPU0/CPU1停止前提不成立`，下载前拒绝。`downloads=[]`，未执行 `dow`、`con` 或断点前进，初始化、UART 数据验收与 DDR smoke 均为 NOT_RUN。finally 中只 CPU0 停止，CPU1 仍 Running；`cleanup_errors` 原样保留。外层 CLI 退出 0 与内部 `PS_SMOKE_FAILED` 分别记录，CLI 0 不构成功能通过。

COM4 为 CP210x，115200/8N1、无流控、DTR/RTS=false；采集 182.2873265 秒，正常 stop_flag 关闭，原始 UART 0 字节。`CAPTURE_CLOSED.exit_code=0` 是采集脚本字段，父进程 `process_exit_code=null` 不等同 0；开关采集成功不能替代 UART/DDR 功能结果。

`preflight_checks.json` 保存 inputs 退出 0 与相对布局路径被拒绝退出 1；`preflight_layout_absolute.json` 保存精确绝对路径复核退出 0，原始失败日志保留。执行命令及真实退出码见 `execution_record.json`、`root_execution_history_after_photo.json`；原始 stdout/stderr、照片、PDF、runner/profile/独立收据均不改写。

初始化/DDR 成功的独立后继 Run 是 `../ps_jtag_retry_20261009_165853_r02/`，不回填本 Run 的 NOT_RUN。共享 `hw_server` PID39576/父37840 经总控核对归属后于17:43:28（UTC+8）释放，native/launcher退出、3121无监听。闭合原件在 `../ps_uart_clock_retest_20261009_172557_r01/hw_server_close.stdout.json`，SHA `f91b10f9a9722ef823c9d0654fc8f28c3e4f7031e0e9a789389a47f7cfce742c`；原服务启动日志现在已闭合。三Run UART采集均已正常关闭，未resume/reset CPU。

clock修正版已在上述新Run独立实测，完整23行/100000000 Hz配置报告/16模式/4194304 word/0 mismatch；旧版结果不继承到新版，也不覆盖本Run失败。清单command字段用JSON字符串表示原始命令全部字符，argv命令用JSON数组表示；原执行记录保留精确文本。

阶段2B PS/PL 地址映射、AXI/DDR 传输、DMA/缓存一致性与缓冲所有权仍未冻结，G4/G5 未通过。峰值内存与全部工具调用量未测。清单包装检查只核对文件及输入绑定，不代表功能、实物或阶段验收。

包装实际执行见 `packaging_checks_r01.json` 及对应原始 stdout/stderr：evidence 退出0/CHECKS_OK，inputs退出2，原因是本Run保留真实相对布局FAIL、下载前BLOCKED及NOT_RUN和阶段阻碍，不是哈希或schema错误。新增包装日志随后列入最终清单，再执行最后只读核验。
