# 复位探针配置已保存；修正 FILE_NAME 返回相对名造成的归档失败，只读重新验证。
set repo_root {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set run_dir [file join $repo_root tmp/2B/S2B-T08/ip_probe_20261009_r01]
set evidence_dir [file join $repo_root report/evidence/S2B-T08/ip_probe_20261009_r01]
set bd_path [file join $run_dir project/s2b_ps_candidate.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
if {![file isfile $bd_path]} {error "ARCHIVE_SOURCE_MISSING:$bd_path"}
open_project [file join $run_dir project/s2b_ps_candidate.xpr]
open_bd_design $bd_path
source -notrace {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set ::ipcfg::native_log_path [file join $run_dir batch/archive_probe_vivado.log]
set receipt [ipcfg::capture [file join $evidence_dir archive_validate.tcldict] {validate_bd_design; set result "ARCHIVE_VALIDATE:OK"} {ARCHIVE_VALIDATE:OK}]
puts $receipt
if {[dict get $receipt status] ne "OK"} {error "ARCHIVE_VALIDATE_FAIL"}
file copy $bd_path [file join $evidence_dir validated_probe.bd]
file copy [file join $run_dir project/.ipcfg/attempts.tcldict] [file join $evidence_dir attempts_final.tcldict]
close_project
puts "ARCHIVE_PROBE:OK"
