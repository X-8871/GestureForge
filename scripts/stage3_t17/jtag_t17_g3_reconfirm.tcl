# S3-T17 部署 G3 重确认：只读寄存器探测（stage-3 freeze closing）。
# 纪律：不 program、不复位、不写寄存器（无 mwr）、不改线；只读一律 halt→mrd→con。
# 安全闸门（沿用 2026-10-25/26 教训，避免再次打坏 DAP）：
#   1) 必须严格停到 "Stopped" 才允许读取；否则直接退出、不读取；
#   2) 只做一次探测式读；**任一 mrd 失败立即停止全部读取**（不重试、不连续失败）；
#   3) 仅在确认已 halt 的情况下执行一次 con 恢复运行。
# 用法: xsdb jtag_t17_g3_reconfirm.tcl <输出目录(空)>
# 退出码: 0=全部读取成功；2=失败（已尽量恢复运行）；3=参数错误

set outdir [lindex $argv 0]
if {$outdir eq "" || ![file isdirectory $outdir]} {
    puts "G3R_FAIL=OUTPUT_DIRECTORY_REQUIRED"
    exit 3
}
if {[llength [glob -nocomplain -directory $outdir *]] != 0} {
    puts "G3R_FAIL=OUTPUT_NOT_EMPTY"
    exit 3
}

puts "G3R_START=[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
if {[catch {connect} e]} { puts "G3R_CONNECT_FAIL=$e"; puts "G3R_EXIT=2"; exit 2 }
puts "G3R_CONNECT_OK=1"

set connected 1
set halted 0
set rc 2

if {[catch {
    set tl [targets]
    puts "G3R_TARGET_COUNT=[llength $tl]"
    foreach t $tl { puts "G3R_TARGET=$t" }

    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    puts "G3R_SEL_CORE0_OK=1"
    stop
    set st [state]
    puts "G3R_STATE_AFTER_STOP=$st"
    if {[string first "Stopped" $st] != 0} {
        puts "G3R_ABORT=STATE_NOT_STRICTLY_STOPPED（不读取任何寄存器）"
        error "state not stopped: $st"
    }
    set halted 1
    after 500

    # 单点探测式首读：失败即停止后续读取
    puts "G3R_PROBE_SR_S2MM=[mrd -force 0x43010034]"
    set reads {
        CR_S2MM    0x43010030
        VSIZE_S2MM 0x430100A0
        HSIZE_S2MM 0x430100A4
        STRIDE_S2MM 0x430100A8
        ADDR_S2MM  0x430100AC
        CR_MM2S    0x43000000
        SR_MM2S    0x43000004
        VSIZE_MM2S 0x43000050
        HSIZE_MM2S 0x43000054
        STRIDE_MM2S 0x43000058
        ADDR_MM2S  0x4300005C
    }
    foreach {name addr} $reads {
        puts "G3R_${name}=[mrd -force $addr]"
    }
    set rc 0
} fail]} {
    puts "G3R_FAIL=$fail"
    set rc 2
}

if {$halted} {
    set st2 [state]
    puts "G3R_STATE_BEFORE_CON=$st2"
    if {[string first "Stopped" $st2] == 0} {
        if {[catch {con} re]} { puts "G3R_CON_FAIL=$re"; set rc 2 } else { puts "G3R_CON_OK=1" }
    } else {
        puts "G3R_CON_SKIPPED=STATE_NOT_STOPPED"
    }
}
if {$connected} { catch {disconnect} }
puts "G3R_END=[clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts "G3R_EXIT=$rc"
exit $rc