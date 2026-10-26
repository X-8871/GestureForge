set project_file {D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r01\project\ov5640_single.xpr}
set project_dir [file dirname $project_file]
set evidence {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_timing36_project_impl_20261026_r01}
set bad_line {create_generated_clock -source [get_ports PixelClk] -multiply_by 5 [get_ports SerialClk]}

proc read_binary {path} {
    set stream [open $path r]
    fconfigure $stream -translation binary -encoding binary
    set value [read $stream]
    close $stream
    return $value
}

proc methodology_rule_count {path rule_id} {
    set content [read_binary $path]
    set count 0
    set found 0
    set pattern [format {^\|\s+TIMING-%s\s+\|[^\r\n]*\|\s+([0-9]+)\s+\|$} $rule_id]
    foreach raw_line [split $content "\n"] {
        set line [string trimright $raw_line "\r"]
        if {[regexp -- $pattern $line -> value]} {
            incr found
            set count $value
        }
    }
    if {$found > 1} {error "DUPLICATE_METHODOLOGY_SUMMARY_ROW_TIMING_$rule_id"}
    return $count
}

proc require_one {objects label} {
    if {[llength $objects] != 1} {
        error "${label}_COUNT=[llength $objects]; OBJECTS=$objects"
    }
    return [lindex $objects 0]
}

if {![file isfile $project_file]} {error "PROJECT_FILE_MISSING=$project_file"}
file mkdir $evidence
puts "PROJECT_FILE=$project_file"
puts "CHANGE_SCOPE=ISOLATED_PROJECT_COPY_ONLY_XDC_FIX_NO_BOARD_ACCESS"
open_project $project_file
update_compile_order -fileset sources_1

set xdc_files {}
foreach xdc [get_files -all -quiet *rgb2dvi_clocks.xdc] {
    set path [get_property NAME $xdc]
    if {[string first $project_dir $path] >= 0} {lappend xdc_files $path}
}
puts "PROJECT_RGB2DVI_CLOCK_XDC_COUNT=[llength $xdc_files]"
if {[llength $xdc_files] < 1} {error "PROJECT_HAS_NO_RGB2DVI_CLOCK_XDC"}
foreach path $xdc_files {
    set contents [read_binary $path]
    if {[string first $bad_line $contents] >= 0} {
        error "BAD_GENERATED_CLOCK_REMAINS_IN_PROJECT_XDC=$path"
    }
    puts "PROJECT_XDC_WITHOUT_BAD_CLOCK=$path"
}

reset_run impl_1
launch_runs impl_1 -jobs 4
wait_on_run impl_1
set impl_run [get_runs impl_1]
set impl_status [get_property STATUS $impl_run]
set impl_progress [get_property PROGRESS $impl_run]
puts "IMPLEMENTATION_STATUS=$impl_status"
puts "IMPLEMENTATION_PROGRESS=$impl_progress"
if {$impl_progress ne "100%" || [string first "Complete" $impl_status] < 0} {
    error "IMPLEMENTATION_NOT_COMPLETE"
}

open_run impl_1
update_timing
set method [file join $evidence methodology_routed.rpt]
set clocks [file join $evidence clocks_routed.rpt]
set timing [file join $evidence timing_summary_routed.rpt]
set interactions [file join $evidence clock_interaction_routed.rpt]
set drc [file join $evidence drc_routed.rpt]
report_methodology -file $method
report_clocks -file $clocks
report_timing_summary -file $timing
report_clock_interaction -file $interactions
report_drc -file $drc

set serial_pin_candidates {}
foreach pin [get_pins -hier -quiet -filter {NAME =~ *rgb2dvi_0/SerialClk}] {
    if {[get_property NAME $pin] eq "design_1_i/rgb2dvi_0/SerialClk"} {
        lappend serial_pin_candidates $pin
    }
}
set serial_pin [require_one $serial_pin_candidates SERIAL_CLOCK_PIN]
set serial_clocks [get_clocks -quiet -of_objects $serial_pin]
set auto_clock_candidates {}
foreach clock $serial_clocks {
    if {[get_property NAME $clock] eq "I"} {lappend auto_clock_candidates $clock}
}
set auto_clock [require_one $auto_clock_candidates SERIAL_AUTO_CLOCK]
set auto_period [get_property PERIOD $auto_clock]
set timing36 [methodology_rule_count $method 36]
set timing30 [methodology_rule_count $method 30]
set timing17 [methodology_rule_count $method 17]
set timing18 [methodology_rule_count $method 18]
set timing9 [methodology_rule_count $method 9]
puts "SERIAL_PORT_PIN=$serial_pin CLOCKS=$serial_clocks"
puts "SERIAL_AUTO_CLOCK=$auto_clock PERIOD=$auto_period"
puts "METHODOLOGY_TIMING36=$timing36 TIMING30=$timing30 TIMING17=$timing17 TIMING18=$timing18 TIMING9=$timing9"

if {abs(double($auto_period) - 2.000) > 0.001} {error "SERIAL_AUTO_CLOCK_PERIOD_CHANGED"}
if {$timing36 != 0 || $timing30 != 0} {error "TIMING36_OR_TIMING30_REMAINS"}
puts "PROJECT_IMPL_DIAGNOSTIC_RESULT=PASS_ROUTED_REPORTS_CAPTURED_NO_BOARD_ACCESS"
close_project
