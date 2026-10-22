# S5-T01 只读核对：haltt A9 → 读显示通道寄存器 + 送显缓冲内容（BUF0）→ con 恢复。
# 用法: xsdb jtag_read_overlay_buf.tcl [buf0_hex]
# 预期（若 P1 画面已进缓冲）：
#   - BUF0+0 附近为白色四角标记 0x00FFFFFF（灰度背景条为 0x00VVVVVV）
#   - 用例5 左边缘框（x=0..77, y=53..425）顶边行 y≈53 上出现 FIST 颜色 0x00FF4040（B=64,G=64,R=255）
puts "S5_READ_BEGIN"
set buf0 0x00114C00
if {[lindex $argv 0] ne ""} { set buf0 [lindex $argv 0] }
puts "S5_BUF0=$buf0"

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "S5_HALT_ERR=$e" } else { puts "S5_HALT_OK=1" }
after 300

puts "S5_MM2S_CR=[mrd -force 0x43000000]"
puts "S5_MM2S_SR=[mrd -force 0x43000004]"
puts "S5_S2MM_CR=[mrd -force 0x43010030]"
puts "S5_S2MM_SR=[mrd -force 0x43010034]"
puts "S5_MM2S_FW1=[mrd -force 0x43000050]"
puts "S5_MM2S_FW2=[mrd -force 0x43000054]"

# 背景：角标记 + 灰度条
puts "S5_BUF0_ROW0=[mrd -force $buf0 16]"
# 条边界：x=64 → 第 192 字节
puts "S5_BUF0_BARBOUND=[mrd -force [expr {$buf0 + 192}] 4]"
# 用例5 左框顶边行（y=53 → 53*3840 = 203520 字节）
set row53 [expr {$buf0 + 203520}]
puts "S5_BUF0_ROW53_X0=[mrd -force $row53 16]"
set row54 [expr {$buf0 + 54*3840}]
puts "S5_BUF0_ROW54_X0=[mrd -force $row54 16]"
# 该行 x=78 之后应是背景（框右边界外）
puts "S5_BUF0_ROW53_X78=[mrd -force [expr {$row53 + 78*3}] 8]"
# 其它两块送显缓冲首字（应为同一画面）
puts "S5_BUF1_ROW0=[mrd -force 0x00703800 4]"
puts "S5_BUF2_ROW0=[mrd -force 0x00CF2400 4]"

if {[catch {con} e2]} { puts "S5_CON_ERR=$e2" } else { puts "S5_CON_OK=1" }
disconnect
puts "S5_READ_DONE=1"