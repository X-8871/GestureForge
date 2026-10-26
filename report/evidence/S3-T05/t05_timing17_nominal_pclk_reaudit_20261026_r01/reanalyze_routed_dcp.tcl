# 只对既有 routed DCP 重新应用名义 CMOS1 PCLK 时钟并生成只读时序报告。
# 不综合、实现、改写 DCP、生成 bitstream 或连接硬件。

set routed_dcp {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_timing36_project_impl_20261026_r02\outputs\design_1_wrapper_routed.dcp}
set stage3_xdc {D:\codex-worktrees\dbdf\board\stage3\hardware\an5642_j11_cmos2.xdc}
set evidence_dir {D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_timing17_nominal_pclk_reaudit_20261026_r01}

foreach path [list $routed_dcp $stage3_xdc] {
    if {![file isfile $path]} {error "INPUT_FILE_MISSING=$path"}
}

open_checkpoint $routed_dcp
read_xdc $stage3_xdc
update_timing

set pclk_port [get_ports -quiet {cmos1_pclk}]
if {[llength $pclk_port] != 1} {error "CMOS1_PCLK_PORT_COUNT=[llength $pclk_port]"}
set pclk_clocks [get_clocks -quiet -of_objects $pclk_port]
if {[llength $pclk_clocks] != 1} {error "CMOS1_PCLK_CLOCK_COUNT=[llength $pclk_clocks]"}
set pclk_clock [lindex $pclk_clocks 0]
set pclk_period [get_property PERIOD $pclk_clock]
if {abs(double($pclk_period) - 11.904762) > 0.00001} {
    error "CMOS1_PCLK_PERIOD_MISMATCH=$pclk_period"
}

report_clocks -file [file join $evidence_dir clocks_after_candidate.xdc.rpt]
report_methodology -file [file join $evidence_dir methodology_after_candidate.xdc.rpt]
report_timing_summary -file [file join $evidence_dir timing_summary_after_candidate.xdc.rpt]
report_clock_interaction -file [file join $evidence_dir clock_interaction_after_candidate.xdc.rpt]

puts "CMOS1_PCLK_PORT=$pclk_port"
puts "CMOS1_PCLK_CLOCK=$pclk_clock"
puts "CMOS1_PCLK_PERIOD_NS=$pclk_period"
puts "TIMING_REANALYSIS=COMPLETE"
close_design
exit 0
