set repo_root {D:\FPGA_Competition}
set evidence_dir {D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local01}
set part_name {xc7z020clg400-1}
set part_objects [get_parts -quiet $part_name]
if {[llength $part_objects] != 1} {
    error "Expected one matching part for $part_name; found [llength $part_objects]"
}
set resolved_part [get_property NAME [lindex $part_objects 0]]
puts "PART_NAME=$resolved_part"
set rtl_files {}
lappend rtl_files [file join $repo_root src s2a_network_descriptor_pkg.sv]
lappend rtl_files [file join $repo_root src int8_maxpool_geometry.sv]
lappend rtl_files [file join $repo_root src int8_maxpool_window.sv]
lappend rtl_files [file join $repo_root src int8_route_query.sv]
lappend rtl_files [file join $repo_root src int8_upsample_query.sv]
lappend rtl_files [file join $repo_root src s2a_conv_tile_engine.sv]
lappend rtl_files [file join $repo_root src s2a_maxpool_engine.sv]
lappend rtl_files [file join $repo_root src s2a_route_engine.sv]
lappend rtl_files [file join $repo_root src s2a_upsample_engine.sv]
lappend rtl_files [file join $repo_root src s2a_network_backend.sv]
foreach source $rtl_files {
    if {![file isfile $source]} {
        error "RTL source is missing: $source"
    }
    puts "RTL_SOURCE=$source"
    read_verilog -sv $source
}
synth_design -top s2a_network_backend -part $part_name -flatten_hierarchy none
report_utilization -file [file join $evidence_dir utilization.rpt]
set timing_status [catch {report_timing_summary -file [file join $evidence_dir timing_summary.rpt]} timing_message]
set clocks_status [catch {report_clocks -file [file join $evidence_dir clocks.rpt]} clocks_message]
set ldce_cells [get_cells -hierarchical -filter {REF_NAME == LDCE}]
set ldpe_cells [get_cells -hierarchical -filter {REF_NAME == LDPE}]
set latch_cells [concat $ldce_cells $ldpe_cells]
set latch_count [llength $latch_cells]
set latch_file [open [file join $evidence_dir latch_cells.txt] w]
foreach cell $latch_cells {
    puts $latch_file [get_property NAME $cell]
}
close $latch_file
set summary_file [open [file join $evidence_dir synthesis_summary.txt] w]
fconfigure $summary_file -encoding utf-8
puts $summary_file "Top: s2a_network_backend"
puts $summary_file "Part: $resolved_part"
puts $summary_file "Frozen source baseline: fecbf1f8f37fcee8b25e6e2517b9621850912a4e"
puts $summary_file "RTL source count: [llength $rtl_files]"
puts $summary_file "LDCE/LDPE latch cell count: $latch_count"
puts $summary_file "Timing summary return code: $timing_status"
puts $summary_file "Timing summary message: $timing_message"
puts $summary_file "Clock report return code: $clocks_status"
puts $summary_file "Clock report message: $clocks_message"
puts $summary_file "Clock constraints: none added; no frozen target period exists."
close $summary_file
write_checkpoint -force [file join $evidence_dir s2a_network_backend_post_synth.dcp]
if {$latch_count > 0} {
    error "Unexpected latch cells were inferred: $latch_count"
}
exit 0