# S3-T05 安全只读探测：先 halt A9#0，再读外设寄存器与物理 DDR（绕过 CPU cache），读完 con 恢复。
# 教训（2026-10-20 12:0x 实测）：对**运行中**的 A9 直接 mrd 会触发
#   "Timeout waiting for the Instruction Complete bit" 并把 DAP 置为
#   "APB AP transaction error, DAP status 0x30000021"，导致目标树里 APU/A9 消失；
#   恢复方式：targets -set *DAP* → rst -type system（会清 PL 配置，需重下比特流）。
# 因此本脚本一律 halt → 读 → con，不写任何寄存器、不烧录。
# 用法: xsdb jtag_read_safe.tcl [frame_base_hex]

set base 0x00110C00
if {[lindex $argv 0] ne ""} { set base [lindex $argv 0] }
puts "READ_BASE=$base"

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "HALT_ERR=$e" } else { puts "HALT_OK=1" }
after 300

puts "CR_S2MM=[mrd -force 0x43010030]"
puts "SR_S2MM=[mrd -force 0x43010034]"
puts "VSIZE_S2MM=[mrd -force 0x430100A0]"
puts "HSIZE_S2MM=[mrd -force 0x430100A4]"
puts "STRIDE_S2MM=[mrd -force 0x430100A8]"
puts "ADDR_S2MM=[mrd -force 0x430100AC]"
puts "SR_MM2S=[mrd -force 0x43000004]"

puts "DDR_FB_000=[mrd -force $base 8]"
puts "DDR_FB_400=[mrd -force [expr {$base + 0x1000}] 8]"
puts "DDR_FB_MID=[mrd -force [expr {$base + 0x400000}] 8]"

if {[catch {con} e2]} { puts "CON_ERR=$e2" } else { puts "CON_OK=1" }
disconnect
puts "SAFE_READ_DONE=1"