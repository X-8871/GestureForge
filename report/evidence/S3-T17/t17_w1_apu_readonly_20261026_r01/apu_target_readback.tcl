# 仅供新的明确批准窗口执行；使用新 RunId，不复用旧窗口。
# 仅在已确认 A9 正常运行后暂停短时，再经 APU/AXI-AP 只读 VDMA MMIO。
# 不写寄存器、不复位、不烧录、不改线、不直接访问 DDR 地址；所有访问错误立即中止。

set rc 2
set connected 0
set stop_attempted 0
set read_ok 0

if {[catch {connect} err]} {
    puts "W1_APU_CONNECT_FAIL=$err"
    puts "W1_APU_EXIT=2"
    exit 2
}
set connected 1
puts "W1_APU_CONNECT_OK=1"

if {[catch {set chain [jtag targets]} err]} {
    puts "W1_APU_CHAIN_FAIL=$err"
    catch {disconnect}
    puts "W1_APU_EXIT=2"
    exit 2
}
puts "W1_APU_CHAIN_BEGIN"
puts $chain
puts "W1_APU_CHAIN_END"

if {[catch {set tree [targets]} err]} {
    puts "W1_APU_TARGET_TREE_FAIL=$err"
    catch {disconnect}
    puts "W1_APU_EXIT=2"
    exit 2
}
puts "W1_APU_TARGET_TREE_BEGIN"
puts $tree
puts "W1_APU_TARGET_TREE_END"

if {[catch {
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    set before [string trim [state]]
    puts "W1_APU_A9_STATE_BEFORE=$before"
    if {$before ne "Running"} {
        error "A9_NOT_CONFIRMED_RUNNING_BEFORE_STOP"
    }

    set stop_attempted 1
    stop
    after 300
    set after_stop [string trim [state]]
    puts "W1_APU_A9_STATE_AFTER_STOP=$after_stop"
    if {$after_stop ne "Stopped" && $after_stop ne "Stopped: (Suspended)"} {
        error "A9_HALT_NOT_CONFIRMED"
    }
    # 精确名称选择；targets -set 在无匹配或多匹配时应失败关闭。
    targets -set -nocase -filter {name == "APU"}
    puts "W1_APU_ACTIVE_TARGET_PROPERTIES_BEGIN"
    puts [targets -target-properties]
    puts "W1_APU_ACTIVE_TARGET_PROPERTIES_END"

    set sr [mrd -value 0x43010034]
    puts "W1_APU_S2MM_SR=$sr"
    set s2mm_addr [mrd -value 0x430100AC]
    puts "W1_APU_ADDR_S2MM=$s2mm_addr"
    set mm2s_addr [mrd -value 0x4300005C]
    puts "W1_APU_ADDR_MM2S=$mm2s_addr"
    set read_ok 1
} err]} {
    puts "W1_APU_READBACK_FAIL=$err"
}

if {$read_ok} { set rc 0 }

if {$stop_attempted} {
    if {[catch {targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}} err]} {
        puts "W1_APU_RESELECT_A9_FAIL=$err"
        puts "W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1"
        set rc 2
    } elseif {[catch {set before_resume [string trim [state]]} err]} {
        puts "W1_APU_STATE_BEFORE_RESUME_FAIL=$err"
        puts "W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1"
        set rc 2
    } elseif {$before_resume eq "Stopped" || $before_resume eq "Stopped: (Suspended)"} {
        if {[catch {con} err]} {
            puts "W1_APU_RESUME_FAIL=$err"
            puts "W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1"
            set rc 2
        } elseif {[catch {set after_resume [string trim [state]]} err]} {
            puts "W1_APU_STATE_AFTER_RESUME_FAIL=$err"
            puts "W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1"
            set rc 2
        } else {
            puts "W1_APU_A9_STATE_AFTER_RESUME=$after_resume"
            if {$after_resume ne "Running"} {
                puts "W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1"
                set rc 2
            }
        }
    } elseif {$before_resume eq "Running"} {
        puts "W1_APU_ALREADY_RUNNING_AFTER_READ=1"
    } else {
        puts "W1_APU_RESUME_SKIPPED_STATE_UNCONFIRMED=$before_resume"
        puts "W1_APU_RECOVERY_REQUIRED_NEW_AUTHORIZATION=1"
        set rc 2
    }
}

if {$connected} { catch {disconnect} }
puts "W1_APU_EXIT=$rc"
exit $rc
