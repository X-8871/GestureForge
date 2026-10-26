# 本脚本仅恢复精确处于 Stopped 状态的 A9；不接受 Suspended 或其他状态。

set rc 2
set connected 0

if {[catch {connect} err]} {
    puts "RECOVERY_CONNECT_FAIL=$err"
    puts "RECOVERY_EXIT=2"
    exit 2
}
set connected 1
puts "RECOVERY_CONNECT_OK=1"

if {[catch {targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}} err]} {
    puts "RECOVERY_TARGET_FAIL=$err"
} elseif {[catch {set before [string trim [state]]} err]} {
    puts "RECOVERY_STATE_FAIL=$err"
} elseif {$before eq "Running"} {
    puts "RECOVERY_ALREADY_RUNNING=1"
    set rc 0
} elseif {$before eq "Stopped"} {
    puts "RECOVERY_EXACT_STOPPED=$before"
    if {[catch {con} err]} {
        puts "RECOVERY_CON_FAIL=$err"
    } elseif {[catch {set after [string trim [state]]} err]} {
        puts "RECOVERY_STATE_AFTER_CON_FAIL=$err"
    } else {
        puts "RECOVERY_STATE_AFTER_CON=$after"
        if {$after eq "Running"} { set rc 0 }
    }
} else {
    puts "RECOVERY_STATE_UNRECOGNIZED=$before"
}

if {$connected} { catch {disconnect} }
puts "RECOVERY_EXIT=$rc"
exit $rc
