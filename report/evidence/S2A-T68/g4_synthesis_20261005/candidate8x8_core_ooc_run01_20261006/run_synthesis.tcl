set repo_root {D:\FPGA_Competition}
set evidence_dir {D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\candidate8x8_core_ooc_run01_20261006}
set expected_commit {999238284157bed77cdb3a37e3e6eea52daeefc4}
set expected_tree {b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67}
set top_name {s2a_stage2a_core_ooc}
set part_name {xa7z020clg400-1I}
set_param general.maxThreads 2
set part_objects [get_parts -quiet $part_name]
if {[llength $part_objects] != 1} { error "Expected one part $part_name; found [llength $part_objects]" }
set resolved_part [get_property NAME [lindex $part_objects 0]]
puts "CANDIDATE_COMMIT=$expected_commit"
puts "CANDIDATE_TREE=$expected_tree"
puts "TOP=$top_name"
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
{D:\FPGA_Competition\src\s2a_memory_master.sv}
{D:\FPGA_Competition\src\s2a_runtime_shell.sv}
{D:\FPGA_Competition\src\s2a_stage2a_core_ooc.sv}
{D:\FPGA_Competition\src\s2a_control_csr.sv}
}
foreach source $rtl_files {
    if {![file isfile $source]} { error "RTL source is missing: $source" }
    puts "RTL_SOURCE=$source"
    if {[catch {read_verilog -sv $source} message]} {
        puts stderr "S2A_READ_VERILOG_FAILED source=$source message=$message"
        exit 1
    }
}
set synth_status [catch {synth_design -top $top_name -part $part_name -mode out_of_context -flatten_hierarchy none} synth_message]
if {$synth_status != 0} {
    puts stderr "S2A_SYNTHESIS_FAILED message=$synth_message"
    exit 1
}
set report_status 0
foreach report_cmd [list \
    [list report_utilization -file [file join $evidence_dir utilization.rpt]] \
    [list report_utilization -hierarchical -hierarchical_min_primitive_count 0 -file [file join $evidence_dir utilization_hierarchical.rpt]] \
    [list report_timing_summary -report_unconstrained -file [file join $evidence_dir timing_summary.rpt]] \
    [list report_clocks -file [file join $evidence_dir clocks.rpt]] \
    [list report_timing -delay_type max -max_paths 20 -file [file join $evidence_dir worst_paths.rpt]]] {
    if {[catch {uplevel #0 $report_cmd} message]} {
        puts stderr "S2A_REPORT_FAILED command=$report_cmd message=$message"
        set report_status 1
    }
}
set ldce_cells [get_cells -hierarchical -filter {REF_NAME == LDCE}]
set ldpe_cells [get_cells -hierarchical -filter {REF_NAME == LDPE}]
set latch_cells [concat $ldce_cells $ldpe_cells]
set latch_count [llength $latch_cells]
set latch_file [open [file join $evidence_dir latch_cells.txt] w]
foreach cell $latch_cells { puts $latch_file [get_property NAME $cell] }
close $latch_file
set summary_file [open [file join $evidence_dir synthesis_summary.txt] w]
fconfigure $summary_file -encoding utf-8
puts $summary_file "Top: $top_name"
puts $summary_file "Part: $resolved_part"
puts $summary_file "Candidate commit: $expected_commit"
puts $summary_file "Candidate tree: $expected_tree"
puts $summary_file "RTL source count: [llength $rtl_files]"
puts $summary_file "LDCE/LDPE latch cell count: $latch_count"
puts $summary_file "Clock constraints: none; no Stage 2A target period is frozen; timing reports are risk evidence only."
puts $summary_file "Maximum Vivado threads: [get_param general.maxThreads]"
puts $summary_file "Report generation failure count: $report_status"
close $summary_file
write_checkpoint -force [file join $evidence_dir s2a_stage2a_core_ooc_post_synth.dcp]
if {$latch_count > 0 || $report_status > 0} { exit 1 }
exit 0