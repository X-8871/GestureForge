# Data Package

保存输入样例、标签、数据集说明和模型输出参考。大型原始数据集不直接复制进提交包，改用外部数据根目录、UTF-8 清单和校验值登记。

## S1-T01 当前状态

2026-09-13 的历史状态是工程内只有本说明文件；当前真实数据存放在仓库外的 `D:\FPGA_Data\HaGRIDv2`，不把完整数据、模型或权重复制进 Git。Wong 摄像头多会话数据用于后续域适配和独立测试；不把合成图片当作真实手势精度证据。

五类编码固定为：`0=fist`、`1=palm`、`2=one`、`3=two_up`、`4=three`。

## S1-T01 当前外部数据与清单

- 原始图片和官方标注已解压到 `D:\FPGA_Data\HaGRIDv2\dataset`；七个下载包均已在内容校验后清理，下载目录不再有 ZIP。
- 生成标签根目录：`D:\FPGA_Data\HaGRIDv2\labels`；正式清单：`D:\FPGA_Data\HaGRIDv2\manifest.csv`；未去重全清单备份：`D:\FPGA_Data\HaGRIDv2\manifest_all.csv`。标签文件保留原始转换的 158,698 个，正式清单引用其中 158,675 个；为保留可追溯性，去重移除的 23 个标签文件未删除。
- 正式清单含 158,675 行、156,518 个五类框；原始转换清单含 158,698 行、156,536 个框。正式清单按 `train > val > test` 移除 23 条跨 split 完全重复图片行，原始图片不删除。
- `no_gesture` 目录有 2,166 张图片，其中 2 张带 `-checkpoint` 后缀且未被官方 JSON 引用，未伪造 split/person 字段，保留为未入清单原始数据。
- 许可证文件 `D:\FPGA_Data\HaGRIDv2\license\en_us.pdf` SHA-256：`14f4845e9c8d3de875cbac4139491da368ab1040a7f565e02894477279134d22`。原 ZIP 已按用户要求删除，未在删除前采集 ZIP SHA-256；证据保留 ZIP CRC、条目数、解压尺寸和清理结果。

## S1-T01 清单接口

数据根目录放在 Git 仓库外，例如当前的 `D:\FPGA_Data\HaGRIDv2`。清单为 UTF-8 CSV，路径均相对数据根目录，必须包含以下列：

```text
image,label,split,session_id,person_id,source,license,is_real
```

- `image` 和 `label` 分别指向图片与同名 YOLO 标签；无手图片保留同名空标签文件。HaGRIDv2 官方 `bboxes` 使用归一化 COCO `[left, top, width, height]`，转换器发布前会转为归一化 YOLO `[center_x, center_y, width, height]`。
- `split` 只能是 `train`、`val` 或 `test`；训练、验证、测试不得共享 `session_id` 或 `person_id`。
- `source` 和 `license` 记录来源与使用条件；`is_real` 必须为 `true` 或 `false`。
- YOLO 标签每行是 `class_id center_x center_y width height`，五个数值均在 `[0,1]`，宽高为正；一只手一个框，多手逐手标注。
- 遮挡或截断但仍能辨认的手保留并记录属性；无法可靠辨认的样本移入待复核，不伪标为五类。

检查命令：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py `
  --data-root 'D:\FPGA_Data\HaGRIDv2' `
  --manifest 'D:\FPGA_Data\HaGRIDv2\manifest.csv' `
  --report report\evidence\S1-T01\<运行编号>_dataset_check.json `
  --preview-dir report\evidence\S1-T01\<运行编号>_previews
```

标签重建命令：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_prepare_hagrid.py `
  --data-root 'D:\FPGA_Data\HaGRIDv2' `
  --manifest 'D:\FPGA_Data\HaGRIDv2\manifest_all.csv' `
  --labels-root 'D:\FPGA_Data\HaGRIDv2\labels' `
  --report report\evidence\S1-T01\<运行编号>_prepare.json
```

工具主要使用标准库完成支持格式的结构和像素载荷校验；JPEG 还要求 Pillow 完整解码像素载荷。检查标签合法性、图片/标签 stem 一一对应、来源字段、人员/会话隔离和跨集合重复内容，并输出每类两个框及五张无手图的确定性抽查候选。它不能替代 Wong 对真实图片、框覆盖和遮挡规则的人工观察；AC04 在人工回传前保持待抽查。

最低流程门槛为至少 30 张真实图片、每类至少 5 个框、至少 5 张无手图，且训练/验证都覆盖五类和无手样本。该门槛只用于 S1-T01 流程验证，不是阶段1正式精度验收门槛。
