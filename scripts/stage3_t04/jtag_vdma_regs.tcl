# 阶段3 VDMA 寄存器全量回读：S2MM（摄像头写）与 MM2S（显示读）各 16 个字。
# 只读，不写寄存器、不复位。
# 用法: xsdb jtag_vdma_regs.tcl

puts "VDMA_REGS_START"
connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
puts "VDMA_MM2S_REGS_43000000:"
puts [mrd -force 0x43000000 16]
puts "VDMA_S2MM_REGS_43010030:"
puts [mrd -force 0x43010030 16]
puts "VDMA_S2MM_REGS_43010070:"
puts [mrd -force 0x43010070 8]
puts "VDMA_REGS_ALL_DONE=1"