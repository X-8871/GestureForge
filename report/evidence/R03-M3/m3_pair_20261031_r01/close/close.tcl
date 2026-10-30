# 每次选择前核验唯一目标与已知名称，不依赖隐式活动目标。
proc select_unique {filter} {
    set matches [targets -target-properties -filter $filter]
    if {[llength $matches] != 1} {error "TARGET_NOT_UNIQUE"}
    set name [dict get [lindex $matches 0] name]
    if {![regexp -nocase {^(ARM )?Cortex-A9 MPCore #[01]$|^xc7z020(_[0-9]+)?$} $name]} {error "TARGET_NAME_UNEXPECTED: $name"}
    targets -set -filter $filter
    puts "SELECTED_UNIQUE=$name"
}
# 只核验/停止本窗两核，异常停止，不复位或重试。
set code [catch {
    connect -url tcp:127.0.0.1:3121
    foreach core {0 1} {
        select_unique [format {name =~ "*Cortex-A9*#%d"} $core]
        set value [string trim [state]]
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {stop; set value [string trim [state]]}
        puts "CLOSE_CORE_${core}=$value"
        if {![regexp -nocase {^(stopped|suspended)(:|[[:space:]]|$)} $value]} {error "HALT_NOT_CONFIRMED"}
    }
    puts "M3_CLOSE_CORES_STOPPED"
} message]
set disconnect_code [catch {disconnect} disconnect_message]
if {$code == 0 && $disconnect_code != 0} {set code 2; set message "DISCONNECT_FAILED: $disconnect_message"}
if {$code != 0} {puts stderr "ERROR: $message"; exit 2}
exit 0
