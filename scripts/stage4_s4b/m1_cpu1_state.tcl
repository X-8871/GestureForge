# M1：CPU1 保持停止（只读；不 halt、不 resume、不改任何目标状态）
# 用法：xsdb.bat scripts\stage4_s4b\m1_cpu1_state.tcl
# 输出约定：以 M1_ 前缀行供驱动解析；退出码 0=PASS(确定性 halted) / 3=cpu1 未找到 / 4=cpu1 非 halted

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url
set all_targets [targets]
puts "M1_TARGET_COUNT=[llength $all_targets]"
foreach t $all_targets { puts "M1_TARGET=$t" }

set cpu1 {}
foreach t $all_targets {
    set lowered [string tolower $t]
    if {[string match "*#1*" $t] || [string match "*cpu*1*" $lowered] || [string match "*cortex*a9*1*" $lowered]} {
        lappend cpu1 $t
    }
}
if {[llength $cpu1] == 0} {
    puts "M1_CPU1_TARGET=NOT_FOUND"
    disconnect
    exit 3
}
set t [lindex $cpu1 0]
puts "M1_CPU1_TARGET=$t"
targets $t
set state1 [state]
set pc1 [rrd pc]
puts "M1_CPU1_STATE=$state1"
puts "M1_CPU1_PC_1=$pc1"
after 2000
set pc2 [rrd pc]
set state2 [state]
puts "M1_CPU1_PC_2=$pc2"
puts "M1_CPU1_STATE_2=$state2"
if {$pc1 == $pc2} { puts "M1_CPU1_PC_STABLE=1" } else { puts "M1_CPU1_PC_STABLE=0" }
disconnect
if {[string match -nocase "*halt*" $state1] && $pc1 == $pc2} {
    puts "M1_RESULT=PASS"
    exit 0
}
puts "M1_RESULT=FAIL"
exit 4