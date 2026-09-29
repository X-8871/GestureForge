set t57_simset [get_filesets sim_s2a_t57_row21]
if {[llength $t57_simset] != 1} {
    error "T57 temporary simulation fileset is unavailable"
}
if {![info exists ::t57_xsim_tcl] || ![file isfile $::t57_xsim_tcl]} {
    error "T57 run09 custom XSim Tcl is unavailable"
}
set_property xsim.elaborate.debug_level off $t57_simset
set_property xsim.simulate.log_all_signals 0 $t57_simset
set_property xsim.simulate.runtime {} $t57_simset
set_property xsim.simulate.wdb {} $t57_simset
set_property xsim.simulate.xsim.more_options {} $t57_simset
set t57_backslash [format %c 92]
set t57_custom_tcl_path [file normalize $::t57_xsim_tcl]
set t57_custom_tcl_path [string map [list $t57_backslash /] $t57_custom_tcl_path]
set_property xsim.simulate.custom_tcl $t57_custom_tcl_path $t57_simset
if {[string tolower [get_property xsim.elaborate.debug_level $t57_simset]] ne "off"} {
    error "T57 debug_level is not off"
}
if {[get_property xsim.simulate.log_all_signals $t57_simset]} {
    error "T57 log_all_signals is enabled"
}
if {[get_property xsim.simulate.runtime $t57_simset] ne ""} {
    error "T57 runtime property must be empty; run length is controlled by custom Tcl"
}
if {[file normalize [get_property xsim.simulate.custom_tcl $t57_simset]] ne [file normalize $::t57_xsim_tcl]} {
    error "T57 custom Tcl property does not point to run09/attempt02"
}
puts "T57_SIMULATION_OPTIONS_CONFIGURED simset=sim_s2a_t57_row21 debug=off runtime_property=empty custom_tcl=run09/attempt02"
