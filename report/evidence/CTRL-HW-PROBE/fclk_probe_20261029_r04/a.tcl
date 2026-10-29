connect -url tcp:127.0.0.1:3121
puts [targets]
catch {rst -system -stop}
after 800
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
catch {dow D:/codex-worktrees/w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf}
catch {con}
after 4000
catch {rst -processor -stop}
catch {mrd 0xF8000170 1} f0
puts "FCLK0_before=$f0"
catch {mwr 0xF8000008 0xDF0D}
catch {mwr 0xF8000170 0x00600601}
catch {mwr 0xF8000004 0x767B}
catch {mrd 0xF8000170 1} f1
puts "FCLK0_after=$f1"
