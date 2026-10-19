# 阶段3 VDMA 尺寸/步长/起始地址寄存器回读（正确偏移）。
# 依据 axivdma_v6_17 头文件：MM2S 通道地址区基址 = 实例基址+0x50，S2MM = +0xA0；
#   VSIZE=+0x00, HSIZE=+0x04, STRD_FRMDLY=+0x08, START_ADDR=+0x0C, START_ADDR_MSB=+0x10
# 只读。用法: xsdb jtag_vdma_addr.tcl

puts "VDMA_ADDR_START"
connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
puts "MM2S_CFG_43000050（VSIZE,HSIZE,STRIDE,ADDR,ADDR_MSB）:"
puts [mrd -force 0x43000050 5]
puts "S2MM_CFG_430100A0（VSIZE,HSIZE,STRIDE,ADDR,ADDR_MSB）:"
puts [mrd -force 0x430100A0 5]
puts "S2MM_ADDR_LIST_430100B0:"
puts [mrd -force 0x430100B0 8]
puts "VDMA_ADDR_ALL_DONE=1"