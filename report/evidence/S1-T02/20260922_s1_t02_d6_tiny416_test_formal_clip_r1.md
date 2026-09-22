# S1-T02-D6 离线检测指标证据

状态：`G0_PENDING`；schema_valid=`True`；errors=0。
本文件只验证离线评估口径和夹具/输入绑定，不代表正式训练、正式浮点/INT8 精度、G0/G4 或板上通过。

## 固定评估配置

- split：`test`；图片数：`25484`；GT 框数：`24990`。
- score threshold：`0.25`；NMS：类别内 greedy IoU=`0.45`；每图最大输出=`15`。
- AP：IoU 0.50:0.05:0.95、101-point all-point interpolation、五类宏平均；无 GT 类别保留 support 并不静默计入0。
- mAP@0.5：`0.9774176564941799`；mAP@0.5:0.95：`0.7700877728041977`（仅夹具/当前输入结果）。
- 坐标政策：`clip_finite_positive_xyxy_to_unit_range`；有限正面积框逐坐标裁剪到 `[0,1]`，裁剪后零面积仍拒绝；本次 raw 越界框=`76`，实际裁剪=`76`。

## 绑定与限制

- manifest、预测、names 和代码 SHA 见机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260922_s1_t02_d6_tiny416_test_formal_clip_r1.json`。
- 批准样本政策决策日期：`2026-09-22`；正式口径文档 SHA-256：`a79245b577e72ecdc9c36a0e2f5dac783a67422e5a8ad414b2eb2a77f40734c0`。
- 官方 test：批准 manifest SHA-256=`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`，完整图片数=`25484`；本次绑定状态=`BOUND`。
- 独立 robustness：每个目标类别至少 `100` 张、每个条件 bucket 至少 `100` 张；实际数据绑定=`PENDING`。
- 完整 G0 指标策略快照：`BOUND_AND_VERIFIED`；test/robustness 使用快照固定 score threshold=0.25，禁止调参。
- no_hand 误检率：`NOT_EXECUTED`；non-target 误检率：`NOT_EXECUTED`。缺少批准 subset 时不生成0%。
- 仍未决：mAP 与逐类 precision/recall 验收门槛，以及 robustness 数据集构建和人物/session 隔离审计；G0 acceptance 仍 pending。
- 本轮未启动 Darknet、训练、权重下载、INT8 整网或硬件测量。

## 验证

- 评估器使用显式 relative_coordinates 或 xyxy_normalized，严格拒绝缺失、重复、额外、错序 filename/frame_id、非法类别、非有限/非正面积坐标和输出覆盖；有限正面积的越界框按冻结政策裁剪。
- 预测输出中的对象字段保留 class_id/name、confidence、裁剪后和 raw 归一化 xyxy；原始预测输入保持外部/夹具位置，不被报告覆盖。
