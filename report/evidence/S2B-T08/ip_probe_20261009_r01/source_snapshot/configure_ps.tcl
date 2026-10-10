# 以已核验 PS-only 请求为基础，仅启用候选 PL 接口。
set probe_ps_requested [dict replace [::s2b_ps_platform::requested] CONFIG.PCW_USE_M_AXI_GP0 1 CONFIG.PCW_USE_S_AXI_HP0 1 CONFIG.PCW_S_AXI_HP0_DATA_WIDTH 64 CONFIG.PCW_EN_CLK0_PORT 1 CONFIG.PCW_EN_RST0_PORT 1 CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ 50]
set probe_ps_baseline [ipcfg::snapshot ps_defaults [dict keys $probe_ps_requested]]
puts [ipcfg::write_evidence [file join $probe_evidence ps_baseline.tcldict] $probe_ps_baseline]
puts [ipcfg::cleanup ps_defaults]
proc probe_configure_ps {} {
    global probe_ps_requested probe_ps_baseline probe_evidence
    set result [ipcfg::create_cell_cfg xilinx.com:ip:processing_system7 ps7 $probe_ps_requested]
    puts $result
    if {![string match {SUCCESS:*} $result]} {error $result}
    set stuck [ipcfg::verify_stuck ps7 $probe_ps_requested]
    if {[llength $stuck]} {error "STUCK_FAIL:$stuck"}
    set reqmap {}
    dict for {key want} $probe_ps_requested {lappend reqmap $key $want [dict get $probe_ps_baseline $key]}
    set intent [ipcfg::verify_intent ps7 $reqmap 0]
    if {[llength $intent]} {error "INTENT_FAIL:$intent"}
    puts [ipcfg::write_evidence [file join $probe_evidence ps_intent.tcldict] [dict create requested $probe_ps_requested audit [ipcfg::audit_intent ps7 $reqmap]]]
    puts "PS_CONFIG:OK"
}
set receipt [ipcfg::capture [file join $probe_evidence ps_config_capture.tcldict] {probe_configure_ps} {EXPECT:PS_CONFIG:OK}]
puts $receipt
if {[dict get $receipt status] ne "OK"} {error "PS_CAPTURE_FAIL:$receipt"}
puts [ipcfg::write_evidence [file join $probe_evidence ps_interfaces_before_validate.tcldict] [dict create gp0 [ipcfg::snapshot ps7 [dict keys $probe_ps_requested]] interfaces [get_bd_intf_pins -of_objects [get_bd_cells ps7]] scalar [get_bd_pins -of_objects [get_bd_cells ps7]]]]
puts "CONFIGURE_PS:OK"
