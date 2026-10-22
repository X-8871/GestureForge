# S5-T01 数值核对：只读 dump 送显缓冲的若干行（word 对齐取数）→ con 恢复。
# 前提：板上运行 s5t01_case5_r02.elf（单用例 5 常显），BUF0=0x00114C00，stride=3840。
# 期望（冻结参考实现给出的用例 5 矩形）：
#   红 FIST 框 (0,53)-(77,425)；绿 PALM 框 (513,0)-(1025,66)
# 用法: xsdb jtag_dump_rows.tcl
puts "S5_DUMP_BEGIN"
set buf0 0x00114C00
set stride 3840

connect
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
if {[catch {stop} e]} { puts "S5_HALT_ERR=$e" } else { puts "S5_HALT_OK=1" }
after 300

puts "S5_REG_MM2S_CR=[mrd -force 0x43000000]"
puts "S5_REG_MM2S_SR=[mrd -force 0x43000004]"

# 行 0：x 0..84（白角标记 16px + 斜坡起点）
puts "S5_ROW_BEGIN row=0 x=0"
puts [mrd -force $buf0 64]
# 行 53：x 0..84（红框顶边 0..78）
puts "S5_ROW_BEGIN row=53 x=0"
puts [mrd -force [expr {$buf0 + 53*$stride}] 64]
# 行 53：x 512..596（绿框左边 513,514）
puts "S5_ROW_BEGIN row=53 x=512"
puts [mrd -force [expr {$buf0 + 53*$stride + 1536}] 64]
# 行 66：x 512..596（绿框底边 66,67）
puts "S5_ROW_BEGIN row=66 x=512"
puts [mrd -force [expr {$buf0 + 66*$stride + 1536}] 64]
# 行 359：x 0..15（红框左边 0,1）
puts "S5_ROW_BEGIN row=359 x=0"
puts [mrd -force [expr {$buf0 + 359*$stride}] 16]
# 行 200：x 64..127（红框右边 77,78；行 200 不在 HUD/标签覆盖带内）
puts "S5_ROW_BEGIN row=200 x=64"
puts [mrd -force [expr {$buf0 + 200*$stride + 192}] 24]
# 行 66：x 0..21（红框左边仍在；绿框底边之外的对照行）
puts "S5_ROW_BEGIN row=200 x=0"
puts [mrd -force [expr {$buf0 + 200*$stride}] 8]
# 行 359：x 1216..1279 附近（右白角标记）
puts "S5_ROW_BEGIN row=359 x=1256"
puts [mrd -force [expr {$buf0 + 359*$stride + 3768}] 16]
# 行 0 的另两块送显缓冲（应同为该画面）
puts "S5_ROW_BEGIN row=0 x=0 buf1"
puts [mrd -force 0x00703800 8]
puts "S5_ROW_BEGIN row=0 x=0 buf2"
puts [mrd -force 0x00CF2400 8]

if {[catch {con} e2]} { puts "S5_CON_ERR=$e2" } else { puts "S5_CON_OK=1" }
disconnect
puts "S5_DUMP_DONE=1"