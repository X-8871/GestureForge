# S1-T01-D4 第3轮修复摘要

时间：2026-09-15（UTC+8）

## 本轮关闭项

- 将审查输入基线修正为当前固定 HEAD `4a0278668aa91802e5e02c65c8083f4e3e574dbe`，保留“最终交付提交：待总控冻结并提交；本轮开发者按约定不提交”声明。
- 对哈希清单中的 41 个仓库/外部文件条目逐项使用 PowerShell `Get-FileHash -Algorithm SHA256` 重算；最终不一致数为 0。
- 两条 executable identity 与实际文件保持一致：Darknet `358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`，CUDA smoke `4abc2065f7d798685043dd8066bc231f0098285e0ff1d82e66b2b360c4a8480c`。

## 第3轮实际差异

- `report/evidence/S1-T01/20260914_sha256_manifest.txt`：新增“按当前候选工作树/外部数据重新核对”说明；更新审查输入基线；更新实际变化的 `data/README.md`、两份环境探针代码/测试、两份 HaGRID 审查文件和外部 `manifest.csv` 哈希。路径和条目集合未改变。
- 新增本摘要及 `20260915_round3_manifest_consistency.log`；未修改探针逻辑、测试逻辑、README、Darknet 源、`.codex/STATE.md` 或用户已有文件。

## 验证命令与结果

- `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest verification.test_s1_t01_environment_probe -v`：exit `0`，8 项全部 `OK`。
- `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m py_compile verification/s1_t01_environment_probe.py verification/test_s1_t01_environment_probe.py`：exit `0`。
- `git diff --check`：exit `0`；仅有 Git 的 LF/CRLF 提示。
- 在 `vcvars64.bat` 环境并将以下路径置于 PATH 前端后运行绝对路径 probe：
  `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\x64`、`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin`、`D:\FPGA_Data\darknet\3rdparty\pthreads\bin`。
- probe 命令：
  `C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe D:\FPGA_Competition\verification\s1_t01_environment_probe.py --darknet-executable D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe --cuda-smoke-executable D:\FPGA_Competition\build\s1_t01\s1_t01_cuda_smoke.exe --identity-manifest D:\FPGA_Competition\report\evidence\S1-T01\20260914_sha256_manifest.txt --report D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v3.json`
- probe exit `0`，`status=PASS`；nvidia-smi、nvcc、cmake、Darknet 两次探测和 CUDA smoke 的命令 exit 均为 `0`。

## 完整一致性结果

- 完整 41 项 `manifest/actual` 路径、大小写归一化 SHA-256 和 PASS 状态见 `20260915_round3_manifest_consistency.log`。
- probe JSON SHA-256：`fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11`。
- Darknet 产物为有效 PE，路径：`D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe`。
- CUDA smoke 路径：`D:\FPGA_Competition\build\s1_t01\s1_t01_cuda_smoke.exe`。
- 外部 Darknet HEAD：`59596d7880f6504768df41d6daa586f5cb2b932f`；`git -C D:\FPGA_Data\darknet diff --quiet` exit `0`。外部工作区仅有未跟踪 build 输出，不涉及源文件改动。

## 限制与阶段边界

此前 CUDNN 检查仍仅覆盖 `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4` 与 `D:\FPGA_Data\darknet\3rdparty`，不能解释为全盘缺失；详情见 `20260915_cudnn_check_after_install.md`。

本轮未执行 AC05、AC06、AC07；未启动训练、量化、RTL、烧录或阶段2。本证据不代表 S1-T01 或阶段1通过。按用户要求未提交 Git。
