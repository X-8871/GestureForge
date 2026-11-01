
connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
if {[catch {stop} e]} { puts "STOP_ERR $e" } else { puts STOP_OK }
if {[catch {loadhw -hw D:/tmp/lead/p3r_camera_20261031_r01/out/build7/s4d_p3r_r01.xsa -mem-ranges {0x00000000 0xFFFFFFFF}} e]} { puts "LH_ERR $e" } else { puts LH_OK }
proc setpins {scl sda} {
    set v 0x1
    if {!$scl} { set v [expr {$v | 0x2}] }
    if {!$sda} { set v [expr {$v | 0x4}] }
    mwr -force 0x43C80000 $v
    after 2
}
proc lvl {} { return [mrd -value 0x43C80008] }
proc bitout {b} {
    setpins 0 $b
    setpins 1 $b
    setpins 0 $b
}
proc sendbyte {byte} {
    for {set i 7} {$i >= 0} {incr i -1} { bitout [expr {($byte >> $i) & 1}] }
    setpins 0 1
    setpins 1 1
    set l [lvl]
    set ack [expr {($l & 0x2) ? 0 : 1}]
    setpins 0 1
    return $ack
}
proc readbyte {} {
    set v 0
    for {set i 0} {$i < 8} {incr i} {
        setpins 0 1
        setpins 1 1
        set l [lvl]
        set b [expr {($l >> 1) & 1}]
        set v [expr {($v << 1) | $b}]
        setpins 0 1
    }
    return $v
}
proc master_ack {ack} {
    if {$ack} { setpins 0 0 } else { setpins 0 1 }
    setpins 1 [expr {$ack ? 0 : 1}]
    setpins 0 1
}
puts "A_BEFORE [lvl]"
mwr -force 0x43C80000 0x1
after 20
puts "A [lvl]"
mwr -force 0x43C80000 0x3
after 20
puts "B [lvl]"
mwr -force 0x43C80000 0x5
after 20
puts "C [lvl]"
mwr -force 0x43C80000 0x1
after 20
puts "D [lvl]"
for {set i 0} {$i < 9} {incr i} {
    setpins 0 1
    setpins 1 1
}
after 20
puts "E [lvl]"
# START + 0x78 + 0x30 + 0x0A
setpins 1 1
after 5
setpins 1 0
after 5
set a78 [sendbyte 0x78]
puts "ACK78 $a78"
set a30 [sendbyte 0x30]
puts "ACK30 $a30"
set a0a [sendbyte 0x0A]
puts "ACK0A $a0a"
# repeated START
setpins 1 1
after 5
setpins 1 0
after 5
set a79 [sendbyte 0x79]
puts "ACK79 $a79"
set b0 [readbyte]
puts "RX0 $b0"
master_ack 1
set b1 [readbyte]
puts "RX1 $b1"
master_ack 0
# STOP
setpins 0 0
after 5
setpins 1 0
after 5
setpins 1 1
after 20
puts "F [lvl]"
mwr -force 0x43C80000 0x0
after 20
puts "F2 [lvl]"
disconnect
exit
