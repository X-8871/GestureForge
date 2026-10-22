# S5-T01 只读链查询（正确子命令版）：jtag servers / targets / sequence / skew，全部 catch，最后 disconnect。
puts "S5T01_CHAIN2_BEGIN"
connect
after 1500
foreach sub {servers targets sequence skew} {
    if {[catch {jtag $sub} r]} { puts "JTAG_${sub}_ERR=$r" } else { puts "JTAG_${sub}=$r" }
}
puts "S5T01_TARGETS_BEGIN"
targets
puts "S5T01_TARGETS_END"
disconnect
puts "S5T01_CHAIN2_DONE=1"