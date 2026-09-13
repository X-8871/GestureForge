# S1-T01 G0 环境与数据清点证据

## 运行信息

- 日期：2026-09-13（UTC+8）
- 工程：`D:\FPGA_Competition`
- 工程分支：`main`
- 说明：本记录只保存只读清点结果，不代表 S1-T01 或阶段1通过。

## 检查方法

- 使用 PowerShell 清点 `data/` 目录及工程相关文件。
- 查询默认 `python` 和受控 Python 运行时版本。
- 在受控 Python 中检查 `numpy`、`torch`、`torchvision`、`cv2`、`yaml`、`ultralytics`、`onnx` 的导入可用性。
- 使用 `nvidia-smi` 查询 GPU 名称、显存和驱动版本。
- 查询 D 盘可用空间；未安装依赖、未下载数据、未启动训练。

## 实际结果

| 项目 | 结果 |
|---|---|
| 数据目录 | `data/` 只有 `README.md`，没有图片、标签、清单或哈希 |
| 默认 Python | 启动目标 `C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe` 失效 |
| 受控 Python | `3.12.14` |
| 可导入包 | `numpy` |
| 未就绪包 | `torch`、`torchvision`、`cv2`、`yaml`、`ultralytics`、`onnx` |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU |
| GPU 显存 | 8188 MiB |
| D 盘可用空间 | 306166423552 bytes |

## G0 判定

- AC01：未通过；设备可查询，但选定训练框架尚未就绪，尚未完成小张量设备运算。
- AC02—AC04：待数据来源、标签编码、框覆盖及遮挡/截断/多手规则确认后执行。
- AC05—AC07：未执行。
- G3：纯 PC 任务，不适用。
- 当前结论：S1-T01 G0 核验中，尚未通过；不得启动正式训练，不得宣称阶段1通过。
