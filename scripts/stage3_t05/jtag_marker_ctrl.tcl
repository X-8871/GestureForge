# S3-T05 标记实验 v2：对照组。帧内地址 vs 帧外地址各写一个标记，各读回 3 次。
#   帧内被覆盖 + 帧外保留  => S2MM 正在连续写帧（活画面）
#   两处都保留            => 写机制正常但 S2MM 未再写（park/停）
# 只改 2 个字（易失），不写 PL、不烧 QSPI。用法: xsdb jtag_marker_ctrl.tcl

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

set in_f  0x00120C40
set out_f 0x00500000

puts "IN_BEFORE=[mrd -force $in_f 2]"
puts "OUT_BEFORE=[mrd -force $out_f 2]"

mwr -force $in_f  0xDEADBEEF
mwr -force $out_f 0xCAFEBABE
puts "IN_T0=[mrd -force $in_f 2]"
puts "OUT_T0=[mrd -force $out_f 2]"

after 1000
puts "IN_T1=[mrd -force $in_f 2]"
puts "OUT_T1=[mrd -force $out_f 2]"

after 3000
puts "IN_T4=[mrd -force $in_f 2]"
puts "OUT_T4=[mrd -force $out_f 2]"
puts "SR_T4=[mrd -force 0x43010034]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "MARKER_CTRL_DONE=1"