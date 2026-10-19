# S3-T04 J11 变体约束：把官方 22_ov5640_single 的 CMOS1 通道从 J10 改到 J11。
#
# 用途：区分“J10 侧供电/连线问题”与“摄像头模块本体问题”的 A/B 验证。
# 依据：AX7020 V3.0 用户手册 Table 7.5.1 - J11 Expansion Port Pin Assignment
#       （D:\FPGA_Competition\摄像头资料\Wong搜集的资料\AX7020 User Manual_V3.0.pdf, p.30-31）
# 约定：与官方 J10 例程相同 —— 模块 PinN ↔ 扩展口 PinN（CMOS1 占 Pin20–Pin35）。
# 电源/地：Pin1=GND、Pin2=+5V、Pin37/38=GND、Pin39/40=+3.3V（两端口一致）。
#
# 注意：这是本项目自建变体，不是厂商工程；不改变 BD 结构、不影响器件与软件地址映射。

set_property PACKAGE_PIN J20 [get_ports {cmos1_i2c_sda_io}]
set_property PACKAGE_PIN L17 [get_ports {cmos1_d[9]}]
set_property PACKAGE_PIN L16 [get_ports {cmos1_d[8]}]
set_property PACKAGE_PIN M18 [get_ports {cmos1_i2c_scl_io}]
set_property PACKAGE_PIN M17 [get_ports {cmos1_d[5]}]
set_property PACKAGE_PIN D20 [get_ports {cmos1_d[3]}]
set_property PACKAGE_PIN D19 [get_ports {cmos1_d[4]}]
set_property PACKAGE_PIN E19 [get_ports {cmos1_d[6]}]
set_property PACKAGE_PIN E18 [get_ports {cmos1_d[0]}]
set_property PACKAGE_PIN G18 [get_ports {cmos1_d[7]}]
set_property PACKAGE_PIN G17 [get_ports {cmos1_d[1]}]
set_property PACKAGE_PIN H17 [get_ports {cmos1_d[2]}]
set_property PACKAGE_PIN H16 [get_ports {cmos1_pclk}]
set_property PACKAGE_PIN G15 [get_ports {cmos1_href}]
set_property PACKAGE_PIN H15 [get_ports {cmos1_vsync}]
set_property PACKAGE_PIN J14 [get_ports {cmos_rstn_tri_o[0]}]

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

# 与官方 J10 例程相同的处理：PCLK 作为普通 I/O 而非专用时钟引脚
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF]