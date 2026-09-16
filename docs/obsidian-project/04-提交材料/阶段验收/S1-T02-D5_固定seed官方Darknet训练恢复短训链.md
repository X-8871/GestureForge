# S1-T02-D5 固定 seed 的官方 Darknet 训练/恢复短训链

## 范围与状态

本记录只证明 tiny416 浮点模型的 seeded 官方 Darknet train/resume 短训链可执行。它不是正式模型、精度验收、mAP、INT8、full YOLOv4 训练或 Vivado/板上结论。D4 已证明该 seed 在 CUDA/并发条件下不是 bit-exact，因此本任务的候选状态为 `EXECUTED_REVIEW_REQUIRED`。

固定 seed 为十进制 `424242`，只注入 Darknet 子进程环境变量 `GESTUREFORGE_DARKNET_SEED`；未提供 `--darknet-seed` 时 workflow 保持未注入的兼容行为。父 Python 进程环境不得被修改。

## 固定执行绑定

- 模型：YOLOv4-tiny、416×416、RGB/CHW/255，五类固定 names。
- 官方 seeded executable：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\build_seeded_release_r2\Release\darknet.exe`，SHA-256 为 `01c96dccb902a3f1f776b1619188a30bef7b33bf5ed607f466de0b6eedf1635e`。
- official Darknet source：`D:\FPGA_Data\darknet`，现场 HEAD 为 `59596d7880f6504768df41d6daa586f5cb2b932f`；seed patch 与 D4 build 绑定见 D5 summary 的哈希表。
- workflow 的 canonical `data-root` 必须为 `D:\FPGA_Data\HaGRIDv2`，因为现有 dataset report/approval 的 `data_root` 绑定在该路径；Darknet `working-directory` 为 `D:\FPGA_Data\HaGRIDv2\darknet_inputs`。不能将 dataset root 错传为 `darknet_inputs`。
- train/resume cfg 均为隔离副本，唯一短训变化为 `max_batches=20`；`batch=64`、`subdivisions=16`、`learning_rate=0.00261`、`momentum=0.9`、`decay=0.0005`、`burn_in=1000`、`steps=4800,5400` 保持原 formal cfg 文本值。
- train data 使用 `saveweights=10`、`savelast=1`；resume 使用同一 cfg 基名但独立 data/backup 目录。

## 复现与停止条件

完整命令、cwd、退出码、日志/检查点 SHA 和 workflow JSON 位于本轮 evidence summary；命令必须使用 `shell=False` 等价的 workflow 入口，并临时向子进程继承 pthread/CUDA PATH。执行前检查 Darknet、Python、MSBuild 冲突进程及输出候选。OOM、NaN/Inf、损坏输入、Darknet 启动失败、日志超过300秒无增长或总超时900秒时立即停止；禁止覆盖既有 checkpoint。

train 成功后只允许以 train 生成的 numbered step10 checkpoint 为 resume 输入；resume 输出必须位于独立 backup，且输入 checkpoint 前后 SHA 相同。full、正式 test/mAP、INT8、Vivado 和板测均为 `NOT_EXECUTED`。
