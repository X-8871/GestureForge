connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
puts "FIX_SELECT=OK"
puts "FIX_BEFORE=[mrd -value 0x12000000]"
mwr 0x12000000 0x0486bdbf
puts "FIX_WRITE_DONE"
puts "FIX_AFTER=[mrd -value 0x12000000]"
mrd -bin -file D:\codex-worktrees\w4\report\evidence\S4-B\s4_ddr_four_measurements_20261027_r01\execution_20261027_r05\remediation_restore\fix_readback16.bin 0x12000000 4
puts "FIX_READBACK_DONE"
disconnect
exit 0
