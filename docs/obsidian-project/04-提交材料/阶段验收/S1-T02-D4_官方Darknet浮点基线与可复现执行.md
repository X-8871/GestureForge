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

模型角色固定为：tiny320 和 tiny416 是 PC 预检/未来上板候选，tiny416 仅作为优先比较对象；完整 YOLOv4 608 是 PC-only 对照，不做板上资源或板上性能验收。完整模型缺少官方 `yolov4.conv.137` 时必须保持 PENDING，不下载或伪造。当前 full608 输入已绑定 W5 R5 核验的官方 `D:\FPGA_Data\darknet\weights\yolov4.conv.137`，大小 `170038676` bytes、SHA-256 `11C5286CFBFFABC9A3059927401AB3480E9483CEAFD3265779A0DC26C769BED0`；该输入绑定不代表训练或精度通过。

## 随机性与可复现语义

上游 `59596d7880f6504768df41d6daa586f5cb2b932f` 的训练入口原先使用 `time(0)`，Windows `rand_s` 也不受 `srand` 控制。隔离 seeded 副本仅修改 `detector.c`、`utils.c/.h`、`dark_cuda.c`、`yolo_layer.c`、`detection_layer.c` 和 `gaussian_yolo_layer.c`：训练初始化、Windows 随机数和设备 curand 读取同一环境 seed；未设置环境变量时保留官方路径。

该方案控制了已审查的 seed 入口，但不承诺 bit-exact。数据加载线程调度、OpenMP/CUDA kernel 并发和浮点归约仍可能造成差异。seed smoke 使用 424242 两次和 424243 一次，三次均退出 0；同 seed 的 loss/checkpoint 不同，正是 `bit_exact=false` 限制的现场依据。

## pilot 和状态语义

允许的有限 pilot 只使用官方 `detector train`，不带 `-map` 或正式 test 参数；每个 run 使用独立 `.data` backup、日志和 checkpoint。`READY` 表示结构、版本和 seed patch 构建绑定已通过；`PENDING` 表示缺少后续产物；`BLOCKED` 表示已执行步骤存在失败或未满足停止条件；`NOT_EXECUTED` 不是通过。

本轮 seeded build 配置和构建均退出 0。tiny416 pilot 以 `max_batches=100` 启动，真实推进到 8/100，随后退出码 `-1073741510`（Windows `0xC000013A`），未生成 checkpoint。日志中未发现 OOM、NaN、Inf 或损坏输入标记，但由于非零退出和无 checkpoint，D4 报告保持 `BLOCKED`，不把 8 步 loss 当作正式训练结果，也不重跑第二个 pilot。

### full608 formal 失败与 random=0 重试结果

full608 formal_r3 使用 `random=1`、`subdivisions=64` 和 seed `424242`，实际推进到 `1164/6000` 后在 `image.c:807 make_image()` 因 CPU `calloc` 失败退出码 `2`。失败前隔离诊断观测到 private memory 约 `14.96 GB`、free commit 约 `5.37 GB`。1000 checkpoint 存在（`256102140` bytes，SHA-256 `9306AA18C04DC68373DA121E9D69BE0A0D0920003C736EBF627D2361372F3CD5`），但本次没有 `6000` 或 `final` 权重，不能作为完成的正式训练证据。

失败证据入口为 `report/evidence/S1-T02/20260919_s1_t02_d4_full608_formal_r3_cpu_ram_failure.json`（SHA-256 `CCF967C88B89CDDADFDE68B56196BAF55CF1221C57248AB98A48F3541BF3E6A7`）及同名 `_summary.md`（SHA-256 `A09DE3F914A71614040B9BD0485B3AC94CE33FFAF338FBEDFA081E2564903CF5`），对应证据提交为 `047cab6`。该证据只记录失败事实，不产生精度、最终模型或阶段验收结论。

当前重试使用固定 608×608、random=0、subdivisions=64、seed 424242 和全新隔离目录 D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r6_random0\workflow_formal_r3。工作流于 2026-09-20 17:19:37 因预设总超时 21600 秒停止，报告状态 EXECUTION_FAILED、工作流退出码 2、Darknet 命令退出码 1，最后观察到 1786/6000 步。报告 SHA-256 为 B82CC1D0F8375207838A9C41263C7594B9F6521965B01F988F0C8E4D016245FF，日志 SHA-256 为 AB52D2168E1BD6C2A8C0387E59F3FE6D8FFD842888745614CD5955CE1DF5B102。生成的 1000 checkpoint（256102140 bytes，SHA-256 C4D28C6605D105A1B97D51E41C8E35F8D18754DAF7AAB62F98A5895CAB6B33B3）与 last checkpoint（同大小，SHA-256 B37348630D3EE5311D6CE044076B48BDC09822B34153285E3CCBC81275154E6C）仅为中间恢复材料；没有 6000 或 final 权重。硬超时证据为 report/evidence/S1-T02/20260920_s1_t02_d4_full608_random0_timeout_r3.json（SHA-256 DF7DAC7AD8B7A9BDABF1A8DDD6AAC42DF1D5E46D9040996A665EE2701A65170F）及同名 _summary.md（SHA-256 D786EE3EA0AA397C59D950B93AAD2525905669D272407B70EA2DDF7ED3A37093）。日志未发现 NaN、Inf、OOM、calloc 或 CUDA 错误关键词；该证据只记录未完成事实，不产生训练完成、精度、最终模型或阶段验收结论。

随后创建的恢复候选 r7、r8 均由工作流在预检阶段安全阻断，未创建 Darknet 子进程：r7 误用 `_last.weights`，报告 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r7_resume1500\reports\workflow_resume_r4.json` SHA-256 `756F7743E776E4533FBFA6EA2989D25561C591879289BACE982A68A967780A42A`；r8 的 cfg 基名与编号 checkpoint 不一致，报告 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r8_resume1000\reports\workflow_resume_r5.json` SHA-256 `701A6F92A9F8F7187B7A85468490F1175114925F2B7AFF70ADDDD79B3CDB9013`。两次均为 `BLOCKED_PREFLIGHT`、命令数为0，不能解释为训练失败或训练结果。

当前恢复候选 r9 使用与 cfg 基名完全一致的编号 checkpoint `yolov4_5class_608_formal_r6_random0_1000.weights`（256102140 bytes，SHA-256 `C4D28C6605D105A1B97D51E41C8E35F8D18754DAF7AAB62F98A5895CAB6B33B3`），独立计划 Reviewer PASS（结果 SHA-256 `C74E2E2C7BD68E5FE547A0FEFBFF92B07F9C803B2139F3C4A173E688A08C21E7`），预检 PASS。r9 于 2026-09-20 23:02:30 以隐藏脱离方式启动，工作流 PID 468、Darknet PID 21396；启动门证据为 `report/evidence/S1-T02/20260920_s1_t02_d4_full608_random0_resume1000_launch_gate_r6.json`（SHA-256 `92E281097784E6C64B09F360B6FE2DAC6640D5B270C34F1A08B5E6AE8DB8C2F5`），独立启动门 Reviewer PASS 结果 SHA-256 `81D666E44EA628EDB0E06A0764354A00E943D22D1FAD9EA846829886E24F65FE`。r9 已完成 `1001..6000` 共 5000 个恢复更新步，工作流与 Darknet 退出码均为 `0`，报告状态为 `EXECUTED_REVIEW_REQUIRED`。`6000.weights`、`final.weights`、`last.weights` 均为 256102140 bytes，SHA-256 `1C1A4237F69853A7C1813C40F792FC7F3F5B5F1949AACE4869D700FC8589B152`。完成证据为 `report/evidence/S1-T02/20260921_s1_t02_d4_full608_random0_resume1000_completion_r6.json`（SHA-256 `6451CE2C01FF56850387F9C9A0FB0B9065EA1EDA329C8147599D7A1A9B146416`）及同名摘要（SHA-256 `AF115ED33D6ACAEA3F5A6781DAC5BD1B5EC7659972CEF87594593672B3B6ED3F`）；独立完成证据 Reviewer PASS 结果 SHA-256 `85B1BCEB90B1F5FAD58C97A9CD25D414BD2F3C95F6D21521A0484F138F3DB55B`。该结果只确认执行完成和权重产出，不产生精度、泛化、INT8、资源、板上或阶段验收结论。

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

尚未形成可供 D4 验收的三模型完整正式训练/恢复闭环、official test、robustness、mAP、INT8 整网、最终精度比较、Vivado 综合、资源/时序签核、烧录、板上测量和性能门槛判断。tiny416 pilot 仍为 `BLOCKED`；full608 r9 已完成正式恢复训练并产出权重，但完成证据仍待独立 Reviewer，且不产生精度或阶段验收结论。D4 不关闭 S1-T02 G0，也不产生最终模型选择结论。
