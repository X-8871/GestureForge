# S2A-T58 row22 attempt03 的隔离 Vivado 项目入口。
if {![info exists argv] || [llength $argv] != 1} {
    error "期望一个 run03 证据目录参数"
}

set repo_root {D:\FPGA_Competition}
set run_root [file normalize [lindex $argv 0]]
set expected_run_root [file normalize {D:\FPGA_Competition\report\evidence\S2A-T58\run03}]
if {$run_root ne $expected_run_root} {
    error "run03 目录与固定证据路径不匹配"
}
if {![file isdirectory $run_root]} {
    error "run03 证据目录不存在"
}

set project_name {T58_Row22_Attempt03}
set project_dir [file join $run_root {isolated_project}]
if {[file exists $project_dir]} {
    error "隔离项目目录已存在，拒绝覆盖"
}

set rtl_files [list \
    [file join $repo_root {src} {int8_conv_tap_geometry.sv}] \
    [file join $repo_root {src} {int8_conv_weight_address.sv}] \
    [file join $repo_root {src} {int8_mac_accumulator.sv}] \
    [file join $repo_root {src} {s2a_conv_engine.sv}] \
    [file join $repo_root {src} {s2a_conv_layer35_channel_probe.sv}]]
set tb_file [file join $repo_root {sim} {tb_s2a_conv_layer35_row22_attempt03.sv}]
set xsim_script [file join $run_root {xsim_run.tcl}]
foreach source_file [concat $rtl_files [list $tb_file $xsim_script]] {
    if {![file isfile $source_file]} {
        error "仿真输入文件缺失：$source_file"
    }
}

create_project $project_name $project_dir -part xc7z020clg400-1
set_property target_language Verilog [current_project]
set_property simulator_language Mixed [current_project]
set_property TARGET_SIMULATOR XSim [current_project]

add_files -norecurse -fileset sources_1 $rtl_files
add_files -norecurse -fileset sim_1 $tb_file
set_property top {tb_s2a_conv_layer35_row22_attempt03} [get_filesets sim_1]
set_property xsim.simulate.runtime {all} [get_filesets sim_1]
set_property xsim.simulate.custom_tcl $xsim_script [get_filesets sim_1]
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1

puts {T58_RUN_PROJECT=ISOLATED_PROJECT_CREATED}
puts {T58_RUN_PROJECT=COMPILE_ELABORATE_SIMULATE_BEGIN}
launch_simulation -mode behavioral -step all
puts {T58_RUN_PROJECT=COMPILE_ELABORATE_SIMULATE_RETURNED}
close_project
puts {T58_RUN_PROJECT=CLOSED}
