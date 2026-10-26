# 阶段3只读 W1：核对目标链与 A9 状态；仅在本脚本已将运行中的 A9 确认暂停后读取寄存器。
# 不写寄存器、不复位、不烧录；若目标原先已暂停或暂停状态不能确认，则不执行 mrd。

set rc 2
set connected 0
set halted_by_this_script 0

if {[catch {connect} err]} {
    puts "W1_CONNECT_FAIL=$err"
    puts "W1_EXIT=2"
    exit 2
}
set connected 1
puts "W1_CONNECT_OK=1"

if {[catch {set chain [jtag targets]} err]} {
    puts "W1_CHAIN_FAIL=$err"
    catch {disconnect}
    puts "W1_EXIT=2"
    exit 2
}
puts "W1_CHAIN_BEGIN"
puts $chain
puts "W1_CHAIN_END"

if {[catch {targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}} err]} {
    puts "W1_A9_SELECT_FAIL=$err"
    catch {disconnect}
    puts "W1_EXIT=2"
    exit 2
}

if {[catch {set before [string trim [state]]} err]} {
    puts "W1_STATE_BEFORE_FAIL=$err"
    catch {disconnect}
    puts "W1_EXIT=2"
    exit 2
}
puts "W1_A9_STATE_BEFORE=$before"

if {![regexp -nocase {running} $before]} {
    puts "W1_READBACK_BLOCKED=TARGET_NOT_CONFIRMED_RUNNING_BEFORE_STOP"
} elseif {[catch {stop} err]} {
    puts "W1_STOP_FAIL=$err"
} else {
    after 500
    if {[catch {set after_stop [string trim [state]]} err]} {
        puts "W1_STATE_AFTER_STOP_FAIL=$err"
    } else {
        puts "W1_A9_STATE_AFTER_STOP=$after_stop"
        if {[regexp -nocase {halt|stop} $after_stop]} {
            set halted_by_this_script 1
            if {[catch {
                puts "W1_S2MM_SR=[mrd -force 0x43010034]"
                puts "W1_S2MM_ADDR=[mrd -force 0x430100AC]"
                puts "W1_MM2S_ADDR=[mrd -force 0x4300005C]"
            } err]} {
                puts "W1_MRD_FAIL=$err"
            } else {
                set rc 0
                puts "W1_READBACK_OK=1"
            }
        } else {
            puts "W1_READBACK_BLOCKED=HALT_NOT_CONFIRMED"
        }
    }
}

if {$halted_by_this_script} {
    if {[catch {set before_resume [string trim [state]]} err]} {
        puts "W1_STATE_BEFORE_RESUME_FAIL=$err"
        set rc 2
    } elseif {[regexp -nocase {halt|stop} $before_resume]} {
        if {[catch {con} err]} {
            puts "W1_RESUME_FAIL=$err"
            set rc 2
        } else {
            after 100
            if {[catch {set after_resume [string trim [state]]} err]} {
                puts "W1_STATE_AFTER_RESUME_FAIL=$err"
                set rc 2
            } else {
                puts "W1_A9_STATE_AFTER_RESUME=$after_resume"
                if {![regexp -nocase {running} $after_resume]} {
                    puts "W1_RESUME_STATE_UNCONFIRMED=1"
                    set rc 2
                }
            }
        }
    } else {
        puts "W1_RESUME_SKIPPED=TARGET_NO_LONGER_HALTED"
        set rc 2
    }
}

if {$connected} { catch {disconnect} }
puts "W1_EXIT=$rc"
exit $rc
