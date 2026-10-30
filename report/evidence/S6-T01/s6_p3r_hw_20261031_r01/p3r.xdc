# ============================================================================
# p3m.xdc —— 阶段5（HDMI 显示链）/ S5-T01 / P3r
# RunId s5_p3r_build_20261031_r01
#
# 引脚依据（全部实证）：
#   - sys_clk  = U18, 50 MHz, LVCMOS33          （板上 50 MHz 晶振，P3k 已用同脚出图）
#   - TMDS_*   = N18 / V20 / T20 / N20, TMDS_33  （ALINX demo hdmi_out.xdc，10-22 亮屏基线）
#   - hdmi_oen = V16, LVCMOS33                   （与 HDMI 无实际连接，驱动 1）
#
# 时钟：pixel_clk / pixel_clk_5x 是 RTL 内 MMCM 自动派生的**内部时钟**（不是芯片端口），
#       由 MMCME2_ADV 原语自动约束；这里只对输入 50 MHz 建主时钟。
#       BD 的 FCLK0(50 MHz) 由 PS7 IP 自带约束；其与像素域的 CDC 只有
#       ① VDMA 内部（IP 内，不暴露为可分析路径）② 本设计的格雷码同步器（已加 ASYNC_REG）。
#       所以本文件**不写 set_clock_groups**（用户 XDC 早于 IP/BD 时钟被读取，写了会 12-4739，
#       见 XDC_GUIDELINES.md），跨域安全由上述两点保证。
#
# !!! 声明式约束，禁止 if/foreach/proc/set !!!
# ============================================================================

# 1) 板载 50 MHz 输入
create_clock -period 20.000 -name sys_clk [get_ports sys_clk]
set_property PACKAGE_PIN U18 [get_ports sys_clk]
set_property IOSTANDARD  LVCMOS33 [get_ports sys_clk]

# 2) TMDS 差分输出（_n 只给 IOSTANDARD，球位由 P 端推断）
set_property PACKAGE_PIN N18 [get_ports TMDS_clk_p]
set_property IOSTANDARD  TMDS_33 [get_ports TMDS_clk_p]
set_property IOSTANDARD  TMDS_33 [get_ports TMDS_clk_n]

set_property PACKAGE_PIN V20 [get_ports {TMDS_data_p[0]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_p[0]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_n[0]}]

set_property PACKAGE_PIN T20 [get_ports {TMDS_data_p[1]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_p[1]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_n[1]}]

set_property PACKAGE_PIN N20 [get_ports {TMDS_data_p[2]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_p[2]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_n[2]}]

# 3) HDMI 使能脚（与 HDMI 无实际连接）
set_property PACKAGE_PIN V16 [get_ports hdmi_oen]
set_property IOSTANDARD  LVCMOS33 [get_ports hdmi_oen]
# ============================================================================
# P3r：AN5642 相机（J11 / CMOS2）引脚与 I/O 时序
#   引脚来源：阶段3 冻结约束 an5642_j11_cmos2.xdc
#             D:\codex-worktrees\dbdf\board\stage3\hardware\an5642_j11_cmos2.xdc
#             （其本身依据：官方 23_ov5640_dual 的 an5642.xdc + AX7020 V3.0 手册 Table 7.5.1 J11 针脚表）
#   连接器：J11（CMOS2 通道）；模块 pin3..18 对应 D9,SDA,D6,SCL,D7,D2,HREF,D8,D3,RESET,D4,D5,D1,D0,VSYNC,PCLK
# ============================================================================
set_property PACKAGE_PIN F17 [get_ports {cmos1_d[9]}]
set_property PACKAGE_PIN F20 [get_ports {cmos1_d[6]}]
set_property PACKAGE_PIN G20 [get_ports {cmos1_d[7]}]
set_property PACKAGE_PIN G19 [get_ports {cmos1_d[2]}]
set_property PACKAGE_PIN J18 [get_ports {cmos1_d[8]}]
set_property PACKAGE_PIN L20 [get_ports {cmos1_d[3]}]
set_property PACKAGE_PIN M20 [get_ports {cmos1_d[4]}]
set_property PACKAGE_PIN M19 [get_ports {cmos1_d[5]}]
set_property PACKAGE_PIN K18 [get_ports {cmos1_d[1]}]
set_property PACKAGE_PIN K17 [get_ports {cmos1_d[0]}]
set_property PACKAGE_PIN H18 [get_ports cmos1_href]
set_property PACKAGE_PIN J19 [get_ports cmos1_vsync]
set_property PACKAGE_PIN K19 [get_ports cmos1_pclk]
set_property PACKAGE_PIN F16 [get_ports cmos1_i2c_sda_io]
set_property PACKAGE_PIN F19 [get_ports cmos1_i2c_scl_io]
set_property PACKAGE_PIN L19 [get_ports cmos_rstn]

set_property IOSTANDARD LVCMOS33 [get_ports {cmos1_d[*]}]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_href]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_vsync]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_pclk]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_i2c_sda_io]
set_property IOSTANDARD LVCMOS33 [get_ports cmos1_i2c_scl_io]
set_property IOSTANDARD LVCMOS33 [get_ports cmos_rstn]

set_property PULLUP true [get_ports cmos1_i2c_scl_io]
set_property PULLUP true [get_ports cmos1_i2c_sda_io]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets cmos1_pclk_IBUF]

# ---- PCLK 与 DVP 输入 I/O 时序（R-02-3 §2.2 草案的正式落地）----
# PCLK 周期：OV5640 DVP PCLK 上限 96 MHz ⇒ 按最紧 10.417 ns 约束（实际频率由软件配置决定，必然 <= 96 MHz）
create_clock -period 10.417 -name cam_pclk [get_ports cmos1_pclk]
# DVP 数据/同步相对 PCLK 的输入延迟：
#   ⚠ 数值为**保守占位**，来源待补（OV5640 数据手册 AC Characteristics 的 DVP tSU/tH 表）。
#   现值按"数据在 PCLK 上升沿后 <= 2.5 ns 稳定、保持 >= 1.5 ns"的假定给出；
#   R-02-3 §2.2 要求 V4 以手册页码 + 板级走线延迟核对后签核，本版不声称已签核。
set_input_delay -clock cam_pclk -max 2.500 [get_ports {cmos1_d[*]}]
set_input_delay -clock cam_pclk -max 2.500 [get_ports cmos1_href]
set_input_delay -clock cam_pclk -max 2.500 [get_ports cmos1_vsync]
set_input_delay -clock cam_pclk -min 1.500 [get_ports {cmos1_d[*]}]
set_input_delay -clock cam_pclk -min 1.500 [get_ports cmos1_href]
set_input_delay -clock cam_pclk -min 1.500 [get_ports cmos1_vsync]
