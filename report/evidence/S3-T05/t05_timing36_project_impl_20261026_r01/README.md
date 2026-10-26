# TIMING-36 隔离工程实现尝试 r01

## 结果

Vivado 在隔离工程副本上成功打开项目，但脚本用 `get_files -all -quiet *rgb2dvi_clocks.xdc` 查询尚未注册的 IP 约束文件时返回 0 个对象，于退出码 1 安全停止。日志没有 `reset_run`、综合、实现或硬件操作记录；这属于脚本入口查询失败，不是设计或实现结果。原始脚本、stdout、stderr 与退出码保留。

此失败已由新 RunId r02 替代：r02 从本地 IP repository 生成 BD targets，再重新综合、路由并生成 bitstream；r01 不重跑、不覆盖。

## 固定基线与限制

- 起始项目快照目录：`D:/codex-worktrees/dbdf/tmp/s3r06/t04_sof_fix_20261020_r01/`
- 原项目 XPR SHA-256：`f7606f5b3a53a852b88f3494c35e552aaa3861a7270b71354e8e9a73796c2087`
- 原 RGB2DVI 时钟 XDC SHA-256：`e6ceadc3fcfcf59fe1f5eaf13f8f94d862e9513ad6cd2e850a035c312c8d2002`
- Vivado：2026.1 Build 6511674；目标器件由 XPR 指定 `xc7z020clg400-2`
- 项目文件来自隔离临时快照；未修改其原件、`D:/FPGA/AX7Z020` 或其他工作树。
- 退出码 1 仅表示脚本在 IP 文件查找门禁停止；它不代表实现失败或通过。
