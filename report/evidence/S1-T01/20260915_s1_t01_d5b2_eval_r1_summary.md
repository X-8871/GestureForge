# S1-T01-D5B-2（AC06）全量 valid 评估摘要

## 结论

本次 AC06 执行失败，不能作为 AC06 通过证据。按任务停止条件在第 1 张验证图失败即停，未进行第二次评估；15195 张图均未完成，Wong 批准的 val no_hand 图也未进入 detector 推理，因此没有 `objects=[]` 的实际评估证明。

## 执行记录

- 执行时间：2026-09-15 19:19:46（UTC+8）启动；2026-09-15 19:23:28（UTC+8）workflow 退出并写报告。
- 运行工作目录：`D:\FPGA_Data\HaGRIDv2\darknet_inputs`
- run-dir：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r1`
- report：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b2_eval_r1.json`
- 顶层状态：`EXECUTION_FAILED`
- 顶层退出码：`2`
- 实际 Darknet 命令数：`1`
- planned commands：`15195`
- valid 清单预检计数：`15195`
- completed image count：`0`
- `ac06_candidate`：`false`
- `all_validation_images_completed`：未满足
- `errors`：`evaluate 第 1 张图未以干净状态结束，失败即停`
- 锁文件：已清理；结束时无本任务 `darknet.exe`、Python workflow 进程。

准确执行命令（未使用 `--dry-run`）：

```text
py D:\FPGA_Competition\verification\s1_t01_darknet_workflow.py evaluate --darknet-executable D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe --environment-report D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v3.json --data-root D:\FPGA_Data\HaGRIDv2 --manifest D:\FPGA_Data\HaGRIDv2\manifest.csv --dataset-report D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json --dataset-approval D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_approval.json --data-config D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.data --model-config D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg --names-file D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names --working-directory D:\FPGA_Data\HaGRIDv2\darknet_inputs --run-dir D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5b2_eval_r1 --report D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b2_eval_r1.json --weights D:\FPGA_Data\HaGRIDv2\darknet_inputs\backup_resume_r1\gesture_yolov4_tiny_416_short_20.weights --valid-list D:\FPGA_Data\HaGRIDv2\darknet_inputs\valid.list --zero-prediction-image D:\FPGA_Data\HaGRIDv2\user_no_hand\20260915_friend_004.png --timeout-seconds 180 --no-progress-timeout-seconds 60
```

预计耗时依据为 15195 个独立 Darknet 进程、每次加载约 23.6 MB 权重，以及 RTX 4060/CUDA smoke 和 D5B-1 单步约 3 秒的保守范围，原计划为 1–8 小时；实际在首图启动阶段失败。

## 失败证据

第 1 张图：

`D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\50775c97-7833-4cc5-92d7-01569cd7d35e.jpg`

实际 Darknet 命令退出码为 `1`，workflow stop reason 为 `日志出现 OOM 或数据损坏停止标记`。日志中重复出现官方 Darknet `load_alphabet()` 对相对路径 `data/labels/32_0.png` 至 `data/labels/126_7.png` 的 `Cannot load image` / `STB Reason: can't fopen`；随后仅输出到网络层 26，未生成 detector output JSON。该工作目录不存在 `data\labels`，官方源 `D:\FPGA_Data\darknet\data\labels` 存在 761 个 alphabet PNG。workflow 当前严格正则将 `Cannot load image` 统一视为失败标记，因此按既定失败即停规则收口。

## 产物清单与哈希

仓库证据：

- `D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b2_eval_r1.json`，11,517,478 bytes，SHA-256 `3a4181382e2f5d05db1bcdbafe4f916994b6eda8612f722bd85cc8241b2dde85`。
- `D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5b2_eval_r1_summary.md`，本摘要。

外部 run-dir：

- `eval_000001.log`，53,377 bytes，SHA-256 `1fcb3e4e07650f8e17eac1d18742578ad7092c84eaf99d1ad5e311125334a87b`。
- `workflow.stdout.log`，209 bytes，SHA-256 `b64c24493ca01444643071b8d8787aabe561ad0de7fe8a1f0a35b27e85cbd4d6`。
- `workflow.stderr.log`，0 bytes，SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。
- `evaluation.json`：未生成。
- `evaluation.jsonl`：0 bytes，SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；无有效记录。
- `detections\`：未产生逐图 JSON。

## 输入绑定哈希

- Darknet exe：`358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`
- workflow：`99558cde41413d8ba97bf1e6cef8b9a8b172d5dd1c452bc7939657b96459ae77`
- cfg：`76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`
- evaluation weights：`580deab95686bf93a2d54d33175459e6e5bf55325700a099ed8dee32da32c9e3`
- gesture.data：`379e02c6a68ccea896f5f16375879d0a52b698a66bd05dfcc7eba66c2068e3c8`
- gesture.names：`5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`
- valid.list：`8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`，预检 15195 行；批准 no_hand 图在第 15194 行。
- manifest：`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`
- dataset report：`9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be`
- approval：`90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213`
- environment report：`fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11`
- zero-prediction image：`D:\FPGA_Data\HaGRIDv2\user_no_hand\20260915_friend_004.png`，SHA-256 `8d79dc6c3cd4bb5e2134dedf4f9f8232586c15d84f2f8106c9dc8e73a781806c`。
- official source rev：`59596d7880f6504768df41d6daa586f5cb2b932f`；失败后核对工作树 clean。失败启动前未单独保存 `git diff --quiet` 的命令回显。

## 限制与未执行项

- 未生成完整逐图 detection JSON、汇总 JSON 或有效 JSONL，不能计算或解释 mAP，也未设置 mAP 下限。
- no_hand 图仅通过 workflow 预检的批准绑定和 valid 清单成员检查，未实际推理，不能宣称 `objects=[]`。
- 未执行数据 checker 复跑、第二次评估、量化、RTL、烧录或最终规格冻结。
- 未修改 valid.list、gesture.data、cfg、names、labels、manifest、D5A/D5B-1 报告或用户既有文件。
- Python 编译检查通过；workflow 单元测试 25/25 通过；本次失败后的补救评估未执行。
