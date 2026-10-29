connect -url tcp:127.0.0.1:3121
puts T_BEGIN
puts [targets]
puts T_END
targets -set -filter {name =~ "*Cortex-A9*#0*"}
puts S_BEGIN
state
puts S_END
puts ID_BEGIN
mrd 0xf8000000 1
puts ID_END
disconnect
exit
