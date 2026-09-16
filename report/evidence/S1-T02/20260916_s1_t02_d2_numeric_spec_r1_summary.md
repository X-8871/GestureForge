# S1-T02-D2 固定预处理与 INT8 数值规格（R1）

状态：`REFERENCE_IMPLEMENTED_INPUT_BOUND_REVIEW_REQUIRED`。本轮只完成独立参考、golden 和训练校准输入绑定；未训练、未执行 Darknet 正式评估、未测 mAP、未进行 INT8 整网精度或上板验收。

## 已落地规则

- 输入为 RGB 三通道，参考布局 CHW，像素除以 255；候选尺寸为 tiny320、tiny416、完整 YOLOv4 608。
- letterbox 保持比例，按 Darknet `resize_image` 的端点对齐双线性；整数尺寸使用源码截断，左右/上下偏移为 `(目标尺寸-新尺寸)//2`；归一化填充 0.5（8-bit 128）。
- INT8 为有符号 `[-127,127]`、zero-point=0、输入 scale=`1/127`；权重逐输出通道、激活逐层逐张量对称量化；BN 折叠后 bias 进入累加器域；INT32 累加并独立 INT64 检查；正负半数远离零；饱和到 `[-127,127]`；检测头后处理仍为 PS 浮点逻辑。

## 输入绑定

校准清单：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_calibration_r1\calibration.list`，SHA256=`d637a2feb671429741c8b6703caaa9cdf995abf49dfa4b72e41f62dfbea1a35c`，共 `512` 行。组成是五类各100张、12张训练负样本，其中批准语义的 train no_hand 3张全部纳入；其余负样本为5张批准 non_target_gesture 和4张其余空标签。只读取 train，不使用 valid/test/robust；原始 train.list、manifest、标签未修改。

机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d2_numeric_spec_r1.json`

## cfg 路由限制

固定源 cfg `D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg`（SHA `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`，3499 bytes）未显式包含 `letter_box=1`。因此本轮生成隔离绑定副本 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_calibration_r1\gesture_tiny416_d2_letterbox.cfg`（SHA `285fd457aa9456709758149d48014374c1e5628e3d5484171410c9a9fc1905a7`，3513 bytes），仅增加一行 `letter_box=1`，源 cfg 不变。Darknet 源 `D:\FPGA_Data\darknet` 实际 HEAD=`59596d7880f6504768df41d6daa586f5cb2b932f`；源码依据为 `src/image.c:989-1021,1399-1446`、`src/detector.c:1630-1675` 和 parser 的 `letter_box` 默认值。正式 workflow 尚未使用该副本运行，故该路由的真实推理一致性仍是后续验证项。

## 验证与限制

根目录模块调用、verification 目录 D2 discover、verification 目录全量 discover 和仓库根目录全量 discover 均退出0；D2 测试9项、全量 verification 测试64项。py_compile、golden 生成、校准绑定和 git diff --check 均退出0。两次早期低效扫描被主动停止，未产生通过报告；最终成功命令和退出码只见机器报告。

本轮未设置或宣称 mAP/精度门槛通过；用户批准的量化损失门槛仍是后续浮点基线和 INT8 对照的验收候选。当前证据不能宣称最终模型、INT8 精度、GPU 性能、资源、RTL 或板上结果。
