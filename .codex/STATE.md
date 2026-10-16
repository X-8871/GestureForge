# 项目状态入口

更新：2026-10-16 23:39（UTC+8）。按根目录 AGENTS.md 恢复；当前HEAD为`6f5c6dc871d92fe32e5d37a58ff693442b793903`，下列检查点覆盖后文旧运行状态。

## 最新检查点（覆盖下方历史运行状态）

- 核心综合总上限10次，当前6次实际启动、剩余4次；R01在综合前失败不计。T19 R04综合/实现/bit/XSA Job退出0、资源停止线未触发；原始`input_record.json`仍为FAIL（profile marker未进入Vivado stdout日志），不得改写。独立审查只对当前构建/产物链PASS_LIMITED_SCOPE。R04 bit SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`。
- 板级候选G0由独立Reviewer限定为PASS_LIMITED_SCOPE：用户确认AX7Z020/XC7Z020-2CLG400I，手册第6/9/11–15页及R04 PS DDR读回参数支持本轮易失PL候选；实际PCB/BOM版次未绑定。当前JTAG只读识别`xc7z020_1`/PART `xc7z020`/IDCODE `00100011011100100111000010010011`。随后R04 bit已volatile配置，Vivado返回`End of startup status: HIGH`。证据 `report/evidence/S2B-T19/volatile_pl_program_20261016_r01/`；evidence包装核验CHECKS_OK、独立Reviewer PASS，仅限PL配置命令成功。
- Wong回复“已重启，10s”，记录于 `report/evidence/S2B-T19/cold_confirmation_20261016_r01/`；人工确认回执时间不是测得的POR边沿。该冷启动后已完成的本轮JTAG读取与PL配置见上方Run记录；PS初始化/DDR/HP0尚未启动，109样本、1000连续任务、恢复及2B G5仍未通过。
- qualification入口当前阻断：脚本仍固定旧XSA/bit/build，R04 bit-included XSA与T15 ELF组合尚未独立兼容审查；R04构建产物limited review不能代替该组合审查或资格entry收据。`TRUSTED_REVIEW/G0/COLD/TIMEOUT` anchors仍为空。资格rebind子任务正在只读核查/准备离线绑定，不访问硬件。下一步先关闭组合兼容和门禁/收据审查，再PS初始化、DDR/cache/HP0、单样本，随后109样本、1000连续任务和异常恢复。

## 当前目标与器件基本事实

- 2026-10-16当前进展覆盖下列旧阻断记录：R07 CSR完整矩阵及`csr_final_review`独立R08完整XSim复跑通过，均为146 directed/128 random/25 integration/6362 cycles、两类四相位全1；原生三阶段退出0且Job清理确认。CSR源码SHA `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`，TB SHA `04afb9a9d3a154c415b40effb2bf47c955c858d0cf203da20b3a0f170f88112a`。修复首AXI故障响应metadata独立锁存；旧位流不自动继承此修复。入口`report/evidence/S2B-T11/control_r18_xsim_first_axi_20261016_r07/`与`control_r18_independent_20261016_r08/`。G2仅限RTL/接口，不是实板通过。
- 2026-10-16 Wong明确DDR“以手册为准”：继续采用手册第12页`MT41K256M16TW-107`配置，不再等待厂家回复才推进已授权的易失板上验证；仍不声称D9PSK实装解码或DDR实测通过。见`board/README.md`。外部断电重启及后续独占操作确认已向用户请求，尚待回复。
- Vitis实际候选r02内部BSP/ELF/MMU离线通过，但外层Job十秒后仍有成员，整体FAIL；受控server/client真实probe r01也FAIL。兼容连接与专属Job收尾修复后，`managed_vitis_lifecycle_20261016_r02`真实probe PASS，client自然清空、SDK额外server PID为None、公开close/dispose完成；server按专属Job显式终止并稳定空读/关闭，不宣称优雅RPC关闭。源码经`vitis_managed_review`复审PASS，helper最终仅修UNIT成功状态字符串；完整新XSA BSP构建尚未执行。100样本/1000任务仍NOT_RUN，2B未冻结。
- 当前T13新平台`report/evidence/S2B-T13/platform_csr_fixed_20261016_r03/`已生成，源基线`f971ff9cf842e3ebd852d36e832f301845fd56a3`，18 RTL含新CSR，手册MT41K DDR/50MHz/visibility0；no-bit XSA SHA `0607120b1733ee17582ab0c508c366fca7b1f49d32afffe87a070a346df04252`，清单SHA `d91726e83102bcf6c5507c2192e97782d8a14fbc74bcde9728d9d1f7529d35bb`。`csr_final_review`独审82项绑定及HWH/PS/GP0/HP0/reset PASS；保留products原helper计数回退FAIL与独立native-slice核对、7条未打印validate警告未知限制。该自有MCP会话24236已关闭。
- 唯一重型运行：`report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r02/launch_build.py`，exec session `89706`，基于上述T13工程做全新synth/route/bit/XSA。预算1800秒、4.5GiB启动/2GiB停止、单线程/单重型，使用既有追加综合第2/3轮（r01在映像路径检查前失败，未启动Vivado，不算综合）。恢复先检查该session/结果及进程，不重复启动。T14 r01失败原件保留；当前r02未结束，不能宣称时序或位流通过。
- T18离线资产已准备：`report/evidence/S2B-T18/model_assets_20261016_r01/prep/preparation.json` SHA `e581acb600e9501553c22e7738a1c0c32ad27993682dfb5cbacf19b4093d3012`，109样本、约2.87MiB黄金head/reference；原输入/权重引用`D:\FPGA_Competition\report\evidence\S2A-T68\candidate8x8_109_20261006_130252`。prepare退出0/6.005秒，仅资产绑定；109板测和1000连续均NOT_RUN。

- 2026-10-16 Wong最新明确：子agent只用`gpt-6-luna`/`high`，总控用`gpt-6.1-sol`/`high`；覆盖旧模型偏好。本轮已用显式spawn参数新建`csr_fast_fix`、`vitis_fast_cleanup`，不再续用未能指定新参数的旧子agent。工具未提供当前总控模型查询/切换接口，不能宣称已切换当前运行模型。今日优先2B冻结关键路径，合并重复检查、减少非必要工具层防御扩展；正式独审、实板100样本/1000任务与真实证据标准不降。

- 本窗口是阶段2B总控：持续完成固定模型部署、至少100个黄金样本、1000次连续任务与异常恢复，直至2B G5；不自动进入阶段3或推送。
- AX7020实物器件为 XC7Z020-2CLG400I，Vivado part为 xc7z020clg400-2，时序按 -2。Wong于2026-10-14明确确认此前照片中的同一块板也是该型号；旧XA解读不再作为身份冲突或部署阻断。
- 本轮实际Vivado查询唯一匹配XC7Z020/CLG400/-2，主XPR项目、综合、实现三个字段及visibility=1会话均匹配。当前事实入口为 board/README.md；厂商原件目录 D:\FPGA\AX7Z020\AX7Z020 保持只读。
- 当前2B工作树为 `D:\FPGA_Competition\w2b`，分支 `codex/stage2b-dma-g0`；T11 R12失败关闭运行器/仿真仪表化及失败包提交为 `03be19c2c3915749234871d19878fb8b4bb98020`；其被全局`*.log`忽略的原始编译日志在补充提交 `14928578ec08d257cc19f6ece684887e3e294ed3` 纳入，提交树中清单21项逐项核对无缺失/哈希错误。审查仅覆盖失败关闭、仪表化、证据一致性；RTL仿真仍FAIL。较早D4提交 `75988f2e6d737f68b10807834be1112698c7916a`、器件事实文档 `b02ea83` 与PS重建/封装提交 `37c4b840977e727b6504d83b803da3358f89040e`保留为历史输入；恢复时以 `git rev-parse HEAD` 为准。
- DDR料号来源已澄清：Wong提供的 `MT41K256M16TW-107` 来自开发板手册，尚未按芯片丝印解码；2026-10-15 Wong要求暂按该型号继续后续工程/离线配置步骤，厂家预计2026-10-16确认。照片中两颗Micron芯片可见标记为 `D9PSK`；照片SHA-256 `f95f83d116fdd62ad01501241f00ca2299c9b80286182905f4ec0e4041f9cfee`，观察记录为 `OBSERVED_MARKING_ONLY`。当前 `board/ps_platform_fields.json` 与 `vivado/s2b_ps_platform.tcl` 已有该料号的活动离线候选配置；T13 r02 HWH读回仅证明Vivado候选参数，不证明实装料号、PCB/电源/时序绑定，DDR G0/G3仍阻断。厂家确认后重核料号并重做受影响检查。
- Wong已授权本阶段必要的易失PL/PS下载、DDR模型装载与板上验证；不含QSPI等非易失烧写。T19 r02新鲜只读探针确认Digilent JTAG target序列号 `210512180081`、`xc7z020` / IDCODE `23727093`，CP210x USB-UART桥为COM4；不证明完整订货型号、接线、UART协议或DDR。没有进行串口访问、PL/PS编程或DDR操作。后续本机全局进程名快照未发现vivado/hw_server/cs_server，但无法按工作树归属或证明特定会话退出，且交接曾报告另一Vivado PID `25196`活动；该项保持未确认。T13/T19证据一致性独审PASS；未操作另一工作树会话。证据入口 `report/evidence/S2B-T19/board_readonly_20261016_r02/`。

## 已完成与证据

- 阶段2A已通过G4/G5并冻结：tiny416、8×8空间tile、8路输出通道并行、双检测头与PS解码/NMS。验收基线 671f9cf494b92ce182b3f1542fefd0cfd4b209f5，入口 report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md。
- T04按用户暂定 `MT41K256M16TW-107` 完成Vivado 2026.1 PS7离线候选读回，目标 `xc7z020clg400-2`，PS-only BD/XSA，无bitstream；独审PASS并提交 `0486bc7cebc7d98a9c9ce7dc31505570ced0ed9e`，证据入口 `report/evidence/S2B-T04/ps_platform_mt41k_provisional_vivado_20261016_r01/`。Vivado日志计数为WARNING=9但仅保留2条文本，另7条内容/来源/影响未知，评估明确保留限制。未执行PS初始化、DDR或板卡操作；不关闭DDR G0/G3。
- 当前2A候选109/109整网仿真及D9对比通过，最大score/xyxy误差0；原始Run为 candidate8x8_109_20261006_130252、恢复Run为 candidate8x8_109_resume_20261007_023531。它们是离线逻辑证据，不是2B实板109样本结果，不重复运行。
- T19当前visibility=1平台以RTL源码基线 f92823f0bd577a49db543868f44c4f63b670d8e0 在XC/-2、50 MHz完成布局布线、bit与含bit XSA。WNS +0.229 ns/TNS 0/失败端点0，WHS +0.095 ns/THS 0，WPWS +8.870 ns；入口 report/evidence/S2B-T19/visibility1_timing_current_20261014_r01/。
- 当前XSA SHA 90f8d0b9e857f8beb9d99a6264b96441f9ba9b4b0af0568dbbcc064aecba6065；bit SHA a3e87d076ac102a4927a20ffa1e80699c2a29b5bc1ad3eacd1d7623f9ccf43da，XSA内bit与独立bit一致。XA/-1补充分析仅针对其他器件条件，不作为本板时序失败依据。
- T15同XSA Vitis 2026.1已按当前主机源码重新构建并独审PASS：CPU0 BSP 102/102、外层原生退出0/113.234秒；入口 report/evidence/S2B-T15/visibility1_xsa_20261014_r02/。新应用ELF SHA a436634e803cd6990a108e9d00b23a13a4e039149d0e413e450faca1daf67f2d；硬件NOT_RUN。R01旧构建被主机运输脚本哈希漂移阻断，保留原件不再直接运行。
- 新旧ELF的有长度函数地址/长度/字节一致；infer的.text仅GNU build-id 20字节变化，.rodata仅三处BSP路径RunId变化，init仅build-id变化。原始逐节/符号对照已绑定，但不自动继承旧ELF的GP0契约准入。
- T19顶层恢复仿真R02/R04及独审通过，覆盖公开CSR超时停止、迟到响应排空、错误安全ACK重启与协议故障持续隔离；入口 report/evidence/S2B-T19/top_recovery_verilator_20261014_r02/、top_recovery_verilator_20261014_r04/。保留177/179条warning，不能继承为硬件通过。
- GP0 HWH静态审计已提交 5b4b140：AXI3→AXI4-Lite、mode0，LEN连线仅静态。旧T15 R01 ELF的32位Device标量软件契约R03已独审并提交 9bdd207，支持提交后只读回算；入口 report/evidence/S2B-T01/gp0_software_contract_20261014_r03/。其R01初稿丢失、R02只读HEAD限制如实保留；新ELF的31原字样例、MMU/Device路径迁移和限定探针准入现已独审通过。
- visibility0与visibility1的937项PS参数、六份初始化原字节、BSP/MMU、地址/时钟、完整核和RTL来源兼容事实已独审，提交 6e75eca；入口 report/evidence/S2B-T19/visibility0_compatibility_20261014_r01/。原包绑定旧ELF且运行受阻，不直接充当新构建运行收据。
- 2026-10-09 PS初始化、UART与1 MiB DDR smoke有实板功能通过记录。后续旧平台CPU/DAP缓存预探针只覆盖起始256字节，不经过PL/HP0；不能作为当前平台32 MiB arena或整网可见性证明。
- 许可证问题已解决：有效Basic许可完成bitgen。历史许可证隔离与兼容审查入口 report/evidence/S2B-T17/basic_license_isolation_20261013_r01/、implemented_export_independent_20261013_r01/。

## 当前阻碍与在制事项

- 本轮最新恢复检查点：两组真实失败证据已独立核对并提交`abe095e1bff4586193149bbe837bc9bd855b2a03`（仅evidence，121项暂存原字节匹配）。下面提及“待独审/提交”的旧运行描述以本条和各Run原件为准；无板卡动作，2B仍未通过。
- 历史微型运行及XSim未执行阻断包独立一致性PASS，提交`eec3be34e5b571805d8e637e7e3410d6ed293969`（80项原字节匹配）。监督器最终r04 G2 PASS：源码SHA`c1f1eb733675a0c316788198420940236f062363808648f84c5293caccc85ac3`，测试SHA`5f9889891949b492dd87c0350c72844cabdb2cb7a721a31e0bf1e0886a0c04ed`，Developer21项/8.589秒、Reviewer21项/8.544秒及定向边界攻击均退出0。四项硬约束只允许收紧，慢终态查询跨期限/采样间隔失败关闭；此PASS仅覆盖监督器，不能替代实际XSim/Vitis重跑或硬件验收。
- 受监控自然drain的r03源码`e5c551ee…ab7e3046`完成Developer17项/8.640秒与Reviewer17项/8.634秒，均退出0，但G2为CHANGES_REQUIRED：API可放宽0.25秒采样、1秒最大间隔、10秒drain或2GiB停止线。两项独立攻击已复现超限仍PASS，正在同轮封住参数并补充边界测试；旧Run原件/快照和审查阻断保留，不使用旧源码启动重型任务。最终修复须独审PASS、固定提交后再执行。
- TB诊断版SHA`379bbccdffb8700ac0d562c5d5daa8e5c0f12852aedbc1564f47a0390151e214`静态G2 PASS，原epoch force/断言/seed/覆盖不改。XSim诊断准备r03因旧监督器终态采样/期限缺陷被拒绝启动，明确BLOCKED/NOT_RUN；新r04静态准备PASS但依赖新监督器最终G2和真实启动前快照，尚未启动compile/elaborate/simulation。候选Vitis离线r02同样已准备但NOT_RUN。

- 2026-10-16 XSim r02已真实执行：`report/evidence/S2B-T11/control_r18_xsim_execution_20261016_r02/`以`ba71fef`为源码基线，compile/elaborate/simulation原生均退出0、Job清理均确认，但cycle=3308、directed=130、integration=0出现Fatal，驱动退出1，整体FAIL。中文后缀损坏，只能确认AW相关文本；最大epoch持续force与packed struct更新的交互尚为假设。原结果/清单保持原字节，另保留必要WDB/journal及历史快照补充清单；包装CHECKS_OK不代表矩阵通过。TB仅增加ASCII位置和q/d诊断，原刺激/断言/seed/覆盖不变，尚待独审与新Run动态复验。
- 当前T13 r02 XSA候选首次离线构建`report/evidence/S2B-T15/candidate_t13_r02_offline_20261016_r01/`内层生成BSP/infer/init ELF，初始MMU静态通过，infer SHA`4972fac2d414bc5bb60942233b948b530d6864252be999176fb82a9da9f4e4df`；但外层`FAIL_JOB_NOT_EMPTY`/退出1，整体FAIL。root/native0退出时Job残留PID9332（不同于server壳PID23024，身份未留证），监督器随即报错；请求终止后空Job双读/Accounting0/句柄闭合，cleanup_confirmed=true。原运行不改判PASS；正在修复有界自然排空且持续RAM监控。只离线，无板卡动作；原始失败、源码/BSP归档及产物已保存，尚待独审/提交。

- PS/PL s2b-physical-candidate/0.1.2、UART s2bu-candidate/1.1 尚未整体冻结；器件身份XC7Z020-2CLG400I已由用户确认，DDR实际料号与当前板卡修订绑定仍待厂家确认。
- 仍需收敛HP0非Bufferable完整路径依据、统一冷启动/排空恢复、32 MiB arena的实际BSP/cache访问与运行绑定；实际总线、延迟、可见性及恢复结果必须在受控实板测试留证。
- 整网core/drain部署期限尚未实测。32位全局core计数在50 MHz最多85.8993459秒；实际tile复用/权重重读静态预算为每帧96,135,961次请求（读84,753,811/写11,382,150），38层及9项轻量测试独审PASS，提交 c8977ef；入口 report/evidence/S2B-T19/request_budget_20261014_r01/。不把静态敏感性估算当真实HP延迟或周期上界；T66原记录缺失仍BLOCKED，仅有T68间接计数依据。
- 平台检查器受限祖先枚举问题已独审并提交 0aaea57：11项中10通过、1项因WinError1314跳过，静态preflight通过。入口 report/evidence/S2B-T19/platform_path_preflight_20261014_r01/。
- 当前完整平台尚未完成JTAG/PS/UART/DDR/cache联调、完整模型首次实板推理、100样本/1000连续任务及异常恢复；2B G0/G3/G4/G5尚未通过。

## 下一步与恢复限制

- 2026-10-15限定visibility0 CPU0/DAP起始256B真实探针已执行；运行原件状态保留`API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`，native退出0、约107.672秒、cleanup_errors为空、`cold_lifecycle_proven=false`。独立Reviewer对运行与封包G2为PASS；总控仅接受该限定观测包。证据入口 report/evidence/S2B-T19/cache_probe_execution_20261015_r01/ 与 report/evidence/S2B-T19/cache_probe_acceptance_20261015_r01/。它未LOAD/START、未经过PL/HP0，不能证明32MiB arena、整网G0、100样本、1000连续任务、冷生命周期或恢复；原清单包装失败及补充清单修正均保留。
- 2026-10-15单样本整网入口`vitis/run_s2b_model_qualification.py`与失败安全测试完成离线G1，13/13专用测试通过；Reviewer针对D1修复与证据包D2 PASS，提交`0f768c9055f0a3eae9e45b3aaf514307e778fda2`。证据入口`report/evidence/S2B-T19/model_qualification_entry_20261015_r01/`中的资格执行记录及delivery checker `CHECKS_OK`仅对应历史提交`0f768c9055f0a3eae9e45b3aaf514307e778fda2`的runner/test源码SHA-256（分别为`fef2aa5b137eccf4e3c15dae7e9dd7d5ca9fff9d207180db6730073805a0fa7b`与`d24a5d6eb41b2488f00b1fd350f8ab75a73161c4ff3c8b1ffbc80a75652b3bd3`）；它不验证D4及后续源码变更后的当前checkout。该G2仅覆盖历史版本的入口代码与证据包；没有批准整网G0或实板运行。正式物理接口、外部POR/独占保管及CORE/DRAIN期限可信锚仍缺失，硬件门保持关闭；单样本资格入口尚未在硬件执行。
- 2026-10-15 Wong确认阶段计划中的DMA按数据搬运功能验收：保留自定义PL AXI3 master/word adapter，不要求AMD AXI DMA IP，字节/lane长度、cache、ownership、错误/取消/完成及连续任务均须覆盖，100样本/1000次标准不变。D4人工信任根与资格入口改动已独立复审并提交 `75988f2e6d737f68b10807834be1112698c7916a`；该根绑定两份用户指定JSON哈希，属于有限范围的人为批准，不是密码学签名，不构成G0或硬件执行通过。
- T11候选CSR runner重绑 `s2b-physical-candidate/0.1.2` 的R11编译因180秒超时失败，direct启动分别因缺少工具链DLL路径和完整启动环境不明而失败/超时；原始证据保留于R11目录与两个direct目录。R12编译在360.015秒超时、`simulation_started=false`，代码加入wall超时清理确认、100,000周期watchdog与阶段标记；独立审查PASS仅覆盖失败关闭逻辑、仪表化和证据一致性。`taskkill`被拒后，4个本Run残留编译进程经Stop-Process清理并记录后续无残留（Stop-Process独立退出码未回传）。提交 `03be19c`；RTL仿真仍FAIL，T11未通过。证据入口 `report/evidence/S2B-T11/control_r12_candidate012_20261015/`。
- R18扩展外层CSR/恢复矩阵并补充CSR读失败诊断，静态独审PASS；唯一实际新Run `control_r18_readreg_diag_20261016_r01` 在编译阶段约225秒触发2 GiB停止线（可用内存约1.80 GiB），编译FAIL_EXIT、外层码4294967295，仿真NOT_RUN。失败证据与测试源码快照提交 `86de3bb`；其PASS仅限静态/失败包审查，不代表RTL动态通过或G1。串行编译生成约120.3 MB、136个C++文件；本轮可用内存计数器读数6929 MB（约6.77 GiB），低于10 GiB启动门槛。编译墙钟上限从360秒调至600秒的单行改动经独审PASS并提交 `1b44b647d4b0c7085eb7673a2d67a1bc96c7a0df`；随后runner只加Verilator `--output-groups 8`，独立静态审查PASS并随 `63b7b10ddc4a827017234d739754dac7970e4359` 提交；没有重跑。runner本身没有2 GiB内存监控，下一次运行仍须有针对该Run的外部监控和安全停止方式。
- XSim等范围入口预检独审PASS：`report/evidence/S2B-T11/control_r18_xsim_preflight_20261016_r01/` 绑定同7份SV源码、原随机/集成/四相位覆盖判据，导出strict单线程、debug typical、2ms有界脚本；未执行HDL编译/展开/仿真。Windows原生xvlog/xelab/xsim版本均2026.1；doctor平台适配警告保留。生成compile.bat的call type会覆盖原errorlevel已微型复现实测，后续须分别捕获原生退出码。自己的Vivado预检会话已关闭、root PID21680后续查询不存在；不对其他会话作结论。
- 资源监督器修复独审PASS：最终`report/evidence/S2B-T11/control_r18_process_supervisor_20261016_r04/`独立复跑direct8项（9个夹具场景）+supervisor10项退出0；拒绝非有限时间预算，direct挂起入口按原始HANDLE/出生时间/稳定单成员Job核验，Job构造读回异常关闭句柄。CSR默认10GiB启动/2GiB停止、0.25秒采样、最长间隔1秒；只有自身Job清空且句柄闭合才能PASS。前三Run真实失败/阻断保留，提交`43f9b46`。XSim执行脚本静态准入PASS，SHA`e118d2394de5c95f146810a3d8985b15e27edf6cc5c8a40377df84c56960f517`，新Run仍未执行；其独立工具预算4.5GiB启动/2GiB停止，原矩阵判据不变。微型测试不代表RTL通过。
- 实际ELF初始MMU检查器独审PASS：`report/evidence/S2B-T15/initial_mmu_checker_20261016_r03/`独立23项单测、3项来源链定向攻击、AST退出0；前两Run的setter额外写入、固定CSR地址、map节地址及实际BSP编译源/归档成员来源链阻断已关闭。没有本次Vitis候选构建或硬件结果，不改变visibility=0或实板G0状态。
- 自动审批已恢复。资源监督器/S15/CSR runner及r04证据提交`5b2f6024ea716e6a9337d5c5cef8aed74c5ea1b6`；精确-text规则独审PASS后提交`15fee2b3e05a785475d0d4185905f0dbd75368c2`，两份S15原字节补提交`8add7ef46be9f28a9372de8420f03e6119cd44f4`；提交树5源码哈希匹配独审值。MMU源码及r03证据提交`9bcf0237020174ec5ce0faa6a6697419e5a56536`，3源码提交树原字节匹配独审值；没有Vitis候选新构建或板卡动作。
- XSim真实r01已运行：`report/evidence/S2B-T11/control_r18_xsim_execution_20261016_r01/`以源码基线`8add7ef`完成compile原生0/2.453秒、elaborate原生0/12.141秒且两Job清理确认；simulation在CreateProcessW挂起创建前WinError87、未产生root/未Resume，外层FAIL，RTL仿真NOT_RUN。原始结果/清单保留，不能把包装CHECKS_OK当矩阵通过。正在核查HANDLE白名单数组需保留到DeleteProcThreadAttributeList的生命周期；新小任务只修启动器与轻量夹具，不改RTL判据，不覆盖r01重跑。
- r01失败包/历史快照清单一致性独审PASS，提交`c2ed441aa012966f93c1905f03aeb6ed1d5cfd56`。HANDLE_LIST数组owner修复独审PASS：`report/evidence/S2B-T17/handle_list_attribute_owner_20261016_r01/`独立target1、direct9、supervisor10项退出0；旧probe真实Initialize/Delete但模拟Update，GC后weakref消失，无同址复用/WinError87复现。新launcher持有数组至Delete结束，不更改白名单或RTL。后续完整XSim须新r02实测，不把微型通过当原故障已复现或RTL通过。
- 活动平台版本绑定 `s2b-physical-candidate/0.1.2` 已独审PASS并提交 `707a3e41e536c88ed064fd0f1f8a5683488553de`；候选正文SHA-256 `1486a7f69e7a2053acfcad05151a9c54cfffab776d4154141741236aa88c401b`。平台仍为 `CANDIDATE_NOT_FROZEN`。T13 r01因RunId父目录缺失而路径预检失败，没有创建BD/XSA；r02用Vivado 2026.1完成PS7/GP0/reset/constants读回、BD校验和no-bit XSA导出（XSA SHA-256 `481e1a73b5ce731743c61491bb98ab3d640903417c4457ac96a1270f9a1ca783`），静态平台检查通过。日志有4条WARNING；通用产品警告捕获器因累计计数回退报FAIL，专用回退核对产品区间2条，原捕获失败与4条警告均保留。未综合、实现、生成bit或访问DDR。T13 Reviewer仅对证据/声明一致性PASS，不覆盖G0/G3/G4/G5。证据入口 `report/evidence/S2B-T13/platform_current_20261016_r01/` 和 `_r02/`。
- 之前的R18真实编译及CSR恢复矩阵已在上方检查点记录通过；旧RTL位流不继承新CSR结论。后续仍需以同一冻结平台/ELF/位流完成受审资格入口、DDR/cache/HP0/单样本、至少109黄金样本、1000连续任务及异常恢复，最后完成适用重建/时序和G4/G5。DDR继续以用户指定的手册候选MT41K256M16TW-107推进，正式实物G3前记录型号/PCB对应限制。
- 历史板级调试失败、TCF memory map及目标枚举修复、unloadhw无进度原件见 report/evidence/S2B-T19/cache_probe_execution_20261013_r01/至_r04/、board_failure_packaging_20261013_r01/、server_starter_fix_review_20261014_r01/。不把启动器退出0当实际运行通过；SDK卸载根因仍UNKNOWN。
- 当前16 GB机器只运行一个重型任务。用户将核心综合总预算上调至10次；6次实际启动、4次可用。资源启动/停止条件与正式验收标准仍有效；轻量读报告/静态检查不算重跑综合。
- 仿真、独审、包装CHECKS_OK与实板分别判断；不改原始失败/冻结证据，不覆盖RunId，不降低指标。阶段冻结须绑定版本、完成适用验收、独审和精确Git提交。
