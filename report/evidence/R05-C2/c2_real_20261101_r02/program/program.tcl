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
stopped
choose {name =~ "*Cortex-A9*#1"}
stopped
choose {name =~ "*Cortex-A9*#0"}
mwr 0xf8000008 0xdf0d
mwr 0xf8000900 0xa
mwr 0xf8000240 0
mwr 0xf8000004 0x767b
choose {name =~ "*xc7z020*"}
fpga -file {D:/tmp/lead/p3q_video_20261030_r01/out/s4d_p3q_r01.bit}
choose {name =~ "*Cortex-A9*#0"}
mwr 0xf8000008 0xdf0d
mwr 0xf8000900 0xf
mwr 0xf8000240 0
mwr 0xf8000004 0x767b
set ident [mrd -value 0x43c00000]
set status [mrd -value 0x43c0000c]
puts "C2_CSR_ID=$ident STATUS=$status"
if {$ident != 0x53324250 || ($status & 0x3107) != 0} {error "C2_NEW_PL_NOT_IDLE"}
dow {D:/codex-worktrees/w6/report/evidence/R05-C2/c2_real_20261101_r02/artifacts/c2_real_chainb_display.elf}
mwr 0xf8000008 0xdf0d
mwr 0xf8000900 0xf
mwr 0xf8000240 0
mwr 0xf8000004 0x767b
stopped
puts "C2_PROGRAMMED_APP_NOT_STARTED"
} message]
set dc [catch {disconnect} dm]
if {$code == 0 && $dc != 0} {set code 2;set message $dm}
if {$code != 0} {puts stderr "ERROR:$message";exit 2}
exit 0
