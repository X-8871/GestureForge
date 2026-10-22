# 极短只读 JTAG 扫描（Wong 2026-10-22 授权）
# 只做 connect / targets / disconnect；不 program、不烧录、不重配板卡、不写任何寄存器。
puts "SCAN_START=1"
if {[catch {connect -url tcp:127.0.0.1:3121} err]} {
    puts "SCAN_CONNECT_FAIL=$err"
    exit 4
}
puts "SCAN_CONNECTED=1"
puts "SCAN_TARGETS_BEGIN"
if {[catch {targets} terr]} {
    puts "SCAN_TARGETS_FAIL=$terr"
} else {
    puts "SCAN_TARGETS_DONE=1"
}
puts "SCAN_TARGETS_END"
if {[catch {disconnect} derr]} {
    puts "SCAN_DISCONNECT_FAIL=$derr"
} else {
    puts "SCAN_DISCONNECTED=1"
}
exit 0