# 每次选择前核验唯一目标与已知名称，不依赖隐式活动目标。
proc select_unique {filter} {
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "TARGET_NOT_UNIQUE"}
    set name [dict get [lindex $matches 0] name]
    if {![regexp -nocase {^(ARM )?Cortex-A9 MPCore #[01]$|^xc7z020(_[0-9]+)?$} $name]} {error "TARGET_NAME_UNEXPECTED: $name"}
    targets -set -filter $filter
    puts "SELECTED_UNIQUE=$name"
}
# 两次成对取样之间只有只读寄存器检查与短时保持，不运行应用。
set code [catch {
    set port_file [file join [file dirname [info script]] .. port.txt]
    set port_handle [open $port_file r]
    set m3_port [string trim [read $port_handle]]
    close $port_handle
    if {$m3_port ne "3121" && $m3_port ne "3122"} {error "UNAPPROVED_PORT"}
    connect -url "tcp:127.0.0.1:$m3_port"
    # 每个新XSDB客户端独立加载固定地址映射，不执行任何初始化。
    select_unique {name =~ "*Cortex-A9*#0"}
    loadhw -hw {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa} -mem-ranges {0x00000000 0x7FFFFFFF}
    foreach core {0 1} {
        select_unique [format {name =~ "*Cortex-A9*#%d"} $core]
        set value [string trim [state]]
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {error "CPU_NOT_STOPPED"}
        puts "EVENT_CORE_${core}=$value"
    }
    select_unique {name =~ "*Cortex-A9*#0"}
    for {set i 0} {$i < 3} {incr i} {
        set ident [mrd -value 0x43c00000]
        set status [mrd -value 0x43c0000c]
        set clock [mrd -value 0xf8f00200 2]
        puts "EVENT_SAMPLE=$i ID=$ident STATUS=$status GT=$clock"
        if {$ident != 0x53324250 || ($status & 0x3107) != 0} {error "EVENT_PL_NOT_IDLE"}
        after 200
    }
    puts "M3_READONLY_EVENT_OK"
} message]
set disconnect_code [catch {disconnect} disconnect_message]
if {$code == 0 && $disconnect_code != 0} {set code 2; set message "DISCONNECT_FAILED: $disconnect_message"}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
