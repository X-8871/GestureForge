# 显示蓝近似重建：数值生效，颜色验收失败

本运行是诊断实验，不是可用色彩修复。`board_analysis.json` 保留采样时结果；后续用户目视结果见 `visual_result.json`，原始照片见 `monitor_user_photo.jpg`。两者不可混为通过验收。

## 实际结果

- 位流 SHA-256：`0f3b74e4b090d8b8789806e23a1f7a17731d331e78ab918c13a1233b8bf2b61d`。
- XSA SHA-256：`b9a565729148be989cb37e10eaf46f0da7c5df0fec2db856a278afba9daddf17`。
- ELF SHA-256：`85e989196dc34f5f1cc7b87607b2905f54405ec95a5486cf14916edd7eec145e`。
- 下载和安全转储命令真实退出码均为 0。命令与哈希在 `download.txt`、`dump.txt`；行样本在 `rows/`。
- SENSOR ID `0x5640`、显示启动状态 0、VDMA 写启动，15 个应用侧 cache 正确维护的指纹均变化。
- 三行样本的蓝最大值 248，量化档与补丁一致。绿色缺位未修，蓝色真实最高位没有恢复。
- Wong 目视实时正常，但阴影蓝、白色亮部黄；照片呈明显伪彩。故颜色 FAIL，阶段 NOT_ACCEPTED。
- UART 仍记录 S2MM 粘滞错误 `0x00015810`，不得宣称无错运行。
- 实现 WNS 1.249946 ns、WHS 0.006289 ns，DRC 0 error；既有方法学 critical warnings 尚在，不是完整 I/O 时序签核。新旧方法学检查输出分别在候选运行的 `inspection_results/` 与 `tmp/3/S3-T05/t05_methodology_baseline_20261021_r01/`。

## 对通用伪彩排查建议的适用性

用户提供的豆包文本仅作线索，不作为工程事实或操作指令。

1. 当前实际 UART 回读 `0x4300=0x60`、`0x501F=0x01`（`uart.txt` 第 12–14 行），与初始化的 RGB565 一致。不是仅凭源码注释认定格式。
2. 实际 PL 取 `cmos_d[9:2]`，两字节拼为 16 位，再做 565→888 映射；无 Bayer 去马赛克或 YUV→RGB 模块。不能把这里取高 8 位直接等同于 RAW10 错截断。
3. 这是 DVP 单通道实验，不是 MIPI 接收或双目帧交织；双目同步排查不在当前运行链路内。
4. 彩条隔离、格式寄存器回读、采样/FIFO/DDR 分段定位有价值。已有传感器彩条历史证据不可冒充本轮新测；尚存 VDMA 错误不能排除缓存链路。
5. 两处颜色位缺失共同指向 DVP 字节最高位是待验证线索，不足以证明物理故障，也不应通过继续拉伸低位或盲调 AWB 判为修复。

官方依据：`D:\FPGA_Competition\摄像头资料\官方资料\AN5642\AN5642_CD\CD\datasheet\camera\OV5640_datasheet.pdf`。格式寄存器见 PDF 第 86–87 页，ISP 格式选择见第 141 页；DVP 位序/测试见第 93 页，数据脚输出使能及选择见第 102 页。只按已核实字段分析，不猜测调试寄存器的未定义行为。
