puts "== ENUM =="
connect -url tcp:127.0.0.1:3121
puts [targets]
puts [jtag targets]
puts "== STOP A9 #0 =="
if {[catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}} e]} { puts "ERR_SET_A9: $e" }
if {[catch {rst -processor -stop} e]} { puts "ERR_STOP: $e" }
puts "== DEVCONFIG BEFORE PROGRAM =="
foreach a {0xF8007000 0xF8007004 0xF8007008 0xF8007080} {
  if {[catch {mrd $a 1} e]} { puts "MRD_$a ERR: $e" } else { puts "MRD_$a = $e" }
}
puts "== PROGRAM PL =="
if {[catch {fpga -file D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit} e]} { puts "ERR_FPGA: $e" } else { puts "FPGA_OK: $e" }
puts "== DEVCONFIG AFTER PROGRAM =="
if {[catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}} e]} { puts "ERR_SET_A9_2: $e" }
if {[catch {rst -processor -stop} e]} { puts "ERR_STOP_2: $e" }
foreach a {0xF8007000 0xF8007004 0xF8007008 0xF8007080} {
  if {[catch {mrd $a 1} e]} { puts "MRD2_$a ERR: $e" } else { puts "MRD2_$a = $e" }
}
puts "== CSR ID ATTEMPT =="
if {[catch {loadhw -hw D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08/s2b_inference.xsa -mem-ranges {{0x43C00000 0x43C0FFFF}}} e]} { puts "ERR_LOADHW: $e" } else { puts "LOADHW_OK" }
if {[catch {mrd 0x43C00000 1} e]} { puts "ERR_CSR: $e" } else { puts "CSR_ID = $e" }
puts "== DONE =="
