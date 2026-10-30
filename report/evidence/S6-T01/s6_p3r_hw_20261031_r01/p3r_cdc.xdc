# ============================================================================
# p3r_cdc.xdc -- P3r 的跨时钟域时序约束（只约束 CDC，不掩盖真实路径）
#
# 背景：P3r 有 3 处 "像素域(74.21875 MHz) -> 50 MHz 域" 的跨域，全部是安全 CDC 结构：
#   1) uf_pixels      累计欠载像素数（单调递增）-> 格雷码 + 3 级同步
#   2) tlast_misalign tlast 位置异常计数（单调递增）-> 格雷码 + 3 级同步
#   3) vs             场同步（单比特慢变，高电平约 5 行 ~111 us）-> 2 级同步
# Vivado 默认把未显式排除的跨时钟路径当同步路径分析，会给出 0.2ns 量级假性 requirement，
# 产生成片假性违例。正确做法：对这几条数据通路加 set_max_delay -datapath_only
# （Xilinx 推荐的标准 CDC 约束：只限制物理绕线延迟，不要求满足同步建立关系）。
#
# 为什么用 get_cells 过滤而不是 get_clocks：
#   用户 XDC 早于 IP/BD 时钟约束被读取，get_clocks 会取到空集合（[Vivado 12-4739]，
#   P3b/P3c 已实测，见 XDC_GUIDELINES.md）。get_cells 不依赖时钟对象，避开该问题。
#
# 影响面：只匹配下列几组寄存器，不动像素域 / VDMA / TMDS 输出任何其它路径。
# ============================================================================

# 1) 累计欠载像素数：像素域计数器 -> 50 MHz 域第 1 级同步器
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *uf_pixels_reg[*]}] -to [get_cells -hier -filter {NAME =~ *uf_g_s1_reg[*]}] 13.474
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *uf_g_s1_reg[*]}]    -to [get_cells -hier -filter {NAME =~ *uf_g_s2_reg[*]}] 20.000

# 2) tlast 异常计数：同上
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *tlast_misalign_reg[*]}] -to [get_cells -hier -filter {NAME =~ *mis_g_s1_reg[*]}] 13.474
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *mis_g_s1_reg[*]}]      -to [get_cells -hier -filter {NAME =~ *mis_g_s2_reg[*]}] 20.000

# 3) vsync 单比特：像素域 vs 寄存器 -> 50 MHz 域第 1 级同步器
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *u_atv*vs_r_reg*}] -to [get_cells -hier -filter {NAME =~ *vs_meta_reg*}] 20.000
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *vs_meta_reg*}]    -to [get_cells -hier -filter {NAME =~ *vs_sync_reg*}] 20.000
# ---------------------------------------------------------------------------
# P3r：厂商 alinx_ov5640 IP **内部** PCLK -> AXIS 时钟域的慢变标志同步器
#   失效路径（P3r r01 实测，唯一 1 个失败端点）：
#     u_bd/s4d_p3r_i/alinx_ov5640_0/inst/fifo_ready_reg_replica/C  (cam_pclk)
#   ->u_bd/s4d_p3r_i/alinx_ov5640_0/inst/fifo_ready_maxis_reg/D    (clk_fpga_1)
#   requirement 仅 0.097 ns（两异步时钟最近边沿关系），数据路径 1.411 ns
#   —— 与 P3m/P3p 同类：异步跨域被当同步分析。该寄存器在厂商源码里已标
#   (* ASYNC_REG="true" *)，属标准单比特同步结构。
#   用 cell 过滤（避 12-4739）+ -datapath_only（只限物理绕线，不要求同步建立关系）。
# ---------------------------------------------------------------------------
set_max_delay -datapath_only -from [get_cells -hier -filter {NAME =~ *alinx_ov5640_0*fifo_ready_reg*}] -to [get_cells -hier -filter {NAME =~ *alinx_ov5640_0*fifo_ready_maxis_reg*}] 10.417
