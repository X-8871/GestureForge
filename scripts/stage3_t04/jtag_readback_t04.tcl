# 阶段3 T04 板上寄存器回读：两个 VDMA（显示读/摄像头写）+ dynclk + v_tc + cmos_rst。
# 只读；不写寄存器、不复位、不烧录。
# 用法: xsdb jtag_readback_t04.tcl

puts "T04_RB_START"
connect
puts "T04_RB_TARGETS_BEGIN"
puts [targets]
puts "T04_RB_TARGETS_END"
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}

puts "T04_RB_DISPLAY_VDMA_CR_43000000=[mrd -force 0x43000000]"
puts "T04_RB_DISPLAY_VDMA_SR_43000004=[mrd -force 0x43000004]"
# 注意：VDMA 的 S2MM 寄存器组在 +0x30（CR=+0x30, SR=+0x34）；MM2S 在 +0x00
puts "T04_RB_CAMERA_VDMA_CR_43010030=[mrd -force 0x43010030]"
puts "T04_RB_CAMERA_VDMA_SR_43010034=[mrd -force 0x43010034]"
puts "T04_RB_CAMERA_VDMA_STARTADDR_43010038=[mrd -force 0x43010038]"
puts "T04_RB_CAMERA_VDMA_RSVD_43010000=[mrd -force 0x43010000]"
puts "T04_RB_CMOS_RST_41200000=[mrd -force 0x41200000]"
puts "T04_RB_VTC_CTRL_43C00000=[mrd -force 0x43C00000]"
puts "T04_RB_VTC_STATUS_43C00004=[mrd -force 0x43C00004]"
puts "T04_RB_DYNCLK_CTRL_43C10000=[mrd -force 0x43C10000]"
puts "T04_RB_DYNCLK_STATUS_43C10004=[mrd -force 0x43C10004]"
puts "T04_RB_DYNCLK_LOCK_L_43C10018=[mrd -force 0x43C10018]"
puts "T04_RB_ALL_DONE=1"