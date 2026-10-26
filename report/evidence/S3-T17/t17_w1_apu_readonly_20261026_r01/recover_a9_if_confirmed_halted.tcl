# 仅供新批准 W1 窗口中的异常恢复；旧 XSDB 会话已核实不存在时最多执行一次。
# 只查询 A9 状态；仅精确确认停止时执行 con，不包含 mrd、mwr、复位或烧录。

set rc 2
set connected 0

if {[catch {connect} err]} {
    puts "W1_APU_RECOVERY_CONNECT_FAIL=$err"
    puts "W1_APU_RECOVERY_EXIT=2"
    exit 2
}
set connected 1
puts "W1_APU_RECOVERY_CONNECT_OK=1"

if {[catch {targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}} err]} {
    puts "W1_APU_RECOVERY_TARGET_FAIL=$err"
} elseif {[catch {set before [string trim [state]]} err]} {
    puts "W1_APU_RECOVERY_STATE_FAIL=$err"
} elseif {$before eq "Running"} {
    puts "W1_APU_RECOVERY_ALREADY_RUNNING=1"
    set rc 0
} elseif {$before eq "Stopped" || $before eq "Stopped: (Suspended)"} {
    puts "W1_APU_RECOVERY_CONFIRMED_STOPPED=$before"
    if {[catch {con} err]} {
        puts "W1_APU_RECOVERY_CON_FAIL=$err"
    } elseif {[catch {set after [string trim [state]]} err]} {
        puts "W1_APU_RECOVERY_STATE_AFTER_CON_FAIL=$err"
    } else {
        puts "W1_APU_RECOVERY_STATE_AFTER_CON=$after"
        if {$after eq "Running"} { set rc 0 }
    }
} else {
    puts "W1_APU_RECOVERY_STATE_UNRECOGNIZED=$before"
}

if {$connected} { catch {disconnect} }
puts "W1_APU_RECOVERY_EXIT=$rc"
exit $rc
