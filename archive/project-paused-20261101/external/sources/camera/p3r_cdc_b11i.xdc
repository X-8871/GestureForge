# ============================================================================
# p3r_cdc_b11i.xdc -- build11i 新增跨域同步器的 set_max_delay 约束
# 背景：build11i WNS -5.284，全部 11 条违规都在新加的 CDC 上：
#   10 条  vsf_g1_reg[*] （cam_pclk 域 vsf_r 格雷码 -> clk_50 两级同步）
#    1 条  sof_t1_reg/D  （cam_pclk 域 sof_tgl 翻转 -> clk_100 两级同步）
# 这些是异步跨域路径，Vivado 会按 cam_pclk(10.417ns) 给 0.097ns 级假性 requirement；
# 沿用 p3r_cdc_b9.xdc 的写法：-datapath_only 只约束物理延迟，不建立同步关系。
# 影响面：仅匹配 build11i 新增的 2 组同步器，不掩盖真实同步路径。
# ============================================================================

# 1) cam_pclk -> clk_50：vsync 下降沿计数（vsf_r 格雷码 -> vsf_g1 -> vsf_g2）
set_max_delay -datapath_only 10.000 \
    -from [get_cells -hier -filter {NAME =~ *vsf_r_reg[*]}] \
    -to   [get_cells -hier -filter {NAME =~ *vsf_g1_reg[*]}]
set_max_delay -datapath_only 10.000 \
    -from [get_cells -hier -filter {NAME =~ *vsf_g1_reg[*]}] \
    -to   [get_cells -hier -filter {NAME =~ *vsf_g2_reg[*]}]

# 2) cam_pclk -> clk_100：SOF 翻转同步（sof_tgl -> sof_t1 -> sof_t2）
set_max_delay -datapath_only 10.000 \
    -from [get_cells -hier -filter {NAME =~ *sof_tgl_reg}] \
    -to   [get_cells -hier -filter {NAME =~ *sof_t1_reg}]
set_max_delay -datapath_only 10.000 \
    -from [get_cells -hier -filter {NAME =~ *sof_t1_reg}] \
    -to   [get_cells -hier -filter {NAME =~ *sof_t2_reg}]
