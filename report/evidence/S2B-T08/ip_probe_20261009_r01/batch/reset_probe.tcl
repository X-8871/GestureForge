# 在隔离探针内补齐同域复位同步释放，保留配置、连接及验证原件。
set repo_root {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set run_dir [file join $repo_root tmp/2B/S2B-T08/ip_probe_20261009_r01]
set evidence_dir [file join $repo_root report/evidence/S2B-T08/ip_probe_20261009_r01]
set helper {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
open_project [file join $run_dir project/s2b_ps_candidate.xpr]
open_bd_design [file join $run_dir project/s2b_ps_candidate.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
source -notrace $helper
set ::ipcfg::native_log_path [file join $run_dir batch/reset_probe_vivado.log]
set py_status [ipcfg::python_status]
if {![string match {PYTHON:OK *} $py_status]} {error $py_status}
puts [ipcfg::python_exec -c {import argparse, base64, hashlib, json, pathlib, re, sys, typing; print("PYTHON_IMPORTS:OK")}]
puts [ipcfg::write_evidence [file join $evidence_dir reset_preflight.tcldict] [dict create python $py_status version [version -short]]]
foreach {cell vlnv request} {
    rst_fclk0 xilinx.com:ip:proc_sys_reset {CONFIG.C_EXT_RESET_HIGH 0 CONFIG.C_AUX_RESET_HIGH 1}
    const_zero xilinx.com:ip:xlconstant {CONFIG.CONST_WIDTH 1 CONFIG.CONST_VAL 0}
    const_one xilinx.com:ip:xlconstant {CONFIG.CONST_WIDTH 1 CONFIG.CONST_VAL 1}
} {
    set receipt [ipcfg::capture [file join $evidence_dir ${cell}_config.tcldict] [list ipcfg::create_cell_cfg $vlnv $cell $request] {SUCCESS:}]
    puts $receipt
    if {[dict get $receipt status] ne "OK"} {error "RESET_CONFIG_FAIL:$cell"}
    set stuck [ipcfg::verify_stuck $cell $request]
    if {[llength $stuck]} {error "RESET_READBACK_FAIL:$stuck"}
    puts [ipcfg::write_evidence [file join $evidence_dir ${cell}_readback.tcldict] [dict create request $request readback [ipcfg::snapshot $cell [dict keys $request]]]]
}
disconnect_bd_net [get_bd_nets ps7_FCLK_RESET0_N] [get_bd_pins axi_gp0_lite/aresetn]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins rst_fclk0/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins rst_fclk0/ext_reset_in]
connect_bd_net [get_bd_pins const_zero/dout] [get_bd_pins rst_fclk0/aux_reset_in] [get_bd_pins rst_fclk0/mb_debug_sys_rst]
connect_bd_net [get_bd_pins const_one/dout] [get_bd_pins rst_fclk0/dcm_locked]
connect_bd_net [get_bd_pins rst_fclk0/peripheral_aresetn] [get_bd_pins axi_gp0_lite/aresetn]
set receipt [ipcfg::capture [file join $evidence_dir reset_validate.tcldict] {validate_bd_design; set result "RESET_VALIDATE:OK"} {RESET_VALIDATE:OK}]
puts $receipt
if {[dict get $receipt status] ne "OK"} {error "RESET_VALIDATE_FAIL"}
save_bd_design
set readback [dict create part [get_property PART [current_project]] cells [get_bd_cells] nets {} addresses {}]
foreach net [get_bd_nets] {
    dict set readback nets $net [get_bd_pins -of_objects $net]
}
foreach seg [get_bd_addr_segs] {
    dict set readback addresses $seg [list OFFSET [get_property OFFSET $seg] RANGE [get_property RANGE $seg]]
}
puts [ipcfg::write_evidence [file join $evidence_dir reset_connection_readback.tcldict] $readback]
write_bd_tcl [file join $evidence_dir validated_probe_bd.tcl]
file copy [get_property FILE_NAME [current_bd_design]] [file join $evidence_dir validated_probe.bd]
file copy [file join $run_dir project/.ipcfg/attempts.tcldict] [file join $evidence_dir attempts_final.tcldict]
close_project
puts "RESET_PROBE:OK"
