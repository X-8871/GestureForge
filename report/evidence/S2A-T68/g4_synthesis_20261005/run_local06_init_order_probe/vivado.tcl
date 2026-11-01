set marker [open {D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local06_init_order_probe\init_marker.txt} w]
puts $marker {INIT_ENTERED}
close $marker
set param_result [catch {set_param tclapp.enableGitAccess 0} param_message]
set marker [open {
D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local06_init_order_probe\init_marker.txt
} a]
puts $marker "SET_PARAM_RESULT=$param_result; MESSAGE=$param_message"
close $marker