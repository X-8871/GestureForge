# 独立外口创建桩：创建命令返回空，只从网对象查询端点。
source [file join [lindex $argv 0] vivado/s2b_inference_platform.tcl]
proc get_bd_intf_pins {name} {
    if {$::mode eq "multiple_pin"} {return {/ps7/DDR /wrong}}
    return /ps7/DDR
}
proc get_bd_intf_ports {args} {
    if {![llength $args]} {return $::ports}
    if {$::mode eq "no_created"} {return /OLD}
    return $::endpoints
}
proc make_bd_intf_pins_external {pin} {
    set ::endpoints /DDR_0
    if {$::mode eq "multiple_created"} {set ::endpoints {/DDR_0 /DDR_1}}
    set ::ports [concat $::ports $::endpoints]
    return ""
}
proc get_bd_intf_nets {args} {
    if {$::mode eq "no_net"} {return {}}
    if {$::mode eq "multiple_net"} {return {DDR_NET OTHER_NET}}
    return DDR_NET
}
proc set_property {property value object} {
    if {$object eq ""} {error "EMPTY_OBJECT_REJECTED"}
    if {$property ne "name" || $value ne "DDR"} {error "UNEXPECTED_RENAME"}
    if {$::mode ne "rename_failed"} {set ::endpoints /DDR}
    return ""
}
foreach mode {void_success multiple_pin no_net multiple_net no_created multiple_created rename_failed} {
    set ports /OLD
    set endpoints {}
    set code [catch {::s2b_inference_platform::externalize_unique ps7/DDR DDR} message]
    puts "CASE:$mode CODE:$code MESSAGE:$message"
    if {$mode eq "void_success"} {
        if {$code != 0 || $message ne "/DDR"} {error "VOID_EXTERNAL_FAILED"}
    } elseif {$code != 1} {error "BAD_EXTERNAL_ACCEPTED:$mode"}
}
puts "EXTERNAL_CASES:PASS"
