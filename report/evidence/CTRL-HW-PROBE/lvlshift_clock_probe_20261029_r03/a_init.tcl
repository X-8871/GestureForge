connect -url tcp:127.0.0.1:3121
puts [targets]
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -system -stop}
after 1000
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
catch {dow D:/codex-worktrees/w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf} d
puts "DOW=$d"
catch {con}
after 3000
catch {rst -processor -stop}
catch {mrd 0xF8000900 1} s
puts "SHFTR_after_init=$s"
