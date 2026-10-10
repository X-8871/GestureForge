# 第一轮真实验证已完成；本脚本补齐剩余只读断言。
set work C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/tmp/2B/S2B-T08/review_ip_20261010_r01
proc require_equal {label actual expected} {
    if {$actual ne $expected} {error "$label actual=$actual expected=$expected"}
    puts "REVIEW_ASSERT:$label=$actual"
}
proc same_net {a b} {
    require_equal "$a==$b" [get_bd_nets -of_objects [get_bd_pins $a]] [get_bd_nets -of_objects [get_bd_pins $b]]
}
open_project [file join $work project/review_ip.xpr]
open_bd_design [file join $work project/review_ip.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
require_equal csr_range [get_property RANGE [get_bd_addr_segs ps7/Data/SEG_M_AXI_0_Reg]] 0x00010000
require_equal hp_offset [get_property OFFSET [get_bd_addr_segs S_AXI_HP0_0/SEG_ps7_HP0_DDR_LOWOCM]] 0x00000000
require_equal hp_range [get_property RANGE [get_bd_addr_segs S_AXI_HP0_0/SEG_ps7_HP0_DDR_LOWOCM]] 0x40000000
foreach pin {ps7/M_AXI_GP0_ACLK ps7/S_AXI_HP0_ACLK axi_gp0_lite/aclk rst_fclk0/slowest_sync_clk} {same_net ps7/FCLK_CLK0 $pin}
same_net ps7/FCLK_RESET0_N rst_fclk0/ext_reset_in
same_net rst_fclk0/peripheral_aresetn axi_gp0_lite/aresetn
same_net const_zero/dout rst_fclk0/aux_reset_in
same_net const_zero/dout rst_fclk0/mb_debug_sys_rst
same_net const_one/dout rst_fclk0/dcm_locked
require_equal ext_reset_active_low [get_property CONFIG.C_EXT_RESET_HIGH [get_bd_cells rst_fclk0]] 0
require_equal const_zero [get_property CONFIG.CONST_VAL [get_bd_cells const_zero]] 0
require_equal const_one [get_property CONFIG.CONST_VAL [get_bd_cells const_one]] 1
puts "REVIEW_REMAINDER:PASS"
close_project
exit 0
