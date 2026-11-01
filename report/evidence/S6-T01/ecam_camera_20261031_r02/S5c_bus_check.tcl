
connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
if {[catch {stop} e]} { puts "STOP_ERR $e" } else { puts STOP_OK }
if {[catch {loadhw -hw D:/tmp/lead/p3r_camera_20261031_r01/out/build8/s4d_p3r_r01.xsa -mem-ranges {0x00000000 0xFFFFFFFF}} e]} { puts "LH_ERR $e" } else { puts LH_OK }
puts "STAT_PRE [mrd -value 0x43C80008]"
set s0 [mrd -value 0x43C80008]
if {($s0 & 0x3) != 3} {
    mwr -force 0x43C80000 0x1
    after 5
    for {set i 0} {$i < 9} {incr i} {
        mwr -force 0x43C80000 0x3
        after 3
        mwr -force 0x43C80000 0x1
        after 3
    }
    mwr -force 0x43C80000 0x0
    after 20
}
puts "STAT_POST [mrd -value 0x43C80008]"
disconnect
exit
