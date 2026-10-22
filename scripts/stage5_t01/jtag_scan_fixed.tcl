# S5-T01 链探测（修正版，程序化判据）：绝不使用裸 `targets` 作为“是否接上”的证据。
#
# 判据来源（Wong 2026-10-22 13:41 的 CTRL-HW-SCAN/hw_scan_20261022_r01 反例）：
#   - 裸 `targets` 在**输出重定向**下不打印表格，看起来“没有目标”，极易误判为板卡未接；
#   - 正确做法：`set tg [targets]; llength $tg` 计数 > 0，并用 `jtag targets` 打印链（电缆/器件/idcode）。
#
# 注意：xsdb 即使 tcl 报错也返回 0 ⇒ **必须检查输出标记**，不能只信退出码。
# 本脚本只读：不 halt、不写寄存器、不下载。全部 catch，最后 disconnect。

puts "S5T01_SCANX_BEGIN"
connect
after 1000
if {[catch {set tg [targets]} e]} {
    puts "S5T01_TARGETS_ERR=$e"
    puts "S5T01_TARGET_COUNT=ERR"
} else {
    puts "S5T01_TARGET_COUNT=[llength $tg]"
    set i 0
    foreach t $tg { puts "S5T01_TARGET_$i=$t"; incr i }
}
puts "S5T01_JTAG_TARGETS_BEGIN"
if {[catch {jtag targets} r]} { puts "S5T01_JTAG_TARGETS_ERR=$r" } else { puts $r }
puts "S5T01_JTAG_TARGETS_END"
if {[catch {targets -set -nocase -filter {name =~ "*xc7z020*"}} e2]} {
    puts "S5T01_SET_XC7Z020_ERR=$e2"
} else {
    puts "S5T01_SET_XC7Z020_OK=1"
    if {[catch {set tg2 [targets]} e3]} { puts "S5T01_TREE_ERR=$e3" } else {
        puts "S5T01_TREE_COUNT=[llength $tg2]"
        set j 0
        foreach t $tg2 { puts "S5T01_TREE_$j=$t"; incr j }
    }
}
disconnect
puts "S5T01_SCANX_DONE=1"