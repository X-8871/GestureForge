connect -url tcp:127.0.0.1:23121
puts "TARGET_COUNT=[llength [targets]]"
jtag targets
puts "---TARGETS_LIST---"
foreach t [targets] { puts "T=$t" }
disconnect
exit
