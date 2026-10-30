# 本窗沿用已初始化的当前POR，不运行init，不复位，不运行应用。
proc stopped {filter} {
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "TARGET_NOT_UNIQUE"}
    targets -set -filter $filter
    set value [string trim [state]]
    if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {error "CPU_NOT_STOPPED: $value"}
    puts "CORE_STATE=$value"
}
set code [catch {
    connect -url tcp:127.0.0.1:3121
    stopped {name =~ "*Cortex-A9*#0"}
    stopped {name =~ "*Cortex-A9*#1"}
    targets -set -filter {name =~ "*Cortex-A9*#0"}
    loadhw -hw {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa} -mem-ranges {0x00000000 0x7FFFFFFF}
    mwr 0xf8000008 0xdf0d
    mwr 0xf8000900 0xa
    mwr 0xf8000240 0x0
    mwr 0xf8000004 0x767b
    if {[mrd -value 0xf8000900] != 10 || [mrd -value 0xf8000240] != 0} {error "LEVEL_A_CHECK_FAILED"}
    targets -set -filter {name =~ "*xc7z020*"}
    fpga -file {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit}
    puts "M3_FPGA_PROGRAMMED"
    targets -set -filter {name =~ "*Cortex-A9*#0"}
    mwr 0xf8000008 0xdf0d
    mwr 0xf8000900 0xf
    mwr 0xf8000240 0x0
    mwr 0xf8000004 0x767b
    if {[mrd -value 0xf8000900] != 15 || [mrd -value 0xf8000240] != 0} {error "LEVEL_F_CHECK_FAILED"}
    set ident [mrd -value 0x43c00000]
    set status [mrd -value 0x43c0000c]
    puts "CSR_ID=$ident CSR_STATUS=$status"
    if {$ident != 0x53324250 || ($status & 0x3107) != 0} {error "NEW_PL_NOT_IDLE"}
    dow {D:/tmp/lead/tailfix_20261029_r01/build/s4d_ps_app_sw0_chainA.elf}
    mwr 0xf8000008 0xdf0d
    mwr 0xf8000900 0xf
    mwr 0xf8000240 0x0
    mwr 0xf8000004 0x767b
    if {[mrd -value 0xf8000900] != 15 || [mrd -value 0xf8000240] != 0} {error "POST_DOW_LEVEL_F_CHECK_FAILED"}
    stopped {name =~ "*Cortex-A9*#0"}
    stopped {name =~ "*Cortex-A9*#1"}
    puts "M3_SETUP_OK_APP_NOT_RUN"
} message]
catch {disconnect}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
