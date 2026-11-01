# 本文件只连接、选择 Cortex-A9 #0、核验两核已停止并读取固定 DDR 区域。
proc m3_read_pair {} {
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_BEGIN"
connect -url tcp:127.0.0.1:3121
set cpu0_matches [targets -target-properties -filter {name =~ "*Cortex-A9*#0"}]
set cpu1_matches [targets -target-properties -filter {name =~ "*Cortex-A9*#1"}]
if {[llength $cpu0_matches] != 1} {error "M3_CPU0_TARGET_COUNT_MISMATCH"}
if {[llength $cpu1_matches] != 1} {error "M3_CPU1_TARGET_COUNT_MISMATCH"}
set cpu0_props [lindex $cpu0_matches 0]
set cpu1_props [lindex $cpu1_matches 0]
set cpu0_name [dict get $cpu0_props name]
set cpu1_name [dict get $cpu1_props name]
if {![string match "*Cortex-A9*#0" $cpu0_name]} {error "M3_CPU0_TARGET_NAME_MISMATCH"}
if {![string match "*Cortex-A9*#1" $cpu1_name]} {error "M3_CPU1_TARGET_NAME_MISMATCH"}
set cpu0_state [string trim [dict get $cpu0_props state]]
set cpu1_state [string trim [dict get $cpu1_props state]]
if {![regexp -nocase {^(stopped|suspended)(\s|$)} $cpu0_state]} {error "M3_CPU0_NOT_STOPPED_OR_SUSPENDED"}
if {![regexp -nocase {^(stopped|suspended)(\s|$)} $cpu1_state]} {error "M3_CPU1_NOT_STOPPED_OR_SUSPENDED"}
targets -set -filter {name =~ "*Cortex-A9*#0"}
set active_matches [targets -target-properties -filter {name =~ "*Cortex-A9*#0"}]
if {[llength $active_matches] != 1} {error "M3_ACTIVE_TARGET_COUNT_MISMATCH"}
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_TARGET_STATE_OK"
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_READ_A_BEGIN"
mrd -bin -file "D:\\tmp\\lead\\m3_pair_20261030_r01\\before\\read_a.bin" 0x12000000 3153920
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_READ_A_OK"
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_READ_B_BEGIN"
mrd -bin -file "D:\\tmp\\lead\\m3_pair_20261030_r01\\before\\read_b.bin" 0x12000000 3153920
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_READ_B_OK"
puts "M3PAIR_89398451072a4602a50a5ec20e33f9dc_END"
}
set m3_rc [catch {m3_read_pair} m3_error]
set m3_disconnect_rc [catch {disconnect} m3_disconnect_error]
if {$m3_rc != 0} {
    puts stderr "ERROR: $m3_error"
    exit 2
}
if {$m3_disconnect_rc != 0} {
    puts stderr "ERROR: disconnect failed: $m3_disconnect_error"
    exit 2
}
exit 0
