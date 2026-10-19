# 阶段3 T04 摄像头链路只读探测：帧缓冲内容 + 摄像头 VDMA + cmos_rst + PS I2C 控制器状态。
# 只读，不写寄存器、不复位。
# 用法: xsdb jtag_camera_probe.tcl
# 符号来自 tmp/s3r06/t04_camera_diag2_r02/app/an5642_single_diag2.elf：
#   frameBuf=0x00110C00  pFrames=0x00110080  dispCtrl=0x00110A60

puts "T04_CAM_START"
connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}

puts "T04_CAM_PFRAMES=[mrd -force 0x00110080 4]"
puts "T04_CAM_FRAMEBUF_HEAD=[mrd -force 0x00110C00 8]"
puts "T04_CAM_FRAMEBUF_MID=[mrd -force 0x00140C00 8]"
puts "T04_CAM_CAMERA_VDMA_CR=[mrd -force 0x43010030]"
puts "T04_CAM_CAMERA_VDMA_SR=[mrd -force 0x43010034]"
puts "T04_CAM_DISPLAY_VDMA_CR=[mrd -force 0x43000000]"
puts "T04_CAM_DISPLAY_VDMA_SR=[mrd -force 0x43000004]"
puts "T04_CAM_CMOS_RST_GPIO=[mrd -force 0x41200000]"
puts "T04_CAM_DYNCLK_STATUS=[mrd -force 0x43C10004]"
puts "T04_CAM_IIC_CR=[mrd -force 0xE0004000]"
puts "T04_CAM_IIC_SR=[mrd -force 0xE0004004]"
puts "T04_CAM_IIC_ADDR=[mrd -force 0xE0004008]"
puts "T04_CAM_IIC_ISR=[mrd -force 0xE0004010]"
puts "T04_CAM_ALL_DONE=1"