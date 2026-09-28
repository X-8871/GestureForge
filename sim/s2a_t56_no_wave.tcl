# T56 仿真关闭调试能力和全信号日志，避免启用波形跟踪。
set t56_simset [get_filesets sim_s2a_t56_row20]
if {[llength $t56_simset] != 1} {
    error "找不到唯一的 T56 仿真 fileset"
}
set_property xsim.elaborate.debug_level off $t56_simset
set_property xsim.simulate.log_all_signals 0 $t56_simset
if {[string tolower [get_property xsim.elaborate.debug_level $t56_simset]] ne "off"} {
    error "T56 debug_level 未关闭"
}
if {[get_property xsim.simulate.log_all_signals $t56_simset]} {
    error "T56 log_all_signals 未关闭"
}
puts "T56 no-wave: debug_level=off log_all_signals=0"