# tiny416 当前 RTL 静态请求预算

实际计算时间为2026-10-10（UTC+8）；RunId沿用已分配的`request_budget_20261009_r01`。源码基线`3d424b9cc207e85375ef4f703ee193806c73bd34`。这是正常完成38层任务的静态整数计算，未运行RTL、软件测试、综合、完整仿真或实物；成功路径请求数可精确计算，完成周期仅给严格下界。物理候选`0.1.1`尚未冻结，adapter未实现。

一次完整任务共 **96,135,961** 笔逻辑memory请求：读 **84,753,811**、写 **11,382,150**。读包括特征 **15,021,075** 和权重 **69,732,736**。原模型的独立输出字节数为11,382,150；两个YOLO层是视图，无额外读写。所有正常请求均one-hot INT8，32-bit word地址是4-byte对齐的容器，不能把请求数乘4当有效数据长度。

| 算子 | 特征读 | 权重读 | 写 | 合计 |
|---|---:|---:|---:|---:|
| convolutional | 7,969,043 | 69,732,736 | 6,147,206 | 83,848,985 |
| maxpool | 2,422,784 | 0 | 605,696 | 3,028,480 |
| route | 4,542,720 | 0 | 4,542,720 | 9,085,440 |
| upsample | 86,528 | 0 | 86,528 | 173,056 |
| yolo | 0 | 0 | 0 | 0 |

## 计算依据与复用边界

真实顶层路径为`stage2a_core_ooc → runtime_shell/memory_master → network_backend → conv_tile/maxpool/route/upsample`。旧`conv_layer_scheduler`及逐元素卷积pilot没有用于本次计数。网络backend仅对非卷积逐输出dispatch，卷积一次启动完整层；两个YOLO descriptor作为alias直接推进，不启动memory。

卷积空间tile尺寸8×8，输出通道组最多8路。对每维tile起点`t`、实际输出长度`m=min(8,O-t)`，patch连续长度为`p=(m-1)*stride+kernel`，来源起点为`t*stride-pad_before`；有效长度`v=max(0,min(I,origin+p)-max(0,origin))`。本层特征读为`Cin * sum(vy) * sum(vx)`；padding只写内部feature_patch零值，跳过外部请求。实际patch扫描为`Cin*sum(py)*sum(px)`，两者差为padding扫描数316,793。

`ST_TILE_PREP/ST_FEATURE_SCAN`先读整个patch，再`ST_WEIGHT_PREP`遍历通道组；特征跨通道组复用，tile之间重新加载，包含patch重叠。每个tile、每个实际输出通道都读全部`K=Cin*Kh*Kw`权重，权重读为`ceil(Hout/8)*ceil(Wout/8)*Cout*K`。最后不足8路的组只加载实际通道。权重跨该tile的全部空间点复用，在下个tile重新加载；即使某个tap为padding，该通道的完整K权重仍加载，不以padding减少权重请求。独立权重字节5,877,088，重复tile读使实际权重请求达到69,732,736。

输出写为`Cout*Hout*Wout`，每个INT8一笔one-hot写。bias、M/Q由descriptor ROM常量在`ST_MQ_PREFETCH`取值（`S2A_CONV_BIAS_ACCUMULATOR_INT32/S2A_T23_MQ_ROM`），不通过DDR读取包头、record、float32 scale/bias，也不由PL动态解析GF8。因此这些参数的外部请求数为0。每层GF8 offsets已与冻结manifest逐项比较；整个包仍是5,903,100字节，包与独立权重数组相差26,012字节：28字节包头、21×32字节record、3164×4字节scale及3164×4字节bias。DDR加载/白名单必须保留完整包，不能把本报告的实际权重读范围改写为模型接口长度。

池化三层均2×2/stride2，当前冻结形状的全部四tap有效，每输出四读一写，不跨窗口缓存或合并word。route按source切通道再拼接/定点重定标，每输出一读一写，两个来源的读量按切片长度求和。upsample每输出一读一写，即使四个输出对应同一个来源byte，仍读四次。source、shape、kernel、stride、padding和GF8 offsets取实际descriptor，与冻结manifest及候选layout交叉核对；机器投影保留消费字段和原22MB manifest SHA，不复制完整manifest或读取外部参数原件。

关键源码位置：`s2a_conv_tile_engine.sv`第375、518、519、840、873、909、923、1000、1032、1059、1108行；`s2a_network_backend.sv`第345附近的memory握手和注册response、第430附近的tile实例、第630附近的逐层推进；`s2a_memory_master.sv`第31行起的pending/入队/完成；`s2a_control_csr.sv`第216至253行的busy计数和完成优先。交付包源快照与SHA绑定实际版本，行号辅助定位，实际代码为准。

## 独立手算锚点

1. layer0：208/8=26个tile/维，3×3/stride2/pad1。每维首tile有效16，其余25个有效17（最后tile覆盖399..415），有效跨度和`16+25*17=441`。特征`3*441²=583443`；权重`26²*32*27=584064`；输出`32*208²=1384448`；总`2551955`。与已有layer0 TB记录的2,551,955请求相等，仅作既有旁证，本轮未复跑TB。
2. 104×104输出、3×3/stride1/pad1：首/尾tile各有效9，中间11个各10，每维有效和128、扫描和130。每输入通道读16,384，padding扫描`130²-128²=516`；tile内复用不等于整个输入只读一次。
3. 13×13输出、1×1：每维tile为8+5，四个空间tile，特征每输入通道读169；30个输出通道分8/8/8/6，权重每K读`4*30=120`，不把最后6路补到8路。此锚点可解释layer29边缘和末组计数，实际Cin=512，由descriptor消费。
4. layer36：26×26/1×1，空间tile为8/8/8/2，16个tile。特征`256*26²=173056`，权重`16*30*256=122880`，输出20280，总316216；读取特征不会乘4个输出组。
5. layer9池化：104×104输入、52×52输出、2×2/stride2、Darknet padding参数1给origin0。最后窗口102/103都在界内。特征读`128*52²*4=1384448`、写346112。upsample33则每源byte被重复读取4次，不能只按源大小21632计读。

## 候选HP0事务映射

按现有`0.1.1`候选，所有one-hot读只需一个`ARSIZE=0/ARLEN=0`子读，未使用可选的full-mask size2读路径。因此AR事务/R单beat各84,753,811。one-hot写使用`AWSIZE=2/AWLEN=0`，WSTRB只写一byte，AW事务/W单beat/B响应各11,382,150；无读改写，读写事务合计96,135,961。AW/W通道可独立握手，但single outstanding仍逐逻辑请求完成。

有效读写数据合计96,135,961 byte，64-bit R/W数据通道slot合计769,087,688 byte（每beat8-byte总线槽位），有效lane比例1/8。写声明的size2传输范围4byte/事务、合计45,528,600 byte，其中只有11,382,150 byte被WSTRB选中。slot字节和AxSIZE范围均不表示DRAM实际内部访问字节数或实测带宽；不包含AXI地址/响应、PS参数加载、cache维护、D9/UART等。

## 全局32-bit deadline必要条件

定义`Li`为公开memory请求从第一次`mem_valid=1`到`mem_valid&&mem_ready`握手的服务周期数，包含握手周期，最小1。它包含adapter、HP/DDR服务与背压，不等于独立HP往返延迟。成功路径公开请求区间互不重叠；每请求需要一个入队周期（master尚未pending）和一个network注册response周期（`response_pending`阻止下次入队，算子消费返回），这两个周期不属于公开服务区间。

另有卷积`ST_COMPUTE`至少424,506,368周期：每空间点每输出通道组执行K次，包括padding零tap；`ST_COMPUTE_REQUANT`每实际输出通道每点一周期，共6,147,206；padding扫描316,793周期。四类周期与公开service/入队/注册response不重叠。因此严格非服务下界为：

`Cnonservice >= 2*96135961 + 424506368 + 6147206 + 316793 = 623242289`。

它遗漏额外scan、MQ prefetch、状态切换、compute point prep、逐输出dispatch、启动和最终完成等，不能当精确完成周期。严格必要条件为：

`84753811*平均读服务周期 + 11382150*平均写服务周期 + Cnonservice + 余量 <= 4294967295`。

忽略非服务成本的均值必要上界44.6759698486周期；加入已证明下界后为**38.1930441825周期**，实际允许均值还会更小。若均值39，下界为4,372,544,768周期，已经超过4,294,967,295。候选50MHz只把周期换算为时间：32-bit最大期限85.89934590秒；38.19周期约0.764微秒是逻辑service必要上界，未测、不应设置为实测HP延迟。

| 假设每逻辑请求均匀service周期 | 完成周期下界 | 50MHz时间下界/秒 | 下界已超deadline |
|---:|---:|---:|---|
| 1 | 719,378,250 | 14.387565 | 否 |
| 8 | 1,392,329,977 | 27.84659954 | 否 |
| 16 | 2,161,417,665 | 43.22835330 | 否 |
| 32 | 3,699,593,041 | 73.99186082 | 否 |
| 39 | 4,372,544,768 | 87.45089536 | 是 |
| 48 | 5,237,768,417 | 104.75536834 | 是 |
| 64 | 6,775,943,793 | 135.51887586 | 是 |
| 96 | 9,852,294,545 | 197.04589090 | 是 |

表中全部是假设敏感性，未超下界不证明正常可完成。服务慢到超过上限时，当前请求数可用于证明瓶颈，但不能暂停stall期间的内层计数、逐层重启、延长deadline或降低100样本/1000连续任务指标。即使完全无service背压，1周期行也给每任务至少14.387565秒，仅PL内层的1000任务至少3.99655小时；实际时间含遗漏周期、HP延迟及PS工作会更长，不能当项目正式性能指标或实测预测。

普通部署TIMEOUT与DRAIN_TIMEOUT均保持NOT_MEASURED。必须取得adapter及实际HP合法事务的服务界、精确/有界完整非服务成本、clock/时序证据和余量，再证明指定正常任务范围可满足global deadline。排空观察期限不保证有限排空：永久stall或协议异常继续隔离，事务未结束不安全归还。本报告不冻结物理接口、不宣称G0/G3/G4/G5、实板推理或100/1000验收。

## 复核与证据

在工程根执行`python -B report/evidence/S2B-T08/request_budget_20261009_r01/calculate_budget.py`完成一次真实静态计算，exit0、0.1619528秒。脚本以exclusive create写结果，避免覆盖已有Run产物；复核重算应将整个脚本按原相对布局放入新隔离副本，或只读复核当前结果，不能在本Run直接覆盖重跑。真实日志、机器结果、消费投影、source快照、工具版本与SHA位于同目录manifest。峰值内存、全过程工具调用总量未测。

首次只读`evidence`检查exit0/CHECKS_OK；首次`inputs`实际exit1/CHECKS_FAILED，错误为物理候选frozen=false、部署BLOCKED、实物NOT_RUN。原始两个日志与收据保留；静态计算成功不关闭这些依赖阻断。增补日志/收据后复核最终manifest。包装检查只证明文件绑定，与部署可行性、独立审查或验收分开。
