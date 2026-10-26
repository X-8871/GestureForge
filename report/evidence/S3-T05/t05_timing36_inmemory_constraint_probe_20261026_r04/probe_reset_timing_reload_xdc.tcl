set dcp {D:\codex-worktrees\dbdf\tmp\s3r06\t04_sof_fix_20261020_r01\project\ov5640_single.runs\impl_1\design_1_wrapper_routed.dcp}
set source_xdc {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_dcp_readonly_20261024_r01\v3_constraints_exported.xdc}
set evidence {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_timing36_inmemory_constraint_probe_20261026_r04}

proc read_binary {path} {
    set stream [open $path r]
    fconfigure $stream -translation binary -encoding binary
    set value [read $stream]
    close $stream
    return $value
}

proc write_binary {path value} {
    set stream [open $path wb]
    fconfigure $stream -translation binary -encoding binary
    puts -nonewline $stream $value
    close $stream
}

proc count_exact {text needle} {
    set count 0
    set start 0
    while {1} {
        set index [string first $needle $text $start]
        if {$index < 0} {break}
        incr count
        set start [expr {$index + [string length $needle]}]
    }
    return $count
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

proc exact_clock_by_name {name} {
    set matches {}
    foreach clock [get_clocks -quiet *] {
        if {[get_property NAME $clock] eq $name} {lappend matches $clock}
    }
    return $matches
}

if {![file isfile $dcp] || ![file isfile $source_xdc]} {
    error "PINNED_DCP_OR_SOURCE_XDC_MISSING"
}
file mkdir $evidence
set source_text [read_binary $source_xdc]
set bad_line {create_generated_clock -source [get_ports -scoped_to_current_instance PixelClk] -multiply_by 5 [get_ports -scoped_to_current_instance SerialClk]}
set bad_line_count [count_exact $source_text $bad_line]
if {$bad_line_count != 1} {
    error "EXPECTED_ONE_BAD_GENERATED_CLOCK_LINE_GOT_$bad_line_count"
}
set candidate_text [string map [list $bad_line {}] $source_text]
if {[count_exact $candidate_text $bad_line] != 0} {
    error "BAD_GENERATED_CLOCK_LINE_REMAINS_IN_CANDIDATE"
}
set candidate_xdc [file join $evidence constraints_without_rgb2dvi_serial_generated_clock.xdc]
write_binary $candidate_xdc $candidate_text

puts "DCP=$dcp"
puts "SOURCE_XDC=$source_xdc"
puts "BAD_GENERATED_CLOCK_LINE_COUNT=$bad_line_count"
puts "CHANGE_SCOPE=RESET_AND_RELOAD_IN_MEMORY_TIMING_CONSTRAINTS_FROM_EXPORTED_XDC_WITH_ONE_LINE_OMITTED_NO_CHECKPOINT_WRITEBACK"
open_checkpoint $dcp

set method_before [file join $evidence methodology_before.rpt]
report_methodology -file $method_before
set timing36_before [methodology_rule_count $method_before 36]
set timing30_before [methodology_rule_count $method_before 30]
set timing17_before [methodology_rule_count $method_before 17]
set timing18_before [methodology_rule_count $method_before 18]
puts "METHODOLOGY_BEFORE_TIMING36=$timing36_before TIMING30=$timing30_before TIMING17=$timing17_before TIMING18=$timing18_before"
report_clocks -file [file join $evidence clocks_before.rpt]

if {[catch {reset_timing} reset_error]} {
    error "RESET_TIMING_FAILED=$reset_error"
}
puts "CLOCK_COUNT_AFTER_RESET=[llength [get_clocks -quiet *]]"
if {[catch {read_xdc $candidate_xdc} read_error]} {
    error "READ_XDC_FAILED=$read_error"
}
update_timing

set serial_pin_candidates {}
foreach pin [get_pins -hier -quiet -filter {NAME =~ *rgb2dvi_0/SerialClk}] {
    if {[get_property NAME $pin] eq "design_1_i/rgb2dvi_0/SerialClk"} {
        lappend serial_pin_candidates $pin
    }
}
set serial_pin [require_one $serial_pin_candidates SERIAL_CLOCK_PIN]
set serial_clocks [get_clocks -quiet -of_objects $serial_pin]
set removed_clock [exact_clock_by_name {design_1_i/rgb2dvi_0/U0/SerialClk}]
set auto_clock_candidates {}
foreach clock $serial_clocks {
    if {[get_property NAME $clock] eq "I"} {lappend auto_clock_candidates $clock}
}
set auto_clock [require_one $auto_clock_candidates AUTO_DERIVED_SERIAL_CLOCK_I]
set auto_period [get_property PERIOD $auto_clock]
puts "SERIAL_PORT_PIN=$serial_pin CLOCKS_AFTER=$serial_clocks"
puts "BAD_GENERATED_CLOCK_COUNT_AFTER=[llength $removed_clock]"
puts "RETAINED_AUTO_CLOCK=$auto_clock PERIOD=$auto_period"

report_clocks -file [file join $evidence clocks_after.rpt]
set method_after [file join $evidence methodology_after.rpt]
report_methodology -file $method_after
set timing36_after [methodology_rule_count $method_after 36]
set timing30_after [methodology_rule_count $method_after 30]
set timing17_after [methodology_rule_count $method_after 17]
set timing18_after [methodology_rule_count $method_after 18]
puts "METHODOLOGY_AFTER_TIMING36=$timing36_after TIMING30=$timing30_after TIMING17=$timing17_after TIMING18=$timing18_after"

if {[llength $removed_clock] != 0} {error "BAD_GENERATED_CLOCK_STILL_PRESENT"}
if {abs(double($auto_period) - 2.000) > 0.001} {error "AUTO_DERIVED_SERIAL_CLOCK_PERIOD_CHANGED"}
if {$timing36_before != 1 || $timing30_before != 1 || $timing36_after != 0 || $timing30_after != 0} {
    error "TIMING36_30_SUMMARY_DELTA_NOT_AS_EXPECTED"
}
if {$timing17_before != 240 || $timing17_after != 240 || $timing18_before != 1 || $timing18_after != 1} {
    error "OTHER_METHODOLOGY_SUMMARY_ROWS_CHANGED"
}
close_design
puts "IN_MEMORY_DIAGNOSTIC_RESULT=PASS_WARNING_REMOVED_AUTO_CLOCK_I_RETAINED_NO_WRITEBACK"
