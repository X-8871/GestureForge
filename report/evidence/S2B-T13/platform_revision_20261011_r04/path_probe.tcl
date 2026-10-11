source {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/vivado/s2b_inference_platform.tcl}
set repo {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set work {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/tmp/2B/S2B-T13/platform_revision_20261011_r04}
set helper [file join $work helper.tcl]
set native [file join $work native.log]
proc current_project {args} {return ""}
proc get_parts {args} {return xc7z020clg400-2}
proc create_project {args} {error REACHED_CREATE_PROJECT}
namespace eval ::ipcfg {
    proc help {args} {return ""}
    proc python_status {} {return "PYTHON:OK path_test_stub"}
    proc python_exec {args} {return "PYTHON_IMPORTS:OK"}
    proc python_script {args} {return "PLATFORM_STATIC:OK"}
}
rename source original_source
proc source {args} {incr ::source_count; return ""}
set failures 0
proc check_case {name project evidence expected {case_repo ""}} {
    global repo helper native failures
    if {$case_repo eq ""} {set case_repo $repo}
    set ::source_count 0
    set before_p [file exists $project]
    set before_e [file exists $evidence]
    set code [catch {::s2b_inference_platform::run $case_repo $project $evidence $helper $native} message]
    set after_p [file exists $project]
    set after_e [file exists $evidence]
    if {$expected eq "VALID"} {
        set ok [expr {$code == 1 && $message eq "REACHED_CREATE_PROJECT" && $::source_count == 1 && $after_p && $after_e}]
    } else {
        set ok [expr {$code == 1 && [string match $expected $message] && $::source_count == 0 && $before_p == $after_p && $before_e == $after_e}]
    }
    puts "CASE:$name PASS:$ok CODE:$code SOURCES:$::source_count PROJECT:$before_p/$after_p EVIDENCE:$before_e/$after_e MESSAGE:$message"
    if {!$ok} {incr failures}
}
check_case same [file join $work same] [file join $work same] PATH_OUTPUT_OVERLAP:*
check_case nested [file join $work outer] [file join $work outer inner] PATH_OUTPUT_OVERLAP:*
check_case reverse_nested [file join $work outer2 inner] [file join $work outer2] PATH_OUTPUT_OVERLAP:*
check_case case_parent [string map {S2B-T13 s2b-t13} [file join $work case_project]] [file join $work case_evidence] PATH_EXACT_NAME_FAIL:*
check_case case_repo [file join $work case_repo_project] [file join $work case_repo_evidence] PATH_EXACT_NAME_FAIL:* [string map {FPGA_Competition fpga_competition} $repo]
check_case dot [format "%s/./dot_project" $work] [file join $work dot_evidence] PATH_LITERAL_FAIL:*
check_case existing [file join $work existing_dir] [file join $work existing_evidence] PATH_ALREADY_EXISTS:*
check_case file_parent [file join $helper project] [file join $work type_evidence] PATH_TARGET_TYPE_FAIL:*
check_case junction [file join $work junction_parent project] [file join $work junction_evidence] *PATH_*FAIL*
puts {SYMLINK_FIXTURE:NOT_AVAILABLE; actual_junction_reparse_test_retained}
check_case valid [file join $work valid_project] [file join $work valid_evidence] VALID
puts "PATH_CASES_FAILURES:$failures"
exit [expr {$failures ? 1 : 0}]
