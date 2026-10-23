# S3-T05 只读地址事实回读（2026-10-24 阶段3 板级窗口）：为跨阶段地址不相交提供部署事实。
# 只读：halt → mrd → con；不写任何寄存器。
# 寄存器偏移沿用 Xilinx AXI VDMA 驱动定义：S2MM_ADDR_OFFSET=0xAC（+0x04 步进，3 个帧指针）、
#   MM2S_ADDR_OFFSET=0x18（+0x04 步进，3 个帧指针）；基址 0x43010000（S2MM）/ 0x43000000（MM2S）。
# 用法: xsdb jtag_addr_map_read.tcl
connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "ADDRMAP_S2MM_CR=[mrd -force 0x43010030]"
puts "ADDRMAP_S2MM_SR=[mrd -force 0x43010034]"
puts "ADDRMAP_S2MM_VSIZE=[mrd -force 0x430100A0]"
puts "ADDRMAP_S2MM_HSIZE=[mrd -force 0x430100A4]"
puts "ADDRMAP_S2MM_STRIDE=[mrd -force 0x430100A8]"
puts "ADDRMAP_S2MM_FRMPTR0=[mrd -force 0x430100AC]"
puts "ADDRMAP_S2MM_FRMPTR1=[mrd -force 0x430100B0]"
puts "ADDRMAP_S2MM_FRMPTR2=[mrd -force 0x430100B4]"
puts "ADDRMAP_MM2S_CR=[mrd -force 0x43000000]"
puts "ADDRMAP_MM2S_SR=[mrd -force 0x43000004]"
puts "ADDRMAP_MM2S_FRMPTR0=[mrd -force 0x43000018]"
puts "ADDRMAP_MM2S_FRMPTR1=[mrd -force 0x4300001C]"
puts "ADDRMAP_MM2S_FRMPTR2=[mrd -force 0x43000020]"
puts "ADDRMAP_MM2S_STRIDE=[mrd -force 0x43000028]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "ADDRMAP_DONE=1"