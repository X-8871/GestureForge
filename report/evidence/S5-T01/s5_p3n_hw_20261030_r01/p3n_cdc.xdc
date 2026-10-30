# ============================================================================
# p3n_cdc.xdc —— P3n 的跨时钟域时序约束（**只约束 CDC，不掩盖真实路径**）
#
# 背景：RTL 里 underflow 计数从像素域(clk_pixel_raw, 74.21875 MHz) 送到
#       50 MHz 域(clk_fpga_0) 用的是 **格雷码 + 3 级同步器**（top_p3m.v）。
#       格雷码每次只有 1 bit 变化，本身是安全的 CDC；但 Vivado 默认把
#       "未显式排除的跨时钟路径"当同步路径分析（报告原文：
#       "Inter clock paths are considered valid unless explicitly excluded ...
#        such as set_clock_groups or set_false_path"），
#       于是给出 0.211 ns 的假性 requirement，产生 32 个假性失败端点
#       （32 = 计数器的位宽），原始 WNS = -5.503 ns。
#
# 正确做法：对**这一条 CDC 数据通路**加 set_max_delay -datapath_only
#       （标准 CDC 约束：只限制物理绕线延迟，不要求满足同步建立关系）。
#
# 为什么用 cell 过滤而不是 get_clocks：
#       用户 XDC 早于 IP/BD 时钟约束被读取，`get_clocks` 会取到空集合
#       （[Vivado 12-4739]，P3b/P3c 已实测，见 XDC_GUIDELINES.md）。
#       用 get_cells 过滤**不依赖时钟对象**，因此不受该问题影响。
#
# 影响面：只匹配 u_atv 内 uf_pixels 寄存器 与 顶层的 uf_g_s1 寄存器，
#         不涉及任何其它路径（不动像素域、不动 VDMA、不动 TMDS 输出）。
# ============================================================================

# 第一跳：像素域计数寄存器 -> 50 MHz 域第一级同步器（格雷码，允许异步，但要限制绕线）
set_max_delay -datapath_only \
    -from [get_cells -hier -filter {NAME =~ *uf_pixels_reg[*]}] \
    -to   [get_cells -hier -filter {NAME =~ *uf_g_s1_reg[*]}] \
    13.474

# 第二跳：同步器一级 -> 二级（同为 clk_fpga_0，正常同步路径，这里只限制最大延迟以防长绕线）
set_max_delay -datapath_only \
    -from [get_cells -hier -filter {NAME =~ *uf_g_s1_reg[*]}] \
    -to   [get_cells -hier -filter {NAME =~ *uf_g_s2_reg[*]}] \
    20.000