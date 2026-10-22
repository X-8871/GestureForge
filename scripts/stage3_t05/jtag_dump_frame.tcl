# S3-T05 安全整帧转储（供把真实流水线帧喂给训练好的模型做域差实测）。
# 只读：halt → mrd -bin -file → con。用法: xsdb jtag_dump_frame.tcl <已手动创建的空目录>
# 注意：调用前须确认当前 ELF 的 FRAME0/stride（本轮为 0x00110C00 / 0x0F00 / 1280x720）。

set outdir [lindex $argv 0]
set fb     [lindex $argv 1]
if {$fb eq ""} { set fb 0x00110C00 }
if {$outdir eq "" || ![file isdirectory $outdir]} {
    puts "FRAME_DUMP_FAIL=OUTPUT_DIRECTORY_REQUIRED"
    exit 3
}
if {[llength [glob -nocomplain -directory $outdir *]] != 0} {
    puts "FRAME_DUMP_FAIL=OUTPUT_NOT_EMPTY"
    exit 3
}
puts "FRAME_DUMP_BASE_USED=$fb"

set connected 0
set halted 0
set failure ""
if {[catch {
    connect
    set connected 1
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    stop
    set halted 1
    puts "FRAME_DUMP_HALT_OK=1"
    after 300
    set base $fb
    puts "FRAME_DUMP_S2MM_FRAME0=[mrd -force 0x430100AC]"
    puts "FRAME_DUMP_S2MM_STRIDE=[mrd -force 0x430100A8]"
    # 720 行 × 960 字 = 691200 字 = 2,764,800 字节
    set path [file join $outdir frame_full.bin]
    mrd -bin -file $path $base 691200
    puts "FRAME_DUMP_OK=$path"
} failure]} {
    puts "FRAME_DUMP_FAIL=$failure"
    set rc 2
} else {
    set rc 0
}

if {$halted} {
    if {[catch {con} resume_error]} {
        puts "FRAME_DUMP_RESUME_FAIL=$resume_error"
        set rc 2
    } else {
        puts "FRAME_DUMP_RESUME_OK=1"
    }
}
if {$connected} { catch {disconnect} }
puts "FRAME_DUMP_DONE=1"
exit $rc