# 独立轻量 Tcl 桩：只检测文件前置核验，不运行 Vivado。
set repo [lindex $argv 0]
set output [lindex $argv 1]
source [file join $repo vivado/s2b_inference_platform.tcl]
rename source original_source
proc source {args} {original_source [lindex $args end]}
proc current_project {args} {return ""}
proc get_parts {args} {return xc7z020clg400-2}
namespace eval ::ipcfg {}
proc ::ipcfg::help {} {}
proc ::ipcfg::python_status {} {return "PYTHON:OK synthetic"}
proc ::ipcfg::python_exec {args} {return "PYTHON_IMPORTS:OK"}
proc ::ipcfg::python_script {args} {return "PLATFORM_STATIC:OK"}
proc create_project {args} {error "REACHED_CREATE_PROJECT:$args"}
set helper [file join $output synthetic_raw.txt]
foreach case {same_directory case_changed_parent dot_parent} {
    if {$case eq "same_directory"} {
        set project [file join $output same_run]
        set evidence $project
    } elseif {$case eq "case_changed_parent"} {
        set project [file join [string map {S2B-T13 s2b-t13} $output] case_project]
        set evidence [file join $output case_evidence]
    } else {
        set project [file join $output . dot_project]
        set evidence [file join $output dot_evidence]
    }
    set code [catch {::s2b_inference_platform::run $repo $project $evidence $helper $helper} message]
    puts "CASE:$case CODE:$code MESSAGE:$message"
    puts "PROJECT_EXISTS:[file isdirectory $project] EVIDENCE_EXISTS:[file isdirectory $evidence]"
}
