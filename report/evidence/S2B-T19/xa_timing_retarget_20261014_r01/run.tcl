# 只在本任务自有会话中重开已布线检查点，核验照片所示XA系列的时序适用范围。
# 不综合、不布局布线、不生成位流，不修改已冻结检查点或原工程文件。
set s2b_run_dir [file dirname [file normalize [info script]]]
set s2b_dcp {C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T19\visibility1_timing_current_20261014_r01\artifacts\s2b_inference_wrapper_routed.dcp}
set s2b_target xa7z020clg400-1I
set s2b_outputs {result.tcldict timing_summary.rpt methodology.rpt route_status.rpt constraints.xdc}
foreach s2b_name $s2b_outputs {
    if {[file exists [file join $s2b_run_dir $s2b_name]]} {
        error "证据输出已经存在，拒绝覆盖同一RunId：$s2b_name"
    }
}
if {![file isfile $s2b_dcp]} {error "绑定的检查点不是普通文件"}
set s2b_result [dict create scope OFFLINE_RETARGET_STA_ONLY source_commit f92823f0bd577a49db543868f44c4f63b670d8e0 audit_base_commit 5b4b140d9540759a6940b339e93278371c06987e source_dcp $s2b_dcp source_dcp_sha256 cd0a10f90659a5a9a9cc184f08750ed6057a39e6eefe63f60173d031465df101 requested_part $s2b_target previous_project [current_project] previous_part [get_property PART [current_project]] tool_version [version -short] started_utc [clock format [clock seconds] -gmt 1 -format {%Y-%m-%dT%H:%M:%SZ}] hardware_execution NOT_RUN]
set s2b_started_ms [clock milliseconds]
close_project
set s2b_open_code [catch {open_checkpoint -part $s2b_target $s2b_dcp} s2b_open_message s2b_open_options]
dict set s2b_result open_code $s2b_open_code
dict set s2b_result open_message $s2b_open_message
if {$s2b_open_code != 0} {
    dict set s2b_result status RETARGET_REJECTED
    dict set s2b_result error_options $s2b_open_options
} else {
    dict set s2b_result actual_part [get_property PART [current_project]]
    set s2b_report_code [catch {
        if {[get_property PART [current_project]] ne $s2b_target} {error "重开检查点后的器件与请求不一致"}
        report_timing_summary -report_unconstrained -warn_on_violation -max_paths 10 -file [file join $s2b_run_dir timing_summary.rpt]
        report_methodology -file [file join $s2b_run_dir methodology.rpt]
        report_route_status -file [file join $s2b_run_dir route_status.rpt]
        write_xdc -exclude_physical [file join $s2b_run_dir constraints.xdc]
        dict set s2b_result setup_slack_ns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1]]
        dict set s2b_result hold_slack_ns [get_property SLACK [get_timing_paths -delay_type min -max_paths 1]]
        foreach s2b_clock [get_clocks] {
            dict lappend s2b_result clocks [dict create name [get_property NAME $s2b_clock] period_ns [get_property PERIOD $s2b_clock]]
        }
    } s2b_report_message s2b_report_options]
    dict set s2b_result report_code $s2b_report_code
    dict set s2b_result report_message $s2b_report_message
    if {$s2b_report_code != 0} {
        dict set s2b_result status REPORT_FAILED
        dict set s2b_result error_options $s2b_report_options
    } else {
        dict set s2b_result status REPORTS_COMPLETE_NOT_DEPLOYMENT_APPROVAL
    }
}
dict set s2b_result elapsed_ms [expr {[clock milliseconds] - $s2b_started_ms}]
set s2b_channel [open [file join $s2b_run_dir result.tcldict] {WRONLY CREAT EXCL}]
fconfigure $s2b_channel -encoding utf-8 -translation lf
puts $s2b_channel $s2b_result
close $s2b_channel
puts $s2b_result
if {$s2b_open_code != 0} {return -code error $s2b_open_message}
if {$s2b_report_code != 0} {return -code error $s2b_report_message}
