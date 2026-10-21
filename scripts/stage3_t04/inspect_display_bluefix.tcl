# 阶段3最小位重排变体构建后核验，独立新目录保存网表及方法学结果。
# 用法：vivado -mode batch -source inspect_display_bluefix.tcl -tclargs <run_dir> <新输出目录>
# 只读取已有 DCP；不改变工程、不实现、不接触硬件。

set run_dir [file normalize [lindex $argv 0]]
set output_dir [file normalize [lindex $argv 1]]
if {[llength $argv] != 2 || ![file isdirectory $run_dir] || [file exists $output_dir]} {
    puts "DISPLAY_INSPECT_FAIL=INVALID_OR_EXISTING_PATH"
    exit 3
}
file mkdir $output_dir
cd $output_dir
if {[catch {
    set ooc [file join $run_dir project ov5640_single.runs design_1_alinx_ov5640_0_0_synth_1 design_1_alinx_ov5640_0_0.dcp]
    open_checkpoint $ooc
    write_verilog -force -mode funcsim [file join $output_dir camera_ooc_netlist.v]
    close_design
    open_checkpoint [file join $run_dir project ov5640_single.runs impl_1 design_1_wrapper_routed.dcp]
    report_methodology -json [file join $output_dir methodology.json]
    write_xdc -force -exclude_physical [file join $output_dir constraints.xdc]
    report_timing_summary -delay_type min_max -report_unconstrained -file [file join $output_dir timing_summary.rpt]
    report_drc -file [file join $output_dir drc.rpt]
    close_design
} err]} {
    puts "DISPLAY_INSPECT_FAIL=$err"
    exit 2
}
puts "DISPLAY_INSPECT_DONE=1"
exit 0
