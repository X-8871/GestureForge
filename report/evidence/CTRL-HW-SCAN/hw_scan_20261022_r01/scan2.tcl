# 极短只读 JTAG 扫描 v2（显式打印目标数量，避免空输出歧义）
puts "SCAN2_START=1"
if {[catch {connect -url tcp:127.0.0.1:3121} err]} {
    puts "SCAN2_CONNECT_FAIL=$err"
    exit 4
}
puts "SCAN2_CONNECTED=1"
if {[catch {set tg [targets]} terr]} {
    puts "SCAN2_TARGETS_FAIL=$terr"
    set tg {}
}
puts "SCAN2_TARGET_COUNT=[llength $tg]"
foreach t $tg { puts "SCAN2_TARGET=[string trim $t]" }
if {[catch {set jt [jtag targets]} jerr]} {
    puts "SCAN2_JTAG_CMD_UNAVAILABLE=$jerr"
} else {
    puts "SCAN2_JTAG_CHAIN=[string trim $jt]"
}
catch {disconnect}
puts "SCAN2_DISCONNECTED=1"
exit 0