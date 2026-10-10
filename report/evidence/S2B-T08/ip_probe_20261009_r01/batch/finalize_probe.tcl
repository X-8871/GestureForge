# 收敛已保存的最小连接探针：补充可分配地址，并保存最终读回。
set repo_root {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set run_dir [file join $repo_root tmp/2B/S2B-T08/ip_probe_20261009_r01]
set evidence_dir [file join $repo_root report/evidence/S2B-T08/ip_probe_20261009_r01]
set helper {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set project_path [file join $run_dir project/s2b_ps_candidate.xpr]
set bd_path [file join $run_dir project/s2b_ps_candidate.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
set native_log [file join $run_dir batch/finalize_probe_vivado.log]

proc props_of {obj props} {
    set out {}
    foreach p $props {
        if {[catch {set v [get_property $p $obj]}]} {
            set v "<NA>"
        }
        dict set out $p $v
    }
    return $out
}

proc try_step {script} {
    if {[catch {uplevel 1 $script} msg opts]} {
        return [dict create status FAIL message $msg errorinfo [dict get $opts -errorinfo]]
    }
    return [dict create status OK message $msg]
}

open_project $project_path
open_bd_design $bd_path
source -notrace $helper
set ::ipcfg::native_log_path $native_log

set actions [dict create]
dict set actions assign_gp0_csr [try_step {
    assign_bd_address -offset 0x43C00000 -range 64K [get_bd_addr_segs M_AXI_0/Reg]
}]
dict set actions assign_hp0_space [try_step {
    assign_bd_address [get_bd_addr_segs ps7/S_AXI_HP0/HP0_DDR_LOWOCM]
}]
dict set actions validate [try_step {
    validate_bd_design
}]
save_bd_design

set intf_props {MODE VLNV CONFIG.PROTOCOL CONFIG.ADDR_WIDTH CONFIG.DATA_WIDTH CONFIG.ID_WIDTH CONFIG.FREQ_HZ CONFIG.HAS_BURST CONFIG.HAS_LOCK CONFIG.HAS_CACHE CONFIG.HAS_PROT CONFIG.HAS_QOS CONFIG.HAS_REGION CONFIG.HAS_WSTRB CONFIG.HAS_BRESP CONFIG.HAS_RRESP CONFIG.NUM_READ_OUTSTANDING CONFIG.NUM_WRITE_OUTSTANDING}
set scalar_props {TYPE DIR CLK_DOMAIN FREQ_HZ CONFIG.FREQ_HZ CONFIG.ASSOCIATED_BUSIF}
set report [dict create actions $actions]
foreach pin {ps7/M_AXI_GP0 ps7/S_AXI_HP0 axi_gp0_lite/S_AXI axi_gp0_lite/M_AXI} {
    dict set report intf_pins $pin [props_of [get_bd_intf_pins $pin] $intf_props]
}
foreach port {S_AXI_HP0_0 M_AXI_0 DDR_0 FIXED_IO_0} {
    if {[llength [get_bd_intf_ports -quiet $port]]} {
        dict set report intf_ports $port [props_of [get_bd_intf_ports $port] $intf_props]
    }
}
foreach pin {ps7/FCLK_CLK0 ps7/FCLK_RESET0_N ps7/M_AXI_GP0_ACLK ps7/S_AXI_HP0_ACLK axi_gp0_lite/aclk axi_gp0_lite/aresetn} {
    dict set report scalar_pins $pin [props_of [get_bd_pins $pin] $scalar_props]
}
dict set report address_spaces [get_bd_addr_spaces -quiet]
dict set report address_segments [get_bd_addr_segs -quiet]
dict set report cells [get_bd_cells -quiet]
dict set report intf_nets [get_bd_intf_nets -quiet]
dict set report nets [get_bd_nets -quiet]
puts [ipcfg::write_evidence [file join $evidence_dir final_probe_readback.tcldict] $report]
close_project
puts "FINALIZE_PROBE:OK"
