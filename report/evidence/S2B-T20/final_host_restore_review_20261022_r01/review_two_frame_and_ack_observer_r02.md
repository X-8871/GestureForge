# 双帧选择与 ACK 只读观察器 G2 增量审查 R02

- 结论：**PASS**
- 基线 HEAD：`d569dfbbdbe1c75b552300dedcc6d544e9d38908`
- observer：`tmp/2B/observe_rebuilt_r02_ack_20261022.py`
- observer SHA-256：`6bb8538dcf072628857459498009ff118d0192bfb1627d5bfa7a4e7209f9198c`
- 双帧业务文件未变，SHA-256：`171d83cab7d8b41d0fe999c9b27585b2789207453d73814095d86dd17ab075de`
- observer AST 静态解析通过。R01 已运行的 15 项业务回归仍适用于未变化的双帧业务文件；本轮不重跑测试。

## R01 阻断项关闭

1. observer 现在逐项重新哈希 parent `raw_logs` 的实际文件，并要求样本结果和 `uart_rx_raw.bin` 都在原始输出清单内；只有哈希一致才继续。结合样本状态、weights seq3/epoch0、模型 seq4/epoch1、最终 epoch/sequence 和冻结 ELF SHA，原运行数据漂移会在创建 observer Run 前被拒绝。
2. 新建 SDK session 前要求 parent 仅有预期的 `controller.close` 清理错误，并核实 serial、RX/TX 文件、CSR map、session、XSDB、journal 七项原资源关闭步骤均 PASS；其他资源泄漏或清理异常会被门禁拒绝。
3. observer `journal.close()` 异常现在会加入 `cleanup_errors`，并继续尝试写 `observer_result.json`。

## 现场边界

代码路径只对必要的 Running CPU 发 stop、要求双核 Stopped、注册临时 CSR debug map、读取稳定 CSR 并核验 safe IDLE/epoch 1/账本零，再清除映射并关闭新建资源。未见 UART 发送、CSR 写入、system reset 或部署调用。本结论仅为代码 G2；没有执行 observer 或验证实板状态，不代表 G3/G4/G5。
