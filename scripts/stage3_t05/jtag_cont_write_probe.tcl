# S3-T05 连续写帧判定：对同一地址做多轮「写标记→等 500ms→读回」。
#   每轮标记都被覆盖 => DMA 连续写帧（活数据在流）
#   只有第一轮被覆盖   => DMA 只写了一帧就停（park/停）
#   没有一轮被覆盖     => DMA 完全没在写
# 之后再做一次 S2MM 重启（易失、可恢复），重复同样判定。
# 用法: xsdb jtag_cont_write_probe.tcl

proc marker_rounds {tag rounds} {
    set addr 0x00120C40
    set overwritten 0
    for {set i 0} {$i < $rounds} {incr i} {
        mwr -force $addr 0xDEADBEEF
        after 500
        set v [mrd -force $addr]
        if {[string first "DEADBEEF" $v] >= 0} {
            puts "$tag ROUND_$i=KEPT"
        } else {
            puts "$tag ROUND_$i=OVERWRITTEN"
            incr overwritten
        }
    }
    puts "$tag OVERWRITTEN=$overwritten/$rounds"
}

proc restart_s2mm {} {
    mwr -force 0x43010030 0x00018002
    after 200
    mwr -force 0x43010030 0x00000004
    after 200
    mwr -force 0x43010030 0x00000000
    after 200
    mwr -force 0x43010034 0xFFFFFFFF
    after 200
    mwr -force 0x430100A0 0x000002D0
    mwr -force 0x430100A4 0x00000F00
    mwr -force 0x430100A8 0x00000F00
    mwr -force 0x430100AC 0x00110C00
    mwr -force 0x43010030 0x00018003
}

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "=== PHASE A: 当前状态（不重启） ==="
puts "A_SR=[mrd -force 0x43010034]"
marker_rounds A 5
puts "A_SR_END=[mrd -force 0x43010034]"

puts "=== PHASE B: 重启 S2MM 后 ==="
restart_s2mm
after 2000
puts "B_SR=[mrd -force 0x43010034]"
marker_rounds B 5
puts "B_SR_END=[mrd -force 0x43010034]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "CONT_WRITE_PROBE_DONE=1"