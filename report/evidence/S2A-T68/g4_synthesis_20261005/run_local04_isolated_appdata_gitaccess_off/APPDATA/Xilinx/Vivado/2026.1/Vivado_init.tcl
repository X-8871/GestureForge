set marker [open {D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local04_isolated_appdata_gitaccess_off\vivado_init_marker.txt} w]
puts D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local04_isolated_appdata_gitaccess_off\vivado_init_marker.txt {INIT_ENTERED}
close D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local04_isolated_appdata_gitaccess_off\vivado_init_marker.txt
set param_result [catch {set_param tclapp.enableGitAccess 0} param_message]
set marker [open {D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local04_isolated_appdata_gitaccess_off\vivado_init_marker.txt} a]
puts D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local04_isolated_appdata_gitaccess_off\vivado_init_marker.txt "SET_PARAM_RESULT=; MESSAGE="
close D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\run_local04_isolated_appdata_gitaccess_off\vivado_init_marker.txt