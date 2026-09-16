# S1-T02-D4 官方 Darknet 浮点基线与可复现执行

## 目的与边界

本任务只建立 YOLOv4-tiny 320、YOLOv4-tiny 416 和完整 YOLOv4 608 PC 对照的官方 Darknet 浮点执行绑定，并记录有限短程预检。它不冻结最终模型、输入尺寸、精度指标或上板性能，不执行 official test、robustness、mAP、INT8 整网、Vivado 综合、烧录或板上测试。

完整机器计划、现场版本和运行产物见：

`report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1_plan.json`

`report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1.json`

`report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1_summary.md`

## 绑定 schema

计划 JSON 使用 `s1-t02-d4-v1`。顶层必须包含 `source`、`build`、`seed`、`data`、`models`、`file_bindings`、`pilot` 和 `formal_evaluation`。

- `source`：官方源仓库、现场 `rev-parse HEAD`、`diff --quiet` 退出码、隔离副本、patch 和 network_access=false。官方源与 seeded 副本分开记录；隔离副本每个修改源文件都要现场核对 SHA-256。
- `build`：隔离构建目录、CMake 参数、CUDA 架构、配置/构建退出码、configure/build 日志 SHA 和可执行文件 SHA-256；可执行文件必须位于该隔离构建目录。
- `seed`：`GESTUREFORGE_DARKNET_SEED` 必须是非负 32 位十进制整数；记录 patch SHA、覆盖的源文件、每个 seed smoke 的退出码/seed/日志/checkpoint SHA、`bit_exact=false` 及 CUDA/线程并发限制。
- `data`：五类 names、原始 train/valid 清单、manifest、数量和 SHA-256；训练使用 train，正式 test 在后续任务执行。
- `preprocessing`：D2 参考实现路径必须存在，`reference_sha256` 必须是现场计算的完整 64 位 SHA-256；该引用与三种模型共用的 RGB/letterbox/CHW/255 口径绑定。
- `models`：模型键、角色、输入尺寸、五类检测头、anchors/masks、cfg/data/初始权重绑定和官方 argv。checker 会读取 formal cfg 的实际 `[net]` 字段并逐项核对 batch、subdivisions、learning_rate、momentum、decay、burn_in、max_batches、steps；pilot cfg 单独记录，不套用 formal max_batches。正式参数为 batch=64、tiny subdivisions=16、full subdivisions=32、SGD momentum=0.9、decay=0.0005、tiny learning_rate=0.00261、full learning_rate=0.0013、max_batches=6000、steps=4800/5400、burn_in=1000。
- `models.command` 固定为 `[exe, detector, train, data_config_path, config_path, initial_weight.path, flags...]`；checker 会交叉核对 argv[3]、argv[4]、argv[5]，不能只检查 `detector train` 前缀。
- `file_bindings`：每个文件现场计算 SHA-256，并由 checker 与 source/build/seed/model/pilot 字段逐项交叉核对路径和 SHA；`scope=run` 的文件必须位于隔离 run-dir。配置、构建日志、seed smoke 日志和 checkpoint 不得写入固定输入目录。

模型角色固定为：tiny320 和 tiny416 是 PC 预检/未来上板候选，tiny416 仅作为优先比较对象；完整 YOLOv4 608 是 PC-only 对照，不做板上资源或板上性能验收。完整模型缺少官方 `yolov4.conv.137` 时必须保持 PENDING，不下载或伪造。

## 随机性与可复现语义

上游 `59596d7880f6504768df41d6daa586f5cb2b932f` 的训练入口原先使用 `time(0)`，Windows `rand_s` 也不受 `srand` 控制。隔离 seeded 副本仅修改 `detector.c`、`utils.c/.h`、`dark_cuda.c`、`yolo_layer.c`、`detection_layer.c` 和 `gaussian_yolo_layer.c`：训练初始化、Windows 随机数和设备 curand 读取同一环境 seed；未设置环境变量时保留官方路径。

该方案控制了已审查的 seed 入口，但不承诺 bit-exact。数据加载线程调度、OpenMP/CUDA kernel 并发和浮点归约仍可能造成差异。seed smoke 使用 424242 两次和 424243 一次，三次均退出 0；同 seed 的 loss/checkpoint 不同，正是 `bit_exact=false` 限制的现场依据。

## pilot 和状态语义

允许的有限 pilot 只使用官方 `detector train`，不带 `-map` 或正式 test 参数；每个 run 使用独立 `.data` backup、日志和 checkpoint。`READY` 表示结构、版本和 seed patch 构建绑定已通过；`PENDING` 表示缺少后续产物；`BLOCKED` 表示已执行步骤存在失败或未满足停止条件；`NOT_EXECUTED` 不是通过。

本轮 seeded build 配置和构建均退出 0。tiny416 pilot 以 `max_batches=100` 启动，真实推进到 8/100，随后退出码 `-1073741510`（Windows `0xC000013A`），未生成 checkpoint。日志中未发现 OOM、NaN、Inf 或损坏输入标记，但由于非零退出和无 checkpoint，D4 报告保持 `BLOCKED`，不把 8 步 loss 当作正式训练结果，也不重跑第二个 pilot。

## 复现与检查命令

从仓库根目录运行：

```powershell
py verification\s1_t02_d4_float_baseline.py validate --input report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1_plan.json --report report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1.json --summary report\evidence\S1-T02\20260916_s1_t02_d4_float_baseline_r1_summary.md
py -m unittest verification.test_s1_t02_d4_float_baseline -v
py -m unittest discover -s verification -p 'test_*.py'
py -m py_compile verification\s1_t02_d4_float_baseline.py verification\test_s1_t02_d4_float_baseline.py
git diff --check
```

检查器拒绝 `--input` 与 `--report`、`--input` 与 `--summary`、以及 `--report` 与 `--summary` 规范化后同路径，避免输入计划或 JSON 被摘要自覆盖。专项测试和完整 verification 测试只使用隔离临时夹具。

## 当前未执行项和阻断

未执行正式三模型训练、恢复、official test、robustness、mAP、INT8 整网、最终精度比较、Vivado 综合、资源/时序签核、烧录、板上测量和性能门槛判断。当前 D4 只形成可审的版本/路径/seed patch 绑定和 seed smoke；tiny416 pilot 被中止，full 权重缺失。D4 不关闭 S1-T02 G0，也不产生最终模型选择结论。
