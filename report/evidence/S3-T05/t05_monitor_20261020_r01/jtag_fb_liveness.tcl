# S3-T05 在线活性采样：两次读同一帧缓冲位置，判断“冻结帧”还是“活画面”。
# 只读（halt→mrd→con），不写任何寄存器。用法: xsdb jtag_fb_liveness.tcl

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "T1_SITE0=[mrd -force 0x00110C00 16]"
puts "T1_MID=[mrd -force 0x00150C00 16]"
puts "T1_ROW136=[mrd -force 0x00190C00 16]"
after 8000
puts "T2_SITE0=[mrd -force 0x00110C00 16]"
puts "T2_MID=[mrd -force 0x00150C00 16]"
puts "T2_ROW136=[mrd -force 0x00190C00 16]"
after 8000
puts "T3_SITE0=[mrd -force 0x00110C00 16]"
puts "SR_S2MM=[mrd -force 0x43010034]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "FB_LIVENESS_DONE=1"