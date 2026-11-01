# 每次选择前核验唯一目标与已知名称，不依赖隐式活动目标。
proc select_unique {filter} {
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "TARGET_NOT_UNIQUE"}
    set name [dict get [lindex $matches 0] name]
    if {![regexp -nocase {^(ARM )?Cortex-A9 MPCore #[01]$|^xc7z020(_[0-9]+)?$} $name]} {error "TARGET_NAME_UNEXPECTED: $name"}
    targets -set -filter $filter
    puts "SELECTED_UNIQUE=$name"
}
# 仅在before之前按旧快照重建候选区，字数固定，不建立新基准。
set code [catch {
    set port_file [file join [file dirname [info script]] .. port.txt]
    set port_handle [open $port_file r]
    set m3_port [string trim [read $port_handle]]
    close $port_handle
    if {$m3_port ne "3121" && $m3_port ne "3122"} {error "UNAPPROVED_PORT"}
    connect -url "tcp:127.0.0.1:$m3_port"
    # XSDB每次新进程均需声明固定XSA映射；不初始化或改写PS配置。
    select_unique {name =~ "*Cortex-A9*#0"}
    loadhw -hw {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa} -mem-ranges {0x00000000 0x7FFFFFFF}
    foreach core {0 1} {
        select_unique [format {name =~ "*Cortex-A9*#%d"} $core]
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} [string trim [state]]]} {error "CPU_NOT_STOPPED"}
    }
    select_unique {name =~ "*Cortex-A9*#0"}
    if {([mrd -value 0x43c0000c] & 0x3107) != 0} {error "PL_NOT_IDLE"}
    mwr -bin -file {D:/codex-worktrees/w4/report/evidence/S4-T32/window_a_20261027_r01/m3_snapshot_orig.bin} 0x12000000 3153920
    puts "M3_RESTORED_FROM_ORIGINAL_SNAPSHOT"
} message]
set disconnect_code [catch {disconnect} disconnect_message]
if {$code == 0 && $disconnect_code != 0} {set code 2; set message "DISCONNECT_FAILED: $disconnect_message"}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
