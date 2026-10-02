# 仅在新隔离目录校验固定厂商单路 BD 或生成 HDL，不加载 XDC、不综合、不连接设备。
if {$argc < 2 || $argc > 4} {puts stderr "EXPECTED_VENDOR_ROOT_NEW_OUTPUT_DIR_OPTIONAL_MODE_OPTIONAL_PHASE"; exit 2}
set vendor_root [lindex $argv 0]
set output_dir [lindex $argv 1]
set mode native
if {$argc >= 3} {set mode [lindex $argv 2]}
if {$mode ni {native azynq_metadata}} {puts stderr "INVALID_MODE"; exit 2}
set phase bd
if {$argc == 4} {set phase [lindex $argv 3]}
if {$phase ni {bd hdl}} {puts stderr "INVALID_PHASE"; exit 2}
if {[file pathtype $vendor_root] ne "absolute" || ![file isdirectory $vendor_root]} {
    puts stderr "INVALID_VENDOR_ROOT"; exit 2
}
if {[file pathtype $output_dir] ne "absolute" || [file exists $output_dir] || ![file isdirectory [file dirname $output_dir]]} {
    puts stderr "OUTPUT_MUST_BE_NEW_WITH_EXISTING_PARENT"; exit 2
}
set expected_commit fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327
set source_relative course_s2_vitis/22_ov5640_single/Vivado/auto_create_project
set checked [catch {
    set actual_commit [string trim [exec git -C $vendor_root rev-parse HEAD]]
    if {$actual_commit ne $expected_commit} {error "VENDOR_COMMIT_MISMATCH"}
    set changes [exec git -C $vendor_root status --porcelain -- $source_relative]
    if {[string trim $changes] ne ""} {error "VENDOR_SOURCE_NOT_CLEAN"}
    set source_root [file join $vendor_root $source_relative]
    foreach name {ps_config.tcl pl_config.tcl} {
        if {![file isfile [file join $source_root $name]]} {error "MISSING_TEMPLATE_$name"}
    }
    if {![file isdirectory [file join $source_root my_ip]]} {error "MISSING_VENDOR_IP"}
} check_error]
if {$checked} {puts stderr $check_error; exit 2}

# 固定来源已核实后创建全新工程；所有生成产物保留在隔离目录。
file mkdir $output_dir
set failed [catch {
    set_param general.maxThreads 1
    set part [get_parts -quiet xa7z020clg400-1I]
    if {[llength $part] != 1 || ![string equal -nocase [lindex $part 0] xa7z020clg400-1I]} {
        error "EXACT_XA_PART_NOT_AVAILABLE"
    }
    set family [get_property FAMILY [lindex $part 0]]
    puts "EXACT_PART_FAMILY=$family"
    set ip_root [file join $source_root my_ip]
    if {$mode eq "azynq_metadata"} {
        if {$family ne "azynq"} {error "UNEXPECTED_XA_FAMILY"}
        # 只对新生成副本添加家族声明；不修改 HDL、端口、参数或原厂文件。
        set ip_root [file join $output_dir vendor_ip_experiment]
        file copy [file join $source_root my_ip] $ip_root
        foreach core {axi_dynclk_v1_0 rgb2dvi_v1_3 ov5640_ip} {
            set xml_path [file join $ip_root $core component.xml]
            set channel [open $xml_path r]
            fconfigure $channel -encoding utf-8
            set xml [read $channel]
            close $channel
            set marker </xilinx:supportedFamilies>
            if {[regexp -all $marker $xml] != 1} {error "INVALID_FAMILY_BLOCK_$core"}
            if {[string first {>azynq</xilinx:family>} $xml] >= 0} {error "ALREADY_HAS_AZYNQ_$core"}
            set addition {<xilinx:family xilinx:lifeCycle="Pre-Production">azynq</xilinx:family>}
            set xml [string map [list $marker "$addition\n      $marker"] $xml]
            set channel [open $xml_path w]
            fconfigure $channel -encoding utf-8 -translation lf
            puts -nonewline $channel $xml
            close $channel
            puts "EXPERIMENTAL_FAMILY_ADDED=$core"
        }
    }
    create_project s3_vendor_bd [file join $output_dir project] -part [lindex $part 0]
    set_property ip_repo_paths [list $ip_root] [current_project]
    update_ip_catalog
    create_bd_design design_1
    create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
    source -encoding utf-8 [file join $source_root ps_config.tcl]
    set_ps_config processing_system7_0
    source -encoding utf-8 [file join $source_root pl_config.tcl]
    validate_bd_design
    save_bd_design
    set cell_count [llength [get_bd_cells]]
    if {$phase eq "hdl"} {
        # 只生成源文件与顶层包装器，禁用任何综合/实现运行；失败保留隔离产物。
        set bd_files [get_files -quiet */design_1.bd]
        if {[llength $bd_files] != 1} {error "EXPECTED_SINGLE_BD_FILE"}
        generate_target all $bd_files
        set wrappers [make_wrapper -files $bd_files -top]
        if {[llength $wrappers] == 0} {error "NO_GENERATED_WRAPPER"}
        foreach wrapper $wrappers {
            if {![file isfile $wrapper]} {error "MISSING_GENERATED_WRAPPER"}
        }
        add_files -norecurse $wrappers
        set_property top design_1_wrapper [current_fileset]
        update_compile_order -fileset sources_1
        puts "GENERATED_WRAPPERS=$wrappers"
    }
    close_project
    set result PASS_BD_VALIDATION_ONLY
    if {$mode eq "azynq_metadata"} {set result PASS_BD_METADATA_EXPERIMENT_ONLY}
    if {$phase eq "hdl"} {set result PASS_HDL_GENERATION_ONLY}
    set result
} result]
set report [open [file join $output_dir result.txt] {WRONLY CREAT EXCL}]
fconfigure $report -encoding utf-8 -translation lf
puts $report "VIVADO=[version -short]"
puts $report "VENDOR_COMMIT=$expected_commit"
puts $report "PART=xa7z020clg400-1I"
puts $report "MODE=$mode"
puts $report "PHASE=$phase"
if {[info exists family]} {puts $report "FAMILY=$family"}
puts $report "FAILED=$failed"
puts $report "RESULT=$result"
if {[info exists cell_count]} {puts $report "BD_CELL_COUNT=$cell_count"}
puts $report "SCOPE=BD_OR_HDL_ONLY_NO_XDC_NO_SYNTHESIS_NO_HARDWARE"
close $report
puts "RESULT=$result"
if {$failed} {exit 2}
exit 0
