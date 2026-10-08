# CUDNN 安装后定向核查

时间：2026-09-15（UTC+8）

本次只核查以下明确范围，不将结果表述为全盘缺失：

- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4`
- `D:\FPGA_Data\darknet\3rdparty`

实际 PowerShell 命令：

```powershell
$searchRoots = @("C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4", "D:\FPGA_Data\darknet\3rdparty")
$filePatterns = @("cudnn.h", "cudnn*.dll", "cudnn.lib")
Get-ChildItem -LiteralPath $searchRoots -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $filePatterns -contains $_.Name -or ($_.Name -like "cudnn*.dll") }
```

结果：两个搜索根目录均存在；匹配文件数为 `0`；PowerShell 搜索退出码为 `0`。本次范围内没有发现 `cudnn.h`、`cudnn*.dll` 或 `cudnn.lib`。未修改 CUDA 安装或 Darknet 源目录。
