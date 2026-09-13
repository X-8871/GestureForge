# 工程脚本

保存工程重建、数据预处理、模型导出、结果比对和批量验证脚本。脚本应注明输入、输出和使用方式。

## S1-T01 数据检查

当前 S1-T01 的数据检查器位于 `verification/s1_t01_dataset_check.py`，使用受控 Python 运行时和外部 UTF-8 CSV 清单；不自动下载 HaGRIDv2，不自动安装 Darknet/CUDA，不启动正式长训。命令与清单接口见 `data/README.md`。

环境探针位于 `verification/s1_t01_environment_probe.py`，固定检查官方 Darknet/CUDA 路线、GPU、`nvcc` 和受控 Python；未提供 Darknet 可执行文件时保持失败，不自动切换框架：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_environment_probe.py `
  --report report\evidence\S1-T01\<运行编号>_environment_probe.json
```

在正式数据到位后运行：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py `
  --data-root 'D:\GestureForgeData\s1_t01' `
  --manifest 'D:\GestureForgeData\s1_t01\manifest.csv' `
  --report report\evidence\S1-T01\<运行编号>_dataset_check.json `
  --preview-dir report\evidence\S1-T01\<运行编号>_previews
```

无外部数据时只运行单元测试，不用合成图片宣称 AC03/AC04 通过：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest verification.test_s1_t01_dataset_check -v
```
