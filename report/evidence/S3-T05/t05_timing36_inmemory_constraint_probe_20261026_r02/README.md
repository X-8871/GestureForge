# TIMING-36 时钟对象内存诊断尝试 r02

## 结论

固定 routed DCP 成功打开；r02 的层级对象过滤与精确 `NAME` 比较成功，确认待诊断对象为生成时钟 `design_1_i/rgb2dvi_0/U0/SerialClk`，其 master 为 `axi_dynclk_0_PXL_CLK_O`、周期 2.000 ns；集成端口 `design_1_i/rgb2dvi_0/SerialClk` 在变更前关联自动衍生时钟 `I`。

原计划使用 `delete_clocks` 仅移除一个错误生成时钟，但 Vivado 2026.1 中 `[info commands delete_clocks]` 返回 0 个命令。脚本据此在任何对象修改前安全退出，退出码 4。**没有执行时钟删除，没有生成修复报告，也没有证明删除错误约束后时钟 `I` 会保留。** 本 RunId 是失败的 API 可用性探测，不是约束修复。

## 边界与输入

- 输入 DCP：`D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper_routed.dcp`
- DCP SHA-256：`17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728`
- Vivado：2026.1 Build 6511674；器件 `xc7z020clg400-2`
- 只读打开 checkpoint 并查询对象；未写回 checkpoint/XDC，未综合/实现，未连接或操作硬件。
- stdout/stderr、退出码与脚本为原始/可复现记录；不覆盖此前 r01 失败。

## 复现与验证

在项目工作树根目录调用 `vivado.bat -mode batch -nojournal -source report/evidence/S3-T05/t05_timing36_inmemory_constraint_probe_20261026_r02/probe_in_memory_clock_removal.tcl`。使用项目捆绑 Python 执行本目录 `validate_probe_outputs.py`，验证输入标记、对象关联、API 缺失、无错误 stderr 和退出码。

## 后续

若继续做内存诊断，应使用 Vivado 当前版本正式支持的时序约束重置与受控重载方式，并在新 RunId 中先绑定完整约束集与 XDC 读取顺序。不得把本次 API 探测升级为修复、时序签核或阶段 G5 结论。基线时钟拓扑分析见 `../t05_timing36_source_probe_20261026_r02/README.md`。
