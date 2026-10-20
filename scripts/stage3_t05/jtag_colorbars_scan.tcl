# S3-T05 彩条逐条取样 v2：在 y=360 行上取 8 个「条起点」各 6 个连续字（每字 4 字节 = 1⅓ 像素），
# 用于判定彩条是否为我假设的 8×160 像素实心条、以及每个条的真实字节三元组（通道顺序 + 是否偏色）。
# 只读。用法: xsdb jtag_colorbars_scan.tcl

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

set base 0x00110C00
set stride 3840
set y 360
set rowstart [expr {$base + $y * $stride}]
puts "ROWSTART=0x[format %06X $rowstart]"

for {set b 0} {$b < 8} {incr b} {
    set x [expr {$b * 160}]
    set addr [expr {$rowstart + $x * 3}]
    puts "BAR[expr {$b+1}]_x=$x addr=0x[format %06X $addr] [mrd -force $addr 6]"
}

# 行首 8 个字（含最左像素）与行尾 8 个字（黑条）
puts "ROW_HEAD=[mrd -force $rowstart 8]"
set tail [expr {$rowstart + 3840 - 32}]
puts "ROW_TAIL=0x[format %06X $tail] [mrd -force $tail 8]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "COLORBARS_SCAN_DONE=1"