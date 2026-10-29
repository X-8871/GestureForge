connect -url tcp:127.0.0.1:3121
puts [targets]
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
puts "-- A: power-on state --"
foreach a {0xF8000900 0xF8000170 0xF8000180 0xF8000190 0xF8000100 0xF8000120} { catch {mrd $a 1} r; puts "A_$a = $r" }
puts "-- B: system reset + init --"
catch {rst -system -stop}
after 800
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
catch {dow D:/codex-worktrees/w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf} d
puts "B_DOW=$d"
catch {con}
after 4000
catch {rst -processor -stop}
foreach a {0xF8000900 0xF8000170 0xF8000180 0xF8000190 0xF8000120} { catch {mrd $a 1} r; puts "B_$a = $r" }
