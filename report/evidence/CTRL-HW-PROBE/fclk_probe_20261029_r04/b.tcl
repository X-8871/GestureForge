connect -url tcp:127.0.0.1:3121
catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}}
catch {rst -processor -stop}
catch {mwr 0xF8000008 0xDF0D}
catch {mwr 0xF8000900 0x0000000F}
catch {mwr 0xF8000004 0x767B}
catch {mrd 0xF8000900 1} s
puts "SHFTR=$s"
catch {loadhw -hw D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08/s2b_inference.xsa -mem-ranges {{0x43C00000 0x43C0FFFF}}}
catch {mrd 0x43C00000 1} e
puts "CSR_ID=$e"
