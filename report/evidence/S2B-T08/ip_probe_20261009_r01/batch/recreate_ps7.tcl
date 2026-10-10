# 重新创建已丢失的内存态 PS7，并保存只读接口证据。
set repo_root {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition}
set run_dir [file join $repo_root tmp/2B/S2B-T08/ip_probe_20261009_r01]
set evidence_dir [file join $repo_root report/evidence/S2B-T08/ip_probe_20261009_r01]
set helper {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set platform [file join $repo_root vivado/s2b_ps_platform.tcl]
set project_path [file join $run_dir project/s2b_ps_candidate.xpr]
set bd_path [file join $run_dir project/s2b_ps_candidate.srcs/sources_1/bd/s2b_ps_only/s2b_ps_only.bd]
set native_log [file join $run_dir batch/recreate_ps7_vivado_r3.log]

proc read_evidence_data {path} {
    set f [open $path r]
    fconfigure $f -encoding utf-8 -translation lf
    set txt [read $f]
    close $f
    return [dict get $txt data]
}

proc pin_props {obj props} {
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
source -notrace $platform
set ::ipcfg::native_log_path $native_log

set requested [dict replace [::s2b_ps_platform::requested] \
    CONFIG.PCW_USE_M_AXI_GP0 1 \
    CONFIG.PCW_USE_S_AXI_HP0 1 \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH 64 \
    CONFIG.PCW_EN_CLK0_PORT 1 \
    CONFIG.PCW_EN_RST0_PORT 1 \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ 50]
set baseline [read_evidence_data [file join $evidence_dir ps_baseline.tcldict]]

proc recreate_ps7 {} {
    global requested baseline evidence_dir
    if {[llength [get_bd_cells -quiet ps7]] != 0} {
        return "PS_CONFIG_RECOVER:EXISTS"
    }
    set result [ipcfg::create_cell_cfg xilinx.com:ip:processing_system7 ps7 $requested]
    if {![string match {SUCCESS:*} $result]} {error $result}
    set stuck [ipcfg::verify_stuck ps7 $requested]
    if {[llength $stuck]} {error "STUCK_FAIL:$stuck"}
    set reqmap {}
    dict for {key want} $requested {
        lappend reqmap $key $want [dict get $baseline $key]
    }
    set intent [ipcfg::verify_intent ps7 $reqmap 0]
    if {[llength $intent]} {error "INTENT_FAIL:$intent"}
    puts [ipcfg::write_evidence [file join $evidence_dir ps_recover3_intent.tcldict] [dict create requested $requested audit [ipcfg::audit_intent ps7 $reqmap]]]
    return "PS_CONFIG_RECOVER:OK"
}

set receipt [ipcfg::capture [file join $evidence_dir ps_recover3_capture.tcldict] {recreate_ps7} {PS_CONFIG_RECOVER:OK}]
puts $receipt
if {[dict get $receipt status] ne "OK"} {error "PS_RECOVER_CAPTURE_FAIL:$receipt"}

set intf_props {MODE VLNV CONFIG.PROTOCOL CONFIG.ADDR_WIDTH CONFIG.DATA_WIDTH CONFIG.ID_WIDTH CONFIG.HAS_BURST CONFIG.HAS_LOCK CONFIG.HAS_CACHE CONFIG.HAS_PROT CONFIG.HAS_QOS CONFIG.HAS_REGION CONFIG.HAS_WSTRB CONFIG.HAS_BRESP CONFIG.HAS_RRESP CONFIG.NUM_READ_OUTSTANDING CONFIG.NUM_WRITE_OUTSTANDING}
set pin_props_list {TYPE DIR CLK_DOMAIN FREQ_HZ CONFIG.FREQ_HZ CONFIG.ASSOCIATED_BUSIF}
set report [dict create]
foreach pin {M_AXI_GP0 S_AXI_HP0} {
    set obj [get_bd_intf_pins ps7/$pin]
    dict set report interfaces $pin [pin_props $obj $intf_props]
}
foreach pin {FCLK_CLK0 FCLK_RESET0_N M_AXI_GP0_ACLK S_AXI_HP0_ACLK} {
    set obj [get_bd_pins ps7/$pin]
    dict set report scalar_pins $pin [pin_props $obj $pin_props_list]
}
dict set report bd_cells [get_bd_cells -quiet]
dict set report bd_intf_pins [get_bd_intf_pins -of_objects [get_bd_cells ps7]]
dict set report bd_pins [get_bd_pins -of_objects [get_bd_cells ps7]]
puts [ipcfg::write_evidence [file join $evidence_dir ps_recover3_interfaces.tcldict] $report]
save_bd_design
close_project
puts "RECREATE_PS7:OK"
