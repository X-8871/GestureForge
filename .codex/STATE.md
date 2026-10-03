# 项目状态

更新：2026-10-03（UTC+8）。恢复时先读 `AGENTS.md`，再读本文件和当前阶段正式规格。

## 当前目标与阶段

- 目标：AX7020 摄像头五类手势检测，最终经 PL INT8 推理、PS 后处理和 HDMI/板卡交互形成可复现作品。
- 当前阶段：阶段 2A「PL 推理仿真」。阶段一与 G0 已冻结；T02 共享 MAC 单元独立仿真及只读审查通过。Wong 已批准 8×8 空间 tile / 8 output-channel lanes；T66-A byte-lane 修复与观测回归已通过静态检查和独立审查，attempt07 完成编译并已启动 layer0 full golden XSim，结果待定、未集成描述符 backend；G1/G2/G3/G4/G5 均未通过。
- 本轮未重新训练；S2A-T02 仅执行独立 MAC RTL 单元仿真，未执行综合、Vivado 工程集成、整网仿真、板上烧录或板测。
- 归档主入口：`docs/obsidian-project/04-提交材料/阶段验收/阶段1_实施步骤与决策_最终产物_20260922.md`。

## 阶段 3 独立穿插入口

- Wong 已批准执行 AN5642 原始视频链路，实物操作由 Wong 执行；本会话工作树分支 `codex/stage3-video` 基于 `955a2b4`，不改主工作树、不查询或干预 2A/T68 运行。
- 入口 `board/stage3/README.md`：计划与原计划差别、固定官方 AX7020 源 `fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327`、PDF 页码/哈希及候选 CMOS1 引脚；旧 AX7Z020 2017.4 XDC 不直接复用。
- Vivado 2026.1 的 XA/-1I 与 13 项精确 IP 目录检查实测通过，见 `report/stage3_vendor_probe_20261002.json`；不代表 BD、综合、时序、软件编译或板测。接口 G0 尚未冻结，继续核对资料对应及 AN5642 模块版本，当前无需上电接线。
- Wong 已确认 AN5642 到手；指定 Vault 项目的 `01-竞赛材料/板卡正面.jpg`、`板卡反面.jpg` 已实际读取并计算哈希，入口 `board/stage3/hardware_photo_evidence.md`。不再向 Wong 索要板卡照片；沿用阶段0已记版本标记 `AX701020.3.0`，与候选图纸的对应仍内部核对，不伪称电气/板测通过。
- 离线准备及诊断工具已独立审查并提交；下一关为 `board/stage3/prepower_check.md` 的 AN5642 型号/版本、Pin1 和直插/排线方式断电核对，不要求重发板卡照片、不上电/烧录。PCB 电气绑定、双通道最终语义、缓冲/丢帧口径仍待 G0 冻结。
- BD 诊断：原厂 IP 在 XA/-1I 上因 `axi_dynclk` 家族声明拒绝实例化；显式隔离副本只给三个 IP XML 增加 azynq 声明后，16-cell BD 校验实测通过，见 `report/stage3_bd_experiment_20261002.json`。只是元数据实验，不是正式 IP 支持、RTL/时序或板测通过；硬件 G0 继续待实物证据，禁止据此烧录。未修改厂商原件。
- HDL 诊断：`azynq_metadata hdl` 在 `tmp/s3h01` 实测退出 0、生成包装器；证据 `report/stage3_hdl_generation_20261002.json`。随后 `check_syntax -fileset sources_1` 退出 0、语法检查无错误/警告，见 `report/stage3_hdl_syntax_20261002.json`；不代表 elaboration/综合/时序/软件/板测通过。五项 AXI ID 1/6 位宽警告未关闭，下一步先查 ID 连接及厂商软件错误处理/超时/缓存交接。旧 AX7Z020 核心板/底板图不能作为当前 AX7020 电气绑定，不要求重复提供板卡照片。
- PL 恢复：确认原阶段3进程不存在后备份中断产物，仅重跑四个 IP 和顶层；`synth_1` 完成但整体诊断 `FAILED=1`（唯一黑盒 dbg_hub 调试核心，不是退出码），另有 Timing 38-249/NSTD/UCIO/RAM 警告；见 `report/stage3_synth_diag_20261003.json`。没有实现/完整时序/bitstream/板测。AXI ID 静态连接及 5 个检查器用例通过，不代替事务验收。
- 厂商传感器差异补丁已提交 `203ab10`；独立审查及主控复验四组合各 968 cases / 847246 checks，303 项表值一致，见 `report/stage3_sensor_host_20261003.json`。底层接收整体截止时间、真实 BSP/显示集成仍未完成；后续还须验证视频背压/复位、缓冲所有权和帧行像素观测，不能宣称仅剩烧录。
- S3-VAXIS-01 host 回归：launcher 退出码读取失败/缺失时，sentinel 即使为 0 也不再通过；WinPS 5.1 策略自测 5/5，Vivado 2026.1 `xvlog/xelab/xsim` 全部退出 0，12 beats、6 stalled cycles、12 FIFO pops。结果 `report/stage3_vaxis01_host_20261003.json`。同钟 FWFT mock 未覆盖真实 XPM CDC、传感器或硬件；G0/G3/G4/G5 均未通过。

## 阶段 2A G0 冻结入口

- G0 规格：`docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md`；状态 `G0_FROZEN`，主候选 `tiny416`。
- 机器清单：`report/evidence/S2A-T01/tiny416_model_manifest.json`；固定输入：`report/evidence/S2A-T01/fixed_test_samples.json`。模型清单覆盖 38 层、21 个卷积层、5 个 cfg 算子类型及共享 INT8 MAC；固定样本 109 项。
- G0 冻结模型/量化/参考源码哈希、NCHW 张量与地址、PS/PL CSR 和 memory 协议、内部 operator completion event、解码/NMS 规则、随机种子及误差口径。算子与 MAC 定向向量各 16 项，case 9 route 用于非恒等 scale 转换。
- 独立复审通过；G0 规格、生成器、测试、model manifest 和 samples manifest 的最终 SHA-256 均记在 G0 规格内。
- 下一项（2026-10-02）：按 Wong 请求只读检查 `batch109_r3` 进度后确认无活动批处理；sample0 的 RTL 仿真实际完成 38/38 层、0 mismatch、972,865,374 cycles，但 CRLF 摘要被 runner 误拒，coordinator 又因 PATH 多个 `python.exe` 候选在 dispatch 前退出，因此验收仍为 0/109。原失败证据保留且不得覆盖。runner/coordinator 修复及合成测试已独立审查 PASS 并提交 `a1298db`；静态源闭包已于提交 `eb8ce872e79869d2346bc9cb206025b563b64236` 固化；2026-10-02 已隐藏启动新 RunId `batch109_r4`：sample0 runner PID 16800、coordinator PID 14472，summary 预期写入 `report/evidence/S2A-T68/batch109_r4/unattended_continuation_batch109_r4.json`。启动时验收数为 0/109；2026-10-02 13:16（UTC+8）按 Wong 请求对两个启动 PID 及 RunId 相关进程作一次定向只读查询：coordinator PID 14472、sample0 runner PID 16800、Verilator 仿真 PID 18956 正在运行 SampleIndex=0；未见 108 样本批跑或 D9 进程。未读取日志/进度文件，因此当时层级进度和验收计数未知。此后不主动轮询；`batch109_r3` 保留且不重用。此前 `batch109_r1`、`batch109_r2` 均保留且不纳入验收。

## 已冻结的模型和口径

- 类别：`fist`、`palm`、`one`、`two_up`、`three`；旧 32×32 分类方案停用。
- 模型：`tiny320`、`tiny416` 为上板候选，`full608` 为 PC-only 对照。
- 固定推理：`score_threshold=0.25`、NMS IoU=`0.45`、每图最多 15 框。
- 浮点门槛：mAP@0.5≥0.90、mAP@0.5:0.95≥0.70、五类逐类 precision/recall≥0.90。
- INT8 保留门：相对浮点 mAP@0.5 和逐类 recall 下降≤5个百分点，且 D2 溢出规则满足；本轮未把整网 INT8 检测下降写成已通过。
- `no_hand` 不是第六类，也不是阶段一阻断项；官方 `no_gesture` 不改名。没有合适独立来源时只保留为可选诊断。

## 已核对的正式结果

- 官方数据来源为 HaGRID；manifest 158,680 行，SHA-256 `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- tiny416 官方 test 25,484 张：mAP@0.5=`0.9774176565`，mAP@0.5:0.95=`0.7700877728`，最小 precision=`0.9479207151`，最小 recall=`0.9701880752`。
- D3 PC 本体（100 warmup+1000 valid）：tiny320 mean/P99=`17.895892/21.176 ms`；tiny416=`27.456450/31.559 ms`；full608=`43.861036/48.585 ms`；三者 timeout/drop/failure 均为 0。
- Wong 已确认三个模型通过网页/摄像头人工测试；该项是人工可用性确认，不替代正式 mAP。

## 可恢复入口

- 网页代码：`web/index.html`、`web/gestureforge_web.py`、`web/README.md`；模型注册表保留三个独立 ID、cfg/data/weights 路径和 SHA，可切换回滚。
- D2/D3/D6/D9 最终证据和清理后的保留清单见阶段一归档记录；外部模型仍在 `D:\FPGA_Data\HaGRIDv2`，本次未删除。
- 阶段冻结基础提交：`27ff12a`、`b3e82d1`；本次整理完成后以最新清理提交为准。

## 后续边界

- tiny320/tiny416 后续板上门：LUT/FF/BRAM/DSP≤85%，WNS/WHS≥0，TNS/THS=0；full608 不适用板上资源门。
- 未来若要求“无手必须拒绝输出”，需另建独立、可审计数据集和新验收门，不回写当前阶段一冻结结论。
- 阶段2A仍未冻结；2B固定输入推理上板仍依赖2A验收。Wong最新选择并行开启阶段3，暂定目标为摄像头→已核实输入→FPGA→HDMI显示原始画面；正式计划允许3在视频接口核实后独立穿插，不依赖2A/2B推理验收。阶段3先按板卡/PCB版本核对端口方向、器件、引脚、电平和摄像头兼容性；分辨率/像素格式/帧率及丢帧策略在G0明确，按原计划至少30分钟无死锁并留计数、日志和视频。本目标不等于已授权烧录/实物操作或已完成验收；不自动引入CNN/检测框。

## 阶段 2A 最新恢复点

- 当前批次最新记录（用户请求状态核查，2026-10-02，UTC+8）：`manual_20261002_140325` 最终协调报告现为 `COORDINATOR_ERROR`，报 Cannot bind argument to parameter Text because it is an empty string；sample0终态 `PASS_SAMPLE0_TERMINAL`、simulation/runner exit0。batch字段保留 `RUNNING_EXISTING_SCHEDULER`，但 `batch_dispatch/batch_summary.json` 不存在、D9为null；本轮未查询进程，不能从该字段断言scheduler当前仍在跑或已停。必须诊断协调器并核对既有scheduler再恢复，禁止盲重跑或覆盖证据；不改变用户要求不主动监控的边界。2A/G4/G5未通过。

- 更新：2026-10-02（UTC+8）。恢复审计：`report/stage2a_execution_audit_20261001.md`，提交 `f7c5830f37f749a71fcb9639f1be58e1ca412c13`；该报告记录当时的病灶、文件哈希与恢复边界。

| T01 项 | 已通过 / 可复用版本 | 缺口 | 下一项验证 |
|---|---|---|---|
| G0 输入与接口 | T01 `G0_FROZEN`，独立审查通过；模型/样本与规则哈希见 T01 规格 | 无；冻结仅定义基线，不证明 RTL | 后续均沿用此基线 |
| 单元向量与协议 | T69 独立只读审计 PASS：T02 MAC、T17 21层卷积、T14 maxpool、T13 upsample、T15 route、T08 YOLO 随机/定向向量覆盖齐；T10–T12/T18–T21 有固定 stall、错误、取消、timeout、ACK/恢复证据；T11 CSR 回归通过非法/保留 CSR 与 BAD_RANGE/BAD_LENGTH/BAD_ARGUMENT start（595 transfers、116 directed、256 random）；T68 protocol_directed05 真实 backend+CSR code6/7→INTERNAL、pending layer0 output write 的 soft/hard reset/timeout 取消、无迟到副作用及 ACK/restart 独立审查 PASS；protocol_directed06 波形版独立复审 PASS，VCD `report/evidence/S2A-T68/protocol_directed06/backend_fault_recovery.vcd`（15,383,328 B，SHA-256 `e08b209e00c467b9571e96f723025fe59930db0721463404a18fe6459b4b1c5f`） | 无（该行通过不代表整网或阶段通过） | T68 sample0 38 层 PL golden 仿真与吞吐校准 |
| CPU oracle 与 D9 | T25 `cpu_layer_golden_index.json` 为109输入×38层整数黄金 `COMPLETE`（提交 `f669103`）；T29 D9 CPU reference 可从冻结 T25 heads 重建，109/109 canonical 比对通过；T68 D9 verifier 已提交 `e55fae0`、独立源码审查 PASS | CPU 链路不代表 PL；实际 PL heads 尚无比较 | 用整网模拟实际 head bytes 与 T29 对照，离散字段一致、score/坐标绝对误差≤1e-6 |
| PL backend 与新卷积 tile | T66 byte-lane 修复与 layer0 tile 回归已静态审查通过；另有独立 Verilator 5.050 sample0 layer0 golden 仿真 8/8 通过，1,384,448 字节、0 mismatch、26,002,719 cycles。证据目录：`report/evidence/S2A-T66/tile01/verilator_run01/` | 尚无 PL 38 层整网 golden；此前 XSim attempt07 按 Wong 指示继续自行运行，本轮未查询、读取或干预 | T67 backend 接入提交 `433b720c1006f34d191e0fd7ed07bee62d6a276c`；静态独立审查 PASS；独立 lint exit=0、143 warnings、0 errors |
| 全网 PL 与头后处理 | harness `e55fae0`、protocol_directed05/06 独立审查 PASS；`batch109_r3` 只读核查发现 sample0 原始 PL RTL 仿真 38 层完成、0 mismatch、972,865,374 cycles，但 runner 因 CRLF 摘要解析误判，coordinator 在后续样本 dispatch 前因 Python 多候选解析退出；验收计数 0/109，失败证据保留。runner/coordinator 修复提交 `a1298db`，合成审查 PASS；静态闭包提交 `eb8ce87`；新 RunId `batch109_r4` 已启动；2026-10-02 13:16（UTC+8）定向进程查询确认 sample0 Verilator 全网仿真正在运行，未见 108 样本批跑或 D9 进程；之后按 Wong 要求不主动监视。 | 109 样本完整 PL golden/head 导出与 D9 比较均未完成 | 按 Wong 要求不主动轮询；用户再次要求时做定向只读状态核验。完成后检查 summary 与 D9、核验各样本快照映射、独立 G4/G5 审查与阶段记录 |

- 新tile边界/缓存/异常回归（2026-10-02）：T70 `report/evidence/S2A-T70/boundary_full01/boundary_report.json`，真实head29/36各零输入和非零pattern完整生产遍历，共50700输出字节逐独立INT64/D2黄金零差异；8异常含5非法descriptor零请求、feature/weight -128与首tapoverflow注入零输出，result背压5拍稳定无请求，12/12 exit0，独立审查PASS。固定request class stall/地址/strobe/cache读数齐，生产RTL不改。overflow仅白盒原语；response固定一拍；不证明3×3完整缓存遍历、PL109或G4/G5。
- 新tile所选tile/group内存回归（2026-10-02）：T70 `report/evidence/S2A-T70/memory_full01/summary.json` 实测21层×16定向=336项、147896输出字节零差异，56740684cycles，编译/仿真exit0，独立审查PASS；真实descriptor和GF8，白盒仅起始tile/group，其后生产patch/weight加载、算术、地址/strobe和固定class stall精确计数。新增独立runner/TB，生产RTL不变；完整遍历/cache和异常仍由boundary任务补，不表示G4/G5通过。
- 新tile算术回归（2026-10-02）：T70 `report/evidence/S2A-T70/whitebox_diagnostic03/summary.json` 实测21层×(1000随机+16定向)=21336查询、169790实际lane、零差异，编译/仿真exit0；独立审查PASS，冻结T17向量/共享PRNG与真实GF8全组权重逐项一致。新增runner/TB，不改生产RTL。白盒只预装所选点patch/权重并执行生产算术/MQ，再取消；不覆盖memory/cache/整层遍历/异常/G4G5。相关缺口由独立memory回归继续补。
- 验收准备（2026-10-02，静态范围）：运行说明 `docs/S2A-T68_local_run_guide.md` 已补齐终态门、证据保留和干净副本恢复/复验命令；真实核查摘要 `report/stage2a_acceptance_preparation_20261002.json` 记录38项源码大小/SHA/基线blob匹配、109项T25 manifest-index元数据匹配、既有定名单元及protocol05/06终态证据。未检查当前批次、未重读shards/大波形、未执行备份或真实恢复。T69无独立机器目录，应使用摘要所列T02/T08/T10–T21原始JSON；T17/T20仅历史串行engine/pilot，新tile适用性须终审及必要回归。实际109 PL/D9/源码映射、clean-copy恢复、归档可恢复性与G4/G5仍PENDING。
- T25/T29 冻结 CPU oracle 可恢复性（2026-10-02，只读文件清单/源码审查）：Git 跟踪 `report/evidence/S2A-T01/tiny416_model_manifest.json`、`report/evidence/S2A-T01/fixed_test_samples.json`、`report/evidence/S2A-T25/cpu_layer_golden_index.json` 和 `report/evidence/S2A-T29/cpu_decode_nms_reference.json`。`report/evidence/S2A-T25/tensors/` 当前有 109 个普通文件、共 390,700,998 B，Git 跟踪路径数为 0。静态 D9 验证器 `verification/verify_s2a_t68_d9_outputs.py::verify_frozen_cpu_baseline` 调用 T29 generator，从这些 T25 shards 确定性重建并与冻结 T29 报告作 canonical bytes 比较；因此干净副本 D9 重验依赖保留这些未跟踪冻结 CPU-oracle shards，它们是 G4/G5 恢复材料。该 T25 归档输入与 `S2A-T68` runtime evidence 分开；本检查没有查询 T68 进程、日志或运行证据，不改变 no-monitoring 边界。阶段冻结时须归档精确 shard 文件清单及逐文件 SHA-256，并记录可恢复路径；不得批量暂存整个 shard 目录。本次未读取 shard 内容或计算其哈希。恢复清单 `report/evidence/S2A-T25/t25_shard_recovery_manifest_20261002.json` 已于提交 `e42f689644be74239ab8d1a2b3f0c505090d7656` 纳入 Git，文件 SHA-256 `5352b2ef6edb8f40bb1e635aaa1337556171937db176db841fb044406657d0d9`；主控已对全部 109 个 shard 计算 SHA-256 并匹配冻结 index 条目/大小，总计 390,700,998 B。独立 Reviewer 的 `PASS` 仅覆盖 manifest-to-index 一致性审查，没有重新计算 shard 内容哈希。该 manifest 是本地恢复/完整性元数据，不是第二份备份，也不是 `S2A-T68` runtime evidence；保持不轮询、不读取、不干预 T68 进程、日志与运行证据的边界。
- T25 clean-copy 恢复风险（2026-10-02，静态源码核对）：`verification/s2a_cpu_layer_goldens.py` 的全量新建流程要求目标目录不存在；干净 Git 副本含已跟踪的 T25 index，因此不能直接按新建流程生成。`--resume` 会验证既有 checkpoint 和 shards，不能补回缺失分片；故未完成 clean-copy shard 恢复验证前，不把“理论可重算”视为可恢复证明。ZIP 归档尝试被本地执行策略在启动前拒绝，未生成归档或 sidecar，源 shards/manifest 未修改；不通过改策略或替代工具绕过。另一次状态整理子代理误用宽泛 Git 状态查询，意外输出受限 T68 目录的文件名；未读取文件内容或查看进程/日志，发现后停止访问并已告知 Wong。按既有边界继续不查询、不读取、不干预 T68 运行状态。
- T25 clean-copy恢复实测（2026-10-02）：干净副本 `tmp/s2a_clean_restore_20261002_160036` HEAD `d530281`；冻结Python3.12.10/NumPy2.4.6/OpenCV4.13.0，单线程数值库BelowNormal。真实恢复109×38成功（2283.61s）、CPU D9 canonical109复验成功（12.359s，总2296.36s），独立Reviewer逐新分片压缩/解压SHA及全部终态记录审查PASS。证据 `report/evidence/S2A-T25/clean_restore_20261002_160036/recovery_execution_record.json`、`final_evidence_integrity.json`；恢复器109完整校验后原子发布，未读取原shards/PL109运行。这关闭CPU oracle clean-copy恢复缺口；不证明PL证据归档、PL全流程副本重跑、G4/G5。
- 截止与预算：Wong 于 2026-10-01 要求 2A 在 7 天内完成；截至 2026-10-02 尚余 6 天（目标 2026-10-08 前通过 G5），不得降低验收标准。架构仍为 8×8 tile / 8 output lanes，CSR、32-bit timeout 与 memory protocol 不变。冻结 manifest 的保守脚本估算为单帧 1,940,519,260 cycles（request stall `[0,1,2,7,3]`，4 个算术用例通过），脚本状态 `ESTIMATE_ONLY_NOT_RTL_PROOF`；109 帧按当前 8-worker layer0 吞吐线性外推约 59 小时，必须由 sample0 全网实测校准。此前约 1.16B cycles 预算仍未被 RTL 验证；不作为当前排期依据。
- G4/G5 静态实施资格审查：基于 HEAD `5116ac1d0f05cb9ad2ea76ee91e45da2ca152161` 的可复用实现与验收链路审查为 `PASS`；该结论仅表示静态上具备按冻结规格产出并核验完整交付物的路径，**不表示仿真运行通过，也不表示 G4/G5 已通过或阶段已冻结**。最终验收仍须在同一冻结基线上取得 109 个固定样本各自完整 38 层 PL golden 记录且零 mismatch；取得 109 样本真实 PL heads 对冻结 CPU T25/T29 D9 的完整比较；合并 T69 已通过的单元/协议结果时逐项保留其证据与适用性，不能替代整网结果；将每个样本编译 source snapshot 的文件哈希映射到干净且可恢复的 Git tree/commit；证据须归档于可访问、可恢复的 `report/evidence/S2A-T68/<RunId>/`（含输入/模型/源码与工具清单、运行记录、逐样本结果、SHA-256、复现命令及从干净副本重建/重跑步骤）；形成真实结果的阶段验收记录并完成独立 G4/G5 签收。G3 板测在 2A 属 N/A：本阶段仅 PL RTL 仿真，T01 与当前范围均不授权烧录或实物操作；综合、资源利用率和时序在 2A 亦属 N/A：本阶段验收目标是功能仿真，不执行综合，不能据此声称资源/时序通过。以上实际结果及审查均待完成。
- 静态源闭合复核（2026-10-02）：`report/evidence/S2A-T68/static_source_closure_20261002.json` SHA-256 `93df3e1947e618f72324444268640382416dd6d631b4ae260e0c49f07fc51b8f`，基线为 runner 修复提交 `a1298dbc4b41eb9ac54caca77e18fd00bee30538` / tree `dbac6be3f860e1ade64eaf55add4e1915ea74545`，38 项中仅 runner 与 coordinator 两项刷新，其余源与固定 T29 绑定保持不变。`verification/verify_s2a_t68_snapshot_git_binding.py` pins 已更新；闭包更新已于提交 `eb8ce872e79869d2346bc9cb206025b563b64236` 固化，独立审查 PASS，10/10 合成测试通过。runtime snapshot mapping 仍未实测，109 样本证据映射及 G4/G5 未完成。
- 归档忽略规则核对（2026-10-02）：`git check-ignore -v` 对 `report/evidence/S2A-T68/batch109_r3` 和预期 D9 报告 `report/evidence/S2A-T68/batch109_r3/d9_109_sample_report.json` 均无匹配（not ignored）；根目录 `.gitignore` 无 `report/evidence` 规则。此项仅记录忽略配置，不代表目录内容或运行状态已核实。阶段冻结时须逐项枚举必要证据文件、记录 SHA-256、注明可访问且可恢复的归档路径及干净副本重建/重跑步骤；不得批量暂存整个证据目录。
- 执行边界：范围为完整 Stage 2A PL 推理仿真，不含综合资源声明、板测或烧录。T61 run05 attempt05 是离线准备，不是新仿真结果；run04 DATA_ONLY 也不是全网通过。
- 保护状态：PID 8712 Vivado、22488/13156 XSim 为审计记录的受保护进程，任何运行前重新核对身份，不停止/关闭/重置/发送状态修改。MCP 当前连接健康但项目为 `s2a_t61_run04` 的 `isolated_project`、Top 为空，不是2A仿真实例。
- T63/T64/T65、进行中的 T66-A 与其他工作区差异均须保留并先核对；日志、夹具、临时文件和大型生成物留在 D 盘，默认不生成大波形。
