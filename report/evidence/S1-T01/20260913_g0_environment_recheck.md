# S1-T01 G0 环境与工程内容复核

## 运行信息

- 日期：2026-09-13（UTC+8）
- 工程：`D:\FPGA_Competition`
- 工程分支：`main`
- 复核目的：阶段1启动后更新 S1-T01 的环境、数据和模型文件状态。

## 实际结果

| 项目 | 结果 |
|---|---|
| 工程 Git | `main` 相对 `origin/main` ahead 6；既有 `vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr` 保持未提交改动 |
| 数据目录 | `data/` 只有 `README.md` |
| 工程内数据/模型 | 未发现图片、标签、`*.weights`、`*.cfg`、`*.pt`、`*.pth`、`*.onnx` 或 `*.safetensors` |
| 默认 Python | 启动目标失效 |
| 受控 Python | 3.12.14 |
| 可导入包 | `numpy` |
| 未就绪包 | `torch`、`torchvision`、`cv2`、`yaml`、`ultralytics`、`onnx` |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU，显存 8188 MiB；复核时空闲约 6977 MiB |
| CMake | 3.30.2 |
| CUDA 编译器 | `nvcc` 不在 PATH 或未安装 |
| D 盘 | 可用空间约 306166407168 bytes |

## 当前 G0 结论

- AC01：未通过；Darknet、CUDA 编译链和小张量设备运算尚未就绪。
- AC02：类别名称和顺序已由 Wong 确认；实际数据来源、许可记录和完整框示例待补。
- AC03—AC04：未执行；等待 HaGRIDv2 子集或 Wong 摄像头数据。
- AC05—AC07：未执行。
- G3：纯 PC 任务，不适用。
- 阶段结论：S1-T01 继续处于 G0 核验中；不启动正式长训，不宣称小样本流程通过或阶段1通过。
