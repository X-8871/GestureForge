# 为 T60 run06 创建独立仿真工程，工程及进程临时目录均落在本次 D 盘目录。
set t60_run_root {D:/FPGA_Competition/report/evidence/S2A-T60/run06}
set t60_temp_root [file normalize [file join $t60_run_root "temp"]]
set t60_project_dir [file normalize [file join $t60_run_root "isolated_project"]]
set t60_project_name "s2a_t60_run06"
set t60_expected_top "tb_s2a_conv_layer35_row24_all_channels"
foreach t60_env_name {TEMP TMP TMPDIR} {
    set ::env($t60_env_name) $t60_temp_root
    if {[file normalize $::env($t60_env_name)] ne $t60_temp_root} { error "T60_RUN06_TEMP_BINDING_FAILED name=$t60_env_name" }
}
cd $t60_run_root
if {![file isdirectory [file join $t60_run_root "fixture"]] || ![file isdirectory [file join $t60_run_root "rtl"]]} {
    error "T60_RUN06_STATIC_INPUTS_MISSING root=$t60_run_root"
}
if {[file exists $t60_project_dir]} { error "T60_RUN06_REFUSE_PROJECT_OVERWRITE path=$t60_project_dir" }
set t60_open_project ""
if {![catch {current_project} t60_open_project] && $t60_open_project ne ""} {
    error "T60_RUN06_REFUSE_EXISTING_PROJECT name=$t60_open_project"
}
set t60_source_files [list \
    {D:/FPGA_Competition/report/evidence/S2A-T60/run06/rtl/int8_conv_tap_geometry.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T60/run06/rtl/int8_conv_weight_address.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T60/run06/rtl/int8_mac_accumulator.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T60/run06/rtl/s2a_conv_engine.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T60/run06/rtl/s2a_conv_layer35_channel_probe.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T60/run06/rtl/tb_s2a_conv_layer35_row24_all_channels.sv}
]
foreach t60_source $t60_source_files {
    if {![file isfile $t60_source]} { error "T60_RUN06_SOURCE_MISSING path=$t60_source" }
}
create_project $t60_project_name $t60_project_dir -part xc7z020clg400-1
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
add_files -fileset sim_1 -norecurse $t60_source_files
set_property top $t60_expected_top [get_filesets sim_1]
update_compile_order -fileset sim_1
save_project
puts "T60_RUN06_PROJECT_READY xpr=[file join $t60_project_dir ${t60_project_name}.xpr] top=$t60_expected_top"
