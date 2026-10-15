# 仅用于离线Vivado scratch候选，不初始化PS/DDR、不连接或操作板卡。
source -notrace {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set ::ipcfg::native_log_path {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r01/.vivado-ai/vivado_78004815_0dd60c44.log}
set ::ipcfg::evidence_dir {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence}
set receipt [ipcfg::capture {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/configure_candidate.tcldict} {
    create_bd_design design_1
    set expected [dict create \
        CONFIG.PCW_UIPARAM_DDR_ENABLE {1} \
        CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41K256M16TW-107} \
        CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE {DDR 3} \
        CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH {32 Bit} \
        CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH {16 Bits} \
        CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY {4096 MBits} \
        CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT {15} \
        CONFIG.PCW_UIPARAM_DDR_COL_ADDR_COUNT {10} \
        CONFIG.PCW_UIPARAM_DDR_BANK_ADDR_COUNT {3} \
        CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ {533.333333}]
    set create_status [ipcfg::create_cell_cfg {xilinx.com:ip:processing_system7:5.5} processing_system7_0 $expected]
    set cell [get_bd_cells processing_system7_0]
    set stuck [ipcfg::verify_stuck $cell $expected]
    set intent [ipcfg::verify_intent $cell $expected 0]
    if {![string match {SUCCESS:*} $create_status]} {error "CONFIGURE_FAIL:$create_status"}
    if {$stuck ne {}} {error "STUCK_FAIL:$stuck"}
    if {$intent ne {}} {error "INTENT_FAIL:$intent"}
    dict create create_status $create_status verify_stuck $stuck verify_intent $intent
}]
puts "CAPTURE_STATUS:[dict get $receipt status]"
puts "CAPTURE_CODE:[dict get $receipt tcl_code]"
if {[dict get $receipt status] ne {OK}} {error "CONFIGURE_CAPTURE_FAIL:see [dict get $receipt evidence_path]"}
