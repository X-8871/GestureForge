# 本次POR仅运行一次固定1GiB初始化，不执行任何复位。
proc choose {filter} {
 set ts [targets -target-properties -filter $filter]
 if {[llength $ts] != 1} {error "TARGET_NOT_UNIQUE"}
 targets -set -filter $filter
}
proc ensure_stop {} {
 set s [string trim [state]]
 if {[regexp -nocase {^running(:|[[:space:]]|$)} $s]} {stop; set s [string trim [state]]}
 if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $s]} {error "NOT_STOPPED:$s"}
 puts "INIT_CORE_STATE=$s"
}
set code [catch {
 connect -url tcp:127.0.0.1:3121
 choose {name =~ "*Cortex-A9*#0"}
 loadhw -hw {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.xsa} -mem-ranges {0x00000000 0x3fffffff}
 ensure_stop
 choose {name =~ "*Cortex-A9*#1"}
 ensure_stop
 choose {name =~ "*Cortex-A9*#0"}
 dow {D:/codex-worktrees/w4/report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf}
 con
 after 2500
 ensure_stop
 puts "M3_SINGLE_INIT_COMPLETED"
} message]
set dc [catch {disconnect} dm]
if {$code == 0 && $dc != 0} {set code 2;set message $dm}
if {$code != 0} {puts stderr "ERROR:$message";exit 2}
exit 0
