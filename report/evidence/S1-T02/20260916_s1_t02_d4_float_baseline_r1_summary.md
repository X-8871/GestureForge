# S1-T02-D4 官方 Darknet 浮点基线预检摘要

- 生成时间（UTC+8）：2026-09-16T17:43:43+08:00
- 计划：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1_plan.json`，SHA-256 `63f569005239d76ec44629271a7db0280fd584210dd51f51fe8b7e8df2d14ff5`
- 机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1.json`，SHA-256 `4bbda22f0feb0df1edf5e82701f539ecfe9ac08565d4540ece72364ebcaae7d8`
- 状态：`BLOCKED`；schema_valid=True；errors=0
- pending：full.initial_weight
- 阻断：tiny416_pilot:Windows 0xC000013A 控制中止；未观察到 OOM/NaN/Inf/损坏输入/300 秒无进度，未生成 checkpoint。

## 语义边界

本证据绑定三种浮点模型的配置、数据、官方 Darknet 命令位置、版本和输入输出计划。官方源基线训练 RNG 使用 `time(0)` 且没有 CLI seed 参数；隔离 seeded 副本已应用 `GESTUREFORGE_DARKNET_SEED` patch 并完成构建/seed smoke，固定 seed 不等于 bit-exact。
正式 test、robustness、mAP、最终精度、INT8 整网、Vivado 综合、烧录和板上测量均未执行；tiny320/full pilot 未启动。tiny416 pilot 已启动但 8/100 后以 `0xC000013A` 中止且未生成 checkpoint，保持 BLOCKED。full 缺少 `yolov4.conv.137` 时保持 PENDING，不下载、不伪造。

## 复现入口

`py verification/s1_t02_d4_float_baseline.py validate --input "D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1_plan.json" --report "D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1.json" --summary "D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1_summary.md"`

检查器会拒绝输入和输出同路径；所有路径比较使用规范化解析结果；本报告只记录 pilot，不会自动启动训练。
