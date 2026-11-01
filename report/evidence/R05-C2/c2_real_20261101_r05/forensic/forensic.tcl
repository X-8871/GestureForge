set code [catch {
connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0"}
puts "FORENSIC_STATE=[state]"
loadhw -hw {D:/tmp/lead/p3q_video_20261030_r01/out/s4d_p3q_r01.xsa} -mem-ranges {0x00000000 0x7FFFFFFF}
puts "FORENSIC_PC=[rrd pc] LR=[rrd r14] SP=[rrd r13]"
puts "LOCK1=[mrd -value 0x20800118]"
mrd -bin -file {D:/codex-worktrees/w6/report/evidence/R05-C2/c2_real_20261101_r05/forensic/result_block.bin} 0x20800000 72
puts "LOCK2=[mrd -value 0x20800118] VDMA_CR=[mrd -value 0x43c40000] VDMA_SR=[mrd -value 0x43c40004]"
puts "FORENSIC_READ_ONLY_OK"
} e]
catch {disconnect}
if {$code != 0} {puts stderr "ERROR:$e";exit 2}
exit 0
