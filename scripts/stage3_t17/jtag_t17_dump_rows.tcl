# S3-T17 受控安全转储（只读）：halt A9#0 → mrd -bin -file → con，再 disconnect。
# 与旧 `jtag_dump_display_channels.tcl` 的区别：**基地址与 stride 必须由调用方显式给出**，
#   不内建旧地址默认值（新 ELF 可能改变 FRAME0/布局；禁止抓错地址后判颜色）。
# 用法: xsdb jtag_t17_dump_rows.tcl <新空输出目录> <base_hex> <stride_bytes> <row_y1> [row_y2 ...] [--frame]
# 退出码: 3=参数/目录错误；2=运行失败（已尽量恢复运行）；0=全部成功

set outdir [lindex $argv 0]
set base   [lindex $argv 1]
set stride [lindex $argv 2]

if {$outdir eq "" || ![file isdirectory $outdir]} {
    puts "T17_DUMP_FAIL=OUTPUT_DIRECTORY_REQUIRED"
    exit 3
}
if {[llength [glob -nocomplain -directory $outdir *]] != 0} {
    puts "T17_DUMP_FAIL=OUTPUT_NOT_EMPTY"
    exit 3
}
if {![regexp {^0[xX][0-9a-fA-F]+$} $base]} {
    puts "T17_DUMP_FAIL=BASE_HEX_REQUIRED（不接受默认/旧地址，必须显式给出）"
    exit 3
}
if {![string is integer -strict $stride] || $stride <= 0} {
    puts "T17_DUMP_FAIL=STRIDE_POSITIVE_INTEGER_REQUIRED"
    exit 3
}

set rows {}
set want_frame 0
foreach arg [lrange $argv 3 end] {
    if {$arg eq "--frame"} {
        set want_frame 1
    } elseif {[string is integer -strict $arg] && $arg >= 0} {
        lappend rows $arg
    } else {
        puts "T17_DUMP_FAIL=BAD_ROW_ARG=$arg"
        exit 3
    }
}
if {[llength $rows] == 0 && !$want_frame} {
    puts "T17_DUMP_FAIL=NO_ROWS_OR_FRAME_REQUESTED"
    exit 3
}

puts "T17_DUMP_BASE_USED=$base"
puts "T17_DUMP_STRIDE_USED=$stride"
puts "T17_DUMP_ROWS=$rows"
puts "T17_DUMP_WANT_FRAME=$want_frame"

set connected 0
set halted 0
if {[catch {
    connect
    set connected 1
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    stop
    set halted 1
    puts "T17_DUMP_HALT_OK=1"
    after 300
    puts "T17_DUMP_S2MM_FRAME0=[mrd -force 0x430100AC]"
    puts "T17_DUMP_S2MM_STRIDE=[mrd -force 0x430100A8]"
    puts "T17_DUMP_S2MM_HSIZE=[mrd -force 0x430100A4]"
    puts "T17_DUMP_S2MM_VSIZE=[mrd -force 0x430100A0]"
    puts "T17_DUMP_S2MM_SR=[mrd -force 0x43010034]"
    puts "T17_DUMP_MM2S_SR=[mrd -force 0x43000004]"
    foreach y $rows {
        set addr [expr {$base + $y * $stride}]
        set path [file join $outdir [format "row_y%d.bin" $y]]
        mrd -bin -file $path $addr 960
        set size [file size $path]
        puts "T17_DUMP_ROW_OK=$y:$path:bytes=$size"
        if {$size != 3840} { puts "T17_DUMP_ROW_SIZE_MISMATCH=$y:$size" ; error "row $y size $size != 3840" }
    }
    if {$want_frame} {
        set path [file join $outdir frame_full.bin]
        mrd -bin -file $path $base 691200
        set size [file size $path]
        puts "T17_DUMP_FRAME_OK=$path:bytes=$size"
        if {$size != 2764800} { puts "T17_DUMP_FRAME_SIZE_MISMATCH=$size" ; error "frame size $size != 2764800" }
    }
} failure]} {
    puts "T17_DUMP_FAIL=$failure"
    set rc 2
} else {
    set rc 0
}

if {$halted} {
    if {[catch {con} resume_err]} {
        puts "T17_DUMP_RESUME_FAIL=$resume_err"
        set rc 2
    } else {
        puts "T17_DUMP_RESUME_OK=1"
    }
}
if {$connected} { catch {disconnect} }
puts "T17_DUMP_EXIT=$rc"
exit $rc