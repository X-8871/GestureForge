# S3-T17 只读 JTAG 链路确认（阶段 B 第一步；不 program、不复位、不写寄存器）。
# 陷阱（2026-10-22 教训）：xsdb 输出被重定向时**裸 `targets` 不打印**，
#   不得据此误报“没接上”；必须用 `llength [targets]` 或 `jtag targets` 判定。
# 用法: xsdb jtag_t17_link_check.tcl
# 退出码: 0=链路有目标；1=连上但 0 目标；2=connect 失败

if {[catch {connect} conn_err]} {
    puts "T17_JTAG_CONNECT_FAIL=$conn_err"
    puts "T17_JTAG_LINK=NO_CONNECT"
    puts "T17_JTAG_EXIT=2"
    exit 2
}

set n 0
if {[catch {set n [llength [targets]]} targets_err]} {
    puts "T17_JTAG_TARGETS_LLENGTH_FAIL=$targets_err"
}
puts "T17_JTAG_TARGET_COUNT=$n"

if {[catch {set tlist [targets]} targets_list_err]} {
    puts "T17_JTAG_TARGETS_LIST_FAIL=$targets_list_err"
} else {
    foreach t $tlist { puts "T17_JTAG_TARGET=$t" }
}

if {[catch {set chain [jtag targets]} chain_err]} {
    puts "T17_JTAG_CHAIN_FAIL=$chain_err"
} else {
    puts "T17_JTAG_CHAIN_COUNT=[llength $chain]"
    foreach c $chain { puts "T17_JTAG_CHAIN_ITEM=$c" }
}

if {$n <= 0} {
    puts "T17_JTAG_LINK=NO_TARGETS"
    set rc 1
} else {
    puts "T17_JTAG_LINK=OK"
    set rc 0
}

catch {disconnect}
puts "T17_JTAG_EXIT=$rc"
exit $rc