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
if {![info exists ::t57_run_root] || ![file isdirectory $::t57_run_root]} {
    error "T57 attempt08 run root is unavailable"
}
set t57_backslash [format %c 92]
set t57_run_root_posix [string map [list $t57_backslash /] [file normalize $::t57_run_root]]
set t57_testplusarg "T57_RUN_ROOT=$t57_run_root_posix"
set t57_xsim_options "-testplusarg $t57_testplusarg"
set_property -name {xsim.simulate.xsim.more_options} -value $t57_xsim_options -objects $t57_simset
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
if {[get_property xsim.simulate.xsim.more_options $t57_simset] ne $t57_xsim_options} {
    error "T57 testplusarg is not bound to the attempt08 run root"
}
if {[file normalize [get_property xsim.simulate.custom_tcl $t57_simset]] ne [file normalize $::t57_xsim_tcl]} {
    error "T57 custom Tcl property does not point to run09/attempt08"
}
puts "T57_SIMULATION_OPTIONS_CONFIGURED simset=sim_s2a_t57_row21 debug=off runtime_property=empty testplusarg=$t57_testplusarg custom_tcl=run09/attempt08"
