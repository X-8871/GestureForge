# ============================================================================
# p3g_tmds.xdc -- 阶段5（HDMI 显示链）/ S5-T01
#                 RunId s5_p3g_build_20261030_r01
# Design : top_p3g (BD s4d_p3g_wrapper + vendor rgb2dvi)  Part : xc7z020clg400-2
#
# !!! 声明式约束，禁止 if/foreach/proc/set !!!
# Vivado 2026.1 的 XDC 解析器不支持控制流，遇到时只发
# CRITICAL WARNING [Designutils 20-1307] 并静默跳过（约束等于没写）。
#
# ============================================================================
# ★ P3g 相对 P3b 的**唯一改动 = 4 个 TMDS PACKAGE_PIN**（勘误修正）
#
#   勘误：P3a/P3b/P3c/P3d/P3e/P3f 的 TMDS 引脚取自
#         D:\FPGA\AX7Z020\AX7Z020\course_s1\course_s1\02_hdmi_out_test\...\hdmi_out_test.xdc
#         的 U13 / W14 / Y18 / Y16 —— **与本实板不符**（该套属于另一工程/板型，很可能是 HDMI IN
#         或另一版底板），导致上屏无信号。已由"10-22 亮屏基线"实证推翻。
#
#   本版改用 ALINX 官方 demo 的 XDC（该套设计 2026-10-22 实拍有画面、今日 12:24 实测出灰度条）：
#     D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r02\
#       vendor_src\src\constraints\hdmi_out.xdc        （sha256 71EDC780…，与 r01 副本逐字节一致）
#
#   | 信号            | 10-22 亮屏设计（实证） | 本版 P3g | 旧（错）P3b |
#   |-----------------|----------------------|----------|-------------|
#   | TMDS_clk_p      | N18                  | **N18**  | U13         |
#   | TMDS_data_p[0]  | V20                  | **V20**  | W14         |
#   | TMDS_data_p[1]  | T20                  | **T20**  | Y18         |
#   | TMDS_data_p[2]  | N20                  | **N20**  | Y16         |
#   | hdmi_oen        | V16  LVCMOS33        | V16      | V16（不变） |
#
#   差分 N 端仍只设 IOSTANDARD、不设 PACKAGE_PIN（N 由 P 端推断）。
#   `hdmi_oen`/V16 经图纸(p2/p12/p13)与手册(p35–37)确认**与 HDMI 无实际连接**，保持原样。
# ============================================================================

# ---------------------------------------------------------------------------
# 1) 时钟域分组（与 P3b 完全相同）
#
#    像素/串行时钟是 BD **内部网络**（pixel_clk / pixel_clk_5x 是 wrapper 的输出端口，
#    不是芯片端口），因此没有可用 create_clock 的顶层端口，也不应伪造主时钟。
#    两者都由 clk_wiz_0 的同一个 MMCM 自动派生：
#        clk_out1_s4d_p3g_clk_wiz_0_0   13.4737 ns  (74.21875 MHz，像素)
#        clk_out2_s4d_p3g_clk_wiz_0_0    2.6945 ns  (371.09375 MHz = 5x，OSERDESE2 CLK)
#    二者必须在**同一组**内（OSERDESE2 依赖 1x/5x 固定相位关系），不能互为异步。
#    真实异步只发生在 50 MHz（clk_fpga_0，控制/数据面）与像素域之间。
# ---------------------------------------------------------------------------
set_clock_groups -asynchronous -group [get_clocks -include_generated_clocks clk_fpga_0] -group [get_clocks -include_generated_clocks clk_fpga_1] -group [get_clocks -include_generated_clocks clk_out*_s4d_p3g_clk_wiz_0_0]

# ---------------------------------------------------------------------------
# 2) TMDS 输出引脚（ALINX 官方 demo hdmi_out.xdc，10-22 亮屏基线实证）
#    不额外声明 output delay：官方 demo 同样没有，且无板级 Tco/Tsu 数据；
#    TMDS 通道时序由 OSERDESE2 + TMDS_33 差分标准保证（上板以 S6-A 上屏为准）。
# ---------------------------------------------------------------------------
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

set_property PACKAGE_PIN V16 [get_ports hdmi_oen]
set_property IOSTANDARD  LVCMOS33 [get_ports hdmi_oen]

# ---------------------------------------------------------------------------
# 3) PS 固定引脚（DDR / FIXED_IO）由 PS7 IP 自带约束提供，此处不重复。
# ---------------------------------------------------------------------------