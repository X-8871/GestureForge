# 创建 AXI3 到 AXI4-Lite 协议转换器，并检查最小 GP0/HP0 接入路径。
set repo_root {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set run_dir [file join $repo_root tmp/2B/S2B-T08/ip_probe_20261009_r01]
set evidence_dir [file join $repo_root report/evidence/S2B-T08/ip_probe_20261009_r01]
set helper {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set project_path [file join $run_dir project/s2b_ps_candidate.xpr]
set bd_path [file join $run_dir project/s2b_ps_candidate.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
set native_log [file join $run_dir batch/probe_converter_vivado.log]

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

open_project $project_path
open_bd_design $bd_path
source -notrace $helper
set ::ipcfg::native_log_path $native_log

set conv_req [dict create \
    CONFIG.SI_PROTOCOL AXI3 \
    CONFIG.MI_PROTOCOL AXI4LITE \
    CONFIG.ADDR_WIDTH 32 \
    CONFIG.DATA_WIDTH 32 \
    CONFIG.ID_WIDTH 12 \
    CONFIG.TRANSLATION_MODE 0]

proc create_converter {} {
    global conv_req evidence_dir
    if {[llength [get_bd_cells -quiet axi_gp0_lite]] == 0} {
        set result [ipcfg::create_cell_cfg xilinx.com:ip:axi_protocol_converter axi_gp0_lite $conv_req]
        if {![string match {SUCCESS:*} $result]} {error $result}
    }
    set stuck [ipcfg::verify_stuck axi_gp0_lite $conv_req]
    if {[llength $stuck]} {error "STUCK_FAIL:$stuck"}
    set snap [ipcfg::snapshot axi_gp0_lite [dict keys $conv_req]]
    puts [ipcfg::write_evidence [file join $evidence_dir converter_config_readback_r2.tcldict] [dict create requested $conv_req readback $snap]]
    return "CONVERTER_CONFIG:OK"
}

set receipt [ipcfg::capture [file join $evidence_dir converter_config_capture_r2.tcldict] {create_converter} {CONVERTER_CONFIG:OK}]
puts $receipt
if {[dict get $receipt status] ne "OK"} {error "CONVERTER_CAPTURE_FAIL:$receipt"}

# 最小候选连接：GP0 进入协议转换器；转换器 AXI4-Lite 主口外接未来 CSR；HP0 外接未来 PL 主设备。
connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] [get_bd_intf_pins axi_gp0_lite/S_AXI]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins ps7/M_AXI_GP0_ACLK]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins ps7/S_AXI_HP0_ACLK]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] [get_bd_pins axi_gp0_lite/aclk]
connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] [get_bd_pins axi_gp0_lite/aresetn]

make_bd_intf_pins_external [get_bd_intf_pins ps7/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7/FIXED_IO]
make_bd_intf_pins_external [get_bd_intf_pins ps7/S_AXI_HP0]
make_bd_intf_pins_external [get_bd_intf_pins axi_gp0_lite/M_AXI]
set_property CONFIG.FREQ_HZ 50000000 [get_bd_intf_ports S_AXI_HP0_0]
set_property CONFIG.FREQ_HZ 50000000 [get_bd_intf_ports M_AXI_0]

set intf_props {MODE VLNV CONFIG.PROTOCOL CONFIG.ADDR_WIDTH CONFIG.DATA_WIDTH CONFIG.ID_WIDTH CONFIG.HAS_BURST CONFIG.HAS_LOCK CONFIG.HAS_CACHE CONFIG.HAS_PROT CONFIG.HAS_QOS CONFIG.HAS_REGION CONFIG.HAS_WSTRB CONFIG.HAS_BRESP CONFIG.HAS_RRESP CONFIG.NUM_READ_OUTSTANDING CONFIG.NUM_WRITE_OUTSTANDING}
set scalar_props {TYPE DIR CLK_DOMAIN FREQ_HZ CONFIG.FREQ_HZ CONFIG.ASSOCIATED_BUSIF}
set report [dict create]
foreach pin {ps7/M_AXI_GP0 ps7/S_AXI_HP0 axi_gp0_lite/S_AXI axi_gp0_lite/M_AXI} {
    dict set report intf_pins $pin [props_of [get_bd_intf_pins $pin] $intf_props]
}
foreach port {S_AXI_HP0_0 M_AXI_0} {
    if {[llength [get_bd_intf_ports -quiet $port]]} {
        dict set report intf_ports $port [props_of [get_bd_intf_ports $port] $intf_props]
    }
}
foreach pin {ps7/FCLK_CLK0 ps7/FCLK_RESET0_N ps7/M_AXI_GP0_ACLK ps7/S_AXI_HP0_ACLK axi_gp0_lite/aclk axi_gp0_lite/aresetn} {
    dict set report scalar_pins $pin [props_of [get_bd_pins $pin] $scalar_props]
}
validate_bd_design
save_bd_design
dict set report validate_status OK
dict set report cells [get_bd_cells -quiet]
dict set report intf_nets [get_bd_intf_nets -quiet]
dict set report nets [get_bd_nets -quiet]
puts [ipcfg::write_evidence [file join $evidence_dir converter_connection_readback_r2.tcldict] $report]
close_project
puts "PROBE_CONVERTER:OK"
