# 阶段2B PS/PL物理接口候选

状态：`CANDIDATE_NOT_FROZEN`。候选编号 `S2B-PHYSICAL-20261009`，版本 `s2b-physical-candidate/0.1.0`。源码分析基线 `3f6e327a0ff9adc04ed6c98c1578862b8c2fae64`；本轮只设计、计算和独立审阅，不生成RTL/BD/XSA、运行测试或操作实物。已批准部分仅为《系统设计》中的 `s2b-axi-recovery-principles/1.0.0`。本文给出该原则的编码与实现候选，不能作为完整2B G0、物理接口冻结或实板通过依据。

## 1. 上游与实施边界

保持 S2A-T01 的逻辑CSR、32-bit单word memory、模型、量化、检测头、PS D9与2A内部timeout周期语义。外层包裹现有 `s2a_stage2a_core_ooc`，内部模块源码不改；GP0的物理状态不是内部CSR STATUS的别名。2A内部清owner后，外层仍可拥有和隔离DDR；软件只信任外层状态。

单CPU0裸机、单驱动、无中断重入/并发提交；CPU1停核，PS DMA/其他PL master/其他调试writer不得访问任务区域。门禁只能拦截控制入口，不能禁止CPU绕过驱动读写DDR。驱动必须遵守所有权，无法用MMIO门禁宣称硬件内存访问保护。

拓扑候选：CPU→PS `M_AXI_GP0`→受控AXI协议转换→32-bit AXI4-Lite控制前端；计算core→自定义word adapter→PS `S_AXI_HP0`→DDR。HP0端直接实现AXI3（包含WID、4-bit LEN、2-bit LOCK），数据64 bit；不把HP0称为AXI4。若后续改AXI4 master，必须另冻结转换配置和排空边界。GP0原生AXI3→Lite的转换器属于完整待审路径，不能省略其reset及响应状态验证。

FCLK0、GP0 ACLK、HP0 ACLK和候选PL逻辑同域，先以50 MHz为工程目标，受控reset同步释放；这是候选约束，不是实测频率或时序收敛。避免2A未计入的CDC假设；正式时钟/XDC和实现资源仍需验证。运行中不得只复位计算之外的adapter/互连/HP通路来清计数。

## 2. 数据布局、地址平移与白名单

`mem_addr`是32-bit字节地址且4-byte对齐；word的4个lane是相邻字节。不是每INT8占一个32-bit word。`s2a_conv_tile_engine.sv`按 `base+((c*H+y)*W+x)`访问特征，按GF8权重偏移+`oc*K+k`访问权重；请求地址向下4-byte对齐，one-hot strobe选择实际INT8，输出也以one-hot WSTRB写入。因此连续INT8已经由上游冻结，不能扩成四倍存储或把内存请求数当作有效数据字节数。

全部逻辑对象统一 `physical_byte = 0x10000000 + logical_byte`，使用33-bit加法检查溢出；基址固定、不可由软件重定位。输入/权重/逐层张量保留逻辑地址，PS配置内层仍用逻辑地址。候选专属DDR窗口 `[0x10000000,0x12000000)`（32 MiB），输入和特征空洞保留不用，不能仅凭落入窗口就准许请求。

| 对象 | 逻辑半开区间/有效字节数 | 物理半开区间 | PL访问 |
|---|---|---|---|
| 输入RGB CHW INT8 | `[0x00000000,0x0007EC00)` / 519,168 | `[0x10000000,0x1007EC00)` | 只读 |
| GFINT8W1完整参数包 | `[0x00100000,0x006A12FC)` / 5,903,100 | `[0x10100000,0x106A12FC)` | 只读 |
| feature外包络 | `[0x01000000,0x01ADADB8)` / 11,382,200跨度 | `[0x11000000,0x11ADADB8)` | 逐张量读写白名单 |
| head13，来源layer29、YOLO layer30别名 | `[0x01A46100,0x01A474CE)` / 5,070 | `[0x11A46100,0x11A474CE)` | 属于layer29张量 |
| head26，来源layer36、YOLO layer37别名 | `[0x01AD5E80,0x01ADADB8)` / 20,280 | `[0x11AD5E80,0x11ADADB8)` | 属于layer36张量 |

逐层形状、地址、长度、GF8 record/scale/bias/权重偏移唯一来源是冻结manifest；尺寸计算结果逐项列在 `report/evidence/S2B-T07/physical_contract_20261009_r01/layout_result.json`。21卷积层权重按OIHW的K连续INT8，GF8中有包头、记录和float32 scale/bias；不能只取约5.8 MB权重数组代替整个5,903,100-byte包。当前core的定点bias/requant参数由 `s2a_network_descriptor_pkg.sv` 的通道bias、M/Q及route参数常量固定，本轮不引入PL解析float32或更换参数语义。

feature共有36个独立存储区间，2个YOLO视图不另分配。白名单必须按这些区间检查，64-byte对齐间隙不允许访问。先检查方向、对齐、非零且不冲突的strobe，再逐选中lane检查：读落在同一输入/参数包/独立张量，写落在同一独立张量。跨两个相邻对象也拒绝；输入/参数包写拒绝。无效请求返回2A的BAD_ARGUMENT/BAD_RANGE，物理AXI VALID从未发出，因而没有副作用。白名单是冻结对象级，未新增逐层生产者状态或压缩复用。

PS linker候选只声明应用 `[0x00100000,0x01100000)`和专属 `s2b_tensor_ddr=[0x10000000,0x12000000)`；中间及其他DDR不由程序分配。专属区一个NOLOAD section/arena占据完整32 MiB，linker断言VMA/LMA、size和64-byte对齐；不能让heap/stack/BSS/下载segment重叠。加载器只装载白名单对象，填充不得覆盖窗口外或原应用。有效对象约17.8 MB，原样地址空洞使窗口跨度约26.86 MiB；32 MiB不是新增模型长度。正式ELF/map、程序头、BSP DDR范围与XSA须再次核验；现有1MiB smoke证明不能继承到此窗口。

## 3. GP0控制寄存器候选

固定64 KiB解码窗口 `[0x43C00000,0x43C10000)`，落在GP0 PL地址段。所有定义字段32-bit little-endian、4-byte对齐。前端必须解码完整地址，不能仅截低8/16位形成别名。未对齐/保留地址/非法访问方向返回DECERR、无副作用；写要求WSTRB=`1111`，其他mask返回SLVERR、无副作用。读保留bit返回0；写非零保留bit返回SLVERR。前端不接受AXI burst，GP0转换路径必须将合法CPU寄存器访问变成single Lite transaction。

| 偏移 | 名称 | 访问/字段 |
|---:|---|---|
| `0x000` | ID | RO `0x53324250` |
| `0x004` | ABI_VERSION | RO `0x00000100`（候选编码，尚未发布ABI） |
| `0x008` | COMMAND | WO W1P bit0 START、bit1 ABORT、bit2 ACK_TERMINAL；同写多个bit拒绝 |
| `0x00C` | PHYS_STATUS | RO bits[2:0]状态：0 IDLE_PS、1 ARMING、2 RUN、3 RECOVERING、4 DONE_SAFE、5 ERROR_SAFE、6 FAULT_ISOLATED；bit8 PHYS_OWNER_PL、9 HEAD_VALID、10 SAFE_TO_REUSE、11 TERMINAL、12 AXI_PENDING；其余0 |
| `0x010` | ERROR_CODE | RO 外层首错：0 NONE、1..7保留2A码、8 ABORTED、9 AXI_SLVERR、10 AXI_DECERR、11 AXI_PROTOCOL、12 DRAIN_TIMEOUT；AXI/排空错误不等于零副作用 |
| `0x014` | FRAME_ID | RW，仅IDLE_PS配置；接受命令后锁存 |
| `0x018/0x01C` | INPUT_ADDR/INPUT_BYTES | RW IDLE_PS，逻辑地址0 / 519,168 |
| `0x020/0x024` | WEIGHT_ADDR/WEIGHT_BYTES | RW IDLE_PS，逻辑地址`0x00100000` / 5,903,100 |
| `0x028` | CORE_TIMEOUT_CYCLES | RW IDLE_PS，1..`0xFFFFFFFF`，对应2A原周期定义 |
| `0x02C` | DRAIN_TIMEOUT_CYCLES | RW IDLE_PS，1..`0xFFFFFFFF`；进入RECOVERING后的观察期限，超限进入FAULT_ISOLATED但继续排空 |
| `0x030/0x034` | DDR_BASE/DDR_WINDOW_BYTES | RO `0x10000000` / `0x02000000` |
| `0x038/0x03C` | FEATURE_BASE/FEATURE_LIMIT | RO 逻辑`0x01000000` / `0x01ADADB8` |
| `0x040/0x044` | HEAD13_ADDR/HEAD13_BYTES | RO 逻辑`0x01A46100` / 5,070 |
| `0x048/0x04C` | HEAD26_ADDR/HEAD26_BYTES | RO 逻辑`0x01AD5E80` / 20,280 |
| `0x050/0x054` | EPOCH_LO/EPOCH_HI | RO，64-bit当前命令epoch |
| `0x058` | RESULT_FRAME_ID | RO，终态对应锁存帧号 |
| `0x05C/0x060` | ACK_EPOCH_LO/ACK_EPOCH_HI | RW，仅安全终态；ACK时与当前epoch比较 |
| `0x064` | LAST_REJECT | RO：0 NONE、1 BUSY、2 NEED_ACK、3 NOT_SAFE、4 ACK_MISMATCH、5 BAD_ENCODING、6 EPOCH_EXHAUSTED；合法命令执行时清零 |
| `0x068` | AXI_PROGRESS | RO bit0 AR_DECLARED、1 AR_ACCEPTED、2 R_PENDING、3 AW_DECLARED、4 AW_ACCEPTED、5 W_DECLARED、6 W_ACCEPTED、7 B_PENDING、8 LOGICAL_RESPONSE_PENDING |
| `0x06C/0x070` | FAULT_LOGICAL_ADDR/FAULT_PHYSICAL_ADDR | RO 首故障地址；无地址关联时为0 |
| `0x074` | FAULT_DETAIL | RO bit[1:0]首AXI响应、bit2写、bit3发生排空超限、bit4协议故障；其余0 |
| `0x100..0x13C` | CORE_CSR_DEBUG | RO映射2A原偏移`0x00..0x3C`读值；原WO字段读0；禁止PS通过此窗口直接写start/reset/ACK或配置 |

COMMAND写在外层完成命令准入、参数快照/拒绝决定后才回B；B必须一直VALID至READY且数据/响应稳定。B OKAY只表示命令已接受，不表示推理成功。被拒绝命令返回SLVERR并更新LAST_REJECT；既有任务frame/epoch/所有权/首错/终态保持不变。LAST_REJECT是独立诊断，不覆盖运行故障。状态不允许时的配置写也SLVERR，不修改快照；终态ACK的两个shadow epoch写例外。ACK_LO/HI不是活跃epoch，只有ACK命令采样二者。

Lite AW与W分别锁存，最多一对尚未提交写，不能等两VALID同时出现；每个通道READY取决于自己的槽位。只在AW/W均捕获后执行一次副作用，B完成前不接受下一写。AR/R独立一个读槽位；RVALID/RDATA/RRESP保持至RREADY。不因B/R backpressure重复start。

外层RO/RW读值在AR握手沿从同一份外层next-state快照锁存；next-state先处理已有AXI响应/终态事件，再处理本沿可commit的控制写，最后译码读。该沿START/参数写commit后的读必须见其新值；ACK等待内层握手时尚未commit，读仍见旧安全终态；在ACK真正commit沿读见IDLE_PS。软件必须先收到对应写B，再执行DSB和顺序MMIO读，才能依赖read-after-command；提前发出的AR读到的旧快照不追改，R stall期间保持原值。CORE_CSR_DEBUG经内部CSR sequencer仲裁，配置/ACK序列进行中不接受debug AR；被接受的debug读在内层CSR读握手时采样，R返回仅供诊断，不能代替外层所有权。普通外层读不占内层CSR通路。

不同AR不自动组成原子寄存器组。安全终态的epoch/frame/首错/head-valid在匹配ACK前保持；单驱动以PHYS_STATUS→EPOCH_HI/LO/HI→RESULT_FRAME_ID/ERROR_CODE→PHYS_STATUS复核，要求前后同一安全终态、epoch高位一致、本次提交epoch/frame匹配，才消费结果。运行态AXI_PROGRESS仅为每次读的诊断快照。64-bit epoch软件读HI→LO→HI，HI不同重读；同一有效任务内epoch不变。

## 4. 一次任务、逻辑CSR桥接与终态

冷统一初始化后IDLE_PS，epoch=0，PHYS_OWNER_PL=0，SAFE_TO_REUSE=1，HEAD_VALID=0。只有IDLE_PS接受START；每次接受的START先取得新epoch（1开始、64-bit单调递增，不回绕），锁存全部参数/frame。epoch耗尽拒绝新START且报告EPOCH_EXHAUSTED，需另行冷恢复，不能用soft_reset回绕。FRAME_ID任意32-bit，可重复；epoch用于内部事务归属，frame原样回传。

在准入沿检查输入/权重固定地址、精确长度、两个非零timeout、窗口常量及本次实现的模型/白名单绑定。错误优先级候选：错误地址BAD_RANGE→错误长度BAD_LENGTH→零timeout BAD_ARGUMENT。错误START发布ERROR_SAFE、HEAD_VALID=0、epoch/frame快照，不取得buffer，保留到匹配ACK；这是外层验证，不伪称修改2A规则。遇到busy、ARMING、RECOVERING、FAULT的START拒绝；安全终态尚未ACK的START拒绝并保持终态。

合法START进入ARMING并立即取得物理所有权，外层保持PHYS_OWNER_PL=1。CSR sequencer按原CSR ready握手各写一次FRAME_ID、固定逻辑地址/长度、TIMEOUT，然后写原CMD.start；2A真实start接受沿后进入RUN。ARMING期间还无memory AXI声明；ABORT可取消尚未提交的CSR序列并发原soft_reset，进入恢复。内层busy超时从真实内层start沿计数，不从外层AXI AW/W计数；ARMING必须有固定有界实现步数，候选≤16个PL周期，超限以INTERNAL失败。ARMING过程不允许CPU更新本次命令。

RUN的内部完成/错误/owner清零不直接发布物理终态。成功只有内层done且全部memory响应已送达、adapter无已声明/接受/待响应事务、可见性条件满足时，发布DONE_SAFE，HEAD_VALID=1、RESULT_FRAME_ID=快照、PHYS_OWNER_PL=0、SAFE_TO_REUSE=1。内部错误/超时或外层ABORT/AXI错误立即使HEAD_VALID=0、停止新逻辑请求和计算，保留首错进入RECOVERING；用原soft_reset中止计算，不清adapter状态。即使内层done同沿外层ABORT，外层ABORT优先，输出无效。其余完成与原timeout同沿保持2A完成优先规则。

RECOVERING只完成已声明AXI事务，不启动新的逻辑请求或尚未声明的剩余子读。已取得读数据/待交付逻辑response仅丢弃，不送core。达到安全排空条件后发布ERROR_SAFE并归还buffer，首错及失败epoch/frame保持。排空超限记FAULT_DETAIL.bit3并进入FAULT_ISOLATED，仍接收响应且保持ownerPL/safe0。诊断保留第一次错误与是否超限，ERROR_CODE仅在无更早错误时为DRAIN_TIMEOUT。

排空期限只限制观察时间，不能证明事务永远不能结束。FAULT_ISOLATED内继续保留并消费完整账本；若后来全部已声明旧事务合法完成、计算已停止、无未解决协议故障且第6节可见性条件完整，则转ERROR_SAFE并归还buffer，保留原失败/超限诊断及epoch到匹配ACK。任务绝不改判成功、HEAD_VALID始终0，超限诊断不因晚完成清除。若异常ID/LAST使账本不能合法闭合，仍持续隔离。总控依据《系统设计》已批准原则“安全归还条件满足后归还”“事务始终未结束保持隔离”选择该实现编码；旧草稿新增的已排空仍永久锁死限制不采用，不把合法晚排空误称为无排空运行中恢复。

ACK_TERMINAL仅在DONE_SAFE/ERROR_SAFE、SAFE_TO_REUSE=1、ACK_EPOCH等于终态epoch时执行：发送内层相应ACK（done bit0/error bit1；内层已soft_reset则无状态可清），确认后清外层终态/HEAD_VALID/首错，回IDLE_PS；所有权已安全归还，ACK只是终态确认。ACK桥接期间锁住START和配置，B等内层握手后返回。非匹配ACK、ACK在运行/恢复/fault、重复ACK都拒绝，无状态改变。ABORT在IDLE_PS或安全终态拒绝，不能替代ACK；恢复/fault中ABORT拒绝并保持事务。

## 5. HP0事务映射、取消和排空

adapter独立保存一个逻辑请求的epoch、方向、地址、data、strobe、子读cursor及AXI通道状态。在读取稳定mem_valid请求并通过白名单后锁存；此时不给mem_ready。一次只允许一个AXI事务outstanding，固定ARID=AWID=WID=0，AXI3 RID/BID必须匹配0；不将epoch塞入ID或假定HP保存epoch。epoch记在本地ledger。

AXI字段候选：AxLEN=0、AxBURST=INCR、AxLOCK=00、AxCACHE=0000、AxPROT=000（安全、非特权、数据），无exclusive；HP只访问DDR不混OCM。AR/AW地址是物理字节地址。64-bit端口上，rstrb=1111且4-byte范围全部合法的读可用ARSIZE=2；其他非零mask按lane0..3给每个选中字节一次ARSIZE=0单beat。读请求没有RSTRB，不能用全word读的方式偷偷读取head13尾外两个字节或对象空隙。size2读从RDATA按地址bit2取32bit；size0读从RDATA按地址bits[2:0]取byte并放回原逻辑lane。disabled逻辑lane保持0，多个子读汇聚后只产生一次逻辑mem_ready。

写用AWSIZE=2、物理地址4-byte对齐、WDATA=`zero_extend(mem_wdata) << (addr[2]*32)`，WSTRB=`zero_extend(mem_wstrb) << (addr[2]*4)`，WLAST=1。选中的write byte合法且disabled lane没有副作用；head13末word允许0011或one-hot。无读改写，避免触碰PS/其他逻辑字节。64-bit窄传输在UG585列为支持但低效，保留后续吞吐测量项。

AR/AW/W声明是相应VALID第一次置1，且从此直到各自READY握手都保持VALID和全部payload不变；不能因cancel、timeout或owner逻辑清零撤回。AW/W独立完成，二者VALID不等待对方READY，分别记录accepted。即使AW已接受/W未接受、W已接受/AW未接受或两者都仅声明，恢复时仍继续完成缺失通道并等B；不能强迫B在AW或W任一完成后立即出现。RREADY/BREADY在恢复及fault保持可消费（单笔存储槽始终足够），响应消费一次；B必须在对应AW/W接受后，R要求RID正确、RLAST=1，否则协议故障隔离。对异常ID/LAST保留ledger，不能凭异常响应清掉正等待的事务。

正常R/B的OKAY只在当前epoch仍RUN、原mem_valid仍对应锁存请求时产生一次mem_ready及对应数据/error；读子任务全部完成后才交付。SLVERR/DECERR转为内层INTERNAL，同时外层分别保留9/10诊断并进入恢复，HEAD_INVALID。错误B/R并不证明DDR无写入/读副作用；已接受写可已修改部分目标，失败输出禁止解码。旧epoch响应/取消后的当前epoch响应只消费丢弃，不产生mem_ready、done或HEAD_VALID；必须在新任务之前完全排空，所以无需依赖ID回绕识别旧响应。

声明前取消的请求可丢弃；刚好取消沿之前/同沿已经声明VALID的事务属于必须排空集合，同沿AW/W/AR握手也必须入账。实现用时序明确的next-state账本，不以当前busy判断握手不存在。取消优先禁止声明新VALID，但不能屏蔽已有VALID handshake。reset/cancel不清adapter pending、地址或epoch。只有无声明/无accepted/无等待B/R/无待交付逻辑响应才满足账本为空，计数0不能代替这些逐通道状态。

## 6. 可见性与PS缓存条件

物理SAFE必须同时满足：计算停止或正常完成、账本为空、所有AXI3写B/读R已消费、属性整条路径保持非Bufferable、HP/DDR可见性依据与具体实现绑定。采用AxCACHE=0000，禁用早返回或改变属性的桥接配置；GP0读STATUS不能作为HP0写屏障。UG585的HP性能章节说明写请求到DDR/OCM slave且响应由该slave返回，以及收到B后发起事务的slave提交顺序。Arm IHI0022C的AXI3缓存属性/响应规则需核对§5.1；§13.8.1属于AXI4章节，只能说明对应非Bufferable语义，不能单独冒充AXI3证明。以上是安全归还的条件论证，不声称数据已到DRAM引脚或断电持久化。完整网表/属性/HP配置核对和CPU跨master cache维护后的真实读回仍未执行，缺一项则不能发布已验证SAFE结论；PG293不是HP可见性依据。

PS启用DCache，任务arena与应用不共享32-byte缓存行，所有arena维护范围64-byte对齐。启动前：CPU写input/完整GF8及必要feature初始化→DSB SY→对input/GF8向外64-byte取整执行实际BSP `Xil_DCacheFlushRange`→DSB；对整个feature外包络向外64-byte取整执行FlushRange再InvalidateRange→DSB，消除旧脏输出cache line。维护覆盖的padding在专属arena内，但不是PL对象白名单。之后写MMIO参数、DSB、START，再DSB；RUN/ARMING/RECOVERING/FAULT禁止CPU访问arena，不做cache维护，也不从旧head解码。

观察安全终态后DSB→对向外64-byte取整的feature范围InvalidateRange→DSB，再在DONE_SAFE且HEAD_VALID=1时读两头。失败也invalidate整个feature包络后才重用，不flush旧输出cache，防止覆盖PL已写数据；整包络的两端和维护长度预先对齐，避免BSP未对齐InvalidateRange先flush边界脏行的行为。PS读取头时额外验证epoch/frame和两个精确长度；ACK前软件完成结果拷贝/处置。input/GF8启动后不写、不读；下个任务开始前PS安全拥有时才可改。

本地官方BSP `D:\Xilinx\2026.1\data\embeddedsw\lib\bsp\standalone_v9_5\src\arm\cortexa9\xil_cache.c`已只读确认32-byte行、L1/L2维护与DSB/L2Sync，USE_AMP会跳过部分L2代码，候选拒绝USE_AMP。`xil_mmu.c`的Tlb设置以1MiB section作用，MMIO所在`[0x43C00000,0x43D00000)`需Device/Strongly-ordered适用属性，程序不在该section分配数据；DDR保持一个cacheable映射，禁止同一物理arena的不同属性alias。实际BSP版本、MMUTable、生成xparameters/SDT及编译宏须绑定新应用，而不是照搬上述文件路径即声称完成。

FAULT未闭合时持续隔离：若事务始终未结束或状态不能证明，只有单独授权且已核实旧事务生命周期终结的全体系冷恢复可以重新准入，包括旧软件停止、CPU1/其他writer静止、PS/DDR/互连/PL统一初始化、arena重新初始化与cache无旧副本、诊断证据保留、新epoch域与旧执行不混用。单独PL reset、驱动重启、写ACK、计数清零都不满足。已合法晚排空按第4节转ERROR_SAFE并保持失败；不省略协议故障/可见性证明。

## 7. adapter与AXI DMA比较、资源和验收

| 候选 | 与当前接口关系 | 取舍/后续条件 |
|---|---|---|
| 自定义HP AXI3 word adapter（本候选） | 保留2A随机字节地址、one-hot/sparse strobe和single outstanding；PL master自己发地址和搬运数据 | 最小语义跨度，明确承担DMA意义的数据搬运/完成/长度/恢复责任；不等于AMD AXI DMA IP |
| AMD AXI DMA（PG021） | AXI4 memory与AXI4-Stream的MM2S/S2MM；当前core没有AXI-Stream数据接口或帧TLAST | 直接接入不匹配，需stream桥、缓冲及地址调度/权重重排，不能把随机请求当连续stream；可能改善后续burst性能但扩大实现和验证范围 |

阶段计划“验证DMA、缓存一致性、缓冲所有权及传输长度”仍全部有效。若采用本候选，验收中的DMA由PL自主DDR搬运模块承担，须验证请求字节数/有效lane长度/错误/取消/完成/cache/连续任务；不能以“没装AXI DMA IP”标记NOT_APPLICABLE或减少100样本/1000连续任务。是否将正式计划中DMA专指特定IP，应在G0记录解释后再冻结，本文不改正式计划。

现有2A OOC资源40,550 LUT / 53,200、3,082 FF / 106,400、32 BRAM / 140、186 DSP / 220，余量12,650 LUT、103,318 FF、108 BRAM、34 DSP。来自当前8×8/8lane冻结综合，不混历史串行计数；GP0转换、adapter、复位和时钟结构尚未集成，未证明布局布线余量。无冻结XDC/时钟及时序收敛，50 MHz也不能先承诺可达。

运行速度风险高：tile engine当前逐INT8读写，即使连续数据只占1 byte，一次窄beat仍占64-bit总线通道和往返延迟，single outstanding不能掩盖DDR延迟。T66实际layer0已有2,551,955请求/响应，只是单层、TB延迟，不等于HP实测吞吐或整网周期。本轮计算给出全部独立feature写入的最低请求量与延迟敏感性，未把这些下界当整网预测。每任务还含重复tile读权重/特征、route/pool/upsample读、控制和PS D9/UART；正式连续1000任务的总时长待硬件测量。若性能不足，burst/coalescing/prefetch须重新定义物理可读范围、写完成和abort ledger并回归，不能改冻结2A数值或静默四倍展开。

`s2a_control_csr.sv` 的timeout_cycles和elapsed_cycles均32 bit，零timeout非法；网络descriptor明确global timeout且不逐层重启。最大值`0xFFFFFFFF`在候选50 MHz下仅85.89934590秒，计数不能因DDR stall或恢复而偷偷延长/回绕。当前一次byte往返与重复tile读可能使整网正常完成超过此上限；所以下界估算不足以证明可部署，正常CORE_TIMEOUT和DRAIN_TIMEOUT部署值均为NOT_MEASURED，未填写无依据的默认值。落实前必须量化完整38层逻辑请求数量、实际HP每笔延迟/背压与计算周期，并证明指定范围的正常总周期加余量≤`0xFFFFFFFF`，再设置并记录deadline；如不满足则回G0选择受控加速或关键timeout接口变更，不能以延长软件等待、降低100/1000指标或内部暂停计数绕过。排空timer候选采用32-bit饱和比较，超限不停止接收B/R；其部署观察期限也需量测/上限依据，不宣称有限时间一定排空。

G0未关闭项：本候选独立审查、AXI3属性和实际转换配置、reset/ARMING时序、linker arena与真实DDR/PCB绑定、计数期限的部署值及估算、软件ABI与cache代码、100样本/1000任务计划。必须随后做AW先/W先/独立stall、VALID保持、byte lane与全部strobe、尾部/空隙拒绝、ACK不匹配/重复、终态start拒绝、timeout各通道阶段、错误可能部分写、旧response、观察期超限后合法晚排空转ERROR_SAFE且HEAD无效/诊断不清、异常响应无法闭合仍隔离、永久stall持续隔离和冷恢复等验证，再做完整集成资源/时序及授权的实板传输/黄金比对。此处仅列验证要求，本轮未运行。

地址、字段编码、单核裸机限制与adapter实现选择属于可审阅的工程候选；若保持本范围可由总控按既有授权推进落实，不另造审批门槛。已批准恢复原则覆盖停止→排空→归还、未排空持续隔离，包括期限后确已合法排空且可见性成立时的失败安全归还。改变正常输入/输出语义、正式长度/模型、无排空归还或无法证明旧事务结束就解除FAULT、改正式验收指标等关键语义须Wong决定。最终物理freeze仍需正式批准/审查记录，不能由本文`version`产生。

## 8. 核查依据

本地正式输入：S2A-T01规格及manifest、当前2A core/memory master/tile engine/descriptor/quant参数、阶段验收与PS-only平台资料；实际SHA绑定于本Run manifest。未读外部模型原图/参数包，不复制私密数据、不操作厂商原件。

primary资料核查范围：本Developer实际打开UG585接口/Transaction Types和PG021 Core Overview；Address Map、Performance Optimization Summary及Arm PDF内容由总控提供的既有读取依据继承，下列对应项标明来源，不冒称本Developer重新读取成功。

- [AMD UG585 1.15 PS–PL AXI Interfaces](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/PS-PL-AXI-Interfaces)：原生AXI3接口。
- [AMD UG585 Address Map](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Address-Map?contentId=YyWiRDziY_R5p9ZPDZc1cg)：GP0与CPU/HP共同DDR范围；总控既有读取依据。
- [AMD UG585 Transaction Types](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Transaction-Types?contentId=q9YGCp2PD_HFpH1Xmk9I8g)：64-bit窄传输及32-bit扩展的效率边界。
- [AMD UG585 Performance Optimization Summary](https://docs.amd.com/r/en-US/ug585-zynq-7000-SoC-TRM/Performance-Optimization-Summary?contentId=SQ4F87dw95hi9lj_8vK6QQ)：HP slave响应与提交顺序条件；总控已读取第23行依据。
- [Arm AMBA AXI IHI0022C](https://documentation-service.arm.com/static/64256e84314e245d086bc88f)：总控已读取132页官方PDF；本Developer本次open为Internal Error，未获得PDF内容。§3握手、§9窄传输、§5.1 AXI3属性与§13.8 AXI4扩展须区分。本文不拿AXI4专用规则替代HP AXI3实现证明。
- [AMD PG021 7.1 Core Overview](https://docs.amd.com/r/en-US/pg021_axi_dma/Core-Overview?contentId=_Z2xHyugj8rFONIeaHuSqw)：AXI DMA MM2S/S2MM的memory/stream边界。初次AXI-DMA链接失败，改Overview→Core Overview读取成功。
