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
loadhw -hw {D:/tmp/lead/p3q_video_20261030_r01/out/s4d_p3q_r01.xsa} -mem-ranges {0x00000000 0x7FFFFFFF}
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
dow {D:/codex-worktrees/w6/report/evidence/R05-C2/c2_real_20261101_r04/artifacts/c2_real_chainb_display.elf}
mwr 0xf8000008 0xdf0d
mwr 0xf8000900 0xf
mwr 0xf8000240 0
mwr 0xf8000004 0x767b
stopped
puts "C2_FCLK_CTRL0=[mrd -value 0xf8000170] IO_PLL=[mrd -value 0xf8000108] ARM_PLL=[mrd -value 0xf8000100] DDR_PLL=[mrd -value 0xf8000104]"
mwr -bin -file {D:/FPGA_Data/HaGRIDv2/darknet_inputs/runs/s1_t02_d2_tiny416_int8_weight_r2/gesture_yolov4_tiny_416_int8_weights.gf8} 0x10100000 1475775
mrd -bin -file {D:/codex-worktrees/w6/report/evidence/R05-C2/c2_real_20261101_r04/weights_readback.bin} 0x10100000 1475775
puts "C2_WEIGHTS_TRANSFERRED"
puts "C2_PROGRAMMED_APP_NOT_STARTED"
} message]
set dc [catch {disconnect} dm]
if {$code == 0 && $dc != 0} {set code 2;set message $dm}
if {$code != 0} {puts stderr "ERROR:$message";exit 2}
exit 0
