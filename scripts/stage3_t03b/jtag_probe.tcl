# 阶段3 JTAG 只读探测：确认板卡可达、JTAG 链路与目标核存在；不下载、不复位、不烧录。
# 用法: xsct jtag_probe.tcl

puts "XSCT_PROBE_START"
connect
puts "XSCT_CONNECTED=1"
puts "XSCT_TARGETS_BEGIN"
puts [targets]
puts "XSCT_TARGETS_END"
disconnect
puts "XSCT_DISCONNECTED=1"