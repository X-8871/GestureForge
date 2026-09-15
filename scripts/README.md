# 工程脚本

保存工程重建、数据预处理、模型导出、结果比对和批量验证脚本。脚本应注明输入、输出和使用方式。

## S1-T01 数据检查

当前 S1-T01 的数据检查器位于 `verification/s1_t01_dataset_check.py`，使用受控 Python 运行时和外部 UTF-8 CSV 清单；不自动下载 HaGRIDv2，不自动安装 Darknet/CUDA，不启动正式长训。命令与清单接口见 `data/README.md`。

HaGRIDv2 标签转换器位于 `verification/s1_t01_prepare_hagrid.py`，逐个读取目标类别/划分 JSON，递归适配官方 ZIP 嵌套目录，生成五类 YOLO 标签和 `manifest_all.csv`。清洁器位于 `verification/s1_t01_filter_manifest.py`，根据完整 SHA-256 重复分析结果按 `train > val > test` 移除跨 split 重复行，不删除原始图片或标签。两者均使用 UTF-8，失败时不发布半成品正式清单。

环境探针位于 `verification/s1_t01_environment_probe.py`，固定检查官方 Darknet/CUDA 路线、GPU、`nvcc`、Darknet 版本/帮助输出和明确的 CUDA 设备冒烟程序；未提供 Darknet 或设备冒烟程序时保持失败，不自动切换框架。设备冒烟程序只有在退出码为 0 且输出包含 `S1_T01_CUDA_SMOKE_PASS` 时才算通过：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_environment_probe.py `
  --darknet-executable 'D:\darknet\darknet.exe' `
  --cuda-smoke-executable 'D:\darknet\s1_t01_cuda_smoke.exe' `
  --report report\evidence\S1-T01\<运行编号>_environment_probe.json
```

Darknet 必须通过 PE 文件检查和版本/帮助命令；CUDA 冒烟程序必须退出码为 0 且输出 `S1_T01_CUDA_SMOKE_PASS`。任一条件缺失都保持失败，不自动切换框架或把 `nvidia-smi` 查询当作设备张量运算。

## S1-T01 短训、恢复与逐图评估入口

`verification/s1_t01_darknet_workflow.py` 是只支持 official Darknet 的严格流程入口。它要求环境报告为 `official-darknet-cuda` 的 `PASS`，数据检查报告的 AC02/AC03 自动通过，并提供 Wong 完成人工叠框抽查后的 `APPROVED` JSON。它还校验五类 names 顺序、`.data` 的 `classes=5`、YOLO cfg 的检测头和 `max_batches`；短训 cfg 的 `max_batches` 必须在 11～100 内，超过安全上限或缺少前置版本绑定时失败即停。

入口不下载、安装或切换框架，不使用 shell，不覆盖已有检查点。`.data` 必须显式提供 `train`、`valid`、`backup`、`saveweights`、`savelast`；入口按官方 Darknet `detector.c` 的 cfg 基名和保存间隔列出本次动作的候选输出。`train` 使用 `--initial-weights` 和必须不存在的 `--checkpoint-output`，`resume` 使用 `--checkpoint` 与不同的 `--checkpoint-output`；输出必须是本次运行新生成的 `<cfg基名>_<iteration>.weights`、`<cfg基名>_last.weights` 或 `<cfg基名>_final.weights`，不会覆盖任何已有候选。

`train` 执行至少 10 个更新步的官方 `detector train`，`resume` 只接受同一 cfg 基名的 numbered checkpoint（例如 `gesture_10.weights`），拒绝 `*_last.weights`/`*_final.weights` 作为输入并继续至少 1 步。`evaluate` 对与 manifest 完全一致的 valid 清单逐图执行带显式 filename 的官方 `detector test -out <per-image-json>`，再按每个 `filename` 的 `objects` 数组生成结构化 `evaluation.jsonl` 和汇总 `evaluation.json`；zero-prediction-image 必须同时属于 Wong 批准的 no_hand manifest 行且 `objects=[]`。训练和评估日志中出现 NaN、Inf、OOM、数据损坏、总超时或无进度超时都会停止，即使 Darknet 立即退出也会扫描完整日志。命令成功只表示流程执行完成；梯度有限性、优化器状态恢复和精度结论仍需独立审查及人工证据，入口不会伪造 AC05/AC06 通过。

数据人工批准 JSON 的最小字段如下，`dataset_report_sha256` 和 `manifest_sha256` 必须按实际文件计算：

```json
{
  "status": "APPROVED",
  "reviewer": "Wong",
  "dataset_report": "D:\\FPGA_Competition\\report\\evidence\\S1-T01\\<dataset-report>.json",
  "dataset_report_sha256": "<64位SHA-256>",
  "manifest_sha256": "<64位SHA-256>",
  "no_hand_images": [
    {
      "image": "val/images/no_hand_001.jpg",
      "split": "val",
      "role": "no_hand",
      "manifest_row": 123
    }
  ]
}
```

`reviewer` 必须精确为 `Wong`；`no_hand_images` 的每一项必须绑定 manifest 的 val 行，且对应标签文件为空。缺少标签、人员/会话审计字段、审批哈希或 `.data` 保存键时，入口统一在启动前输出 `BLOCKED_PREFLIGHT` 报告并返回 `2`。

启动前先以 `--dry-run` 检查命令和版本绑定，再由人工确认没有同名 `darknet.exe` 进程后移除该选项执行。训练/恢复的日志、检查点和评估 JSONL 应写入本次运行的隔离目录；检查点、权重和完整数据不提交 Git。

训练与恢复命令的关键参数形态如下（其余前置参数按上文入口定义补齐）：

```powershell
... s1_t01_darknet_workflow.py train ... --initial-weights D:\darknet\weights\init.weights `
  --checkpoint-output D:\darknet\backup\gesture_10.weights --dry-run
... s1_t01_darknet_workflow.py resume ... --checkpoint D:\darknet\backup\gesture_10.weights `
  --resume-from-step 10 --checkpoint-output D:\darknet\backup\gesture_final.weights --dry-run
... s1_t01_darknet_workflow.py evaluate ... --valid-list D:\darknet\data\valid.txt `
  --zero-prediction-image D:\FPGA_Data\HaGRIDv2\<approved-no-hand-image> --dry-run
```

`evaluate` 的正式动作是对 valid 清单逐图执行 `darknet detector test <data> <cfg> <weights> <filename> -dont_show -ext_output -out <run-dir>\detections\eval_000001.json`；入口在执行前检查 valid 清单和 manifest 集合，执行后逐文件检查 JSON 的 `filename`、`objects`、类别、分数和坐标，再合并为 `evaluation.json`/`evaluation.jsonl`。零框只能由对应文件的 `objects=[]` 证明。每张图的命令均使用参数数组和 `shell=False`，不依赖 shell 重定向。

启动前还按官方源码固定 256 字节输入/路径缓冲检查所有实际命令参数、valid 图片、逐图 JSON 输出、权重及 checkpoint 生成相关路径；采用 UTF-8 字节数加结尾空字符必须小于 256 的严格门槛，超长路径直接失败且不会截断。日志会大小写不敏感地识别 `Cannot load image`、`Can't open label file`、`Couldn't open file` 等官方错误文本，即使 Darknet 立即返回 0 也会在完整日志复查后失败。

在正式数据到位后运行：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_dataset_check.py `
  --data-root 'D:\FPGA_Data\HaGRIDv2' `
  --manifest 'D:\FPGA_Data\HaGRIDv2\manifest.csv' `
  --report report\evidence\S1-T01\<运行编号>_dataset_check.json `
  --preview-dir report\evidence\S1-T01\<运行编号>_previews
```

恢复/重建标签时先确认没有同名进程，再执行：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_prepare_hagrid.py `
  --data-root 'D:\FPGA_Data\HaGRIDv2' `
  --manifest 'D:\FPGA_Data\HaGRIDv2\manifest_all.csv' `
  --labels-root 'D:\FPGA_Data\HaGRIDv2\labels' `
  --report report\evidence\S1-T01\<运行编号>_prepare.json
```

清洁器需要已有的完整重复分析日志；它只改写清单，不删除图片/标签：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' verification\s1_t01_filter_manifest.py `
  --input 'D:\FPGA_Data\HaGRIDv2\manifest_all.csv' `
  --output 'D:\FPGA_Data\HaGRIDv2\manifest.csv' `
  --duplicate-report report\evidence\S1-T01\<重复分析日志> `
  --report report\evidence\S1-T01\<运行编号>_filter.json
```

无外部数据时只运行单元测试，不用合成图片宣称 AC03/AC04 通过：

```powershell
& 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest verification.test_s1_t01_dataset_check -v
```
