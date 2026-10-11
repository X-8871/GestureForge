# API 桩只模拟对象关系和命令副作用，不调用 Vivado。
source {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/vivado/s2b_inference_platform.tcl}
set failures 0
set property_calls 0
set saved_readback {}
set interfaces {/DDR /FIXED_IO}
set members [dict create /DDR {} /FIXED_IO {}]
for {set i 0} {$i < 15} {incr i} {dict lappend members /DDR /DDR_member_$i}
for {set i 0} {$i < 6} {incr i} {dict lappend members /FIXED_IO /FIXED_IO_member_$i}
set cells {/ps7 /axi_gp0_lite /rst_fclk0 /const_zero /const_one /infer}
set buspins {/ps7/M_AXI_GP0 /axi_gp0_lite/S_AXI /axi_gp0_lite/M_AXI /infer/S_AXI /infer/M_AXI /ps7/S_AXI_HP0 /ps7/DDR /ps7/FIXED_IO /mock_intf}
proc get_bd_cells {} {return $::cells}
proc get_bd_intf_ports {} {return $::interfaces}
proc get_bd_ports {args} {
    if {![llength $args]} {return [concat [dict get $::members /DDR] [dict get $::members /FIXED_IO]]}
    return [dict get $::members [lindex $args end]]
}
proc current_project {args} {return PROJECT}
proc get_parts {part} {return $part}
proc get_bd_intf_pins {args} {
    if {[lindex $args 0] ne "-of_objects"} {return /[lindex $args 0]}
    if {[lindex $args 1] eq "HP_NET"} {return {/infer/M_AXI /ps7/S_AXI_HP0}}
    if {[lindex $args 1] eq $::cells} {return $::buspins}
    error MOCK_UNKNOWN_INTERFACE_QUERY
}
proc get_bd_intf_nets {args} {return HP_NET}
proc get_bd_pins {args} {
    if {[lindex $args 0] eq "-of_objects"} {return {/mock_scalar_a /mock_scalar_b}}
    return /[lindex $args 0]
}
proc get_bd_nets {args} {
    if {![llength $args]} {return {CLOCK_NET RESET_NET}}
    if {[lindex $args end] in {/rst_fclk0/peripheral_aresetn /axi_gp0_lite/aresetn /infer/cold_resetn}} {return RESET_NET}
    return CLOCK_NET
}
proc get_bd_addr_spaces {args} {return /ps7/Data}
proc get_bd_addr_segs {args} {return CONTROL_SEG}
proc version {args} {return MOCK_NOT_VIVADO}
proc list_property {object} {
    incr ::property_calls
    if {$object eq "xc7z020clg400-2"} {return {SPEED TEMPERATURE_GRADE}}
    return {MODE CONFIG.PROTOCOL CONFIG.ADDR_WIDTH CONFIG.DATA_WIDTH CONFIG.ID_WIDTH TYPE DIR CONFIG.FREQ_HZ CONFIG.ASSOCIATED_BUSIF CONFIG.ASSOCIATED_RESET CONFIG.POLARITY}
}
proc get_property {property object} {
    switch $property {
        PART {return xc7z020clg400-2}
        CONFIG.PROTOCOL {if {$object in {/axi_gp0_lite/M_AXI /infer/S_AXI}} {return AXI4LITE}; return AXI3}
        CONFIG.ADDR_WIDTH {return 32}
        CONFIG.DATA_WIDTH {if {$object in {/infer/M_AXI /ps7/S_AXI_HP0}} {return 64}; return 32}
        CONFIG.ID_WIDTH {if {$object in {/infer/M_AXI /ps7/S_AXI_HP0}} {return 6}; return 12}
        CONFIG.FREQ_HZ {return 50000000}
        CONFIG.ASSOCIATED_BUSIF {return S_AXI:M_AXI}
        OFFSET {return 0x43C00000}
        RANGE {return 0x00010000}
        NAME {return $::bd_path}
        default {return MOCK}
    }
}
namespace eval ipcfg {}
proc ipcfg::write_evidence {path data} {set ::saved_readback $data}
set code [catch {::s2b_inference_platform::audit MOCK 0} result]
set ok [expr {$code == 0 && $result eq "AUDIT:OK" && $property_calls == 14 && [dict size [dict get $saved_readback interfaces]] == 9 && [dict size [dict get $saved_readback scalar_pins]] == 4}]
puts "CASE:full_audit_official_list_property PASS:$ok CODE:$code CALLS:$property_calls RESULT:$result"
if {!$ok} {incr failures}
rename list_property official_list_property
set code [catch {::s2b_inference_platform::audit MOCK 0} result]
set ok [expr {$code == 1 && [string match {invalid command name "list_property"} $result]}]
puts "CASE:missing_official_API_rejected PASS:$ok CODE:$code RESULT:$result"
if {!$ok} {incr failures}
rename official_list_property list_property
# products 使用隔离缓存内的伪 BD，只核验调用序列与对象来源。
set base [lindex $argv 0]
set bd_path [file join $base mock.bd]
set f [open $bd_path w]; puts $f MOCK_BD; close $f
set imported 0
proc get_files {pattern} {
    if {[string match *_wrapper.v $pattern]} {
        if {!$::imported || $::mode eq "missing_wrapper"} {return {}}
        if {$::mode eq "multiple_wrapper"} {return {/mock_a_wrapper.v /mock_b_wrapper.v}}
        return /mock_imported_wrapper.v
    }
    if {$::mode eq "missing_bd"} {return {}}
    if {$::mode eq "multiple_bd"} {return {/mock_a.bd /mock_b.bd}}
    return $::bd_path
}
proc generate_target {target object} {incr ::generate_count; return ""}
proc make_wrapper {args} {
    if {$args ne [list -files $::bd_path -top -import]} {error MOCK_WRAPPER_OPTIONS_FAIL}
    incr ::make_count
    set ::imported 1
    if {$::mode eq "valid_info_return"} {return {arbitrary creation information}}
    return ""
}
proc current_fileset {} {return SOURCES_1}
proc set_property {property value object} {incr ::top_count; return ""}
proc update_compile_order {args} {return ""}
proc write_bd_tcl {path} {set f [open $path w]; puts $f MOCK_BD_TCL; close $f; return ""}
proc write_hw_platform {args} {set f [open [lindex $args end] w]; puts $f MOCK_XSA; close $f; return ""}
foreach mode {valid_void_return valid_info_return missing_bd multiple_bd missing_wrapper multiple_wrapper} {
    set dir [file join $base $mode]
    file mkdir $dir
    set imported 0
    set make_count 0
    set generate_count 0
    set top_count 0
    set code [catch {::s2b_inference_platform::products $dir} result]
    if {$mode in {valid_void_return valid_info_return}} {
        set ok [expr {$code == 0 && $result eq "PRODUCTS:OK" && $make_count == 1 && $top_count == 1 && [file exists [file join $dir s2b_inference_no_bit.xsa]]}]
    } elseif {$mode in {missing_bd multiple_bd}} {
        set ok [expr {$code == 1 && [string match PRODUCTS_BD_OBJECT_COUNT_FAIL:* $result] && $generate_count == 0 && $top_count == 0}]
    } else {
        set ok [expr {$code == 1 && [string match PRODUCTS_WRAPPER_OBJECT_COUNT_FAIL:* $result] && $make_count == 1 && $top_count == 0}]
    }
    puts "CASE:$mode PASS:$ok CODE:$code GENERATE:$generate_count MAKE:$make_count TOP:$top_count RESULT:$result"
    if {!$ok} {incr failures}
}
puts "API_CASES_FAILURES:$failures"
exit [expr {$failures ? 1 : 0}]
