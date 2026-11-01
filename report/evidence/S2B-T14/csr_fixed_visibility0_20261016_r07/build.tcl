# 从R05实际布线检查点做一次物理优化、重新布线并导出新硬件平台。
set evidence {D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r07}
set project {D:/FPGA_Competition/w2b/tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project/s2b_inference_candidate.xpr}
set r05_dcp {D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r05/routed.dcp}
set impl_run {D:/FPGA_Competition/w2b/tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project/s2b_inference_candidate.runs/impl_1}
set_param general.maxThreads 1
set started [clock milliseconds]

if {[catch {
    open_project $project
    if {[get_property PART [current_project]] ne "xc7z020clg400-2"} {error PART_MISMATCH}
    if {[get_property TOP [current_fileset]] ne "s2b_inference_wrapper"} {error TOP_MISMATCH}
    open_checkpoint $r05_dcp
    if {[get_property PART [current_design]] ne "xc7z020clg400-2"} {error CHECKPOINT_PART_MISMATCH}
    puts "CHECKPOINT DESIGN_NAME=[get_property NAME [current_design]]"
    puts "CHECKPOINT R05_ROUTED_DCP_OPENED"

    phys_opt_design -directive AggressiveExplore
    puts "CHECKPOINT POSTROUTE_PHYS_OPT_COMPLETE"
    route_design -directive Explore
    puts "CHECKPOINT REROUTE_COMPLETE"

    report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file [file join $evidence timing_summary.rpt]
    report_timing -delay_type max -max_paths 10 -path_type full -file [file join $evidence actual_timing_setup.rpt]
    report_timing -delay_type min -max_paths 10 -path_type full -file [file join $evidence actual_timing_hold.rpt]
    report_pulse_width -file [file join $evidence pulse_width.rpt]
    report_clock_interaction -file [file join $evidence clock_interaction.rpt]
    report_clocks -file [file join $evidence clocks.rpt]
    check_timing -verbose -file [file join $evidence check_timing.rpt]
    report_route_status -file [file join $evidence route_status.rpt]
    report_utilization -file [file join $evidence utilization.rpt]
    report_drc -file [file join $evidence drc.rpt]
    report_methodology -file [file join $evidence methodology.rpt]
    report_methodology -json [file join $evidence methodology.json]
    write_xdc -exclude_physical [file join $evidence constraints.xdc]
    write_checkpoint -force [file join $evidence routed.dcp]

    write_bitstream -force [file join $evidence s2b_inference.bit]
    set old_bits [glob -nocomplain [file join $impl_run *.bit]]
    if {[llength $old_bits] != 1} {error IMPL_RUN_BIT_COUNT_MISMATCH}
    file copy -force [file join $evidence s2b_inference.bit] [lindex $old_bits 0]
    puts "CHECKPOINT OWNED_IMPL_BIT_REPLACED_FOR_XSA_EXPORT"
    write_hw_platform -fixed -include_bit -force [file join $evidence s2b_inference.xsa]

    set setup [get_timing_paths -delay_type max -max_paths 1]
    set hold [get_timing_paths -delay_type min -max_paths 1]
    if {[llength $setup] != 1 || [llength $hold] != 1} {error MISSING_TIMING_PATHS}
    set setup_slack [get_property SLACK $setup]
    set hold_slack [get_property SLACK $hold]
    set stream [open [file join $evidence timing_metrics.tcldict] {WRONLY CREAT EXCL}]
    puts $stream [dict create part [get_property PART [current_project]] setup_slack $setup_slack hold_slack $hold_slack elapsed_ms [expr {[clock milliseconds]-$started}] source_checkpoint $r05_dcp postroute_phys_opt AggressiveExplore reroute Explore]
    close $stream
    puts "R07_SETUP_SLACK=$setup_slack"
    puts "R07_HOLD_SLACK=$hold_slack"
    puts "R07_ARTIFACTS_WRITTEN"
    close_project
} message options]} {
    puts stderr "BUILD_FAILED: $message"
    if {[dict exists $options -errorinfo]} {puts stderr [dict get $options -errorinfo]}
    catch {close_project}
    exit 1
}
exit 0
