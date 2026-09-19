# S1-T02-D6 tiny416 验证集坐标裁剪影响诊断 R1

状态：`DIAGNOSTIC_ONLY_NO_METRICS`。本证据绑定 HEAD `70f55a1c0321152151a6653b2d8a9b147e4154ea`，不修改 D6/D9 代码、候选 `evaluation.json` 或 STATE。

## 输入与执行

- 候选捕获报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260918_s1_t02_d6_tiny416_val_candidate_r1_retry02.json`；SHA-256 `2eeabde5dfd56283f42fdf53d4b393aceb58c42b9b24c499585b6ceb3ab4354b`。
- 外部预测：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d6_tiny416_val_candidate_r1_retry02\evaluation.json`；SHA-256 `56cc6cc222b281b1f3f2aa1a952d86444892bef1052463a4bbaf66675ba7700e`；大小 `4574715` B。
- 输入包含 `15195` 条图像记录、`15223` 个预测 objects。
- 执行：`PowerShell here-string | C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe -`；退出码 `0`；仅 CPU，未联网、未使用 GPU、未训练。
- 输出 JSON SHA-256：`88896cedea23f8cb50ea981c1a7072f1bae41871dbd425f575ec4f8ec423f569`。

## 定义

对 Darknet `relative_coordinates` 使用 `x1=cx-w/2`、`y1=cy-h/2`、`x2=cx+w/2`、`y2=cy+h/2`。`raw_valid` 要求四值有限、均在 `[0,1]` 且面积为正；clip 对有限坐标逐项执行 `min(max(value,0),1)`。裁剪后 `x2<=x1` 或 `y2<=y1` 为零面积；原框在 x 或 y 方向完全位于单位方框外的零面积框另计为 fully outside。

## 结果

| 项目 | objects |
|---|---:|
| 总 objects | 15223 |
| 有限 xyxy | 15223 |
| 非有限 xyxy | 0 |
| raw 有效 | 15174 |
| raw 无效 | 49 |
| raw 越界 | 49 |
| raw 非正面积 | 0 |
| clip 改变 | 49 |
| clip 后正面积 | 15223 |
| clip 后零面积 | 0 |
| clip 后完全外部 | 0 |
| clip 后零面积但非完全外部 | 0 |

越界坐标事件：`{"x1_below_0": 24, "x2_above_1": 14, "y1_below_0": 12, "y2_above_1": 2}`。这是坐标事件数，不能与 objects 数直接相加。

按类别：`fist 2960/25 越界`、`palm 3013/12`、`one 3099/4`、`two_up 3116/5`、`three 3035/3`；每类格式为“总 objects/ raw 越界 objects”。五类均为有限坐标，非有限为 0。

## 解释边界与待决策项

当前 49 个 raw 越界 objects 均可通过 clip 保留正面积；没有 clip 后零面积或完全外部 object。因此本证据说明了坐标边界影响，但没有比较任何 mAP、precision、recall、IoU 或阈值结果。正式评估仍需 Wong 决定 raw 严格拒绝还是 clip 后计分，并由对应 D6 实现、测试和复审闭环关闭。

不产生 mAP/AP/precision/recall、不扫描或推荐 threshold、不读取图片、不读取 GT、不联网、不使用 GPU。
