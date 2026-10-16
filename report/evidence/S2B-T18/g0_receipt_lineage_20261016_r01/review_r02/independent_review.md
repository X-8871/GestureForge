# S2B-T18 CSR scope R02 独立审查

结论：PASS（仅限本次固定源码差异的静态实现审查及轻量自动检查；不代表Vivado、实板、G3/G4/G5通过）。

## 固定版本

- 工作树：`D:\FPGA_Competition\w2b`
- HEAD：`6448ba4e1bfbab5275741fd55184cdfb588c4fc9`
- `vitis/run_s2b_model_acceptance.py`：`ad24b68b5ab19c680e0c2af51df8186be25d49c1731eff24e0b7076f58abd7ba`
- `verification/test_s2b_model_acceptance_runner.py`：`6ce6d47b48358e937993f7d37cf7b293bce0244f05803a43244192c8fd1264fc`
- `verification/s2b_csr_acceptance_flow.py`：`136b7bf5831363080ac1224fbe32c07c7dac001b63ad59198de098688cf6046b`
- `verification/test_s2b_csr_acceptance_flow.py`：`1bc9c8dc9fa7d869d93140fc9bdc32947eebf9e5354a8abe1d49b35cb7ae7942`

## 审查范围与结论依据

- 核实原阻断：CSR流程异常时记录原异常表示与traceback，扫描本次已创建的T20运行目录并以SHA-256绑定输出；创建`FAILED_CSR_RECOVERY_SCOPE_ONLY`结果及失败检查清单。上层runner将该失败结果附着到异常，写入顶层`acceptance`，由最终证据封装器继续绑定T20输出。
- 检查异常仍失败关闭：runner只接受`PASS_CSR_RECOVERY_SCOPE_ONLY`继续返回；失败结果被包装为`RunnerError`后进入既有失败锁存路径，未见自动恢复或把失败映射为PASS。
- 检查新增BusyObserver中途异常注入：测试核验保留原错误、生成失败结果和delivery manifest，并确认`busy_result.json`的实际SHA同时出现在flow结果与manifest中。
- 核对既有流程顺序、模型scope默认值、CSR scope显式选择、banner前置消费及CSR helper源码SHA固定逻辑。之前审查发现的scope工作流顺序测试仍适用。

## 验证

- 命令：`C:\Users\22061\.local\bin\python3.11.exe -m unittest verification.test_s2b_model_acceptance_runner verification.test_s2b_csr_acceptance_flow`
- 结果：34 tests，exit 0，全部通过。
- 命令：`git diff --check`
- 结果：exit 0。
- 四个被审文件的SHA-256与本审查固定版本一致；未启动Vivado/硬件，未修改被审文件，未提交。

## 限制

- 中途失败验证使用隔离fake helper注入，不是板上运行结果。
- 未做完整项目回归、RTL动态仿真或硬件验收；本PASS不关闭109样本、1000次压力、实板负例或2B阶段验收。
