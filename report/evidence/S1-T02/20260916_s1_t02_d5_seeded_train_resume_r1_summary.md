# S1-T02-D5 seeded tiny416 train/resume 短训证据

## 结论与边界

本轮真实执行完成 tiny416 的官方 Darknet seeded train/resume 短训链。train 与 resume 均为 `EXECUTED_REVIEW_REQUIRED`、workflow 顶层 `exit_code=0`、`errors=[]`。这是流程候选和恢复链证据，不是正式模型、bit-exact 训练、mAP/精度、INT8、full YOLOv4、Vivado 或板上通过；正式 test/mAP、full 训练和板测均 `NOT_EXECUTED`。

固定 seed 为 `424242`，环境变量名为 `GESTUREFORGE_DARKNET_SEED`。workflow 只在 Darknet 子进程环境中设置该变量，父 Python 环境保持不变。D4 已观察到相同 seed 的 CUDA/并发结果不同，故 `bit_exact=false`。

## 实际时间与状态

| 动作 | UTC+8 开始 | workflow 完成/日志结束 | 退出码 | 观察步数 | 日志 | 指定 checkpoint |
|---|---|---|---:|---|---|---|
| train | 2026-09-16 18:15:26 | 约18:16:59 | 0 | 1..20 | `train/train.log`，SHA `53bfa0afbc40d02087d5776da85c8b209f0747430eca30cc977245ece5d9b9bf` | step10，SHA `8573cd4933c6ac8fc5d7d6349daa73ebe1f4f8302f900cb0eeceacd24c0b7422` |
| resume | 2026-09-16 18:17:43 | 约18:19:09 | 0 | 11..20 | `resume/resume.log`，SHA `8527962d41af3df8b2786207435298a65dbe5f64af69c1c820e672fea46c724f` | 新 last，SHA `3947286f2b8c1d3c90e4b2420cb6878edb1d8dfb92da98a8cbb349b0c22dbdda` |

两次均未观察 NaN/Inf、OOM、损坏输入、STOP_RE 或无进度停止；完成后无 Darknet/Python/MSBuild 相关后台进程。train 另外生成的 step20/last/final 保留在外部隔离目录，但 resume 只使用 step10 numbered checkpoint。

## 实际命令

两次命令均在 `D:\FPGA_Data\HaGRIDv2\darknet_inputs` 运行，workflow 使用 `shell=False`；PATH 仅在当前 PowerShell 进程及其子进程中临时追加：

```text
D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\build_seeded_release_r2\Release\darknet.exe detector train <data-config> <cfg> <weights-or-checkpoint> -dont_show
```

train 的实际 argv：

```text
darknet.exe detector train D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\train\data\gesture_tiny416_d5_short.data D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\train\configs\gesture_yolov4_tiny_416_d5_short.cfg D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29 -dont_show
```

resume 的实际 argv：

```text
darknet.exe detector train D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\resume\data\gesture_tiny416_d5_short.data D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\resume\configs\gesture_yolov4_tiny_416_d5_short.cfg D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\train\backup\gesture_yolov4_tiny_416_d5_short_10.weights -dont_show
```

workflow 参数还分别为 `--darknet-seed 424242 --timeout-seconds 900 --no-progress-timeout-seconds 300`，并显式使用 `--checkpoint-output` 指定新输出。输入数据根实际使用 `D:\FPGA_Data\HaGRIDv2`，因为 dataset report/approval 的 `data_root` 绑定该路径；Darknet 工作目录仍为 `D:\FPGA_Data\HaGRIDv2\darknet_inputs`。

## 文件与 SHA-256 绑定

### workflow 机器报告

- train report：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d5_seeded_train_resume_r1_train.json`，SHA `7f0ea6051b7a6882567c95ee98bb63917cceace1b32b82e848c2214b5af79771`。
- resume report：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d5_seeded_train_resume_r1_resume.json`，SHA `57f9f10149ce099e752f096b486769ffb05993ab0e926c7f24c4a44b43e28ca6`。
- 两份报告均记录 `seed_binding.passed_to_child_process=true`、`parent_process_unchanged=true`，并记录实际 argv/cwd、workflow 状态、观察步数、日志 SHA、checkpoint 映射和错误数组。

### 外部 seeded 环境与 D4 构建绑定

- seeded environment binding：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\environment_seeded_binding.json`，SHA `ebd70a70a8da348ff2b80622384b6bccc7090e46278d8ac11bd7d31dd8e095f9`。
- seeded executable：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\build_seeded_release_r2\Release\darknet.exe`，SHA `01c96dccb902a3f1f776b1619188a30bef7b33bf5ed607f466de0b6eedf1635e`。
- official Darknet source：`D:\FPGA_Data\darknet`，现场 `git rev-parse HEAD` 为 `59596d7880f6504768df41d6daa586f5cb2b932f`；现场 `git diff --quiet` 退出码 `0`，未改动 tracked source，status 仅有外部 `build/`、`weights/` 未跟踪目录。
- D4 source archive SHA：`474916bd5b61b6e913e1d9b6bd4e3a48117000be62deffe5191f966df85a1a47`。
- seed patch：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_float_baseline_r1\seed_support.patch`，SHA `b3025639731271fac3476647823e5cb4cfa1a09e9fd54fedf36cd45e6539c01b`。
- D4 configure/build log SHA：`5b74a689bd14f7f52858b351b5fd4b8176c42665c6b3cefe74d1d0d97af9fb66` / `12459520033a6ccbe467e65aed4d6b4781539a9d15588a8519e8418c61a3e8db`。
- 未修改已提交的旧 environment report；本轮 binding 来源报告 SHA 为 `fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11`，D4 report SHA 为 `4bbda22f0feb0df1edf5e82701f539ecfe9ac08565d4540ece72364ebcaae7d8`。

### 模型、数据与代码

- train/resume cfg：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d5_seed_short_r1\train\configs\gesture_yolov4_tiny_416_d5_short.cfg` 与对应 `resume\configs`，两者 SHA 均为 `8a1f3f4ff84d59bb9c32eceeb8c32e1f9372d1def06fe56d8cd0241c80dc744a`；仅 `max_batches=20`，其余 formal tiny416 训练字段保留。
- train data SHA `24ac02adb4fdf5d0bde7e482c0dec46223d031ba4f8acf68a4eeb4cb4238b57a`；resume data SHA `537c14ffe6e2bda6cb2a97be39fe336986e9823b240c69e61f2221c97d5837c9`。
- 初始权重 `D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29`，SHA `3c794b8420b12ed2a609daa71d075880e7bd152671323f5eb3e8d9e57e31785b`。
- names SHA `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`；train.list SHA `4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa`；valid.list SHA `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`；manifest SHA `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- dataset report SHA `9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be`；dataset approval SHA `90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213`。
- 当前竞争仓库 HEAD `1ae869b97db0c8012c69d980dc2c3c27643bc9ef`；workflow 源 SHA `7121439c4b3b47ca63b21f677acb2c33e3a2a990d94054b6cc98a2e3359aa588`；workflow 测试源 SHA `ed1aede99a142ccda5dc9b2c96578028c11225f4f3a759393b1169018ec896f0`。

## 预检与未执行项

- train dry-run：状态 `PLANNED_NO_EXECUTION`、exit `0`、errors `[]`；实际数据绑定使用 canonical data root。
- train/resume 真实 workflow：均 `EXECUTED_REVIEW_REQUIRED`、exit `0`、errors `[]`。
- 未执行 full YOLOv4 训练、正式 test/mAP、robustness、INT8、Vivado 综合、烧录和板上测量。
- 本轮未修改 workflow/test；未修改 D4 文件、官方 source、原始数据、manifest/list、用户文件；未提交 Git。
