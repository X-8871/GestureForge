# S3-T05 彩条像素实测：从 DDR 帧缓冲里读 8 条彩条中心像素的原始字节，判断偏色发生在传感器侧还是显示侧。
# 只读（halt→mrd→con），不写任何寄存器。用法: xsdb jtag_colorbars_pixels.tcl
# 帧缓冲 base=0x00110C00，行 stride=3840 字节，1280 像素/行，3 字节/像素。
# 彩条 8 条各占 160 像素：中心 x = 80,240,400,560,720,880,1040,1200；取 y=360（画面中部）。

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

set base 0x00110C00
set stride 3840
set y 360
foreach {bar x} {1 80 2 240 3 400 4 560 5 720 6 880 7 1040 8 1200} {
    set off [expr {$y * $stride + $x * 3}]
    set addr [expr {$base + ($off & ~3)}]
    set w [mrd -force $addr]
    puts "BAR$bar x=$x off=0x[format %06X $off] $w"
}

# 另取同一行的 4 个相邻像素原始字节（x=8..12），便于确认字节序与像素对齐
set off0 [expr {$y * $stride + 8 * 3}]
set addr0 [expr {$base + ($off0 & ~3)}]
puts "ROW_RAW_ALIGNED=[mrd -force $addr0 4]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "COLORBARS_PIXELS_DONE=1"