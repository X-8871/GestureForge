connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
puts "EVENT=1 CMD=mrd -value 0xF8000000 (SLCR 只读)"
puts "EVENT=1 RESULT=[mrd -value 0xF8000000]"
puts "EVENT=2 CMD=mrd -value 0x12000000 (候选区首字 只读)"
puts "EVENT=2 RESULT=[mrd -value 0x12000000]"
puts "EVENT_STATE=[state]"
disconnect
exit