# ============================================================================
# p3m.xdc —— 阶段5（HDMI 显示链）/ S5-T01 / P3q
# RunId s5_p3q_build_20261030_r01
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