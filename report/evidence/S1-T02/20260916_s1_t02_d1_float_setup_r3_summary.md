# S1-T02-D1-FLOAT-BASELINE-SETUP-R3

状态：`READ_ONLY_REGENERATED_FROM_R1_NO_PILOT_RERUN`。本轮仅修正 topology parser 和双仓库 provenance；复用既有 r1 pilot，不重跑、不训练、不正式评估、不生成 mAP 结论。r1/r2 证据保持不动。

## topology 修复

- route 按官方 `route_layer.c` 语义计算：`output_channels=sum(input_channels)//groups`，每个输入贡献 `input_channels//groups`；groups/group_id、输入/输出形状和逐层计算均写入 r3 JSON。
- 卷积参数公式：`filters*(input_channels//groups)*size*size + filters + BN(2*filters)`；卷积 BFLOPs：`2*output_width*output_height*kernel_weights/1e9`。maxpool、shortcut 公式也已纳入。
- tiny416 source/setup 关系：source bytes=3499、SHA256 `76ad1108d199150bef8b949a8a67937ca36b33209f8cfe744f2969847c506025`；setup bytes=3507、SHA256 `5c5af96850ca3f13a86decb111fb2710d1b061353d46253ffb16be097da8fa09`；normalized_text_equal=True，关系为“文本等价/换行规范化副本”。
- `gesture_yolov4_tiny_416_float_setup.cfg`：params=5886460，parser BFLOPs=6.793486，layers=38，conv=21，SHA256 `5c5af96850ca3f13a86decb111fb2710d1b061353d46253ffb16be097da8fa09`。来源：外部 parser；BFLOPs 另与既有官方 Darknet pilot 日志 Total BFLOPS 三位小数交叉核对。
  - route layer 3：input_channels=[64]，groups=2，group_id=1，channels_per_input=[32]，output_channels=32。
  - route layer 11：input_channels=[128]，groups=2，group_id=1，channels_per_input=[64]，output_channels=64。
  - route layer 19：input_channels=[256]，groups=2，group_id=1，channels_per_input=[128]，output_channels=128。
- `gesture_yolov4_tiny_320_float_setup.cfg`：params=5886460，parser BFLOPs=4.019814，layers=38，conv=21，SHA256 `9b4da2163d4a540ac2f7535312ffc22d1f465445fd175509575fc601dad74fa8`。来源：外部 parser；BFLOPs 另与既有官方 Darknet pilot 日志 Total BFLOPS 三位小数交叉核对。
  - route layer 3：input_channels=[64]，groups=2，group_id=1，channels_per_input=[32]，output_channels=32。
  - route layer 11：input_channels=[128]，groups=2，group_id=1，channels_per_input=[64]，output_channels=64。
  - route layer 19：input_channels=[256]，groups=2，group_id=1，channels_per_input=[128]，output_channels=128。
- `yolov4_5class_float_pc_setup.cfg`：params=63992378，parser BFLOPs=123.248005，layers=162，conv=110，SHA256 `9f3f518e995a0f536bc0edf0530a10362ead0ec3858466f1bdcc81bfdd71fb41`。来源：外部 parser estimate；无五类完整 YOLOv4 权重和官方完整模型 pilot，不能当作官方运行时数值。

## BFLOPs 交叉核对

- tiny416 parser=6.793486，既有官方日志 `Total BFLOPS 6.793`；tiny320 parser=4.019814，既有官方日志 `Total BFLOPS 4.020`；均按三位小数通过。pilot 日志仅复用，未重跑。
- 完整 YOLOv4 数值明确为 parser estimate，不是官方运行时输出；仍无匹配的五类完整模型权重。

## 双仓库 provenance

- 竞赛仓库：`D:\FPGA_Competition`；`git_head_observed` 为现场 `rev-parse HEAD` stdout `743279ad943c7d38a099f9266009b147616d4382`。完整 argv/cwd/stdout/stderr/exit/time/network_access=false 在 `competition_provenance.commands` 保存；diff exit=1。
- 官方 Darknet source：`D:\FPGA_Data\darknet`；`darknet_source_commit` 为现场 `rev-parse HEAD` stdout `59596d7880f6504768df41d6daa586f5cb2b932f`。完整 argv/cwd/stdout/stderr/exit/time/network_access=false 在 `darknet_source_provenance.commands` 保存；diff exit=0，status exit=0。
- 两个仓库不共用 provenance 字段；r3 不保留语义混用的 `official_source_commit`/`source_provenance` 字段。

## 复用范围和限制

- r1 pilot 的 2 条 tiny416 与 2 条 tiny320 JSON 记录及日志原样复用；`r3_pilot_rerun=false`。未训练、未正式评估、未设置 mAP 阈值。
- r1 JSON SHA `b82408fd17f220c1f9d47ba4f2da375b9858aa1b23b118c7558286af37f24923`；r1 summary SHA `1a53dc04a8a789460af0ed42968ba8fc9947f1f8c682b0c1ef9696449871a4ca`。r2 JSON SHA `26b05b899220cef7955617ae1533262a0629d9084f8c2b9b7e53e1f1d2b566ff`；r2 summary SHA `0c9881c69fe51ed2f91b47de8b6516fa5c358bf80a3d61c3af6a42e141281b63`。
- r3 JSON：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d1_float_setup_r3.json`；SHA 写入后由命令输出。r3 summary：`D:\FPGA_Competition\report\evidence\S1-T02\20260916_s1_t02_d1_float_setup_r3_summary.md`；SHA 写入后由命令输出。

G0 仍需正式冻结数据口径、随机种子、预处理、评估阈值、mAP/每类指标、no_hand 误检、INT8 损失和性能统计标准。
