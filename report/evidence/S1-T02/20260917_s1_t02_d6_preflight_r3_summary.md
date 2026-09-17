# S1-T02-D6 R2 evidence-only remediation — source binding and R3 preflight

## 结论与边界

R3 的 CPU-only val preflight 退出码为 **0**，状态为 `PLANNED_NO_EXECUTION`，实际执行命令数为 **0**。只有一条 Darknet 命令被计划，未启动 Darknet/CUDA/GPU，未生成模型预测或离线指标。D8 独立 G2 仍为 `CHANGES_REQUIRED`，GPU 前置继续关闭。最终 score threshold 未选择、未冻结；获批分析范围仍为 `[0.25, 0.50]`，capture-only 参数为显式 `-thresh 0.249999`。

R3 工作流报告中的 `identity.official_darknet_source` **原样为 `unavailable`**。本补充证据不声称该字段已捕获，也没有修改 workflow 或报告；它单独记录 D4 plan/provenance 对固定上游 commit、seed patch、seeded copy、源归档及文件哈希的关系。

## 哈希语义：上游原始文件 vs. seed-patched 副本

固定上游仓库 `D:\FPGA_Data\darknet` 的 HEAD 为 `59596d7880f6504768df41d6daa586f5cb2b932f`，与 D4 plan 的 `source.commit_observed` 一致。上游哈希通过 `git cat-file blob <commit>:<path>` 取得原始文件内容字节后计算 SHA256；seeded 哈希对 `official_darknet_seeded/src` 的实际文件字节直接计算 SHA256。两者是不同对象的内容哈希，不是 Git blob object id。

| 源文件 | 上游 commit 原始内容 SHA256 | seed-patched 副本路径 | seed-patched 副本 SHA256 |
|---|---|---|---|
| `src/detector.c` | `7dd184184ce3a01be5c2361a821d4b0a09597bcf5854343950b00c1b28eda6be` | `.../official_darknet_seeded/src/detector.c` | `3795c4b144ce12177268128c019dc29589ca94412622d137b7a5ecf5528a4a77` |
| `src/utils.c` | `d046a6ccc4eb784186a697851877612109777bbd554756591924498fede449ad` | `.../official_darknet_seeded/src/utils.c` | `d5a3d487b0086af2361282b002302c4a7581fb7daaf6b272ee07eb5d82b154ec` |
| `src/yolo_layer.c` | `3996ef6b465add3b1779f52c757a7d16250ac1036b332cc3ec975071c947d94e` | `.../official_darknet_seeded/src/yolo_layer.c` | `8b164c3dcf82b276698a3ffd9694d0ccd029f22b9b09f8a98e38e64627dfd381` |

这些哈希**有意不同**：D4 plan 标记 `patch_applied=true`，seeded copy 含 `seed_support.patch` 修改。D4 plan 的 patch SHA256 为 `b3025639731271fac3476647823e5cb4cfa1a09e9fd54fedf36cd45e6539c01b`；只读 `git apply --stat/--numstat` 显示其作用范围为 7 个文件：`src/utils.h`、`src/utils.c`、`src/detector.c`、`src/yolo_layer.c`、`src/detection_layer.c`、`src/gaussian_yolo_layer.c`、`src/dark_cuda.c`（合计 64 insertions、9 deletions）。源归档为 `D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\official_darknet_59596d7_source.zip`，SHA256 `474916bd5b61b6e913e1d9b6bd4e3a48117000be62deffe5191f966df85a1a47`，与 D4 plan 记录一致。

来源入口：D4 [immutable plan](D:/FPGA_Competition/report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1_plan.json)（SHA256 `63f569005239d76ec44629271a7db0280fd584210dd51f51fe8b7e8df2d14ff5`）的 `source`、`seed`、`file_bindings`；D4 [provenance report](D:/FPGA_Competition/report/evidence/S1-T02/20260916_s1_t02_d4_float_baseline_r1.json)（SHA256 `4bbda22f0feb0df1edf5e82701f539ecfe9ac08565d4540ece72364ebcaae7d8`）；plan 所列本地源归档与 patch。D4 report validation 状态是 `BLOCKED`，此处仅引用来源绑定字段，不把它表述为 D4 验收通过。

## 候选与数据绑定

- D6 workflow 当前只读哈希：`a4c77c92eb8f3c62d126cc801d3b82b3f9f8c309b999bd6532a2526721cd0c53`。
- D6 workflow tests 当前只读哈希：`4813f3bfceea9749c42dd7b9688531cb069913bb20308f1dbcb48210448a453a`。
- R3 workflow 报告记录竞赛仓库 HEAD `5de369708c73b0dcac9e17fd56fe54625296f265`；不可变 R2 报告记录 `78f62b61c52040942fa8920628d2cd388306771b`。只读 `git show --stat` 显示 `5de3697` 仅改 `.codex/STATE.md`；本 remediation 未写仓库或 Git，D6 候选文件哈希仍与输入一致。
- D8 权重绑定 SHA256：`c03616fa823181478885d99db21b1f2ed9fd57b59db118776241758b54c4df1e`。
- manifest SHA256：`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`；val/valid-list 计数 15,195，R3 preflight 正常通过清单与获批 no_hand 绑定检查；no_hand val 行为 158680、158681，代表路径为 `20260915_friend_004.png`。没有打开图像像素。

## 命令与运行结果

实际执行的 workflow CLI（完整 argv 亦记录于 JSON）为：

```powershell
py -3 -B verification/s1_t01_darknet_workflow.py evaluate --darknet-executable "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\build_seeded_release_r2\Release\darknet.exe" --environment-report "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\environment_seeded_binding.json" --data-root "D:\FPGA_Data\HaGRIDv2" --manifest "D:\FPGA_Data\HaGRIDv2\manifest.csv" --dataset-report "D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json" --dataset-approval "D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_approval.json" --data-config "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r1\data\gesture_tiny416_d8_formal.data" --model-config "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r1\configs\gesture_yolov4_tiny_416_d8_formal.cfg" --names-file "D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names" --working-directory "D:\FPGA_Data\HaGRIDv2\darknet_inputs" --run-dir "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d6_val_tiny416_6000_r3" --report "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d6_val_tiny416_6000_r3\preflight_evaluate.json" --weights "D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r1\checkpoints\gesture_yolov4_tiny_416_d8_formal_final.weights" --valid-list "D:\FPGA_Data\HaGRIDv2\darknet_inputs\valid.list" --zero-prediction-image "D:\FPGA_Data\HaGRIDv2\user_no_hand\20260915_friend_004.png" --dry-run
```

进程退出码 **0**，报告状态 `PLANNED_NO_EXECUTION`，`commands=[]`、`planned_commands` 长度 1。

唯一计划但未执行的 Darknet argv 末尾为：

```text
-out D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d6_val_tiny416_6000_r3\evaluation.json
-thresh 0.249999
```

补充核验命令：

- `git -C D:\FPGA_Data\darknet rev-parse HEAD`：退出码 0，值为固定 commit。
- Python `git cat-file blob <commit>:src/{detector.c,utils.c,yolo_layer.c}` 字节 SHA256 核验：退出码 0，均匹配上表上游哈希。
- 对 seeded 文件、`seed_support.patch`、源归档、D4 plan/report 执行 `Get-FileHash -Algorithm SHA256`：退出码 0，匹配 JSON 记录值。
- `git -C D:\FPGA_Data\darknet apply --stat <seed_support.patch>` 与 `--numstat`：均退出码 0；只读展示 7 文件 patch scope，没有应用 patch。

完整结构化记录见本目录 `source_binding.json`；R3 workflow 报告见 [preflight_evaluate.json](D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t02_d6_val_tiny416_6000_r3/preflight_evaluate.json)，SHA256 `5cce02ef02cb47ca585f7518812be45b1e9e26e193c482a3514cd598be9c3a7c`。

## 未改变项与限制

- R1/R2 证据保持只读；R2 report SHA256 仍为 `2f7034b6bfcc3852ea8227b63820aaf2b7641a3483b576ca96efdad76d350260`，R2 summary SHA256 仍为 `6eb50dba760ffe4ed01579169ec94ff53fc00d0cf488a4cde239c802de9a4fcc`。
- 未修改 D6 workflow/test、D4 文件、D8 report、项目文档或 STATE；未提交。
- 未进行网络下载、license 判断、GPU/CUDA、Darknet 推理、训练/resume、预测、指标计算、最终阈值选择或精度通过声明。
- Preflight 检查 manifest/审批/标签与路径绑定元数据；无图像像素读取。R3 结束时没有 `evaluation.json`。
- 等待独立 Reviewer 对补充证据复核；D8 G2 仍 `CHANGES_REQUIRED`，本轮不放行 GPU。
