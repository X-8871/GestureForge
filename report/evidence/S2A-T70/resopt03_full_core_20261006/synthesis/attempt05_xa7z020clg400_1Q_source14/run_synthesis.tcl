set repo_root {D:\FPGA_Competition\report\evidence\S2A-T70\resopt03_full_core_20261006\source_full_core_14src}
set evidence_dir {D:\FPGA_Competition\report\evidence\S2A-T70\resopt03_full_core_20261006\synthesis\attempt05_xa7z020clg400_1Q_source14}
set part_name {xa7z020clg400-1Q}
set part_objects [get_parts -quiet $part_name]
if {[llength $part_objects] != 1} {
    puts stderr "S2A_PRECHECK_FAILED_PART=$part_name matches=[llength $part_objects]"
    flush stderr
    exit 1
}
set resolved_part [get_property NAME [lindex $part_objects 0]]
puts "xa7z020clg400-1Q=$resolved_part"
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
    [file join $repo_root src s2a_control_csr.sv] \
    [file join $repo_root src s2a_runtime_shell.sv] \
    [file join $repo_root src s2a_stage2a_core_ooc.sv]]
foreach source $rtl_files {
    if {![file isfile $source]} {
        puts stderr "S2A_PRECHECK_FAILED_SOURCE_MISSING=$source"
        flush stderr
        exit 1
    }
    puts "RTL_SOURCE=$source"
    if {[catch {read_verilog -sv $source} message]} {
        puts stderr "S2A_READ_VERILOG_FAILED source=$source message=$message"
        flush stderr
        exit 1
    }
}
set synth_status [catch {synth_design -top s2a_stage2a_core_ooc -part $part_name -mode out_of_context -flatten_hierarchy none} synth_message]
if {$synth_status != 0} {
    puts stderr "S2A_SYNTHESIS_FAILED=$synth_message"
    flush stderr
    exit 1
}
foreach report_cmd [list \
    [list report_utilization -file [file join $evidence_dir utilization.rpt]] \
    [list report_utilization -hierarchical -hierarchical_min_primitive_count 0 -file [file join $evidence_dir utilization_hierarchical.rpt]] \
    [list report_timing_summary -report_unconstrained -file [file join $evidence_dir timing_summary.rpt]] \
    [list report_clocks -file [file join $evidence_dir clocks.rpt]] \
    [list report_timing -delay_type max -max_paths 20 -file [file join $evidence_dir worst_paths.rpt]]] {
    if {[catch {uplevel #0 $report_cmd} message]} {
        puts stderr "S2A_REPORT_FAILED command=$report_cmd message=$message"
        flush stderr
        exit 1
    }
}
set latch_cells [concat [get_cells -hierarchical -filter {REF_NAME == LDCE}] [get_cells -hierarchical -filter {REF_NAME == LDPE}]]
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
puts $summary_file "Source manifest: [file join $repo_root source_manifest.json]"
puts $summary_file "Source manifest SHA-256: d8446dd1da6bafd85de3410bff876512568dc5c7e47f4d20362f05758399483d"
puts $summary_file "RTL source count: [llength $rtl_files]"
puts $summary_file "LDCE/LDPE latch cell count: $latch_count"
puts $summary_file "Timing summary: report_unconstrained enabled; no Stage 2A target period is frozen."
puts $summary_file "Clock constraints: none; no timing closure claim is made."
close $summary_file
if {[catch {write_checkpoint -force [file join $evidence_dir s2a_stage2a_core_ooc_post_synth.dcp]} message]} {
    puts stderr "S2A_CHECKPOINT_FAILED=$message"
    flush stderr
    exit 1
}
if {$latch_count > 0} {
    puts stderr "S2A_UNEXPECTED_LATCH_COUNT=$latch_count"
    flush stderr
    exit 2
}
puts "SYNTHESIS_COMPLETED=1 part=$resolved_part rtl_source_count=[llength $rtl_files] latch_count=$latch_count"
flush stdout
exit 0