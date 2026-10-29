# S2C 吞吐优化状态入口

更新：2026-10-30 01:40（UTC+8）。本树为独立离线候选，阶段目标尚未完成。

## 目标与边界

- 目标：tiny416、INT8五类手势检测保持冻结数学语义，最终由DSH连续至少2帧、每帧不超过0.5秒裁决。当前没有整帧达标结论。
- 当前优先级：Wong于2026-10-30明确选择先完成32 lane加突发中间版；继续离线实现，不用中间结果替代原2fps目标。
- 工作树：`D:\FPGA_Competition\w2c`；分支：`codex/stage2c-throughput`；冻结上游：`07c3d3958578b9cc9d3b8eae3758711fe08724c2`。
- w2b及其2B位流/证据只读；不写main/w4/w5/dbdf/w6业务文件；不push、不操作板卡。跨方只追加Codex信箱，主目录提交由DSH负责。
- 禁止JTAG、COM4、hw_server、xsdb、program、QSPI与Hardware Manager。DSH提出的2B板级排障不构成本任务的硬件授权。
- 单重型任务互斥；每次启动前检查进程与内存，不结束其他方会话。仅离线短仿真已执行；本轮没有启动整网综合/实现。

## 已验证与提交

- 模型/论文分析见现有设计文档 `docs/obsidian-project/02-方案设计/s2c_throughput_feasibility_20261029.md`，冻结三数424506368拍、69732736B权重读、11382150B写复算一致。预测误差±20%未验证。
- `6ac0dbf`：32 bank特征缓存独立短仿真通过；此处32 bank不等于32 MAC。
- `dff544d`：AXI3读缓存原型，64bit、最多16 beat、ID0、单outstanding、授权区间/4KiB切分及取消排空；25项短仿真及独立审查通过。尚未接入adapter/整网。
- `340aa2d`：DSP候选与失败归档；module属性OOC报告route_query为7→0 DSP、LUT1245→2484，但退出码未留、无时钟约束；XSim引擎失败。业务源无效属性已撤销，未声称DSP资源或时序关口通过。
- `f1a136ec1ec6548c8774a1269b49ff91349b85b0`：银行缓存接入frozen16×16 Tile；工程Tcl/JSON加入源清单。首层首Tile实测73559 cycles，8192个输出字节与T66旧黄金逐位一致、无重复/遗漏。独立审查PASS_LIMITED_PROTOTYPE_CODE。
- RTL05 r04为真实PASS；r01环境失败、r02声明顺序编译失败、r03 tap计数预期漏乘4组失败均保留。r01-r03清单打包改动和缺少修改前SHA按r05审计说明。
- RTL05 r06补证因输出截断失败，原件保留，不能把校验器0清单/0条目当通过；r07完整commit_blob补证已实查11项/0差异，未重跑仿真。

## 当前限定原型

- 成段接口设计已独立审查READY_FOR_IMPLEMENTATION，契约为`docs/obsidian-project/02-方案设计/s2c_lane32_bulk_interface_20261030.md`；保留旧mem_ready完成语义，新增8B对齐/8..128B命令及本地字节流，物理64-bit AXI3突发，写先收齐缓冲后声明AXI。

- RTL06已实现可选frozen8/32输出lane，generic仍8、network默认仍8；当前仅新TB显式32。完整每lane4608B权重阵列尚未综合，不声称资源放得下。
- RTL06 r02：32 lane同一首Tile实际52043 cycles，8192字节黄金逐位一致、无重复/遗漏；input3072、weight864、bank写3267、bank读6627。默认8回归仍73559 cycles、bank读26508。两配置编译/展开/仿真各exit0。
- 32/8首Tile周期改善约1.41倍，不是整帧加速或板级帧率；逐字节搬运与逐通道量化开销仍在。RTL06源码/证据已由独立Reviewer审为PASS_LIMITED_PROTOTYPE_CODE，随本STATE提交；最终身份以包含本STATE的提交为准。
- 非法lane参数仅有仿真time-zero的initial $fatal保护，未运行非法配置分支，不主张综合或elaboration拒绝；generic0未新增仿真。
- 新证据入口：`report/evidence/S2C-RTL06/`；RTL05提交绑定补证：`report/evidence/S2C-RTL05/feature_bank_engine_20261029_r07/manifest.json`。
- RTL07 r07：真实AXI3成段桥38项定向检查PASS，含未对齐/非8倍数长度拒绝、取消排空及合法B先AW；三工具exit0。随机样本0，不能当随机覆盖。
- RTL08 r04：32 lane成段字节流首Tile8192唯一字节黄金一致，35019 cycles，615 bulk加8 legacy，早错误2/早成功6语义PASS，三工具exit0。r01/r02首输出X为fixture加载触发问题，r03结果握手竞态FAIL；旧失败保留且另作可恢复归档。
- RTL09 r02：旧word经新适配器8544向量/179定向检查PASS，seed=722472976，三工具exit0；r01参数传递失败保留。
- RTL10 r01：engine经真实bulk适配器及AXI模型首Tile8192唯一字节黄金一致，36993 cycles；111AR/512AW/499R/1024W/512B精确匹配预测。三工具exit0；编译覆盖21个候选平台RTL源。不是整帧/板级结果。
- 新顶层generic默认仍8/0，候选平台显式32/1、100MHz、visibility0，新身份不继承2B缓存/XSA/ELF证据；集成静态检查及独立源码审查限定通过，综合入口仅准备未执行。审查原件见S2C-REVIEW。
- `3dfac02277c13d68c1adcfc4ea057025179c62b2`已提交上述原型/成功与失败证据。S2C-BIND/lane32_bulk_commit_20261030_r01补充140项commit_blob绑定，strict核验140项/0差异；未重跑实验。日志原件已入提交但不作manifest条目，退出码/日志SHA由result绑定。

## 风险与下一步

- 32个MAC在100MHz的整帧纯算术下界106126592 cycles，即1.061秒；32 lane单独加突发不能达到2fps。原始≥2fps目标仍开放，需额外空间并行或另经用户决策调整模型。
- 当前逐字节本地流且装载/计算/逐lane量化/输出互斥，额外串行下界137270380 cycles，即100MHz至少1.3727038秒；约0.72849fps仅为上限而非预测。S2C-M02独立复算PASS；历史traffic/8乐观候选不能直接用于本实现。
- 原11.821秒/100MHz校准与DSH新回执的47.3秒/50MHz及4倍计时误差说法冲突，尚无已确认的精确勘误证据路径。旧预测暂不能作可靠帧时承诺；保留历史模型不追改L0冻结预算。
- DSH新函`DSH-20261030-002-fps-baseline-correction.md`声称47.287秒/50MHz并作计时宏勘误；仍缺所引RunId精确绝对路径及原件，正文时间也晚于收函时间。Codex信箱003已请求补齐，暂不追改旧校准或三项预算。
- 下一步：RTL11整网黄金TB正在独立准备；完整head13/head26及框逐位比较、整帧cycles、100MHz综合资源/时序尚未执行。原默认顶层恢复矩阵也待资源窗口，不继承旧结论。
- 外方Vivado r02构建占用重型槽；本方启动门禁返回RESOURCE_BUSY_NOT_STARTED，不并发综合/仿真。Codex信箱002/003请求30–60分钟独占窗口；不停止外方进程。
- 三项门控尚不齐备，把握未达到80%，没有上板验证请求，不主张G3/G4/G5。
- 旧未跟踪`report/evidence/S2C-RTL01/tile16_20261029_01/manifest.json`为历史无效包装，保留且不纳入交付通过证据。

## 当前交接行（11字段）

任务=`S2C吞吐离线候选` | 负责人=`Codex本总控` | 工作树/分支=`D:\FPGA_Competition\w2c / codex/stage2c-throughput` | 起始提交=`07c3d3958578b9cc9d3b8eae3758711fe08724c2` | 允许修改范围=`w2c候选源码/仿真/设计/证据及本STATE；主目录仅Codex信箱追加` | 未提交改动归属=`本轮候选实现/短仿真及证据归Codex；RTL11新TB归Developer integration_review且仍开发中；旧RTL01与RTL08r01包装保留不交付` | 让出声明=`未让出` | 心跳(UTC+8)=`2026-10-30 01:40` | 证据入口=`S2C-RTL07 r07；RTL08 r04；RTL09 r02；RTL10 r01；M02及REVIEW` | 恢复命令=`先核HEAD/status/锁/进程/RAM，再读取本STATE与相应manifest；禁止连接板卡` | 状态/下一接手方=`IN_PROGRESS / Codex本总控`
