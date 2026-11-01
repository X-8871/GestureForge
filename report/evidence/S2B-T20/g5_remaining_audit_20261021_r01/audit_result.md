# 2B 剩余 G4/G5 独立只读核查

日期：2026-10-21（南京时间，UTC+8）  
核查基线：`bca323b1750caee783af5552c00769fd584fc1a6`  
范围：复核 `final_acceptance_matrix_20261019_r01` 后的相关证据、DDR 256B 探针及恢复包重建记录；不操作硬件、不运行测试、不改业务代码或 STATE。**阶段仍 NOT ACCEPTED；本文件不构成 G4/G5 通过回执，也不修改旧矩阵或运行状态。**

## 旧矩阵结论与新证据增量

- 数量证据仍成立：108 个有 ACK 闭合且覆盖充分的黄金样本，加 1000 个连续任务满足数量门槛；R02 第 109 个样本最后 ACK 缺动态读回，继续单列，不补写为已证明。证据：`S2B-T18/formal_model_result_review_20261019_r01/scope_analysis.json`。
- R08 真实 `RUN+AXI_PENDING` 下 ABORT→ERROR_SAFE/排空→显式 ACK→sample000 黄金恢复证据有效；R08 总运行仍失败，静止矩阵遇 UNKNOWN 后按 fail-stop 停止。不得将局部证据改写为 R08 全通过。
- 原生 BRESP 有一项后来补强：`cpu_bresp_gp0_postmortem_20261019_r01/postmortem.json` 的 64-word 保存快照满足 SLVERR 分类谓词（DFSR FS=8、外部同步写异常、DFAR `0x43C00008`、PC/opcode 对应忙 START；`LAST_REJECT 0→1`，epoch 6 / frame 0 不变）。独审 `cpu_bresp_gp0_postmortem_independent_review_20261019_r01/review_outcome.json` 为 `PASS_POSTMORTEM_CLASSIFICATION_ONLY`。这可作为**该次忙 START 的原生 SLVERR 事后分类证据**；原运行 `cpu_bresp_gp0_board_20261019_r01` 仍是 `FAILED`、native exit 2（XSDB `con --block` 超时），不是端到端运行 PASS。它不覆盖静止非法参数各案。
- R10 于 10 月 19 日中断，原记录缺最终结果；10 月 20 日只读 observer R02 见 CPU0/1 停止、CSR status `0xE04`（DONE_SAFE）、epoch 2 / frame 1、AXI progress 0，记录状态仍为 `OBSERVATIONS_SAVED_NOT_ACCEPTANCE`。10 月 21 日 observer R02 再次尝试失败于 `CPU1未停止`，没有可用 PC/CSR 终态。两者都不是 R10 期限验收或可继续执行的授权/证明；任何恢复前须按当前真实硬件会话读 SAFE/owner/pending/ledger，并遵循独占会话规则。
- 仍未闭合的最小实板项：正常期限 profile 的受控终态记录与 CORE/DRAIN 配置依据、静止非法命令矩阵剩余场景的原生响应及逐项状态/epoch 无副作用证据。`csr_deadline_review_20261019_r03` 是离线代码审查（129 项回归），不能代替实板期限运行。禁止要求在未决事务时用 FCLK reset/POR/cold reset 清账；T11 RTL 晚排空/永久隔离模拟和 R08 实板 pending ABORT 各按原层级计证据。

## 恢复包 ELF 的确切身份及单样本后续入口

重建包 R02 的机器结果 `S2B-T15/recovery_inputs_20261019_r02/machine_result.json`、逐 PT_LOAD 比对 `comparison.json` 及审查回执绑定以下重建文件：

- 绝对路径：`D:\FPGA_Competition\w2b\tmp\2B\S2B-T15\recovery_inputs_20261019_r02\attempt_03\fresh_build\infer\infer.elf`
- SHA-256：`f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9`
- ELF entry：十进制 `1048576`，即 `0x00100000`；与原 R04 ELF entry 相同。
- 核对结论限度：两个 ELF 的 PT_LOAD 布局及加载 payload（归一化 GNU build-id note 后）逐字节相同；整体文件 SHA 不同，重建物不能冒充旧 R04 ELF。原应用身份仍是 `...qualification_r04_xsa_rebuild_20261016_r04_artifacts\infer.elf`，SHA `a51499895e9387a74db87a3267843b9fbf7fdfa8b6646fcbc5db01485e090bf8`。恢复包本身 SHA `50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436`。

只读本次发现该精确重建路径存在，`sha256sum` 与上述 SHA 相符。后续若把该 ELF 用于板上运行，**不可覆盖旧 R04 文件、旧运行目录或旧回执**：在新鲜、唯一的 T18/T20 运行目录保存一份字节相同副本并记录 SHA/ELF entry；从原 R08/R10 同一冻结接口配置派生新 config，仅把 `bindings.app_elf.path` 和 `sha256` 改为该新副本，保留并复核 bit/XSA、CSR/transport、接口、模型/权重/黄金输入与复入依据绑定；新清单明确 `recovery_bundle.zip` SHA 和“PS 应用重建 ELF”。这会产生新的运行身份，不继承旧的成功结果。

随后仅在已核实 CPU 状态和 CSR 为安全终态、owner=PS、pending/ledger 清空、硬件会话身份归属明确之后，按正式入口运行单样本 scope：

```powershell
D:\Xilinx\2026.1\Vitis\bin\vitis.bat -s D:\FPGA_Competition\w2b\vitis\run_s2b_model_acceptance.py --config D:\FPGA_Competition\w2b\report\evidence\S2B-T20\<新唯一运行目录>\input_config.json --scope csr
```

新 config 应复用已审 runner 的 formal CSR seed/sample000 输入与黄金绑定（R08 旧结果仅供核对，不可复用旧 RunId）；在运行结果里明确只执行 1 个黄金样本。关账证据至少包含新 ELF SHA/entry 与源/平台绑定、权重装载、sample000 双头整数张量与框黄金比较、真实 DONE_SAFE、ACK 后 IDLE/epoch 变化和 pending/ledger 清零、CPU/session/映射清理结果，以及命令与退出码。若初始 CSR 不满足新鲜安全门、CPU1 停止条件不满足、或服务/会话身份不一致，立即停止，不发 START/ACK/reset，也不把等待时间当成安全证明。此处给出的是后续运行入口和验收条件，本审计未执行它。

## DDR 256B 探针：可接受范围

- 原始探针 `S2B-T19/cache_probe_execution_20261017_r02/visibility_probe_result.json` 确有两个 phase、从 `0x10000000` 起始的 256B 数据匹配结果与相应 UART/JTAG 原始记录，native exit 0；但原 status 保持 `API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING`、`cold_lifecycle_proven=false`、`owned_hw_server_released=false`。
- `current_probe_independent_20261017_r02/reviewer_outcome.json` 独审范围仅为 visibility0 探针的 owned `hw_server` 释放附件与身份绑定，并明确未升级原执行状态，也不声称 DDR/HP0/G3/G4/G5。另一个旧回执 `cache_probe_acceptance_20261015_r01/limited_scope_acceptance_receipt.json` 虽接受 CPU0/DAP 的 256B 限定观察封包，但注明 LOAD/START=0、数据路径未经过 PL/HP0，且其基线/RunId 为旧 worktree 的 `d49f9b8...` / `cache_probe_execution_20261015_r01`；它不能替 10 月 17 日原件补独审。
- 因此可以把已保存数据表述为“特定旧 artifact 身份下的 256B 两阶段探针观察”；现有独审不能支持“已独立验收 cross-master/HP0”，更不能推广成 32 MiB DDR arena、实装 DDR 料号、PCB 修订/走线绑定或完整阶段验收。旧 probe 与当前 HEAD/平台/器件身份绑定不完整；若需要将这项作为正式验收证据，Reviewer 必须直接核对旧 RunId 的完整原始 UART/JTAG 记录、输入与 bit/XSA/源码绑定、探针实际主从路径、结果摘要、执行状态及冷生命周期限制，并明确只给 256B 限定范围 verdict。不能重写旧身份为当前 `bca323b...`。

## 最小后续清单 / 依赖 / 阻碍

1. **受控恢复及应用 ELF 新身份**：需新 RunId、新 deployment config、保留原包 SHA 和副本 SHA/entry；先检查当前 CPU/CSR/账本安全状态。依赖会话所有者确认及当前状态读回。R10 10 月 21 日只读 observer 失败，不能从旧观测推断当前安全。
2. **单样本黄金与 ACK 闭环**：复用现有正式 runner（上列精确命令入口），只跑 sample000，验证双头/框黄金、DONE_SAFE、显式 ACK→IDLE/epoch、账本清空及完整清理。该结果只闭合所用重建 ELF 的 PS app 单样本 G3 证据。
3. **正常 deadline profile**：用已审核 `with_deadlines` profile、解释有依据的非零 CORE/DRAIN 值；保存完整 START→DONE_SAFE 区间、时钟基准与保守上界及余量，精确 PL cycles 无来源时标 `NOT_MEASURED`。不得把旧 R10 的 UINT32 最大超时或 observer 读回解释为期限通过。
4. **静止非法命令矩阵**：从真实安全 IDLE 基线逐项运行未执行项；每项须有底层可核的原生 SLVERR、`LAST_REJECT` 和状态/epoch 不变，发生未知响应立即 fail-stop。R01 保存快照只支持其忙 START 事件，不等价于静止非法写矩阵全覆盖。
5. **DDR 限定项**：先对旧 R02 原始数据做独立只读审查，决定能否将 256B 作为“limited observation”接受；不能作为 HP0/整块 DDR/物理料号验收。料号仍只按用户授权的手册候选表述，安装器件和 PCB 对应关系无独立证据。
6. 完成上述适用任务后，另做 G4/G5 依赖矩阵与恢复包/产物清单核验、最终审查及冻结；当前仍有阻断项，**本审计不作阶段通过判断**。

## 核查命令和边界

- 已只读核验基线：`git rev-parse HEAD` → `bca323b1750caee783af5552c00769fd584fc1a6`。工作树存在多组既有未跟踪证据目录；未触碰。
- 已核验 ELF 路径及散列：`sha256sum tmp/2B/S2B-T15/recovery_inputs_20261019_r02/attempt_03/fresh_build/infer/infer.elf` → 上述 SHA；entry 与布局来自 `recovery_inputs_20261019_r02/comparison.json`。
- 只读文件范围包括 `final_acceptance_matrix_20261019_r01/{audit_result.json,g4_g5_matrix.md}`、指定 R08/R10 observer 与 BRESP postmortem、recovery R02、T19 DDR probe/review、`csr_deadline_review_20261019_r03`。没有访问板卡、XSDB、JTAG、UART，没有执行测试或硬件命令，没有修改旧证据/业务/STATE。
