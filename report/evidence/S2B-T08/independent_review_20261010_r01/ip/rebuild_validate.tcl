# 独立审查只在隔离目录创建工程，原证据只读。
set root C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition
set work [file join $root tmp/2B/S2B-T08/review_ip_20261010_r01]
proc require_equal {label actual expected} {
    if {$actual ne $expected} {error "$label actual=$actual expected=$expected"}
    puts "REVIEW_ASSERT:$label=$actual"
}
proc same_net {a b} {
    require_equal "$a==$b" [get_bd_nets -of_objects [get_bd_pins $a]] [get_bd_nets -of_objects [get_bd_pins $b]]
}
create_project review_ip [file join $work project] -part xc7z020clg400-2
set before [get_msg_config -count -severity WARNING]
puts "REVIEW_SOURCE_VALIDATE_BEGIN warning_count=$before"
source [file join $root report/evidence/S2B-T08/ip_probe_20261009_r01/validated_probe_bd.tcl]
puts "REVIEW_SOURCE_VALIDATE_END warning_count=[get_msg_config -count -severity WARNING]"
# 强制重新运行验证，避免已验证状态跳过。
puts "REVIEW_FORCE_VALIDATE_BEGIN"
validate_bd_design -force
puts "REVIEW_FORCE_VALIDATE_END warning_count=[get_msg_config -count -severity WARNING] critical_count=[get_msg_config -count -severity {CRITICAL WARNING}] error_count=[get_msg_config -count -severity ERROR]"
require_equal part [get_property PART [current_project]] xc7z020clg400-2
foreach {pin protocol width id} {ps7/M_AXI_GP0 AXI3 32 12 ps7/S_AXI_HP0 AXI3 64 6 axi_gp0_lite/S_AXI AXI3 32 12 axi_gp0_lite/M_AXI AXI4LITE 32 0} {
    set p [get_bd_intf_pins $pin]
    require_equal "$pin.protocol" [get_property CONFIG.PROTOCOL $p] $protocol
    require_equal "$pin.width" [get_property CONFIG.DATA_WIDTH $p] $width
    require_equal "$pin.id" [get_property CONFIG.ID_WIDTH $p] $id
    require_equal "$pin.freq" [get_property CONFIG.FREQ_HZ $p] 50000000
}
require_equal csr_offset [get_property OFFSET [get_bd_addr_segs ps7/Data/SEG_M_AXI_0_Reg]] 0x43C00000
require_equal csr_range [get_property RANGE [get_bd_addr_segs ps7/Data/SEG_M_AXI_0_Reg]] 64K
require_equal hp_offset [get_property OFFSET [get_bd_addr_segs S_AXI_HP0_0/SEG_ps7_HP0_DDR_LOWOCM]] 0x00000000
require_equal hp_range [get_property RANGE [get_bd_addr_segs S_AXI_HP0_0/SEG_ps7_HP0_DDR_LOWOCM]] 1G
foreach pin {ps7/M_AXI_GP0_ACLK ps7/S_AXI_HP0_ACLK axi_gp0_lite/aclk rst_fclk0/slowest_sync_clk} {same_net ps7/FCLK_CLK0 $pin}
same_net ps7/FCLK_RESET0_N rst_fclk0/ext_reset_in
same_net rst_fclk0/peripheral_aresetn axi_gp0_lite/aresetn
same_net const_zero/dout rst_fclk0/aux_reset_in
same_net const_zero/dout rst_fclk0/mb_debug_sys_rst
same_net const_one/dout rst_fclk0/dcm_locked
require_equal ext_reset_active_low [get_property CONFIG.C_EXT_RESET_HIGH [get_bd_cells rst_fclk0]] 0
require_equal const_zero [get_property CONFIG.CONST_VAL [get_bd_cells const_zero]] 0
require_equal const_one [get_property CONFIG.CONST_VAL [get_bd_cells const_one]] 1
require_equal critical_count [get_msg_config -count -severity {CRITICAL WARNING}] 0
require_equal error_count [get_msg_config -count -severity ERROR] 0
save_bd_design
puts "REVIEW_REBUILD:PASS"
close_project
exit 0
