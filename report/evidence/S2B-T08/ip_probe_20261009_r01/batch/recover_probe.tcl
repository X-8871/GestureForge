# 恢复 S2B-T08 探针工程，只读核对磁盘中的 BD 状态。
set repo_root {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set run_dir [file join $repo_root tmp/2B/S2B-T08/ip_probe_20261009_r01]
set evidence_dir [file join $repo_root report/evidence/S2B-T08/ip_probe_20261009_r01]
set helper {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set project_path [file join $run_dir project/s2b_ps_candidate.xpr]
set bd_path [file join $run_dir project/s2b_ps_candidate.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
set native_log [file join $run_dir batch/recover_probe_vivado.log]

proc write_text {path text} {
    set f [open $path w]
    fconfigure $f -encoding utf-8 -translation lf
    puts -nonewline $f $text
    close $f
}

open_project $project_path
open_bd_design $bd_path
source -notrace $helper
set ::ipcfg::native_log_path $native_log

set cells [get_bd_cells -quiet]
set ps7_count [llength [get_bd_cells -quiet ps7]]
set defaults_count [llength [get_bd_cells -quiet ps_defaults]]
set current_bd [current_bd_design]
set part [get_property PART [current_project]]
set result [dict create \
    schema_version 1 \
    status RECOVERED \
    project_path $project_path \
    bd_path $bd_path \
    current_bd $current_bd \
    part $part \
    cells $cells \
    ps7_count $ps7_count \
    ps_defaults_count $defaults_count \
    helper_loaded [expr {[llength [info commands ipcfg::write_evidence]] > 0}] \
    native_log_path $native_log \
]
write_text [file join $evidence_dir recover_status.tcldict] $result
puts "RECOVER_STATUS:ps7=$ps7_count defaults=$defaults_count part=$part cells=[llength $cells]"
close_project
