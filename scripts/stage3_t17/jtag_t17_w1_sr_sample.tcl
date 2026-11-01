# S3-T17 W1 只读时间序列采样：只读 S2MM_SR（0x43010034）等寄存器，观察粘滞位是否复现/新增。
# 纪律：不写寄存器（无 mwr）、不 program、不 reset；每次采样 halt→mrd→con，halt 窗口尽量短。
# 用法: xsdb jtag_t17_w1_sr_sample.tcl <输出文件> <快段次数> <快段间隔ms> <慢段次数> <慢段间隔ms>
#   例（本轮）: 72 5000 48 30000  ⇒ 6 min@5s + 24 min@30s ≈ 30 min，共 120 点
# 退出码: 0=完成；2=中途中止（已恢复运行）；3=参数错误

set outfile [lindex $argv 0]
set nf      [lindex $argv 1]
set intf    [lindex $argv 2]
set ns      [lindex $argv 3]
set ints    [lindex $argv 4]

if {$outfile eq "" || $nf eq "" || $intf eq "" || $ns eq "" || $ints eq ""} {
    puts "T17W1_SAMPLE_FAIL=ARGS_REQUIRED"
    exit 3
}
if {[catch {set fh [open $outfile a]}]} {
    puts "T17W1_SAMPLE_FAIL=OUTPUT_OPEN_FAILED"
    exit 3
}

proc emit {fh line} {
    puts $line
    puts $fh $line
    flush $fh
}

emit $fh "T17W1_SAMPLE_START=[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
emit $fh "T17W1_SAMPLE_SCHEME=fast=${nf}x${intf}ms+slow=${ns}x${ints}ms"

if {[catch {connect} conn_err]} {
    emit $fh "T17W1_SAMPLE_CONNECT_FAIL=$conn_err"
    close $fh
    puts "T17W1_SAMPLE_EXIT=2"
    exit 2
}
puts "T17W1_SAMPLE_CONNECT_OK=1"
set halted 0
set rc 2
set k 0

if {[catch {
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    # 先做一次 2 点快速差分，确认 SR 是否随时间变化（且验证采样通路）
    for {set i 0} {$i < [expr {$nf + $ns}]} {incr i} {
        if {$i < $nf} { set gap $intf } else { set gap $ints }
        stop
        set halted 1
        set ms [clock milliseconds]
        set sr [mrd -force 0x43010034]
        set cr [mrd -force 0x43010030]
        set addr [mrd -force 0x430100AC]
        set m2sr [mrd -force 0x43000004]
        con
        set halted 0
        incr k
        emit $fh [format "T17W1_SR t=%s ms=%d idx=%d SR=%s CR=%s ADDR=%s MM2S_SR=%s" \
            [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}] $ms $k $sr $cr $addr $m2sr]
        if {$i < [expr {$nf + $ns - 1}]} { after $gap }
    }
    set rc 0
} fail]} {
    emit $fh "T17W1_SAMPLE_FAIL=$fail"
}

if {$halted} {
    if {[catch {con} re]} { emit $fh "T17W1_SAMPLE_RESUME_FAIL=$re" } else { emit $fh "T17W1_SAMPLE_RESUME_OK=1" }
}
catch {disconnect}
emit $fh "T17W1_SAMPLE_POINTS=$k"
emit $fh "T17W1_SAMPLE_END=[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
close $fh
puts "T17W1_SAMPLE_EXIT=$rc"
exit $rc