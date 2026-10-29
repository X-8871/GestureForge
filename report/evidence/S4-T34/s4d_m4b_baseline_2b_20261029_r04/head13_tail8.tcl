connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
puts "PROBE_TARGETS_SET"
if {[catch {loadhw -hw D:/FPGA_Competition/w2b/report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08/s2b_inference.xsa -mem-ranges {0x00000000 0x1FFFFFFF}} e_lhw]} {
    puts "PROBE_LOADHW_SKIPPED: $e_lhw"
} else {
    puts "PROBE_LOADHW_OK"
}
set f "D:/codex-worktrees/w4/report/evidence/S4-T34/s4d_m4b_baseline_2b_20261029_r04/head13_tail8.bin"
set rc [catch {mrd -bin -file $f 0x11A474C8 2} e1]
if {$rc != 0} {
    puts "PROBE_MRD_FAIL_1: $e1"
    catch {rst -processor -stop}
    after 500
    set rc2 [catch {mrd -bin -file $f 0x11A474C8 2} e2]
    puts "PROBE_MRD_RETRY_RC=$rc2 ERR=$e2"
} else {
    puts "PROBE_MRD_OK"
}
disconnect
exit