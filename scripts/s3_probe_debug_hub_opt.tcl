# 仅用已完成综合的隔离参考工程验证 debug hub 的 opt_design 生命周期。
if {$argc != 2} {
    puts stderr "EXPECTED_PROJECT_XPR_AND_NEW_RESULT_DIR"
    exit 2
}

set project_path [lindex $argv 0]
set result_dir [lindex $argv 1]
if {[file pathtype $project_path] ne "absolute" ||
    [file pathtype $result_dir] ne "absolute"} {
    puts stderr "ABSOLUTE_PATHS_REQUIRED"
    exit 2
}

# 将工程输入和所有输出限制在脚本所属仓库的隔离试验目录内。
proc s3_path_within {candidate root} {
    set candidate [file normalize $candidate]
    set root [string trimright [file normalize $root] "/\\"]
    if {[string equal -nocase $candidate $root]} {
        return 1
    }
    set root_length [string length $root]
    if {[string length $candidate] <= $root_length ||
        ![string equal -nocase [string range $candidate 0 [expr {$root_length - 1}]] $root]} {
        return 0
    }
    set separator [string index $candidate $root_length]
    return [expr {$separator eq "/" || $separator eq "\\"}]
}

set script_path [file normalize [info script]]
set repo_root [file dirname [file dirname $script_path]]
set isolated_root [file normalize [file join $repo_root tmp s3s05]]
set project_path [file normalize $project_path]
set result_dir [file normalize $result_dir]
if {![file isdirectory $isolated_root]} {
    puts stderr "ISOLATED_ROOT_MISSING"
    exit 2
}
if {![s3_path_within $project_path $isolated_root]} {
    puts stderr "PROJECT_OUTSIDE_ISOLATED_ROOT"
    exit 2
}
if {![s3_path_within $result_dir $isolated_root] ||
    ![s3_path_within [file dirname $result_dir] $isolated_root]} {
    puts stderr "RESULT_DIR_OUTSIDE_ISOLATED_ROOT"
    exit 2
}
if {![file isfile $project_path]} {
    puts stderr "INVALID_PROJECT_XPR"
    exit 2
}
if {[file exists $result_dir] ||
    ![file isdirectory [file dirname $result_dir]]} {
    puts stderr "RESULT_DIR_MUST_BE_NEW_WITH_EXISTING_PARENT"
    exit 2
}
file mkdir $result_dir

set result_path [file join $result_dir result.txt]
set synth_progress NOT_RECORDED
set synth_status NOT_RECORDED
set synth_hub_states {}
set impl_progress_before NOT_RECORDED
set impl_progress_after NOT_RECORDED
set impl_status NOT_RECORDED
set post_hub_states {}
set post_blackboxes {}
set opt_dcp NOT_RECORDED
set opt_log NOT_RECORDED
set stage_markers NOT_RECORDED
set error_info ""
set failed [catch {
    set_param general.maxThreads 1
    open_project $project_path
    if {![string equal -nocase [get_property PART [current_project]] xa7z020clg400-1I]} {
        error "EXACT_PART_MISMATCH"
    }
    if {[get_property TOP [get_filesets sources_1]] ne "design_1_wrapper"} {
        error "UNEXPECTED_TOP"
    }

    set synth_run [get_runs synth_1]
    set synth_progress [get_property PROGRESS $synth_run]
    set synth_status [get_property STATUS $synth_run]
    if {$synth_progress ne "100%" || ![string match {*Complete*} $synth_status]} {
        error "FROZEN_SYNTH_CHECKPOINT_REQUIRED:$synth_progress:$synth_status"
    }

    open_run synth_1
    set synth_debug_hubs [get_cells -hierarchical -quiet -filter {NAME == "dbg_hub"}]
    set synth_hub_states {}
    foreach cell $synth_debug_hubs {
        lappend synth_hub_states "$cell=[get_property IS_BLACKBOX $cell]"
    }
    if {[llength $synth_debug_hubs] == 0} {
        error "SYNTH_DEBUG_HUB_NOT_FOUND"
    }
    close_design

    set impl_run [get_runs impl_1]
    set impl_progress_before [get_property PROGRESS $impl_run]
    if {$impl_progress_before ne "0%"} {
        error "IMPL_RUN_NOT_FRESH:$impl_progress_before"
    }
    launch_runs impl_1 -to_step opt_design -jobs 1
    wait_on_run impl_1

    set impl_progress_after [get_property PROGRESS $impl_run]
    set impl_status [get_property STATUS $impl_run]
    set run_dir [file join [file dirname $project_path] "[file rootname [file tail $project_path]].runs" impl_1]
    set opt_dcp [file join $run_dir design_1_wrapper_opt.dcp]
    set opt_log [file join $run_dir runme.log]
    set opt_marker [file join $run_dir .opt_design.end.rst]
    set place_marker [file join $run_dir .place_design.begin.rst]
    set route_marker [file join $run_dir .route_design.begin.rst]
    set bitstream_marker [file join $run_dir .write_bitstream.begin.rst]
    set stage_markers "OPT_END=[file exists $opt_marker];PLACE_BEGIN=[file exists $place_marker];ROUTE_BEGIN=[file exists $route_marker];BITSTREAM_BEGIN=[file exists $bitstream_marker]"

    if {![string match -nocase {*not started place_design*} $impl_status]} {
        error "RUN_NOT_STOPPED_BEFORE_PLACE_DESIGN:$impl_status:$impl_progress_after"
    }
    if {![file isfile $opt_dcp] || ![file isfile $opt_marker] ||
        [file exists $place_marker] || [file exists $route_marker] || [file exists $bitstream_marker]} {
        error "OPT_STAGE_MARKERS_INVALID:$stage_markers"
    }

    if {![file isfile $opt_log]} {
        error "OPT_RUN_LOG_MISSING:$opt_log"
    }
    set log_channel [open $opt_log r]
    set opt_log_text [read $log_channel]
    close $log_channel
    if {![regexp -nocase {opt_design completed successfully} $opt_log_text] ||
        ![regexp {0 Errors encountered\.} $opt_log_text]} {
        error "OPT_RUN_LOG_DID_NOT_CONFIRM_SUCCESS"
    }

    open_checkpoint $opt_dcp
    set post_debug_hubs [get_cells -hierarchical -quiet -filter {NAME == "dbg_hub"}]
    set post_hub_states {}
    foreach cell $post_debug_hubs {
        lappend post_hub_states "$cell=[get_property IS_BLACKBOX $cell]"
    }
    if {[llength $post_debug_hubs] == 0} {
        error "OPT_DEBUG_HUB_NOT_FOUND_IN_CHECKPOINT"
    }
    set blackbox_query_failed [catch {
        set post_blackboxes [get_cells -hierarchical -quiet -filter {IS_BLACKBOX == 1}]
    } blackbox_query_result]
    if {$blackbox_query_failed} {
        error "OPT_BLACKBOX_QUERY_FAILED:$blackbox_query_result"
    }
    if {[llength $post_blackboxes] != 0} {
        error "OPT_CHECKPOINT_HAS_BLACKBOXES:$post_blackboxes"
    }
    close_design

    set result PASS_OPT_DESIGN_STAGE_REACHED_ONLY
} result error_info]

set channel [open $result_path {WRONLY CREAT EXCL}]
fconfigure $channel -encoding utf-8 -translation lf
puts $channel "VIVADO=[version -short]"
puts $channel "PART=xa7z020clg400-1I"
puts $channel "PROJECT=$project_path"
puts $channel "ISOLATED_ROOT=$isolated_root"
puts $channel "SYNTH_PROGRESS=$synth_progress"
puts $channel "SYNTH_STATUS=$synth_status"
puts $channel "SYNTH_DEBUG_HUBS=$synth_hub_states"
puts $channel "SYNTH_GLOBAL_BLACKBOX_QUERY=NOT_USED"
puts $channel "IMPL_STATUS=$impl_status"
puts $channel "IMPL_PROGRESS_AFTER_OPT=$impl_progress_after"
puts $channel "OPT_DCP=$opt_dcp"
puts $channel "OPT_LOG=$opt_log"
puts $channel "STAGE_MARKERS=$stage_markers"
puts $channel "OPT_DEBUG_HUBS=$post_hub_states"
puts $channel "OPT_BLACKBOXES=$post_blackboxes"
puts $channel "FAILED=$failed"
puts $channel "RESULT=$result"
puts $channel "SCOPE=OPT_DESIGN_ONLY_NO_FINAL_BOARD_XDC_NO_PLACE_ROUTE_NO_BITSTREAM_NO_HARDWARE"
if {$failed} {
    puts $channel "ERROR=$result"
    puts $channel "ERROR_INFO=$error_info"
}
close $channel
puts "RESULT=$result"
if {$failed} {exit 2}
exit 0
