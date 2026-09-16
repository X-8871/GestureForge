# S1-T02-D6 离线检测指标证据

状态：`G0_PENDING`；schema_valid=`True`；errors=0。
本文件只验证离线评估口径和夹具/输入绑定，不代表正式训练、正式浮点/INT8 精度、G0/G4 或板上通过。

## 固定评估配置

- split：`val`；图片数：`2`；GT 框数：`1`。
- score threshold：`0.25`；NMS：类别内 greedy IoU=`0.45`；每图最大输出=`15`。
- AP：IoU 0.50:0.05:0.95、101-point all-point interpolation、五类宏平均；无 GT 类别保留 support 并不静默计入0。
- mAP@0.5：`1.0`；mAP@0.5:0.95：`1.0`（仅夹具/当前输入结果）。

## 绑定与限制

- manifest、预测、names 和代码 SHA 见机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d6_detection_metrics_r2.json`。
- no_hand 误检率：`NOT_EXECUTED`；non-target 误检率：`NOT_EXECUTED`。缺少批准 subset 时不生成0%。
- 当前 threshold 是 CLI 绑定值而非本轮冻结的独立 G0 配置；test/robustness 不得重新调参。
- 本轮未启动 Darknet、训练、权重下载、INT8 整网或硬件测量。

## 验证

- 评估器使用显式 relative_coordinates 或 xyxy_normalized，严格拒绝缺失、重复、额外、错序 filename/frame_id、非法类别、非法坐标和输出覆盖。
- 预测输出中的对象字段保留 class_id/name、confidence 和归一化 xyxy；原始预测输入保持外部/夹具位置，不被报告覆盖。
