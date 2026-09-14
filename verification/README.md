# 验证工程区

- `sandbox/`：临时模块验证工程。
- `sim_results/`：波形和仿真输出。
- `reports/`：综合、实现、资源和时序报告。
- `s1_t01_cuda_smoke.cu`：S1-T01 固定 CUDA 设备冒烟源程序；只做设备枚举、显存拷贝、四元素内核计算和结果校验，不启动训练。

在已安装 CUDA Toolkit 且 `nvcc` 位于 PATH 后，从工程根目录编译并运行：

```powershell
New-Item -ItemType Directory -Force build\s1_t01 | Out-Null
nvcc -O2 -o build\s1_t01\s1_t01_cuda_smoke.exe verification\s1_t01_cuda_smoke.cu
build\s1_t01\s1_t01_cuda_smoke.exe
```

只有进程退出码为 `0` 且输出包含 `S1_T01_CUDA_SMOKE_PASS` 时，才能把生成的可执行文件路径传给 `s1_t01_environment_probe.py`；编译产物不提交 Git。当前机器没有 `nvcc`，上述编译和运行尚未执行。

实验结论同步记录到 Obsidian 的 `03-实验记录/实验记录.md`。
