# 阶段4 状态（真实PS张量诊断接入准备）

更新：2026-10-23 23:32（UTC+8）。工作树 `D:\codex-worktrees\w4`／分支 `stage4-infer-prep`。规则见 `D:\FPGA_Competition\AGENTS.md`。
**写权：Codex 阶段4接续总控受 Codex 项目总控委派独占，IN_PROGRESS。** 认领基线 `af85d5a8495598262395165492df5e4d0bfb723c`；DSH 于 00:35 OFFERED 并停止写入，00:42 现场复核 `handoff_check --claim` 得到 9 PASS / 0 FAIL / 0 SKIP，随后 CLAIMED→IN_PROGRESS。
**Wong 最新要求：先完成当前整帧PL小程序，然后结束本轮。4-D及完整阶段4尚未验收。** 仅收尾该小程序的必要仿真、独审和提交；系统集成/板测不继续开启。工作树写权无转移；硬件未认领、SDK/JTAG/UART均未操作。

## 继承的交付与版本

- DSH 主体提交 `e247b49`：4-A G0 r06、共享契约 `s4-shared-io/1.1.0` r02、主机 mock DDR/cache 单帧注入；审查限制 `bb5d9ab`；OFFERED 声明 `821b05a`；末次交接提交 `af85d5a`，认领时工作树干净。
- 4-A 自检 18/18、变异 9/9、包装核验通过；24条上游绑定包含23文件及109分片目录。R1 只读独立复算全部匹配（109片 / 390,700,998 B）。
- Codex接管后新自检：`report/evidence/S4-A/s4a_g0_20261023_r03/`，18/18、23文件及109分片SHA匹配，exit 0；首轮R02日志编码环境失败原样保留。
- 最终修复S4-B r08：严格GCC 0警告、host42/42、C API检查30/30、unit10/10、小图CRC2/2；30项含两个64位平台不适用提示，不代表32位覆盖。32位两个编译单元通过，链接缺i686 CRT/libgcc退出1，行为NOT_RUN。S4-CTRL r05：23项通过、契约变异5/5及运行书反序变异1/1拒绝；最终两包CHECKS_OK。
- 4-B 历史离线证据：gcc 严格编译0警告、23用例、8条 unittest；这些证据未覆盖本轮独审缺陷，不能据此判 G2。
- 契约与地址图仍 `DRAFT_PENDING_REVIEW`；200 ms stale 门槛仍 `DRAFT_PENDING_APPROVAL`。不得提前作为正式验收阈值。
- 提交前源码/STATE空白检查通过；全量暂存检查退出2仅因原始证据CRCRLF/历史探针末尾空行，保留原字节，例外及实际退出码见最终 `lead_validation.json`。

## 本轮离线修复与独立审查

- Codex 独立 Reviewer R1/R2 已对 `bb5d9ab` 源码补审，均 `CHANGES_REQUIRED`（源文件在交接提交中未变）。
- R1：共享契约 session_id string 与 S4-A u32 不一致；各连接键角色未对齐；synthetic 时间可用性/词表不完整；地址图草案被称冻结、S4-A 镜像旧哈希未标历史。T3显示语义/T4 HUD 13键符合；旧 r01 T1–T4 原始报告未找到，类别摘要不能代替原关闭条件。
- R2：写前未拒绝在途区间重叠；在途帧序号回退；空payload绕过完整性；采集时间哨兵/CLI解析；stride/帧长溢出；缓存顺序与mock可见性；CHW平面统计；timeout后安全释放及回调生命周期。
- 两轮修复后R1-03/R2-03独立复审均PASS，本轮主机离线实现/规格G2通过；最终19文件快照及原始探针在 `report/evidence/S4-CTRL/s4_g2_closure_20261023_r02/`。闭合运行书顺序、通用SIZE_MAX范围及初始化失败重试；先前失败复审与所有RunId保留。此结论不等于32位行为、真实PS/BSP、PL、G3/G4或阶段G5通过。
- 保护旧已冻结离线链：`s4_ps_decode.*`、`s4_uart_protocol.*`、`s4_offline_host.c`、`run_s4b_offline_chain.py`、`build_s4b_manifest.py`、`test_s4_ps_decode.py` 与全部旧RunId不改写。

## 必须保持的接口与边界

- 2B 正式冻结 `07c3d3958578b9cc9d3b8eae3758711fe08724c2`：1000连续任务、108 ACK闭环样本；109黄金不等于109 ACK闭环。
- UART方案B：`s2bu/1.1`正文不变、扩展关闭，时间/丢帧/过期/状态只记PS侧；结果与旁路日志按会话/帧/结果序号明确关联。
- 候选上限12675可行，尝试追加12676为硬错误；4096禁用；候选数与最终≤15框不同。
- 注入须位于被验收预处理前；capture_time_available=false，capture_time_ns为0哨兵并注解，计时起点用injection_start_ns。灰度不能对旧彩色golden。
- S4-B-REAL-01/02A已提交 `0d3ad04be26efeb366ecf20487848a613a0a63fe`：离线源码/操作计划G2闭合，R1来源计划PASS、R2终态PASS；37单测及34独立CRC快照探针exit0，17文件原字节Git快照核对一致。闭合包 `report/evidence/S4-CTRL/s4_ps_tensor_closure_20261023_r02/`；evidence exit0、inputs exit2保留草案/硬件/RGB门禁。ARM相关源码未变，限定复用r12实际构建，不冒称旧全包匹配当前doc。5份ELF及5份map原位保留并绑定SHA，不入源码Git；不等于完整4-B/G3/G4。
- S4-B-REAL-02B修复3及运行书最终独审PASS：修复1的权威来源/成功RUN竞态、修复2的RunId前缀误配/测试写旧prep均关闭；原失败证据保留。r04四源冻结record SHA `ecde9ec0fca0d9cca3ea835f861b32199656b0141af4e91aa6d61f7dc5fed366`；main硬件OFFER+w4 CLAIM须为真实Git双记录，逐键精确匹配。r13 ARM构建0，Developer及Reviewer各22 adapter/38 tensor tests0，fresh prepare/validate0；独立ARM反汇编确认真正RUN成功后永久WFE停泊，stop前后CSR校验。闭合 `S4-CTRL/s4_ps_adapter_closure_20261023_r01/` evidence0/inputs2；6份ELF/map及init原位保留，不入Git。当前无正式硬件offer/claim，真实gate拒绝；SDK/JTAG/UART及46,000-word能力NOT_RUN。
- 原始RGB入口尚未接通；合法202×329→416反例D2=100、精确有理数=101，不能改容限。Wong已在本会话明确批准RAW RGB888→PL预处理→HP0串行owner→冻结网络、独立PS/JTAG原帧入口及跳过CPU tensor拷贝路线进入受控开发/OOC，保持D2及S2BU1.1、不合并stage3视频；`docs/stage4/S4B_pl_preprocess_g0_readiness.md` 已登记 `ARCHITECTURE_APPROVED / G0_NOT_READY`。PL-G0-02正核对数值可实现性和地址/资源依据。额度中断后17:47恢复，Wong告知板卡已上电连接；尚未装载、打开串口或板测。
- 阶段5仍绑定S4-A r05；请求 `S4CTRL-20261022-003` 由阶段5所有者改绑r06并确认共享契约，不写w5。
- 真实摄像头回归尚未完成，不能声明完整阶段4 G5；模块到货/阶段3复测以其持有方现场证据为准。4-D文件注入候选不合并视频XSA。硬件门禁未闭合前不操作板卡/JTAG/COM4，不结束他人进程；阶段5已明确释放板卡，仍须核对当前注册表及正式接管条件。

- G0材料已独审PASS并提交 `161401e644bf5830931758fe776c6e8bdf823742`：109帧中97帧>4MiB，最大packed RGB888=11,059,200B，4MiB草案仅容12帧；按109完整覆盖预算。D2旧/新SHA仅EOL差；34合成桥接一致，未重生成/逐值核验109帧或PL。证据 `S4-B/s4b_pl_g0_input_scope_20261023_r01/`、`s4b_pl_g0_reference_bridge_20261023_r01/`、`S4-CTRL/s4_pl_g0_materials_20261023_r01/` 保持当时待批准身份；本次批准不改写旧证据。6份桥接文件误落主tmp已保全/恢复，记录保留。
- 后续109 RAW+直接标量D2重生完成：109/109匹配冻结输入SHA，exit0、190.075秒；RAW808263072B、参考56589312B留w4新tmp RunId，已对218输入逐文件机器核验。长期脚本/日志/结果/恢复政策 `report/evidence/S4-B/s4b_raw_reference_109_20261023_r01/`，不代表PL/4D。
- PL单通道数值核G2独审PASS并提交 `c9bab114d535191ae2dc2ef8bdcd087f15ed672a`：r04 XSim 547 FP64逐位、10pixel及6系数错误通过，工具exit0；Reviewer独立重建127阈值、381邻界点/1021整数半整数/10000固定种子点并重核547期望。5源冻结 `S4-B/s4b_pl_numeric_g2_20261023_r02/`，record SHA `a091bae3b4fcd98bc898bfb77cd89a5fa3a1bbb4dfd0f012b20404b17935b7bd`；闭合包 `S4-CTRL/s4_pl_numeric_closure_20261023_r01/` evidence0、inputs2（当时OOC/硬件NOT_RUN）。仅单通道、不含padding/几何/整帧。
- 后续单次OOC综合exit0：xc7z020clg400-2，LUT1930/FF1674/BRAM0/DSP0、43秒、Vivado peak2008.668MB。综合后施加20ns/IOdelay0，WNS+9.411ns、WHS−0.276ns（288保持违例端点；仅最差路径已证实为输入到寄存器），HD.CLK_SRC未设、无布局布线；整体时序未闭合，不外推FPS/整网。报告 `S4-B/s4b_pl_numeric_ooc_20261023_r01/` 已独审PASS其证据和限制口径，timing检查真实exit1、evidence0/inputs2；自有Vivado会话已关闭，无实物操作。
- geometry修复2冻结r03独审PASS并提交 `e1e79fcfcedd653681336e45c323de6ba3ed5558`：42设备名及6路径别名在文件IO前拒绝，13tests0，202×329真实D2边界和目标轴1/同尺寸分支独立复核。闭合包 `S4-CTRL/s4_pl_geometry_closure_20261023_r01/` 保留27份各轮记录；仅metadata，不含硬件ABI/整帧PL。DDR材料事实独审PASS；系统G0独审CHANGES_REQUIRED（PS无golden参考、全owner期START gate、COMMIT精确回显、跨启动session唯一性、注入PS时基五项），按停止指令封存草案，不称系统G0通过；独立参数化整帧引擎局部G0已明确；26份2B固定Git源已逐SHA恢复到新隔离tmp，不改w2b。19时子代理额度中断，22:48同一总控恢复、无移权，四个整帧目标文件尚未创建，现已恢复Developer。Wong先暂不发送、后明确“可以发送”，22:48已向“新项目总控”成功发送硬件窗口/DSH协调请求；项目总控回执CDX-20261023-018建议摄像头先行、阶段4就绪后再申请，窗口未落实、COM4持有者未核实。随后已通知项目总控本轮收尾停止、不申请OFFER/窗口；无实物操作。

- 历史S4-C `s4c_replay_20261021_r05` 的109/109 PASS、0数值差异已独立核对，可精确复用CPU golden heads→D9→T29范围；本轮未重跑109样本/重哈希390MB分片，未覆盖D2/r06新字段或板卡。复用证据 `report/evidence/S4-C/s4c_evidence_reuse_20261023_r01/` 包装CHECKS_OK；此前“109全量NOT_RUN”不能解释为历史离线回放未做。

- 当前小程序 S4B-PL-FRAME-01：r07 prepare/5 Python tests/XSim各0，TEST_PASS cycles29978；两4×4完整CHW及202×329→416通道0前88B/abort，非完整416验证或吞吐。四源已停写，冻结 `S4-B/s4b_pl_frame_g2_20261023_r01/`，record SHA `28d820ab0034adc99aac74cdb375f8eae9e7a75f95267f0c608112bcb965bb67`；最终独审中。r03–r06失败/工具审批拒绝及归属核验保留；本任务Vivado会话均关闭。

## 证据与恢复入口

- 认领：`report/evidence/S4-CTRL/S4-C05/s4_codex_claim_20261023_r01/claim.json`；DSH原让出：`report/evidence/CTRL-DSH-HANDOFF/handoff_20261023_r01/`（原记录不改）。
- 既有：`report/evidence/S4-A/s4a_g0_20261022_r01/`、`report/evidence/S4-B/s4b_injection_20261022_r01/`、`report/evidence/S4-CTRL/S4-C02|S4-C03|S4-C04/`。
- 通用清单规范包：`report/evidence/S4-CTRL/s4_codex_takeover_20261023_r01/`，认领及审查摘要包装CHECKS_OK；初版清单结构失败与原始C05记录保留。
- 上游冻结 SHA 仍以 `docs/stage4/s4a_stage4_g0_fields.json` 及原证据清单为权威；不复制另一套业务规格。

## 交接行（11字段）

任务=`按Wong收尾当前整帧PL小程序，独审提交后结束本轮` | 负责人=`Codex 阶段4接续总控（受Codex项目总控委派）` | 工作树/分支=`D:\codex-worktrees\w4 / stage4-infer-prep` | 起始提交=`af85d5a8495598262395165492df5e4d0bfb723c` | 允许修改范围=`本树docs/、verification/、scripts/、vitis/、report/evidence/、tmp/4/、.codex/STATE.md；Wong批准PL路线所需src/、sim/、vivado/受控新增；保护旧冻结离线链与既有RunId` | 未提交改动归属=`截至4639501已提交；系统G0草案/DDR审计、当前小程序与证据均本总控；6ELF/6map本机恢复依赖不入源码提交` | 让出声明=`未让出；本树写权由Codex阶段4接续总控独占；硬件尚未认领` | 心跳(UTC+8)=`2026-10-23 23:32` | 证据入口=`report/evidence/S4-B/s4b_ps_adapter_g2_20261023_r04/；S4-CTRL/s4_ps_adapter_closure_20261023_r01/；S4-B/s4b_pl_numeric_ooc_20261023_r01/` | 恢复命令=`git -C D:/codex-worktrees/w4 status --short; git -C D:/codex-worktrees/w4 log --oneline -3; git -C D:/codex-worktrees/w4 rev-parse --git-path index.lock` | 状态/下一接手方=`IN_PROGRESS / 当前Codex阶段4接续总控`
