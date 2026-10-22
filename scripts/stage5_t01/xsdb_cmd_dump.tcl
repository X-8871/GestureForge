# S5-T01 只读诊断：不连接硬件，仅列出 xsdb 的 jtag/cable 相关命令，便于下一步精确查询线缆状态。
puts "S5T01_CMDDUMP_BEGIN"
puts "JTAG_CMDS=[lsort [info commands *jtag*]]"
puts "CABLE_CMDS=[lsort [info commands *cable*]]"
puts "TARGET_CMDS=[lsort [info commands *target*]]"
if {[catch {help jtag} h]} { puts "HELP_JTAG_ERR=$h" } else { puts "HELP_JTAG=$h" }
puts "S5T01_CMDDUMP_DONE=1"