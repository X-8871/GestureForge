# 第二轮独立路径检查，不启动 Vivado。
set repo [lindex $argv 0]
set output [lindex $argv 1]
source [file join $repo vivado/s2b_inference_platform.tcl]
set helper [file join $output synthetic_raw.txt]
set base_project [file join $output valid_project]
set base_evidence [file join $output valid_evidence]
set cases [list \
    [list same $base_project $base_project] \
    [list nested $base_project [file join $base_project child]] \
    [list changed_case [file join [string map {S2B-T13 s2b-t13} $output] new_project] $base_evidence] \
    [list dot [file join $output . dot_project] $base_evidence] \
    [list parent_dot [file join $output .. dot_project] $base_evidence] \
    [list relative relative_project $base_evidence] \
    [list existing $output $base_evidence] \
    [list missing_parent [file join $output absent child] $base_evidence] \
    [list trailing "$base_project " $base_evidence] \
    [list junction [file join $output junction_parent new_project] $base_evidence]]
foreach case $cases {
    lassign $case name project evidence
    set code [catch {::s2b_inference_platform::path_preflight $repo $project $evidence $helper $helper "" ""} message]
    puts "CASE:$name CODE:$code MESSAGE:$message"
    if {$code != 1} {error "NEGATIVE_CASE_ACCEPTED:$name"}
    if {$name ne "existing" && [file exists $project]} {error "NEGATIVE_CREATED_PATH:$name"}
}
puts [::s2b_inference_platform::path_preflight $repo $base_project $base_evidence $helper $helper "" ""]
if {[file exists $base_project] || [file exists $base_evidence]} {error "PREFLIGHT_CREATED_OUTPUT"}
rename source original_source
set source_count 0
proc source {args} {incr ::source_count; original_source [lindex $args end]}
proc current_project {args} {return ""}
proc get_parts {args} {return xc7z020clg400-2}
namespace eval ::ipcfg {}
proc ::ipcfg::help {} {}
proc ::ipcfg::python_status {} {return "PYTHON:OK synthetic"}
proc ::ipcfg::python_exec {args} {return "PYTHON_IMPORTS:OK"}
proc ::ipcfg::python_script {args} {return "PLATFORM_STATIC:OK"}
proc create_project {args} {error "REACHED_CREATE_PROJECT"}
set code [catch {::s2b_inference_platform::run $repo $base_project $base_project $helper $helper} message]
if {$code != 1 || $source_count != 0 || [file exists $base_project]} {error "RUN_NEGATIVE_SIDE_EFFECT"}
puts "RUN_NEGATIVE:$message SOURCE_COUNT:$source_count"
set code [catch {::s2b_inference_platform::run $repo $base_project $base_evidence $helper $helper} message]
if {$code != 1 || $message ne "REACHED_CREATE_PROJECT" || $source_count != 1 ||
    ![file isdirectory $base_project] || ![file isdirectory $base_evidence]} {error "VALID_RUN_PRECONDITION_FAIL:$message"}
puts "VALID_RUN:REACHED_CREATE_PROJECT SOURCE_COUNT:$source_count"
puts "PATH_PROBES:PASS"
