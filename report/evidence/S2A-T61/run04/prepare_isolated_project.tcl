# 通过本会话 Vivado MCP 执行，为 T61 run04 创建独立行为仿真工程。
set t61_run_root {D:/FPGA_Competition/report/evidence/S2A-T61/run04}
set t61_temp_root [file normalize [file join $t61_run_root temp]]
set t61_project_dir [file normalize [file join $t61_run_root isolated_project]]
set t61_project_name "s2a_t61_run04"
set t61_expected_top "tb_s2a_conv_layer35_row25_all_channels"
set t61_expected_part "xa7z020clg400-1I"

foreach t61_env_name {TEMP TMP TMPDIR} {
    set ::env($t61_env_name) $t61_temp_root
    if {[file normalize $::env($t61_env_name)] ne $t61_temp_root} {
        error "T61_RUN04_TEMP_BINDING_FAILED name=$t61_env_name value=$::env($t61_env_name)"
    }
}
file mkdir $t61_temp_root
cd $t61_run_root
if {![file isdirectory [file join $t61_run_root fixture]] || ![file isdirectory [file join $t61_run_root rtl]]} {
    error "T61_RUN04_STATIC_INPUTS_MISSING root=$t61_run_root"
}
if {[file exists $t61_project_dir]} { error "T61_RUN04_REFUSE_PROJECT_OVERWRITE path=$t61_project_dir" }
set t61_open_project ""
if {![catch {current_project} t61_open_project] && $t61_open_project ne ""} {
    error "T61_RUN04_REFUSE_EXISTING_PROJECT name=$t61_open_project"
}
set t61_source_files [list \
    {D:/FPGA_Competition/report/evidence/S2A-T61/run04/rtl/int8_conv_tap_geometry.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T61/run04/rtl/int8_conv_weight_address.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T61/run04/rtl/int8_mac_accumulator.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T61/run04/rtl/s2a_conv_engine.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T61/run04/rtl/s2a_conv_layer35_channel_probe.sv} \
    {D:/FPGA_Competition/report/evidence/S2A-T61/run04/rtl/tb_s2a_conv_layer35_row25_all_channels.sv} \
]
foreach t61_source $t61_source_files {
    if {![file isfile $t61_source]} { error "T61_RUN04_SOURCE_MISSING path=$t61_source" }
}
create_project $t61_project_name $t61_project_dir -part $t61_expected_part
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
add_files -fileset sim_1 -norecurse $t61_source_files
set t61_simset [get_filesets sim_1]
set_property top $t61_expected_top $t61_simset
set_property xsim.elaborate.debug_level off $t61_simset
set_property xsim.simulate.log_all_signals 0 $t61_simset
set_property xsim.simulate.runtime {} $t61_simset
set_property xsim.simulate.wdb {} $t61_simset
update_compile_order -fileset sim_1
if {[get_property part [current_project]] ne $t61_expected_part} { error "T61_RUN04_PART_MISMATCH" }
if {[get_property top $t61_simset] ne $t61_expected_top} { error "T61_RUN04_TOP_MISMATCH" }
if {[string tolower [get_property xsim.elaborate.debug_level $t61_simset]] ne "off"} { error "T61_RUN04_DEBUG_NOT_OFF" }
if {[get_property xsim.simulate.log_all_signals $t61_simset]} { error "T61_RUN04_LOG_ALL_SIGNALS_ENABLED" }
if {[get_property xsim.simulate.runtime $t61_simset] ne ""} { error "T61_RUN04_RUNTIME_PROPERTY_NOT_EMPTY" }
if {[get_property xsim.simulate.wdb $t61_simset] ne ""} { error "T61_RUN04_WDB_ENABLED" }
puts "T61_RUN04_PROJECT_READY xpr=[file join $t61_project_dir ${t61_project_name}.xpr] part=$t61_expected_part top=$t61_expected_top temp=$t61_temp_root waveform=off"
