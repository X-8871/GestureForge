# 工程脚本

保存工程重建、数据预处理、模型导出、结果比对和批量验证脚本。脚本应注明输入、输出和使用方式。

## S1-T01 数据检查

当前 S1-T01 的数据检查器位于 `verification/s1_t01_dataset_check.py`，使用受控 Python 运行时和外部 UTF-8 CSV 清单；不自动下载 HaGRIDv2，不自动安装 Darknet/CUDA，不启动正式长训。命令与清单接口见 `data/README.md`。

HaGRIDv2 标签转换器位于 `verification/s1_t01_prepare_hagrid.py`，逐个读取目标类别/划分 JSON，递归适配官方 ZIP 嵌套目录，生成五类 YOLO 标签和 `manifest_all.csv`。清洁器位于 `verification/s1_t01_filter_manifest.py`，根据完整 SHA-256 重复分析结果按 `train > val > test` 移除跨 split 重复行，不删除原始图片或标签。两者均使用 UTF-8，失败时不发布半成品正式清单。

环境探针位于 `verification/s1_t01_environment_probe.py`，固定检查官方 Darknet/CUDA 路线、GPU、`nvcc`、Darknet 版本/帮助输出和明确的 CUDA 设备冒烟程序；未提供 Darknet 或设备冒烟程序时保持失败，不自动切换框架。设备冒烟程序只有在退出码为 0 且输出包含 `S1_T01_CUDA_SMOKE_PASS` 时才算通过：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_environment_probe.py `
  --darknet-executable 'D:\darknet\darknet.exe' `
  --cuda-smoke-executable 'D:\darknet\s1_t01_cuda_smoke.exe' `
  --report report\evidence\S1-T01\<运行编号>_environment_probe.json
```

Darknet 必须通过 PE 文件检查和版本/帮助命令；CUDA 冒烟程序必须退出码为 0 且输出 `S1_T01_CUDA_SMOKE_PASS`。任一条件缺失都保持失败，不自动切换框架或把 `nvidia-smi` 查询当作设备张量运算。

在正式数据到位后运行：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py `
  --data-root 'D:\FPGA_Data\HaGRIDv2' `
  --manifest 'D:\FPGA_Data\HaGRIDv2\manifest.csv' `
  --report report\evidence\S1-T01\<运行编号>_dataset_check.json `
  --preview-dir report\evidence\S1-T01\<运行编号>_previews
```

恢复/重建标签时先确认没有同名进程，再执行：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_prepare_hagrid.py `
  --data-root 'D:\FPGA_Data\HaGRIDv2' `
  --manifest 'D:\FPGA_Data\HaGRIDv2\manifest_all.csv' `
  --labels-root 'D:\FPGA_Data\HaGRIDv2\labels' `
  --report report\evidence\S1-T01\<运行编号>_prepare.json
```

清洁器需要已有的完整重复分析日志；它只改写清单，不删除图片/标签：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_filter_manifest.py `
  --input 'D:\FPGA_Data\HaGRIDv2\manifest_all.csv' `
  --output 'D:\FPGA_Data\HaGRIDv2\manifest.csv' `
  --duplicate-report report\evidence\S1-T01\<重复分析日志> `
  --report report\evidence\S1-T01\<运行编号>_filter.json
```

无外部数据时只运行单元测试，不用合成图片宣称 AC03/AC04 通过：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest verification.test_s1_t01_dataset_check -v
```
