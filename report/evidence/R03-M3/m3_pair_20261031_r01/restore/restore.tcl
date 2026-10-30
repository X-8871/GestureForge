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
    connect -url tcp:127.0.0.1:3121
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
