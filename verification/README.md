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

`s1_t01_darknet_workflow.py` 提供 official Darknet 的 `train`、`resume` 和 valid 清单批量 `evaluate` 入口。它只接受已通过环境探针的 Darknet/CUDA、已通过数据检查并由 Wong 精确批准的清单、带 image/label 和完整审计字段的 manifest、显式 `.data` 保存键及五类配置。`train`/`resume` 默认仍是诊断短训，仅允许 11～100 `max_batches`；正式训练必须显式添加 `--formal-training` 并提供 `--darknet-seed`，cfg 必须同时固定 `max_batches=6000`、`steps=4800,5400`，不接受其他长训长度。`--formal-training` 只注册在 `train` 和 `resume`，`evaluate` 不接受。缺少任何前置条件时退出码为 2、写出 `BLOCKED_PREFLIGHT` 报告且不启动 Darknet。

S1-T02-D2 的测试可从仓库根目录运行 `python -m unittest discover -s verification -p 'test_*.py'`，也可在 `verification` 目录运行 `py -m unittest discover -s . -p 'test_*.py'`；测试导入兼容两种入口，正式验收应记录实际工作目录和退出码。

S1-T02-D3 的专项测试可从仓库根目录运行 `python -m unittest verification.test_s1_t02_d3_resource_performance`，也可在 `verification` 目录运行 `py -m unittest discover -s . -p 'test_s1_t02_d3_*.py' -v`。资源/性能 JSON 检查命令见 `S1-T02-D3_资源性能与阶段验收门槛.md`，必须使用独立的 `*_spec.json` 输入、`*.json` 报告和 `*_summary.md` 输出，禁止 `--input` 与 `--report` 同路径；检查器将 estimate、synthesis、board_measurement 分开，缺少综合或板测只返回 `NOT_EXECUTED_PENDING`，不代表 PASS。

S1-T02-D4 使用 `verification/s1_t02_d4_float_baseline.py validate` 校验三模型官方 Darknet 浮点运行计划并生成独立报告；输入计划、报告和摘要必须是不同路径，且检查器会现场核验 D2 参考实现 SHA、官方源 commit/diff、隔离 patched source、构建日志/可执行文件、seed smoke 日志/checkpoint 和模型命令的 argv[3:5] 交叉绑定。专项测试为 `python -m unittest verification.test_s1_t02_d4_float_baseline -v`，完整回归为 `python -m unittest discover -s verification -p 'test_*.py'`。D4 seeded build、seed smoke 和 tiny416 pilot 的实际状态以 `report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1.json` 为准；`BLOCKED`、`PENDING` 和 `NOT_EXECUTED` 不表示正式训练或精度通过。

S1-T02-D5 使用 `s1_t01_darknet_workflow.py train/resume --darknet-seed <0..4294967295>` 执行隔离的 seeded 官方 Darknet 短训/恢复链；诊断短训的种子仍可选。正式运行必须同时显式提供 `--formal-training` 和 `--darknet-seed <0..4294967295>`，缺少种子时启动前保持 `BLOCKED_PREFLIGHT`；正式 profile 严格选择获批的 6000-step schedule（`max_batches=6000`、`steps=4800,5400`）。不带 `--formal-training` 时短训上限仍为 100，正式参数不会扩大为任意长训。种子仅通过子进程环境变量 `GESTUREFORGE_DARKNET_SEED` 传递；训练与恢复的 `.data`、cfg、checkpoint、日志和 workflow JSON 必须分目录，resume 只能读取 numbered checkpoint、恢复起始步必须小于 6000 且必须证明输入 SHA 未改变。正式日志还必须连续覆盖 train 的 1..6000 或 resume 的 `resume_from_step+1..6000`，否则不得形成成功候选。报告用 `training_profile=diagnostic_short` 或 `formal_6000` 绑定所选 profile（evaluate 为 `not_applicable`），并明确 profile/训练执行不代表精度、泛化、INT8、资源、最终模型或板上验收通过。复现实例及实际状态见 `report/evidence/S1-T02/20260916_s1_t02_d5_seeded_train_resume_r1_summary.md`；该证据是 `EXECUTED_REVIEW_REQUIRED` 候选，不代表 bit-exact、正式精度、mAP、full 训练或板上通过。

训练检查点输出严格由 `.data` 的 `backup`、`saveweights`、`savelast` 和 cfg 基名确定。`train` 必须使用新建的 `--checkpoint-output`；`resume` 只允许同一 cfg 基名的 numbered 输入（例如 `gesture_10.weights`），拒绝 `*_last.weights`/`*_final.weights`，并必须使用不同的 `--checkpoint-output`。入口会拒绝已有候选文件，运行后核对输出路径、大小、修改时间和 SHA-256，并核对 resume 输入哈希未改变。`evaluate` 对 valid 清单逐图执行带显式 filename 的官方 `detector test -out`，每图产生独立 JSON 后合并解析；只有解析出与清单一一对应的 `filename`/`objects` 记录，并证明批准 no_hand 图片 `objects=[]`，才形成 AC06 候选。类别必须在五类范围内，`class_id` 与 `name` 同时出现时必须一致。实际运行输出只作为 AC05/AC06 候选证据，梯度、优化器状态和精度结论仍需独立核对。

入口在启动前对所有传给 Darknet 的路径、valid 图片、逐图 JSON 输出以及 checkpoint 的 backup/cfg 候选路径执行固定缓冲区检查：UTF-8 字节数加结尾空字符必须小于 256；train、resume、evaluate 任一超长路径均返回 2，绝不截断。运行中和进程退出后的完整日志均识别大小写不敏感的 `Cannot load image`、`Can't open label file`、`Couldn't open file`、OOM 和损坏输入标记。

## S2B-T02 固定输入离线结果检查

`s2b_fixed_capture_check.py` 只读取保存到 PC 的 JSON 和原始 INT8 文件，复用已冻结
tiny416/D9/D6 规则。它不定义串口报文、AXI/DDR 地址或事务连通语义；离线 PASS
不代表阶段2B G0/G3、实际输入传输或 1000 次连续板上任务通过。

从仓库根运行（下面的 `reference.json`、`capture.json` 和新报告路径由调用者明确指定）：

```bash
python -B verification/s2b_fixed_capture_check.py --reference reference.json --capture capture.json --report result_new.json
python -B -m unittest verification.test_s2b_fixed_capture_check -v
```

两个输入封装都要求 `schema_version=1`、冻结 `model_manifest_sha256` 和显式非空
`samples`；`kind` 分别为 `s2b_fixed_reference`、`s2b_fixed_capture`。这是 PC 中间文件
约定，不是板上通信冻结。每项直接复用 T29 的业务字段：

- `frame_id` 是原样比较的 uint32 不透明值，不由列表索引生成；`sample_id` 原样比较。
- `input={pl_input_sha256,geometry_wh}`，分别绑定预处理 tensor 摘要和原图宽高。
- `head_tensors={head13,head26}`，每头恰含 `path`、`tensor_sha256`、`byte_length`。
  必须为完整 5,070/20,280 字节、连续 NCHW 对称 INT8；head13 尾部不得补为 5,072 字节。
- `nms_output_box_count` 与 `detections` 长度一致，最多 15；每框恰含
  `class_id,class_name,score,xyxy,source_order`。xyxy 是有限、正面积、裁剪到 `[0,1]` 的归一化坐标。

reference 另含 `golden_source={kind,path,sha256}`。这份独立来源 JSON 必须实际存在，
两头摘要、帧身份及期望框都必须与其中的样本记录一致；黄金 raw 文件的摘要还会现场核验。
支持两种明确来源：

- `frozen_cpu_d9`：固定到阶段2A冻结提交 `671f9cf494b92ce182b3f1542fefd0cfd4b209f5`
  中的 `report/evidence/S2A-T29/cpu_decode_nms_reference.json`，Git LF 字节摘要
  `24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231`。
  `sha256` 仍填写本次来源文件的实际原始字节摘要；其 Git 文本只在冻结摘要核对时将 CRLF 转 LF。
- `synthetic_hand_computed`：来源 JSON 恰含 `schema_version=1`、
  `kind=s2b_synthetic_hand_computed`、冻结模型摘要、`basis={path,sha256,description}`
  和 T29 字段的 `samples`，只允许 `synthetic_` 样本。来源头至少含 `tensor_sha256,byte_length`，
  不从捕获文件生成黄金。`test_s2b_fixed_capture_check.py::write_fixture` 提供不调用 D9 的独立
  手算单框、空框、同分异类多框及第二头示例。来源作者与手算依据仍需独立审查。

来源记录的期望框以 `1e-12` 绝对容差核对黄金 raw 头的现有 D9 解码；最终捕获框直接
对该 D9 结果检查，防止叠加容差。先要求两头所有字节相等，再要求框数量、类别、
source_order、输出顺序完全相同，score/每坐标绝对误差 `<=1e-6`、相对容差 0。
不对框重新排序；不同帧按输入列表顺序比较。重复 sample/frame 身份、重复 JSON 键、
布尔整数、缺字段、未知字段、NaN/Inf、截断/多字节和错误哈希均拒绝。

JSON 内相对文件路径以该脚本所在仓库根为基准，绝对路径按平台字面使用；不展开变量、
改写分隔符或猜测相邻文件。捕获与黄金不得指向同一文件或硬链接。报告父目录必须已存在，
报告使用独占创建，不能覆盖输入或旧结果。退出码 0 为 `PASS_OFFLINE_CAPTURE_CHECK`，
1 为已生成的比较失败报告，2 为格式/文件/来源/输出错误且本次无有效报告；遇到旧报告
返回 2，明确标明旧文件不是本次结果，调用者须使用新的报告名称。

专项随机验证固定 seed=`20261008`：24 个单字节故障，以及 8 帧所有 logits 为负数的随机
空输出；只覆盖离线检查器，不计为 1000 次板上任务。验证证据见
`report/evidence/S2B-T02/capture_check_20261008_r01/`。
