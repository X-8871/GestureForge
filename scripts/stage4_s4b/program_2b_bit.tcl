# 装载已登记的 2B 位流到 PL（窗口 B 用；不烧 QSPI、不改线）
# 用法：vivado -mode batch -source program_2b_bit.tcl -tclargs <bit 路径> <期望 SHA256>
# 成功判据：日志出现 PROGRAM_OK（且 PROGRAM.IS_DONE=1）

set bit    [lindex $argv 0]
set expect [lindex $argv 1]

if {![file isfile $bit]} {
    puts "PROGRAM_FAIL=bit_missing:$bit"
    exit 2
}
puts "PROGRAM_BIT=$bit"
puts "PROGRAM_SHA_EXPECT=$expect"

open_hw_manager
connect_hw_server -url localhost:3121
open_hw_target
set devs [get_hw_devices xc7z020*]
if {[llength $devs] == 0} {
    puts "PROGRAM_FAIL=no_xc7z020_device"
    exit 3
}
set dev [lindex $devs 0]
current_hw_device $dev
set_property PROGRAM.FILE $bit $dev
program_hw_devices $dev
refresh_hw_device -update_hw_probes false $dev
set done [get_property PROGRAM.IS_DONE $dev]
puts "PROGRAM_IS_DONE=$done"
close_hw_target
disconnect_hw_server
close_hw_manager
if {$done != 1} {
    puts "PROGRAM_FAIL=not_done"
    exit 4
}
puts "PROGRAM_OK"
exit 0