set project_dir {D:/FPGA_Competition/report/evidence/S2A-T58/run04/isolated_project/T58_Row22_Attempt04} if {[file exists $project_dir]} { error "拒绝覆盖已存在的 run04 isolated project" } file mkdir [file dirname $project_dir] create_project T58_Row22_Attempt04 $project_dir -part xc7z020clg400-1 set_property target_language Verilog [current_project]
add_files -fileset sources_1 -norecurse {D:/FPGA_Competition/src/int8_conv_tap_geometry.sv}
add_files -fileset sources_1 -norecurse {D:/FPGA_Competition/src/int8_conv_weight_address.sv}
add_files -fileset sources_1 -norecurse {D:/FPGA_Competition/src/int8_mac_accumulator.sv}
add_files -fileset sources_1 -norecurse {D:/FPGA_Competition/src/s2a_conv_engine.sv}
add_files -fileset sources_1 -norecurse {D:/FPGA_Competition/src/s2a_conv_layer35_channel_probe.sv}
add_files -fileset sim_1 -norecurse {D:/FPGA_Competition/sim/tb_s2a_conv_layer35_row22_attempt04.sv} set_property top tb_s2a_conv_layer35_row22_attempt04 [get_filesets sim_1] update_compile_order -fileset sim_1 launch_simulation -mode behavioral -simset sim_1
