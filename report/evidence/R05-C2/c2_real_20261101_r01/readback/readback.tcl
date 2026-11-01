proc choose {f} {
 set ts [targets -target-properties -filter $f]
 if {[llength $ts] != 1} {error "TARGET_NOT_UNIQUE"}
 targets -set -filter $f
}
proc stopped {} {
 set s [string trim [state]]
 if {[regexp -nocase {^running(:|[[:space:]]|$)} $s]} {stop;set s [string trim [state]]}
 if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $s]} {error "CPU_NOT_STOPPED:$s"}
 puts "CORE_STOPPED=$s"
}
set code [catch {
connect -url tcp:127.0.0.1:3121
choose {name =~ "*Cortex-A9*#0"}
loadhw -hw {D:/tmp/lead/p3q_video_20261030_r01/out/s4d_p3q_r01.xsa} -mem-ranges {0x00000000 0x3FFFFFFF}
set s1 [mrd -value 0x20800118]
mrd -bin -file {D:/codex-worktrees/w6/report/evidence/R05-C2/c2_real_20261101_r01/readback/result_block.bin} 0x20800000 72
set s2 [mrd -value 0x20800118]
puts "C2_LOCK_S1=$s1 C2_LOCK_S2=$s2"
if {$s1 != $s2 || ($s1 & 1) != 0} {error "C2_TORN_BLOCK"}
puts "C2_VDMA_CR=[mrd -value 0x43c40000] C2_VDMA_SR=[mrd -value 0x43c40004]"
puts "C2_GT=[mrd -value 0xf8f00200 2]"
puts "C2_READBACK_OK"
} message]
set dc [catch {disconnect} dm]
if {$code == 0 && $dc != 0} {set code 2;set message $dm}
if {$code != 0} {puts stderr "ERROR:$message";exit 2}
exit 0
