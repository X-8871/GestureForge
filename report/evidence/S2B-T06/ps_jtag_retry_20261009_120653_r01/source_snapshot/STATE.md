# 项目状态入口

更新：2026-10-09（UTC+8）。按根目录 `AGENTS.md` 恢复；阶段验收以当前代码、Git 和报告证据为准。

## 当前目标与阶段

- 阶段2A「PL 推理仿真」已完成 G4/G5 独立审查并冻结。用户已批准 8×8 空间 tile、8 路输出通道并行；保持 T01 冻结的 CSR、32-bit 单 word memory 接口、timeout 和握手协议。
- 用户已启动阶段2B，本工作树位于 `C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition`，分支 `codex/stage2b-t01-board-audit`，起点 `e433a081bc5f42a44ddec18b421f651d05e9c639`。PS-only平台及UART/DDR软件离线G1/G2已完成；2026-10-09固定OCM PS初始化、旧版及clock修正版UART/1MiB DDR smoke已实板功能通过。阶段2B PS/PL物理接口未冻结，G0/G4/G5未通过，不能称完整2B完成。
- S2A-T01 已冻结 tiny416 模型、检测头布局及 PS 解码/NMS；2B G0 尚需物理 PS/PL 地址映射、AXI/DDR 传输、DMA与缓存一致性、缓冲所有权绑定。Wong 于2026-10-08最后确认「厂商已明确确认实板是XC7Z020-2」，据此离线候选使用 `xc7z020clg400-2`，优先于此前XA/-1I确认及AGENTS旧基线。Vivado2026.1精确查询通过，XPR三个Part字段与3375cb4基线一致；照片仍直接显示XA7Z020/CLG400，实物身份冲突未关闭。资料入口 `D:\FPGA\AX7Z020\AX7Z020` 已确认，不再重复询问。PS-only UART/DDR离线BD/XSA及Vitis软件均独立G2通过；无板级XDC；实板PS初始化与1MiB UART/DDR功能结果见本轮新Run，实物身份冲突仍不由JTAG名称或功能通过消除。
- 先前的阶段3方向保持原代码和文档现状；当前请求仅处理阶段2B。Wong于2026-10-09已授权连接后执行固定PS-only OCM初始化、CPU0 UART/DDR检查及回传日志；对应范围无需重复授权。实际PCB/profile、接线/电平/供电、冷JTAG和独占条件仍须核实；模型/PL部署及非易失存储烧写不在此次检查范围。
- 2026-10-05 核对最新 Vault 阶段计划源 SHA `a94830afe60ae6a339038c1f41656101931a2999529a1bf866ad75d8d1c9f3fd`：2A G4 现要求综合无错误/非预期锁存器、资源可容纳性与时钟风险报告；已将 `docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` 单文件精确同步到该源。旧准备报告的综合 N/A 字段已过时。

## 当前候选批次（2026-10-08）

- 当前 RTL 候选为 commit `999238284157bed77cdb3a37e3e6eea52daeefc4` / tree `b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67`。原始 RunId `candidate8x8_109_20261006_130252` 的索引 0–24 PASS；恢复 RunId `candidate8x8_109_resume_20261007_023531` 仅运行 25–108，摘要 `PASS_RESUMED_84_RUNNERS`。恢复清单 `PASS_109_RECOVERY_MANIFEST`、109/109 PASS，SHA `eefe285f1c03673143d1fa0563f153626fe90d86be2d245ced59a05d8a7e65a2`；无存活协调器/仿真进程，不重跑。
- 当前候选 D9 报告 `PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`，最大 score/xyxy 误差均 0，报告 SHA `fcdf60ef68990a13ba634ee6cb2df71ad152d7f9d5a05d6625f5f3af296523ab`。sample000 磁盘 marker 后续被截断；D9 verifier 从 SHA 绑定的 console 原始字节恢复并显式记录，未改写文件、未重跑。109 源快照映射 `PASS_109_CROSS_RUNID_RECOVERY_SOURCE_SNAPSHOT_TO_GIT_TREE`，报告 SHA `61789bb7951dde06160e376761e74b4f2a408002ae81533bbb9cd86906b89ba1`。
- D9 修复及三项关键结果报告提交 `8646a02`。T66 runner 异常处理四项发现已修复并经独立 Reviewer PASS，离线故障回归 35 项 PASS、无残留进程，提交 `671f9cf`；之后当前候选 layer0 完整黑盒仿真亦 PASS（1,384,448 输出字节、2,551,955 请求/响应、6,635,073 stall cycles，记录 SHA `1b7bb9efcf4dc1f5ef0e920a28e5549888005cc2986e42158fc4adfca8e848b3`）。OS 拒绝结束进程时，runner 明确报告进程未退出/输出不完整并返回非零。

## 历史基线批次（非当前候选）

- 历史 RunId `repair109_20261003_194620` 的原始证据为 `report/evidence/S2A-T68/repair109_20261003_194620/`，逐样本审计为 `report/evidence/S2A-T68/acceptance_audit_repair109_20261003_194620.json`。它不是当前 `candidate8x8_109_20261006_130252` 候选的通过记录。
- 该历史批次索引 0–108 均通过当时版本的完整 38 cfg 层 PL golden，无 mismatch；记录每样本 972,865,374 cycles。协调器摘要 `PASS_108_RUNNERS` 只含 1–108；sample000 是同 RunId 独立成功记录。最终审计合并为 109，不能称协调器原始摘要为 `PASS_109`。
- 历史批次的 PL head 对冻结 CPU D9 比较记录最大 score/xyxy 绝对误差为 0：`d9_109_sample_report.json`，`PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9`。该项不替代当前候选独立 D9 证据。
- 该历史批次 109 份编译快照映射到当时冻结的 38 项闭包：源码 commit `fecbf1f8f37fcee8b25e6e2517b9621850912a4e`，tree `094e1492396a6788cc33b3b5866dd304387c02da`。映射报告状态 `PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE`；当前候选映射见上文候选批次段及验收记录。
- 当前候选 T70 tile 算术、选定内存和边界/异常结果，以及 T68 `protocol_directed24` 有各自独立范围，不替代 109 样本整网结果；当前白盒/边界证据经独立 Reviewer PASS。T17/T20 是历史串行 engine/pilot，不能称作新 tile 等价覆盖。详见 `report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`。
- T25 独立干净副本实际恢复 109×38 CPU shards 并完成 109 样本 D9 canonical replay；恢复 2,283.61 秒、D9 12.359 秒。它证明 CPU oracle 可恢复，不证明 PL 在干净副本全量重跑。

## 冻结限制与证据保全

- 当前候选全核心 OOC Vivado 综合（`s2a_stage2a_core_ooc`，14 个 RTL）已成功：0 errors、0 latch；LUT 40,550/53,200，FF 3,082/106,400，BRAM 32/140，DSP 186/220。无 XDC/冻结时钟，不能宣称 timing closure。独立 Reviewer 对综合/资源/风险子项 PASS；证据在 `report/evidence/S2A-T68/g4_synthesis_20261005/candidate8x8_core_ooc_run01_20261006/`。T68/OOC、T70 与协议材料归档情况见验收记录。最终 G4/G5 独立 Reviewer 对固定 HEAD `671f9cf494b92ce182b3f1542fefd0cfd4b209f5` 及本轮证据返回 PASS，Stage 2A 已冻结；验收记录为 `report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`。
- T68、T25 与 tile/协议支持证据已分别归档到 `archive/S2A-T68/repair109_20261003_194620/`、`archive/S2A-T25/clean_restore_20261002_160036/`、`archive/S2A-Support/Stage2A_20261005/`，逐文件 manifest 校验通过。归档和源都在 D 盘同一物理卷，不是异盘备份。
- 在证据归档校验后，仅清理 109 个 PL `build` 与 4 个支持回归 `build/obj_dir` 缓存，释放 33,104,952,077 字节；输入、结果、日志、VCD、T25 shards 和失败记录保留。该 RunId 已完成，绝不重跑。
- T13/T14/T15 当前 helper 源专项已有独立复核通过的新证据；早期 `helper_vectors_current_candidate_20261008_r2` 的 T13/T15 PASS manifest 被 FAIL 日志推翻，失败证据保留，新运行替代其验收地位。验收记录列出各报告、运行日志哈希及确切范围。
- 验收记录：`report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md`；用户本地运行说明：`docs/S2A-T68_local_run_guide.md`。限制仍包括无 XDC/时序收敛证明，以及当前候选未在干净副本重跑完整 109 样本 PL；审查确认后者不是 2A 硬性门槛。

## Git 与下一步

- 2026-10-08 用户要求改用新建的独立工作树/阶段2B总控窗口，旧2B窗口暂不使用；主目录与阶段3已有未提交改动保持不动。新工作树必须先核对冻结基线，不复制主目录全部未提交内容。
- 新增交付规则见 `AGENTS.md`「产物落点、阶段对接与 ROSS 使用」及 `report/README.md`；只读检查器提交 `9db8d64` 已通过50项回归与独立审查，证据 `report/evidence/CTRL-DELIVERY/validation_20261008_2054/`。它只核对当前声明的输入/证据，不代表阶段 G0/G4/G5 或实物通过。
- 本次 ROSS 2026.9.1 独立 Tcl 冒烟已通过：Vivado 2026.1 `version` 与 Tcl 查询完成码均为0，状态健康且仅本次会话已关闭；证据 `report/evidence/CTRL-ROSS-SMOKE/ross_tcl_20261008_192127/`。未测试 IP、综合/实现或硬件，不能由此关闭上文2B G0阻碍。
- 历史 T68 源映射修复基线为 `65dd1c310e7686d50685d2f83b9b2b623e6cf3ad`。候选实现提交 `999238284157bed77cdb3a37e3e6eea52daeefc4` 包含 tile engine、T66 testbench 与 runner；2026-10-06 G4 acceptance/OOC 综合证据提交为 `a232bc7c815a1e9bb18c675b0e9f31bccd857c62`。均未推送；保持其他阶段改动、运行目录、shards、模型数据、密钥和构建产物不入提交。
- S2B-T01 资料核查入口：`report/evidence/S2B-T01/vendor_manual_audit_20261008_r01/audit.md` 与同目录 delivery manifest；保留解析状态、六页渲染图及外部 XPR 的只读差异。包装通过不代表阶段2B G0或实物通过。
- S2B-T03 最新依据：`board/README.md` 及 `report/evidence/S2B-T03/target_resolution_20261008_r02/`；新手册PDF10/12页含XC/-2完整型号，照片XA冲突保留部署前核实。r01被替代，原始日志和旧候选源码快照保留。当前Goal持续推进全部可离线工作，到必要实物交接或无法自主消除的阻碍停止；不把预上板包称为阶段2B通过。
- S2B-T02 离线采集比对工具已独立G2 PASS，源码 `verification/s2b_fixed_capture_check.py`；32项测试、9次真实CLI期望及独立手算均通过，两头全字节与框顺序/1e-6绝对容差检查可用。证据 `report/evidence/S2B-T02/capture_check_20261008_r01/`，inputs依赖与delivery包装均通过；原始失败/拒绝日志保留。这是PC文件检查器，不冻结UART/AXI传输，不计为109整网或1000次板上任务。
- S2B-T05：Wong于2026-10-09回复「可以采用这个方案」，已批准采用《系统设计》候选 `S2B-AXI-RECOVERY-20261008` 的恢复原则 `s2b-axi-recovery-principles/1.0.0`：2A内部超时事件保留，2B停止计算并排空已发AXI事务后归还buffer，未排空持续隔离；控制门禁不能阻止CPU绕过驱动访问DDR。仅冻结恢复原则，完整物理接口待设计验证；物理实现/实板验收未执行，2B G0/G3/G4/G5未通过。2A原契约不变；候选快照/协议反例保留于 `report/evidence/S2B-T05/axi_abort_contract_20261008_r01/`。
- S2B-T04 PS-only平台独立R2 G2 PASS：全新Vivado2026.1重建23.482秒、10项防覆盖、73字段/50请求及历史映射通过，R1作用域问题关闭。正式离线冻结记录为 `docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_platform_offline_freeze_20261009.md`；唯一下游XSA位于r02/candidate_attempt1，SHA `a57948c60cfc573b710f562ed7177b0422313d6b77f100856410370273f3eb58`。独立实际证据在 `report/evidence/S2B-T04/ps_platform_freeze_20261009_r01/`；仅批准S2B-T06离线构建，原工具UNKNOWN保留，不代表实板profile或2B G0/G3/G5。
- S2B-T06离线候选`s2b-ps-smoke/1.0.0`独立G2 PASS：Developer真实构建43.564秒，干净隔离副本48.032秒，36项核查/9CLI/14布局反例及3实际ELF反例通过。两轮均启用DCache、每模式写回/失效后读回；专属1MiB DDR `[0x01100000,0x01200000)`，最小OCM初始化不加载旧boot image或PL。正式记录`docs/obsidian-project/04-提交材料/阶段验收/stage2b_ps_smoke_offline_freeze_20261009.md`；完整操作入口`vitis/s2b_ps_smoke.md`；开发、独立及集成实际证据在`report/evidence/S2B-T06/`，旧FAIL保留。冻结包evidence检查0，inputs检查2，仅因实板项NOT_RUN阻断依赖；此批准不等于实板安全窗口/初始化、G3/G4或2B G5通过。
- 2026-10-09真实连接诊断：COM4为CP210x；Digilent JTAG-HS1序列号`210512180081`枚举唯一APU及同parent CPU0/CPU1。11:44:53（UTC+8）观测双核Running→Stopped，CPU0 PC=`0x00102030`、CPU1 PC=`0xFFFFFF34`；BOOT_MODE=`0x00000001`（非JTAG的0）、MCTRL=`0x30800100`、OCM_CFG=`0x00000018`。串口115200/8N1开启525.0109092秒后以stop_flag正常关闭，raw为0字节，只证明开关采集完成。总控此后未resume/reset，未执行dow/con/mwr/BP或PS初始化；本次串口及归属核实的hw_server/launcher已释放，11:46:48观测3121无监听；未持续观测板卡，用户后续断电上电后须重新核验。
- 本轮完整证据：`report/evidence/S2B-T06/ps_jtag_retry_20261009_120653_r01/` 保留BOOT_MODE=0/OCM=0x18、停核PC与照片/PDF/profile独立PASS；16:56旧runner下载前因双核Running拒绝，INIT/SMOKE NOT_RUN、CPU1Running与cleanup错误原样保留。r02在17:10真实初始化INIT_RESULT2/rc0/readyhit1/failhit0，随后旧smoke完整23行/16模式/4194304 verified_words/0mismatch；旧clock_hz=0诊断错误独立保留。
- 修正版证据 `report/evidence/S2B-T06/ps_uart_clock_retest_20261009_172557_r01/`：17:41仅重跑新smoke，复用r02真实PS初始化，未重复冷初始化；新ELF SHA `9be608b847da26988f42105e2ab856c454d6dd7090c87b7dc95064f4cc05e847`，raw1453字节 SHA `7c6bcaf7ff15c8e73212e261fccb903bdbd567279cf4218a08ad824e477875c2`；clock_hz=100000000为BSP配置值，完整23行/16模式/4194304 word/0mismatch，`PASS_UART_DDR_RETEST`。旧版通过未继承到新版，本次新版有独立真实结果。

- 新C/md及离线永久精简包分别独立R09/R12 PASS；永久包 `report/evidence/S2B-T06/ps_uart_clock_fix_delivery_20261009_173128_r01/` 的89原件mapping保留原长路径构建/缓存包装失败，下载仍使用原build路径。新C只修正诊断字段，不改变正式总线/内存/协议接口，也不将旧freeze实现SHA称为新版。
- 串口三Run均已stop_flag正常关闭，脚本marker exit0与父进程ExitCode null分别记录；共享hw_server PID39576/父37840于17:43:28（UTC+8）核对归属后释放，native/launcher退出且3121无监听，闭合记录在新版Run。最后两核Stopped仅为disconnect前观测；无持续监测、无实物时钟测量、仅1MiB非全DDR，峰值内存及全部工具调用未测。
- 新版root执行记录的初次collector部分store值丢失，原null元数据保留；最终history透明说明来源，SDK57 API/8 hostquery命令与返回、UART原字节及服务闭合原件完整，不伪称恢复全部store。后续推进2B物理地址/AXI传输/缓存一致性/缓冲所有权设计与冻结；无需重复此次物理动作请求，不自动越过阶段方向。
