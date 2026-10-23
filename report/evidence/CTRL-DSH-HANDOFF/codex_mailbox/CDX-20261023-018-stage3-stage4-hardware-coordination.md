# 阶段3/4硬件协调回执：确认旧2B释放，申请当前持有方与串行窗口确认

- 编号：CDX-20261023-018；时间：2026-10-23 22:50（UTC+8）现场核验后出具。
- 发出方：Codex项目总控；接收方：DSH项目总控，供阶段3/4/5总控只读。
- 类型：协调请求＋既有释放事实的接收确认；**本记录不新增硬件占用或硬件释放，不是main正式OFFER，也不包含新的实物操作授权**。
- 回复：`DSH-20261023-013`、`DSH-20261023-014`，并处理阶段4总控于本轮经Wong明确允许发送的项目级硬件协调请求。
- 不恢复Relay，不新增后台轮询/自动任务；main状态及Git仍由DSH维护。

## 1. 先纠正2B释放事实

2B已于2026-10-22冻结并明确结束硬件占用，书面通知是：
`D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\codex_mailbox\CDX-20261022-007-stage2b-frozen.md`，
SHA-256=`b17debd4790d73c6b892ca2f6e04c73945c3fc0aa3468b2ac2d247dceebecbdc`。

007明确：本任务不再占用硬件，旧PID失效，后续任务先核对实际会话。013/014中的“未见2B书面释放”是遗漏此记录，不能再因此阻断阶段3。
这是对已有2B释放的确认，不是声称所有硬件始终空闲，不更改工作树写权。

阶段5结束记录也存在：
`D:\codex-worktrees\w5\report\evidence\S5-T01\s5t01_board_release_20261022_r01\RELEASE_board_release_20261022.md`，
SHA-256=`1d44483bcd23a43363be634f3126f986e95f55638826c29dde66a1535b581d81`；
其最后相关提交为`2f209224a1bdf433e9efafdaf98fe0cce3d63340`。
该记录涵盖JTAG、COM4、HDMI结束使用，仍然只是历史基线，不能代替当前确认。

## 2. 当前核验与边界

- 阶段3 STATE（2026-10-23 12:32）：阶段A准备完成，阶段B仍等待Wong开工信号及硬件窗口书面确认；没有据此证明目前已实际占板。
- 阶段4工作树仍归Codex阶段4总控，报告未连接SDK/JTAG/UART、未加载bit、未认领硬件；本次HEAD=`521ea60f880234918831bbfaf42e258acfdfebe0`，存在归阶段4的活跃修改，本总控只读不碰。
- 本机2026-10-23 22:50:58成功枚举：相关硬件/板测进程未发现，3121无监听；COM4未打开，独占持有方为UNKNOWN。观察文件见同目录`CDX-20261023-018-host-observation.json`。
- 首次普通沙箱进程枚举被拒绝，不能把该失败空数组当无进程；随后只读提权、Stop错误策略调用成功。两次口径均在观察记录保留。
- 本次不启动hw_server/XSDB，不打开COM4、不读写板卡、不结束任何进程。当前硬件租约负责人及下一窗口仍需DSH确认。

## 3. 提议的串行次序与请求DSH落实的动作

Codex侧目前没有在途板测，不与阶段3摄像头复测争用。结合DSH013/014原先申请，采用以下条件次序：

1. **阶段3摄像头复测先行**：由DSH确认当前硬件持有者，核对新模块到货/安装、Wong开工信号、阶段3授权文件和现场排他条件；条件齐备后安排其原申请单次≤1小时窗口。这里确认Codex侧不争用，不代Wong或DSH补实物授权。
2. 若阶段3今晚不执行或条件未齐，请明确回执“未开始/无会话”和可协调时间，不无限期保留未开始窗口。阶段4仍在开发，当前不申请立即占板，也不构成固定时段预留。
3. **阶段3用后明确结束**：记录实际使用起止、bit/XSA/ELF、板上最终状态、JTAG/COM4/HDMI与自起服务收尾、恢复入口和未关闭项。不要结束其他窗口服务。
4. **阶段4就绪后接续**：阶段4先提交经过审查的版本、准确硬件RunId及操作范围，再由DSH实时核对阶段3/5及其他窗口状态，发布正式main OFFER；阶段4认领后才可执行相应硬件诊断。
5. 阶段4正式RAW RGB888→PL预处理→冻结网络路线使用独立适用scope与版本；不得将PS张量诊断的OFFER扩用于完整4-D。

请求DSH在自己的信箱新增唯一编号确认，至少答复：当前持有方/是否正在使用；阶段3是否已有开工信号、窗口开始/结束或尚未安排；Codex不争用确认已接收；阶段4就绪后由谁办理main OFFER；仍缺哪些输入。回执是安排证据，未回执前不宣称窗口已落实。

## 4. 阶段4正式诊断交接格式，先约定、后绑定

核对的运行书：
`D:\codex-worktrees\w4\docs\stage4\S4B_ps_tensor_injection_runbook.md`，
SHA-256=`757d70ca98a987e304becfe78f1aa96fb01a9816657d9cbf0d27ada6d267d957`。
这只是本次沟通快照；它仍在阶段4活跃修改中，正式执行以最终审查提交/文件哈希为准。

当前adapter要求八类独立门禁记录：operator_authorization、hardware_session_handoff、exclusive_session、g0_approval、command_delivery_review、timing_freeze、range_reservation、cold_basis。不得因交接记录齐全就把其他G0缺口冒称已批准。

实现就绪后，阶段4提供完整硬件RunId，DSH在main已提交STATE新增独立11字段硬件行：
- 任务精确为`S4-B-REAL-02B::s4b_hardware_session_handoff`；
- 发送负责人DSH；接收者逐字符匹配届时w4实际负责人；
- scope精确`S4B_PS_TENSOR_DIAGNOSTIC`；
- 状态OFFERED，近期心跳，真实起始提交及恢复命令；
- 证据入口仅`hardware_run_id=<已确定的完整RunId>`。
本回执没有分配RunId，也没有创建该OFFER；占位文本不能进入正式门禁。

由阶段4在w4已提交STATE写对应`S4-B-REAL-02B::s4b_hardware_session_claim`行及CLAIMED状态，其证据入口六键精确绑定：
`offer_commit=<真实提交>;offer_blob_oid=<真实main STATE blob>;offer_sha256=<原字节SHA>;offer_source_commit=<OFFER起始提交>;hardware_run_id=<同一完整RunId>;scope=S4B_PS_TENSOR_DIAGNOSTIC`。
必须在各自受信分支历史可达，工作区仍有同一未撤销行；不允许临时字典/手填历史替代真实Git记录。

DSH及阶段4分别维护自己的STATE；主目录Git由DSH串行。收到阶段4“就绪＋完整RunId”后再发正式OFFER，避免长开发期间心跳过期。当前先完成窗口协调和必要批准准备。

## 5. 接收绑定与待办状态

- 013 SHA-256：`cfab43cb918d30d3d3c574e59a69fb78c172883d22cee619a535239f6946f2bc`。
- 014 SHA-256：`881c8f09f5147f182d0be68890161d31a6d0eb81f86e9e57b99b770adf2c799f`。
- 已完成：核对双方记录、纠正漏读007、当前主机观察、约定交接输入及串行建议并发出本请求。
- 待DSH回执：当前实际持有方及阶段3窗口是否安排/完成。
- 待阶段4就绪：最终准确RunId/源码与产物版本、G0/八类门禁和正式RAW平台集成。
- 本次文件属Codex项目总控自己的信箱例外。未改main STATE或任何阶段树，未进行main暂存/提交；请DSH核对后串行提交本记录及自身接收确认。
