# S3-T05 只读寄存器扫描（2026-10-24 窗口）：为「采集与显示是否共用帧缓冲」提供板上事实。
# 只读：halt → mrd → con。扫描 AXI VDMA 两个通道的地址/杂项寄存器区，找出实际持有的 DDR 地址。
# 用法: xsdb jtag_addr_scan.tcl
connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "--- MM2S 0x00..0x2C ---"
foreach off {0x00 0x04 0x10 0x14 0x18 0x1C 0x20 0x24 0x28 0x2C} {
    puts [format "SCAN_MM2S_%s=%s" $off [mrd -force [expr {0x43000000 + $off}]]]
}
puts "--- S2MM 0x30..0x3C 与 0xA0..0xB8 ---"
foreach off {0x30 0x34 0x38 0x3C} {
    puts [format "SCAN_S2MM_%s=%s" $off [mrd -force [expr {0x43010000 + $off}]]]
}
foreach off {0xA0 0xA4 0xA8 0xAC 0xB0 0xB4 0xB8 0xBC} {
    puts [format "SCAN_S2MM_%s=%s" $off [mrd -force [expr {0x43010000 + $off}]]]
}

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "ADDR_SCAN_DONE=1"