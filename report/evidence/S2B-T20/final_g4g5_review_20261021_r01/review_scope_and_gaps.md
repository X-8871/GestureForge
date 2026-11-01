# 阶段2B G4/G5 验收范围与缺项清单（初稿）

日期：2026-10-21（南京时间，UTC+8）  
状态：**初稿；尚未形成最终 G4/G5 verdict。阶段保持 NOT ACCEPTED。**  
用途：在当前已保存证据上圈定正式验收范围与待补项；后续只按新 RunId 追加实际结果，不改写历史状态。本文件不授权或执行硬件操作。

## 核查范围与基线

直接核对了阶段计划“阶段2B：固定输入上板”及物理接口候选 `s2b-physical/1.0.0` 的 deadline/恢复条款、已有 G4/G5 矩阵和 G5 剩余审计、BRESP 组合分析与其独立 postmortem 回执、重建 app 的最终 G2 回执，以及 R11 的顶层/子流程结果、部署绑定、事件摘要和错误记录。

本轮观察到工作树 HEAD `3b753853f6d066b6f6a2a6fe23c27644d6aff0e0`，但 R11 运行自身声明 `source_commit=914b30a42ca39be5635140907efb5405132a4441`。R11 实际绑定旧 PS app ELF `a5149989…090bf8`、R04 init ELF、XSA `ea52da1b…0eb6` 和 bit `555a70c2…1047ef7`；不得把工作树当前 HEAD 或后续重建 app 冒充为该次运行身份。

## 按正式要求归位的已具备证据

| 正式验收项 | 可计证据 | 本次范围结论 |
|---|---|---|
| 至少100个覆盖规定类别的黄金样本 | `S2B-T18/formal_model_result_review_20261019_r01/scope_analysis.json`：corpus index 0–107 共108个样本有后续成功任务证明前一匹配 ACK；覆盖五类、无手、多框、边界、空框和小框。原 R02 对109个输出比较匹配，但 index 108 / seq111 / frame1108 / epoch1109 缺运行结束前动态 ACK/IDLE 读回。 | **数量及覆盖门槛已满足：108 个闭环样本。** 不声称109个样本均有动态 ACK 证据；缺失的 index108 不影响100样本最低数量结论。 |
| 至少1000次连续任务无丢失、重复或死锁 | 同一 `scope_analysis.json`：stress indices 0–999、epoch 1–1000 闭合；原模型运行 `PASS_MODEL_CORPUS_AND_STRESS_ONLY`、native exit 0。 | **数量门槛已满足：1000次闭合。** 该结果只计入正式定义的连续任务数量，不替代独立接口/部署验收。 |
| 布局后时序与位流身份 | R04 路由报告：WNS +0.156 ns、WHS +0.078 ns、TNS/THS 0，DRC 无相关违规；bit SHA `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`。 | **限 R04 实现及绑定证据 PASS。** 保留其 `input_record.json` 顶层因 stdout marker 缺失而为 FAIL 的包装记录；不得扩展为当前 PS 重建或其他平台身份的验证。 |
| R08 pending 中 ABORT/排空恢复 | R08 在 RUN+AXI_PENDING 下 ABORT，后续 ERROR_SAFE/TERMINAL/SAFE_TO_REUSE、owner归PS、pending清零、error=8；显式ACK后 sample000 黄金恢复成功。 | **局部实板恢复证据成立。** 不等于 R08 全流程 PASS，也未观察到超过 DRAIN 观察期限才到达的晚响应。 |
| 旧 app 的 sample000 运行 | R11 子结果 `PASS_SAMPLE000_SEED_ONLY`，阶段资料指向已有真实 sample000 结果。 | **仅计该样本和其对应运行身份。** 它不是新重建 app 的板上证明，不能复用为后续 ELF 的 G3 结果。 |

以上数量门槛不会因其他测试失败而消失；反之，也不会单独使阶段 G4/G5 通过。

## R08、R11 与 BRESP 的精确状态

### R08

R08 ABORT/恢复和 sample000 闭环可分别按其子回执计入。R08 顶层 `FAILED_CSR_RECOVERY_SCOPE_ONLY`、native/launcher exit 2；静止非法矩阵第一项 `idle_bad_encoding` 的 SDK 原生响应 UNKNOWN 后按 fail-stop 停止，后续项未执行，controller.close 也记录清理错误。不得把这些局部成功合并成 R08 全通过。

### R11

- 顶层 `formal_csr_recovery_20261021_r11/orchestrator_result.json` 为 **FAILED**；scope `csr`，source commit `914b30a…`。R11 部署绑定的是旧 app ELF `a5149989…090bf8` 和 R04 XSA/bit，不是 PS 重建 ELF。
- 子流程 `maximum_deadline_start_measurement` 保存 **PASS_DONE_SAFE_MEASURED_ACKED**：START 至 DONE_SAFE 的 host wall 时间上界为 `47.4017962 s`，950次观察，frame 1 / epoch 2，随后 ACK 回 IDLE。配置的 `0xFFFFFFFF` timeout 下限/上限试验中，该次 wall 时间乘绑定 HWH 配置时钟50 MHz得 `2,370,089,810` cycles；额外乘1.25的比较满足32-bit上限。该证据是**该 R04 位流、该任务和该观察窗口的 host-wall 估算上界**；HWH/PS init 配置50 MHz并非本次实际FCLK实测。结果的 `golden_comparison=NOT_APPLICABLE_TO_DIRECT_DAP_START`，所以它不是黄金 app 路径证明，也不是精确 PL cycle 测量。
- 子流程 `core_timeout_code5_safe_ack` 的场景结果为 **PASS**：实际 CORE timeout / code 5 到达安全终态并匹配 ACK。场景说明明确旧 UART 与 DAP epoch 无同步入口，`hot_golden_recovery=BLOCKED`；不得解读为 CORE timeout 后黄金 app 已恢复。
- deadline 流程整体 `FAILED_CSR_DEADLINE_FLOW`，异常为 `FileExistsError`：尝试以独占新建方式保存已存在的 `deadline_epoch_causality.json`。顶层还记有 `controller.close` 清理失败。故以上子项不改变 R11 整体 FAILED 状态。
- R11 `core_timeout`、`drain_timeout` 绑定均为 `0xFFFFFFFF`。这满足有限观察实验的非零边界，但不是已经论证和选定的最终部署 deadline。正式物理接口要求量化完整38层请求、实际HP延迟/背压及计算周期依据，并证明正常总周期加余量不超过32-bit，同时记录最终部署值；wall-time换算只能标成保守估算，不冒充PL周期。DRAIN 观测期限也须有依据，不能据此宣称任意晚响应都会在有限期限内到达。

### BRESP 组合条件

现有 `bresp_composition_review_20261021_r01/analysis.md` 是**有条件**组合论证：冻结 R04 CSR 源中 COMMAND 的各拒绝分支共用响应产生路径并赋 SLVERR；同地址 busy START 的 CPU postmortem 独审从保存异常邮箱分类为 SLVERR。但原 R01 launcher 仍是 FAILED（XSDB `con --block` 超时），其 postmortem 回执仅 `PASS_POSTMORTEM_CLASSIFICATION_ONLY`；R08 SDK 的 `AHB AP transaction error` 仍记录为 UNKNOWN，不能改写成逐笔原生读数。

组合论证只在以下条件同时满足时可用于静止矩阵的实现级 BRESP 结论：R11 的每个场景确实执行预期 COMMAND 拒绝分支；`LAST_REJECT` 与其他 CSR 状态/epoch 无副作用逐项核对；R11 的 CSR 源、bit/XSA 仍与组合审查所绑定的 R04 实现相同；并且报告保留每笔 SDK 原观察 UNKNOWN，将 SLVERR 标为“共用 RTL 路径 + 同地址原生代表样本的组合推论”。如果任何场景未执行、前态不符或走不同响应路径，该项继续缺证；不能伪称每笔 SDK 直接观测到了 SLVERR。

本次所核材料未提供 R11 静止非法命令矩阵完整通过证据。R08 在首项 UNKNOWN 后已停止，R11 deadline 子流程不是该矩阵的替代物。还需在正式修复后的新运行中完成未执行矩阵项目，按上述组合条件逐项审查副作用及分支身份。

## PS app 重建与 R04 平台边界

恢复包隔离重建的 `infer.elf` SHA 为 `f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9`，entry `0x00100000`。比对证据称 PT_LOAD 布局与加载 payload（归一化 GNU build-id note 后）逐字节一致于旧 R04 app，但整个 ELF SHA 不同；包 SHA `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`。`rebuilt_app_scope_review_20261021_r01/review_final.md` 对指定脚本和测试给 **G2 PASS（代码审查范围）**，不代表板测。

R11 仍运行旧 app ELF；G2PASS 的新 runner/acceptance scope 仍须以新 RunId 和该 ELF 新 SHA/entry 绑定，执行后独立核对实板 sample000 双头张量与框黄金、DONE_SAFE、显式 ACK→IDLE/epoch、账本清零以及 CPU/session/map 清理。该单样本结果只覆盖重建 PS app 的这条执行路径，不会自动补齐100样本/1000连续任务、静止拒绝矩阵或 deadline 正式部署依据。

现有隔离重建包证明 PS 应用输入编译/链接与 ELF payload 比对范围；没有证明 BSP 全量重建、XSA/PL/bitstream 重建或完整平台干净环境复现。R04 bit/XSA 的时序和平台证据应保留原 SHA、原范围；不得把 PS ELF 重建称为 R04 平台重建，也不得把 R04 结果重命名成新 ELF 的板上结果。

## 当前最小剩余项

以下清单按正式阶段计划和冻结接口现有要求列出，不添加32 MiB全DDR扫描、板端未决事务注入、精确PL周期等无依据的新门槛。

1. **R11 正式结果收尾**：以已修复的重复保存/结果落盘路径新 RunId 运行正式 CSR 流程；保留旧 R11 FAILED 原件，不覆盖重跑。核对完整顶层结果和清理错误状态。
2. **静止非法 COMMAND 拒绝矩阵**：完成 R08 未执行项及正式矩阵其余场景；逐项验证前态、拒绝原因、`LAST_REJECT`、状态/epoch等不变。按上节条件采用明确标识的 BRESP 组合推论，或保留未观察项为阻断；遇 UNKNOWN 按既有 fail-stop 停止，不对未知场景外推。
3. **新 PS ELF 实板单样本**：使用 G2PASS scope、全新运行身份和恢复 ELF SHA/entry；绑定同一明确 R04 init/XSA/bit 与模型/权重/黄金数据；证明 sample000 黄金、终态、ACK及清理。只计此 ELF/此 scope。
4. **最终正常期限配置与依据**：按正式冻结接口说明完整请求/延迟/背压/计算依据、非零最终 CORE/DRAIN 值及 margin；若没有精确 PL cycle CSR，仍标 `NOT_MEASURED`，可提供已明确界定的保守 host-wall 周期上界。R11 的最大值 `0xFFFFFFFF` 探索观察和 10,000-cycle CORE timeout 故障场景都不替代最终配置论证。无需为关闭该项另造测试，只做规范要求的完整定量和受控终态证据。
5. **DDR 前置限定证据**：10月17日旧 R02 的 `ddr_prior_probe_review_20261021_r01/review.md` 已给**限定范围 PASS**：旧 visibility0 平台上，`0x10000000` 起256B，CPU flush→DAP读与DAP写→CPU invalidate/读两个方向，各用独立 seed、64 words、零不匹配；原运行状态仍是 `API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`、`cold_lifecycle_proven=false`。据此仅有限 CPU↔DAP 前置观察已独立核实。它不覆盖 HP0、完整 DDR 容量、实装料号/PCB关系或当前 R04 平台。若当前重建 app 的 R04 验收依赖其平台自身的 DDR/cache 观察，则该观察须用 R04 平台和新 RunId 单独绑定；不拿旧 visibility0 结果代替。不得将10月15日旧 RunId或阶段3/其他板卡证据代用。
6. **G4/G5 冻结包核对**：前项完成后，核对最终代码/RTL、R04平台身份、PS app身份、模型/输入/黄金、工具和部署清单彼此一致，失败与限制仍可追溯，并核对恢复入口。若所需交付明确声称完整平台可重建，则需补齐对应 BSP/XSA/PL/bit 构建来源及复现证据；现有 PS 单独重建不足以支持该声明。

已满足的1000任务与108闭合黄金数量门槛、R04时序，以及R08真实pending ABORT分别按各自边界保持有效，不因以上待办而重复要求重跑；它们也不覆盖其余阻断项。

## 证据入口与限制

- 正式要求：`docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` §阶段2B；`docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md` §deadline与下游待关闭项。
- 对照基线：`report/evidence/S2B-T20/final_acceptance_matrix_20261019_r01/g4_g5_matrix.md`；`report/evidence/S2B-T20/g5_remaining_audit_20261021_r01/audit_result.md`。
- R11：`report/evidence/S2B-T18/formal_csr_recovery_20261021_r11/orchestrator_result.json`、`deadline_scope/acceptance_result.json` 和同目录绑定配置；子结果在 `report/evidence/S2B-T20/formal_csr_recovery_20261021_r11_csr_{deadline_max_start_measurement,deadline_core_timeout,seed_sample000}/`。
- BRESP：`report/evidence/S2B-T20/bresp_composition_review_20261021_r01/analysis.md`；`cpu_bresp_gp0_postmortem_independent_review_20261019_r01/review_outcome.json`。
- 新 PS app G2：`report/evidence/S2B-T20/rebuilt_app_scope_review_20261021_r01/review_final.md`；恢复 ELF 比对与恢复包见 `report/evidence/S2B-T15/recovery_inputs_20261019_r02/`。
- 限制：只读业务文档和已保存结果；没有访问硬件、运行测试、改写已有文件、修改源码/STATE/HEAD。本文件只整理当前范围，不是正式 `PASS`/`CHANGES_REQUIRED` 独审终值；待新 CSR 运行、重建 app 实测和 DDR 限定前置审查完成后再更新 verdict。
