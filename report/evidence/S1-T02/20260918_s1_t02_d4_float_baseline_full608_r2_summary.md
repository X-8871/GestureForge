# S1-T02-D4 官方 Darknet 浮点基线预检摘要

- 生成时间（UTC+8）：2026-09-18T21:02:39+08:00
- 计划：`D:\FPGA_Competition\report\evidence\S1-T02\20260918_s1_t02_d4_float_baseline_full608_r2_plan.json`，SHA-256 `08af1994a9c506735a359d45cdb6d29d20b002e6747c3e84397b81c7f5a5bcb2`
- 机器报告：`D:\FPGA_Competition\report\evidence\S1-T02\20260918_s1_t02_d4_float_baseline_full608_r2.json`，SHA-256 `271a582cc30fb61f1565cfbfdbddeb6711bcfb985d42775e444704d8dca51617`
- 状态：`BLOCKED`；schema_valid=True；errors=0
- pending：无
- 阻断：tiny416_pilot:Windows 0xC000013A 控制中止；未观察到 OOM/NaN/Inf/损坏输入/300 秒无进度，未生成 checkpoint。

## 语义边界

本证据绑定三种浮点模型的配置、数据、官方 Darknet 命令位置、版本和输入输出计划。官方源基线训练 RNG 使用 `time(0)` 且没有 CLI seed 参数；隔离 seeded 副本已应用 `GESTUREFORGE_DARKNET_SEED` patch 并完成构建/seed smoke，固定 seed 不等于 bit-exact。
正式 test、robustness、mAP、最终精度、INT8 整网、Vivado 综合、烧录和板上测量均未执行；tiny320/full pilot 未启动。tiny416 pilot 已启动但 8/100 后以 `0xC000013A` 中止且未生成 checkpoint，保持 BLOCKED。full 缺少 `yolov4.conv.137` 时保持 PENDING，不下载、不伪造。

## 复现入口

`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B verification/s1_t02_d4_float_baseline.py validate --input report/evidence/S1-T02/20260918_s1_t02_d4_float_baseline_full608_r2_plan.json --report report/evidence/S1-T02/20260918_s1_t02_d4_float_baseline_full608_r2.json --summary report/evidence/S1-T02/20260918_s1_t02_d4_float_baseline_full608_r2_summary.md`

检查器会拒绝输入和输出同路径；所有路径比较使用规范化解析结果；本报告只记录 pilot，不会自动启动训练。

## full608 r2 输入与运行状态

- full 角色保持 `pc_only_reference`、608×608、5 类、3 个官方 YOLO head；训练参数沿用 batch=64、subdivisions=32、learning_rate=0.0013、momentum=0.9、decay=0.0005、burn_in=1000、max_batches=6000、steps=4800/5400。命令顺序仍为 seeded `darknet.exe detector train <data> <cfg> <initial_weight> -dont_show`。
- 初始化权重 `D:\FPGA_Data\darknet\weights\yolov4.conv.137`：170,038,676 bytes，SHA-256 `11c5286cfbffabc9a3059927401ab3480e9483ceafd3265779a0dc26c769bed0`；绑定 W5 r5 来源报告 SHA-256 `768022d56bde61f4b7b24623b76ce0c0ab3edea0252a6afb4b7d1b6e72fe6fc8` 与独立 Reviewer PASS JSON SHA-256 `4510d18fc5e680cbf43e47c56c7643ded630cb49cfdb0071c11fa961c7a33600`。许可证仍为 `UNRESOLVED`。
- full cfg/data SHA-256 分别为 `da66c6f68dc8da821299c91f8ff8ce0773aa7e719d6bfd5944ea2e2b36e75ad5`、`7b15d354f560a9ad3b1186a1fa1169a3f0f77d560f6f96c24d8cb1eca8573a59`。计划输出 backup `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\checkpoints\full` 递归项目数为 0；D4 run 内无 lock、无 full608 checkpoint/log 冲突。
- 预检观察到 Darknet PID 10628，当前状态记录将其关联到 D8 tiny320 formal_r2；该进程共享 GPU，因此 full608 不在此次任务中启动，后续启动前仍须重查。Windows 进程命令行查询受访问拒绝限制；状态关联依据为 `.codex/STATE.md` 中 PID 快照。
- 本机 `py` launcher 不可用；实际使用 bundled Python 3.12.14 执行上面的等价校验命令，exit=0。D4 定向测试 `verification/test_s1_t02_d4_float_baseline.py` 为 22/22 OK；全量 `unittest discover -s verification -p test_*.py` 为 172 项 OK。
- 本证据只完成输入计划校验：full608 训练=`NOT_STARTED`；正式 mAP/test/robustness=`NOT_EXECUTED`。机器报告 `schema_valid=true`、`errors=[]`；整体 D4 状态仍为 `BLOCKED`，原因是既有 tiny416 pilot 中断，不代表 full608 训练或精度通过。
