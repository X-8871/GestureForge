# S3-T05 彩条整行转储：把 y=360 行（3840 B）二进制转储到文件，供主机侧分析条的边界与真实三元组。
# 只读。用法: xsdb jtag_dump_row.tcl <out_bin>

set out [lindex $argv 0]
if {$out eq ""} { set out "D:/codex-worktrees/dbdf/tmp/3/S3-CTRL/t05_live_r01/row360.bin" }

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

set base 0x00110C00
set y 360
set rowstart [expr {$base + $y * 3840}]
puts "ROWSTART=0x[format %06X $rowstart]"
if {[catch {mrd -bin -file $out $rowstart 960} e2]} {
    puts "MRD_BIN_ERR=$e2"
    # 退路：分块普通读，打印前 60 个字
    puts "FALLBACK_HEAD=[mrd -force $rowstart 60]"
} else {
    puts "MRD_BIN_OK=$out"
}

if {[catch {con} e3]} { puts "CON_ERR=$e3" } else { puts "CON_OK=1" }
disconnect
puts "DUMP_ROW_DONE=1"