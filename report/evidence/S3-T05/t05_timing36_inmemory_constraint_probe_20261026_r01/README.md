# TIMING-36 时钟对象内存诊断尝试 r01

## 结论

本次尝试失败于 Tcl 对象查询，不构成设计结论。固定 routed DCP 已成功只读打开，但 `get_pins -quiet -hier {design_1_i/rgb2dvi_0/SerialClk}` 返回 0 个对象，脚本以 Vivado 进程退出码 1 结束。该查询形式与实际对象名不匹配；后续 r02 改用层级过滤并逐字符核对 `NAME`。

## 边界与输入

- 输入 DCP：`D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp`
- DCP SHA-256：`17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`
- Vivado：2026.1 Build 6511674；器件 `xc7z020clg400-2`
- 仅打开并查询 DCP；未写回 checkpoint/XDC，未进行综合/实现，未连接或操作硬件。
- stdout/stderr 为工具原始输出；退出码单独记录为 1。该失败包保留，不覆盖或删除。

## 复现

在项目工作树根目录调用 `vivado.bat -mode batch -nojournal -source report/evidence/S3-T05/t05_timing36_inmemory_constraint_probe_20261026_r01/probe_in_memory_clock_removal.tcl`。脚本固定 DCP 路径及只读探测范围。

## 判定限制

该失败只说明 r01 的对象查询表达式无匹配，不影响此前 r02 时钟拓扑探测，也不表示 TIMING-36 已修复或阶段 G2/G3/G4/G5 通过。
