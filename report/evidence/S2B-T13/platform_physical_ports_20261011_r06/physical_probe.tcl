# 隔离桩覆盖两个外接口的实际成员集合，不调用任何 Vivado 命令。
source {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/vivado/s2b_inference_platform.tcl}
set failures 0
set original_members [dict create /DDR {} /FIXED_IO {}]
for {set i 0} {$i < 15} {incr i} {dict lappend original_members /DDR /DDR_member_$i}
for {set i 0} {$i < 6} {incr i} {dict lappend original_members /FIXED_IO /FIXED_IO_member_$i}
proc get_bd_intf_ports {} {return $::interfaces}
proc get_bd_ports {args} {
    if {![llength $args]} {return $::actual}
    if {[lindex $args 0] ne "-of_objects"} {error MOCK_BAD_QUERY}
    return [dict get $::members [lindex $args 1]]
}
foreach mode {valid valid_reordered extra_scalar missing_scalar empty_members extra_interface missing_interface duplicate_interface} {
    set interfaces {/DDR /FIXED_IO}
    set members $original_members
    set actual [concat [dict get $members /DDR] [dict get $members /FIXED_IO]]
    switch $mode {
        valid_reordered {set interfaces [lreverse $interfaces]; set actual [lreverse $actual]}
        extra_scalar {lappend actual /unexpected_gpio}
        missing_scalar {set actual [lrange $actual 1 end]}
        empty_members {dict set members /DDR {}}
        extra_interface {lappend interfaces /OTHER; dict set members /OTHER {/unexpected_gpio}; lappend actual /unexpected_gpio}
        missing_interface {set interfaces {/DDR}; set actual [dict get $members /DDR]}
        duplicate_interface {lappend interfaces /DDR}
    }
    set code [catch {::s2b_inference_platform::physical_port_members} result]
    if {$mode in {valid valid_reordered}} {
        set ok [expr {$code == 0 && [llength [dict get $result scalar_ports]] == 21 && [llength [dict get $result members DDR]] == 15 && [llength [dict get $result members FIXED_IO]] == 6}]
    } else {
        set ok [expr {$code == 1 && [string match {PHYSICAL_*FAIL:*} $result] || $code == 1 && [string match {PHYSICAL_INTERFACE_MEMBERS_EMPTY:*} $result]}]
    }
    puts "CASE:$mode PASS:$ok CODE:$code RESULT:$result"
    if {!$ok} {incr failures}
}
proc get_bd_cells {} {return {/ps7 /infer /gp0_lite /rst_fclk0 /constant_zero /constant_one}}
proc get_bd_intf_pins {args} {
    if {![llength $args]} {return {}}
    if {$args ne [list -of_objects [get_bd_cells]]} {error MOCK_BAD_CELL_ENUMERATION}
    return {/ps7/DDR /ps7/FIXED_IO /ps7/M_AXI_GP0 /ps7/S_AXI_HP0 /gp0_lite/S_AXI /gp0_lite/M_AXI /infer/S_AXI /infer/M_AXI /rst_fclk0/unused_mock}
}
set seen {}
foreach pin [get_bd_intf_pins -of_objects [get_bd_cells]] {lappend seen $pin}
set ok [expr {[llength $seen] == 9 && [llength [get_bd_intf_pins]] == 0}]
puts "CASE:all_cells_interface_enumeration PASS:$ok COUNT:[llength $seen] DEFAULT_COUNT:[llength [get_bd_intf_pins]]"
if {!$ok} {incr failures}
puts "PHYSICAL_CASES_FAILURES:$failures"
exit [expr {$failures ? 1 : 0}]
