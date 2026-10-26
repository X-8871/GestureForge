# S3-T04 J11+CMOS2 通道变体约束（交叉验证：模块另一路传感器/另一套 LDO）
#
# 用途：模块是双目的，CMOS1 与 CMOS2 有各自独立的 LDO（U2/U3）与复位线。若只有 CMOS1 侧故障，
#       走 CMOS2 通道即可正常出图，从而既能定位故障又能拿到第一版画面。
#
# 依据：
#   - 官方双目例程 23_ov5640_dual 的 an5642.xdc（模块 Pin3–18 = CMOS2 通道各信号，J10 映射）
#   - AX7020 V3.0 手册 Table 7.5.1（J11 针脚表）
#   - 模块 PinN ↔ 扩展口 PinN；本变体固定在 **J11**（模块当前就插在 J11）
#
# 信号对应（模块 pin → CMOS2 信号 → 本设计的 cmos1_* 端口）：
#   pin3  D9    -> cmos1_d[9]      pin11 D3    -> cmos1_d[3]
#   pin4  SDA   -> cmos1_i2c_sda   pin12 RESET -> cmos_rstn_tri_o[0]
#   pin5  D6    -> cmos1_d[6]      pin13 D4    -> cmos1_d[4]
#   pin6  SCL   -> cmos1_i2c_scl   pin14 D5    -> cmos1_d[5]
#   pin7  D7    -> cmos1_d[7]      pin15 D1    -> cmos1_d[1]
#   pin8  D2    -> cmos1_d[2]      pin16 D0    -> cmos1_d[0]
#   pin9  HREF  -> cmos1_href      pin17 VSYNC -> cmos1_vsync
#   pin10 D8    -> cmos1_d[8]      pin18 PCLK  -> cmos1_pclk
#
# 只改 PL 引脚落点，不改 BD 结构、不改软件地址映射、不动厂商原件。

set_property PACKAGE_PIN F17 [get_ports {cmos1_d[9]}]
set_property PACKAGE_PIN F16 [get_ports {cmos1_i2c_sda_io}]
set_property PACKAGE_PIN F20 [get_ports {cmos1_d[6]}]
set_property PACKAGE_PIN F19 [get_ports {cmos1_i2c_scl_io}]
set_property PACKAGE_PIN G20 [get_ports {cmos1_d[7]}]
set_property PACKAGE_PIN G19 [get_ports {cmos1_d[2]}]
set_property PACKAGE_PIN H18 [get_ports {cmos1_href}]
set_property PACKAGE_PIN J18 [get_ports {cmos1_d[8]}]
set_property PACKAGE_PIN L20 [get_ports {cmos1_d[3]}]
set_property PACKAGE_PIN L19 [get_ports {cmos_rstn_tri_o[0]}]
set_property PACKAGE_PIN M20 [get_ports {cmos1_d[4]}]
set_property PACKAGE_PIN M19 [get_ports {cmos1_d[5]}]
set_property PACKAGE_PIN K18 [get_ports {cmos1_d[1]}]
set_property PACKAGE_PIN K17 [get_ports {cmos1_d[0]}]
set_property PACKAGE_PIN J19 [get_ports {cmos1_vsync}]
set_property PACKAGE_PIN K19 [get_ports {cmos1_pclk}]

set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_i2c_sda_io}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[9]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[8]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_i2c_scl_io}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[5]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[6]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[7]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_pclk}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_href}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_vsync}]
set_property IOSTANDARD LVCMOS33 [get_ports {cmos_rstn_tri_o[0]}]

set_property PULLUP true [get_ports cmos1_i2c_scl_io]
set_property PULLUP true [get_ports cmos1_i2c_sda_io]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF]

# 名义时钟依据：厂商初始化摘录注释称 24 MHz 输入下 0x3035=0x21、0x3036=0x69 对应 PCLK=84 MHz；
# v10/v11 板级 UART 回读到 0x3035=0x21（见 t05_color_msb_missing_20261022_r01、t05_stage3_window_20261024_r01）。
# PCLK 尚未由仪器实测，实际频偏须复核后调整周期；该约束仅为名义 STA 假设，不代表时序签核通过。
create_clock -name CMOS1_PCLK -period 11.904762 [get_ports {cmos1_pclk}]
