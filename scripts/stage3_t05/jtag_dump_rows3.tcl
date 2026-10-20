# S3-T05 三行转储：y=100 / 400 / 600 各 3840 字节，用于判定「上半黑下半亮」是场景内容还是采集错位，
# 并检查亮区里蓝通道能否出现 >127（B[4] 是否仍在）。
# 只读。用法: xsdb jtag_dump_rows3.tcl <out_dir>

set outdir [lindex $argv 0]
if {$outdir eq ""} { set outdir "D:/codex-worktrees/dbdf/tmp/3/S3-CTRL/t05_live_r01" }

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

set base 0x00110C00
foreach y {100 400 600} {
    set addr [expr {$base + $y * 3840}]
    set f [format "%s/row_y%d.bin" $outdir $y]
    if {[catch {mrd -bin -file $f $addr 960} e2]} {
        puts "ROW_ERR y=$y $e2"
    } else {
        puts "ROW_OK y=$y addr=0x[format %06X $addr] file=$f"
    }
}

if {[catch {con} e3]} { puts "CON_ERR=$e3" } else { puts "CON_OK=1" }
disconnect
puts "DUMP_ROWS3_DONE=1"