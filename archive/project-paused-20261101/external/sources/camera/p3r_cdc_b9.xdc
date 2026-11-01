# ============================================================================
# p3r_cdc_b9.xdc -- build9 新增：cam_pclk 域输入计数器 -> clk_fpga_1(100 MHz) 域格雷码同步
#
# 结构：cam_pclk 域二进制计数器(pclk_cnt/href_cnt/vsync_r_cnt/vsync_f_cnt)
#        -> 格雷码(b2g) -> clk_fpga_1 域两级同步(*_g1_reg -> *_g2_reg) -> 还原二进制
# 格雷码每次只变 1 位，是标准多 bit CDC；两时钟异步，必须用 -datapath_only
# （只约束物理绕线延迟，不要求同步建立关系），否则 Vivado 会按最近边沿给出
# 0.097 ns 的假性 requirement（build9 实测 WNS -5.161，全部失败路径都在这里）。
# 用 get_cells 过滤而非 get_clocks：用户 XDC 早于 BD 时钟约束被读取（[Vivado 12-4739]）。
# 影响面：只匹配这 8 组寄存器，不掩盖任何真实同步路径。
# ============================================================================

set_max_delay -datapath_only 10.000 \
    -from [get_cells -hier -filter {NAME =~ *pclk_cnt_reg[*] || NAME =~ *href_cnt_reg[*] || NAME =~ *vsync_r_cnt_reg[*] || NAME =~ *vsync_f_cnt_reg[*]}] \
    -to   [get_cells -hier -filter {NAME =~ *pclk_g1_reg[*] || NAME =~ *href_g1_reg[*] || NAME =~ *vr_g1_reg[*] || NAME =~ *vf_g1_reg[*]}]

set_max_delay -datapath_only 10.000 \
    -from [get_cells -hier -filter {NAME =~ *pclk_g1_reg[*] || NAME =~ *href_g1_reg[*] || NAME =~ *vr_g1_reg[*] || NAME =~ *vf_g1_reg[*]}] \
    -to   [get_cells -hier -filter {NAME =~ *pclk_g2_reg[*] || NAME =~ *href_g2_reg[*] || NAME =~ *vr_g2_reg[*] || NAME =~ *vf_g2_reg[*]}]
