source -notrace {C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl}
set ::ipcfg::native_log_path {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r01/.vivado-ai/vivado_78004815_0dd60c44.log}
set ::ipcfg::evidence_dir {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence}
proc load_evidence_data {path} {
    set handle [open $path r]
    set contents [read $handle]
    close $handle
    dict get $contents data
}
set configure_record [load_evidence_data {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/configure_candidate.tcldict}]
set verify_record [load_evidence_data {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/baseline_verify.tcldict}]
set disabled_configure [ipcfg::find_disabled [dict get $configure_record output]]
set disabled_verify [ipcfg::find_disabled [dict get $verify_record output]]
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
set candidate [get_bd_cells processing_system7_0]
set mismatches {}
set read_keys {CONFIG.PCW_UIPARAM_DDR_ENABLE CONFIG.PCW_UIPARAM_DDR_PARTNO CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT CONFIG.PCW_UIPARAM_DDR_COL_ADDR_COUNT CONFIG.PCW_UIPARAM_DDR_BANK_ADDR_COUNT CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ CONFIG.PCW_UIPARAM_DDR_SPEED_BIN CONFIG.PCW_UIPARAM_DDR_CL CONFIG.PCW_UIPARAM_DDR_CWL CONFIG.PCW_UIPARAM_DDR_T_FAW CONFIG.PCW_UIPARAM_DDR_T_RAS_MIN CONFIG.PCW_UIPARAM_DDR_T_RC CONFIG.PCW_UIPARAM_DDR_T_RCD CONFIG.PCW_UIPARAM_DDR_T_RP CONFIG.PCW_UIPARAM_ACT_DDR_FREQ_MHZ}
set readback [dict create]
foreach key $read_keys {
    set value [get_property $key $candidate]
    dict set readback $key $value
    if {[dict exists $expected $key] && $value ne [dict get $expected $key]} {lappend mismatches "$key=$value"}
}
if {$disabled_configure ne {} || $disabled_verify ne {}} {error "DISABLED_PARAM:$disabled_configure $disabled_verify"}
if {$mismatches ne {}} {error "READBACK_MISMATCH:$mismatches"}
if {[dict get $verify_record status] ne {OK}} {error "VERIFY_CAPTURE_NOT_OK:[dict get $verify_record status]"}
if {[dict get [dict get $verify_record raw] verify_stuck] ne {} || [dict get [dict get $verify_record raw] verify_intent] ne {}} {error "HELPER_VERIFICATION_NOT_EMPTY"}
set readback_receipt [ipcfg::write_evidence {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/candidate_final_readback.tcldict} $readback]
set audit [dict create configure_capture_status [dict get $configure_record status] configure_capture_code [dict get $configure_record code] verify_capture_status [dict get $verify_record status] verify_stuck [dict get [dict get $verify_record raw] verify_stuck] verify_intent [dict get [dict get $verify_record raw] verify_intent] disabled_configure $disabled_configure disabled_verify $disabled_verify readback_file [dict get $readback_receipt evidence_path] readback_count [dict size $readback] mismatches $mismatches timing_evidence_status {NOT_VERIFIED: applicable Micron timing table unavailable; CL/CWL/timing values are Vivado readback only} hardware_execution NOT_RUN xsa_export NOT_RUN bitstream NOT_RUN ps_init NOT_RUN board_access NOT_RUN]
set audit_receipt [ipcfg::write_evidence {D:/FPGA_Competition/w2b/tmp/2B/S2B-T04/ps_platform_mt41k_provisional_20261015_r02/ipcfg_evidence/final_audit.tcldict} $audit]
save_bd_design
puts "FINAL_AUDIT:[dict get $audit_receipt evidence_path] VALUES:[dict size $readback] VERIFY:PASS DISABLED:EMPTY"
