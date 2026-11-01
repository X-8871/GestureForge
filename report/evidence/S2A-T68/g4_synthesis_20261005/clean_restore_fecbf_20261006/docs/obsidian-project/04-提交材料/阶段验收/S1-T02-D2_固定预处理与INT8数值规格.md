# S1-T02-D2 固定预处理与 INT8 数值规格

本规范记录 Wong 已批准的阶段1第4项预设，供浮点基线、INT8 参考和后续 PL/PS 对照使用。本文件不表示最终上板模型、INT8 精度关口或阶段1 G4 已通过。

## 输入与预处理

- 输入为 RGB 三通道；Darknet 参考布局为 CHW，像素值除以 255。
- 候选固定方形尺寸为 YOLOv4-tiny 320×320、YOLOv4-tiny 416×416、完整 YOLOv4 608×608。
- letterbox 保持宽高比，使用 Darknet `resize_image` 的端点对齐双线性插值；整数新宽高按源码整数截断，左上偏移为 `(目标尺寸-新尺寸)//2`。
- 补边的归一化值为 0.5，对应 8-bit 值 128；正式推理关闭随机增强、多尺度和随机裁剪。训练、PC 评估和 FPGA 输入必须使用同一规则。

## INT8 数值规则

- 使用有符号 `[-127,127]`，zero-point 为 0；输入 scale 固定为 `1/127`。
- 卷积前先折叠 BN；权重按输出通道分别对称量化，激活按层、按张量对称量化。
- 卷积使用 INT32 累加器，并以独立 INT64 精确整数路径检查乘积和累加溢出；BN 折叠后的 bias 进入累加器域。
- 舍入为正负对称、半数远离零；结果饱和到 `[-127,127]`。零层的 scale 回退为 `1/127`。
- 检测头反量化后，PS 使用浮点 sigmoid、exp、坐标解码和 NMS；本规范不冻结或实现 NMS 测试。

## 校准集与证据

校准集固定从 train 清单选择 512 张：五类各 100 张，加 12 张训练负样本；当前 3 张经批准的 train no_hand 必须全部纳入。不得使用 valid、official test 或独立 robustness 集校准。no_hand 是空标签负样本，不是第六类；其他空标签不能被改写为 no_hand。

独立实现和机器证据：

- [s1_t02_d2_numeric_reference.py](../../../../verification/s1_t02_d2_numeric_reference.py)：预处理、舍入、量化、饱和、bias/requant 和溢出检查。
- [s1_t02_d2_calibration.py](../../../../verification/s1_t02_d2_calibration.py)：train-only 的确定性 512 张选择与 canonical/标签校验。
- 证据摘要：[20260916_s1_t02_d2_numeric_spec_r2_summary.md](../../../../report/evidence/S1-T02/20260916_s1_t02_d2_numeric_spec_r2_summary.md)。

## 当前绑定限制

固定项目 cfg 当前未显式包含 `letter_box=1`。本轮未修改源 cfg，而在外部隔离目录生成显式绑定副本；正式 Darknet 运行仍需使用该绑定副本或等价的 `-letter_box` 路由并单独验证。当前未执行训练、正式评估、mAP、INT8 整网精度、资源、RTL 或板上测试。
