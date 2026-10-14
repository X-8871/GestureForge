# 记录当前已实现DCP中HP0的BREADY/RREADY实际网表输出驱动与叶级端点。
set output_path {C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T19\postroute_hp0_query_20261014_r02\query_ready_drivers_output.tcldict}
set fp [open $output_path w]
set ps [get_cells -hierarchical -filter {REF_NAME == PS7}]
if {[llength $ps] != 1} {close $fp; error "期望一个PS7单元，实际数量=[llength $ps]"}
set run [get_runs impl_1]
puts $fp [list record design_identity project [current_project] design [current_design] run_status [get_property STATUS $run] run_directory [get_property DIRECTORY $run] part [get_property PART [current_project]] ps7_cells [llength $ps]]
foreach signal {SAXIHP0BREADY SAXIHP0RREADY} {
    set pins [get_pins -quiet -of_objects $ps -filter [format {REF_PIN_NAME == %s} $signal]]
    if {[llength $pins] != 1} {close $fp; error "$signal pin数量异常=[llength $pins]"}
    set nets [get_nets -quiet -segments -of_objects $pins]
    set leaf_pins [get_pins -quiet -leaf -of_objects $nets]
    set endpoints {}
    foreach lp $leaf_pins {
        set cell [get_cells -quiet -of_objects $lp]
        lappend endpoints [list pin [get_property NAME $lp] direction [get_property DIRECTION $lp] cell [get_property NAME $cell] ref_name [get_property REF_NAME $cell]]
    }
    set drivers {}
    foreach dp [get_pins -quiet -leaf -of_objects $nets -filter {DIRECTION == OUT}] {
        set cell [get_cells -quiet -of_objects $dp]
        lappend drivers [list pin [get_property NAME $dp] cell [get_property NAME $cell] ref_name [get_property REF_NAME $cell]]
    }
    puts $fp [list record hp0_ready_driver signal $signal direction [get_property DIRECTION [lindex $pins 0]] segment_count [llength $nets] leaf_endpoint_count [llength $leaf_pins] endpoints $endpoints output_driver_count [llength $drivers] output_drivers $drivers]
}
close $fp
puts [list query_output $output_path signals {SAXIHP0BREADY SAXIHP0RREADY}]
