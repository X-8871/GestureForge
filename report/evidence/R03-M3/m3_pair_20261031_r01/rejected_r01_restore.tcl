# 仅在before之前按旧快照重建候选区，字数固定，不建立新基准。
set code [catch {
    connect -url tcp:127.0.0.1:3121
    foreach core {0 1} {
        targets -set -filter [format {name =~ "*Cortex-A9*#%d"} $core]
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} [string trim [state]]]} {error "CPU_NOT_STOPPED"}
    }
    targets -set -filter {name =~ "*Cortex-A9*#0"}
    if {([mrd -value 0x43c0000c] & 0x3107) != 0} {error "PL_NOT_IDLE"}
    mwr -bin -file {D:/codex-worktrees/w4/report/evidence/S4-T32/window_a_20261027_r01/m3_snapshot_orig.bin} 0x12000000 3153920
    puts "M3_RESTORED_FROM_ORIGINAL_SNAPSHOT"
} message]
catch {disconnect}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
