# 自动生成（scripts/stage5_t01/gen_dump_rows.py）用例 5 的行/列选择；勿手改。
# 用法: xsdb jtag_dump_rows_gen.tcl <buf0_hex> <port>
set ::buf0 0x00138C00
if {[lindex $argv 0] ne ""} { set ::buf0 [lindex $argv 0] }
set ::port [lindex $argv 1]
if {$::port eq ""} { set ::port 23121 }
set ::stride 3840
puts "S5_DUMP_BEGIN"
connect -url tcp:localhost:$::port
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "S5_HALT_ERR=$e" } else { puts "S5_HALT_OK=1" }
after 300
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=0 x=508"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 0 * $::stride + 1524 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 竖边
puts "S5_ROW_BEGIN row=0 x=512"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 0 * $::stride + 1536 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=0 x=1020"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 0 * $::stride + 3060 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=1 x=508"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 1 * $::stride + 1524 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=1 x=1020"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 1 * $::stride + 3060 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 竖边
puts "S5_ROW_BEGIN row=33 x=508"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 33 * $::stride + 1524 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 竖边
puts "S5_ROW_BEGIN row=33 x=512"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 33 * $::stride + 1536 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 竖边
puts "S5_ROW_BEGIN row=33 x=1020"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 33 * $::stride + 3060 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=53 x=0"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 53 * $::stride + 0 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=53 x=72"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 53 * $::stride + 216 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=54 x=0"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 54 * $::stride + 0 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=54 x=72"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 54 * $::stride + 216 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=65 x=508"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 65 * $::stride + 1524 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 竖边
puts "S5_ROW_BEGIN row=65 x=512"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 65 * $::stride + 1536 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=65 x=1020"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 65 * $::stride + 3060 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=66 x=508"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 66 * $::stride + 1524 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# PALM 0.62 横边
puts "S5_ROW_BEGIN row=66 x=1020"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 66 * $::stride + 3060 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 竖边
puts "S5_ROW_BEGIN row=239 x=0"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 239 * $::stride + 0 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 竖边
puts "S5_ROW_BEGIN row=239 x=72"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 239 * $::stride + 216 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=424 x=0"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 424 * $::stride + 0 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=424 x=72"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 424 * $::stride + 216 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=425 x=0"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 425 * $::stride + 0 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
# FIST 0.66 横边
puts "S5_ROW_BEGIN row=425 x=72"
for {set i 0} {$i < 72} {incr i} {
    set addr [expr {$::buf0 + 425 * $::stride + 216 + $i * 4}]
    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]
}
con
disconnect
puts "S5_DUMP_DONE=1"
