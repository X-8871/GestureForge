# 项目状态入口

## 2026-11-01 管理权更新（优先于下方旧归属记录）

Wong 直接指令：所有 GestureForge 阶段及工作树由 Codex 项目总控接管，取消 DSH 最高管理权。项目最高总控、主目录与本树写权、任务分派、串行提交和硬件窗口协调均归 Codex；Wong 保留最终决策与明确审批权。DSH 仅可执行 Codex 后续明确委派的任务，不再持有全局否决权、独占调度权或必须经其 OFFER 的前置权。

权威规则：`D:\FPGA_Competition\AGENTS.md`；接管决策及全树基线：`D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\decisions\codex_project_takeover_20261101_r01.md`。本次依据用户直接指令，非伪造 DSH OFFER/CLAIM。下方旧写权、租约及 DSH 提交权仅作历史，不再授权；历史技术证据与未提交改动归属保留。接管不等于新板级窗口授权、阶段验收通过或允许覆盖既有工作；单写者、资源核验、证据保全和独立审查继续有效。

本树当前管理/写入负责人：Codex 项目总控；技术状态和冻结版本按原证据逐项核对。


更新：2026-10-22 18:14（UTC+8）。阶段2B已通过独立G4/G5并冻结；板上验收结束，不重复运行模型。

## 目标、归属与授权

- 本窗口完成2B tiny416固定输入、至少100黄金样本、1000连续任务、CSR/恢复及独立G4/G5，完成相关提交；不自动进入阶段3或推送、不写QSPI。
- 实施树 `D:\FPGA_Competition\w2b`，分支 `codex/stage2b-dma-g0`；冻结代码基线 `16ce2cdf8c00c6214435629d75a5e4b63acb66a9`，最终元数据由包含本STATE与冻结回执的Git提交确定。主目录由DSH持写权；只读其STATE、业务代码和阶段3树，不接管。
- Wong指定 `XC7Z020-2CLG400I`，Vivado part `xc7z020clg400-2`；DDR按手册 `MT41K256M16TW-107`、双x16/32-bit/1GiB候选。D9PSK解码、实际PCB修订、电压与工业温度未测，不声称已核实。
- 用户批准DMA按搬运功能验收、保留AXI3 adapter；已授权必要易失下载、停双核和恢复，不再重复索取旧POR确认。主机缓存、字节长度、ownership、错误、连续任务标准不变。
- 最后实板会话使用hw_server PID4812，创建FILETIME134371091860065760，身份在 `tmp/2B/hw_server_20261022.json`；COM4/原CP210x PNP、Digilent HS1串号210512180081。11:21补证后已断SDK/串口并停核；18:05只读主机检查无hw_server/XSDB/板测程序，不把旧PID当当前身份。用户18点后述板子显示识别框并允许必要时停；余下冻结为离线，不据画面改写旧证据。
- 主Codex信箱追加通知 `CDX-20261022-006-2b-final-acceptance-resume.md`；不修改主STATE或DSH信箱。活动任务期间不改HEAD/runtime、不关server、不连接JTAG/串口。

## 固定平台及已完成范围

- tiny416、8×8 tile、8路输出通道、双头、PS解码/NMS；物理接口 `s2b-physical/1.0.0`，UART `s2bu/1.1`。
- R04 PL位流SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`；XSA SHA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。50MHz，路由setup+0.156ns/hold+0.078ns/TNS/THS0，DRC393项/0error；原input_record标记失败保留，实际Vivado Job0。不重综合。
- 原infer ELF `a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8`；init `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1`。平台入口 T19 `visibility1_csr_fixed_20261016_r04/`、T15 `qualification_r04_xsa_rebuild_20261016_r04_artifacts/`。
- CSR RTL SHA `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`。T11 R07及独立R08：146 directed、128 random、25 integration、6362cycles PASS，含晚排空/永久停顿；不冒称对应实板场景。
- 模型真实运行 T18 `formal_stress1000_then109_20261018_r02/`：1109次RUN双头28113150字节及全部框比对通过。独审 `formal_model_result_review_20261019_r01/` 认可1000连续任务+前108个ACK闭合黄金样本，覆盖全标签；第109个最后ACK缺动态读回，完整R02独审CHANGES_REQUIRED保留，按108满足≥100。
- 3项历史host源码漂移由 T18 `formal_model_evidence_audit_20261019_r01/` 的Git原字节及原始证据副本解释；不称原运行clean tree。原始9103文件和失败原件不得删除。
- CSR实板R08真实完成忙START拒绝、同RUN黄金/ACK及重接受；RUN且AXI_PENDING=1时ABORT→ERROR_SAFE8/账本0→ACK→sample000黄金恢复。R08整体因后续静止矩阵失败保持FAILED，子范围另行审查。
- CPU原生postmortem保存DFSR1808/DFAR43C00008/PC C344/STR e5801000/LAST_REJECT变化，独审判SLVERR；原SDK超时失败不改写。T20 `cpu_bresp_gp0_postmortem_independent_review_20261019_r01/`。
- R11实际正常START47.4017962s和CORE10000/DRAIN最大值安全ACK通过，随后重复证据文件名失败。提交6e66bfc修复，52回归和独审PASS。
- R12真实完成正常START47.4058308s、CORE10000/DRAIN最大值→ERROR_SAFE5/ACK、DRAIN1→bit3/ERROR_SAFE5/ACK、DIAG0对账及黄金恢复；8项非法参数START安全ERROR/ACK、11项COMMAND拒绝LAST_REJECT及其他CSR无副作用。SDK11笔BRESP仍UNKNOWN/BLOCKED。
- 组合BRESP证据由固定RTL共用SLVERR提交路径+同地址CPU代表事务+逐场景无副作用支持实现级推论，不能称11笔SDK直接读回。入口 T20 `bresp_composition_review_20261021_r01/`。
- R12板上子范围结束后封装失败；原orchestrator PASS/native0为封装前快照，实际最终退出未捕获。生产封装接口/失败快照已修复并独审，提交9115150；真实函数隔离重放 T18 `csr_r12_finalize_replay_20261022_r05/` inputs/evidence CHECKS_OK，仅证明包装。
- 最终CORE/DRAIN选0xFFFFFFFF。较大完整START wall包络×名义50MHz×1.25=2962864425<4294967295；DRAIN最大值真实CORE错误场景安全ACK。逻辑请求96135961、compute424506368、乐观下界616778290不能当HP上界。实板FAULT_ISOLATED/晚响应未观察；见正式候选第4节及RTL分层证据。
- 历史DDR有限cache探针 T19 `cache_probe_execution_20261017_r02/` 两相256B/64words零错，早于模型运行；原cold=false保留。T20 `ddr_prior_probe_review_20261021_r01/` 限定PASS，无带宽/全DDR容量声明。
- 当前厂商资料对应已核验：手册时钟第17/18页、UART48/49第34页、DDR第12页；核心原理图Rev1.0第7页明确VCC1V8→MIO1_501、VCC1V5→DDR502。手册19/33页BANK矛盾保留，不当勘误或实装修订证明。解析整页/切片 T04 `board_material_mapping_20261022_r01/`，最终Reviewer已看图认可设计依据。

## 恢复演练与当前运行

- T15 `recovery_inputs_20261019_r02/recovery_bundle.zip` SHA `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`；67头文件/3库，隔离副本4C对象+2ELF重建原生0，PT_LOAD仅GNU build-id描述差异。BSP静态库复用、PL不重建，限制保留。
- 新infer ELF SHA `f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9`，entry100000。10/21重建app R02实际部署和两相256B通过，后sample000目录重复失败；目录修复aef41a8/10回归及独审PASS。
- 10/22现场先后观察ROM及stage3 v10_read，原恢复r01/r02、同会话PS r01均在部署前失败并保留，不假定旧2B状态。
- 最新 T18 `stage3_to_2b_restore_20261022_r03/` 实读16B唯一匹配stage3 v10_read，双VDMA RUNSTOP0/HALTED、卸映射、system reset/EOS0；后续新session所有权检查失败，未部署，cleanup[]。已完成的停DMA/复位证据保留。
- T18 `rebuilt_app_acceptance_20261022_r02/` 于11:13结束，69929已终止。严格ROM/EOS0准入、完整R04+新ELF下载、两相256B及weights通过，真实sample000双头/框结果PASS、epoch1/seq4；随后host误把含weights+sample的两条frames断言为1条，内层FAILED、外层FAILED_CLEANUP。CPU0已停，原失败不改写；原r02没有动态IDLE读回，由下一条独立补证单独提供。
- host双响应筛选修复已独审/15回归0并提交 `16ce2cdf8c00c6214435629d75a5e4b63acb66a9`，源码SHA171d83ca…075de、test b0de9b64…709c5。只读ACK补证脚本最终SHA6bb8538d…9198c，G2 R02 PASS，真实结果 T18 `rebuilt_app_ack_observation_20261022_r01/observer_result.json` SHA52c7db0b…9dbc14：PASS/exit0/cleanup[]，安全IDLE/epoch1/四项账本0、双核停。原r02逐项raw_logs哈希未变，无UART/LOAD/START/ACK/reset或CSR写。
- 同会话代码G2独审PASS/14回归，T20 `final_host_restore_review_20261022_r01/review_rebuilt_single_session_r01.md` SHA `ae614e0a92186201b93fc3924862a203229cf7bbdf0f7eceafeba5eb4a8fe35d`。
- 正式技术文档 `docs/obsidian-project/04-提交材料/阶段验收/stage2b_fixed_input_acceptance_20261022.md` SHA2345a741…59bc6。最终候选 T18 `stage2b_freeze_20261022_r02/`，79项绑定，inputs/evidence实际CHECKS_OK/exit0；delivery SHA1efc124b…1aa66，inventory SHA7ec952fe…dd25f6。r01非法note/role字段的包装失败保留，r02独立新RunId已修，生成器G2 R03 PASS。
- 最终独审 T20 `final_acceptance_review_20261022_r01/review_outcome.json` SHAef3df215…ed8b1，G4=PASS/G5=PASS，无阶段阻断。正式入口 T18 `stage2b_freeze_receipt_20261022_r01/freeze_receipt.json`；回执inputs/evidence均实跑CHECKS_OK/exit0。候选中此前NOT_RUN不追溯修改，由独立阶段回执补充最终判定。
- 本阶段完成；仅交付2B冻结版本，不启动其他阶段。108闭环/1000正式门槛、原109末ACK缺口、各失败、SDK逐笔UNKNOWN、BSP复用、PL未从源码重建、硬件身份/温测/DDR范围限制完整保留。Git之外bit/XSA/恢复ZIP/原始模型与UART/ELF及官方工具链必须保全；不能只clone源码恢复全部二进制。

## 当前交接行（11字段）

任务=`阶段2B验收冻结` | 负责人=`Codex本总控` | 工作树/分支=`D:\FPGA_Competition\w2b / codex/stage2b-dma-g0` | 起始提交=`16ce2cdf8c00c6214435629d75a5e4b63acb66a9` | 允许修改范围=`2B verification/vitis/docs/report及本STATE` | 未提交改动归属=`历史本总控2B原始证据与大产物保留本地；最终源码/元数据仅精确提交` | 让出声明=`阶段结束；未交接工作树写权，后续接管仍须正式OFFERED` | 心跳(UTC+8)=`2026-10-22 18:14` | 证据入口=`report/evidence/S2B-T18/stage2b_freeze_receipt_20261022_r01/freeze_receipt.json` | 恢复命令=`先读冻结回执及候选README、核对本地二进制与来源SHA；后续上板先检查实际会话，不复用旧PID、不覆盖RunId` | 状态/下一接手方=`DONE / 项目总控按冻结输入消费`
