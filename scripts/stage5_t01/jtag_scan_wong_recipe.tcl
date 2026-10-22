# S5-T01 链探测（按 Wong 配方复核）：connect → jtag targets → 选中 xc7z020 → targets 打印树。
# 只读：不 halt、不写寄存器、不下载。全部 catch，最后 disconnect。
puts "S5T01_SCAN_BEGIN"
connect
after 1000
puts "S5T01_JTAG_TARGETS_BEGIN"
if {[catch {jtag targets} r]} { puts "JTAG_TARGETS_ERR=$r" } else { puts "JTAG_TARGETS=$r" }
puts "S5T01_JTAG_TARGETS_END"
if {[catch {targets -set -nocase -filter {name =~ "*xc7z020*"}} e]} {
    puts "SET_XC7Z020_ERR=$e"
} else {
    puts "SET_XC7Z020_OK=1"
}
puts "S5T01_TREE_BEGIN"
targets
puts "S5T01_TREE_END"
disconnect
puts "S5T01_SCAN_DONE=1"