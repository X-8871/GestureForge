# 本文件只连接、选择 Cortex-A9 #0、核验两核已停止并读取固定 DDR 区域。
proc m3_get_core_state {filter core_label expected_name_pattern} {
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "M3_${core_label}_TARGET_COUNT_MISMATCH"}
    set props [lindex $matches 0]
    set name [dict get $props name]
    if {![string match $expected_name_pattern $name]} {error "M3_${core_label}_TARGET_NAME_MISMATCH"}
    targets -set -filter $filter
    set core_state [string trim [state]]
    if {$core_state eq ""} {error "M3_${core_label}_STATE_EMPTY"}
    if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $core_state]} {error "M3_${core_label}_NOT_STOPPED_OR_SUSPENDED: $core_state"}
    puts "M3PAIR_3ba8e47047c446fda56b31009722c903_${core_label}_STATE=$core_state"
    puts "M3PAIR_3ba8e47047c446fda56b31009722c903_${core_label}_STATE_OK"
    return $core_state
}
proc m3_read_pair {} {
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_BEGIN"
connect -url tcp:127.0.0.1:3121
set cpu0_state [m3_get_core_state {name =~ "*Cortex-A9*#0"} CPU0 {*Cortex-A9*#0}]
set cpu1_state [m3_get_core_state {name =~ "*Cortex-A9*#1"} CPU1 {*Cortex-A9*#1}]
targets -set -filter {name =~ "*Cortex-A9*#0"}
set active_matches [targets -target-properties -filter {name =~ "*Cortex-A9*#0"}]
if {[llength $active_matches] != 1} {error "M3_ACTIVE_TARGET_COUNT_MISMATCH"}
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_TARGET_STATE_OK"
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_READ_A_BEGIN"
mrd -bin -file "D:\\codex-worktrees\\w6\\report\\evidence\\R03-M3\\m3_pair_20261101_r05\\capture_before\\read_a.bin" 0x12000000 3153920
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_READ_A_OK"
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_READ_B_BEGIN"
mrd -bin -file "D:\\codex-worktrees\\w6\\report\\evidence\\R03-M3\\m3_pair_20261101_r05\\capture_before\\read_b.bin" 0x12000000 3153920
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_READ_B_OK"
puts "M3PAIR_3ba8e47047c446fda56b31009722c903_END"
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
