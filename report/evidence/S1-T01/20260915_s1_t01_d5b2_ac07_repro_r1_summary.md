# S1-T01-D5B2-AC07-REPRO-R1 复现证据摘要

## 结果

- 数据复检：退出码 `0`，报告状态 `PASS_AUTOMATED_MANUAL_PENDING`，异常 `[]`。
- 全量评估：workflow 退出码 `0`，报告状态 `EXECUTED_REVIEW_REQUIRED`，异常 `[]`。
- valid 清单、runtime stdin 清单和 Darknet 预测顺序均为 `15195/15195`；未设置 mAP 下限或精度门槛。
- 独立只读审计：evaluation JSON、evaluation JSONL、逐图 JSON 均可解析，顺序绑定、字段、有限数值和输出文件 SHA 校验通过。
- Wong 批准的 `friend_004` 为 valid 第 `15194` 条，逐图 JSON 和汇总 JSONL 均为 `objects=[]`、`box_count=0`。
- 未发现 OOM、NaN、Inf、损坏、STOP_RE 或日志错误停止标记；Darknet/Python 进程已结束，锁文件已清理。

## 时间与命令（UTC+8）

Python 解释器：`C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe`，Python `3.12.10`。

数据复检于 `2026-09-15 20:57:13` 启动，目标报告/预览于 `22:14:52` 完成，耗时约 `1:17:39`；工作目录为 `D:\FPGA_Competition`，退出码 `0`。

```text
py D:\FPGA_Competition\verification\s1_t01_dataset_check.py --data-root D:\FPGA_Data\HaGRIDv2 --manifest D:\FPGA_Data\HaGRIDv2\manifest.csv --semantic-review report\evidence\S1-T01\20260914_hagrid_semantic_review.csv --report report\evidence\S1-T01\20260915_s1_t01_ac07_dataset_recheck.json --preview-dir report\evidence\S1-T01\20260915_s1_t01_ac07_dataset_recheck_previews
```

全量评估于 `2026-09-15 22:15:18` 启动，报告及 JSONL 于 `22:52:53` 完成，耗时约 `0:37:35`；Darknet cwd 为 `D:\FPGA_Data\darknet`，workflow 退出码 `0`。PATH 仅在该进程树内临时加入 pthread/CUDA 目录。

```text
py D:\FPGA_Competition\verification\s1_t01_darknet_workflow.py evaluate --darknet-executable D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe --environment-report D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v3.json --data-root D:\FPGA_Data\HaGRIDv2 --manifest D:\FPGA_Data\HaGRIDv2\manifest.csv --dataset-report D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json --dataset-approval D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_approval.json --data-config D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture_eval_r2.data --model-config D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg --names-file D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names --working-directory D:\FPGA_Data\darknet --run-dir D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_ac07_repro_r1 --report D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b2_ac07_repro_r1.json --weights D:\FPGA_Data\HaGRIDv2\darknet_inputs\diag_s1_t01_d5b2_200\backup\gesture_yolov4_tiny_416_diag_200_200.weights --valid-list D:\FPGA_Data\HaGRIDv2\darknet_inputs\valid.list --zero-prediction-image D:\FPGA_Data\HaGRIDv2\user_no_hand\20260915_friend_004.png --timeout-seconds 7200 --no-progress-timeout-seconds 300
```

实际 detector argv 为单进程官方接口顺序：`[darknet.exe, detector, test, data, cfg, weights, -dont_show, -out, evaluation.json]`，无 filename positional，stdin 为隔离 runtime 清单。

## 数据复检证据

- 报告：[20260915_s1_t01_ac07_dataset_recheck.json](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_ac07_dataset_recheck.json)，7902 bytes，SHA256 `ec9be81db33a36830c9dbc3f50a6127a5cc949c20862ae59941bdea97d852082`。
- 预览目录：[20260915_s1_t01_ac07_dataset_recheck_previews](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_ac07_dataset_recheck_previews)，15 个 SVG，合计 25,752,883 bytes；目录内文件均保留，未覆盖旧预览。
- manifest：`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`；semantic CSV：`aa1177e9afffd1c0de8ae09ffaa98339c385216bbf1d4802cae6eab4a36eb799`。
- 自动指标：manifest/valid rows `158680`，real images `158680`，non-real `0`，boxes `156518`，val images `15195`，session/person overlap `{}`；AC02、AC03 自动通过，AC04 保留原有 Wong 人工抽查提示。

## 全量评估证据

- 报告：[20260915_s1_t01_d5b2_ac07_repro_r1.json](D:/FPGA_Competition/report/evidence/S1-T01/20260915_s1_t01_d5b2_ac07_repro_r1.json)，3,317,923 bytes，SHA256 `0394d2125e9597f01e9d5c0cca2ce5e81483505f63bb7b3a7611ce5a4dd6cf6f`。
- 外部 run-dir：[s1_t01_d5b2_ac07_repro_r1](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1)。
- runtime stdin：[runtime_valid.list](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/runtime_valid.list)，15195 行，SHA256 `14604d2313c6bdbdb206ae979f60d7681ffc8ed27ccd2ad5191985ae631c4f60`；source valid.list SHA256 `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`。逐行 canonical-resolve 映射错误 `0`。
- [evaluation.json](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/evaluation.json)：15195 条，3,947,295 bytes，SHA256 `31d1979458293e2026b98ceefd3d986686851902d8cbcb9a9e28f2d75a84e4e4`；对象总数 `11212`。
- [evaluation.jsonl](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/evaluation.jsonl)：15195 条，10,266,634 bytes，SHA256 `1b0664ba420146d78b5535c292e535f4066640907f1ee6c08e51b2dbf1631813`。
- [detections](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/detections)：15195 个 `eval_*.json`，合计 5,284,313 bytes；首文件 SHA256 `d7dfbb83f0d81e743a2d0695f859890213e3d969db0abfce44505dc48e93020a`，末文件 SHA256 `ed7b647bf4c14b085c72543473a38d9992770f8a3b032bee20958e4685be73a2`。
- [evaluate.log](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t01_d5b2_ac07_repro_r1/evaluate.log)：3,306,338 bytes，SHA256 `b511b5bb2bbb1a8115fb55e8ed3028b3539f1163e772eeb5eaa2c9444ac96acf`；`Predicted in=15195`，`Enter Image Path=15196`。

固定输入摘要：Darknet exe SHA256 `358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`；source commit `59596d7880f6504768df41d6daa586f5cb2b932f`；workflow SHA256 `5ead5ca061f1b41f3124d7e3865398065be7d13bfd1e6a6ddbbed152d6382e04`；data cfg `ff9e3d1a2b43de9d70a1884f6181c6d0a495713575ed7331712c7ea1e1d93d3e`；project cfg `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`；names `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`；weights `ba3ba3bff1b12c0f3b5b23df9c5fb22ea9744eeb05f78ea1fe109ccc73671017`。

## 范围与限制

- 未修改 verification 代码、原始 valid.list、gesture.data、cfg、names、labels、manifest、权重、approval、环境报告或既有 r1/r2/r3/full-r1 证据；未提交 Git。
- 当前仓库 HEAD 实测为 `5e13ad4273925b525e459735f625d8c7143b5def`，工作区保留任务开始前已有用户改动；本轮未清理或纳入这些改动。
- 本证据证明数据复检与 AC06 评估输出闭环及可复现绑定，不作 mAP/精度结论；AC04 的人工抽查状态仍按数据复检报告和 Wong 批准记录解释。
