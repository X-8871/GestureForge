# S5-WE window_20261028_r02 B9 重连/恢复：disconnect → 重新 connect → 目标树可枚举 + A9 仍在运行
puts "S5WE_B9_BEGIN"
connect
puts "S5WE_B9_CONNECT1=OK"
puts "S5WE_B9_TARGETS1=[llength [targets]]"
disconnect
puts "S5WE_B9_DISCONNECT1=OK"
after 2000
connect
puts "S5WE_B9_CONNECT2=OK"
puts "S5WE_B9_TARGETS2=[llength [targets]]"
targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}
puts "S5WE_B9_A9_0_STATE=[state]"
disconnect
puts "S5WE_B9_DONE=1"