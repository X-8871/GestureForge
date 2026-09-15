# S1-T02-D1-FLOAT-BASELINE-SETUP-R2

状态：`READ_ONLY_REGENERATED_FROM_R1_NO_PILOT_RERUN`。本轮仅修复 r1 Reviewer 指出的语义和 provenance 缺陷；不运行 pilot、不训练、不正式评估。r1 JSON/summary、配置和 pilot 原始文件保持不动。

## 修复项

- tiny416 不称为字节完全一致副本，准确表述为“文本等价/换行规范化副本”。固定项目 cfg 为 3499 bytes，setup cfg 为 3507 bytes；二者 UTF-8 换行规范化后文本相等。
- source cfg：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\configs\gesture_yolov4_tiny_416_short.cfg`，bytes=3499，SHA256 `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`。
- setup cfg：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\s1_t02_float_setup_r1\configs\gesture_yolov4_tiny_416_float_setup.cfg`，bytes=3507，SHA256 `5c5af96850ca3f13a86decb111fb2710d1b061353d46253ffb16be097da8fa09`。
- tiny320/full 配置、拓扑、诊断权重和两次真实 pilot 数据均从 r1 复用，未重复运行。

## 现场 source provenance

- repository/cwd：`D:\FPGA_Data\darknet`。实际 `rev-parse HEAD` stdout 为 `59596d7880f6504768df41d6daa586f5cb2b932f`，退出码 `0`；该值同时写入 `official_source_commit`。
- 实际 `git diff --quiet` 退出码 `0`；`git status --short` 退出码 `0`。三条命令的 argv/stdout/stderr/观察时间/network_access=false 均在 r2 JSON `source_provenance.commands` 中保存。
- 本地 Git 探测没有网络访问；未把网络访问或未执行命令写成事实。

## r1 真实结果（复用，不改写为精度结论）

- tiny416 pilot 和 tiny320 pilot 均退出码 0，各生成 2 条合法 JSON 记录；日志无 NaN/Inf/OOM/error。
- tiny416 正样本 0 框、friend_004 0 框；tiny320 正样本 1 个 fist、friend_004 0 框。结果仅是加载/拓扑/短时 pilot，不是 mAP、精度或最终模型结论。
- diagnostic weights：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\diag_s1_t01_d5b2_200\backup\gesture_yolov4_tiny_416_diag_200_200.weights`，SHA256 `ba3ba3bff1b12c0f3b5b23df9c5fb22ea9744eeb05f78ea1fe109ccc73671017`。

## r2 证据

- JSON：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d1_float_setup_r2.json`，SHA256 `26b05b899220cef7955617ae1533262a0629d9084f8c2b9b7e53e1f1d2b566ff`。
- 本摘要：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d1_float_setup_r2_summary.md`；摘要 SHA256 在写入后由命令输出。
- r1 原始证据保持不动；本轮仅新增 r2 JSON/summary，并修改外部 setup 脚本以支持只读重生成。

## 未执行与后续

未训练、未正式 test/mAP 评估、未下载完整 YOLOv4 权重、未执行 INT8/RTL。G0 仍需冻结数据口径、随机种子、预处理、score/IoU/NMS、mAP/每类指标、no_hand 误检、INT8 损失和性能统计标准。
