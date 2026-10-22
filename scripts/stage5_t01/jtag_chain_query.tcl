# S5-T01 只读链查询：connect 后依次尝试 jtag 子命令与 get_jtag_nodes，全部 catch，最后 disconnect。
puts "S5T01_CHAIN_BEGIN"
connect
after 1500
foreach probe {get_jtag_nodes} {
    if {[catch {$probe} r]} { puts "PROBE_${probe}_ERR=$r" } else { puts "PROBE_${probe}=$r" }
}
foreach sub {frequency devices device cable scan} {
    if {[catch {jtag $sub} r]} { puts "JTAG_${sub}_ERR=$r" } else { puts "JTAG_${sub}=$r" }
}
puts "S5T01_TARGETS_BEGIN"
targets
puts "S5T01_TARGETS_END"
disconnect
puts "S5T01_CHAIN_DONE=1"