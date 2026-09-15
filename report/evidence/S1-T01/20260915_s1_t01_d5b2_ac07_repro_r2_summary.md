# S1-T01-D5B2-AC07-REPRO-R2 版本绑定复核摘要

## 结论

本 r2 证据是“基于已完成 r1 全量运行产物的版本绑定重生成/只读复核”，不是新的评估执行。未启动 Darknet、未启动 workflow、未重复 37 分钟全量评估；r1 报告与外部 r1 run-dir 保持不变。

- 本地 source commit 已现场验证为 `59596d7880f6504768df41d6daa586f5cb2b932f`（完整 40 位）。
- `git -C D:\FPGA_Data\darknet diff --quiet` 退出码 `0`；未执行网络访问。source 仓库仍有原有未跟踪 `build/`、`weights/`，不影响 HEAD 验证。
- r1 运行状态保留为 `EXECUTED_REVIEW_REQUIRED`，exit code `0`，错误 `[]`。
- valid/runtime/evaluation/JSONL/逐图输出均为 `15195/15195`；独立只读校验通过。
- `friend_004` 为第 `15194` 条，`objects=[]`、`box_count=0`。
- 未设置 mAP 下限；本证据不作精度结论。

## 版本绑定来源

workflow 当前 `_identity_artifacts()` 只从 environment report 的 `darknet_source_commit` 读取提交号；缺失时写入 `unavailable`，不会自动读取 `D:\FPGA_Data\darknet`。r1 因此留下了 `unavailable`。本 r2 通过本地只读命令补齐绑定：

```text
git -C D:\FPGA_Data\darknet rev-parse HEAD
=> 59596d7880f6504768df41d6daa586f5cb2b932f

git -C D:\FPGA_Data\darknet diff --quiet
=> exit 0
```

r2 JSON 的 `identity.official_darknet_source` 为 `D:\FPGA_Data\darknet`，`identity.official_darknet_source_commit` 为上述完整提交号，并记录了命令、退出码、观察时间和 `network_access=false`。

## 证据文件

- 新报告：[20260915_s1_t01_d5b2_ac07_repro_r2.json](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_d5b2_ac07_repro_r2.json)，3,319,866 bytes，SHA256 `8ada6e3572577464639aba3248ceb1e38056977b36df3c7a013917de8ff1eb06`。
- r1 基础报告：[20260915_s1_t01_d5b2_ac07_repro_r1.json](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_d5b2_ac07_repro_r1.json)，SHA256 `0394d2125e9597f01e9d5c0cca2ce5e81483505f63bb7b3a7611ce5a4dd6cf6f`；r2 记录了该基础 SHA，确认未覆盖。
- r1 外部运行目录：[s1_t01_d5b2_ac07_repro_r1](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1)。
- 新摘要文件：[20260915_s1_t01_d5b2_ac07_repro_r2_summary.md](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_d5b2_ac07_repro_r2_summary.md)，最终 SHA256 记录于交付摘要。

## r1 运行产物只读校验

- source valid.list：15195 行，SHA256 `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`。
- runtime_valid.list：15195 行，SHA256 `14604d2313c6bdbdb206ae979f60d7681ffc8ed27ccd2ad5191985ae631c4f60`；逐行 canonical-resolve 映射错误 `0`。
- [evaluation.json](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/evaluation.json)：15195 条，3,947,295 bytes，SHA256 `31d1979458293e2026b98ceefd3d986686851902d8cbcb9a9e28f2d75a84e4e4`。
- [evaluation.jsonl](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/evaluation.jsonl)：15195 条，10,266,634 bytes，SHA256 `1b0664ba420146d78b5535c292e535f4066640907f1ee6c08e51b2dbf1631813`。
- [detections](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/detections)：15195 个 `eval_*.json`，合计 5,284,313 bytes；逐图 JSON 均可解析，frame/order/path/objects/class/confidence/坐标校验通过。
- [evaluate.log](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/evaluate.log)：3,306,338 bytes，SHA256 `b511b5bb2bbb1a8115fb55e8ed3028b3539f1163e772eeb5eaa2c9444ac96acf`；`Predicted in=15195`，`Enter Image Path=15196`。
- 锁文件不存在；评估进程已结束；STOP_RE、OOM、NaN、Inf、损坏和错误停止标记均为 `0`。

## 固定输入绑定

- Darknet exe：`358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`。
- source cwd：`D:\FPGA_Data\darknet`，source commit：`59596d7880f6504768df41d6daa586f5cb2b932f`。
- workflow：`5ead5ca061f1b41f3124d7e3865398065be7d13bfd1e6a6ddbbed152d6382e04`。
- data cfg：`ff9e3d1a2b43de9d70a1884f6181c6d0a495713575ed7331712c7ea1e1d93d3e`。
- project cfg：`76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`。
- names：`5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`。
- weights：`ba3ba3bff1b12c0f3b5b23df9c5fb22ea9744eeb05f78ea1fe109ccc73671017`。
- manifest：`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- dataset approval：`90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213`；environment report：`fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11`。

## 验证与范围

- 本轮未修改 `verification/s1_t01_darknet_workflow.py` 或测试文件，因此无代码差异、无需新增单元测试。
- `py -m py_compile verification\\s1_t01_darknet_workflow.py verification\\test_s1_t01_darknet_workflow.py`：退出码 `0`。
- `py -m unittest verification.test_s1_t01_darknet_workflow`：退出码 `0`，`Ran 30 tests`，`OK`。
- `git diff --check`：退出码 `0`。
- 当前仓库 HEAD 为 `5e13ad4273925b525e459735f625d8c7143b5def`，工作区已有用户改动及既有外部证据未清理、未提交；r1/r2 证据均不纳入 Git 提交。
