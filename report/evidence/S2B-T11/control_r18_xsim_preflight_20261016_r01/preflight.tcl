# 仅建立隔离仿真工程并核对原矩阵源码；此脚本不启动编译、展开或仿真。
set root {D:/FPGA_Competition/w2b}
set run_id control_r18_xsim_preflight_20261016_r01
set work $root/tmp/2B/S2B-T11/$run_id
set snapshots $root/report/evidence/S2B-T11/$run_id/source_snapshot
create_project csr_xsim $work/project -part xc7z020clg400-2
set_property target_simulator XSim [current_project]
set files {}
foreach name {s2b_control_csr.sv s2b_hp0_word_adapter.sv s2b_request_guard.sv s2a_control_csr.sv s2a_memory_master.sv s2a_runtime_shell.sv tb_s2b_control_csr.sv} {
    lappend files $snapshots/$name
}
add_files -fileset sim_1 -norecurse $files
set_property top tb_s2b_control_csr [get_filesets sim_1]
update_compile_order -fileset sim_1
puts "XSIM_PREFLIGHT_VERSION=[version -short]"
puts "XSIM_PREFLIGHT_EXECUTABLE=[info nameofexecutable]"
puts "XSIM_PREFLIGHT_PART=[get_property PART [current_project]]"
puts "XSIM_PREFLIGHT_TOP=[get_property TOP [get_filesets sim_1]]"
puts "XSIM_PREFLIGHT_SOURCE_ORDER=[get_files -compile_order sources -used_in simulation -of_objects [get_filesets sim_1]]"
foreach prop [list_property [get_filesets sim_1]] {
    if {[string match -nocase *xsim* $prop]} {puts "$prop=[get_property $prop [get_filesets sim_1]]"}
}
