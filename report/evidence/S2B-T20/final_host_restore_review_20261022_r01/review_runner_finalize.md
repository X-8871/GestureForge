# B：T18验收 runner 证据封装修复独立审查

- 结论：**PASS（仅离线代码及副本重放范围）**
- 被审 runner：`vitis/run_s2b_model_acceptance.py`，SHA-256 `45c7c0f86e8bc4e06721ed419ec6fc9d5ff1660e0d90797ca5ff806e402e4229`。
- 被审测试：`verification/test_s2b_model_acceptance_runner.py`，SHA-256 `e30e1713b3a70a0274e671940ca554b4523404397c66ae0d18990203ea429707`。
- 基线：HEAD `aef41a87d8e2724376b50b48365404e2dcf80c41`；本轮未提交文件差异仅以上runner和测试文件。
- 审查范围：新增G0接口声明生成、失败结果持久化/manifest SHA同步、完整差异和修复函数副本重放。无JTAG/UART/硬件调用。

## 核验结果

- 完整diff显示变更限于 `persist_failure_snapshot()`、`_delivery_interfaces()`、`finalize_evidence()` 中补接口字段，以及 `run()` 失败退出前写最终异常、退出码和trace并同步结果SHA。没有改变部署、CSR调度或身份语义。
- `_delivery_interfaces()` 从已绑定的G0回执取 `interface_versions`，并校验两份正式接口文档的路径/原字节SHA绑定，再输出 `physical` 与 `uart` 两项；适用manifest checker也会验证正式 `docs/` 路径、版本名、frozen布尔值和文档SHA。
- 失败快照先落盘最终runner错误和trace，再唯一更新或新增manifest结果项并fsync；重复结果路径声明会拒绝。快照同步失败会写入 `failure_snapshot_persist_error` 并尽力保留结果，未掩盖封包失败。
- 实际聚焦回归命令：

  `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest verification.test_s2b_model_acceptance_runner.ModelAcceptanceRunnerTests.test_finalize_manifest_binds_exact_g0_receipt_path_and_sha verification.test_s2b_model_acceptance_runner.ModelAcceptanceRunnerTests.test_failure_snapshot_persists_runner_trace_and_manifest_hash`

  退出码0；2项测试通过。
- r03失败诊断SHA为 `a9cdad5e5397e35ac012d1f833fc78f134223398743089eaae90d270d2edb676`，明确记录生产finalizer因缺 `interfaces` 失败；r05修复重放使用本次runner SHA，结果 `CHECKS_OK`。回放记录为无硬件访问，R12原始运行未改写；副本config仅重绑runner源码身份。r05结果SHA `67b89a2e483e9a7599989cab8f49c31a0be5bc7e397be6b08cf30536173c3dda`，report manifest SHA `c0c1a27b2091d48816062f27c296e00c76efdedd5d0bfcccb015e7c278ffe552`。
- r05 的CSR状态说明仍明确11类静止BRESP场景BLOCKED，部分busy/ABORT未运行，未伪称覆盖；manifest的 `CHECKS_OK` 仅代表证据包装核验。

## 限制

本审查与副本重放不代表硬件执行、G3实物验证、G4任务验收或G5阶段验收。原R12失败/封装证据没有被重写；后续运行结果需使用新的RunId并按阶段验收要求独立判断。
