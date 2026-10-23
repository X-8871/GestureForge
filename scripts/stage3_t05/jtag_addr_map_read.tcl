# S3-T05 只读地址事实回读（2026-10-24 阶段3 板级窗口）：为跨阶段地址不相交提供部署事实。
# 只读：halt → mrd → con；不写任何寄存器。
# 寄存器偏移（**本设计实测修正版**，评审 N-3）：S2MM 通道 0xA0/0xA4/0xA8/0xAC = VSIZE/HSIZE/STRIDE/帧地址
#   （0xB0/0xB4 为 0，单缓冲）；MM2S 通道 **0x50/0x54/0x58/0x5C** = VSIZE/HSIZE/STRIDE/帧地址。
#   旧版误把 MM2S 标在 0x18/0x1C/0x20/0x28（读回全 0，非地址寄存器），已更正；见
#   report/evidence/S3-T05/t05_stage3_window_20261024_r01/addr_map_mislabel_correction.md。
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
puts "ADDRMAP_MM2S_VSIZE=[mrd -force 0x43000050]"
puts "ADDRMAP_MM2S_HSIZE=[mrd -force 0x43000054]"
puts "ADDRMAP_MM2S_STRIDE=[mrd -force 0x43000058]"
puts "ADDRMAP_MM2S_FRMPTR0=[mrd -force 0x4300005C]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "ADDRMAP_DONE=1"