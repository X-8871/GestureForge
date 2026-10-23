# S3-T05 一次性清 S2MM SR 粘滞位（W1C）——仅授权窗口内、须记录前后值。
# 依据：015 §2.4「保留启动原值、错误位解释和运行增量……不能只清寄存器后称零错误」。
# 本脚本**只清一次** SR（写入启动观测值），不做 S2MM 重启、不写其它寄存器；用完即扣回 con。
# 用法: xsdb jtag_s2mm_sr_clear.tcl [value_hex]（默认 0x00015810 = 本窗口启动观测值）
set val 0x00015810
if {[lindex $argv 0] ne ""} { set val [lindex $argv 0] }
puts "CLEAR_VALUE=$val"

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "SR_BEFORE=[mrd -force 0x43010034]"
mwr -force 0x43010034 $val
after 300
puts "SR_AFTER=[mrd -force 0x43010034]"
puts "CR_NOW=[mrd -force 0x43010030]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "SR_CLEAR_DONE=1"