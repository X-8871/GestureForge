# S1-T01-D4 第1轮修复交付摘要

时间：2026-09-15（UTC+8）

## 固定身份与边界

- 官方仓库：`https://github.com/AlexeyAB/darknet.git`
- 源目录：`D:\FPGA_Data\darknet`
- 固定提交：`59596d7880f6504768df41d6daa586f5cb2b932f`
- `git diff --quiet`（外部源文件）：退出码 `0`。外部目录仅有本轮隔离构建目录未跟踪项，没有源文件修改。
- 未启动训练、量化、RTL、烧录或真实照片上传。
- CUDNN 直接核查未发现 `cudnn.h`、`cudnn*.dll`、`cudnn.lib`；最终配置保持 `ENABLE_CUDNN=OFF`。

## 最终 CMake 配置

构建目录：`D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2`

配置命令在 `vcvars64.bat` 环境、`CUDA_PATH_V13_4=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4`、`CUDACXX=nvcc.exe` 下执行，退出码 `0`：

```powershell
cmake -S D:\FPGA_Data\darknet -B D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2 -G "Visual Studio 17 2022" -T cuda=13.4 -A x64 -DENABLE_CUDA=ON -DENABLE_CUDA_OPENGL_INTEGRATION=OFF -DENABLE_CUDNN=OFF -DENABLE_CUDNN_HALF=OFF -DENABLE_OPENCV=OFF -DBUILD_SHARED_LIBS=OFF -DBUILD_USELIB_TRACK=OFF -DCMAKE_CUDA_ARCHITECTURES=89
```

缓存核对：CUDA ON、CUDA OpenGL integration OFF、CUDNN OFF、OpenCV OFF、架构 `89`、生成器工具集 `cuda=13.4`。

## 实际构建与运行

```powershell
cmake --build D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2 --config Release --target darknet -- /m:2 /verbosity:minimal
```

- 构建退出码：`0`
- 输出：`D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe`
- PE：探针确认有效 Windows PE；文件大小 `3030528` 字节
- Darknet SHA-256：`358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`
- `darknet.exe --version`：退出码 `0`，该提交输出 `Not an option: --version`，不作为识别依据。
- `darknet.exe` 帮助：退出码 `0`，输出 `usage: ...darknet.exe <function>`，探针据此确认 Darknet。

构建完整 stdout/stderr 与退出码：`20260915_darknet_cmake_build_release.md`。

## CUDA smoke

- 源：`D:\FPGA_Competition\verification\s1_t01_cuda_smoke.cu`
- `nvcc -O2` 首次运行退出码 `2`：PTX 使用了不受支持的 toolchain；原始 stderr 已保留。
- `nvcc -O2 -arch=sm_89 ...` 编译退出码 `0`。
- 运行退出码 `0`，输出 `S1_T01_CUDA_SMOKE_PASS device=0 name=NVIDIA GeForce RTX 4060 Laptop GPU`。
- 可执行文件：`D:\FPGA_Competition\build\s1_t01\s1_t01_cuda_smoke.exe`
- SHA-256：`4abc2065f7d798685043dd8066bc231f0098285e0ff1d82e66b2b360c4a8480c`
- 记录：`20260915_s1_t01_cuda_smoke_sm89.md`。

## 环境 probe

运行目录为 Darknet Release 目录，显式传入 `darknet.exe`、smoke exe、身份清单和报告；CUDA `bin\\x64`、`bin`、PThreads4W bin 均在 PATH。完整命令/环境/日志/报告摘要见 `20260915_environment_probe_after_install.md`。

- probe 退出码：`0`
- report status：`PASS`
- nvidia-smi、nvcc、cmake、darknet、cuda_device_smoke：全部通过，命令退出码均为 `0`
- 报告：`20260915_environment_probe_after_install.json`
- 报告 SHA-256：`a0265a4446d7b45142cd4a40fb0080f7ad93c01bfaba85097360f8f69fc6b88b`

## 本轮失败尝试

- 首选 Makefile `GPU=1 CUDNN=1 CUDNN_HALF=1 OPENCV=0`：退出码 `2`，Windows shell 下 `uname`/目录规则不兼容；CUDNN 文件也确实不存在。
- Makefile 最小 CUDA 轮次：依次记录 `-rdynamic` 不支持、CUDA 头路径不适配、MinGW GCC 8.1 win32 线程模型下 `std::mutex` 不可用。
- CMake 前置配置轮次：记录了生成器参数拆分、CUDA compiler 未发现、VS targets 缺少 `CUDA_PATH_V13_4` 的真实错误；最终通过设置版本化 CUDA 路径变量和 `-T cuda=13.4` 修正。

上述各轮完整证据在同目录的 `20260915_darknet_make_*.md`、`20260915_darknet_cmake_configure_*.md` 及对应 stdout/stderr 日志中。

## 仓库文件变更

- `verification/README.md`：移除过时的“当前机器没有 nvcc/尚未执行”描述，改为安装后验证说明，并注明本次 `sm_89` 真实通过、构建产物不提交。
- `report/evidence/S1-T01/20260914_sha256_manifest.txt`：仅替换两条 identity 的 `UNAVAILABLE` 为上述真实 SHA-256。
- 新增本目录本轮命令、日志、JSON 和摘要证据；构建产物未纳入 Git 提交。
- 用户已有 docs/obsidian-project、Vivado、JPG 改动未触碰。

本证据不表示 S1-T01、阶段1或任何训练/板上验收通过。
