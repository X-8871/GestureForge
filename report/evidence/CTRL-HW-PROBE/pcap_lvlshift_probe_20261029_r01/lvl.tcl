connect -url tcp:127.0.0.1:3121
puts [targets]
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
puts "--- LVL_SHFTR_EN before ---"
catch {mrd 0xF8000900 1} e1
puts "M1=$e1"
puts "--- CSR before enable ---"
catch {loadhw -hw D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08/s2b_inference.xsa -mem-ranges {{0x43C00000 0x43C0FFFF}}}
catch {mrd 0x43C00000 1} e2
puts "CSR1=$e2"
puts "--- enable level shifters ---"
catch {mwr 0xF8000008 0xDF0D}
catch {mwr 0xF8000900 0x0000000F}
catch {mwr 0xF8000004 0x767B}
catch {mrd 0xF8000900 1} e3
puts "M2=$e3"
puts "--- CSR after enable ---"
catch {mrd 0x43C00000 1} e4
puts "CSR2=$e4"
puts "--- DevCfg STATUS ---"
catch {mrd 0xF8007008 1} e5
puts "DEVCFG=$e5"
