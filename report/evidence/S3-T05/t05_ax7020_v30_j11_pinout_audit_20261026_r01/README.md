# AX7020 V3.0 手册与阶段三 J11 引脚映射核对

- RunId：t05_ax7020_v30_j11_pinout_audit_20261026_r01
- 核对时间：2026-10-26（UTC+8）
- 阶段三工作树基线：8f937b4955f54c566b567222e1df07747dfba22c
- 输入手册：D:\FPGA_Competition\摄像头资料\Wong搜集的资料\AX7020_User Manual_V3.0.pdf
- 输入手册 SHA-256：2c17f708ecbc01c9c870d9bfdfed3b7706dbe86cf6dec08f75c9a710e5ce13ee
- 对照约束：board/stage3/hardware/an5642_j11_cmos2.xdc
- 对照约束 SHA-256：d1d3e976f84e0aa5a67ff695d07c83983cf32887c463d6bf25250821f64aa595

## 核对方法

用户确认使用文件名中 AX7020 后带下划线的候选手册后，使用本机 read-pdf-reliably Skill 的 Docling 2.115.0 解析 PDF 第 23–33 页，text 模式、180 DPI、OCR 未启用、无解析警告。视觉复核手册印刷页 29–31（随本记录保存）。随后逐项比较手册 J11 表中的封装坐标与基线 XDC 的 PACKAGE_PIN 约束。原始解析参数见 source_provenance.json。

机器核对命令：C:\Users\22061\.codex\skills\read-pdf-reliably\.venv\Scripts\python.exe -B report/evidence/S3-T05/t05_ax7020_v30_j11_pinout_audit_20261026_r01/verify_j11_pin_map.py；本次退出码为 0，输出 PIN3-18 共 16/16 一致。该脚本只校验从手册表摘录的坐标是否与 XDC 一致，手册原表内容仍以随包页面图为依据。

## 结果

手册印刷第 29 页 §7.5 将 J11 描述为 40 针、2.54 mm 双排扩展接口，连接到 ZYNQ PL BANK35，默认 I/O 电平 3.3 V；还说明连接器与 FPGA 之间有串联 33 Ω 电阻阵列。手册印刷第 29–31 页表 7.5.1 给出 J11 接点到 ZYNQ 封装坐标的映射。

手册表与 an5642_j11_cmos2.xdc 中的 PACKAGE_PIN 映射逐项一致：

| J11 接点 | 封装坐标 | 阶段三 XDC 端口 |
|---:|:---:|:---|
| 3 | F17 | cmos1_d[9] |
| 4 | F16 | cmos1_i2c_sda_io |
| 5 | F20 | cmos1_d[6] |
| 6 | F19 | cmos1_i2c_scl_io |
| 7 | G20 | cmos1_d[7] |
| 8 | G19 | cmos1_d[2] |
| 9 | H18 | cmos1_href |
| 10 | J18 | cmos1_d[8] |
| 11 | L20 | cmos1_d[3] |
| 12 | L19 | cmos_rstn_tri_o[0] |
| 13 | M20 | cmos1_d[4] |
| 14 | M19 | cmos1_d[5] |
| 15 | K18 | cmos1_d[1] |
| 16 | K17 | cmos1_d[0] |
| 17 | J19 | cmos1_vsync |
| 18 | K19 | cmos1_pclk |

XDC 注释说明这些模块接点属于 CMOS2 通道，而设计顶层端口沿用 cmos1_* 命名；本记录保留这一区别，不把端口命名误读成物理 CMOS1 通道。对本次最相关的时钟脚，手册 J11 PIN18=K19 与 XDC cmos1_pclk=K19 一致。

## 结论边界

这次核对只确认“AX7020 V3.0 手册所列 J11 接点封装坐标”与“阶段三基线 XDC PACKAGE_PIN 声明”相互一致。它没有独立确认当前实物 PCB 修订、相机转接板的实际接线或板卡标签与该手册版本的对应关系。

手册未给出当前摄像头 DVP 数据相对 PCLK 的有效 setup/hold 或输入延迟，也未给出板级走线、连接器和传感器输出延迟。33 Ω 电阻值不能单独换算为 I/O delay。不得从本手册推导或补造 set_input_delay 数值。

因此，本证据只补充 J11 pinout 的文档交叉核对；C2、I/O delay、TIMING-17/36、VDMA 根因、task-11 完整等价、G3/G4/G5 均不因本记录而关闭。阶段三仍未冻结。

## 保存的页面

- page-0029.png：手册印刷第 29 页，§7.5 与 J11 表开头。
- page-0030.png：手册印刷第 30 页，J11 表中段。
- page-0031.png：手册印刷第 31 页，J11 表尾及后续章节开头。
