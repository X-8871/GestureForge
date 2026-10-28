connect -url tcp:127.0.0.1:3121
puts [targets]
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -dap} e
puts "RST_DAP=$e"
catch {rst -processor -stop} e2
puts "STOP=$e2"
catch {mrd 0xF8000900 1} e3
puts "LVL=$e3"
catch {mrd 0x43C00000 1} e4
puts "CSR=$e4"
