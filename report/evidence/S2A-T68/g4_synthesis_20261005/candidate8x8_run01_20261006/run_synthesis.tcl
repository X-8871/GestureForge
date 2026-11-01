set repo_root {D:\FPGA_Competition}
set evidence_dir {D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\candidate8x8_run01_20261006}
set expected_commit {999238284157bed77cdb3a37e3e6eea52daeefc4}
set expected_tree {b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67}
set part_name {xc7z020clg400-1}
set_param general.maxThreads 2
set part_objects [get_parts -quiet $part_name]
if {[llength $part_objects] != 1} { error "Expected one part $part_name; found [llength $part_objects]" }
set resolved_part [get_property NAME [lindex $part_objects 0]]
puts "CANDIDATE_COMMIT=$expected_commit"
puts "CANDIDATE_TREE=$expected_tree"
puts "PART_NAME=$resolved_part"
puts "MAX_THREADS=[get_param general.maxThreads]"
set rtl_files {
{D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv}
{D:\FPGA_Competition\src\int8_maxpool_geometry.sv}
{D:\FPGA_Competition\src\int8_maxpool_window.sv}
{D:\FPGA_Competition\src\int8_route_query.sv}
{D:\FPGA_Competition\src\int8_upsample_query.sv}
{D:\FPGA_Competition\src\s2a_conv_tile_engine.sv}
{D:\FPGA_Competition\src\s2a_maxpool_engine.sv}
{D:\FPGA_Competition\src\s2a_route_engine.sv}
{D:\FPGA_Competition\src\s2a_upsample_engine.sv}
{D:\FPGA_Competition\src\s2a_network_backend.sv}
}
foreach source $rtl_files {
    if {![file isfile $source]} { error "RTL source is missing: $source" }
    puts "RTL_SOURCE=$source"
    read_verilog -sv $source
}
synth_design -top s2a_network_backend -part $part_name -flatten_hierarchy none
report_utilization -file [file join $evidence_dir utilization.rpt]
report_utilization -hierarchical -file [file join $evidence_dir utilization_hierarchical.rpt]
report_timing_summary -file [file join $evidence_dir timing_summary.rpt]
report_clocks -file [file join $evidence_dir clocks.rpt]
set ldce_cells [get_cells -hierarchical -filter {REF_NAME == LDCE}]
set ldpe_cells [get_cells -hierarchical -filter {REF_NAME == LDPE}]
set latch_cells [concat $ldce_cells $ldpe_cells]
set latch_count [llength $latch_cells]
set latch_file [open [file join $evidence_dir latch_cells.txt] w]
foreach cell $latch_cells { puts $latch_file [get_property NAME $cell] }
close $latch_file
set summary_file [open [file join $evidence_dir synthesis_summary.txt] w]
fconfigure $summary_file -encoding utf-8
puts $summary_file "Top: s2a_network_backend"
puts $summary_file "Part: $resolved_part"
puts $summary_file "Candidate commit: $expected_commit"
puts $summary_file "Candidate tree: $expected_tree"
puts $summary_file "RTL source count: [llength $rtl_files]"
puts $summary_file "LDCE/LDPE latch cell count: $latch_count"
puts $summary_file "Clock constraints: none; no frozen target period exists; timing reports are risk information only."
puts $summary_file "Maximum Vivado threads: [get_param general.maxThreads]"
close $summary_file
write_checkpoint -force [file join $evidence_dir s2a_network_backend_post_synth.dcp]
if {$latch_count > 0} { error "Unexpected latch cells were inferred: $latch_count" }
exit 0