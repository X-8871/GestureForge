# ============================================================================
# p3q_cdc.xdc -- P3q 的跨时钟域时序约束（只约束 CDC，不掩盖真实路径）
#
# 背景：P3q 有 3 处 "像素域(74.21875 MHz) -> 50 MHz 域" 的跨域，全部是安全 CDC 结构：
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