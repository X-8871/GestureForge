# S1-T02-D4 fixed608/random=0 CPU/RAM 隔离诊断

- 任务：`S1-T02-D4-DIAG-FIXED608-R1`
- 状态：**DIAGNOSTIC_ONLY_NO_FORMAL_TRAINING**
- 目录：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r4_subdiv64\cpu_ram_diag_fixed608_r1`
- 现场工作目录：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\build_seeded_release_r2\Release`；PATH 前缀为 `D:\FPGA_Data\darknet\3rdparty\pthreads\bin` 与 CUDA x64。
- 证据 JSON：`D:\FPGA_Competition\report\evidence\S1-T02\20260919_s1_t02_d4_full608_fixed608_diag_r1.json`

## 结果

从 formal 1000 checkpoint 启动独立 `diag.cfg`/`diag.data`，配置为 batch=64、subdivisions=64、608×608、max_batches=1010、random=0、seed=424242。日志完整记录 `1001/1010` 至 `1010/1010`，共 10 步；实际每步耗时范围 **11.286–11.624 s**，其中主体约为 11.334–11.624 s。stdout 未出现动态 `Resizing`，stderr 无 CUDA Error、OOM、NaN、Inf 或 calloc error 关键词，并写出 `diag_final.weights`。

`diag_final.weights` 大小为 256,102,140 字节，SHA-256：`18E2B7B1F4824B8E9FA7F819A139F29080495FCADEFE922BD48306573FE08D4E`。数值 exit code 未被 detached wrapper 持久化，证据中标记为 `UNKNOWN_NOT_CAPTURED`；日志完成提示不能替代数值退出码。启动 PID 记录为 wrapper `25504`、child `25492`；结束快照未发现 Darknet 或上述 PID 残留。

## 限制

该诊断使用 `random=0`，正式训练使用 `random=1`；它只有 10 步，不能代表正式 6000 步训练、模型质量、精度、泛化、INT8 或阶段验收。完整路径、大小、哈希、逐步时间和限制见 JSON。
