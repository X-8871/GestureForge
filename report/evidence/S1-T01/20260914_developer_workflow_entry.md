# S1-T01-D1 Developer 流程入口证据摘要

- 任务：S1-T01-D1，基线工作区 HEAD `649f50cedc06ffdbb35bf74c8cc44434a9e7afd0`，阶段计划 v3.0。
- 目标：为 AC05、AC06、AC07 提供可复用且失败即停的 official Darknet 短训/恢复/逐验证图评估入口。
- 允许范围：新增 `verification/s1_t01_darknet_workflow.py` 及其定向单测，更新 `verification/README.md`、`scripts/README.md`、`data/README.md`；未修改用户已有正式 Markdown、Vivado 工程或 JPG。本轮仍不提交 Git。

## 实现边界

1. 入口必须先验证 `official-darknet-cuda` 环境报告为 `PASS`，并核对 Darknet PE 与已登记 SHA-256；`nvidia-smi` 单独通过不能放行。
2. 入口必须验证数据自动检查 AC02/AC03 通过、AC04 已生成待人工抽查候选，并要求独立的 Wong `APPROVED` JSON 将数据报告和 manifest SHA-256 绑定。
3. `.data`、names 和 YOLO cfg 必须固定五类；cfg 的每个 YOLO 头逐头检查紧邻卷积 `filters=3*(5+5)=30`，`max_batches` 必须为 11～100，拒绝从该入口启动正式长训。
4. `.data` 强制 `train`、`valid`、`backup`、`saveweights`、`savelast`；train/valid 清单按 Darknet 工作目录解析并与 manifest 对应划分精确比对，manifest 同时强制 image、label、split、session_id、person_id、source、license、is_real 和实际标签文件。检查点候选绑定 cfg 基名和官方保存间隔，`--checkpoint-output` 不得已有文件；resume 输入和输出分离并核对输入哈希不变。
5. `train` 使用显式初始权重执行官方 `detector train`，至少观察 10 个更新步并核对本次新生成检查点；`resume` 使用显式输入和不同输出继续至少 1 步；`evaluate` 对完整 valid 清单逐图执行带显式 filename 的官方 `detector test -out` JSON，每图独立文件后合并，要求每个 filename/objects 结构化记录和批准 no_hand 图片 `objects=[]`。
6. 所有命令使用参数数组、`shell=False`，不自动下载、安装、切换框架或删除文件。训练和评估日志出现 NaN/Inf、OOM、数据损坏、超时或无进度时停止；已有同名 Darknet 进程或运行锁时拒绝启动；evaluate 分支同样拒绝非有限或损坏输出。
7. 流程执行完成不自动宣称 AC05/AC06 通过：官方 Darknet 文本无法独立证明梯度有限、优化器状态恢复和无手语义，报告明确保留人工/独立审查项。

## 本机实际状态

- 本轮未启动训练、恢复或评估：当前环境报告显示 `nvcc`、Darknet PE 和固定 CUDA 设备冒烟程序均缺失，且数据语义报告 `no_hand=0/5`、AC03 未通过；因此没有伪造命令输出、检查点、评估结果或权重哈希。
- 当前仅运行了隔离临时目录中的定向单测、`py_compile` 和一次真实前置失败预检。真实 Darknet/CUDA、真实无手样本、Wong 人工批准、短训检查点和评估结果仍是 S1-T01 阻断项。
- 第3轮真实预检报告 `20260915_round3_train_blocked.json` 记录当前提交 `649f50cedc06ffdbb35bf74c8cc44434a9e7afd0`、dirty 工作树、环境探针/数据检查器/CUDA 冒烟源文件摘要，以及 Darknet 二进制、CUDA 冒烟可执行文件和官方源提交为 `unavailable`；状态 `BLOCKED_PREFLIGHT`，命令数为 0，返回码为 2。第2轮报告 `20260915_round2_train_blocked.json` 和旧报告 `20260914_round1_train_blocked.json` 保留作为历史证据。

## 本轮验证

| 检查 | 命令/口径 | 退出码 | 结果 |
|---|---|---:|---|
| 定向编译 | 受控 Python 3.12.14 对新增工作流及单测执行 `py_compile` | 0 | 通过 |
| 定向单测 | `python -m unittest verification.test_s1_t01_darknet_workflow -v` | 0 | 24 项通过 |
| 全量回归 | `python -m unittest discover -s verification -p "test*.py" -v` | 0 | 48 项通过 |
| 全量编译 | 受控 `py_compile`，`PYTHONPYCACHEPREFIX` 指向系统临时目录，对 `verification/`、`scripts/` 全部 Python 文件 | 0 | 通过 |
| 当前环境阻断演练 | 使用 `20260914_environment_recheck.json`、`20260914_hagrid_dataset_check_semantic.json`、真实外部 manifest 和缺失 Darknet/config 调用 `s1_t01_darknet_workflow.py train` | 2 | `BLOCKED_PREFLIGHT`，命令数 0，未启动 Darknet；报告见 `20260915_round3_train_blocked.json` |
| 差异检查 | `git diff --check` | 0 | 通过；仅有 Git 行尾提示 |

单测输出和编译缓存写入系统隔离临时目录；真实预检报告按任务授权写入本目录，未写入工程 `build/` 或提交构建产物。第2轮新增并验证：resume 仅接受同 cfg 基名 numbered checkpoint 并拒绝 `_last`/`_final` 输入；训练完成后补扫已退出进程的完整日志；检测类别检查范围、名称和二者一致性；train/evaluate 立即 OOM/损坏失败、无进度超时、输入 SHA 与候选不覆盖保护。第3轮新增并验证：官方 `Cannot load image`、`Can't open label file`、`Couldn't open file` 大小写不敏感匹配；train/resume/evaluate 统一执行 UTF-8 路径含终止符小于 256 字节门槛且不截断；resume 实际执行输入 SHA/新输出检查、总超时和空/畸形 detector JSON 的 AC06 失败收口。

第3轮工作流脚本实测 SHA-256：`85bc06a6ff431efcda43b5f09565fa7c60d9edd78a7c6c5b76284b6e251d4809`。该值是当前工作树实测值，不是 Git 提交对象；上一轮审查消息中的 SHA mismatch 为总控消息误写，未据此修改代码。

## 待环境和数据满足后的复现顺序

1. 运行现有 `s1_t01_environment_probe.py`，确认真实 official Darknet、`nvcc` 和 CUDA 冒烟均通过，并保存环境报告。
2. 完成真实 `no_hand` 采集、AC03/AC04 人工确认，生成 `APPROVED` JSON，并按实际文件计算数据报告和 manifest SHA-256。
3. 准备显式五类 `.data`、names、每个检测头前置 `filters=30` 且 `max_batches` 为 11～100 的短 cfg、初始权重及与 manifest train/val 集合完全一致的清单；先使用入口的 `--dry-run`。
4. 确认没有同名 Darknet 进程后执行 `train --checkpoint-output <backup>\<cfg>_<iteration|last|final>.weights`，核对至少 10 个更新步、文件新生成和 SHA-256；再执行 `resume --checkpoint <input> --resume-from-step <记录步数> --checkpoint-output <不同新输出>`，核对至少 1 个后续步、输入未被修改和新输出哈希。
5. 使用固定检查点执行 `evaluate`，核对每张验证图的显式 filename 命令、独立 JSON、汇总 JSON/JSONL 的框/类别/分数/坐标、人工批准 no_hand 行及 `objects=[]`，随后绑定代码、配置、数据、检查点和日志哈希形成 AC07 复跑证据。

本摘要是 Developer 实现证据，不是独立 Reviewer 结论，也不关闭 AC01、AC03、AC04 或 AC05～AC07。
