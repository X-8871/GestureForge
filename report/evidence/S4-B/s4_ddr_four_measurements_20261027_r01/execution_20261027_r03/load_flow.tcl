connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
puts "LOAD_SELECT0=OK"
rst -system -stop
puts "LOAD_RST_SYSTEM_STOP=OK"
dow -file D:\codex-worktrees\w4\report\evidence\S4-B\s4b_ps_tensor_20261023_r13\verified_payload\init.elf
puts "LOAD_INIT_DOW=OK"
con
after 6000
puts "LOAD_INIT_CON=OK"
targets -set -filter {name =~ "*Cortex-A9*#0*"}
dow -file D:\codex-worktrees\w4\report\evidence\S4-B\s4_ddr_four_measurements_20261027_r01\preparation\payloads\m4a_cache_probe.elf
puts "LOAD_APP_DOW=OK"
puts "LOAD_CPU0_STATE=[state]"
disconnect
exit 0
