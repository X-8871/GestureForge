# 两次成对取样之间只有只读寄存器检查与短时保持，不运行应用。
set code [catch {
    connect -url tcp:127.0.0.1:3121
    foreach core {0 1} {
        targets -set -filter [format {name =~ "*Cortex-A9*#%d"} $core]
        set value [string trim [state]]
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {error "CPU_NOT_STOPPED"}
        puts "EVENT_CORE_${core}=$value"
    }
    targets -set -filter {name =~ "*Cortex-A9*#0"}
    for {set i 0} {$i < 3} {incr i} {
        set ident [mrd -value 0x43c00000]
        set status [mrd -value 0x43c0000c]
        set clock [mrd -value 0xf8f00200 2]
        puts "EVENT_SAMPLE=$i ID=$ident STATUS=$status GT=$clock"
        if {$ident != 0x53324250 || ($status & 0x3107) != 0} {error "EVENT_PL_NOT_IDLE"}
        after 200
    }
    puts "M3_READONLY_EVENT_OK"
} message]
catch {disconnect}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
