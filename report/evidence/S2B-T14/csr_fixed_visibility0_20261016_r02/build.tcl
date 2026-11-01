# 当前CSR与手册DDR的visibility0隔离工程，禁止任何硬件操作。
set evidence {D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r02}
set project {D:/FPGA_Competition/w2b/tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project/s2b_inference_candidate.xpr}
set_param general.maxThreads 1
set started [clock milliseconds]
if {[catch {
    open_project $project
    if {[get_property PART [current_project]] ne "xc7z020clg400-2"} {error PART_MISMATCH}
    if {[get_property TOP [current_fileset]] ne "s2b_inference_wrapper"} {error TOP_MISMATCH}
    set bd [get_files */s2b_inference.bd]
    if {[llength $bd] != 1} {error BD_COUNT_MISMATCH}
    create_ip_run $bd
    puts "CHECKPOINT SYNTH_START"
    launch_runs synth_1 -jobs 1
    wait_on_run synth_1
    if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} {error SYNTH_INCOMPLETE}
    puts "CHECKPOINT SYNTH_COMPLETE"
    launch_runs impl_1 -to_step write_bitstream -jobs 1
    wait_on_run impl_1
    if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error IMPLEMENTATION_INCOMPLETE}
    puts "CHECKPOINT BITSTREAM_COMPLETE"
    open_run impl_1
    report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file [file join $evidence timing_summary.rpt]
    report_clock_interaction -file [file join $evidence clock_interaction.rpt]
    report_clocks -file [file join $evidence clocks.rpt]
    check_timing -verbose -file [file join $evidence check_timing.rpt]
    report_route_status -file [file join $evidence route_status.rpt]
    report_utilization -file [file join $evidence utilization.rpt]
    report_drc -file [file join $evidence drc.rpt]
    report_methodology -file [file join $evidence methodology.rpt]
    report_methodology -json [file join $evidence methodology.json]
    write_xdc -exclude_physical [file join $evidence constraints.xdc]
    write_checkpoint [file join $evidence routed.dcp]
    write_hw_platform -fixed -include_bit [file join $evidence s2b_inference.xsa]
    set bits [glob -nocomplain [file join [get_property DIRECTORY [get_runs impl_1]] *.bit]]
    if {[llength $bits] != 1} {error BIT_COUNT_MISMATCH}
    file copy [lindex $bits 0] [file join $evidence s2b_inference.bit]
    set setup [get_timing_paths -delay_type max -max_paths 1]
    set hold [get_timing_paths -delay_type min -max_paths 1]
    if {[llength $setup] != 1 || [llength $hold] != 1} {error MISSING_TIMING_PATHS}
    set setup_slack [get_property SLACK $setup]
    set hold_slack [get_property SLACK $hold]
    set stream [open [file join $evidence timing_metrics.tcldict] {WRONLY CREAT EXCL}]
    puts $stream [dict create part [get_property PART [current_project]] setup_slack $setup_slack hold_slack $hold_slack elapsed_ms [expr {[clock milliseconds]-$started}] synthesis_status [get_property STATUS [get_runs synth_1]] implementation_status [get_property STATUS [get_runs impl_1]]]
    close $stream
    if {$setup_slack < 0 || $hold_slack < 0} {error TIMING_NOT_MET}
    puts "PASS_IMPLEMENTED_ARTIFACTS_TIMING_REVIEW_PENDING"
    close_project
} message options]} {
    puts stderr "BUILD_FAILED: $message"
    if {[dict exists $options -errorinfo]} {puts stderr [dict get $options -errorinfo]}
    exit 1
}
exit 0
