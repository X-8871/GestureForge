# S3-T05-PL2 J10 + 模块 CMOS2 通道约束（交叉验证变体）
#
# 用途：把 AN5642 双目模块的 **CMOS2 通道** 接到开发板的 **J10** 扩展口（模块当前插在 J11 时
#       实测 RGB565 的 B[4] 恒为 0、蓝最大恒 120；本变体改插 J10 用完全不同的 FPGA 脚，
#       用于判定该缺陷在「板侧 J11 走线」还是在「模块 D6 走线」）。
#
# 依据（两份独立资料一致）：
#   1) 官方双目例程 23_ov5640_dual 的 src/constraints/an5642.xdc —— cmos2 通道 16 个信号的
#      PACKAGE_PIN 落点（本文件逐条照抄，只把 cmos2_* 端口名换成单相机设计的 cmos1_*，
#      并把 cmos_rstn_tri_o[1] 换成 1 位 GPIO 的 cmos_rstn_tri_o[0]）。
#   2) AX7020 V3.0 手册 Table 7.4.1（J10 针脚表）：模块 pin3–18 ↔ J10 pin3–18。
#
# 信号对应（模块 pin → 官方 cmos2 信号 → 本设计端口 → J10 pin → FPGA）：
#   pin3  D9    -> cmos2_d[9]      -> cmos1_d[9]        -> J10 pin3  -> W19
#   pin4  SDA   -> cmos2_i2c_sda   -> cmos1_i2c_sda_io  -> J10 pin4  -> W18
#   pin5  D6    -> cmos2_d[6]      -> cmos1_d[6]        -> J10 pin5  -> R14   <== B[4] 缺失位所对应的数据线
#   pin6  SCL   -> cmos2_i2c_scl   -> cmos1_i2c_scl_io  -> J10 pin6  -> P14
#   pin7  D7    -> cmos2_d[7]      -> cmos1_d[7]        -> J10 pin7  -> Y17
#   pin8  D2    -> cmos2_d[2]      -> cmos1_d[2]        -> J10 pin8  -> Y16
#   pin9  HREF  -> cmos2_href      -> cmos1_href        -> J10 pin9  -> W15
#   pin10 D8    -> cmos2_d[8]      -> cmos1_d[8]        -> J10 pin10 -> V15
#   pin11 D3    -> cmos2_d[3]      -> cmos1_d[3]        -> J10 pin11 -> Y14
#   pin12 RESET -> cmos_rstn[1]    -> cmos_rstn_tri_o[0]-> J10 pin12 -> W14
#   pin13 D4    -> cmos2_d[4]      -> cmos1_d[4]        -> J10 pin13 -> P18
#   pin14 D5    -> cmos2_d[5]      -> cmos1_d[5]        -> J10 pin14 -> N17
#   pin15 D1    -> cmos2_d[1]      -> cmos1_d[1]        -> J10 pin15 -> U15
#   pin16 D0    -> cmos2_d[0]      -> cmos1_d[0]        -> J10 pin16 -> U14
#   pin17 VSYNC -> cmos2_vsync     -> cmos1_vsync       -> J10 pin17 -> P16
#   pin18 PCLK  -> cmos2_pclk      -> cmos1_pclk        -> J10 pin18 -> P15
#
# 24 位数据线的映射与 J11 变体完全同序（D9..D0 → cmos1_d[9:0]），只换 FPGA 落点。
# 只改引脚落点，不改 BD 结构、不改软件地址映射、不动厂商原件、不打开 DEBUG_OV5640。

set_property PACKAGE_PIN W19 [get_ports {cmos1_d[9]}]
set_property PACKAGE_PIN W18 [get_ports {cmos1_i2c_sda_io}]
set_property PACKAGE_PIN R14 [get_ports {cmos1_d[6]}]
set_property PACKAGE_PIN P14 [get_ports {cmos1_i2c_scl_io}]
set_property PACKAGE_PIN Y17 [get_ports {cmos1_d[7]}]
set_property PACKAGE_PIN Y16 [get_ports {cmos1_d[2]}]
set_property PACKAGE_PIN W15 [get_ports {cmos1_href}]
set_property PACKAGE_PIN V15 [get_ports {cmos1_d[8]}]
set_property PACKAGE_PIN Y14 [get_ports {cmos1_d[3]}]
set_property PACKAGE_PIN W14 [get_ports {cmos_rstn_tri_o[0]}]
set_property PACKAGE_PIN P18 [get_ports {cmos1_d[4]}]
set_property PACKAGE_PIN N17 [get_ports {cmos1_d[5]}]
set_property PACKAGE_PIN U15 [get_ports {cmos1_d[1]}]
set_property PACKAGE_PIN U14 [get_ports {cmos1_d[0]}]
set_property PACKAGE_PIN P16 [get_ports {cmos1_vsync}]
set_property PACKAGE_PIN P15 [get_ports {cmos1_pclk}]

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