# 阶段3 在线实验：改 S2MM 的 VSIZE 并重启通道，用 SR 错误位判断真实帧行数。
#   FSZ_LESS(0x80)  => 实际帧比配置的少
#   FSZ_MORE(0x800) => 实际帧比配置的多
# 只在本轮实验中使用；不写 QSPI、不改 PL。用法: xsdb jtag_s2mm_vsize_trial.tcl <vsize_hex>
# 注意：会停止/重启摄像头 VDMA（易失、可恢复：重下应用即可）

set vsize [lindex $argv 0]
if {$vsize eq ""} { set vsize 0x2D1 }
puts "TRIAL_VSIZE=$vsize"

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}

# 1) 停通道
mwr -force 0x43010030 0x00018002
after 200
# 2) 复位通道并清粘滞状态
mwr -force 0x43010030 0x00000004
after 200
mwr -force 0x43010030 0x00000000
after 200
mwr -force 0x43010034 0xFFFFFFFF
after 200
# 3) 重新编程尺寸/步长/地址（VSIZE 用试验值）
mwr -force 0x430100A0 $vsize
mwr -force 0x430100A4 0x00000F00
mwr -force 0x430100A8 0x00000F00
mwr -force 0x430100AC 0x00110C00
mwr -force 0x430100B0 0x00000000
# 4) 启动
mwr -force 0x43010030 0x00018003
after 5000

puts "TRIAL_SR=[mrd -force 0x43010034]"
puts "TRIAL_FRAME=[mrd -force 0x00110C00 4]"
puts "TRIAL_FRAME_MID=[mrd -force 0x00130C00 4]"
puts "TRIAL_DONE=1"