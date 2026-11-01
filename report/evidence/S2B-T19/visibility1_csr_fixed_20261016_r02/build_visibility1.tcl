# 仅在 proof、独立审查和预算批准齐备后构建 visibility=1 独立平台。
if {[llength $argv] != 8} {
    puts "VISIBILITY1_ARGUMENT_COUNT_FAIL:[llength $argv]"
    exit 2
}
lassign $argv repo_root project_dir evidence_dir helper native_log proof review review_sha256
set_param general.maxThreads 1
set started_ms [clock milliseconds]

proc emit_visibility1_reports {evidence_dir} {
    report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file [file join $evidence_dir timing_summary.rpt]
    report_timing -delay_type max -max_paths 10 -path_type full -file [file join $evidence_dir actual_timing_setup.rpt]
    report_timing -delay_type min -max_paths 10 -path_type full -file [file join $evidence_dir actual_timing_hold.rpt]
    report_pulse_width -file [file join $evidence_dir pulse_width.rpt]
    report_clock_interaction -file [file join $evidence_dir clock_interaction.rpt]
    report_clocks -file [file join $evidence_dir clocks.rpt]
    check_timing -verbose -file [file join $evidence_dir check_timing.rpt]
    report_route_status -file [file join $evidence_dir route_status.rpt]
    report_utilization -file [file join $evidence_dir utilization.rpt]
    report_drc -file [file join $evidence_dir drc.rpt]
    report_methodology -file [file join $evidence_dir methodology.rpt]
    report_methodology -json [file join $evidence_dir methodology.json]
    write_xdc -exclude_physical [file join $evidence_dir constraints.xdc]
    write_checkpoint -force [file join $evidence_dir routed.dcp]
}

if {[catch {
    if {[current_project -quiet] ne ""} {error "已有打开项目，停止独立构建"}
    source -notrace [file join $repo_root vivado/s2b_inference_platform.tcl]
    set platform_result [::s2b_inference_platform::run $repo_root $project_dir $evidence_dir $helper $native_log $proof $review $review_sha256]
    if {$platform_result ne "INFERENCE_PLATFORM:BUILD_CANDIDATE_OK"} {error "PLATFORM_BUILD_RESULT_FAIL:$platform_result"}
    puts "VISIBILITY1_PLATFORM_PROOF_ACCEPTED"

    if {[current_project -quiet] eq ""} {error "PLATFORM_PROJECT_NOT_OPEN"}
    if {[get_property PART [current_project]] ne "xc7z020clg400-2"} {error "PART_MISMATCH"}
    if {[get_property TOP [current_fileset]] ne "s2b_inference_wrapper"} {error "TOP_MISMATCH"}
    launch_runs synth_1 -jobs 1
    wait_on_run synth_1
    if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} {error "SYNTH_INCOMPLETE"}
    if {[get_property NEEDS_REFRESH [get_runs synth_1]]} {error "SYNTH_NEEDS_REFRESH"}
    puts "CHECKPOINT SYNTH_COMPLETE"

    launch_runs impl_1 -to_step route_design -jobs 1
    wait_on_run impl_1
    if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error "ROUTE_INCOMPLETE"}
    if {[get_property NEEDS_REFRESH [get_runs impl_1]]} {error "IMPLEMENTATION_NEEDS_REFRESH"}
    open_run impl_1
    set setup_path [get_timing_paths -delay_type max -max_paths 1]
    set hold_path [get_timing_paths -delay_type min -max_paths 1]
    if {[llength $setup_path] != 1 || [llength $hold_path] != 1} {error "MISSING_INITIAL_POST_ROUTE_TIMING_PATHS"}
    set initial_setup_slack [get_property SLACK [lindex $setup_path 0]]
    set initial_hold_slack [get_property SLACK [lindex $hold_path 0]]
    report_timing_summary -delay_type min_max -report_unconstrained -max_paths 10 -file [file join $evidence_dir timing_summary_before_opt.rpt]
    report_timing -delay_type max -max_paths 10 -path_type full -file [file join $evidence_dir actual_timing_setup_before_opt.rpt]
    report_timing -delay_type min -max_paths 10 -path_type full -file [file join $evidence_dir actual_timing_hold_before_opt.rpt]
    set phys_opt_ran false
    if {$initial_setup_slack < 0 || $initial_hold_slack < 0} {
        puts "CHECKPOINT POST_ROUTE_PHYS_OPT_BEGIN setup_slack=$initial_setup_slack hold_slack=$initial_hold_slack"
        phys_opt_design -directive AggressiveExplore
        set phys_opt_ran true
        puts "CHECKPOINT POST_ROUTE_PHYS_OPT_END"
        route_design -directive Explore
        puts "CHECKPOINT POST_ROUTE_REROUTE_END"
    }

    set setup_path [get_timing_paths -delay_type max -max_paths 1]
    set hold_path [get_timing_paths -delay_type min -max_paths 1]
    if {[llength $setup_path] != 1 || [llength $hold_path] != 1} {error "MISSING_FINAL_TIMING_PATHS"}
    set setup_slack [get_property SLACK [lindex $setup_path 0]]
    set hold_slack [get_property SLACK [lindex $hold_path 0]]
    emit_visibility1_reports $evidence_dir
    write_bitstream -force [file join $evidence_dir bitgen_raw.bit]
    set owned_impl_bit [file join $project_dir s2b_inference_candidate.runs impl_1 s2b_inference_wrapper.bit]
    if {[file exists $owned_impl_bit]} {error "OWNED_IMPL_BIT_ALREADY_EXISTS:$owned_impl_bit"}
    file mkdir [file dirname $owned_impl_bit]
    file copy [file join $evidence_dir bitgen_raw.bit] $owned_impl_bit
    puts "CHECKPOINT OWNED_IMPL_BIT_SET_TO_OPTIMIZED_BIT"
    write_hw_platform -fixed -include_bit [file join $evidence_dir s2b_inference.xsa]
    set metrics [open [file join $evidence_dir timing_metrics.tcldict] {WRONLY CREAT EXCL}]
    puts $metrics [dict create part [get_property PART [current_project]] visibility_parameter 1 initial_setup_slack $initial_setup_slack initial_hold_slack $initial_hold_slack setup_slack $setup_slack hold_slack $hold_slack post_route_phys_opt_ran $phys_opt_ran post_route_reroute_ran $phys_opt_ran no_bit_xsa [file join $evidence_dir s2b_inference_no_bit.xsa] bitgen_raw [file join $evidence_dir bitgen_raw.bit] packaged_impl_bit $owned_impl_bit elapsed_ms [expr {[clock milliseconds]-$started_ms}] synthesis_status [get_property STATUS [get_runs synth_1]] implementation_status [get_property STATUS [get_runs impl_1]]]
    close $metrics
    puts "CHECKPOINT ROUTED_ARTIFACTS_WRITTEN"
    if {$setup_slack < 0 || $hold_slack < 0} {error "TIMING_NOT_MET:setup=$setup_slack:hold=$hold_slack"}
    puts "PASS_VISIBILITY1_FULL_SYNTH_IMPL_TIMING_REVIEW_PENDING"
    close_project
} message options]} {
    puts "VISIBILITY1_BUILD_FAILED: $message"
    if {[dict exists $options -errorinfo]} {puts [dict get $options -errorinfo]}
    catch {close_project}
    exit 1
}
exit 0
