# 阶段6 STATE（S6-A/S6-B/S6-E 交互控制；离线部分）

## 6-D 最新阶段5交付资格核验（2026-10-30 19:27，UTC+8；优先于下方历史状态）

- `report/evidence/S6-D/s6d_handoff_qualification_20261030_r01/` 绑定main a25ee008的阶段5 G0/显示ABI/G3记录、w4 17fe51bb的显示消费者与G3-B结果包，以及旧w5 2decd0dc/r07。新交付在main/w4，旧w5未更新不等于阶段5没有新证据；仅消费固定提交，不改上游。
- G3-B清单45项SHA/字节数一致；80B种子按32B头/16B检测步进解出8字段和3框，96B回读前80B一致。cap/inf四个时间字均0、status=1；已有GT时间槽和stale位，但本例为预置显示种子，src=real不证明真实推理。旧w5核对93成员声明结构及2个消费成员，未重跑159套件或声称93成员全部字节核验。
- 字段矩阵11项，6-D资格仍BLOCKED：生产写端未交付，会话/结果序号与业务状态映射不完整，缺可信发布时间/时基与可重算年龄。显示stale超1帧及47.3s+16.7ms年龄口径不能直接替代交互已批200ms；参数未改。具体证据、责任输入见field_qualification.json与gaps.json，不补造事件或时间。
- 独立Reviewer s6d_handoff_audit_review 对manifest SHA-256 2385b41eea0c01db759b37a2736bd20b7b4f297edcf7f821fdc33bec30443063 返回PASS；隔离重跑四份资格/解码结果逐字节一致。inputs/evidence/strict全0，65条清单项零不符、最终stdout一致；PASS限交付绑定与资格审计，不代表6-D集成通过。
- 包装初轮15次调用失败轨迹与成功轮21次均保留；审计3.460秒、93次Git调用（版本查询另1次），峰内存未测。297个原文件在本轮STATE更新前未变，旧3处差异与14个历史包不混提交；恢复入口为本包audit.py、source_bindings.json及输入快照。core_event_constructed/core_step_called均false，preview/T6-A03 NOT_RUN，6-E实物及阶段G3/G4/G5未闭合；未上板。

任务=`6-D正式交付绑定与输入资格审计收口` | 负责人=`Codex阶段6总控` | 工作树/分支=`D:\codex-worktrees\w6 / stage6-interact-prep` | 起始提交=`ec1a35b5b367620c19d5a54597aad1b8d98e6c48` | 允许修改范围=`本轮6-D离线审计新证据、STATE新增段与字节保真规则` | 未提交改动归属=`原3处差异及14个历史包保持原归属；本轮精确提交新增内容` | 让出声明=`Codex持续持w6写权，未OFFER；无硬件操作` | 心跳(UTC+8)=`2026-10-30T19:27:17+08:00` | 证据入口=`report/evidence/S6-D/s6d_handoff_qualification_20261030_r01/` | 恢复命令=`git -c core.longpaths=true -C D:/codex-worktrees/w6 status --short` | 状态/下一接手方=`IN_PROGRESS / Codex；资格审计PASS，6-D业务BLOCKED，等上游生产与语义交付`

## 6-C 隔离恢复验证（2026-10-30 18:06，UTC+8；优先于下方历史状态）

- `report/evidence/S6-C/s6c_isolated_recovery_20261030_r01/` 从固定提交44615bd3完整干净检出，再按提交内快照恢复130项历史输入、10项canonical源码和1项运行STATE；7项上游只重定位path/git_repo，固定提交、相对路径、SHA及批准参数不变。5个业务模块均从隔离副本加载。
- 44项S6-B、17项receipt、26+1回放、6步序号探针、S6-A 17项自检通过，27份事件日志和两份expected_freeze与原r07逐字节一致；JSON差异仅精确列明的路径和C8外部漂移诊断说明。原r07 strict114项零不符；新包inputs/evidence/strict全0、84条清单记录零不符，最终stdout复跑一致。
- 独立Reviewer s6c_recovery_review 在第二个全新副本恢复141项并重跑全部验证，结论PASS；被审manifest SHA-256=3035993cfa7167891b6d6ef6e535826f380cb9c0faffd30a52537c2730f650a6。原297个保护文件在本轮STATE更新前全部未变；两次包装schema预检失败原文保留，不作为通过记录。
- 恢复入口为本包recover.py、restoration.json、upstream_relocation.json、comparison.json及delivery_manifest.json；再次运行必须选新RunId和空目录，不覆盖r01。副本只读共享原Git对象库，证明独立文件系统恢复，不是自包含Git归档；业务输入未从live dirty工作区借用。缓存保留在tmp/stage6/S6-C，未清理旧证据。
- 主恢复12.296秒、最终封包2.082秒；16个验证子进程、21次包装调用，Git blob调用未单独计数、峰值内存未测。未修改生产行为；旧STATE/两规格差异与14个历史未跟踪包继续保留、不混入提交。6-D仍BLOCKED，P/T6-A03仍NOT_RUN，6-E实物/G3及阶段G4/G5未通过；未上板。

任务=`6-C隔离恢复验证收口` | 负责人=`Codex阶段6总控` | 工作树/分支=`D:\codex-worktrees\w6 / stage6-interact-prep` | 起始提交=`44615bd3aad2a1f423af996b9af2b68cb8d20e57` | 允许修改范围=`本轮6-C恢复证据、STATE新增记录与字节保真规则` | 未提交改动归属=`原3处差异及14个历史包保持原归属；本轮精确提交新证据和新增状态段` | 让出声明=`Codex仍持w6写权，未OFFER；无硬件操作` | 心跳(UTC+8)=`2026-10-30T18:06:00+08:00` | 证据入口=`report/evidence/S6-C/s6c_isolated_recovery_20261030_r01/` | 恢复命令=`git -c core.longpaths=true -C D:/codex-worktrees/w6 status --short` | 状态/下一接手方=`IN_PROGRESS / Codex；隔离恢复PASS，6-D依赖未闭合，阶段G5未通过`

## 6-C 离线确定性矩阵收口（2026-10-30 15:12，UTC+8；优先于下方历史状态）

- Wong 委托总控裁定：0xFFFFFFFE 无特殊停发阈值，FE→FFFFFFFF 可正常递增；同会话 FE→0/FFFFFFFF→0 一律 B23 拒绝，高水位/窗口/目标证据不更新，H3 单调期限继续；从零重计须新 session_id。24 项已批准参数值未改，未操作硬件或 FPS 优化。
- `report/evidence/S6-C/s6c_deterministic_matrix_20261030_r07/`：44 项 S6-B（core 34）、17 项 receipt、26 条矩阵、重复 ACK 1 例、序号边界 6 步、S6-A 自检 17 项通过；正式矩阵 11/11 行覆盖。C11 实际83文件/82绑定，inputs/evidence/closing 均0，strict 114清单条目零不符；最终保存输出与复跑一致。
- 独立 Reviewer s6c_final_review 对基线 e13c5532 与 r07 manifest SHA-256 460060de6fa4276ddfe2759e4895783c9b1cf8a70997e8e52eb7353d86aa92d7 返回 PASS，隔离复跑44+17/26+1/6步及17自检一致。6-C离线任务限定范围 G0/G1/G2/G4 满足；不代表阶段6整体关口通过。
- 20261030 r01–r06 原位保留为权限、导入、先验预期及封包失败轨迹；r05/r06记录或部分检查通过不能覆盖其最终失败。历史 dc180833 与 f44bd3eb 的差异已证明是 CRLF→LF 哈希口径；精确对应见 r07/hash_reconciliation.json。
- 恢复入口为 r07/source_bindings.json、inputs/src/behavior.md、inputs/src/behavior.json、inputs/state_at_run.md 与 execution_record.json；原 U6-02 规格/STATE 差异继续保留且不混入本轮提交，孤立 HEAD 不等于运行时完整规格。峰值内存及工具调用总量未测，单测耗时保留于日志；未运行重型流程。
- 下一任务6-D仍 BLOCKED：固定阶段4 replay包及阶段5冻结输入未变，仍缺可信结果时间/stale/阳性状态映射；本轮不改上游。T6-A03 缺实测帧周期P保持 NOT_RUN，推理耗时47287ms不能代替P；6-E实物/G3及阶段G4/G5未通过，暂不上板，不开启阶段7。

任务=`6-C离线矩阵收口及6-D依赖核验` | 负责人=`Codex阶段6总控` | 工作树/分支=`D:\codex-worktrees\w6 / stage6-interact-prep` | 起始提交=`e13c5532abde97771c9e8ce3776e837f0c6816df` | 允许修改范围=`阶段6离线规格增量、测试、独立新RunId、STATE与字节保真规则` | 未提交改动归属=`原STATE/两份S6-A规格及14个历史未跟踪包保持原归属；本轮仅精确提交新增内容` | 让出声明=`Codex持续持有w6写权，未OFFER；无硬件操作` | 心跳(UTC+8)=`2026-10-30T15:12:00+08:00` | 证据入口=`report/evidence/S6-C/s6c_deterministic_matrix_20261030_r07/` | 恢复命令=`git -c core.longpaths=true -C D:/codex-worktrees/w6 status --short` | 状态/下一接手方=`IN_PROGRESS / Codex；6-C离线限定验收完成，6-D等上游字段，阶段G5未通过`

## 回绕拒绝与证据修复（2026-10-30，UTC+8）

- Wong 明确同会话回绕一律拒绝；B23/B25 与机器规格已统一，异常帧不刷新窗口/目标证据，H3 单调时间期限仍评估，新 session 才允许重新从零开始。0xFFFFFFFE 是否提前停发/换会话保持待裁决，旧强制表述已标历史非当前规则。帧率优化由 Wong 取消，按其确认的 0.08 fps 可用继续，本任务不启动 FPS 优化或硬件。
- `report/evidence/S6-A/s6a_b25_decision_20261030_r03/`：定向回绕 1 项、核心回归 33 项及 S6-A 17 项自检通过，C11 最终42文件/41内部+18外部，strict hash 59项零不符；最终输出逐字节复验且独立复审 PASS。r01/r02 保留此前过期输出/阈值冲突问题；该结论仅限本轮离线修订，6-C完整矩阵及G3/G4/G5仍未通过。
- r03 固定运行时 STATE 与实际工作树规格字节；本次STATE更新后，恢复该次哈希核验需在隔离副本按包内 inputs/state_at_run.md 及绑定源码快照还原运行版本。原有U6-02规格/STATE未提交差异继续保留，不代表整个工作树冻结。

## B25 裁决续办（2026-10-29，UTC+8）

- Wong 选择与阶段4契约一致：同会话帧号回退按倒序异常处理，重启或计数器复位须新 session_id。当前实现已有此路径，补充回退不刷新窗口/目标锚点、H3 到期及新会话保留冷却的回归；32 项独立复跑 PASS。两份 S6-A 规格本轮修订叠加在既有未提交差异上，尚未作为精确审查版本提交。
- DSH-20261029-004/005 声称允许同会话 FFFFFFFF→0，与 S4 r07 合同的回绕均拒绝冲突；其“状态改变前拒绝”与既有 H3 单调时间推进亦待澄清，两项 BLOCKED，不能默认为用户已批准。0xFFFFFFFE 描述待明确；不触板。
- `report/evidence/S6-A/s6a_b25_decision_20261029_r04/` 保存回执和失败自检：C11 缺证据目录/清单参数而 FAIL，未完成交付清单；`report/evidence/S6-A/s6a_b25_regression_20261029_r01/` 保存 32 项回归与 strict hash 检查路径错误 exit 2。此为局部进展，S6-C/G4/G5 未闭合；r01–r04 失败轨迹保留。

## S6-C 离线矩阵进行中（2026-10-29，UTC+8）

- 本轮新增 K01 冷却阈值前 1 ns、等于和后 1 ns 回归；独立复审单项 PASS。`report/evidence/S6-C/s6c_deterministic_matrix_20261029_r04/` 记录 40 项 S6-B、17 项回执单测和 C11 重复 ACK 回放退出 0；独立复跑 C11 PASS，先验 expected 以 r02 的较早冻结记录为依据。
- S6-C 整体未通过：`report/evidence/S6-C/s6c_deterministic_matrix_20261029_r06/` 输入及 hash-basis 检查退出 0，但 evidence/closing 因 BLOCKED 项空命令字段退出 2；固定点未闭合，不能当完整交付。r01–r06 保留，r05 封包筛选重复帧错误。历史矩阵绑定的行为 JSON 哈希 `f44bd3…` 与当前 `dc1808…` 的可复核版本对应尚未建立，不声称语义等价。
- B25 同会话大回退判据和 0xFFFFFFFE 回绕表述仍待决，第 8 行及整体矩阵 BLOCKED；其余行的本轮汇总仅供后续复审，不代表 G4/G5。r04–r06 含 Windows 默认路径长度限制下无法检出的深层副本，恢复须先配置 Git 的 core.longpaths=true；后续从 r04 原始日志、r06 失败检查及固定上游版本恢复，先闭合规格版本与封包问题，再重新独立审查；暂不上板。

## S6-B 离线核心核验（2026-10-29，UTC+8）

- `report/evidence/S6-B/s6b_current_20261029_r08/` 绑定当前核心、测试、U6-02 r07 回执及阶段4离线冻结契约；frame_id 的 uint32 类型与范围在状态变化前校验。39 项回归、26 条矩阵、4 项探针及证据哈希检查通过；独立复审对本轮离线核心变更 PASS。r01–r05 和未运行的 r07 保留，r04/r05 包装失败不得当作交付通过。
- B25 的同会话 frame_id「大幅回退」阈值未定义，当前仍 BLOCKED；阶段4契约规定计数器复位须新 session_id。S6-A 文档的 0xFFFFFFFE 回绕要求与机器规格表达存在差异，生成侧及真实链路尚未验证；本轮不声称该路径通过。P/T6-A03、6-E 实物、G3/G4/G5 仍未闭合；Wong 指示暂不上板。

## S6-A 回执恢复绑定（2026-10-29，UTC+8）

- `report/evidence/S6-A/s6a_u6_02_recovery_20261029_r04/` 固定基线 `86a2bb18` 与 130 项声明输入；在隔离 Git 副本恢复后 S6-A 自检 17/17 PASS，U6-02 r07 回执批准语义核验 PASS，输入、证据及 hash-basis 检查通过，独立复审 PASS。复现结果绝对路径随隔离目录变化，归一化后逐字段一致。
- 恢复包仅涵盖已声明的 C11 输入及门禁工具，不是完整工作树备份；原有未提交 STATE、规格和历史证据仍保留。r01–r03 失败记录保留，其中 r01 保存退出码及 stderr 哈希但未保存 stderr 原文。该结果不代表阶段 G0/G3/G4/G5 通过；Wong 指示暂不上板。

## S6-D 回放资格修复（2026-10-29，UTC+8）

- `report/evidence/S6-D/s6d_replay_qualification_20261029_r05/`：对当前阶段4/5冻结回放输入执行资格核验，缺可信结果时间、stale 与阳性状态映射，结论 BLOCKED，核心 NOT_RUN。资格门对无法证明时间来源的 stale=true/false 均失败关闭；恢复固定源码快照后 12 项定向测试、阶段5冻结集 93 项及输入/证据和哈希检查通过，独立复审 PASS。不得将此结果作为实时或板级验收。
- 修复旧上游审计的换行哈希基座混用：冻结工作区字节与固定提交 blob 分别校验；修复前失败记录和 10 月 28、29 日旧轮次保留。S6-A 的 U6-02 r07 已有会话级独立复审 PASS，但其未提交规格/回执和未归档复审结论尚不足以从干净提交恢复。
- Wong 指示暂不上板；T6-A03 缺阶段4实测 P 保持 NOT_RUN，6-D 真实集成、6-E 实物验收及阶段 G4/G5 未闭合。此前 10 月 28 日 10:00 的板卡借用期限已过，不视为当前硬件授权。

## 只读诊断租约时间核验（2026-10-28，UTC+8）

- Wong 将阶段6板卡借用授权延至 10 月 28 日 10:00（UTC+8）；执行前仍须核验最新租约、独占及正式硬件会话 OFFER/CLAIM。`CDX-20261027-002-stage6-jtag-readonly-offer` 已请求交接；当前尚未收到正式交接，不得仅凭授权或无进程开会话。
- `report/evidence/S6-E/s6e_jtag_readonly_timebounds_20261028_r04/` 的离线修复采用唯一时间或日期元数据字段及保守时间区间，65 项测试通过，独立复审 PASS；该次租约快照可解析 DSH-010。CHECKS_OK 仅表示清单绑定；r01–r03 保留此前失败及审查记录。本节替代下方关于 DSH-20261024-004 时间不可解析的历史状态。
- 实际只读 JTAG 扫描 NOT_RUN；真实动作执行器/观察接口与阶段4/5真实集成仍未就绪，P/T6-A03 和 6-E 实物保持 NOT_RUN，G3/G4/G5 未通过。恢复时先重新核对最新交接、租约与设备占用；既有未提交 STATE、S6-A 规格和历史证据继续保留。

## 只读连接诊断准备（2026-10-28，UTC+8）

- `verification/s6e_jtag_readonly_scan.py` 及其测试的离线限定复审 PASS；40/40 模拟测试通过，证据与真实检查器来源见 `report/evidence/S6-E/s6e_jtag_readonly_prep_20261028_r08/`。旧 checker 不支持 hash_basis 的失败与 r06 初轮测试失败保留；CHECKS_OK 仅说明清单绑定。
- 硬件扫描仍 NOT_RUN：主目录与 w6 的正式 OFFER/CLAIM 尚缺，执行时 reviewer receipt 尚未签发；DSH-20261024-004 的不完整时间使租约验证 fail-closed，须先取得可核验的时序澄清，不得绕过。收到有效交接和租约证据后，按已审源码生成绑定实际提交的审查回执，再执行只读连接核验；该核验不代表 G3/G4/G5。
- Wong 已安排 2026-10-28 05:00（UTC+8）在本对话继续阶段6冻结闭环。原 STATE、S6-A 规格及历史证据未提交差异继续保留，P/T6-A03 和 6-E 实物仍 NOT_RUN。

## 阶段6执行边界与板卡通知（2026-10-27，UTC+8）

- S6-C 动作回执边界 `report/evidence/S6-C/s6c_action_receipt_boundary_20261027_r02/`：离线串行 ACK 路径 45/45 单测、inputs/evidence 与哈希检查通过，独立复审 PASS。边界只检测串行旁路，不能阻止并发直调核心；真实后端/跨进程恢复接口仍 BLOCKED，须保持唯一 ACK 写入口。
- Wong 指示立即推进阶段6，不处理阶段4；已按既有协作授权在主目录 Codex 信箱发送 CDX-20261027-002-stage6-jtag-readonly-offer，仅请求阶段6只读连接诊断的正式交接。DSH 信箱 009 曾要求暂停新会话，010 于 23:00 明确释放并恢复 008 租用；执行前仍须核验最新召回、独占和正式交接。本窗口未开窗、未连板、未启动硬件会话；只读 JTAG 扫描器仍在离线修复/审查，未通过前不得执行。
- 阶段6真实动作执行器与观察接口尚未就绪；P/T6-A03、6-E 实物/G3 保持 NOT_RUN，阶段 G4/G5 未闭合。

## 板卡租用与 P 测量准备（2026-10-27 22:11，UTC+8）

- Wong 已明确授权 Codex 使用板卡；主目录 DSH 信箱的 DSH-20261027-008-board-lease-stage6 允许阶段6限时单会话使用，须遵守提前通知、候选区禁写、异常停止与收窗清理约束。当前未开窗、未连接、未启动硬件会话。
- Wong 已授权发送协作请求；已在主目录 Codex 信箱新增 CDX-20261027-001-stage6-p-lease-request，请求 DSH 确认 P 采集程序的固定版本与测量执行/交接安排。该信箱记录尚由主目录写入方按规则串行提交。
- P 测量当前仅核实到阶段4方案、模板和校验器，未核实到实时采集程序；阶段6真实板级执行器与结果接口仍未就绪。P/T6-A03 保持 NOT_RUN，不把板卡租用、离线回放或单帧诊断当作测量结果。

## 真实单帧诊断与显式复位（2026-10-27，UTC+8）

- Wong 批准显式 `reset_session()` 返回 RESET 日志并保持原复位行为；`report/evidence/S6-B/s6b_reset_log_20261027_r02/` 的 28 项单测、26 条矩阵、4 项探针及 inputs/evidence/closing 通过，独立复审 PASS。保留冷却锚点、单调时间和 ACK 账本，旧参数接受范围不变；r01 失败记录保留。
- S6-B r02 清单的 interfaces_not_applicable.reason 沿用旧句“阶段4/5 契约仍未冻结”，该句对当前状态已过期：阶段4/5 已分别冻结离线范围；它们不等于真实接口/板级集成已验收。清单原文与哈希保留，CHECKS_OK 不验证该历史描述的实时准确性。
- 阶段4提交 `4e0b03dd7090c7dc5615a4cd1e40bd193715faff` 的真实 PS INT8 单帧诊断在 `report/evidence/S6-D/s6d_real_ps_diag_20261027_r01/` 完成只读重解码与关联核查，7 项测试、inputs/evidence 和独立复审 PASS。PS `(session_id,result_seq)=(1396845568,1)` 与 UART `(frame_id,repeat_index,sequence)=(0,0,2)` 属不同命名空间；无检测框几何、state、可信结果时间及 stale，阶段6核心资格 BLOCKED，未调用核心。
- 因本轮核心字节变化，历史回放 r08 对当前核心的哈希绑定已过期，仍作为当时版本的历史证据；r10 保全其临时输入并不改变该限制。当前真实单帧诊断预检不读取或绑定阶段6核心。P/T6-A03、6-E 实物及 G3 保持 NOT_RUN；真实集成与阶段 G0/G4/G5 未闭合。

## 离线准备续办（2026-10-27，UTC+8）

- S6-D 对提交 `15a26c1` 的核心重绑定：`report/evidence/S6-D/s6d_replay_no_hand_20261027_r08/` 上游审计及清单检查通过并经独立复审；NO_HAND 与 PRESENT 两帧均缺有效时间/stale，资格 BLOCKED、核心 NOT_RUN。R08 引用的 9 个缓存输入已在 `report/evidence/S6-D/s6d_replay_no_hand_20261027_r10/` 原字节保全并映射；该恢复包独立复审 PASS，无 tmp 的隔离副本 verify-local 通过；重跑 R08 原 checker 仍须先按映射恢复缓存文件。R05/R07/R09 失败轨迹保留，R06 失败材料由 R10 保全。

- S6-B 会话切换修复 `report/evidence/S6-B/s6b_session_clock_20261027_r06/`：保留全局冷却、单调时钟和已见 ACK 身份，重置会话窗口/目标/计数；非法输入先校验，补 source_order、超大数和抖动耗尽复位边界。28/28 单测、26/26 矩阵、4/4 探针及 inputs/evidence/closing 通过，独立复审 PASS。公开 `reset_session()` 的外部日志接口尚无正式定义，保持待决；ACK 接口缺 session_id，重启后的 ID 冲突及跨会话迟到来源无法消歧。
- S6-E 纯离线计划 `report/evidence/S6-E/s6e_command_delivery_20261027_r05/`：26 条均 NOT_RUN；24/24 测试及清单检查通过，独立复审 PASS。路径覆盖、重复 JSON 键、非有限数及伪造验收声明均有拒绝测试；真实 Windows 符号链接创建因 WinError 1314 未执行，模拟拒绝分支通过。此结果不关闭正式 `command_delivery_review`，不授予硬件窗口。
- S6-D r04 绑定上一版核心 `80080866…`，对当前核心的哈希检查已过期，保留历史；当前有效绑定与阻塞范围见本节上方 R08/R10。T6-A03 缺实测 P 仍 NOT_RUN；6-E 实物/G3 未执行；真实 6-D 及阶段 G0/G4/G5 未闭合。

## 离线推进（2026-10-27，UTC+8）

- S6-A U6-02 r07 回执绑定包 `report/evidence/S6-A/s6a_u6_02_bound_20261027_r05/`：17/17 自检、9/9 claim、17 项工具自测及 inputs/evidence 通过；独立复审 PASS。被绑定的两份规格和 r07 回执属于本轮开始前未提交内容，提交基线本身不能单独恢复该包；r01–r04 失败或未完成记录保留。
- S6-D 回放单帧预检 `report/evidence/S6-D/s6d_replay_no_hand_20261027_r04/` 独立复审 PASS，绑定核心提交 `590823b` 与阶段4冻结契约提交 `4400bb89`；r03 因并行修改核心导致绑定过期，保留历史证据。阶段4 离线冻结包 10/10 哈希一致、阶段5 消费产物已绑定。实际单帧 NO_HAND/零框缺有效 stale 与结果时间，预检 BLOCKED、核心 NOT_RUN；该预检不解除真实集成阻塞。6 项单测针对工作树模板的未变化分类函数，运行副本的上游审计另行实跑通过。
- S6-B/C M10、重复 ACK 与 B22 业务内容冲突修复：`report/evidence/S6-B/s6b_ack_suppress_20261027_r01/`，定向 27/27、既有矩阵 26/26、清单检查 PASS；独立复审前几轮问题关闭，最终 suppression 定向复审 PASS。ACK 去重集在单一长会话随回执数增长，接口缺 session_id，异步跨会话迟到回执无法消歧。
- T6-A03 缺实测 P 仍 NOT_RUN；6-E 实物/G3 未执行；真实 6-D、阶段 G0/G4/G5 未闭合。所有工作仅离线，不修改阶段4/5 工作树或操作硬件。

任务=`阶段6离线缺口修复与验收准备` | 负责人=`Codex 阶段6总控` | 工作树/分支=`D:\codex-worktrees\w6` / `stage6-interact-prep` | 起始提交=`3be42b897003e00680bd554d915939de7dfde08e` | 允许修改范围=`阶段6离线源码、测试、新证据及 STATE` | 未提交改动归属=`原有 STATE、两份 S6-A 规格及旧证据继续保留；本轮变更见离线推进段` | 让出声明=`Codex 持有写权；未操作硬件，未向其他方 OFFER` | 心跳(UTC+8)=`2026-10-27 14:22` | 证据入口=`report/evidence/S6-A/s6a_u6_02_bound_20261027_r05/`；`report/evidence/S6-B/s6b_ack_suppress_20261027_r01/`；`report/evidence/S6-D/s6d_replay_no_hand_20261027_r03/` | 恢复命令=`git -C D:/codex-worktrees/w6 status --short` | 状态/下一接手方=`IN_PROGRESS / Codex；离线审查完成，真实集成与阶段验收未闭合`

## 目标
阶段6 交互控制：五类动作判定、多框选择/同分排序、目标保持与重获、抖动/稳定窗口、冷却与再触发、
持续保持只触发一次；产出 G0 行为表 + S6-B/S6-C 实现与确定性证据 + 6-E 验收用例集。硬件（摄像头/板测）不在本轮。

## 当前事实（2026-10-25，6-E/6-B 离线轮）
- 2026-10-25 R6-02 修复延迟模板检查器对批准绑定与嵌套 `*_ns` 占位值的遗漏；24/24 定向回归、7/7 注入拒绝通过，R6-03 独立代码审查 PASS。R6-04 补齐本轮 RunId 清单，R6-05 独立包装审查 PASS，evidence checker `CHECKS_OK`；此结论仅限源码/证据包装。
- RunId `report/evidence/S6-E/s6e_latency_gate_fix_20261025_r01/` 绑定修复源码、测试、27 项 RunId 文件与3项回归输入；硬件测量、完整工具自测保持 `NOT_RUN`，T6-A03 数值仍 `NOT_RUN`。此修复不解除 6-D、实物验收或阶段 G5 阻塞。
- 契约：`S6A-G0-v1.8`；**24 项参数按草案值获 Wong 批准**（2026-10-23，批准记录在 main：
  CTRL-DSH-HANDOFF/decisions/`stage6_approval_receipt_20261023_r01.md`）；行为表含 `approval_record` +
  24 项 `approval_status=APPROVED_20261023` 与 `approval_ref`；**参数值未修改**。
- `T6-A02`=500ms 保持；`B16 S_DEDUP` 设计上不可达（H-10 全局冷却门覆盖）不计入覆盖；`T6-S01`=200ms/`T6-S02`=6
  （30fps 第 8 帧 233.1ms，按 `T6-S03`「取较晚」）；`U6-12` 保留 M4 并计入覆盖；`U6-16` STABLE 获取内锁存；
  `U6-15`=`A_SWITCH_UI`+`A_SWITCH_CHANNEL`；`U6-13` 口径固化、**数值 `NOT_RUN`**；`T6-STALE_LIMIT`=200ms（阶段4/5/6 同一常量）。
- 关键机制事实：S6-A 自检 17 项（C4 批准纪律、C8 已批准包扫描、C11 清单/STATE、C16 语义可达性）；S6-B 26 条确定性用例 + 4 项探针；
  `claim_verify` 逐条真实退出码且 verdict 由全部 claim 计算；`export_selfproof` 必须显式 `--s6a-run`。

## 谓词绑定口径（与行为表逐字一致）
> M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段。

## 冻结链与轮次关系
- F4/G4（`6b8e5f2a`/`f5b749ed`，tag r3）→ F5/G5（`caa9728a`/`61caac0d`，tag r4，**已降级为非冻结记录**）→
  F6c/G6（`0a2abc49`/`a2d232da`，tag r5）→ **F6d/G6b（`2f16d668`/`538b7923`，tag r6，当前有效冻结）**。
- **本轮（6-E 离线）产出 r13/r08 修订内容**：不新打冻结 tag、**不称已冻结/已审查**；终审批次 E 的关闭项逐条落实，独立复评由项目总控另派。
- **A1 失实陈述更正（终审 E §五）**：G6b STATE 曾写「规格文档拆分当时/现口径、**8 条历史修订行写回当时状态并标注历史语境**」——
  终审 E 复核为**实际 0 条写回、7/8 无标记**，该表述属「把未做写成已做」。**本轮 r13 已真正落实**（8 行写回 `PENDING_APPROVAL`（当时状态）+ 逐行机读标记 `【历史语境】`）。
- 旧 tag（r1..r6 与 per-profile tag）保留不动；旧 RunId r01..r12 / r01..r07 **不就地改写**。

## 6-E 离线轮完成项（A 组：结清被推迟的遗留清单）
- **A2 规格改准**：L9/L171/L185/L282/L320/L321 改为已批准口径（L128/L397 保留机读历史标记）；另修 L10/L184/L313/L47/L186 附近口径。
- **A3 历史行写回**：8 条修订行（L14/21/28/30/32/34/36/38）写回当时状态 `PENDING_APPROVAL` 并逐行加 `【历史语境】`。
- **A4 机读假命题清除**：`fix_record.json` 的 `all_parameters_pending_approval: true` 删除，改为 `all_parameters_approved_20261023: true`；
  陈旧 `new_run_id` 改准为 r13；覆盖矩阵位置标签与 C4 标签改准；S6-B 侧 `reachability_notes.derived_from`、
  `case_matrix`/`build_case_matrix.py` 的现行陈述改为 APPROVED 口径；矛盾文本（`limitations` 指标口径、「草案值 草案值」）已修。
- **A5 扫描器收紧**：`approved_package_scan.py` 改**大小写不敏感**（修死正则）、收窄逐行豁免（机读历史标记/非批准类状态/禁止性规则描述）、
  注入/探针/失败证据按**文件级**豁免；对旧包 r12 仍报 5 处命中（判别力反例），对 r13/r08 为 `CLEAN`。
- **A6 双向必失败注入**：`--inject-self-test` 改为两向 —— B1..B7 必判失败形态**全部命中**、C1..C4 必须放行对照**全部不命中**；纳入 claim `S6A-C8`/`S6B-C5` 与套件用例。
- **A7 批次 C 三项**：① `fresh_selfcheck_pair.json` 由 claim `S6A-C6` 对**清单当前**状态实跑生成并入库（S6-B 侧由 `--fresh-pair` 在不动点内跑）；
  ② 套件两条必 FAIL 例改为**只在临时副本**内运行（不再改写真实附录）；③ 套件 `skipped` 改为 **fail-closed**（`INCOMPLETE_SKIPPED` + 退出码非 0），
  新增 `--simulate-skip` 必 FAIL 自测，套件产物 `tool_self_tests.json` 直接入库。
- **A8 复跑**：见「证据入口」中三包清单 `checks` 的真实退出码（r13 4/4、r08 6/6、S6-E 4/4 全 PASS 且 exit 0）。
- **快照自证（提交前，2026-10-24）**：S6-A 剖面 `--worktree-snapshot --s6a-run r13` → `ALL_SELF_PROVEN [0,0,0]` exit 0；
  双剖面（+`--s6b-run r08`）→ `ALL_SELF_PROVEN [0,0,0,0]` exit 0；报告见两条 `_selfproof` 目录。
- **提交级自证（2026-10-24）**：交付提交 **`509e39e`**（本轮 A+B 内容）经
  `export_selfproof --commit 509e39e… --s6a-run r13 [--s6b-run r08]` 复跑 → S6-A 剖面 `[0,0,0]`、双剖面 `[0,0,0,0]`，
  均 `ALL_SELF_PROVEN` exit 0（报告含 commit 与快照两个主体）。**G 段记录提交本身未再做第三层提交级自证**（如实披露）。

## 6-E 离线轮完成项（B 组：真实推理验收用例与窗口材料）
- **用例集 v1**（`S6E-ACC-v1`，26 条：动作 11 / 未知 3 / 恢复 8 / 离线自检 4），绑定已批准 24 项与 `stale=200ms`；
  覆盖运行手册 §4 全部 11 类；`T6-A03` 数值保持 `NOT_RUN`（机器断言禁止填造）。
- **真实 vs 离线边界**：`ACT-*`/`UNK-*`/`REC-*` 一律要求**真实推理结果**（`REC-07` 要求真实连续时间 ≥30 min），
  `synthetic_substitution_allowed=false`；`OFS-*` 仅离线自检且**不构成** 6-E 验收。
- **校验器**：`verification/s6e_acceptance_check.py`（E1..E11 + 6 类必 FAIL 注入；基线 ALL_PASS、6/6 捕获）。
- **上板窗口申请材料**：`report/evidence/S6-E/s6e_acceptance_20261024_r01/board_window_request.md`（**未申请**，八类门禁逐项状态、11 字段模板、时长预算、停止条件与恢复）。

## 无板卡轮（task-28，2026-10-24）
- 全局事实：**Wong 已拔下板卡** ⇒ 板级工作暂停且不设期限（`decisions/board_detached_boardfree_plan_20261024_r01.md`）；6-E 实物验收暂停，恢复须先重做受连接判据。
- **项 2 已交付（延迟方法学 + 占位模板）**：`docs/stage6/S6E_latency_methodology_v1.md` + `docs/stage6/s6e_latency_measurement_template_v1.json`（`S6E-LAT-v1`）
  + 校验器 `verification/s6e_latency_template_check.py`（L1..L7 + 5 类必 FAIL 注入，基线 ALL_PASS、5/5 捕获，exit 0）。
  结构禁填造：实测 `*_ns` 占位字段为 `null`；`acceptance_gate.t6_a01_limit_ns=1000000000` 是已批准门限，不是实测延迟；`acceptance_gate.t6_a03_limit_ms=null`、**`T6-A03` 数值仍 `NOT_RUN`**；**回放不构成实时证据**。
- **项 3 已交付（窗口申请包就绪化）**：`report/evidence/S6-E/s6e_boardfree_20261024_r01/board_window_readiness.md`，
  八类门禁与 P1–P7 **如实**核对，结论 **`NOT_READY`**（仅 `g0_approval` 部分满足：用例集冻结 + 24 参数批准）；未申请、不排期。
- **项 1（回放驱动的 6-E 预演）`BLOCKED`**：依赖阶段4 回放结果包（`task-26`，前置 `task-25`）与阶段5 离线显示回归（`task-27`），两者均未产出；
  解阻后跑 `S6E-ACC-v1` 的动作/未知/恢复用例，结论须标注「回放预演、非实物验收」，不得改写任何门禁状态。
- 复用工具：通用证据包构建器 `verification/s6e_pack_build.py`（清单/哈希/两检查器真实退出码；不动点 + 收尾断言）。

## 阻碍 / 开放
- **2026-10-24 Codex 门禁修复轮（优先于上文历史自证结论）**：正常 claim 保留真实退出码并核验全部声明；ACT/UNK/REC 逐 ID 固定真实证据类别并全禁合成替代；24 项状态、回执引用、原始参数/批准 ID 数量、类型与唯一性均精确校验。
- E4 修复首轮复核发现重复参数/批准 ID 可被字典/集合掩盖；r03 已修正。独立复核 PASS：定向 unittest 9 项 exit 0、验收基线 `ALL_PASS`、14/14 注入捕获 exit 0、重复 ID 探针 exit 0。
- 新增证据 `report/evidence/S6-E/s6e_gate_fix_20261024_r03/`；源码与测试哈希见 `report/evidence/S6-E/s6e_gate_fix_20261024_r03/validation_summary.json`。`.gitattributes` 对 r01/r02/r03 限定为逐字节保存，避免全局 autocrlf 破坏原始哈希。
- r02 完整工具套件为 **exit 1 / UNEXPECTED**：其正常 claim 和快照自证针对旧 r13 运行包；C11 确认旧 r13 清单仍绑定旧版 `verification/tool_self_tests.py`，因此 C6 真实失败。旧 r13 与 r01/r02 失败证据均保留，不重写、不引用为通过。
- **S6-A G0 交付状态**：`DELIVERED_PENDING_G0_CONFIRMATION`；r14/r15/r16 失败与过期包均保留。r17 已构建：17 项自检 `ALL_PASS`，inputs/evidence 检查均 PASS，source commit=`bc9b2b7`；独立增量包审查 PASS，整体 G0/G5 仍未通过。
- **S6-B 重建**：r10-r13 全部保留；r11 是缺输入失败包，r12 虽清单检查 PASS 但摘要仍记录修复前 evidence exit 2，r13 只有部分初始产物且无 manifest。代码修复 `ef2f74d` 与 closing 独立封存修复 `c539828` 均经 Reviewer PASS；探针基线计数修复 `72c10e5` 经独立复审 PASS、定向测试 4/4。r01 保留为前版证据：closing 退出码未有独立 sidecar/清单绑定。r02 保留并标记 `CHANGES_REQUIRED`：probe 摘要把基线写成 23 例，矩阵及运行报告为 26 例，尽管结构/哈希检查通过。新包 `s6b_core_20261025_r03` 基于 `72c10e5470c6e1d4deecee3fec538605e16499d4` 与用例矩阵 SHA-256 `3a23f62c7b23acd1f35dd1eec6c974782fe38b5713dde3fb86763791d21e2552`：26/26 用例、4 项探针、inputs、最终 evidence 与独立 closing evidence 均 PASS/exit 0；fixpoint 第 3 轮收敛，首轮 evidence 预检 exit 2 保留。r03 增量包审查 PASS；离线检查不代表 G0/G4/G5 通过。
- **工具自测路径隔离修复**：`verification/tool_self_tests.py`、`verification/hash_convention_check.py`、`verification/test_s6_gate_regression.py` 已独立审查 PASS 并提交 `bc9b2b7`。最终路径回归 10/10 PASS；最新源码的完整工具套件在隔离克隆仅运行一次，16/16 `ALL_AS_EXPECTED`、无跳过，JSON SHA-256 `caf5af32c0002543d55d17efae7445d92ec8934828b646b058d2f35170cafecb`。旧 RunId、STATE 和共享输出指纹前后未变。复制前路径复验缩小了本机非对抗并发 TOCTOU 窗口，但不能消除最终检查与系统调用之间的竞态。
- `T6-A03` 交互延迟数值 `NOT_RUN`（缺阶段4 实测帧周期 P，不得填造）；G3 板测未做，Wong 报告板卡已接上但主机当前只识别 COM4、未枚举 JTAG（阶段3 W1 依用户选择等待 JTAG）；6-D 集成待阶段4/5 接口冻结（`BLOCKED`）；6-E 实物验收未执行；阶段7 暂不开工作树。
- 阶段6 完整增量独立复审 **PASS**（覆盖 F6d → task-23/task-28/E4 r03，并对照 S6-A r17、S6-B r03 的绑定）；STATE 摘要 P2 已在 `e55a326` 修正。不得把代码审查 PASS 或离线自测 PASS 写成 G3/G4/G5。

## 下一步
增量复审已完成；6-D/6-E 仍依赖阶段4/5 契约冻结及相应回放/显示结果包。板级工作须等 Windows 枚举 JTAG、取得适用窗口授权并重做受连接判据。

## 证据入口
（C11 口径：凡带扩展名的反引号 token 按**项目根**解析；此处只用全路径，避免被当作本证据目录内文件。）
- S6-A（本轮）：`report/evidence/S6-A/s6a_g0_20261024_r13/`、`report/evidence/S6-A/s6a_g0_20261024_r13/S6A_run_summary.md`、
  `report/evidence/S6-A/s6a_g0_20261024_r13/delivery_manifest.json`、`report/evidence/S6-A/s6a_g0_20261024_r13/claim_verification.json`、
  `report/evidence/S6-A/s6a_g0_20261024_r13/tool_self_tests.json`、`report/evidence/S6-A/s6a_g0_20261024_r13/fresh_selfcheck_pair.json`
- S6-A r17：`report/evidence/S6-A/s6a_g0_20261024_r17/`（17 项自检与 inputs/evidence 检查均 PASS；增量独立审查 PASS；source commit `bc9b2b7`；不代表整体 G0/G5 通过）；失败/过期包保留：`report/evidence/S6-A/s6a_g0_20261024_r14/`、`report/evidence/S6-A/s6a_g0_20261024_r15/`、`report/evidence/S6-A/s6a_g0_20261024_r16/`
- S6-B（本轮）：`report/evidence/S6-B/s6b_core_20261024_r08/`、`report/evidence/S6-B/s6b_core_20261024_r08/s6b_run_summary.md`、
  `report/evidence/S6-B/s6b_core_20261024_r08/delivery_manifest.json`、`report/evidence/S6-B/s6b_core_20261024_r08/claim_verification.json`、
  `report/evidence/S6-B/s6b_core_20261024_r08/tool_self_tests.json`、`report/evidence/S6-B/s6b_core_20261024_r08/s6b_fresh_evidence_pair.json`
- S6-B 修复后包 r01（保留，closing 未独立绑定）：`report/evidence/S6-B/s6b_core_20261025_r01/`（source commit `ef2f74d`）。r02（保留，Reviewer `CHANGES_REQUIRED`）：`report/evidence/S6-B/s6b_core_20261025_r02/`（probe 摘要基线注记 23 与实际 26 矛盾；inputs/evidence 结构检查 PASS 不关闭此语义问题）。新包 r03：`report/evidence/S6-B/s6b_core_20261025_r03/`（source commit `72c10e5`；26/26、探针 4/4、inputs/evidence/closing 均 PASS/exit 0；首轮预检 exit 2 如实保留），增量证据审查 PASS。r10-r13 全部保留；r12 是修复前摘要不一致包，r13 未完成且无 manifest。
- S6-E（本轮）：`report/evidence/S6-E/s6e_acceptance_20261024_r01/`、`report/evidence/S6-E/s6e_acceptance_20261024_r01/S6E_run_summary.md`、
  `report/evidence/S6-E/s6e_acceptance_20261024_r01/board_window_request.md`、`report/evidence/S6-E/s6e_acceptance_20261024_r01/s6e_acceptance_check.json`、
  `report/evidence/S6-E/s6e_acceptance_20261024_r01/delivery_manifest.json`、`report/evidence/S6-E/s6e_acceptance_20261024_r01/preserved_failures/`
- 上一冻结（保留不改写）：`report/evidence/S6-A/s6a_g0_20261023_r12/`、`report/evidence/S6-B/s6b_core_20261023_r07/`
- 本轮自证记录（提交前快照）：`report/evidence/S6-A/s6a_g0_20261024_r13_selfproof/`、`report/evidence/S6-B/s6b_core_20261024_r08_selfproof/`
- 无板卡轮（task-28）：`report/evidence/S6-E/s6e_boardfree_20261024_r01/`、`report/evidence/S6-E/s6e_boardfree_20261024_r01/S6E_boardfree_run_summary.md`、
  `report/evidence/S6-E/s6e_boardfree_20261024_r01/board_window_readiness.md`、`report/evidence/S6-E/s6e_boardfree_20261024_r01/delivery_manifest.json`
- 门禁修复（保留所有失败与修复轮）：`report/evidence/S6-E/s6e_gate_fix_20261024_r01/`、`report/evidence/S6-E/s6e_gate_fix_20261024_r02/`、`report/evidence/S6-E/s6e_gate_fix_20261024_r03/`

## 历史交接行（2026-10-25 01:05）
任务：S6-B builder/探针修复与 r03 证据复审/提交 | 负责人：Codex 项目总控 | 工作树/分支：D:\codex-worktrees\w6 / stage6-interact-prep |
起始提交：`d662e483229d4b63916aac708a73d257db1cb939` | 允许修改范围：S6-B builder/探针与定向测试（修复已提交 `ef2f74d`、`c539828`、`72c10e5`）、S6-A r17/S6-B r01-r03 证据、`.codex/STATE.md` |
未提交改动归属：旧 STATE 差异与 S6-A r14-r17、S6-B r10-r13 旧包保留；S6-B r01-r03 与本轮 STATE 更新归当前 Codex lead，按独立复审结论精确提交 | 让出声明：DSH-20261024-006 已正式交回主目录与四阶段树；Developer 已停写，builder/探针修复经独立 Reviewer PASS；w6 由 Codex 项目 lead 单写，无硬件操作 | 心跳(UTC+8)：2026-10-25 01:05 |
证据入口：`report/evidence/S6-E/s6e_gate_fix_20261024_r03/`、`report/evidence/S6-B/s6b_core_20261025_r02/`、`report/evidence/S6-B/s6b_core_20261025_r03/`、`report/evidence/S6-A/s6a_g0_20261024_r17/` | 恢复命令：`python -B -m unittest test_s6b_build_evidence -v`（verification/）；后续复审 F6d → task-23/task-28/E4 增量 |
状态/下一接手方：S6-B builder/探针修复 REVIEWED_PASS / `72c10e5`；r02 证据 CHANGES_REQUIRED 并保留，r03 包审查 PASS；S6-A r17 增量包审查 PASS；F6d → task-23/task-28/E4 整体增量复审未完成；6-D、实物验收及阶段 G5 仍 BLOCKED/NOT_RUN。

## 当前交接行（2026-10-25 05:39）
任务：R6-02 延迟门禁修复及 R6-04 清单补全（R6-03/R6-05 独立审查 PASS） | 负责人：Codex 项目总控 | 工作树/分支：`D:\codex-worktrees\w6` / `stage6-interact-prep`
起始提交：`c80fe7e714c83f1c73e08fcb8c23072e9225c4d7` | 允许修改范围：`verification/s6e_latency_template_check.py`、`verification/test_s6_gate_regression.py`、`report/evidence/S6-E/s6e_latency_gate_fix_20261025_r01/`、`.codex/STATE.md`
未提交改动归属：本轮源码、RunId 与 STATE 已提交于 `6324b93`；原有 S6-A r14-r16、S6-B r10-r13 与7个旧失败包保留、不入提交 | 让出声明：Developer 已停写；R6-03 代码与 R6-05 包装审查 PASS；未运行硬件/Vivado | 心跳(UTC+8)：2026-10-25 05:39
证据入口：`report/evidence/S6-E/s6e_latency_gate_fix_20261025_r01/delivery_manifest.json`；恢复命令：`C:/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -B D:/FPGA_Competition/verification/check_stage_delivery.py --mode evidence --project-root D:/codex-worktrees/w6 --manifest report/evidence/S6-E/s6e_latency_gate_fix_20261025_r01/delivery_manifest.json`
状态/下一接手方：R6 修复与包装限定范围 PASS，已提交 `6324b93`；T6-A03/T6-D/G3/G4/G5 仍 NOT_RUN 或 BLOCKED；下一步继续独立可执行离线增量，不越阶段/不操作硬件。
