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
con
puts "C2_APP_STARTED"
} message]
set dc [catch {disconnect} dm]
if {$code == 0 && $dc != 0} {set code 2;set message $dm}
if {$code != 0} {puts stderr "ERROR:$message";exit 2}
exit 0
