# S1-T01-D4 第2轮修复交付摘要

时间：2026-09-15（UTC+8）

## 修复内容

- `verification/s1_t01_environment_probe.py`：Darknet 输出识别按精确 basename `darknet`/`darknet.exe` 处理，支持相对路径、绝对 Windows 路径和 Unix 风格路径；`notdarknet.exe` 不匹配。未放宽 PE、身份 SHA-256 或实际命令检查。
- `verification/test_s1_t01_environment_probe.py`：新增 1 个最小回归测试，覆盖 4 个可接受路径输出和 `notdarknet.exe` 拒绝。
- `verification/README.md`：smoke 编译命令加入 `-arch=sm_89`，并说明必须在 `vcvars64.bat` 和 CUDA PATH 环境中运行。
- `report/evidence/S1-T01/20260914_sha256_manifest.txt`：只更新 `verification/README.md` 条目；两条 executable identity 保持真实值。

## 实际验证命令与结果

```powershell
python -m unittest verification.test_s1_t01_environment_probe -v
```

退出码：`0`，共 `8` 项通过。

```powershell
python -m py_compile verification/s1_t01_environment_probe.py verification/test_s1_t01_environment_probe.py
```

退出码：`0`。

```powershell
git diff --check
```

退出码：`0`。

单测与 py_compile 记录：`20260915_round2_validation.md` 及对应 stdout/stderr 日志。

## 绝对路径环境 probe

在 `vcvars64.bat` 环境中，PATH 前缀包含：

- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\x64`
- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin`
- `D:\FPGA_Data\darknet\3rdparty\pthreads\bin`

实际命令：

```powershell
python D:\FPGA_Competition\verification\s1_t01_environment_probe.py --darknet-executable D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe --cuda-smoke-executable D:\FPGA_Competition\build\s1_t01\s1_t01_cuda_smoke.exe --identity-manifest D:\FPGA_Competition\report\evidence\S1-T01\20260914_sha256_manifest.txt --report D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v2.json
```

- probe 退出码：`0`
- report status：`PASS`
- `nvidia_smi`、`nvcc`、`cmake`、`darknet`、`cuda_device_smoke`：全部通过，命令退出码均为 `0`
- 报告：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v2.json`
- 报告 SHA-256：`3e2b8233c3f17bae315748d056f938f3dab0c546b4bcf5331eab1392aaba41a8`
- 完整命令、环境、stdout/stderr：`20260915_environment_probe_after_install_v2.md` 及对应日志。

## 身份绑定

- README SHA-256：`46e1ac6c1646065dd0e9f6db4dd7b2c8389b0c29c740536a84d1e7ef7367f3c6`
- Darknet SHA-256：`358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`
- CUDA smoke SHA-256：`4abc2065f7d798685043dd8066bc231f0098285e0ff1d82e66b2b360c4a8480c`
- 清单两条 executable identity 与实际文件摘要一致；README 条目与实际摘要一致。

## CUDNN 定向证据

`20260915_cudnn_check_after_install.md` 记录了对以下两个根目录和指定模式的实际 PowerShell 搜索：

- `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4`
- `D:\FPGA_Data\darknet\3rdparty`
- `cudnn.h`、`cudnn*.dll`、`cudnn.lib`

匹配数为 `0`，搜索退出码为 `0`；该结果不扩展为全盘缺失结论。

外部 Darknet commit 仍为 `59596d7880f6504768df41d6daa586f5cb2b932f`，源文件 `git diff --quiet` 退出码为 `0`。未修改 `.codex/STATE.md`、用户已有 docs/Vivado/JPG；未训练、未量化、未烧录、未上传照片、未提交 Git。本证据不表示 S1-T01 或阶段1通过。
