# 阶段2B固定输入验收记录

日期：2026-10-22（UTC+8）。本记录固定技术范围与真实验收事实。阶段冻结结论以 T18 `stage2b_freeze_receipt_20261022_r01/freeze_receipt.json` 绑定的独立 G4/G5 审查及交付清单为准；本文件和单个脚本的 PASS 不单独授予阶段通过。

## 1. 验收对象与配置

- 目标：Wong 指定的 `XC7Z020-2CLG400I`，工具 part `xc7z020clg400-2`；tiny416、8×8 空间 tile、8 路输出通道、两个检测头、PS 解码/NMS。工业后缀为用户输入，不声明温度等级实测。
- 搬运：按用户批准的搬运功能验收保留既有 AXI3 master/adapter；传输字节数、cache、ownership、错误恢复及连续任务要求保持。
- PL：R04 bit SHA-256 `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`；XSA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。配置 FCLK 50 MHz；布局后 setup +0.156 ns、hold +0.078 ns、TNS/THS=0，DRC 393 项/0 errors。
- CSR RTL：`src/s2b_control_csr.sv` SHA-256 `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`。
- 原 PS infer ELF：`a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8`；恢复演练使用独立重建 ELF `f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9`，entry `0x00100000`。两个 ELF 不混称为同一文件。
- 接口：`s2b-physical/1.0.0` 和 `s2bu/1.1`，正文及 SHA 由最终交付清单固定；候选文件名中的历史编号不改变正文版本。

## 2. 实板证据与范围

| 要求 | 实际证据 | 边界 |
|---|---|---|
| 至少100个黄金样本 | T18 `formal_model_result_review_20261019_r01/scope_analysis.json`：108 个 ACK 闭合样本覆盖五类、无手、多手及边界框；双头整数张量及全部框比对通过 | 原109帧输出全部比较通过，但第109帧最后ACK缺动态读回，只按108个完整闭环计数 |
| 1000次连续任务 | 同次原始运行及独审重放1000次stress，序号/epoch闭合，无丢失、重复、死锁 | 不把后续少量恢复样本混入1000次 |
| 正常与忙启动 | 正常模型运行；R08 BusyObserver忙START拒绝，同RUN黄金与ACK，随后重新接受任务 | R08整体FAILED保留；局部场景另计 |
| 真正未决时取消/恢复 | R08 RUN且AXI_PENDING=1→ABORT→ERROR_SAFE/code8→匹配ACK→sample000黄金恢复 | 实际取消与安全归还；不声称未决时强制POR或外部reset波形 |
| CORE/DRAIN期限及恢复 | R12正常START、CORE=10000/DRAIN最大值错误5安全ACK、DRAIN=1/bit3安全ACK、DIAG0外部epoch对账、sample000黄金恢复 | 实板未观察FAULT_ISOLATED或晚响应；对应机制另依T11 RTL验证，不冒称板测 |
| 非法参数/拒绝命令 | R12静止矩阵中8个合法START的参数错误及ACK；11个COMMAND拒绝的LAST_REJECT及其他CSR无副作用 | SDK每笔BRESP仍UNKNOWN，响应类型仅按第3节组合证据判断 |
| RTL恢复矩阵 | T11 R07与独立R08：146 directed、128 random、25 integration、6362 cycles | 仿真与板测分层；不把仿真称实物观察 |
| 重建ELF演练 | 10月22日R02完整R04+新ELF易失下载、两相256B、weights、sample000双头及框黄金通过；随后只读补证确认安全IDLE/epoch1/账本0，cleanup=[] | R02在黄金后因host双响应误计数整体FAILED_CLEANUP；只读补证不改写原失败。10月21日旧R02的目录失败也保留 |

原1000+109运行独立重放1109份RUN，两头共28,113,150字节及全部检测框通过。其3项历史host源码漂移由 `formal_model_evidence_audit_20261019_r01/` 的Git原字节与输入/结果绑定解释，不声称原运行clean tree。原第109帧缺ACK和各失败RunId均保留。

R12的物理子范围完成后，原runner在封装阶段报告失败；原`orchestrator_result.json`的PASS/native0是封装前快照，实际脚本最终退出码未被捕获。已修复生产封装入口缺少接口版本及最终失败快照的问题；隔离副本以真实生产函数重放 `csr_r12_finalize_replay_20261022_r05/`，inputs/evidence 均为 CHECKS_OK。该重放只证明封装修复及真实子范围的文件绑定，不是新的板测，不改写原运行，也不把包装检查视为阶段通过。

## 3. COMMAND响应的组合证据

R12十一项拒绝均针对COMMAND地址 `0x43C00008`；每项核对前态、预期LAST_REJECT，其他CSR/epoch不变。原SDK响应 `UNKNOWN`、`NOT_OBSERVED`、`BLOCKED_BRESP_UNRESOLVED` 逐项保留。

R04固定CSR实现中这些COMMAND拒绝分支共用写入提交及响应输出路径，明确赋SLVERR。另一次同地址忙START的CPU原生postmortem保存DFSR `0x1808`、DFAR `0x43C00008`、fault PC/opcode与LAST_REJECT变化，独立分类为SLVERR。只有在源码、bit/XSA身份及逐场景路径都一致的独立审查通过后，才采用“共用RTL路径＋同地址原生代表事务”的实现级SLVERR推论；不表述为十一笔SDK直接读到了SLVERR。

八个非法参数START为合法接收后进入ERROR_SAFE/code1、2或3并匹配ACK，不能误列为总线SLVERR。静止helper的busy_start及外部UART同步能力限制由对应真实BusyObserver、DIAG0及黄金恢复证据单独覆盖。

## 4. 最终期限选择及定量依据

固定部署选用 `CORE_TIMEOUT_CYCLES=DRAIN_TIMEOUT_CYCLES=0xFFFFFFFF`，均为非零32-bit有限值。配置50 MHz下各自名义85.8993459秒；不延长、暂停或回绕硬件计数。UART响应期限是独立的秒单位。

T07冻结38层预算为逻辑读84,753,811、写11,382,150，合计96,135,961个逻辑单字节请求；卷积计算迭代424,506,368。按最低请求状态得到的616,778,290拍仅是下界，不用作HP等待上界。

实际R11、R12从START写调用之前到稳定DONE_SAFE读之后的完整wall包络分别为47.4017962秒、47.4058308秒，包含该次实际计算、HP响应/可能背压、控制和主机观察。较大者按绑定HWH配置50 MHz换算为2,370,291,540名义周期，乘1.25为2,962,864,425，小于4,294,967,295，余量1,332,102,870名义周期。未拆分可能重叠的HP等待或扣除计算下界；未把包络冒称精确PL周期、逐笔HP延迟或实测FCLK。

DRAIN最终值的观察期限依据包括：上述完整任务包络加25%为59.2572885秒，低于选定85.8993459秒；R11/R12的CORE故障场景实际以DRAIN最大值到达ERROR_SAFE/账本0并ACK。另以DRAIN=1的实板短测确认超限bit3仍保持失败诊断并安全归还；其42.262 ms主机观察区间不冒称最大值到期或精确硬件排空时间。

这些结果只支持所声明固定模型/平台及已执行任务的观察期限选择，不保证未来任意DDR停顿的最坏情况。接口规定期限超限后隔离且继续接收B/R；事务永久不结束时保持隔离，不能凭timer到期ACK或复用。实际FAULT_ISOLATED/晚响应板测未执行，T11相应仿真保留原验证层级。T07 10月21日候选仍为BLOCKED的原件不覆盖；本节新增纳入CORE场景真实DRAIN最大值及最终选择，独立阶段审查须按本节定量依据及限制判断。

## 5. 当前厂商资料与R04配置对应

Wong指定DDR按手册 `MT41K256M16TW-107`，两颗x16/32-bit/1GiB候选；不将D9PSK解码、PCB修订或实际电压测量称为已核实。

当前AX7Z020用户手册SHA `7d9e34045501637bc6277f7ad372f168165fc6969c640092909f1317b10ccedf`；随包AC7Z010/AC7Z020 Rev1.0核心板原理图SHA `5d810e712666839df18692ce05c3e280d39f9226de336315dab13b17b22339cc`。仅按各文档自身范围建立以下对应，不由资料推断本板修订身份。

| 项目 | 厂商来源 | R04实际生成配置 |
|---|---|---|
| PS时钟 | 手册第17页X1=33.333333 MHz→PS_CLK_500；第18页引脚E7 | PCW_CRYSTAL_PERIPHERAL_FREQMHZ=33.333333；生成init/XSA绑定 |
| UART发送/接收 | 手册第34页UART_TX=PS_MIO48/B12，UART_RX=PS_MIO49/C12 | UART1 MIO48..49、48输出/49输入，基址0xE0001000，115200；实收COM4/8N1 |
| MIO电平 | 核心板原理图第7页VCC1V8连接VCCO_MIO1_501及U1H的四个对应电源脚；VCC1V5另接VCCO_DDR_502 | MIO48/49及BANK1设置LVCMOS1.8V；不是实物电压读数 |
| DDR | 手册第12页；同核心板原理图第6/8页32位DDR及U8/U9候选颗粒 | R04 DDR配置MT41K256M16TW-107，32位，配置/init与XSA一致 |

手册第19页同时把BANK501写在+1.8V与+1.5V行，第33页UART示意图又标BANK500；原文保留。随包原理图第7页明确区分MIO BANK501的1.8V与DDR BANK502的1.5V，为R04设计电平选择提供更具体的连接依据；这不是厂商勘误证明或实装修订鉴定。整页、相邻切片及解析参数保存在T04 `board_material_mapping_20261022_r01/`，不使用旧AX7020手册页码替代本资料。

前置DDR有限测试：10月17日R02在安全地址0x10000000执行两种seed的CPU flush→DAP读及DAP写→CPU invalidate/读，256 B/64 words/两相零错；独审限定PASS，时间早于10月18日模型运行。阶段计划未要求此前探针与后续应用ELF完全相同。原cold=false标记保留，不把该旧观察改写为R04冷启动；当前恢复演练另记R04的真实下载与同范围cache探针。

## 6. 恢复与证据保留

PS恢复包 `S2B-T15/recovery_inputs_20261019_r02/recovery_bundle.zip` SHA `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`。隔离副本重新编译/链接成功，PT_LOAD归一GNU build-id后与原ELF一致；BSP静态库复用，不声明BSP/PL从源码完整重建。原R04位流、XSA及原始实现报告保留且不可由PS重建报告替代。

本次新ELF演练原件位于 T18 `rebuilt_app_acceptance_20261022_r02/`：真实weights seq3/epoch0、模型seq4/epoch1，双头5070/20280字节及全部框比对通过。host把包含权重和模型的两条记录误要求为一条，黄金之后才失败；最小修复提交 `16ce2cdf8c00c6214435629d75a5e4b63acb66a9`，15项回归及独立G2通过，不冒称原运行用了修复后的host。

紧接的只读补证 T18 `rebuilt_app_ack_observation_20261022_r01/observer_result.json` 为 `PASS_POST_R02_ACK_IDLE_EPOCH1_LEDGER0`、exit0、cleanup=[]：逐项核对原运行raw_logs哈希未变及旧资源关闭状态，不发UART、LOAD/START/ACK或reset，只停核并读取稳定安全IDLE、epoch1和四项账本零。原R02整体FAILED_CLEANUP保留；实板子项与补证共同交独立阶段审查，不改写历史终态。

最终清单保存真实配置、源码提交及文件哈希、工具版本、UART原字节、双头与框比较、ACK→IDLE/epoch/账本、CPU停止及会话清理证据。大产物留在声明artifact路径，不混入代码提交；不得清理冻结所依赖的恢复包、ELF、bit/XSA、原始运行和失败记录。新ELF另在最终候选RunId保存逐字节持久副本。BSP复用、硬件身份限制及各未观察实板场景保持；阶段批准以本记录开头指定的冻结回执为准。
