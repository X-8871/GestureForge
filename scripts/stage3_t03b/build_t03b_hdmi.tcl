# 阶段3 S3-T03b：官方 14_vdma_hdmi_out 在现行器件 xc7z020clg400-2 上重建到比特流
# 只读引用官方源副本；产物全部写入本轮新目录；不烧录、不连接硬件、不动厂商原件。
# 用法: vivado -mode batch -source build_t03b_hdmi.tcl -tclargs <run_dir> <vendor_auto_create_project_dir>

set ::run_dir   [lindex $argv 0]
set ::vendor_dir [lindex $argv 1]
if {$::run_dir eq "" || $::vendor_dir eq ""} {
    puts "T03B_FAIL=USAGE: -tclargs <run_dir> <vendor_dir>"
    exit 3
}
set ::part "xc7z020clg400-2"
set ::proj_name "vdma_hdmi_out"
set ::bd_name "design_1"
set ::proj_dir [file join $::run_dir project]

proc t03b_log {msg} { puts "T03B: $msg" }

proc t03b_fail {msg} {
    puts "T03B_FAIL=$msg"
    exit 2
}

t03b_log "VIVADO_VERSION=[version -short]"
t03b_log "PART=$::part"
t03b_log "RUN_DIR=$::run_dir"
t03b_log "VENDOR_DIR=$::vendor_dir"
if {[info exists ::env(XILINXD_LICENSE_FILE)]} {
    t03b_log "LICENSE_ENV=$::env(XILINXD_LICENSE_FILE)"
} else {
    t03b_log "LICENSE_ENV=<unset>"
}

foreach f [list "ps_config.tcl" "pl_config.tcl" "src/constraints/hdmi_out.xdc"] {
    if {![file exists [file join $::vendor_dir $f]]} {
        t03b_fail "VENDOR_FILE_MISSING:$f"
    }
}
if {![file isdirectory [file join $::vendor_dir my_ip]]} {
    t03b_fail "VENDOR_MY_IP_MISSING"
}

file mkdir $::proj_dir
create_project -force $::proj_name $::proj_dir -part $::part
t03b_log "PROJECT_PART=[get_property PART [current_project]]"

# 自定义 IP 仓库（只读引用官方副本）
set_property ip_repo_paths [file join $::vendor_dir my_ip] [current_project]
update_ip_catalog -quiet

# 复用官方 PS/PL 配置脚本重建 BD
create_bd_design $::bd_name
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
source [file join $::vendor_dir ps_config.tcl]
set_ps_config processing_system7_0
source [file join $::vendor_dir pl_config.tcl]
regenerate_bd_layout
set bd_valid [validate_bd_design]
t03b_log "BD_VALIDATED=$bd_valid"
save_bd_design

set bd_file [get_files ${::bd_name}.bd]
make_wrapper -files $bd_file -top
set wrapper_files [glob -nocomplain [file join $::proj_dir ${::proj_name}.gen sources_1 bd ${::bd_name} hdl *.v]]
if {[llength $wrapper_files] == 0} { t03b_fail "WRAPPER_NOT_FOUND" }
add_files -norecurse $wrapper_files
set ::wrapper_name "${::bd_name}_wrapper"
set_property top $::wrapper_name [current_fileset]
update_compile_order -fileset sources_1
t03b_log "TOP=[get_property top [current_fileset]]"

add_files -fileset constrs_1 -norecurse [file join $::vendor_dir src constraints hdmi_out.xdc]
t03b_log "XDC_ADDED=[get_files -of [get_filesets constrs_1]]"

# 综合 + 实现 + 比特流
launch_runs synth_1 -jobs 4
wait_on_run synth_1
set synth_status [get_property STATUS [get_runs synth_1]]
set synth_progress [get_property PROGRESS [get_runs synth_1]]
t03b_log "SYNTH_STATUS=$synth_status"
t03b_log "SYNTH_PROGRESS=$synth_progress"
if {![string match "*Complete*" $synth_status] || $synth_progress ne "100%"} {
    t03b_fail "SYNTH_NOT_COMPLETE:$synth_status:$synth_progress"
}
open_run synth_1 -name synth_1
report_utilization -file [file join $::run_dir report_utilization_synth.rpt]
report_clock_networks -file [file join $::run_dir report_clock_networks_synth.rpt]
close_design

launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
set impl_status [get_property STATUS [get_runs impl_1]]
set impl_progress [get_property PROGRESS [get_runs impl_1]]
t03b_log "IMPL_STATUS=$impl_status"
t03b_log "IMPL_PROGRESS=$impl_progress"
if {![string match "*Complete*" $impl_status] || $impl_progress ne "100%"} {
    t03b_fail "IMPL_NOT_COMPLETE:$impl_status:$impl_progress"
}

open_run impl_1
report_utilization -file [file join $::run_dir report_utilization_impl.rpt]
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -file [file join $::run_dir report_timing_summary_impl.rpt]
report_drc -file [file join $::run_dir report_drc_impl.rpt]
report_clock_interaction -file [file join $::run_dir report_clock_interaction_impl.rpt]
report_clocks -file [file join $::run_dir report_clocks_impl.rpt]
set wns [get_property STATS.WNS [get_runs impl_1]]
set tns [get_property STATS.TNS [get_runs impl_1]]
set whs [get_property STATS.WHS [get_runs impl_1]]
set ths [get_property STATS.THS [get_runs impl_1]]
t03b_log "TIMING_WNS=$wns"
t03b_log "TIMING_TNS=$tns"
t03b_log "TIMING_WHS=$whs"
t03b_log "TIMING_THS=$ths"

set bitfile [glob -nocomplain [file join $::proj_dir ${::proj_name}.runs impl_1 *.bit]]
t03b_log "BITSTREAM_FILES=$bitfile"

# 导出硬件平台（含 bit），供后续 Vitis 使用
write_hw_platform -fixed -include_bit -force -file [file join $::run_dir ${::bd_name}_wrapper.xsa]
t03b_log "XSA_EXISTS=[file exists [file join $::run_dir ${::bd_name}_wrapper.xsa]]"
close_design

t03b_log "ALL_DONE=1"
exit 0