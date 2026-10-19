# 阶段3 T03 板上寄存器回读：确认 PS 应用已配置 dynclk / VDMA / v_tc，并核对帧缓冲已写入图像数据。
# 只读；不写寄存器、不烧录。
# 用法: xsdb jtag_readback_t03.tcl

puts "T03_RB_START"
connect
puts "T03_RB_TARGETS_BEGIN"
puts [targets]
puts "T03_RB_TARGETS_END"
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}

puts "T03_RB_DYNCLK_CTRL=[mrd -force 0x43C10000]"
puts "T03_RB_DYNCLK_STATUS=[mrd -force 0x43C10004]"
puts "T03_RB_DYNCLK_CLK_L=[mrd -force 0x43C10008]"
puts "T03_RB_DYNCLK_FB_L=[mrd -force 0x43C1000C]"
puts "T03_RB_DYNCLK_DIV=[mrd -force 0x43C10014]"
puts "T03_RB_DYNCLK_LOCK_L=[mrd -force 0x43C10018]"
puts "T03_RB_VDMA_MM2S_VDMASR=[mrd -force 0x43000004]"
puts "T03_RB_VDMA_MM2S_CR=[mrd -force 0x43000000]"
puts "T03_RB_VTC_CTRL=[mrd -force 0x43C00000]"
puts "T03_RB_VTC_STATUS=[mrd -force 0x43C00004]"
puts "T03_RB_FRAMEBUF_HEAD=[mrd -force 0x26CBC0 4]"
puts "T03_RB_FRAMEBUF_MID=[mrd -force 0x280000 4]"
puts "T03_RB_DISPCTRL=[mrd -force 0x26CA20 8]"
puts "T03_RB_ALL_DONE=1"