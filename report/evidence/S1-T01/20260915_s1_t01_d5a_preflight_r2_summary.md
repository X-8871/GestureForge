# S1-T01-D5A 第 2 轮 dry-run 证据摘要

时间：2026-09-15（UTC+8）

## 结论与范围

本记录仅完成 D5A 训练前 dry-run 证据收尾，不代表训练或 S1-T01 验收通过。r2 JSON 的 `status=PLANNED_NO_EXECUTION`、`exit_code=0`；`commands=[]` 表示没有实际 subprocess，`planned_commands` 只有 1 条计划命令。dry-run 日志只记录计划结果，stderr 为空。

日志证据：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5a_preflight_r2\train_dry_run.stdout.log`，SHA-256 `6f0ca0bb79dfeea4334b5ccc7f82291f5e480c75064bf6f49b9d9f770630cf45`；`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t01_d5a_preflight_r2\train_dry_run.stderr.log`，SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

## 计划命令

```text
command="D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe" detector train "D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.data" "D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg" "D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29" -dont_show
cwd=D:\FPGA_Data\HaGRIDv2\darknet_inputs
```

真实输入路径保持为：

- manifest：`D:\FPGA_Data\HaGRIDv2\manifest.csv`
- dataset report：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_check_semantic_after_no_hand.json`
- dataset approval：`D:\FPGA_Competition\report\evidence\S1-T01\20260915_hagrid_dataset_approval.json`
- 初始权重：`D:\FPGA_Data\darknet\weights\yolov4-tiny.conv.29`
- cfg：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg`
- Darknet binary：`D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe`

## 输入、身份与哈希

只读重算与已有证据一致：

- 权重大小 `19,789,716` bytes，SHA-256 `3c794b8420b12ed2a609daa71d075880e7bd152671323f5eb3e8d9e57e31785b`；可读、非零、非 HTML，`.part` 残留为 0。
- cfg SHA-256：`76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`。
- Darknet binary SHA-256：`358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f`。
- 固定 Darknet source commit：`59596d7880f6504768df41d6daa586f5cb2b932f`；外部只读 `git diff --quiet` exit `0`。该 commit 由 `20260915_darknet_identity_v3.md` 与 `20260915_round3_manifest_consistency.log` 支持。
- manifest SHA-256：`fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74`。
- dataset report SHA-256：`9b2e4336e30ab49dfd4dfcfa4c9363be8ab82ec13f9fe80c55d8a3412b3277be`。
- dataset approval SHA-256：`90f37987de1cea597515926115fe064ed20df3f83f40ca45a04b41b86c0da213`。
- environment report SHA-256：`fa5e1265b0106d1e7357b18f387fc1c5d5dc9f3ce623f1a33734f1021de43d11`。
- data config SHA-256：`379e02c6a68ccea896f5f16375879d0a52b698a66bd05dfcc7eba66c2068e3c8`；names、train.list、valid.list 哈希分别为 `5926aa20da3fa403315e64a116202d355b044d17f6d7949f5709ce9c9ae3d368`、`4d8e965e7fc3f5d8a9f1ec3613fadb72c50b8463f78feebf863fd26978c8e3fa`、`8fa102bb95aca67bd862ad2e29194a51360abe8c34195efae750e07869f22e3c`。

本轮只读核对还确认：backup 文件数为 `0`，目标 checkpoint 不存在；r2 JSON 记录的 process before/after 均无 `darknet.exe`，当前 `tasklist /FI "IMAGENAME eq darknet.exe"` exit `0` 且无匹配进程。

## 已有验证证据（未在本次收尾重复执行）

以下退出码来自已有证据文件，不能表述为本次 summary 写入时重新运行：

- 回归：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest verification.test_s1_t01_environment_probe -v`，exit `0`，8 项全部 `OK`；证据：`20260915_round2_validation.md`。
- Python 编译静态检查：`C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m py_compile verification/s1_t01_environment_probe.py verification/test_s1_t01_environment_probe.py`，exit `0`；同一证据文件。
- 静态差异检查：`git diff --check`，exit `0`；同一证据文件。
- 第 3 轮哈希一致性证据：41 项 manifest/actual 不一致数为 `0`，environment probe exit `0`、status `PASS`；证据：`20260915_round3_manifest_consistency.log`。

## 明确未执行事项、停止条件与下一步

本次未执行真实 `train`、`resume`、`evaluate`、权重量化、RTL、烧录，也未重新下载权重；`backup checkpoint=0` 是空目录事实，不是训练成功的 checkpoint。不得将 dry-run 的 `exit_code=0` 解读为 Darknet train exit code。

停止条件包括：短训 cfg 的 `max_batches` 超出安全上限时在启动前停止；已有候选 checkpoint 时不得覆盖；发现 NaN/Inf、OOM、损坏输入或不满足固定身份/哈希时停止；evaluate 后续必须以 detector test 输出 JSON 的 objects 数量证明零框并拒绝异常结果。

下一步由总控按固定输入先完成 AC04 证据复核，再由 Wong 决定是否启动受控短训及后续 resume/evaluate 闭环；本记录不跨入 AC05～AC07、正式长训或阶段2。
