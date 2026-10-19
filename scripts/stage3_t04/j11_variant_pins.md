# J11 变体引脚映射（备用方案，尚未构建）

用途：若需把 AN5642 模块改插到 **J11** 以区分"J10 供电/连线"与"模块本体"故障，用本表替换
`an5642.xdc` 中的 `PACKAGE_PIN`（其余 IOSTANDARD/PULLUP/CLOCK_DEDICATE_ROUTE 不变）。

来源：AX7020 V3.0 用户手册 **Table 7.5.1 - J11 Expansion Port Pin Assignment**（本地 PDF：
`D:\FPGA_Competition\摄像头资料\Wong搜集的资料\AX7020 User Manual_V3.0.pdf`，p.30–31）。
约定与 J10 官方例程相同：**模块 PinN ↔ 扩展口 PinN**（CMOS1 占 Pin20–Pin35）。

| 信号（本设计） | 模块/J11 Pin | J10 原映射 | J11 映射 |
|---|---|---|---|
| cmos1_i2c_sda_io | 20 | T16 | **J20** |
| cmos1_d[9] | 21 | V18 | **L17** |
| cmos1_d[8] | 22 | V17 | **L16** |
| cmos1_i2c_scl_io | 23 | T15 | **M18** |
| cmos1_d[5] | 24 | T14 | **M17** |
| cmos1_d[3] | 25 | V13 | **D20** |
| cmos1_d[4] | 26 | U13 | **D19** |
| cmos1_d[6] | 27 | W13 | **E19** |
| cmos1_d[0] | 28 | V12 | **E18** |
| cmos1_d[7] | 29 | U12 | **G18** |
| cmos1_d[1] | 30 | T12 | **G17** |
| cmos1_d[2] | 31 | T10 | **H17** |
| cmos1_pclk | 32 | T11 | **H16** |
| cmos1_href | 33 | A20 | **G15** |
| cmos1_vsync | 34 | B19 | **H15** |
| cmos_rstn_tri_o[0] | 35 | B20 | **J14** |

电源/地（两个口一致）：Pin1=GND、Pin2=+5V、Pin37/38=GND、Pin39/40=+3.3V。

注意：J11 全部位于 BANK35，与 J10 的 BANK34/35 组合不同；I/O 标准仍为 LVCMOS33。
构建前需新 RunId，且必须重新生成软件 BSP/ELF（外设地址不变，但硬件平台需重新导出）。