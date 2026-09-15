# 第3轮 probe 首次失败尝试记录

时间：2026-09-15（UTC+8）

首次尝试通过 `cmd.exe /d /s /c` 调用 `vcvars64.bat` 和 environment probe；命令目标使用真实绝对 Darknet、CUDA smoke、identity manifest 路径。PowerShell 命令包装中 PThreads 变量赋值漏写 `$`，实际 PATH 只有 CUDA `bin\\x64`、CUDA `bin` 和空项，未加入 `D:\FPGA_Data\darknet\3rdparty\pthreads\bin`。

- 实际 probe exit：`2`
- Darknet 探测返回：`3221225781`（缺少 PThreads 运行时 DLL，未将其解释为构建或源码失败）
- CUDA smoke 探测：exit `0`
- 随后已修正 PATH 并重新执行同一绝对路径 probe；最终 exit `0`、`status=PASS`，结果见 `20260915_environment_probe_after_install_v3.json` 及同名 stdout/stderr 日志。

未删除、覆盖或重置外部 Darknet 源目录；该失败不代表最终环境 probe 结果。
