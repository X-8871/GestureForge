# 仅枚举拓扑；不选择目标、不访问寄存器或内存、不改变执行状态。
puts "S6_ENUM_BEGIN=1"
if {[catch {connect -url tcp:127.0.0.1:3121} err]} {
    puts "S6_ENUM_ERROR=connect:$err"
    exit 4
}
set failed 0
if {[catch {set tg [targets]} err]} {
    puts "S6_ENUM_ERROR=targets:$err"
    set failed 1
} else {
    puts "S6_TARGETS_BEGIN"
    puts $tg
    puts "S6_TARGETS_END"
}
if {!$failed} {
    if {[catch {set jt [jtag targets]} err]} {
        puts "S6_ENUM_ERROR=jtag:$err"
        set failed 1
    } else {
        puts "S6_JTAG_BEGIN"
        puts $jt
        puts "S6_JTAG_END"
    }
}
if {[catch {disconnect} err]} {
    puts "S6_ENUM_ERROR=disconnect:$err"
    set failed 1
} else {
    puts "S6_DISCONNECTED=1"
}
if {$failed} {exit 5}
puts "S6_ENUM_END=1"
exit 0
