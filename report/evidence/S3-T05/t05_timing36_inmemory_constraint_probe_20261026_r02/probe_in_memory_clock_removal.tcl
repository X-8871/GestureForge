set dcp {D:\codex-worktrees\dbdf\tmp\s3r06\t04_sof_fix_20261020_r01\project\ov5640_single.runs\impl_1\design_1_wrapper_routed.dcp}
set out {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_timing36_inmemory_constraint_probe_20261026_r02}

if {![file isfile $dcp]} {
    puts stderr "DCP 文件不存在：$dcp"
    exit 2
}
file mkdir $out

proc require_one {objects label} {
    if {[llength $objects] != 1} {
        error "${label}_COUNT=[llength $objects]; OBJECTS=$objects"
    }
    return [lindex $objects 0]
}

puts "DCP=$dcp"
puts "DCP_SHA256_EXPECTED=17f75ab751f621aa56fc0eb78d03dd52e7a40f67192ec0b78be2c6197bfd4728"
puts "CHANGE_SCOPE=IN_MEMORY_ONLY_DELETE_ONE_GENERATED_CLOCK_OBJECT_NO_WRITEBACK"
open_checkpoint $dcp

set all_clocks [get_clocks -quiet *]
set bad_clock_candidates {}
foreach clock $all_clocks {
    if {[get_property NAME $clock] eq "design_1_i/rgb2dvi_0/U0/SerialClk"} {
        lappend bad_clock_candidates $clock
    }
}
set bad_clock [require_one $bad_clock_candidates BAD_GENERATED_CLOCK]
set serial_pins [get_pins -hier -quiet -filter {NAME =~ *rgb2dvi_0/SerialClk}]
set serial_pin_candidates {}
foreach pin $serial_pins {
    if {[get_property NAME $pin] eq "design_1_i/rgb2dvi_0/SerialClk"} {
        lappend serial_pin_candidates $pin
    }
}
set serial_pin [require_one $serial_pin_candidates SERIAL_CLOCK_PIN]

set serial_before [get_clocks -quiet -of_objects $serial_pin]
puts "BAD_CLOCK=$bad_clock MASTER_CLOCK=[get_property MASTER_CLOCK $bad_clock] PERIOD=[get_property PERIOD $bad_clock]"
puts "SERIAL_PORT_PIN=$serial_pin CLOCKS_BEFORE=$serial_before"
if {[lsearch -exact $serial_before I] < 0} {
    error "EXPECTED_AUTO_DERIVED_2NS_CLOCK_I_NOT_PRESENT_BEFORE_CHANGE"
}

set delete_command [info commands delete_clocks]
puts "DELETE_CLOCKS_COMMAND_COUNT=[llength $delete_command]"
if {[llength $delete_command] != 1} {
    close_design
    puts stderr "VIVADO_DELETE_CLOCKS_COMMAND_UNAVAILABLE"
    exit 4
}
if {[catch {delete_clocks $bad_clock} delete_error]} {
    puts stderr "DELETE_CLOCKS_FAILED=$delete_error"
    close_design
    exit 3
}

set clocks_after [get_clocks -quiet *]
set bad_clock_after {}
foreach clock $clocks_after {
    if {[get_property NAME $clock] eq "design_1_i/rgb2dvi_0/U0/SerialClk"} {
        lappend bad_clock_after $clock
    }
}
set serial_after [get_clocks -quiet -of_objects $serial_pin]
puts "CLOCK_COUNT_AFTER=[llength $clocks_after]"
puts "BAD_CLOCK_PRESENT_AFTER=[expr {[llength $bad_clock_after] != 0}]"
puts "SERIAL_PORT_PIN=$serial_pin CLOCKS_AFTER=$serial_after"
if {[llength $bad_clock_after] != 0} {
    error "BAD_GENERATED_CLOCK_REMAINS_AFTER_DELETE"
}
set retained_clock [require_one $serial_after RETAINED_SERIAL_CLOCK]
set retained_period [get_property PERIOD $retained_clock]
puts "RETAINED_CLOCK=$retained_clock PERIOD=$retained_period"
if {$retained_clock ne "I" || abs(double($retained_period) - 2.000) > 0.001} {
    error "RETAINED_SERIAL_CLOCK_NOT_EXPECTED_2NS_AUTO_DERIVED_I"
}

report_clocks -file [file join $out clocks_after.rpt]
report_methodology -file [file join $out methodology_after.rpt]
close_design
puts "IN_MEMORY_DIAGNOSTIC_RESULT=PASS_CLOCK_I_RETAINED_NO_WRITEBACK"
