# ============================================================================
# p3b_tmds.xdc -- 阶段5（HDMI 显示链）/ S5-T01
#                 RunId s5_p3b_build_20261030_r01
# Design : top_p3b (BD s4d_p3b_wrapper + vendor rgb2dvi)  Part : xc7z020clg400-2
#
# !!! 声明式约束，禁止 if/foreach/proc/set !!!
# Vivado 2026.1 的 XDC 解析器不支持控制流，遇到时只发
# CRITICAL WARNING [Designutils 20-1307] 并静默跳过（约束等于没写）。
# 该陷阱在 P3a 的 v1 XDC 上实测发生并被修正，详见 P3A_BUILD_REPORT.md。
#
# 引脚与电平依据（厂商参考工程，未臆造）：
#   D:\FPGA\AX7Z020\AX7Z020\course_s1\course_s1\02_hdmi_out_test\
#     hdmi_out_test.srcs\constrs_1\new\hdmi_out_test.xdc  第 4-17 行
#       TMDS_clk_p      = U13   TMDS_33
#       TMDS_data_p[0]  = W14   TMDS_33
#       TMDS_data_p[1]  = Y18   TMDS_33
#       TMDS_data_p[2]  = Y16   TMDS_33
#       hdmi_oen        = V16   LVCMOS33
#   差分 N 端只设 IOSTANDARD、不设 PACKAGE_PIN（N 由 P 端推出）
# ============================================================================

# ---------------------------------------------------------------------------
# 1) 时钟域分组
#
#    P3b 的像素/串行时钟是 BD **内部网络**（pixel_clk / pixel_clk_5x 是 wrapper
#    的输出端口，不是芯片端口），因此没有可用 create_clock 的顶层端口，也不应
#    伪造主时钟。两者都由 clk_wiz_0 的同一个 MMCM 自动派生：
#        clk_out1_s4d_p3b_clk_wiz_0_0   13.4737 ns  (74.21875 MHz，像素)
#        clk_out2_s4d_p3b_clk_wiz_0_0    2.6945 ns  (371.09375 MHz = 5x，OSERDESE2 CLK)
#    二者必须在**同一组**内（OSERDESE2 依赖 1x/5x 固定相位关系），不能互为异步。
#    真实异步只发生在 50 MHz（clk_fpga_0，控制/数据面）与像素域之间。
#    实测确认见构建报告 §clocks（report_clocks 输出）。
# ---------------------------------------------------------------------------
set_clock_groups -asynchronous -group [get_clocks -include_generated_clocks clk_fpga_0] -group [get_clocks -include_generated_clocks clk_fpga_1] -group [get_clocks -include_generated_clocks clk_out*_s4d_p3b_clk_wiz_0_0]

# ---------------------------------------------------------------------------
# 2) TMDS 输出引脚（厂商 hdmi_out_test.xdc 第 4-15 行）
#    不额外声明 output delay：厂商参考同样没有，且无板级 Tco/Tsu 数据；
#    TMDS 通道时序由 OSERDESE2 + TMDS_33 差分标准保证（上板以 S6-A 上屏为准）。
# ---------------------------------------------------------------------------
set_property PACKAGE_PIN U13 [get_ports TMDS_clk_p]
set_property IOSTANDARD  TMDS_33 [get_ports TMDS_clk_p]
set_property IOSTANDARD  TMDS_33 [get_ports TMDS_clk_n]

set_property PACKAGE_PIN W14 [get_ports {TMDS_data_p[0]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_p[0]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_n[0]}]

set_property PACKAGE_PIN Y18 [get_ports {TMDS_data_p[1]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_p[1]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_n[1]}]

set_property PACKAGE_PIN Y16 [get_ports {TMDS_data_p[2]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_p[2]}]
set_property IOSTANDARD  TMDS_33 [get_ports {TMDS_data_n[2]}]

set_property PACKAGE_PIN V16 [get_ports hdmi_oen]
set_property IOSTANDARD  LVCMOS33 [get_ports hdmi_oen]

# ---------------------------------------------------------------------------
# 3) PS 固定引脚（DDR / FIXED_IO）由 PS7 IP 自带约束提供，此处不重复。
# ---------------------------------------------------------------------------