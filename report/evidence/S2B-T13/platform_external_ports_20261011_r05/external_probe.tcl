# 只读桩验证make_bd_intf_pins_external返回空值，所有对象均为隔离模拟。
source {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/vivado/s2b_inference_platform.tcl}
set mode valid
set ports {}
set net_ports {}
set make_count 0
set rename_count 0
set failures 0
proc get_bd_intf_pins {path} {
    if {$::mode eq "missing_pin"} {return {}}
    return /$path
}
proc get_bd_intf_ports {args} {
    if {![llength $args]} {return $::ports}
    return [dict get $::net_ports [lindex $args end]]
}
proc make_bd_intf_pins_external {pin} {
    incr ::make_count
    set net NET:$pin
    if {$::mode eq "missing_endpoint"} {
        dict set ::net_ports $net {}
    } elseif {$::mode eq "multiple_endpoint"} {
        dict set ::net_ports $net {/random_endpoint_a /random_endpoint_b}
        lappend ::ports /random_endpoint_a /random_endpoint_b
    } elseif {$::mode eq "old_endpoint"} {
        dict set ::net_ports $net {/old_endpoint}
    } else {
        set port /unpredictable_created_$::make_count
        dict set ::net_ports $net [list $port]
        lappend ::ports $port
    }
    return ""
}
proc get_bd_intf_nets {args} {
    if {$::mode eq "missing_net"} {return {}}
    if {$::mode eq "multiple_net"} {return {net_a net_b}}
    return NET:[lindex $args end]
}
proc set_property {property name object} {
    if {$object eq "" || [llength $object] != 1} {error MOCK_COMMON_17_161}
    incr ::rename_count
    set index [lsearch -exact $::ports $object]
    if {$index < 0} {error WRONG_ENDPOINT_OBJECT}
    set ::ports [lreplace $::ports $index $index /$name]
    dict for {net endpoints} $::net_ports {
        if {$endpoints eq [list $object]} {dict set ::net_ports $net [list /$name]}
    }
}
foreach case {missing_pin missing_net multiple_net missing_endpoint multiple_endpoint old_endpoint} {
    set mode $case
    set ports {}
    if {$mode eq "old_endpoint"} {set ports {/old_endpoint}}
    set net_ports {}
    set make_count 0
    set rename_count 0
    set code [catch {::s2b_inference_platform::externalize_unique ps7/DDR DDR} result]
    set ok [expr {$code == 1 && $rename_count == 0 && [string match {EXTERNAL_*_FAIL:*} $result]}]
    puts "CASE:$case PASS:$ok CODE:$code MAKE:$make_count RENAME:$rename_count MESSAGE:$result"
    if {!$ok} {incr failures}
}
set mode valid
set ports {}
set net_ports {}
set make_count 0
set rename_count 0
set code [catch {
    set ddr [::s2b_inference_platform::externalize_unique ps7/DDR DDR]
    set fixed [::s2b_inference_platform::externalize_unique ps7/FIXED_IO FIXED_IO]
} result]
set ok [expr {$code == 0 && $ddr eq "/DDR" && $fixed eq "/FIXED_IO" && $make_count == 2 && $rename_count == 2}]
puts "CASE:void_return_valid_two_interfaces PASS:$ok CODE:$code MAKE:$make_count RENAME:$rename_count PORTS:$ports"
if {!$ok} {incr failures}
proc get_property {property object} {return $::associated_busif}
set associated_busif S_AXI
set code [catch {::s2b_inference_platform::assert_property infer/clk CONFIG.ASSOCIATED_BUSIF S_AXI:M_AXI} message]
set ok [expr {$code == 1 && [string match PLATFORM_AUDIT_FAIL:* $message]}]
puts "CASE:missing_master_clock_association PASS:$ok CODE:$code"
if {!$ok} {incr failures}
set associated_busif S_AXI:M_AXI
set code [catch {::s2b_inference_platform::assert_property infer/clk CONFIG.ASSOCIATED_BUSIF S_AXI:M_AXI} message]
set ok [expr {$code == 0}]
puts "CASE:both_clock_associations PASS:$ok CODE:$code"
if {!$ok} {incr failures}
puts "EXTERNAL_CASES_FAILURES:$failures"
exit [expr {$failures ? 1 : 0}]
