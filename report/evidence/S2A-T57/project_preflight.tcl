set xpr {D:/FPGA_Competition/vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr}
if {![file isfile $xpr]} {
    puts stderr "FAIL target XPR is missing: $xpr"
    exit 2
}
if {[catch {open_project -quiet $xpr} message]} {
    puts stderr "FAIL open_project: $message"
    exit 3
}
set project [current_project]
puts "PROJECT_NAME=[get_property NAME $project]"
puts "PROJECT_DIRECTORY=[get_property DIRECTORY $project]"
puts "FILESETS=[get_filesets]"
foreach simset {sim_s2a_t56_row20 sim_s2a_t55_row19 sim_s2a_t54_row18} {
    if {[llength [get_filesets -quiet $simset]] == 1} {
        puts "SIMSET_BEGIN=$simset"
        foreach property {top xsim.elaborate.debug_level xsim.simulate.log_all_signals xsim.simulate.runtime xsim.simulate.custom_tcl} {
            if {![catch {get_property $property [get_filesets $simset]} value]} {
                puts "SIMSET_PROPERTY=$simset,$property,$value"
            }
        }
        puts "SIMSET_FILES=[get_files -of_objects [get_filesets $simset]]"
        puts "SIMSET_END=$simset"
    } else {
        puts "SIMSET_MISSING=$simset"
    }
}
puts "PROJECT_PREFLIGHT_PASS"
exit 0
