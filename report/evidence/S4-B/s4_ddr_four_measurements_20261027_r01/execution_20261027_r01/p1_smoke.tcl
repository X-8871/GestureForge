connect -url tcp:127.0.0.1:3121
puts "P1_XSDB_VERSION=[version]"
set allt [targets]
puts "P1_TARGET_COUNT=[llength $allt]"
foreach t $allt { puts "P1_TARGET=$t" }
puts "P1_READ_ONLY_PROBE=[mrd 0xF8007014]"
disconnect
exit 0
