set project_file {D:\codex-worktrees\dbdf\tmp\3\S3-T05\t05_timing36_project_impl_20261026_r02\project\ov5640_single.xpr}
set project_dir [file dirname $project_file]
set evidence {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_timing36_project_impl_20261026_r02}
set source_xdc [file normalize [file join $project_dir .. vendor_src my_ip rgb2dvi_v1_3 src rgb2dvi_clocks.xdc]]
set generated_xdc [file join $project_dir ov5640_single.gen sources_1 bd design_1 ip design_1_rgb2dvi_0_0 src rgb2dvi_clocks.xdc]
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

if {![file isfile $project_file] || ![file isfile $source_xdc] || ![file isfile $generated_xdc]} {
    error "PROJECT_OR_PINNED_XDC_MISSING"
}
file mkdir $evidence
puts "PROJECT_FILE=$project_file"
puts "PROJECT_SOURCE_XDC=$source_xdc"
puts "PROJECT_GENERATED_XDC=$generated_xdc"
puts "CHANGE_SCOPE=ISOLATED_PROJECT_AND_LOCAL_IP_REPO_COPY_ONLY_NO_BOARD_ACCESS"
open_project $project_file
update_ip_catalog

foreach path [list $source_xdc $generated_xdc] {
    if {[string first $bad_line [read_binary $path]] >= 0} {
        error "BAD_GENERATED_CLOCK_REMAINS_BEFORE_GENERATION=$path"
    }
}
set bd_file [require_one [get_files -all -quiet *design_1.bd] BLOCK_DESIGN]
puts "BLOCK_DESIGN=$bd_file"
generate_target all $bd_file
update_compile_order -fileset sources_1
foreach path [list $source_xdc $generated_xdc] {
    if {![file isfile $path]} {error "XDC_DISAPPEARED_AFTER_GENERATION=$path"}
    if {[string first $bad_line [read_binary $path]] >= 0} {
        error "BAD_GENERATED_CLOCK_REGENERATED=$path"
    }
}
puts "IP_TARGET_GENERATION=COMPLETE_BOTH_SOURCE_AND_GENERATED_XDC_CLEAN"

reset_run impl_1
reset_run synth_1
launch_runs synth_1 -jobs 4
wait_on_run synth_1
set synth_run [get_runs synth_1]
set synth_status [get_property STATUS $synth_run]
set synth_progress [get_property PROGRESS $synth_run]
puts "SYNTHESIS_STATUS=$synth_status"
puts "SYNTHESIS_PROGRESS=$synth_progress"
if {$synth_progress ne "100%" || [string first "Complete" $synth_status] < 0} {
    error "SYNTHESIS_NOT_COMPLETE"
}

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
set exported_xdc [file join $evidence constraints_routed_exported.xdc]
report_methodology -file $method
report_clocks -file $clocks
report_timing_summary -file $timing
report_clock_interaction -file $interactions
report_drc -file $drc
write_xdc -force -exclude_physical -file $exported_xdc

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
puts "ROUTED_CONSTRAINT_EXPORT=$exported_xdc"

if {abs(double($auto_period) - 2.000) > 0.001} {error "SERIAL_AUTO_CLOCK_PERIOD_CHANGED"}
if {$timing36 != 0 || $timing30 != 0} {error "TIMING36_OR_TIMING30_REMAINS"}
if {[string first $bad_line [read_binary $exported_xdc]] >= 0} {
    error "BAD_GENERATED_CLOCK_PRESENT_IN_ROUTED_CONSTRAINT_EXPORT"
}
puts "PROJECT_IMPL_DIAGNOSTIC_RESULT=PASS_FULL_SYNTH_IMPL_ROUTE_CAPTURED_NO_BOARD_ACCESS"
close_project
