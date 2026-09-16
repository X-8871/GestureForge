# 验证工程区

- `sandbox/`：临时模块验证工程。
- `sim_results/`：波形和仿真输出。
- `reports/`：综合、实现、资源和时序报告。
- `s1_t01_cuda_smoke.cu`：S1-T01 固定 CUDA 设备冒烟源程序；只做设备枚举、显存拷贝、四元素内核计算和结果校验，不启动训练。

在已安装 CUDA Toolkit 且 `nvcc` 位于 PATH 后，从工程根目录编译并运行：

```powershell
New-Item -ItemType Directory -Force build\s1_t01 | Out-Null
nvcc -O2 -arch=sm_89 -o build\s1_t01\s1_t01_cuda_smoke.exe verification\s1_t01_cuda_smoke.cu
build\s1_t01\s1_t01_cuda_smoke.exe
```

上述命令必须在对应的 Visual Studio `vcvars64.bat` 环境中执行，并确保 CUDA `bin` 已加入 PATH；`-arch=sm_89` 与 RTX 4060 Laptop GPU 的 Ada 架构一致，可避免使用默认 PTX 目标导致的运行时不兼容。只有进程退出码为 `0` 且输出包含 `S1_T01_CUDA_SMOKE_PASS` 时，才能把生成的可执行文件路径传给 `s1_t01_environment_probe.py`。本机安装后验证已使用该参数在真实 RTX 4060 Laptop GPU 上编译并运行通过；`build/s1_t01/s1_t01_cuda_smoke.exe` 仅作为本机证据产物，不提交 Git。

实验结论同步记录到 Obsidian 的 `03-实验记录/实验记录.md`。

`s1_t01_dataset_check.py` 对 PNG、BMP、PNM 和 JPEG 执行结构及像素载荷检查；JPEG 还要求当前环境可导入 Pillow 并完成 `Image.load()`，否则该图片按失败写入审计报告。使用 `--semantic-review` 提供人工语义补充 CSV 后，只有明确 `no_hand` 且人工确认的样本才计入无手统计；`non_target_gesture` 和未分类空标签单独统计。检查器输出的 `PASS_AUTOMATED_MANUAL_PENDING` 不能替代真实图片人工叠框观察。

`s1_t01_darknet_workflow.py` 提供 official Darknet 的 `train`、`resume` 和 valid 清单批量 `evaluate` 入口。它只接受已通过环境探针的 Darknet/CUDA、已通过数据检查并由 Wong 精确批准的清单、带 image/label 和完整审计字段的 manifest、显式 `.data` 保存键、五类配置以及 11～100 `max_batches` 短训 cfg；缺少任何前置条件时退出码为 2、写出 `BLOCKED_PREFLIGHT` 报告且不启动 Darknet。

S1-T02-D2 的测试可从仓库根目录运行 `python -m unittest discover -s verification -p 'test_*.py'`，也可在 `verification` 目录运行 `py -m unittest discover -s . -p 'test_*.py'`；测试导入兼容两种入口，正式验收应记录实际工作目录和退出码。

S1-T02-D3 的专项测试可从仓库根目录运行 `python -m unittest verification.test_s1_t02_d3_resource_performance`，也可在 `verification` 目录运行 `py -m unittest discover -s . -p 'test_s1_t02_d3_*.py' -v`。资源/性能 JSON 检查命令见 `S1-T02-D3_资源性能与阶段验收门槛.md`，必须使用独立的 `*_spec.json` 输入、`*.json` 报告和 `*_summary.md` 输出，禁止 `--input` 与 `--report` 同路径；检查器将 estimate、synthesis、board_measurement 分开，缺少综合或板测只返回 `NOT_EXECUTED_PENDING`，不代表 PASS。

S1-T02-D4 使用 `verification/s1_t02_d4_float_baseline.py validate` 校验三模型官方 Darknet 浮点运行计划并生成独立报告；输入计划、报告和摘要必须是不同路径，且检查器会现场核验 D2 参考实现 SHA、官方源 commit/diff、隔离 patched source、构建日志/可执行文件、seed smoke 日志/checkpoint 和模型命令的 argv[3:5] 交叉绑定。专项测试为 `python -m unittest verification.test_s1_t02_d4_float_baseline -v`，完整回归为 `python -m unittest discover -s verification -p 'test_*.py'`。D4 seeded build、seed smoke 和 tiny416 pilot 的实际状态以 `report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1.json` 为准；`BLOCKED`、`PENDING` 和 `NOT_EXECUTED` 不表示正式训练或精度通过。

训练检查点输出严格由 `.data` 的 `backup`、`saveweights`、`savelast` 和 cfg 基名确定。`train` 必须使用新建的 `--checkpoint-output`；`resume` 只允许同一 cfg 基名的 numbered 输入（例如 `gesture_10.weights`），拒绝 `*_last.weights`/`*_final.weights`，并必须使用不同的 `--checkpoint-output`。入口会拒绝已有候选文件，运行后核对输出路径、大小、修改时间和 SHA-256，并核对 resume 输入哈希未改变。`evaluate` 对 valid 清单逐图执行带显式 filename 的官方 `detector test -out`，每图产生独立 JSON 后合并解析；只有解析出与清单一一对应的 `filename`/`objects` 记录，并证明批准 no_hand 图片 `objects=[]`，才形成 AC06 候选。类别必须在五类范围内，`class_id` 与 `name` 同时出现时必须一致。实际运行输出只作为 AC05/AC06 候选证据，梯度、优化器状态和精度结论仍需独立核对。

入口在启动前对所有传给 Darknet 的路径、valid 图片、逐图 JSON 输出以及 checkpoint 的 backup/cfg 候选路径执行固定缓冲区检查：UTF-8 字节数加结尾空字符必须小于 256；train、resume、evaluate 任一超长路径均返回 2，绝不截断。运行中和进程退出后的完整日志均识别大小写不敏感的 `Cannot load image`、`Can't open label file`、`Couldn't open file`、OOM 和损坏输入标记。
