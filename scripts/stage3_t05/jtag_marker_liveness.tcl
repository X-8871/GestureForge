# S3-T05 决定性活性实验：向帧缓冲写一个标记字，看它是否被 DMA 的新帧覆盖。
#   标记仍在  => S2MM 已停止刷新（park/停）
#   标记被覆盖 => S2MM 仍在连续写帧（活画面）
# 只改帧缓冲里的 1 个字（易失、只影响 1 像素），不写 PL、不烧 QSPI。用法: xsdb jtag_marker_liveness.tcl

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

# 先清 sticky，便于观察是否有新错误
mwr -force 0x43010034 0xFFFFFFFF
after 300
puts "SR_CLEARED=[mrd -force 0x43010034]"

set addr 0x00120C40
puts "BEFORE=[mrd -force $addr 4]"
mwr -force $addr 0xDEADBEEF
after 200
puts "WRITTEN=[mrd -force $addr 4]"

after 3000
puts "AFTER_3S=[mrd -force $addr 4]"
puts "SR_3S=[mrd -force 0x43010034]"

after 3000
puts "AFTER_6S=[mrd -force $addr 4]"
puts "SR_6S=[mrd -force 0x43010034]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "MARKER_LIVENESS_DONE=1"