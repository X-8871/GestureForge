# S2B-T20 G4/G5 最小证据矩阵

审计日期：2026-10-19（南京时间，UTC+8）  
审计基线：`75fcc5950f6d848ea5bfbb94226e20a63fe1e075`  
结论：**阶段2B仍 NOT ACCEPTED**。本表只把已有证据按正式标准归位；不改写原运行状态，不新增门槛。

## 数量门槛

| 标准 | 现有证据 | 判定 |
|---|---|---|
| 至少100个规定覆盖的黄金样本，检测头整数张量及冻结规则框结果一致 | [scope_analysis.json](../../../../S2B-T18/formal_model_result_review_20261019_r01/scope_analysis.json) 重放既有独立结果，确定 corpus index 0–107 共108个样本均有后继成功RUN证明前一匹配ACK；108个覆盖五类、无手、多框、边界框、空框和小框。原R02对109个样本的头数据与框比较均匹配。 | **PASS：数量与覆盖满足。** 不是把最后的index 108 ACK补证；该样本不计入闭合的108个。 |
| 至少1000次连续任务无丢失、重复或死锁 | 同一 `scope_analysis.json`：stress indices 0–999、epoch 1–1000均由成功响应及下一任务闭合ACK；原官方模型运行结果为 `PASS_MODEL_CORPUS_AND_STRESS_ONLY`、native exit 0。 | **PASS：1000次闭合。** |
| 109语料整批的原运行最后状态 | [原R02结果](../../../../S2B-T18/formal_stress1000_then109_20261018_r02/orchestrator_result.json) 加独立范围分析：109个输出均匹配，但index 108 / sequence 111 / frame 1108 / epoch 1109缺该R02进程结束前的动态ACK/IDLE读回。 | **限于原R02全109 ACK断言未证明。** 这不推翻正式计划的100样本数量门槛，108个已经闭合且覆盖范围足够。 |

因此“1000 + 108闭合黄金”已经满足正式数量门槛；不能描述为“109个R02任务全部动态ACK已证明”。

## R08 / R09 实板证据

| 运行/场景 | 真实观测 | 可计范围与限制 |
|---|---|---|
| R08 sample000 seed | [R08 seed回执](../../../../S2B-T20/formal_csr_recovery_20261019_r08_csr_seed_sample000/acceptance_result.json)：真实板上完整sample000双头/框匹配、正常安全完成。 | **PASS，限sample000 seed。** |
| R08 busy START → golden / ACK | [busy observer结果](../../../../S2B-T20/formal_csr_recovery_20261019_r08_csr_busy_observer/busy_result.json)：RUN期间CPU0发起busy START；前后CSR显示任务/epoch不被拒绝写改变，`LAST_REJECT=1`；同一运行后续sample000响应与黄金匹配并ACK回IDLE。SDK只返回 `AHB AP transaction error`，原生BRESP记录 `NOT_OBSERVED`，状态为 `BUSY_REJECTION_AND_GOLD_BRESP_UNRESOLVED`。 | **有拒绝无副作用和后续黄金/ACK证据；SLVERR类型未证，不能算精确BRESP PASS。** |
| R08 reaccept | [reaccept回执](../../../../S2B-T20/formal_csr_recovery_20261019_r08_csr_reaccept_sample000_frame0/acceptance_result.json)：拒绝后再次执行frame0黄金并安全ACK。 | **PASS，限该重接受场景。** |
| R08 ABORT / pending recovery | [CSR recovery结果](../../../../S2B-T20/formal_csr_recovery_20261019_r08_csr_abort_recovery/csr_result.json) 和[abort_final事件](../../../../S2B-T20/formal_csr_recovery_20261019_r08_csr_abort_recovery/csr_events.jsonl)：ABORT前状态为RUN+PL owner+AXI_PENDING、epoch 4；SDK对ABORT写合法返回，之后读到ERROR_SAFE/TERMINAL/SAFE_TO_REUSE、owner归PS、pending清零、error 8；显式ACK后真实sample000恢复黄金为epoch 5。 | **PASS，限实测内核软复位/ABORT→排空至安全终态→ACK→新黄金任务。** 这已经是一次真实pending期间的恢复证据，不能误写成“没有实测pending恢复”。但没有观察到超过DRAIN观察期限后再到达的迟响应。 |
| R08静止拒绝矩阵及总状态 | [R08顶层结果](../../../../S2B-T18/formal_csr_recovery_20261019_r08/acceptance_result.json)：前述阶段已保存；静止矩阵第一项`idle_bad_encoding`的SDK结果为UNKNOWN，按 fail-stop停止，后续静止非法参数场景未执行。总体 `FAILED_CSR_RECOVERY_SCOPE_ONLY`，native/launcher exit 2。序列/端口/映射/disconnect清理多数通过，但 `controller.close` 记有清理错误。 | **原R08保持FAILED；阶段局部证据仍按各自真实回执计。未知BRESP与未执行静止场景不得转成PASS。** |
| R09 / 下一次deadline profile | R09未启动；截至本审计时，正式实板R10也未启动，不能引用计划或缓存配置作结果。 | **NOT RUN。** 129项Vitis单测是离线代码回归，不替代板测。 |

## G4/G5 对照

| 正式要求 | 证据入口 | 判定 / 尚缺的范围 |
|---|---|---|
| 规定模型、输入、实际位流/板卡身份绑定；UART数据完整并黄金比较 | 原模型R02、R08 deployment和逐项回执；R08使用R04 bit与infer ELF。109输出已匹配；108 golden与1000 stress满足数量门槛。 | **数据比较PASS；版本/运行身份有绑定。** 原R02最终ACK证据限制如上，R08仅是CSR sample000场景。 |
| 路由后实际时序，setup/hold满足且TNS/THS为零 | [R04 timing_summary.rpt](../../../../S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/timing_summary.rpt)、实际setup/hold报告及DRC；50 MHz下 WNS +0.156 ns、WHS +0.078 ns、TNS/THS 0、DRC无相关violation；bit SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`。 | **PASS，限R04实现物与该证据绑定。** 外层`input_record.json`的profile状态为FAIL（stdout未捕获）；Job/已保存路由报告与产物哈希可核，保留该包装记录限制。 |
| 正常总工作量及deadline依据 | 物理接口正文§7要求38层请求数、HP延迟/背压及计算依据，并证明总周期加余量≤32-bit上限。候选接口也明确：没有精确PL周期CSR时，周期字段标记`NOT_MEASURED`，不能把UART wall说成精确PL cycles。R09未运行；R10亦尚未启动。 | **当前实板deadline证据未执行。** 规范允许采用有依据的保守总周期上界证明期限容量，不要求每个内部状态都提供精确计数器；host wall×已绑定50 MHz并加25%余量可记为“估算上界”而非实测PL周期，须绑定覆盖完整模型的START→DONE_SAFE窗口和时钟配置。此估算不能替代精确周期字段，也不能单独证明DRAIN超期迟响应。 |
| GP0忙命令、非法参数的原生响应与无副作用；IDLE/ACK顺序 | 物理接口§3；R08 busy observer仅有AHB AP错误类别和`LAST_REJECT=1`，R08静止矩阵在第一项UNKNOWN停止。 | **部分行为观测；BRESP精确SLVERR未证，剩余静止矩阵未执行。** 这是当前直接阻断的接口验收范围。 |
| CSR异常恢复和真实事务排空 | 物理接口§4–5、R08 ABORT事件。真实AXI_PENDING在ABORT前为1，之后清零，进入ERROR_SAFE，再ACK与新任务成功。T11独立RTL集成仿真亦覆盖DRAIN超时后合法晚R闭合账本及永久未完成ledger继续隔离。 | **层级证据PASS：R08证明真实板上pending ABORT后安全排空；T11 R08证明集成RTL的超时晚排空和永久隔离分支。** 规范没有要求必须在板上人为注入永久stall；有可控故障源时的真实晚响应不应与现有RTL证明混为同一声明。 |
| 复位与恢复符合约定 | 阶段计划§2B要求复位/恢复行为；物理接口§3/§7给出reset拓扑与真实GP0 reset边界。R08先读旧终态/账本确认安全，再冷复位部署；R08也实测RUN+AXI_PENDING期间ABORT触发内核soft_reset并安全恢复。T11 R08 RTL矩阵包含reset场景。 | **已证明允许范围内的冷启动/安全重入和pending时ABORT软复位。** 冻结接口明确禁止用FCLK reset/POR/cold reset清除未决事务；因此不得把“未决时主动发system reset”列为缺失或要求。单独FCLK波形不是正式计划所列独立交付物；状态/事务轨迹应绑定reset行为。 |
| DDR / 缓冲所有权 / 物理内存映射 | T19 visibility0 cache probe在`0x10000000`对256字节做两phase cross-master读写观察，结果字段为`CROSS_MASTER_256_BYTES_MATCHED`；输入原件外层状态仍`API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`，独立复核仅覆盖server release附件。STATE记录用户按手册确认MT41K256M16TW-107候选，但实装D9PSK编码、PCB修订未知。 | **有限DDR/cache观测有证据；不能上升为32MiB/HP全域证明或DDR料号/PCB绑定。** 按用户授权可继续以手册候选为工作依据，物理对应仍作为限制记录。 |
| 恢复 / 干净重建和交付包 | [PS副本恢复汇总](../../../../S2B-T15/recovery_inputs_20261019_r02/final_summary.json)：隔离副本中PS infer/init C对象与ELF编译链接均成功，归一化PT_LOAD一致；恢复包SHA `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`。 | **PASS，限PS应用输入包和离线重编译。** 不含BSP从源生成、XSA/PL/bit重建，也没有硬件恢复演练；不能单独关闭G5重建/恢复。 |
| 129项Vitis CSR suite | [regression_result.json](../../../../S2B-T20/csr_combined_flow_20261019_r01/regression_result.json)：129/129、native 0、Vitis 2026.1。 | **PASS，限离线代码回归。** 报告自己明确“不代表CSR实板或阶段2B验收通过”。 |

## 尚需的最小实测范围

以下只复述正式计划及已冻结物理接口明确要求，未添加新门槛：

1. 取得CPU/GP0实际写响应的可核证据，证明busy/非法命令按接口返回SLVERR，并保留`LAST_REJECT`及状态/epoch无副作用证据。当前SDK的AHB AP异常不能区分BRESP，R08的UNKNOWN也不能算通过。
2. 完成剩余静止非法参数/编码场景；每项按接口预期记录响应及状态不变。R08在第一项UNKNOWN后正确停止，未执行项保持未执行。
3. 完成部署deadline依据及非零CORE/DRAIN值的实板受控观察。可报告保守周期上界并明确`PL cycles=NOT_MEASURED`；不得把上界包装成精确周期。R09未运行、R10亦未启动。
4. 现有T11 RTL超期晚排空/永久隔离和R08真实pending ABORT排空分别计入对应模块及硬件证据层级；若需声明硬件确实跨过DRAIN期限后收到晚响应，必须另有真实HP trace。现有资料未显示可控板端stall/late-response注入接口，因此不额外要求为此新增硬件故障逻辑。
5. reset范围以可安全执行边界验收：冷复位前确认旧事务终结；pending时用已实测ABORT/软复位和账本排空路径。不得主动制造违反未决事务保护原则的系统reset交叠。单独reset波形不是独立门槛。
6. 保留T19 256B/two-phase cache探针的有限实测范围，并按用户手册授权表述DDR候选；DDR料号/PCB关系仍限制。PS副本恢复仅覆盖离线应用重编译，完整PL/PS重建包仍未闭合。

## 范围说明

本审计只读取正式计划、冻结物理接口、模型scope分析、R04时序/DRC、PS恢复、T19 cache probe、T11独立RTL矩阵和R08冻结回执；未运行测试、SDK/JTAG/UART或硬件，没有改源码、HEAD或既有运行目录。源证据哈希列于同目录 `audit_result.json`。本矩阵不是独立阶段PASS，也不更改R08失败状态或deadline profile尚未执行状态。
