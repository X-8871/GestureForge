# 阶段3 S3-T04/T05：官方 22_ov5640_single（AN5642 单通道采集→DDR→HDMI 直通）在现行器件
# xc7z020clg400-2 上重建到比特流 + XSA。只读引用官方源副本；不烧录、不连接硬件、不动厂商原件。
# 用法: vivado -mode batch -source build_t04_camera.tcl -tclargs <run_dir> <vendor_auto_create_project_dir>

set ::run_dir    [lindex $argv 0]
set ::vendor_dir [lindex $argv 1]
if {$::run_dir eq "" || $::vendor_dir eq ""} {
    puts "T04_FAIL=USAGE: -tclargs <run_dir> <vendor_dir>"
    exit 3
}
set ::part "xc7z020clg400-2"
set ::proj_name "ov5640_single"
set ::bd_name "design_1"
set ::proj_dir [file join $::run_dir project]

proc t04_log {msg} { puts "T04: $msg" }
proc t04_fail {msg} { puts "T04_FAIL=$msg"; exit 2 }

t04_log "VIVADO_VERSION=[version -short]"
t04_log "PART=$::part"
t04_log "RUN_DIR=$::run_dir"
t04_log "VENDOR_DIR=$::vendor_dir"
if {[info exists ::env(XILINXD_LICENSE_FILE)]} { t04_log "LICENSE_ENV=$::env(XILINXD_LICENSE_FILE)" } else { t04_log "LICENSE_ENV=<unset>" }

foreach f [list "ps_config.tcl" "pl_config.tcl"] {
    if {![file exists [file join $::vendor_dir $f]]} { t04_fail "VENDOR_FILE_MISSING:$f" }
}
if {![file isdirectory [file join $::vendor_dir my_ip]]} { t04_fail "VENDOR_MY_IP_MISSING" }
set xdc_files [glob -nocomplain [file join $::vendor_dir src constraints *.xdc]]
if {[llength $xdc_files] == 0} { t04_fail "VENDOR_XDC_MISSING" }
foreach x $xdc_files { t04_log "XDC_IN=[file tail $x]" }

file mkdir $::proj_dir
create_project -force $::proj_name $::proj_dir -part $::part
t04_log "PROJECT_PART=[get_property PART [current_project]]"

set_property ip_repo_paths [file join $::vendor_dir my_ip] [current_project]
update_ip_catalog -quiet

create_bd_design $::bd_name
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
source [file join $::vendor_dir ps_config.tcl]
set_ps_config processing_system7_0
source [file join $::vendor_dir pl_config.tcl]
regenerate_bd_layout
set bd_valid [validate_bd_design]
t04_log "BD_VALIDATED=$bd_valid"
save_bd_design

set bd_file [get_files ${::bd_name}.bd]
make_wrapper -files $bd_file -top
set wrapper_files [glob -nocomplain [file join $::proj_dir ${::proj_name}.gen sources_1 bd ${::bd_name} hdl *.v]]
if {[llength $wrapper_files] == 0} { t04_fail "WRAPPER_NOT_FOUND" }
add_files -norecurse $wrapper_files
set ::wrapper_name "${::bd_name}_wrapper"
set_property top $::wrapper_name [current_fileset]
update_compile_order -fileset sources_1
t04_log "TOP=[get_property top [current_fileset]]"

add_files -fileset constrs_1 -norecurse $xdc_files
t04_log "XDC_ADDED=[llength [get_files -of [get_filesets constrs_1]]]"

launch_runs synth_1 -jobs 4
wait_on_run synth_1
set synth_status [get_property STATUS [get_runs synth_1]]
set synth_progress [get_property PROGRESS [get_runs synth_1]]
t04_log "SYNTH_STATUS=$synth_status"
t04_log "SYNTH_PROGRESS=$synth_progress"
if {![string match "*Complete*" $synth_status] || $synth_progress ne "100%"} {
    t04_fail "SYNTH_NOT_COMPLETE:$synth_status:$synth_progress"
}
open_run synth_1 -name synth_1
report_utilization -file [file join $::run_dir report_utilization_synth.rpt]
close_design

launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
set impl_status [get_property STATUS [get_runs impl_1]]
set impl_progress [get_property PROGRESS [get_runs impl_1]]
t04_log "IMPL_STATUS=$impl_status"
t04_log "IMPL_PROGRESS=$impl_progress"
if {![string match "*Complete*" $impl_status] || $impl_progress ne "100%"} {
    t04_fail "IMPL_NOT_COMPLETE:$impl_status:$impl_progress"
}

open_run impl_1
report_utilization -file [file join $::run_dir report_utilization_impl.rpt]
report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -file [file join $::run_dir report_timing_summary_impl.rpt]
report_drc -file [file join $::run_dir report_drc_impl.rpt]
report_clock_interaction -file [file join $::run_dir report_clock_interaction_impl.rpt]
report_clocks -file [file join $::run_dir report_clocks_impl.rpt]
t04_log "TIMING_WNS=[get_property STATS.WNS [get_runs impl_1]]"
t04_log "TIMING_TNS=[get_property STATS.TNS [get_runs impl_1]]"
t04_log "TIMING_WHS=[get_property STATS.WHS [get_runs impl_1]]"
t04_log "TIMING_THS=[get_property STATS.THS [get_runs impl_1]]"
t04_log "BITSTREAM_FILES=[glob -nocomplain [file join $::proj_dir ${::proj_name}.runs impl_1 *.bit]]"

write_hw_platform -fixed -include_bit -force -file [file join $::run_dir ${::bd_name}_wrapper.xsa]
t04_log "XSA_EXISTS=[file exists [file join $::run_dir ${::bd_name}_wrapper.xsa]]"
close_design
t04_log "ALL_DONE=1"
exit 0