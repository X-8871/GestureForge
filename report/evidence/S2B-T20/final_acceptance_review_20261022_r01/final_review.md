# 阶段2B最终 G4/G5 独立审查

- 结论：**PASS（G4、G5）**
- 审查基线：`16ce2cdf8c00c6214435629d75a5e4b63acb66a9`
- 范围文档：`docs/obsidian-project/04-提交材料/阶段验收/stage2b_fixed_input_acceptance_20261022.md`，SHA-256 `2345a741c9d05866def60c71681003dc96f9470347624e29db6eef4905a59bc6`
- 冻结候选：`report/evidence/S2B-T18/stage2b_freeze_20261022_r02/delivery_manifest.json`，SHA-256 `1efc124b7c6281e453ba8a9d518d33223068ab1818d958ed9938144868e1aa66`
- 范围清单：`report/evidence/S2B-T18/stage2b_freeze_20261022_r02/final_freeze_inventory.json`，SHA-256 `7ec952fe9d56b917414ff960374b2b99983de4fdbd87651a153ca2806edd25f6`
- 输入清单：`inputs_manifest.json` 共79项绑定；证据清单包括候选自身及其证据条目。冻结清单当前状态 `CANDIDATE_FINAL_FREEZE_INPUTS_BOUND_NOT_G4_G5_ACCEPTANCE`，本回执独立给出最终判定。

## 核查与判定依据

1. **固定输入数量与比对**：独立重核 `formal_model_result_review_20261019_r01/scope_analysis.json` 及既有审查结论。108个有 ACK 闭环的黄金样本达到正式计划至少100个门槛，覆盖五类、无手、多手和边界等场景；1000个连续任务满足数量和连续闭环要求。原109样本运行最后一个 ACK 缺动态读回，计数仍为108，不追溯补足。1109任务双头共28,113,150字节及检测框重放结果按其原范围保留。
2. **器件实现与时序**：R04 绑定 `xc7z020clg400-2`、50 MHz、bit `555a70c20ba1a345d3fc2e3dd45ad2d1653dbffbe12db06b2a7f4a2661047ef7`、XSA `ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6`。布局后 setup +0.156 ns、hold +0.078 ns、TNS/THS=0；满足阶段计划的时序门槛。结论限于这些绑定产物。
3. **R08 恢复**：实际 `RUN+AXI_PENDING=1 → ABORT → ERROR_SAFE/code8 → 匹配ACK → sample000黄金恢复` 子范围成立。R08 顶层 `FAILED` 及其他未完成静止矩阵状态原样保留；未声称整次 R08 通过、未决时强制复位或晚响应板测。
4. **R12 CSR、BRESP与期限**：采用 `csr_r12_finalize_replay_20261022_r05` 的生产函数隔离封装重放绑定，限于真实子范围和文件封装；原执行器最终退出码未捕获仍保留未知，不把封装重放说成新板测。静态矩阵8个合法但参数非法的 START 是 `OKAY` 后进入 code1/2/3 并 ACK；11个 COMMAND 拒绝保留逐笔 SDK `UNKNOWN`。仅在同一 R04 源/bit/XSA及路径前提下，采用共用 RTL SLVERR路径与同地址原生 CPU 代表 postmortem 的实现级组合推论，不表述为逐笔 SDK 读到 SLVERR。忙 START 由 R08 BusyObserver 单独支持。

   期限配置选 `CORE=DRAIN=0xFFFFFFFF`。R11/R12正常 START 到稳定 DONE_SAFE 的最大完整主机包络为47.4058308秒；按绑定的50 MHz配置换算并乘1.25余量为2,962,864,425名义周期，小于32-bit上限4,294,967,295。完整包络包含实际任务、HP响应/可能背压、控制和主机观察，不冒称精确 PL 周期或实测 FCLK。实际 CORE=10000/DRAIN最大值错误场景到 ERROR_SAFE、账本0并 ACK；DRAIN=1/code bit3 也有独立短测。未把 DRAIN=1 当最大值证明。该证据满足正式接口对正常包络、有限观察值和依据的要求；不保证未来任意DDR停顿或永久未完成事务必在期限内排空。期限后隔离、继续消费响应及永久未结束时保持隔离仍按接口语义。
5. **新重建 ELF 的板上子项**：实际 R02 绑定的新 ELF `f7a8bc96418590a497577bb45a7cbc0cc75dec416f6af1bf9b33ffd0308fa5a9`，R04 volatile 部署、两相256B cache、weights seq3/epoch0 和 sample000 seq4/epoch1 双头张量及检测框黄金通过。独立后续只读 observer 为 `PASS_POST_R02_ACK_IDLE_EPOCH1_LEDGER0`、exit0、`cleanup=[]`，读回安全 IDLE、epoch1、账本0且不发送 UART/CSR写入、不 reset、不发新模型任务，并哈希绑定原 raw logs 未变。原 R02 外层及内层仍为 `FAILED_CLEANUP` / `FAILED_REBUILT_APP_ACCEPTANCE`，包括 host 双帧计数断言和 controller cleanup 失败；修复提交及 G2回归不改写原运行结果。此组证据只关闭新 ELF 单样本部署/cache/恢复子范围。
6. **实物资料和恢复边界**：手册、AC7Z020 Rev1.0 原理图第7页及 R04 生成配置的页码/映射对应已核，手册内部 BANK/UART 标注矛盾保留；原理图仅支持设计电平选择，不证明实际 PCB 修订、装配料号或实测电压。DDR 按用户指定的 `MT41K256M16TW-107` 候选表述。恢复演练重建 PS ELF，复用 BSP 静态库；没有声称 BSP、XSA 或 PL 从源完整重建，亦未声称工业温度验证、全容量 DDR 扫描或全容量带宽保证。
7. **清单与可恢复入口**：独立重算技术文档、delivery manifest、inventory SHA 均与固定候选一致。两项只读交付检查均成功（下列命令各 exit 0、`CHECKS_OK`）；manifest绑定提交、接口、证据、结果与恢复依赖，README提供可定位恢复入口，并明确本地/归档二进制依赖及原始失败证据保留。清单检查只作完整性佐证，不单独充当 G4/G5。

## 执行的只读检查

```text
& 'C:\\Users\\22061\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' -B verification/check_stage_delivery.py --mode inputs --manifest report/evidence/S2B-T18/stage2b_freeze_20261022_r02/inputs_manifest.json
exit 0; CHECKS_OK; warnings=[]; errors=[]

& 'C:\\Users\\22061\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' -B verification/check_stage_delivery.py --mode evidence --manifest report/evidence/S2B-T18/stage2b_freeze_20261022_r02/delivery_manifest.json
exit 0; CHECKS_OK; warnings=[]; errors=[]
```

检查器明确提示其结果不代表 G0/G4/G5；G4/G5结论来自本独立审查。未操作硬件，未修改源代码、STATE、候选冻结包或既有失败证据。

## 判定范围与保留限制

按阶段计划§2B、R04绑定时序、108/1000数量门槛、R08/R12真实子范围、静止矩阵组合 BRESP 边界、完整期限包络及新 ELF 单样本闭环，适用任务验收条件已满足，故判定 **G4 PASS、G5 PASS**。阶段冻结候选与恢复/版本入口足以定位并恢复已声明交付范围；不将其扩大为干净环境下全平台从源码重建。

仍明确保留：109th最后ACK缺证；R08整体失败；R12原runner最终退出码未知、隔离重放非新板测；PS R02原运行整体失败但黄金与后续只读状态证据分别有效；11笔SDK BRESP均为UNKNOWN并仅接受有条件的组合推论；无实际PCB修订/装配器件/电压鉴定；BSP静态库复用、PL未从源码重建；无工业温度、全容量DDR扫描/带宽或任意未来背压最坏情况保证。上述限制已在验收记录中如实界定，未发现其构成正式阶段2B计划的未满足门槛。
