set t59_run12_temp {D:\FPGA_Competition\report\evidence\S2A-T59\run12\temp}
file mkdir $t59_run12_temp
set ::env(TEMP) $t59_run12_temp
set ::env(TMP) $t59_run12_temp
set ::env(TMPDIR) $t59_run12_temp
source {D:\FPGA_Competition\report\evidence\S2A-T59\run12\isolated_project\project_setup.tcl}
launch_simulation -simset sim_1 -mode behavioral -step compile
launch_simulation -simset sim_1 -mode behavioral -step elaborate
xsim tb_s2a_conv_layer35_row23_all_channels_behav -R -onfinish quit -log {D:\FPGA_Competition\report\evidence\S2A-T59\run12\simulate.log}
close_project
