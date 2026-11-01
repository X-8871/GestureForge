# 静止 CSR COMMAND 拒绝 BRESP 组合证据分析

## 条件性结论

**有条件可用组合证据关闭“静止矩阵各 COMMAND 拒绝都返回精确 SLVERR”这一项实现要求；SDK 对 R11 每笔事务的原始观察仍须保留 `UNKNOWN`，不得改写为直接观测到 SLVERR。** 现有依据没有显示不同静止拒绝分支使用不同 BRESP 产生器。该结论只针对精确 R04 CSR 实现和同一位流；不是 R11 实测结论，也不表示静止矩阵、G3/G4/G5 或阶段2B已通过。

## 规格原文

正式物理接口 `docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md` 第4.3节写明：

> COMMAND写在外层完成命令准入、参数快照/拒绝决定后才回B；B必须一直VALID至READY且数据/响应稳定。B OKAY只表示命令已接受，不表示推理成功。被拒绝命令返回SLVERR并更新LAST_REJECT；既有任务frame/epoch/所有权/首错/终态保持不变。

同节寄存器表定义 `0x008` 为 COMMAND；本段没有要求用 ARM 原生异常替代 AXI BRESP。

## 组合依据

- 当前 `src/s2b_control_csr.sv` SHA-256 为 `4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1`，与指定冻结 R04 源码 SHA 相同。
- RTL 中 `s_axi_bresp = q.bresp`；所有写从同一个 `write_commit` 入口处理。`0x008` COMMAND 分支中，非法编码、START 状态拒绝/epoch耗尽、非法 ABORT、ACK 状态或 epoch 不匹配分支都将 `d.bresp` 赋为同一常量 `SLVERR`（当前源码约第232–278行）。因此在同一已编译实现下，这些分支之间没有 BRESP 输出选择差异。
- 静止验收 helper 的 `reject_command(...)` 对每个命令拒绝场景调用 `write(0x008, command, reject="SLVERR", allow_unresolved_bresp=True)`；随后的 CSR 快照检查允许约定的 `LAST_REJECT` 变化，并核验其他字段不变（`verification/s2b_csr_board_acceptance.py` 约第265–303行）。R11 需真实完成这些场景的前态、拒绝原因与逐项副作用检查。
- 合法的 8参数 START 不属于拒绝命令：它走 START 接受分支，B 默认值为 OKAY，接受后若参数准入失败则进入 ERROR_SAFE，随后 ACK。不得为满足 SLVERR 项而把这类合法命令重分类成被拒绝事务。
- R04 构建记录绑定 CSR 源 SHA；R04 独立构建摘要记录 Vivado job PASS、独立 bit SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`、XSA 内嵌 bit 一致。原生 CPU 试验 `cpu_bresp_gp0_board_20261019_r01/jtag_result.json` 绑定同一 CSR SHA、R04 bit SHA及 XSA SHA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。
- `cpu_bresp_gp0_postmortem_independent_review_20261019_r01/review_outcome.json` 对保存的64字诊断邮箱独立复算，得到 DFSR FS=8、WnR=1、ExT=1、DFAR=`0x43C00008`、故障 PC=`0xC344`、opcode=`0xE5801000`（STR），并将唯一的忙 START 写分类为 SLVERR。它提供相同 GP0 COMMAND 地址和同一实现的原生 CPU 端代表性证据；它不是静止矩阵逐案观测。原始 CPU launcher 仍为 FAILED（XSDB `con --block` 超时），审查范围只认可后验只读分类，不改变该运行状态。
- 既有 R08 实板 `real_busy_start_response_last_reject` 在真正 RUN 时对 COMMAND 发起忙 START，记录精确地址 `0x43C00008` 的 AHB AP transaction error、`LAST_REJECT` 与状态对账；`busy_result.json` 明确将 `native_response` 保留为 `UNKNOWN`，原 CSR recovery 结果因此 FAILED/BRESP_UNRESOLVED。它证明忙拒绝实际发生及诊断副作用，**不单独证明**原生 BRESP=SLVERR；SLVERR 的代表性原生分类来自上述 CPU 后验独审。
- R08 冻结 RTL 的独立 XSim 证据 `report/evidence/S2B-T11/control_r18_independent_20261016_r08/independent_review_receipt.json` 绑定相同 CSR SHA，PASS 范围含146 directed、128 random、25 integration、6362 cycles。它支持 RTL 版本/验证覆盖背景，不是 BRESP 实物证据。

## 关闭所依赖的条件与限制

1. R11 实际矩阵必须逐项证明每个 `reject_command` 的目标命令确实被拒绝、`LAST_REJECT` 正确且其他 CSR 字段按规格保持；所有此类写均为 COMMAND offset `0x008`。若场景输入/前态不符、写失败或出现额外副作用，不能以组合推论关闭该项。
2. R11 使用的 bit/XSA 必须仍与上述 R04 bit/XSA、CSR 源 SHA 闭包一致。若换了 CSR 实现、bit 或响应路径，现有 native 代表样本不能外推，需按变化重新论证。
3. 保持 R11 原始 `observed_bresp=NOT_OBSERVED` / SDK `UNKNOWN` 记录和失败/阻塞原文不变；若验收层采用组合推论，应另行记录为“由冻结实现分支与同地址原生代表样本推论 SLVERR”，不可伪装成每笔原生 BRESP 读数。
4. R04 的原 `input_record.json` 顶层状态是 FAIL，原因记录为 stdout profile marker 未被 Vivado 日志捕获；独立构建摘要转录报告实际 Vivado job PASS且嵌入 XSA bit 与 standalone bit 一致。该摘要标记为总控转录而非Reviewer原始签名。此处依赖这些有界构建记录与 CPU 输入绑定，不把该顶层 FAIL 改写为 PASS。

在上述条件满足时，没有必要要求每个 COMMAND 拒绝各自再做一次 CPU 原生故障分类：所有被拒绝场景共用同一个 COMMAND 写响应产生逻辑，原生样本负责证明该已绑定 GP0 实现的同地址 SLVERR 映射。若 R11 发现有场景绕过此公共 COMMAND 分支或使用不同硬件实现，则该场景不能组合关闭，应明确保留阻断。

## 状态声明

R11 尚未运行。本文件只判断既有固定证据是否足以支持组合推论，不声称 R11 矩阵通过、BRESP 已从 SDK 逐笔读取或阶段验收完成。未访问板卡、未运行 Vitis/XSDB、未修改源码/STATE/HEAD，未运行测试。
