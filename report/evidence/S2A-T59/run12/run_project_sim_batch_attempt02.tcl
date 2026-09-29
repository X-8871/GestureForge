set t59_temp {D:/FPGA_Competition/report/evidence/S2A-T59/run12/temp}
file mkdir $t59_temp
set ::env(TEMP) $t59_temp
set ::env(TMP) $t59_temp
set ::env(TMPDIR) $t59_temp
set t59_expected_project {D:/FPGA_Competition/report/evidence/S2A-T59/run12/isolated_project}
set t59_open_project [file normalize [get_property DIRECTORY [current_project]]]
if {$t59_open_project ne [file normalize $t59_expected_project]} {error "unexpected current project directory: $t59_open_project"}
set t59_xsim_dir [file normalize [file join $t59_open_project s2a_t59_row23_attempt12.sim sim_1 behav xsim]]
set t59_snapshot_exe [file join $t59_xsim_dir xsim.dir tb_s2a_conv_layer35_row23_all_channels_behav xsimk.exe]
if {![file isfile $t59_snapshot_exe]} {error "missing elaborated snapshot: $t59_snapshot_exe"}
set t59_raw_output {D:/FPGA_Competition/report/evidence/S2A-T59/run12/observed_raw.bin}
set t59_int8_output {D:/FPGA_Competition/report/evidence/S2A-T59/run12/observed_output.bin}
if {[file exists $t59_raw_output] || [file exists $t59_int8_output]} {error "refuse to overwrite prior simulation output"}
set t59_previous_directory [pwd]
cd $t59_xsim_dir
xsim tb_s2a_conv_layer35_row23_all_channels_behav -R -onfinish quit -log {D:/FPGA_Competition/report/evidence/S2A-T59/run12/simulate_attempt02.log}
cd $t59_previous_directory