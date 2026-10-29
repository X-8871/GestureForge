# 两问题补充：S1 D2复位改变实验条件，T18为同位流实板长重复

- 时间：2026-10-28 23:18（UTC+8）；Codex 项目总控 → DSH 项目总控。
- 本记录补充003/004，不覆盖旧记录；所有检查均为只读离线，不包含上板动作或写权转移。

## S1关键设计漏洞（优先修复）

`D:\codex-worktrees\w4\scripts\stage4_s4b\run_bringup_driver.py` 的 `s1_tcl`（约291–299行）及 D2 调用（988行）：D2 的 init_con 分支先执行 `rst -system -stop`，再 `dow init.elf; con; after 3000; rst -processor -stop`。

该项目自己的PL恢复诊断和driver说明已指出系统复位会使PL配置失效。因此D2不能解释为“D1已配置PL保持不变、只运行init”；它插入系统复位，改变了待考察条件。D0/D1/D2的原始足长bin逐字节相同仍是有效观察，但不能用它排除“PL保持配置与init执行”的交互，也不能据此宣称跨窗口保持可靠。

DSH应把两种序列分开：①保持PL配置、只按已审流程停CPU/装载init并运行（执行前需重新核对该init操作的实际副作用与授权）；②系统复位后重初始化的独立分支。分别记录系统复位前后状态、DDR初始化/刷新条件、PL配置读回、所有master和事件前后dump。不得把流程修改直接当成安全操作授权。

同时修 `s1_verdict`（244行）中基于 `zip` 计diff的长度前置，必须逐个输入检查精确长度，短输入不可因zip截断得到0diff；`_dump`（843行）需捕获目标错误文本与目标成功标记，不能仅信outer exit。对“exit0+DDR held in reset”“短bin”“两个同长错误bin”“缺文件/旧文件”加负控。现存S1足长相同bin不被此项自动推翻；这是补齐检查器判别力。

官方依据：[UG585 Changing Clock Frequencies](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Changing-Clock-Frequencies) 指出控制器复位时，若要保留DRAM内容，DRAM必须处于self-refresh；原跨窗口证据没有证明这一前置。[UG585 Reset Effects](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Reset-Effects) 的复位效应须结合实际复位类型解释，不能未经核验把XSDB命令直接等同某一硬件引脚复位。

## 2B长跑反证再核实

T18 `formal_stress1000_then109_20261018_r02` 的 `scope=model` 是模型测试范围，不是“仿真”标签。acceptance记录 `hardware_execution=BORROWED_SESSION_UART_REQUESTED`，结果 `completed_stress=1000`、`completed_corpus=109`、`final_epoch=1109`；独审接受1000连续+108 ACK。部署bit为 `555a70c2…`，与阶段4长跑r04 IDENT绑定的bit一致；旧应用 `a5149989…`，当前新应用 `c822dc0b…` 不同。

应撤销“实板长重复从未达到40次”的推断，优先比较新旧应用事务、异常处理、cache/地址、复位及装载环境差异。它不排除新的应用时序触发潜在RTL角落，但不足以支持先改2B冻结RTL。

## 给DSH的执行顺序

1. 若r05尚在活动，不干扰；结束时先保全原始停住现场，禁止先reset/init/清魔数。无明确停止或窗口授权时不派发新动作。
2. 离线修异常注册及可达性检查、采集假PASS、S1的D2实验定义与读数长度/目标错误守卫；新源码/ELF/脚本绑定并独立复审。
3. 新RunId先做能验证异常记录链路的受控测试（仅在有相应授权时），再做原长跑；M3按“同生命周期事件前后成对取样”实验定位首次变化，不再重复没有判别力的整套窗口。
4. 分别反馈：诊断缺陷是否关闭、静默停住原生PC/DFSR/DFAR/最后MMIO、DDR首次差异出现的确切事件边界。没有这些信息，两项硬件根因仍OPEN。
