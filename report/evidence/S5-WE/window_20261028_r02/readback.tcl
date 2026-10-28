# S5-WE window_20261028_r02 只读读回：目标树 / 设备身份 / PS 寄存器回读（不写内存、不下载）
puts "S5WE_RB_BEGIN"
connect
puts "S5WE_TARGETS_BEGIN"
targets
puts "S5WE_TARGETS_END"
# 设备身份（FPGA 目标）
if {[catch {
    targets -set -nocase -filter {name =~ "*xc7z*" || name =~ "*arm_dap*"}
    puts "S5WE_DEV_TARGET=[targets -target]"
} err]} { puts "S5WE_DEV_WARN=$err" }
# 回读 PS 时钟寄存器（只读；与上次失败探测同一地址）
if {[catch {
    targets -set -nocase -filter {name =~ "*APU*"}
    puts "S5WE_MRD_F8007014=[mrd -force 0xF8007014]"
} err2]} { puts "S5WE_MRD_WARN=$err2" }
# A9 核状态（Running 表示应用已运行）
if {[catch {
    targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
    puts "S5WE_A9_0_STATE=[state]"
} err3]} { puts "S5WE_A9_STATE_WARN=$err3" }
disconnect
puts "S5WE_RB_DONE=1"