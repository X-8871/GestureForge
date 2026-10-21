# 阶段3蓝通道复核：仅在成功暂停 A9 后读取寄存器和三行 DDR，失败仍尝试恢复运行。
# 用法：xsdb jtag_dump_display_channels.tcl <已创建的新输出目录>
# 本脚本不复位、不下载、不写外设寄存器；输出目录不得已有任何文件。

set outdir [lindex $argv 0]
if {$outdir eq "" || ![file isdirectory $outdir]} {
    puts "CHANNEL_DUMP_FAIL=OUTPUT_DIRECTORY_REQUIRED"
    exit 3
}
if {[llength [glob -nocomplain -directory $outdir *]] != 0} {
    puts "CHANNEL_DUMP_FAIL=OUTPUT_NOT_EMPTY"
    exit 3
}

set connected 0
set halted 0
set failure ""
if {[catch {
    connect
    set connected 1
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    stop
    set halted 1
    puts "CHANNEL_DUMP_HALT_OK=1"
    after 300
    foreach {name addr} {
        S2MM_CR 0x43010030 S2MM_SR 0x43010034
        S2MM_VSIZE 0x430100A0 S2MM_HSIZE 0x430100A4
        S2MM_STRIDE 0x430100A8 S2MM_FRAME0 0x430100AC
        MM2S_SR 0x43000004
    } {
        puts "CHANNEL_DUMP_${name}=[mrd -force $addr]"
    }
    set base 0x00110C00
    foreach y {100 400 600} {
        set addr [expr {$base + $y * 3840}]
        set path [file join $outdir [format "row_y%d.bin" $y]]
        mrd -bin -file $path $addr 960
        puts "CHANNEL_DUMP_ROW_OK=$y:$path"
    }
} failure]} {
    puts "CHANNEL_DUMP_FAIL=$failure"
    set rc 2
} else {
    set rc 0
}

if {$halted} {
    if {[catch {con} resume_error]} {
        puts "CHANNEL_DUMP_RESUME_FAIL=$resume_error"
        set rc 2
    } else {
        puts "CHANNEL_DUMP_RESUME_OK=1"
    }
}
if {$connected} {
    if {[catch {disconnect} disconnect_error]} {
        puts "CHANNEL_DUMP_DISCONNECT_FAIL=$disconnect_error"
        set rc 2
    }
}
puts "CHANNEL_DUMP_EXIT=$rc"
exit $rc
