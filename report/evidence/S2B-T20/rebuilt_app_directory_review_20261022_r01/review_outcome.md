# S2B-G2 rebuilt app 样本目录修复独立审查

审查时间：2026-10-22（UTC+8）  
审查结论：**PASS**  
基线 HEAD：`6e66bfc553abbe2c2cedde47b49d060439928ef5`

## 被审版本

| 文件 | SHA-256 |
|---|---|
| `verification/s2b_rebuilt_app_acceptance.py` | `1e723058244ce8506796b073cc07db4aaa601b95d0ac3d64488bac2a99e39908` |
| `verification/test_s2b_rebuilt_app_acceptance.py` | `c4f7334850cf0bcbe71a719ba35a99629da06f334957a7127a1ed658645e017d` |

## 核查与依据

- `_create_sample_runner` 将未创建的 `run_dir / "sample000"` 传给真实 `model.AcceptanceRunner`。其构造器通过 `transport.new_directory(run)` 创建目录，并在其中以独占模式创建 `progress.jsonl`、`started.json`。调用方不再先行创建目录，消除了重复 `new_directory(sample000)` 的失败路径。
- `execute` 紧接着将 `sample_dir` 设为 `acceptance_runner.run`。余下两处 `sample_dir` 用途分别读取 `acceptance_result.json` 并写入 `sample000_tx_payload_raw.bin`，路径均指向 runner 实际创建的目录。异常收尾调用同一 runner 的 `finish`，证据汇总也从既有 deployment 根递归收集；没有遗漏旧 `sample_dir` 变量依赖。
- 新测试以真实 `AcceptanceRunner` 和 `TemporaryDirectory` 验证单次目录创建、runner 实际路径、`started.json` 及 wire receipt 配置；测试使用临时目录，finally 关闭日志。
- wrapper `vitis/run_s2b_rebuilt_app_acceptance.py` 未修改。现有 wrapper dispatch 测试验证正向 RunId/deployment 路径仍将真实 controller/wire 及参数送入 `execute`；另有 execute 目录门禁测试在首次硬件门前停止，未操作硬件。
- 仅审阅指定的两份待审差异及其直接依赖的 `AcceptanceRunner` 构造/收尾路径；未改业务源码、STATE、HEAD，未运行硬件流程。

## 验证

命令：`python.exe -B -m unittest verification.test_s2b_rebuilt_app_acceptance`  
结果：`Ran 10 tests ... OK`，退出码 `0`。  
差异格式检查：`git diff --check -- verification/s2b_rebuilt_app_acceptance.py verification/test_s2b_rebuilt_app_acceptance.py`，退出码 `0`。

本结论仅针对上述文件哈希的 G2 代码修复与聚焦测试，不代表 G3/G4/G5 或硬件验收结果。
