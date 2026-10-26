# 只读枚举 JTAG target，并在 A9 target 唯一存在时读取一次 state。
# 本脚本不暂停/继续处理器，不访问 MMIO/寄存器，不复位或编程器件。

set rc 0

if {[catch {connect} err]} {
    puts "ENUM_CONNECT_FAIL=$err"
    puts "ENUM_EXIT=2"
    exit 2
}
puts "ENUM_CONNECT_OK=1"

if {[catch {set chain [jtag targets]} err]} {
    puts "ENUM_JTAG_TARGETS_FAIL=$err"
    set rc 3
} else {
    puts "JTAG_TARGETS_BEGIN"
    puts $chain
    puts "JTAG_TARGETS_END"
}

if {$rc == 0} {
    if {[catch {set tree [targets]} err]} {
        puts "ENUM_TARGET_TREE_FAIL=$err"
        set rc 4
    } else {
        puts "TARGET_TREE_BEGIN"
        puts $tree
        puts "TARGET_TREE_END"
    }
}

if {$rc == 0} {
    if {[catch {targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}} err]} {
        puts "A9_TARGET_MISSING=$err"
        set rc 5
    } elseif {[catch {set a9_state [string trim [state]]} err]} {
        puts "A9_STATE_READ_FAIL=$err"
        set rc 6
    } else {
        puts "A9_STATE=$a9_state"
    }
}

if {[catch {disconnect} err]} {
    puts "ENUM_DISCONNECT_FAIL=$err"
    if {$rc == 0} {set rc 7}
} else {
    puts "ENUM_DISCONNECT_OK=1"
}

puts "ENUM_EXIT=$rc"
exit $rc
