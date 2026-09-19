# S1-T02-D4 full608 加速诊断短跑证据

- 任务：`S1-T02-D4-ACCEL-BENCH-EVIDENCE`
- 生成时间（UTC+8）：`2026-09-19T17:13:38+08:00`
- 状态：**仅诊断证据**，不构成正式 6000 步训练、精度或阶段通过。
- 外部运行目录：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_accel_bench_r1`
- 证据 JSON：`D:\FPGA_Competition\report\evidence\S1-T02\20260919_s1_t02_d4_full608_accel_bench_r1.json`

## 结果

| 配置 | 结果 | 步数 | 每步耗时 | 权重 | 限制 |
|---|---|---:|---:|---|---|
| `subdiv64` | 完成短跑 | 20/20 | 均值 24.379s，中位数 24.334s | 已生成 `final.weights` | 包装层未生成 `runner_result.json`，child 数值退出码未知 |
| `subdiv16` | CUDA OOM | 0/20 | 未进入训练步 | 未生成 | OOM 发生在第 1 步前的 `cuda_make_array()` 分配 |

`subdiv64` 日志包含 1–20 的完整步摘要，最终写出独立权重；`subdiv16` 日志在 `dark_cuda.c: cuda_make_array(), line #484` 处报告 `CUDA Error: out of memory`，发生在第 1 步前；其 checkpoint 目录为空。报告生成时未发现 Darknet 进程。

## 输入绑定

两个 subdivision 均通过各自的 10 条 preflight SHA-256/大小记录，包含 manifest、train/valid list、names、对应 `.data`、两份 cfg、初始化权重、Darknet 可执行文件和环境报告；两份 preflight 的记录均匹配且无 mismatch。完整记录、路径、字节数、时间和 SHA-256 见 JSON。

## 解释边界

本短跑用于比较显存安全性和运行速度。它没有进行独立 GPU 推理、验证集指标、官方 test、robustness、INT8 或板上验证；不能把 `subdiv64` 的短跑权重当作正式模型，也不能据此宣布阶段验收通过。`runner_result.json` 缺失是本次监视器包装层的限制，JSON 中已显式记录。

