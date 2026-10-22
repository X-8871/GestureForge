# 双帧选择与 ACK 只读观察器 G2 审查 R01

- 结论：**CHANGES_REQUIRED**
- 基线 HEAD：`d569dfbbdbe1c75b552300dedcc6d544e9d38908`
- `verification/s2b_rebuilt_app_acceptance.py` SHA-256：`171d83cab7d8b41d0fe999c9b27585b2789207453d73814095d86dd17ab075de`
- `verification/test_s2b_rebuilt_app_acceptance.py` SHA-256：`b0de9b6458adb19eec44d62613caa61fec591a2e4aa9126f95dccd138c8709c5`
- `tmp/2B/observe_rebuilt_r02_ack_20261022.py` SHA-256：`2be1993d0ec6cd362b863b173218de8e1546eb3225c5f8c78629caca0469bce0`

## 核查结果

- `_select_sample000_frame` 要求权重 seq3/epoch0 恰有一帧、sample seq4/epoch1 恰有一帧且顺序正确，并核对 wire epoch/sequence。新增测试覆盖有效双帧、重复模型帧、倒序和错 epoch。
- 实际原始验收文件当前记录两帧 weights `(3, 0)`、rebuilt_app_sample000 `(4, 1)`，sample 状态 PASS、final epoch 1、sequence 4；原 orchestrator 状态为 `FAILED_CLEANUP`，唯一清理错误是 `controller.close`，其他 session.disconnect、xsdb.dispose、journal.close 等清理步骤均为 PASS。此处只读检查未接触设备。
- observer 调用配置校验和绑定文件核验，建立新的 XSDB session，读取两核状态/PC，对 Running 核调用 stop，要求双核 Stopped 后注册 CSR debug map、读取稳定 CSR、要求 safe IDLE、epoch 1、账本零；按 map clear、controller close、session disconnect、XSDB dispose 顺序清理。脚本未发现 UART 发送、CSR 写入、system reset 或重新部署调用。
- 指定离线回归：`python -B -m unittest verification.test_s2b_rebuilt_app_acceptance`，15 项通过（退出码 0）。未运行 observer 或其他硬件操作。

## 阻断项

1. **原始输出绑定只记录当前 SHA，没有与原运行结果交叉核对。** observer 的 `binding()` 重新计算当前 `acceptance_result.json` 与 `uart_rx_raw.bin` 的 SHA，但不与 parent `orchestrator_result.json` 的 `raw_logs` 条目比较。脚本因而可把事后改写的样本摘要/串口字节当作原运行证据绑定。当前 parent raw_logs 已包含这些文件的原始 SHA（样本结果为 `548f16b6a7f0cca3c7b8faace0fdfe1136742497987a2ba02cef6eae84af9952`）。应要求相关路径在 raw_logs 中唯一出现且 SHA 一致；并检查 parent source_commit 与配置一致。

2. **开始新 SDK 会话前没有限制旧运行的清理失败种类。** observer 只要求 parent 状态为 `FAILED_CLEANUP` 且内层 acceptance 为 `FAILED_REBUILT_APP_ACCEPTANCE`，未要求 `cleanup_errors` 仅含已知的 `controller.close` 错误，也未核对旧运行 `session.disconnect`、`xsdb.dispose`、`journal.close` 均成功。若旧运行留下 session/server 资源，observer 会继续新建 session。应在连接前核验这几项资源清理步骤均 PASS，且失败集合严格符合本次预期的 controller.close 单项。

3. **observer 的 journal.close 异常会跳过结果落盘。** `finally` 中该调用未捕获异常，异常会中断后续 `observer_result.json` 写入。应将该异常加入 `cleanup_errors`，仍尝试写出 FAILED 结果。

## 限制

审查没有执行 observer，也未确认板上当前状态或硬件会话可用性。上述离线测试只覆盖双帧选择逻辑，不覆盖 SDK observer 现场行为；修复后需新 SHA 复审。
