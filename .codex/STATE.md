# 项目状态入口

更新：2026-10-19（UTC+8）。按适用 AGENTS.md 恢复；运行状态以代码与原始证据为准。

## 目标、位置与授权

- 本窗口持续完成阶段2B：tiny416固定输入上板、至少100黄金样本（现有109）、1000连续任务、CSR异常恢复及G4/G5；未通过不得称冻结，不自动进入阶段3或推送。
- 实施树为 `D:\FPGA_Competition\w2b`，分支 `codex/stage2b-dma-g0`；本轮起始HEAD为 `2e9e3c625abe523e54be36a3010966b9f679c80e`，恢复时以实际Git HEAD为准。主目录只作全局入口，旧C盘工作树不再用作运行目录。
- 用户确认器件 `XC7Z020-2CLG400I`，Vivado part `xc7z020clg400-2`；不再因旧XA照片解读阻断。DDR按用户“以手册为准”采用第12页 `MT41K256M16TW-107`、双x16/32-bit/1GiB候选；实装D9PSK解码与PCB修订仍未知，不声称已验证。
- 用户已授权本阶段必要易失PL/PS下载、DDR装载和板上验收，不含QSPI非易失烧写。2026-10-18最新用户回复“18：30 JTAG 是的”：18:30上电、JTAG模式、断电至少10秒且上电后无人操作；原话无损绑定见 hardware_online_20261018_r01/user_message_utf8_r02.json，首份消息记录编码损坏原件保留。旧10月17日POR不复用。
- 用户确认DMA按搬运功能验收：保留自定义AXI3 master/adapter；字节长度、cache、ownership、错误、取消、完成和连续任务标准不变。
- 与DSH串行共享工作区：不修改其主目录XPR差异，不结束其他窗口会话，不操作对方沙箱权限，不全量暂存。主目录DSH交出及环境补正见主STATE和 `.codex/DSH_HANDOFF_20261018.md`。

## 已核实的技术结果

- 2A tiny416/8×8空间tile/8路输出通道/双头及PS解码NMS已冻结。109离线整网与D9比较均通过、最大误差0；不重复整网离线仿真，不当作2B板上结果。
- 外层CSR/恢复RTL完整矩阵R07及独立R08均通过：146 directed、128 random、25 integration、6362 cycles，两类四相位全1。CSR SHA `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`；入口 `report/evidence/S2B-T11/control_r18_xsim_first_axi_20261016_r07/`、`control_r18_independent_20261016_r08/`。G2不替代板上恢复。
- 现有物理接口正文首行为 `s2b-physical/1.0.0 | G0_FROZEN`、UART为 `s2bu/1.1 | G0_FROZEN`；仅接口定义与受控实验规程冻结，不代表具体部署G0或G3/G4/G5。旧0.1.2候选名称不覆盖当前正文；源码闭包绑定正文实际SHA，不复用旧32×32分类规格。
- T19 R04已完成XC/-2、50MHz实际路由，setup +0.156ns、hold +0.078ns、TNS/THS零；DRC 393项/0 errors。原始input_record保持FAIL（profile标记未采到stdout），Vivado Job原生0及22项产物哈希已核对；不为采集标记问题重跑综合。入口 `report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/`。
- R04 bit SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`；XSA SHA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`，内嵌bit一致。
- T15已按同R04 XSA重建BSP/ELF：infer SHA `a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8`，init SHA `237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1`；入口 `report/evidence/S2B-T15/qualification_r04_xsa_rebuild_20261016_r04_artifacts/`。原R04旧ELF来源不匹配的记录保留，不混用。
- 旧R04独立资格收据实际存在且PASS，SHA `f6d94bb66ffb678d1334a7194246029d955e62df6075369ca17c422a266f30fe`；只覆盖sample000入口机制，硬件/sample结果NOT_RUN。入口 `report/evidence/S2B-T19/qualification_single_sample_review_20261017_r04/`。
- 最新历史资格运行R14为BLOCKED、hardware_attempted=false、hardware_execution=NOT_RUN，原因是直接调用Python未使用官方Vitis2026.1环境。原件 `report/evidence/S2B-T19/single_sample_qualification_20261017_r14/model_qualification_result.json` 保持不变。

## 本轮离线闭环

- 官方 `D:\Xilinx\2026.1\Vitis\bin\vitis.bat -s` 已真实验证Vitis v2026.1/Python3.13及绑定XSDB/pyserial3.5导入，最终r03启动器/脚本均退出0；没有创建SDK会话、启动server、打开串口或操作板卡。入口 `report/evidence/S2B-T19/qualification_runtime_offline_20261018_r03/`；r01沙箱失败和r02成功原件均保留。
- 新增离线检查器 `verification/check_s2b_qualification_runtime.py`，使用显式配置/结果环境变量、UTC+8和独占结果文件创建。官方启动器退出0不能单独替代脚本结果。
- 旧C盘人工根已随历史树迁到 `D:\codex-worktrees\96a3`。runner仅固定迁移后的读取位置，保留用户原始C路径引用、两个JSON原字节及批准SHA：`c87a2f40…321ce5`、`e22fd0a1…c3d4c7ea`；没有改写历史JSON或扩大信任范围。
- 34项候选源码/平台绑定核验通过，30项入口单测由总控与独立Reviewer分别运行退出0。新canonical digest为 `cf57921c78d33828f5c5da71d5ba7c6dba8f53a8f12d535b804d527dc560c6aa`；旧R04 canonical已被正确拒绝，不能自动继承旧收据。
- 本轮独审PASS仅限离线迁移、入口代码和runtime checker；入口 `report/evidence/S2B-T19/offline_runtime_migration_review_20261018_r01/review_outcome.json`。单测/导入/包装检查均不代表G3/G4/G5。
- 109/1000执行器与CSR恢复执行器已存在，无需因本轮迁盘修改其功能。可复用 `report/evidence/S2B-T18/model_assets_20261016_r02/prep/preparation.json` 的109项输入/黄金引用；全部仍NOT_RUN。

## 当前阻碍与下一步

- 已提交资格helper修复、31项回归及真实首样本证据：`e9fac6cbb1a0b7b60cd33e348dd1d304388de043`。首样本R02于19:00至19:11完成，native0、`GOLDEN_AND_ACK_IDLE_OBSERVED`、cleanup_errors=[]；双头5070/20280字节与全部框黄金一致，DONE_SAFE/HEAD_VALID，ACK后IDLE/epoch1，CPU停止、映射清理并断会话。原始状态仍为 `SINGLE_JOB_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`，独审单样本观察PASS见 `S2B-T18/formal_review_20261018_r01/sample000_independent_review.json`；不是109/1000或阶段PASS。结果SHA `fa7174856e98889978c00122d779b8102b5a40cc4ce3d3dcd67f2e91740e3324`。旧R01失败及cache身份时间误差失败原件保持。
- T18正式入口已补CSR映射注册/自有映射清理、修正正式接口首行版本解析，并按用户最新要求改为权重→1000连续任务→109语料，失败立即停止；没有减少数量/黄金条件，没有改JTAG、probe或34项平台闭包。原35项runner及23项调度回归通过，四文件独审见 `formal_execution_review_20261018_r02/review_outcome.json`。正式R01在首帧前因把文件引用误当构建内容而KeyError，无WEIGHTS/RUN/HP，清理成功；现两行改用预检已验证的checked.build，36项回归和增量独审PASS，见 `formal_build_context_fix_20261018_r01/`、`formal_execution_review_20261018_r02/review_outcome_r03.json` SHA `7051ccbdbab45a22dd9bb97b9f3aeb6d98dfc4fc299c8b8f6262bdd7f213f1d4`。当前runner SHA `f71d2e2c350fcff50336ac304737a9c6e2a66be101c2204cd54596f6867d3a60`。
- 同R04 ELF/BSP/MMU的visibility proof/review、最终平台manifest/review及冷链回执已独审，见 `formal_review_20261018_r01/`、`final_platform_review_20261018_r01/`；仅覆盖当前单样本/平台准入，不是压力或G5通过。冷链基于18:30用户POR→无HP缓存探针→单样本SAFE/ACK→19:13:34主机独占快照，未改旧cold=false等原始记录，不因软件前置失败要求重复POR。
- 新G0 R02绑定仅因host调度源码更新而重绑的prep：`formal_online_20261018_r01/preparation_stress_first.json` SHA `7121f86a36db1920652275af6ea0684af0dc1dd374d6fac3d4e438dc47049c09`；原109行、权重、输入及黄金JSON值完全不变。G0回执 `formal_execution_review_20261018_r02/g0_receipt_r02.json` SHA `cf8366cee925bc67751b751107afeb91c2b73b732864abc76d84a7fe2b1a078b` 已固定。最终 `formal_online_20261018_r01/model_config_r02.json` SHA `2cab084508388688480dd27b1d855e112462088bccb3edda3061f5329729506f` 已通过G0/cold与109 prep验证，完整runtime/主机检查仍未运行。
- 自动审批超时/网络失败记录 `formal_online_20261018_r01/approval_service_failure_r01.json` 原件保留；服务已恢复。CIM真实确认原hw_server/3121均无进程后才新建本任务服务，当前PID10116/父23784，身份从同源CIM绑定，COM4/PNP相同；不因先前无HP软件错误要求新POR。
- 当前真实后台R02于23:45:13启动：launcher PID13956，官方Vitis Python PID26564，hw_server PID10116；23:48:26主机快照确认仍活，部署、CSR映射、banner和T18 admit均PASS，正在发送权重，尚未计入模型完成次数。配置 `formal_online_20261018_r01/model_config_r04.json` SHA `52535107f08a670aaf389fa88cd46a5d0e68ef6dc4c7e44b42d54095356d59fb`，运行基线e9fac6c、实际runner SHA同上；启动记录 `background_launch_r02.json`、快照 `background_r02_running_snapshot.json`。正式R01失败原件和旧启动记录不覆盖。
- 当前活动目录为 `report/evidence/S2B-T18/formal_stress1000_then109_20261018_r02_deployment/` 与 `formal_stress1000_then109_20261018_r02/`；进度在后者 `frames/progress.jsonl`，1000请求为 `frames/request_00000002.json`，权重完成后才发送。1000成功后同一进程自动执行109；日志 `formal_online_20261018_r01/background_r02_stdout.log`/`background_r02_stderr.log`。禁止重启、重传或另开板上任务争用设备。以实际进程和进度/最终orchestrator_result为准，不以启动器退出0代替脚本结果。用户要求后台启动后结束本轮等待。
- 一次性续办已按用户要求通过原生工具改为2026-10-19南京时间06:30，automation ID仍为 `10-19-05-2b-dsh`，目标窗口 `01a09ffa-555f-75f1-bdca-23787df39912`；不把已设置时间当作成功执行。用户授权该窗口继续与DSH对接、必要时自行关闭DSH、范围内自主决定；不得终止健康验收任务或争用JTAG/COM4。
- 2026-10-19在正式运行期间完成固定输入核验并独审PASS：498处绑定、490文件、100084257字节全部SHA一致，XSA内嵌bit一致；提交 `f99b2e9f04a18b3e1d3eb0a24bd1ed6b07b41823`，入口 `S2B-T18/freeze_input_check_20261019_r02/`。R01沙箱读取Python312串口库受限的失败原件保留；R02授权只读核验及inputs/evidence检查通过，不代表G3/G4/G5。活动代码/配置未改，证据提交造成HEAD前进不使既有运行失效。13:06已观察958/1000、corpus0，运行仍须读实时进度。CSR现有flow已具备忙启动、非法参数、ABORT黄金恢复及静止矩阵；短超时/排空和忙时实际reset尚未由该flow覆盖，待当前1000及109结束并清理设备后执行板上后续。
- 已独审离线准备：`S2B-T07/deadline_budget_20261019_r02/` 重算38层逻辑请求96135961、卷积compute迭代424506368、含最少request/response状态的乐观下界616778290 cycles；不代表实际周期或HP延迟上界。cache维护覆盖实际input/weights/features及两头，未用arena区不新增逐字节探针要求。`S2B-T15/offline_restore_20261019_r01/` 在隔离副本重编译4个C对象和两个ELF链接退出0，入口/布局相同，PT_LOAD仅20字节GNU build-id差异，归一化一致；BSP复用、PL未重建、副本linker BOM被忽略及初期部分失败日志已覆写的限制保留。上述准备及关闭日志已提交 `061f592`、`e1b048f`。回执 `S2B-T18/offline_freeze_preparation_review_20261019_r01/`；CSR覆盖/未测项见 `S2B-T20/csr_offline_coverage_20261019_r01/`。
- PS独立恢复输入包已完成且独审PASS：`S2B-T15/recovery_inputs_20261019_r02/recovery_bundle.zip`，697551字节，SHA `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`；含67个BSP头及3库，从新解包目录真实重编译4个C对象并链接两个ELF，退出均0，PT_LOAD仅GNU build-id描述字段差异。消费包不再依赖旧tmp，但仍依赖官方GCC及已构建BSP库；不是BSP/PL源码重建或板上验证。ZIP属于必须保留的本地artifact，不随Git源码提交，不得清理；R01遗漏系统头的失败及R02前置失败保留，初版comparison丢失和dependency inventory汇总字段错误见provenance_limits，不消费错误字段为证明。独审回执 `S2B-T15/recovery_input_review_20261019_r01/`。正式109/1000、后续板上异常恢复、实际周期/HP量测与G4/G5仍未完成。
- 首样本发送45.053秒、发送结束至完整结果49.652秒；1000约14小时仅为单样本外推，今日不能承诺冻结。CORE/DRAIN均有限 `0xFFFFFFFF`，UART观察450秒；最终deadline量化、109/1000、板上异常恢复、适用干净重建/可恢复冻结及G3/G4/G5均未完成。核心综合总预算10次，已用6次，单重型，不重跑现有R04构建；不得使用DSH降级DRC的counter探针bit上板。
