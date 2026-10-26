# S4-T26 T29 控制实验

## 结论

**BLOCKED：T29 冻结控制样本的 layer 29 和 layer 36 量化结果均未逐字节匹配。立即停止，不生成校准样本黄金或 task-27 输入。**

## 运行

- RunId：`s4t26_golden_control_20261026_r04`；离线 Darknet 进程 exit `0`，耗时 1.297 秒（CUDA 13.03，RTX 4060 Laptop GPU）。
- 输入：`test_fist_000`，SHA256 `6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e`；EXE SHA `879148e06aeaa250667c63ada108c10723d4e8056697352f6d9149b1f5ce1289`；hook SHA `ef907ba3f7bbe43b1eeac6f6647fc1b1b6ebea32721fbf7bf95658033f2d196f`。
- 命令、stdout/stderr、全量 hook index/stats 与 float dump 均在本 RunId；本次进程 PATH 仅前置已存在的 pthread DLL 目录。

## 逐字节对拍

| 层 | 冻结 scale | float 数 | 不同 INT8 字节 | 结果 |
|---:|---:|---:|---:|---|
| 29 / head13 | 0.24267549589862975 | 5,070 | 2,929 | FAIL |
| 36 / head26 | 0.30223452951025775 | 20,280 | 10,358 | FAIL |

量化调用现有 `round_away_array` 与 `saturate_array`，舍入为半数远离零，饱和范围 `[-127,127]`。详细候选/参考 SHA 见 `control_comparison.json`。

## 停止项

- G0 r12 已按要求只读核验校准图像路径与 SHA（`c116ba1d…35ee70b`）；由于控制不匹配，未对该图像执行前向，未生成 head13/head26 新黄金或 producer/activation 记录。
- task-26 校准真实前向、D9/NMS、负向对照、PNG `IMREAD_UNCHANGED` 检查均 `NOT_RUN`；task-27 包未生成。
- ENABLE=0；RAW G0 未闭合；P、4-D、G3、G5 均 `NOT_RUN`。本结果仅为离线主机控制样本，不构成实时/板级/阶段验收。
- Darknet stderr 中存在 data-file 标签扫描路径缺失警告，完整内容保存在 `darknet.stderr.txt`；指定测试图仍执行并产生目标层 dump。
