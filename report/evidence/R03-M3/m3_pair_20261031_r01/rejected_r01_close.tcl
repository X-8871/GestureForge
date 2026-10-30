# 只核验/停止本窗两核，异常停止，不复位或重试。
set code [catch {
    connect -url tcp:127.0.0.1:3121
    foreach core {0 1} {
        targets -set -filter [format {name =~ "*Cortex-A9*#%d"} $core]
        set value [string trim [state]]
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {stop; set value [string trim [state]]}
        puts "CLOSE_CORE_${core}=$value"
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {error "HALT_NOT_CONFIRMED"}
    }
    puts "M3_CLOSE_CORES_STOPPED"
} message]
catch {disconnect}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
