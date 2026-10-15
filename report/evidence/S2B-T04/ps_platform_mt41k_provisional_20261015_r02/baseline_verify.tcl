# 仅补采同版本IP的默认基线并复核候选；不初始化PS/DDR或操作板卡。
source -notrace {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set ::ipcfg::native_log_path {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r01/.vivado-ai/vivado_78004815_0dd60c44.log}
set ::ipcfg::evidence_dir {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence}
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
set receipt [ipcfg::capture {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/baseline_verify.tcldict} {
    set probe [create_bd_cell -type ip -vlnv {xilinx.com:ip:processing_system7:5.5} processing_system7_default_probe]
    set baseline [ipcfg::snapshot [get_bd_cells processing_system7_default_probe] [dict keys $expected]]
    set baseline_receipt [ipcfg::write_evidence {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/baseline_default.tcldict} $baseline]
    set cleanup_status [ipcfg::cleanup [get_bd_cells processing_system7_default_probe]]
    set candidate [get_bd_cells processing_system7_0]
    set reqmap {}
    foreach key [dict keys $expected] {lappend reqmap $key [dict get $expected $key] [dict get $baseline $key]}
    set stuck [ipcfg::verify_stuck $candidate $expected]
    set intent [ipcfg::verify_intent $candidate $reqmap 0]
    if {$stuck ne {}} {error "STUCK_FAIL:$stuck"}
    if {$intent ne {}} {error "INTENT_FAIL:$intent"}
    set read_keys {CONFIG.PCW_UIPARAM_DDR_ENABLE CONFIG.PCW_UIPARAM_DDR_PARTNO CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT CONFIG.PCW_UIPARAM_DDR_COL_ADDR_COUNT CONFIG.PCW_UIPARAM_DDR_BANK_ADDR_COUNT CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ CONFIG.PCW_UIPARAM_DDR_SPEED_BIN CONFIG.PCW_UIPARAM_DDR_CL CONFIG.PCW_UIPARAM_DDR_CWL CONFIG.PCW_UIPARAM_DDR_T_FAW CONFIG.PCW_UIPARAM_DDR_T_RAS_MIN CONFIG.PCW_UIPARAM_DDR_T_RC CONFIG.PCW_UIPARAM_DDR_T_RCD CONFIG.PCW_UIPARAM_DDR_T_RP CONFIG.PCW_UIPARAM_ACT_DDR_FREQ_MHZ}
    set readback [dict create]
    foreach key $read_keys {dict set readback $key [get_property $key $candidate]}
    set readback_receipt [ipcfg::write_evidence {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/readback_final.tcldict} $readback]
    save_bd_design
    dict create cleanup_status $cleanup_status baseline_file [dict get $baseline_receipt evidence_path] readback_file [dict get $readback_receipt evidence_path] verify_stuck $stuck verify_intent $intent readback_count [dict size $readback]
}]
puts "CAPTURE_STATUS:[dict get $receipt status]"
puts "CAPTURE_RESULT:[dict get $receipt raw]"
if {[dict get $receipt status] ne {OK}} {error "VERIFY_CAPTURE_FAIL:see [dict get $receipt evidence_path]"}
set disabled [ipcfg::find_disabled [dict get $receipt output]]
puts "DISABLED_SCAN:$disabled"
if {$disabled ne {}} {error "DISABLED_PARAM:$disabled"}
