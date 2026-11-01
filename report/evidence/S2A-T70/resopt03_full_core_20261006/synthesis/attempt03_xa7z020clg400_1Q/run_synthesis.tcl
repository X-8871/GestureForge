set repo_root {D:\FPGA_Competition\report\evidence\S2A-T70\resopt03_full_core_20261006\source}
set evidence_dir {D:\FPGA_Competition\report\evidence\S2A-T70\resopt03_full_core_20261006\synthesis\attempt03_xa7z020clg400_1Q}
set part_name {xa7z020clg400-1Q}
set part_objects [get_parts -quiet $part_name]
if {[llength $part_objects] != 1} {
    error "Expected one matching part for $part_name; found [llength $part_objects]"
}
set resolved_part [get_property NAME [lindex $part_objects 0]]
puts "PART_NAME=$resolved_part"
set rtl_files [list \
    [file join $repo_root src s2a_network_descriptor_pkg.sv] \
    [file join $repo_root src int8_maxpool_geometry.sv] \
    [file join $repo_root src int8_maxpool_window.sv] \
    [file join $repo_root src int8_route_query.sv] \
    [file join $repo_root src int8_upsample_query.sv] \
    [file join $repo_root src s2a_conv_tile_engine.sv] \
    [file join $repo_root src s2a_maxpool_engine.sv] \
    [file join $repo_root src s2a_route_engine.sv] \
    [file join $repo_root src s2a_upsample_engine.sv] \
    [file join $repo_root src s2a_network_backend.sv] \
    [file join $repo_root src s2a_memory_master.sv] \
    [file join $repo_root src s2a_runtime_shell.sv] \
    [file join $repo_root src s2a_stage2a_core_ooc.sv]]
foreach source $rtl_files {
    if {![file isfile $source]} {
        error "RTL source is missing: $source"
    }
    puts "RTL_SOURCE=$source"
    read_verilog -sv $source
}
synth_design -top s2a_stage2a_core_ooc -part $part_name -mode out_of_context -flatten_hierarchy none
report_utilization -file [file join $evidence_dir utilization.rpt]
report_utilization -hierarchical -hierarchical_min_primitive_count 0 -file [file join $evidence_dir utilization_hierarchical.rpt]
set timing_status [catch {report_timing_summary -file [file join $evidence_dir timing_summary.rpt]} timing_message]
set clocks_status [catch {report_clocks -file [file join $evidence_dir clocks.rpt]} clocks_message]
set path_status [catch {report_timing -delay_type max -max_paths 20 -file [file join $evidence_dir worst_paths.rpt]} path_message]
set ldce_cells [get_cells -hierarchical -filter {REF_NAME == LDCE}]
set ldpe_cells [get_cells -hierarchical -filter {REF_NAME == LDPE}]
set latch_cells [concat $ldce_cells $ldpe_cells]
set latch_count [llength $latch_cells]
set latch_file [open [file join $evidence_dir latch_cells.txt] w]
fconfigure $latch_file -encoding utf-8
foreach cell $latch_cells {
    puts $latch_file [get_property NAME $cell]
}
close $latch_file
set summary_file [open [file join $evidence_dir synthesis_summary.txt] w]
fconfigure $summary_file -encoding utf-8
puts $summary_file "Top: s2a_stage2a_core_ooc"
puts $summary_file "Part: $resolved_part"
puts $summary_file "Candidate base commit: ce2637133034606055c99648c5656b464c070705"
puts $summary_file "Candidate engine SHA-256: 0a29e752c640f81c698327f5e78a4ff12839d1b906f7de87953cea88b3abfdef"
puts $summary_file "Source closure manifest: ../source_manifest.json"
puts $summary_file "RTL source count: [llength $rtl_files]"
puts $summary_file "LDCE/LDPE latch cell count: $latch_count"
puts $summary_file "Timing summary return code: $timing_status"
puts $summary_file "Timing summary message: $timing_message"
puts $summary_file "Clock report return code: $clocks_status"
puts $summary_file "Clock report message: $clocks_message"
puts $summary_file "Worst-path report return code: $path_status"
puts $summary_file "Worst-path report message: $path_message"
puts $summary_file "Clock constraints: none; no Stage 2A target period is frozen. No timing closure claim is made."
close $summary_file
write_checkpoint -force [file join $evidence_dir s2a_stage2a_core_ooc_post_synth.dcp]
if {$latch_count > 0} {
    error "Unexpected latch cells were inferred: $latch_count"
}
exit 0
