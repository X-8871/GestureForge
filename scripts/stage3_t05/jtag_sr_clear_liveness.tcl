# S3-T05 SOF 修复后判定：先清 S2MM SR 的 sticky 位，再看(1)是否又出现新错误、(2)帧缓冲是否持续变化。
# 只写 VDMA 的 SR（W1C，驱动本身也这样清中断），不写 PL、不烧 QSPI；读完 con 恢复。
# 用法: xsdb jtag_sr_clear_liveness.tcl

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "SR_BEFORE=[mrd -force 0x43010034]"
mwr -force 0x43010034 0xFFFFFFFF
after 500
puts "SR_CLEARED=[mrd -force 0x43010034]"
puts "FB_T0_A=[mrd -force 0x00110C00 16]"
puts "FB_T0_B=[mrd -force 0x00190C00 16]"

after 10000
puts "SR_T10=[mrd -force 0x43010034]"
puts "FB_T10_A=[mrd -force 0x00110C00 16]"
puts "FB_T10_B=[mrd -force 0x00190C00 16]"

after 10000
puts "SR_T20=[mrd -force 0x43010034]"
puts "FB_T20_A=[mrd -force 0x00110C00 16]"
puts "FB_T20_B=[mrd -force 0x00190C00 16]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "SR_CLEAR_LIVENESS_DONE=1"