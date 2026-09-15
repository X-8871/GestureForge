# S1-T01-D5A 修复第 1 轮 Developer 摘要

## 结果

- Reviewer 前轮结论：`CHANGES_REQUIRED`，审查文件：`C:\Users\22061\AppData\Local\Temp\review-s1-t01-d5a-20260915\review_s1_t01_d5a_final.json`。
- 权重下载阻断：已解决。
- cfg 静态检查：通过。
- 输入绑定哈希重核：现有已批准绑定通过；用户本轮指定的三个外部 JSON 路径缺失。
- 指定 `train --dry-run`：已执行但返回 `BLOCKED_PREFLIGHT`，不是 `PLANNED_NO_EXECUTION`，因此本轮不满足完整 dry-run 验收。
- 实际仓库 HEAD：`cb4e032c2d182bbb06565ae27620a31eef322366`；Developer 未提交 Git。

## 进程与目录保护

- 开始前 `Get-Process` 未发现 `darknet/python/msbuild/nvcc` 相关进程。
- 开始前 `tasklist /FI "IMAGENAME eq darknet.exe" /FO CSV /NH`：无匹配进程。
- 只在不存在时创建：`D:\FPGA_Data\darknet\weights`；本轮创建成功，未删除、覆盖或清理其他文件。
- 下载前最终权重和 `.part` 均不存在。
- dry-run 后 `darknet.exe` 仍无匹配进程。
- `D:\FPGA_Data\HaGRIDv2\darknet_inputs\backup` 文件数为 `0`；`_5`、`_10`、`_20`、`_last`、`_final` 候选均不存在。

## 官方权重

- URL：`https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.conv.29`
- `.part` 下载命令：`curl.exe -L --fail --retry 2 --silent --show-error --output "D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29.part" "https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.conv.29"`
- curl 退出码：`0`。
- `.part` 校验：`19789716` 字节，SHA-256 `3c794b8420b12ed2a609daa71d075880e7bd152671323f5eb3e8d9e57e31785b`；首部 `00-00-00-00-02-00-00-00-05-00-00-00-00-00-00-00-00-00-00-00-D5-23-B1-C0-E3-D6-E4-3F-41-F6-4C-3F`；可读取；非零；非 HTML。
- 安全移动命令：`Move-Item -LiteralPath "D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29.part" -Destination "D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29"`，退出码 `0`。
- 最终文件：`D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29`，`19789716` 字节，SHA-256 `3c794b8420b12ed2a609daa71d075880e7bd152671323f5eb3e8d9e57e31785b`；可读取；非零；非 HTML；`.part` 不存在。
- 备用 `Invoke-WebRequest` 未执行，因为 curl 已成功；未使用非官方来源。

## cfg 与现有输入绑定

- cfg：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg`，SHA-256 `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`。
- 官方源 cfg：`D:\FPGA_Data\darknet\cfg\yolov4-tiny.cfg`，SHA-256 `a6415c2e303f7b3647913a7bb3675f0fe7234049d8875ae7d75c01b8e4dcb854`；源 tracked diff 退出码 `0`，仅有历史未跟踪 build 目录。
- 独立静态检查：规范化行尾后与官方源精确派生，294/294 行一致；`yolo_heads=2`、`classes=5` 为 2、`filters=30` 为 2、`random=0` 为 2，状态 `PASS`。
- 固定字段：`batch=64`、`subdivisions=16`、`width=416`、`height=416`、`max_batches=20`、`steps=16,18`。

当前已批准实际绑定重核哈希：

| 文件 | SHA-256 |
|---|---|
| `D:\FPGA_Data\HaGRIDv2\manifest.csv` | `fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.data` | `379e02c6a68ccea896f5f16375879d0a52b698a66bd05dfcc7eba66c2068e3c8` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names` | `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\train.list` | `4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa` |
| `D:\FPGA_Data\HaGRIDv2\darknet_inputs\valid.list` | `8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c` |
| `D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_approval.json` | `90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213` |
| `D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json` | `9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be` |
| `D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v3.json` | `fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11` |

用户本轮要求的路径均已按原样检查：

- `D:\FPGA_Data\HaGRIDv2\manifests\dataset_manifest.json`：不存在。
- `D:\FPGA_Data\HaGRIDv2\reports\dataset_report.json`：不存在。
- `D:\FPGA_Data\HaGRIDv2\manifests\dataset_approval.json`：不存在。

未创建上述缺失文件，也未用现有 `manifest.csv`、仓库 dataset report 或仓库 approval JSON 静默替换；否则会改变输入绑定语义。

## 指定 dry-run

- 隔离运行目录：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5a_preflight_r1`
- workflow 报告：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_s1_t01_d5a_preflight_r1.json`
- 报告大小：`19360292` 字节；SHA-256：`8b3e28171cce2c3f2b707280cf57935b56948849536386de249decf026176b87b`
- stdout：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5a_preflight_r1\train_dry_run.stdout.log`，大小 `18286785`，SHA-256 `960e69757050e438e17ed19b70f1fa771b99b559d9012cd2a9fa48848397399b`。
- stderr：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5a_preflight_r1\train_dry_run.stderr.log`，大小 `0`，SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。
- 执行环境：先调用 `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat`，再将 CUDA `bin/x64`、CUDA `bin`、Darknet pthreads DLL 目录置于 PATH 前端。
- workflow 返回码：`2`。
- workflow 状态：`BLOCKED_PREFLIGHT`；`commands=[]`；`planned_commands` 为 1 条；未启动 Darknet。
- 阻断首要错误：manifest、dataset report、dataset approval 的用户指定路径不存在。因 manifest 缺失，workflow 进一步产生清单集合错误；原始报告保留全部真实输出。
- checkpoint-output 参数按 cfg 基名和 `.data` backup 规则使用：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\backup\gesture_yolov4_tiny_416_short_10.weights`；dry-run 未写入 backup。

## 自动检查

- `py_compile`：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m py_compile verification/s1_t01_darknet_workflow.py`，退出码 `0`；缓存写入隔离临时目录。
- `python -B -m unittest verification.test_s1_t01_darknet_workflow -v`：24 项通过，退出码 `0`。
- `git diff --check`：退出码 `0`。

## 停止条件与限制

- 未执行真实 train、resume、evaluate、量化、RTL、烧录或阶段2操作。
- 当前仍不能宣称 AC05、AC06、AC07、S1-T01 或阶段1通过。
- 下一轮必须先提供/确认与当前批准绑定一致的三个指定 JSON 输入文件路径；不能通过复制、重命名或替换旧文件绕过绑定检查。路径修复后，重跑同一隔离 dry-run，目标状态才是 `PLANNED_NO_EXECUTION`。
- 本轮只新增本摘要和上述隔离证据；用户已有文档、Vivado 工程、五张图片及无关 Git 改动未修改、未暂存。
