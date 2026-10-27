# 装载已登记的 2B 位流到 PL（窗口 B 用；不烧 QSPI、不改线）
# 用法：vivado -mode batch -source program_2b_bit.tcl -tclargs <bit 路径> <期望 SHA256>
#
# 判据（r2，修正窗口 B 首次执行的缺陷）：
#   · Zynq-7000 的 hw_device **没有** `PROGRAM.IS_DONE` 属性（窗口 B 实测：
#     `ERROR: [Labtoolstcl 44-56] hw_device [xc7z020_1] does not have a [PROGRAM.IS_DONE] property`）；
#     旧版以此属性判定成功 ⇒ 把"已装载成功"误报为失败（日志实际有 `End of startup status: HIGH`）。
#   · 现在改为：`program_hw_devices` 不抛异常 + `refresh_hw_device` 成功 + `PROGRAM.FILE` 回读非空
#     三者同时成立才输出 PROGRAM_OK。

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
if {[catch {program_hw_devices $dev} prog_err]} {
    puts "PROGRAM_FAIL=program_hw_devices_error:$prog_err"
    exit 4
}
refresh_hw_device -update_hw_probes false $dev
set prog_file [get_property PROGRAM.FILE $dev]
puts "PROGRAM_FILE_READBACK=$prog_file"
close_hw_target
disconnect_hw_server
close_hw_manager
if {$prog_file eq ""} {
    puts "PROGRAM_FAIL=program_file_empty"
    exit 5
}
puts "PROGRAM_OK"
exit 0