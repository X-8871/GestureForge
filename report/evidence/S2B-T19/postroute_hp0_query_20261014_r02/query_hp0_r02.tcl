set output_path {C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T19\postroute_hp0_query_20261014_r02\query_output.tcldict}
set fp [open $output_path w]
set run [get_runs impl_1]
puts $fp [list record project_identity project [current_project] design [current_design] run_status [get_property STATUS $run] run_directory [get_property DIRECTORY $run] part [get_property PART [current_project]]]
set ps [get_cells -hierarchical -filter {REF_NAME == PS7}]
if {[llength $ps] != 1} {close $fp; error "期望一个PS7单元，实际数量=[llength $ps]"}
set hp [get_pins -of_objects $ps -filter {REF_PIN_NAME =~ SAXIHP0*}]
set required_unconnected {}
set aux_unconnected {}
set cache_rows {}
set cache_count 0
foreach p $hp {
    set ref [get_property REF_PIN_NAME $p]
    set dir [get_property DIRECTION $p]
    set nets [get_nets -quiet -segments -of_objects $p]
    if {[llength $nets] == 0} {
        if {$dir eq "OUT" && [regexp {^SAXIHP0(ARESETN|RACOUNT|RCOUNT|WACOUNT|WCOUNT)(\[[0-9]+\])?$} $ref]} {
            lappend aux_unconnected $ref
        } else {
            lappend required_unconnected $ref
        }
    }
    if {[regexp {(ARCACHE|AWCACHE)} $ref]} {
        incr cache_count
        set drivers {}
        foreach lp [get_pins -quiet -leaf -of_objects $nets] {
            if {[get_property DIRECTION $lp] eq "OUT"} {
                set c [get_cells -quiet -of_objects $lp]
                if {[get_property REF_NAME $c] in {GND VCC}} {
                    lappend drivers [list $ref [get_property REF_NAME $c] [get_property NAME $lp]]
                }
            }
        }
        lappend cache_rows [list $ref $dir [llength $nets] $drivers]
    }
}
puts $fp [list record hp0_inventory ps7_cells [llength $ps] hp0_pin_count [llength $hp] required_unconnected_count [llength $required_unconnected] required_unconnected $required_unconnected aux_unconnected_count [llength $aux_unconnected] aux_unconnected $aux_unconnected axcache_count $cache_count axcache_rows $cache_rows]
set signal_rows {}
foreach sig {ARVALID ARREADY AWVALID AWREADY WVALID WREADY BVALID BREADY RVALID RREADY} {
    set pinname [format {SAXIHP0%s} $sig]
    set pins [get_pins -quiet -of_objects $ps -filter [format {REF_PIN_NAME == %s} $pinname]]
    set one {}
    foreach p $pins {
        set nets [get_nets -quiet -segments -of_objects $p]
        set leaf_pins [get_pins -quiet -leaf -of_objects $nets]
        set ends {}
        foreach lp $leaf_pins {
            set c [get_cells -quiet -of_objects $lp]
            set cn [get_property NAME $c]
            set cr [get_property REF_NAME $c]
            if {$cr eq "PS7" || [string first "adapter" $cn] >= 0} {
                lappend ends [list $cn [get_property REF_PIN_NAME $lp] $cr]
            }
        }
        lappend one [list signal $pinname direction [get_property DIRECTION $p] pin_count [llength $pins] segment_count [llength $nets] leaf_endpoint_count [llength $leaf_pins] relevant_endpoints $ends]
    }
    lappend signal_rows $one
}
puts $fp [list record hp0_handshakes signals $signal_rows]
close $fp
puts [list query_output $output_path ps7_cells [llength $ps] hp0_pin_count [llength $hp] required_unconnected_count [llength $required_unconnected] aux_unconnected_count [llength $aux_unconnected] axcache_count $cache_count]
