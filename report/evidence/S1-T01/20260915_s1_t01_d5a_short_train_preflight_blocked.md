# S1-T01-D5A 五类 YOLOv4-tiny 416 短训准备阻断证据

## 结论

- 任务范围：只准备官方 Darknet 五类 YOLOv4-tiny 416 短训输入并执行 dry-run；不启动训练、恢复、评估、量化、RTL 或烧录。
- 结果：`BLOCKED_BEFORE_DRY_RUN`。
- 阻断原因：官方初始权重下载命令在写入阶段失败，`curl.exe` 退出码 `23`（`client returned ERROR on write of 12402 bytes`）。目标文件随后不存在，因此不得将其作为 `--initial-weights` 传入工作流。
- 记录时间：2026-09-15（UTC+8）。

## 基线与源目录

- 仓库：`D:\FPGA_Competition`
- 实际 HEAD：`cb4e032c2d182bbb06565ae27620a31eef322366`
- 用户指定代码基线：`4c82535dba330a85187adba53e42f4e41c365981`（实际 HEAD 已包含该提交）
- 官方 Darknet：`D:\FPGA_Data\darknet`
- 官方源 commit：`59596d7880f6504768df41d6daa586f5cb2b932f`
- official remote：`https://github.com/AlexeyAB/darknet.git`
- 源目录 tracked diff：`git diff --quiet` 退出码 `0`
- 源目录已有未跟踪构建目录：`build/s1_t01_vc_cuda134_v2/`；未修改、未删除、未纳入本证据。
- 本仓库用户既有改动未修改、未暂存：两份 Obsidian Markdown、Vivado `.xpr` 及两张板卡 JPG；既有预览目录也未触碰。

## 已准备 cfg

- 派生文件：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg`
- 来源：只读复制官方 `D:\FPGA_Data\darknet\cfg\yolov4-tiny.cfg` 后修改任务要求字段；官方源 cfg 未修改。
- cfg SHA-256：`76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`
- 官方源 cfg SHA-256：`a6415c2e303f7b3647913a7bb3675f0fe7234049d8875ae7d75c01b8e4dcb854`
- 固定字段：`batch=64`、`subdivisions=16`、`width=416`、`height=416`、`max_batches=20`、`steps=16,18`、`random=0`。
- 两个检测头均为 `classes=5`，紧邻前置卷积均为 `filters=30`；anchors 与官方 cfg 保持一致。
- `subdivisions=16` 是 RTX 4060 Laptop 8GB 的保守短训显存起点；尚未通过真实训练验证，不构成正式显存或精度结论。
- 按 `gesture.data` 的 `saveweights=10`、`savelast=5` 和 cfg 基名，拟用初训输出 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\backup\gesture_yolov4_tiny_416_short_10.weights`；相关 `_last.weights`、`_20.weights`、`_final.weights` 候选在停止前均不存在。

## 输入绑定哈希

| 文件 | SHA-256 |
|---|---|
| `D:\FPGA_Data\HaGRIDv2\manifest.csv` | `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.data` | `379e02c6a68ccea896f5f16375879d0a52b698a66bd05dfcc7eba66c2068e3c8` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names` | `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\train.list` | `4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\valid.list` | `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c` |
| `D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_approval.json` | `90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213` |
| `D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json` | `9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be` |
| `D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v3.json` | `fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11` |

`.data`、names、train/valid list 未修改；其相对路径解析工作目录仍为 `D:\FPGA_Data\HaGRIDv2\darknet_inputs`。

## 权重下载尝试

- URL：`https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.conv.29`
- 目标：`D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29`
- 命令：`curl.exe -L --fail --retry 2 --silent --show-error --output D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29 https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.conv.29`
- 退出码：`23`
- stderr：`curl: (23) client returned ERROR on write of 12402 bytes`
- 收尾只读检查：目标文件不存在；大小、SHA-256 均不可用；没有覆盖既有文件。
- 因此没有执行自动下载以外的替代来源，也没有把权重上传、复制到仓库或加入 Git。

## 未执行项

- cfg 独立静态检查：未执行（按下载失败停止条件）。
- `verification/s1_t01_darknet_workflow.py train --dry-run`：未执行，没有生成 `PLANNED_NO_EXECUTION` 报告。
- vcvars64 + CUDA DLL PATH 运行：未执行 Darknet。
- cfg/输入绑定回归、py_compile：未执行；`git diff --check`：已执行，退出码 `0`。
- train、resume、evaluate、checkpoint 生成、逐图评估、精度/损失判断：全部未执行。
- 不得据此宣称 AC05、AC06、AC07、S1-T01 或阶段1通过。

## 恢复条件

先解决官方权重下载写入失败，确保目标文件为非零、非 HTML、可读取的官方 `yolov4-tiny.conv.29`，再只读核对大小和 SHA-256；随后重新做 cfg 静态检查、输入哈希复核和指定 `train --dry-run`。恢复时仍须先检查既有进程和 checkpoint 候选，且不得自动启动真实训练。

本轮 Developer 未提交 Git，仓库新增本证据文件和外部 cfg 属于本轮未提交变更。
