# S3-T17 W1 只读探测（窗口前置一次性）：链路+部署状态+VDMA 配置全量回读+帧缓冲指纹（DDR 只读）。
# 纪律：不写寄存器、不 program、不 reset；halt→读→con；仅 mrd 与 mrd -bin -file。
# 用法: xsdb jtag_t17_w1_probe.tcl <输出目录(空)>
# 退出码: 0=成功；2=失败（已尽量恢复运行）；3=参数错误

set outdir [lindex $argv 0]
if {$outdir eq "" || ![file isdirectory $outdir]} {
    puts "T17W1_PROBE_FAIL=OUTPUT_DIRECTORY_REQUIRED"
    exit 3
}
if {[llength [glob -nocomplain -directory $outdir *]] != 0} {
    puts "T17W1_PROBE_FAIL=OUTPUT_NOT_EMPTY"
    exit 3
}

puts "T17W1_PROBE_START=[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"

if {[catch {connect} conn_err]} {
    puts "T17W1_CONNECT_FAIL=$conn_err"
    puts "T17W1_PROBE_EXIT=2"
    exit 2
}
puts "T17W1_CONNECT_OK=1"

# 链路身份（陷阱：裸 targets 在被重定向时不打印；用 jtag targets 判链）
if {[catch {set chain [jtag targets]} chain_err]} {
    puts "T17W1_JTAG_CHAIN_FAIL=$chain_err"
} else {
    puts "T17W1_JTAG_CHAIN_COUNT=[llength $chain]"
    foreach c $chain { puts "T17W1_JTAG_CHAIN_ITEM=$c" }
}
set connected 1
set halted 0
set rc 2

if {[catch {
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    stop
    set halted 1
    puts "T17W1_HALT_OK=1"
    after 300

    # --- S2MM（采集）寄存器 ---
    puts "T17W1_S2MM_CR=[mrd -force 0x43010030]"
    puts "T17W1_S2MM_SR=[mrd -force 0x43010034]"
    puts "T17W1_S2MM_VSIZE=[mrd -force 0x430100A0]"
    puts "T17W1_S2MM_HSIZE=[mrd -force 0x430100A4]"
    puts "T17W1_S2MM_STRIDE=[mrd -force 0x430100A8]"
    puts "T17W1_S2MM_ADDR=[mrd -force 0x430100AC]"
    # --- MM2S（显示）寄存器 ---
    puts "T17W1_MM2S_CR=[mrd -force 0x43000000]"
    puts "T17W1_MM2S_SR=[mrd -force 0x43000004]"
    puts "T17W1_MM2S_VSIZE=[mrd -force 0x43000050]"
    puts "T17W1_MM2S_HSIZE=[mrd -force 0x43000054]"
    puts "T17W1_MM2S_STRIDE=[mrd -force 0x43000058]"
    puts "T17W1_MM2S_ADDR=[mrd -force 0x4300005C]"

    # --- 帧缓冲指纹（DDR 只读，3 区 × 64 KiB；与 S3_DIAG6 同口径地址偏移）---
    foreach {tag off} {site0 0x000000 site1 0x080000 site2 0x100000} {
        set addr [expr {0x00110C00 + $off}]
        set path [file join $outdir [format "fp_%s.bin" $tag]]
        mrd -bin -file $path $addr 16384
        puts "T17W1_FP_${tag}_ADDR=[format 0x%08X $addr]"
        puts "T17W1_FP_${tag}_BYTES=[file size $path]"
    }
    set rc 0
} fail]} {
    puts "T17W1_PROBE_FAIL=$fail"
}

if {$halted} {
    if {[catch {con} resume_err]} {
        puts "T17W1_RESUME_FAIL=$resume_err"
        set rc 2
    } else {
        puts "T17W1_RESUME_OK=1"
    }
}
if {$connected} { catch {disconnect} }
puts "T17W1_PROBE_END=[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts "T17W1_PROBE_EXIT=$rc"
exit $rc