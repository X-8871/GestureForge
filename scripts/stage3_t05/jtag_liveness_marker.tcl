# S3-T05 活写标记探测（2026-10-24 阶段3 板级窗口）：只判「DMA 是否仍在连续写帧」，**不写任何寄存器**。
# 判据（沿用既有 jtag_cont_write_probe.tcl 的标记法）：对帧缓冲某地址连续多轮「写标记 → 等 500ms → 读回」；
#   每轮标记都被覆盖 => DMA 连续写帧（活数据在流）；只有首轮被覆盖 => 只写了一帧就停；一轮都没有 => 未在写。
# 与旧脚本的区别：**删除 PHASE B 的 S2MM 重启**（本窗口不做状态重启），只保留只读判定所需的最小动作。
# 用法: xsdb jtag_liveness_marker.tcl [marker_addr_hex] [rounds]
set addr 0x00120C40
if {[lindex $argv 0] ne ""} { set addr [lindex $argv 0] }
set rounds 5
if {[lindex $argv 1] ne ""} { set rounds [lindex $argv 1] }
puts "LIVENESS_ADDR=$addr ROUNDS=$rounds"

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "SR_S2MM_BEFORE=[mrd -force 0x43010034]"
set overwritten 0
for {set i 0} {$i < $rounds} {incr i} {
    mwr -force $addr 0xDEADBEEF
    after 500
    set v [mrd -force $addr]
    if {[string first "DEADBEEF" $v] >= 0} {
        puts "ROUND_$i=KEPT"
    } else {
        puts "ROUND_$i=OVERWRITTEN"
        incr overwritten
    }
}
puts "OVERWRITTEN=$overwritten/$rounds"
puts "SR_S2MM_AFTER=[mrd -force 0x43010034]"
puts "FRMCNT_AFTER=[mrd -force 0x43010038]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "LIVENESS_DONE=1"