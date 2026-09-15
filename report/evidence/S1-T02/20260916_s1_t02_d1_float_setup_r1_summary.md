# S1-T02-D1-FLOAT-BASELINE-SETUP-R1

状态：`PILOT_ONLY_NOT_FORMAL_EVALUATION`。本轮只完成三组浮点配置副本、拓扑解析和 tiny 320/416 短加载 pilot；不宣称 mAP、精度、最终输入尺寸、最终模型或性能通过，不启动训练或正式 test split 评估。

## 版本与固定输入

- 仓库 HEAD：`743279ad943c7d38a099f9266009b147616d4382`；工作区保留既有用户改动，本轮未修改代码、用户文件或 Vivado。
- 官方 Darknet：`D:\FPGA_Data\darknet`，HEAD `59596d7880f6504768df41d6daa586f5cb2b932f`；`git diff --quiet` 退出码 `0`。该工作树仍有未跟踪 build/weights，但无 tracked diff。
- Darknet exe：`D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe`，SHA256 `358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`。
- 固定五类 names：`fist,palm,one,two_up,three`，SHA256 `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`。
- manifest：158680 行，SHA256 `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- train.list：118001 行，SHA256 `4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa`。
- valid.list：15195 行，SHA256 `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`。
- D5B2 诊断权重：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\diag_s1_t01_d5b2_200\backup\gesture_yolov4_tiny_416_diag_200_200.weights`，SHA256 `ba3ba3bff1b12c0f3b5b23df9c5fb22ea9744eeb05f78ea1fe109ccc73671017`；仅作加载 pilot，不是正式候选。

机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d1_float_setup_r1.json`，SHA256 `b82408fd17f220c1f9d47ba4f2da375b9858aa1b23b118c7558286af37f24923`。

## 配置库存与拓扑

所有新配置位于 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\configs`，由外部准备脚本生成；原始 cfg/data/list 未改写。

| 配置 | 来源/改变 | SHA256 | 网络/层 | 估算参数 | 估算 BFLOPs | 检测头网格 |
|---|---|---|---:|---:|---:|---|
| `gesture_yolov4_tiny_416_float_setup.cfg` | 固定五类 tiny 416 cfg 的字节副本 | `5c5af96850ca3f13a86decb111fb2710d1b061353d46253ffb16be097da8fa09` | 416×416 / 38 层 / 21 conv | 6,079,996 | 7.389145 | 13×13 mask 3,4,5；26×26 mask 1,2,3 |
| `gesture_yolov4_tiny_320_float_setup.cfg` | 同一 tiny cfg，仅 `width/height=320` | `9b4da2163d4a540ac2f7535312ffc22d1f465445fd175509575fc601dad74fa8` | 320×320 / 38 层 / 21 conv | 6,079,996 | 4.372275 | 10×10 mask 3,4,5；20×20 mask 1,2,3 |
| `yolov4_5class_float_pc_setup.cfg` | 官方 `D:\FPGA_Data\darknet\cfg\yolov4.cfg`，三个 head 的 `classes=80→5`，前置 filters `255→30` | `9f3f518e995a0f536bc0edf0530a10362ead0ec3858466f1bdcc81bfdd71fb41` | 608×608 / 162 层 / 110 conv | 63,992,378 | 123.217383 | 76×76 mask 0,1,2；38×38 mask 3,4,5；19×19 mask 6,7,8 |

三组配置均保留相应来源的 anchors、stride、head 结构；tiny 320 仍使用 tiny 416 的 anchors，是否重新聚类 anchors 属于后续 G0 决策。完整 YOLOv4 保留官方 608 输入和官方三头 anchors，尚未形成正式五类训练权重。

外部 data 配置：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\float_setup.data`，SHA256 `63c0f3a149dc77d4b1003c600112f3385c528ed87a34e7834228de015d05b7fb`；names/train/valid 使用绝对路径，backup 指向隔离目录。

## 实际 pilot

准备/执行脚本：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\prepare_and_pilot.py`。首次执行退出码 `1`：脚本自身先创建空目录后误判为已有产物，未启动 Darknet；修正空目录判断后再次执行退出码 `0`。

两次 pilot 使用同一官方 source cwd 和临时 PATH（pthread/CUDA 目录仅对子进程生效），argv 均为：

```text
darknet.exe detector test float_setup.data <cfg> diag_200_200.weights -dont_show -thresh 0.25 -out <pilot-json>
```

没有 filename positional；输入通过 stdin 逐行提供一张正样本和 `friend_004` no_hand 图。

| Pilot | 时间（UTC+8） | 退出码 | 预测耗时（ms） | JSON | 日志 |
|---|---|---:|---|---|---|
| tiny 416 | 00:12:23–00:12:26 | 0 | 68.666、3.722 | `pilots/tiny416_smoke.json`，SHA `cc811b0c0e260eadaa72cb4bafe3982881e31a55eabb35211b3f3f72b30c44c5` | SHA `3235ceef5d1215b69364cd6e4ff2117fbe9971ff510c964477f66025544c59e0` |
| tiny 320 | 00:12:26–00:12:27 | 0 | 67.523、2.859 | `pilots/tiny320_smoke.json`，SHA `52552e61d63ca9894a0ea1dce3eed2766793eeb5fac28aff57ae13f48e073251` | SHA `be6781a01bc9943a8c355f20d99342e026fde1a32d706eeed9f672f75f4f8b22` |

两个 JSON 均为标准 JSON 数组、各 2 条记录。tiny 416 正样本本次未产生框，tiny 320 正样本产生 1 个 `fist` 对象；两种尺寸的 `friend_004` 均为 0 框。这些仅是诊断权重的加载/拓扑 smoke，不是精度结论，也不用于阈值选择。

完整 YOLOv4：未执行加载 pilot，原因是当前没有匹配的五类完整权重；未下载 COCO 权重，避免将不匹配检测头当作正式模型。

## G0 缺口与下一任务

仍需 Wong 在正式浮点基线前冻结：

1. train/val/test 的正式子集、人员/会话隔离、相邻帧规则和各类/负样本最低数量；当前 test split 有 25484 张，但没有独立 `test.list`。
2. 随机种子、batch/subdivisions、训练步数、学习率/warm-up、预训练权重政策和停止规则。
3. 320/416 最终比较范围，以及完整 YOLOv4 是否只保留 PC 对照。
4. RGB/BGR、缩放插值、补边颜色/位置、归一化、scale/zero-point、layout 和 padding 规则。
5. score、IoU 匹配、NMS 类型/IoU、最大框数、同分排序和零框格式。
6. mAP@0.5、mAP@0.5:0.95、五类 precision/recall、no_hand 误检上限。
7. INT8 相对浮点允许损失及逐层数值一致性规则。
8. 推理时间起止事件、warm-up、预处理/解码/NMS/IO 是否计入、P99、显存、DDR/带宽和资源统计口径。

建议下一 Developer 任务：`S1-T02-D2-FLOAT-BASELINE-RUN-R1`。前置为 Wong 完成上述 G0 冻结；先 tiny 416，再 tiny 320，最后完整 YOLOv4 PC 对照。每组先做短吞吐/显存 pilot，再进入正式浮点训练和统一 val/test 评估；生成独立 cfg、权重、日志、评估器和 SHA。禁止把本轮 D5B2 200 步权重写成正式候选，禁止在阈值未冻结前宣称精度通过。

本轮未运行训练、正式评估、INT8、RTL、烧录或性能长测；未修改仓库 verification 代码，未提交 Git。
