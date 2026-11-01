# 每次选择前核验唯一目标与已知名称，不依赖隐式活动目标。
proc select_unique {filter} {
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "TARGET_NOT_UNIQUE"}
    set name [dict get [lindex $matches 0] name]
    if {![regexp -nocase {^(ARM )?Cortex-A9 MPCore #[01]$|^xc7z020(_[0-9]+)?$} $name]} {error "TARGET_NAME_UNEXPECTED: $name"}
    targets -set -filter $filter
    puts "SELECTED_UNIQUE=$name"
}
# 本窗沿用已初始化的当前POR，不运行init，不复位，不运行应用。
set m3_setup_stop_counts [dict create]
proc stopped {filter {allow_stop 0}} {
    global m3_setup_stop_counts
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "TARGET_NOT_UNIQUE"}
    select_unique $filter
    set value [string trim [state]]
    puts "SETUP_INITIAL_STATE=$value"
    if {[regexp -nocase {^running(:|[[:space:]]|$)} $value] && $allow_stop} {
        if {[dict exists $m3_setup_stop_counts $filter]} {error "SETUP_STOP_RETRY_FORBIDDEN"}
        dict set m3_setup_stop_counts $filter 1
        stop
        set value [string trim [state]]
        puts "SETUP_ONE_STOP=$filter STATE=$value"
    }
    if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {error "CPU_NOT_STOPPED: $value"}
    puts "CORE_STATE=$value"
}
set code [catch {
    set port_file [file join [file dirname [info script]] .. port.txt]
    set port_handle [open $port_file r]
    set m3_port [string trim [read $port_handle]]
    close $port_handle
    if {$m3_port ne "3121" && $m3_port ne "3122"} {error "UNAPPROVED_PORT"}
    connect -url "tcp:127.0.0.1:$m3_port"
    select_unique {name =~ "*Cortex-A9*#0"}
    loadhw -hw {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa} -mem-ranges {0x00000000 0x7FFFFFFF}
    stopped {name =~ "*Cortex-A9*#0"} 1
    stopped {name =~ "*Cortex-A9*#1"} 1
    select_unique {name =~ "*Cortex-A9*#0"}
    mwr 0xf8000008 0xdf0d
    mwr 0xf8000900 0xa
    mwr 0xf8000240 0x0
    mwr 0xf8000004 0x767b
    if {[mrd -value 0xf8000900] != 10 || [mrd -value 0xf8000240] != 0} {error "LEVEL_A_CHECK_FAILED"}
    select_unique {name =~ "*xc7z020*"}
    fpga -file {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit}
    puts "M3_FPGA_PROGRAMMED"
    select_unique {name =~ "*Cortex-A9*#0"}
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
    puts "SETUP_STOP_COUNTS=$m3_setup_stop_counts"
    puts "M3_SETUP_OK_APP_NOT_RUN"
} message]
set disconnect_code [catch {disconnect} disconnect_message]
if {$code == 0 && $disconnect_code != 0} {set code 2; set message "DISCONNECT_FAILED: $disconnect_message"}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
