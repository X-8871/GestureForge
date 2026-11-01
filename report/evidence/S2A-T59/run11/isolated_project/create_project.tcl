create_project s2a_t59_row23_attempt11 {D:\FPGA_Competition\report\evidence\S2A-T59\run11\isolated_project} -part xc7z020clg400-1
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
add_files -fileset sources_1 -norecurse {D:\FPGA_Competition\src\int8_conv_tap_geometry.sv}
add_files -fileset sources_1 -norecurse {D:\FPGA_Competition\src\int8_conv_weight_address.sv}
add_files -fileset sources_1 -norecurse {D:\FPGA_Competition\src\int8_mac_accumulator.sv}
add_files -fileset sources_1 -norecurse {D:\FPGA_Competition\src\s2a_conv_engine.sv}
add_files -fileset sources_1 -norecurse {D:\FPGA_Competition\src\s2a_conv_layer35_channel_probe.sv}
add_files -fileset sim_1 -norecurse {D:\FPGA_Competition\sim\tb_s2a_conv_layer35_attempt11.sv}
set_property top tb_s2a_conv_layer35_row23_all_channels [get_filesets sim_1]
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
