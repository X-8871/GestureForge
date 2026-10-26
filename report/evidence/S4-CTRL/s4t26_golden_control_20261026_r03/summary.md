# 控制实验启动失败记录

- RunId：`s4t26_golden_control_20261026_r03`；结果：`BLOCKED_BEFORE_FORWARD`。
- 命令进程退出码：`3221225781`（`0xC0000135`），持续 0.109 秒；stdout/stderr 均为空。
- 原因：静态 PE 导入含 `pthreadVC2.dll`，原进程 PATH 未含该现有 DLL 目录，Darknet 未进入模型前向。
- stats 未创建，float dump 数量为 0；不能算控制通过或张量不匹配。
- 已有 DLL：`D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_activation_calibration_r1\darknet_source\build\darknet\x64\pthreadVC2.dll`，SHA256 `0e6af724609ef6846982ef717013426c359c455fff324e906d8d55c8bb88d16e`。在后续独立 RunId r04 仅追加该已存在目录到子进程 PATH。
- 本 r03 尝试没有读取或推理校准样本；G0 r12 另行只读核验过校准图像身份/SHA。本记录保留原失败尝试，不覆盖。
