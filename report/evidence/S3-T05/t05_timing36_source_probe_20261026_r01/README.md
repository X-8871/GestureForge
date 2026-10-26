# TIMING-36 时钟源探测调用失败记录

- RunId：`t05_timing36_source_probe_20261026_r01`
- 执行时间：2026-10-26 12:19:35–12:19:43（UTC+8）
- 源工作树 HEAD：`beab61e1a987798774678fc05baae5dcff472b9d`
- 目标 DCP：`tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp`
- 目标 DCP SHA-256：`17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`

## 结果

Vivado 2026.1 BASIC 许可证已识别，但从 PowerShell 直接调用批处理启动器时，Tcl 脚本收到的 `argv` 为空。脚本在 `open_checkpoint` 之前按参数数量保护退出，Vivado 退出码为 `2`。stdout 保留了脚本用法错误；stderr 为空。

因此本次没有读取 DCP，也没有生成时钟结果，更没有更改设计、约束或硬件。该失败是调用参数未传入，不是设计或 Vivado 许可证失败。日志与脚本按原样保留；后续使用固定路径的独立 RunId 执行，见相邻的 `t05_timing36_source_probe_20261026_r02/`。

## 文件

- `probe_clocks.tcl`：失败调用所用脚本，要求两个 Tcl 参数。
- `stdout.txt`、`stderr.txt`：Vivado 原始输出。
- `source_provenance.json`：机器可读绑定启动命令、工作树 HEAD、目标 DCP 哈希及未实际读取说明。
- `delivery_manifest.json`：文件哈希、尝试命令、输入身份及失败状态。

本 RunId 仅作为失败调用证据，不是 TIMING-36 修复或阶段3验收结论。
