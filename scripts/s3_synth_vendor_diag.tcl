# 仅对隔离参考工程执行综合诊断；不加载最终板卡约束、不实现、不生成比特流。
if {$argc != 2} {puts stderr "EXPECTED_ISOLATED_PROJECT_AND_NEW_REPORT_DIR"; exit 2}
set project_path [lindex $argv 0]
set report_dir [lindex $argv 1]
if {[file pathtype $project_path] ne "absolute" || ![file isfile $project_path]} {puts stderr "INVALID_PROJECT"; exit 2}
if {[file pathtype $report_dir] ne "absolute" || [file exists $report_dir] || ![file isdirectory [file dirname $report_dir]]} {puts stderr "INVALID_NEW_REPORT_DIR"; exit 2}
file mkdir $report_dir
set failed [catch {
    open_project $project_path
    if {![string equal -nocase [get_property PART [current_project]] xa7z020clg400-1I]} {error "EXACT_PART_MISMATCH"}
    if {[get_property TOP [get_filesets sources_1]] ne "design_1_wrapper"} {error "UNEXPECTED_TOP"}
    set active [get_property PROGRESS [get_runs synth_1]]
    if {$active ne "0%"} {error "SYNTH_RUN_NOT_FRESH"}
    set_param general.maxThreads 1
    launch_runs synth_1 -jobs 1
    wait_on_run synth_1
    set run_status [get_property STATUS [get_runs synth_1]]
    if {[get_property PROGRESS [get_runs synth_1]] ne "100%" || ![string match {*Complete*} $run_status]} {error "SYNTH_NOT_COMPLETE:$run_status"}
    open_run synth_1
    report_utilization -file [file join $report_dir utilization.rpt]
    report_drc -file [file join $report_dir drc.rpt]
    set blackboxes [get_cells -hierarchical -quiet -filter {IS_BLACKBOX == 1}]
    if {[llength $blackboxes] != 0} {error "UNRESOLVED_BLACKBOXES:$blackboxes"}
    close_project
    set result PASS_UNCONSTRAINED_SYNTH_DIAGNOSTIC_ONLY
} result]
set channel [open [file join $report_dir result.txt] {WRONLY CREAT EXCL}]
fconfigure $channel -encoding utf-8 -translation lf
puts $channel "FAILED=$failed"
puts $channel "RESULT=$result"
if {[info exists run_status]} {puts $channel "RUN_STATUS=$run_status"}
puts $channel "SCOPE=NO_IMPLEMENTATION_NO_BITSTREAM_NO_HARDWARE_NO_TIMING_SIGNOFF"
close $channel
puts "RESULT=$result"
if {$failed} {exit 2}
exit 0
