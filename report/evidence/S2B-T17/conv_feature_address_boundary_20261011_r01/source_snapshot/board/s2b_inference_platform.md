# 阶段 2B 全模型平台构建候选

版本 `s2b-inference-platform/0.1.10`，依据 `s2b-physical-candidate/0.1.1`；字段入口为同目录 JSON。此文件说明实际构建和证据约束，不声明物理接口已冻结或阶段 2B 已验收。

用户提供的芯片字符串原样保存为 `XC7Z020-2CLG400I`。Vivado 精确器件候选为 `xc7z020clg400-2`；生成时核对 `get_parts` 唯一返回，并记录可获得的 temperature/grade/speed/package 属性。工具名称不含 `I` 不能单独证明实物工业温度等级。DDR/UART 请求调用冻结 `s2b_ps_platform::requested`，只增加 GP0、HP0、FCLK0/reset 与 50 MHz 配置，不使用通用 board preset 替换厂商字段。

## 模块、地址和物理端口

JSON 声明 18 个实际编译 RTL 文件：6 个原冻结 2A 模块、8 个 2B 派生模块，以及原有 guard、word adapter、控制器和 `s2b_inference_top`。原冻结 2A 全核心14源保持原字节，以 `source_derivation.upstream_sources` 显式绑定路径和SHA；上游冻结提交为 `671f9cf494b92ce182b3f1542fefd0cfd4b209f5`。派生链历史基线为 `f53e067ba91abc02ed60cf7f9063884d9ddb79f1`；本轮S10开发基线为已保存S9实际综合失败证据的提交 `3f24c94564d10103aaa00db07356f666b085f687`。S1 几何常量化的原始开发基线 `18c0c34f9da885b5f35869c282dc0c2ed50d720e` 和旧证据保留。顶层通过原公共 CSR/memory 口连接派生核心，不读取内部状态。adapter 内已有 guard 实例，不重复串接第二套 guard。

派生策略 `s2b-constant-geometry-coordinates-route-and-conv-validation/1.0.0` 保留 S1 的严格几何常量化：`s2b_maxpool_engine` 内部 geometry kernel为2×2、stride为2×2、Darknet padding参数为1；`s2b_upsample_engine` 内部 query stride为2。原外部参数、参数/长度/地址拒绝判断、错误优先、全部状态、握手、abort和数据通路均保留。池化三个合法层及上采样层33在消费query之前已严格验证这些参数，因此常量连接在成功分支与原输入完全相同；非法输入仍按原先的前置分支拒绝。

S2 仅在派生 backend 加入 C/Y/X 三个坐标寄存器，共25位，并替换原组合坐标除模。38层冻结输出均 N=1、C≤512、H/W≤208；保留原32位 index及64位 count。在原复位、abort、启动、alias换层、结果换层的5个 index归零分支把坐标同步归零，在唯一成功非conv且index+1<count分支按X→Y→C进位。其他分支保持，WAIT 已形成的结果在owner掉低时仍按原条件推进，错误优先于进位，不能额外加入owner门禁。合法索引不变量 `i=c*H*W+y*W+x` 及界限保证原含 `%C` 的 decode与寄存器一致，最后元素的原count条件排除通道wrap；卷积层backend index=0，卷积内部tile坐标不变。所有状态、请求/响应、结果周期、未知状态及descriptor错误门禁保持。`s2b_stage2b_core` 仍只改模块名和backend引用；conv、GF8、INT8与输出布局不变，没有新增周期或时序例外。

S3 新增 `s2b_route_engine` 与 `s2b_route_query`，引擎仅替换模块名和query引用，backend仅更换route引擎引用。11个冻结ROUTE层为3/6/8/11/14/16/19/22/24/31/34；3/11/19为groups=2、group_id=1，其余为groups=1、group_id=0。原query的groups=2已用通道低位及右移验证；派生仅删除groups>2的动态除法/余数分支并按BAD_ARGUMENT拒绝。公开CSR没有groups字段，backend唯一来源为原冻结descriptor ROM；START、inputbase、owner、abort和reset均无法改变ROM组数。实际profile可达域及groups=0、groups=1/2的非法shape/channel/id/index/地址错误优先保持；通用合法groups≥3的直接query输入明确不等价且不适用本profile，其通用实现保留在原2A源。独立验证必须绑定ROM原SHA、逐层枚举及真实backend请求trace，不能靠派生声明证明不可达。

`derived_sources` 每项绑定源/派生路径、派生SHA和逐项允许的字符替换。派生文件按UTF-8/LF创建；仅验证派生关系时将上游CRLF转换为LF，原14源的SHA仍绑定原始字节。检查器独立固定上游14源SHA及允许替换，核对派生源除此之外逐字符一致、实际编译闭包精确为6+8+4，并要求Tcl/JSON版本和闭包一致。S2 坐标来源、全38层数学枚举与实际RTL逐周期/全部nonconv请求trace由独立证据绑定，不由profile字段自证。该版本尚未证明50MHz收敛；旧0.1.0/0.1.1/0.1.2/0.1.3的BD/XSA、综合和可见性证明不能继承为新实现的通过结果。

PS GP0 为 AXI3、32 位数据、12 位 ID，经 `axi_protocol_converter` 到 AXI4-Lite、32 位数据与完整 32 位地址，再到控制器；地址分配 `0x43C00000` / 64 KiB。控制器自行校验完整地址，不截断到低 16 位后盲目接受。HP0 为原生 AXI3、64 位数据、6 位 ID，直接连接 adapter；保留 AXI3 WID、2 位 LOCK 和 4 位 LEN，不套用 AXI4 的早 B 依赖规则。HP 可寻址 1 GiB 是 PS address segment；PL 许可仍由 guard 逐对象限制，完整模型专属 DDR arena 为 `[0x10000000,0x12000000)`。

软件只发对齐 32 位、单 beat、Device/Strongly-ordered MMIO。Lite 口没有 LEN，转换器可以拆 burst，下游控制器无法判断原 GP0 burst；本结构的单 beat 前提必须由实际 PS 指令、MMU 属性、反汇编和集成输入验证确认。不能宣称控制器拒绝了上游原始 burst。GP0 STATUS 读不是 HP0 写屏障。

FCLK0 50 MHz 同时驱动 GP0/HP0 ACLK、转换器、reset 同步器和完整推理 RTL。FCLK_RESET0_N 接 active-low `proc_sys_reset.ext_reset_in`；aux/debug 接 0、dcm_locked 接 1，同步释放的 peripheral_aresetn 同时接转换器与完整 RTL。此时钟来自 PS，未增加 MMCM；dcm_locked 常量仅表示无独立锁相器，不能证明可见性或实际时序收敛。BD 唯一物理外口为 DDR/FIXED_IO，UART 通过固定 MIO，不增加未经板级资料核验的 PL 引脚约束。

## 冷复位与可见性启用

`cold_resetn` 只用于统一 PS/DDR/PL 冷初始化。运行中禁止软件独立切换 FCLK reset、PS7 reset 或重下 PL 位流；上述操作会丢弃 adapter 账本，随后继续旧 CPU 任务或复用旧 arena 不安全。FAULT 未合法闭合必须停止旧软件和 CPU1/其他 writer，统一初始化 PS/DDR/互连/PL、重新初始化 arena、消除旧 cache 副本并进入新 epoch；总控冷 JTAG 操作须保留实际生命周期证据。此约束由部署流程执行，当前接线没有硬件识别“全体系冷复位”的能力，不能把单独 FCLK reset 自动解释为冷恢复。控制器 soft_reset/cancel 保留物理账本并排空，不连接到该冷复位线。

`PROFILE_VISIBILITY_PROVEN` 默认 0，无软件寄存器可置 1。默认构建可用于离线审阅和静态网表验证，不能宣称 DONE_SAFE 已可用。visibility=0 并不禁止 START；一旦启动则不能依靠该构建取得 SAFE/ACK 后重新读 arena，因此首次先验探针必须全程保持 `IDLE_PS`、epoch=0、从未 START、未 LOAD，由 CPU 合法独占 arena。

首次缓存先验使用 CPU0 ↔ JTAG DAP 第二 master，不让 HP 发起模型任务。T15 公开候选传输为 `S2BU/1`、operation=4、40 字节 header、12 字节 payload（phase/cpu_seed/dap_seed）；仅访问物理 `0x10000000` 起的 256 字节、64 个 word，word i 为 `seed ^ ((0x9e3779b9 * i) mod 2^32)`。phase0 CPU 写 cpu_seed pattern、实际 BSP FlushRange+DSB 后回复 WAIT_DAP；总控 DAP 读取完整 256 字节核对，再写 dap_seed pattern 并完整读回。phase1 使用同一 seed pair，实际 BSP InvalidateRange+DSB，CPU 真实比较 64 word，期间禁止 LOAD/RUN；任何不符 fail-stop。响应为 40 字节 meta 加 256 字节实际原字节，保留 header/payload CRC；成功 code=0，失败 code=7 且保留原字节后停止。该先验须绑定最终同一 ELF、BSP、MMU、编译宏及实际 PS 初始化、统一冷生命周期、CPU1/其他 writer 静止、专属 arena 证据与原始 UART/DAP 读写记录；当前 T15 未冻结时仅说明 ABI，不伪造通过或固定其未交付 SHA。

HP 路径另以实际全模型 BD/网表、adapter 两路 AxCACHE=0000、直接 HP0 无桥/无早写响应及官方 AXI3 非 Bufferable / UG585 原始依据独立证明。CPU/DAP 先验只验证上述实际 BSP/cache 路径，不能代替 HP→CPU 模型输出；启用参数 1 后，真实 HP 传输、CPU golden 比对和完整模型结果仍是 G3 必须项。此入口不改变 SAFE 的停止、账本排空和可见性条件。

启用参数由 `run` 同时接收证明 JSON、独立审查 JSON，以及总控从真实独立 Reviewer 返回来源冻结的审查原件 SHA-256。只读检查器只返回 `VISIBILITY_PROFILE:BINDINGS_VERIFIED`，表示文件绑定匹配；总控仍须核对审批来源、原始证据语义和允许的启用范围。

证明 JSON 包含 `schema_version=1`、`status=PASS`、`profile_version=s2b-inference-platform/0.1.8`、`source_sha256` 和两项 `hp_path_audit` / `ps_cache_proof`（每项为仓库相对 `path` 及真实 `sha256`）。`source_sha256` 的精确文件集合由检查器的 `check_static` 返回，包含活跃18 RTL与未编译的8个原上游源，共26个RTL，以及构建脚本、平台JSON/说明、PS字段和检查器本身。源文件或平台配置变化使旧证明失效。

两项证据 JSON 均须 `status=PASS`、同一 `source_sha256`、非空 `evidence_files`（各原始文件 path/hash）与布尔 `checks`。HP 审计要求 `axi3_nonbufferable_basis`、`axcache_0000_full_path`、`direct_hp0_no_bridge`、`no_early_write_response`、`full_model_core_present`。PS 证明要求 `dedicated_32mib_arena`、`cache_maintenance_actual_bsp`、`cpu_dap_prior_probe_idle_no_start`、`same_runtime_bsp_mmu_macros`、`no_use_amp`、`single_cacheable_alias`、`cpu1_other_writers_stopped`、`unified_cold_reset_lifecycle`。

PS 证据的 `prior_probe` 字段包含上述 visibility/state/epoch/start_count/load_count、ABI、地址/长度/word 数、`phase0=FLUSH_DSB_WAIT_DAP`、`phase1=INVALIDATE_DSB_COMPARE`、`dap_read_write_readback=true`。PS 证据与证明 JSON 均含一致的 `runtime_bindings`，其中 `elf`、`bsp`、`mmu`、`macros`、`ps_init`、`cold_lifecycle`、`uart_log`、`dap_log` 各绑定仓库内实际原件 path/hash。实际网表、规范依据和运行记录必须存在原件；布尔字段及哈希只做机器绑定检查，真实过程与语义由 Reviewer 核查。

独立审查 JSON 须 `status=PASS`、`role=INDEPENDENT_REVIEWER`、`approved_profile_sha256` 绑定证明原字节、`visibility_parameter=1`、`cold_reset_only=true`；调用者还须提供从独立 Reviewer 实际交付通道取得并冻结的该原件 SHA-256。机器不能识别真正的 Reviewer 来源，自填 role/PASS 或从自造 receipt 计算哈希都不构成批准。总控核对原始返回来源后才可调用启用入口。该机制防止误用过期文件，不是密码学签名；当前未生成有效证明或启用记录，默认保持 0。

## 隔离重建入口

先执行轻量检查：

```bash
python -B verification/check_s2b_inference_platform.py
```

在总控核对资源、重型占用与会话归属后，使用新的 Tcl batch 会话调用 `::s2b_inference_platform::run repo_root project_dir evidence_dir helper native_log`；全部参数是已核验的绝对路径，project_dir/evidence_dir 必须不存在、互不相同且不嵌套，精确父目录已存在。入口在 source 或创建目录前逐组件核对大小写、名称与类型，拒绝链接、junction/reparse、点组件和可能被 Windows 折叠的新名称；Windows reparse 属性由固定只读 .NET 调用补核，路径作为 Base64 数据传入，失败立即停止。repo_root 指当前工作树，project_dir 放 `tmp/2B/S2B-T13/<新RunId>/project`，evidence_dir 放 `report/evidence/S2B-T13/<新RunId>`；helper 指已安装 ROSS `lib/ipcfg.tcl`，native_log 必须是该 batch 当前实际日志，不能绑定其他会话日志。入口拒绝已有打开项目，不改用户 GUI 工程或厂商原件。

启用 profile 时，在上述参数后追加 proof/review 两个绝对 JSON 路径及固定 review_sha256；三项一起提供且实际字节全部匹配才允许将构建参数置 1。独立运行检查器对应参数为 `--visibility-proof`、`--review`、`--review-sha256`。脚本运行 IPI 配置、强制 BD validate、接口/直接 HP/物理端口读回、输出产品和不含位流 XSA，不运行综合、实现或硬件操作。每项 IP 使用 ROSS capture 和实际参数读回，失败原件保留，重跑另建 RunId；不能清除尝试账本以绕过技能限制。

后续综合/实现由总控独立安排，须保存实际完整闭包和源码哈希、50 MHz 时钟/复位约束、资源/时序结果、bit/XSA/PS 初始化匹配版本及真实 G3 结果。不能用旧 PS-only XSA、1 MiB smoke 或完整失败证据包装检查代替全模型验收。

## CONV batch校验派生

继承几何、坐标和固定tiny416 ROUTE政策；CONV仅模块改名并从两个128-bit元素数乘积删除batch因子。原首个校验分支仍拒绝input/output batch非1，错误优先不变。input元素数只用于其后的长度校验；output元素数另用于OUTPUT_SCAN，但该状态仅能从batch均为1的校验成功轨迹到达。输入端口在运行中变化不改锁存字段，abort/reset返回原状态。因此CONV公开API全域的状态、请求、结果与每周期行为等价；这不扩展ROUTE通用多组覆盖。原14源码原字节保留；生产18闭包为6原2A、8派生及4outer。

## CONV patch范围校验派生

S5 保留S4的两个batch乘子删除，并将patch容量比较替换为同周期窄位宽判据。原首分支保证输入通道C、核KH/KW非零且精确乘积R不超过4608，因此三者均不超过4608；原BAD_LENGTH仍在patch范围BAD_RANGE之前。未通过前置条件时，窄判据不改变首分支错误及layer索引覆盖规则。

每轴D=min(O,8)-1属于0至7。用19位精确计算D×stride低16位+kernel低13位；D非零且stride高16位非零、结果高3位非零或低16位超过51200时标记轴越界。D为0时任意UINT32非零stride均不影响patch，不额外拒绝。轴未越界时，32位P=H低16位×W低16位精确；P高16位非零必越界。否则29位Q=P低16位×C低13位精确，Q超过51200必越界。所有中间值均显式扩展宽度；每个截断都保留独立溢出拒绝条件。在前置条件成立时，该判据与原128位H×W×C>51200严格等价，覆盖通用公开CONV参数域。

原权重组容量判据min(OC,8)×R>36864由R≤4608蕴含永远为假，因此只删除该乘积和判据。输入、输出及权重长度、地址端点、MQ容量、shape、错误优先、全部状态与请求、owner、abort/reset和结果保持原逻辑；不增加寄存器、状态、周期或时序例外。S5版本0.1.5须重新完成独立G2及综合/STA，旧版本通过记录不能继承。

## CONV reduction与长度校验派生

S6依据S5已提交基线`5cb092dcce3631f310e67228738a674a6a82ce41`的真实50MHz综合失败路径，化简首分支R=C×KH×KW及其后的三个长度乘积。首分支仍逐项拒绝所有零因子；layer越界或weight_layer不一致仍把本分支错误覆盖为BAD_RANGE，其他首分支错误仍为BAD_ARGUMENT。对正C、KH、KW，R≤4608等价于各因子≤4608、C×KH≤4608且(C×KH)×KW≤4608。先用13×13的26位精确乘积P，再用P低13位与KW低13位的26位精确乘积Q；任一原32位因子>4608、P>4608或Q>4608均拒绝。P已越界时Q的截断结果不参与成功路径，因此不存在低位别名放行。R锁存仍只在原ST_VALIDATE成功分支赋值，此时Q=原R；保留原变量名及128位零扩展，使两个always_ff全文保持不变。

在首分支通过后，输入/输出长度各有三个正UINT32因子A、B、C。P=A×B用64位精确计算；P高32位非零时P×C必超过UINT32。P≤UINT32时，Q=P低32位×C用64位精确计算；Q高32位非零等价于最终长度超UINT32，否则Q低32位即原长度。长度分支同时检查P和Q高位及原低32位长度一致性。成功路径的output_elements_wide仍是原完整值，后续OUTPUT_SCAN消费它时保持等价；非法描述符不会进入该状态。所有零因子已由更早首分支拒绝，不能将本证明套用到零因子而改变错误优先。

权重长度只在R≤4608后消费，因此OC32×R13只需45位精确结果；高13位非零等价于原权重乘积>UINT32，低32位保持原长度判断。未将MQ的OC限制提前，故长度错误仍优先于地址、MQ及patch范围错误。地址端点、shape交叉乘法、S5 patch判据、请求和结果接口、全部时序状态、owner、abort/reset与周期均未改动；不增加时序例外。S6版本0.1.6需新的独立G2与综合/STA，S5失败或旧通过均不能继承为S6时序通过。

## S7 ROUTE地址守卫等价化简

0.1.7相对S6只缩短两个ROUTE组合地址算式并删除冗余地址末项校验。query保持全部参数、坐标、组、完整源shape/长度和对象端点检查；成功路径中选中通道小于源通道数且坐标在shape内，因此offset小于shape、不大于长度减一；base+length不超过2^32又保证base+offset不超过UINT32。两条末项地址判据由前置条件蕴含，非法输入仍按BAD_ARGUMENT优先于BAD_RANGE返回且所有结果字段为零。source_count=1继续忽略source1，S6的groups>=3拒绝域保持。

engine保留原65位output_elements_work及output_end_work、VALIDATE前两分支；query成功且shape相符时，输出元素数不超过两个源有效shape之和，严格小于2^33，因此原65位乘积在被消费路径精确；长度和端点校验通过后，合法query坐标蕴含offset小于输出长度且输出地址不超过UINT32。时序块唯一差异为删除已证明恒假的四行地址分支；其余寄存器、FSM、请求响应、结果保持、owner、abort和reset逻辑逐字不变，不增加周期或时序例外。S7需要独立G2及新的综合/STA，证据包装通过不代表时序关闭或G3。

## S8 MAXPOOL几何地址分段守卫

0.1.8基于S7提交`2257a450239ea19ef4e2ddf7b2833d44020f95e3`和真实50MHz综合失败路径，新增`s2b_maxpool_geometry`精确派生。全部原14文件原字节保留；生产18RTL为6原2A、8派生及4outer。一般kernel/stride/padding接口、9tap、33位输出维度、64位有符号源坐标、BAD_ARGUMENT/BAD_RANGE全部字段清零行为保持。maxpool engine只更换geometry模块引用，所有时序块及输出64/65位偏移链原字节不变，上采样实现不变。

对于有效tap，r=channel×height+source_y严格小于channels×height且小于2^64；channel×height使用64位精确结果。r低32位由33位加法获得，乘积高32位或该加法进位独立保留。正width意味着r高位非零时完整地址必超UINT32；否则q=r低32位×width的64位结果精确。依次检查q高32位、q低32位+source_x的33位进位、逻辑偏移低32位+base的33位进位；任一为真等价于完整非负地址超过UINT32。高位守卫只在实际有效tap消费，不从kernel2未使用第三行或全padding窗口传播，不能增加全shape CHW范围拒绝。合法地址保持原低32位，任一实际tap越界仍清零全部公开字段。

组合整数证明和RTL差分仅验证功能与每周期控制等价。S8需独立G2和新的综合/STA；旧S7失败记录、50MHz目标、100黄金样本及1000次实板标准保留，本轮未执行STA或G3。

## S9：CONV输出地址的组合因式分解

保留原C/Y/X加法赋值的32位截断，将原输出偏移 `(C×H+Y)×W+X` 改写为 `C×(H×W)+Y×W+X`。H×W使用精确64位结果；channel项、row项及全部加法在原unsigned64模域内计算，base加offset仍保留原64位回绕。该恒等式适用于通用32位输入域，不把冻结descriptor的H/W上界引入端口拒绝条件。未增加33/65位进位拒绝、寄存器、状态或流水；全部公开端口、always_ff后缀、地址范围比较、错误优先和owner语义保持。

S9的组合全域诊断与公开START可达回归分别记录。S8真实综合STA仍FAIL（WNS−6.749ns/TNS−2135.540ns）；本轮功能回归不证明50MHz闭合。H/W→plane→channel可能成为新的关键路径，必须由后续实际综合/STA判断；100黄金样本及1000次实板标准不变。

## S10：CONV feature地址组合因式分解

原signed64坐标生成及bounds比较保持；在bounds内0≤Y<H≤UINT32严格蕴含Y高32位为零。仅此消费分支将原嵌套offset改为C×(H×W)+Y×W+X，plane使用精确64位，channel和base加法仍原unsigned64回绕，row使用零扩展Y低32×W的精确64结果。新三个组合信号完整默认零；未bounds的offset/address仍零。扫描结束→padding→range→read优先、所有端口/FSM/always_ff/owner/错误语义及逐周期请求保持，输出侧S9坐标截断不变。

S9实际综合WNS−4.527ns/TNS−1840.705ns仍FAIL。S10功能G1、独立G2、真实STA与G3分别判断；本组合结构不声明时序改善或50MHz闭合，不增加流水或33/65位拒绝。100黄金样本、109正式样本及1000次实板指标不变。
