# S3-T05 判定 DMA 是否已“换帧存地址”：读 S2MM 各 frame store 地址寄存器 + 低端 DDR 若干点。
# 只读（halt→mrd→con）。用法: xsdb jtag_framestore_probe.tcl

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "SR=[mrd -force 0x43010034]"
puts "CR=[mrd -force 0x43010030]"
puts "PARKPTR=[mrd -force 0x43010028]"
puts "FS1=[mrd -force 0x430100AC]"
puts "FS2=[mrd -force 0x430100B0]"
puts "FS3=[mrd -force 0x430100B4]"
puts "FS4=[mrd -force 0x430100B8]"
puts "DDR_000000=[mrd -force 0x00000000 8]"
puts "DDR_001000=[mrd -force 0x00001000 8]"
puts "DDR_010000=[mrd -force 0x00010000 8]"
puts "DDR_100000=[mrd -force 0x00100000 8]"
puts "DDR_200000=[mrd -force 0x00200000 8]"
puts "DDR_300000=[mrd -force 0x00300000 8]"
puts "DDR_FB_A=[mrd -force 0x00110C00 8]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "FRAMESTORE_PROBE_DONE=1"