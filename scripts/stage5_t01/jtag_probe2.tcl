# S5-T01 只读 JTAG 复核（第二次，简化）：connect → 等链路稳定 → 列目标 → disconnect。
# 只用 XSDB 基本命令，避免未识别命令导致脚本中断而遗留 hw_server。
puts "S5T01_PROBE2_BEGIN"
connect
after 2000
puts "S5T01_TARGETS_BEGIN"
targets
puts "S5T01_TARGETS_END"
disconnect
puts "S5T01_PROBE2_DONE=1"