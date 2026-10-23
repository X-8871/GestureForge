# S3-T05 只读：MM2S 通道地址区扩扫（按 S2MM 布局对称推断通道基址+0x70..0x7C）。
# 只读：halt → mrd → con。用法: xsdb jtag_addr_scan_mm2s.tcl
connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300
foreach off {0x40 0x44 0x48 0x4C 0x50 0x54 0x58 0x5C 0x60 0x64 0x68 0x6C 0x70 0x74 0x78 0x7C} {
    puts [format "MM2S_SCAN_%s=%s" $off [mrd -force [expr {0x43000000 + $off}]]]
}
if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "MM2S_SCAN_DONE=1"