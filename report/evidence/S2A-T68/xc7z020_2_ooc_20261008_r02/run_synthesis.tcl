# 本脚本只运行新 RunId 的同源 OOC，失败返回 Tcl error，不退出共享 MCP 会话。
if {[namespace exists ::s2a_xc2_ooc_r02]} {
    error "本 RunId 已在当前会话调用过，拒绝覆盖或重复运行"
}
namespace eval ::s2a_xc2_ooc_r02 {
    variable evidence_dir [file dirname [file normalize [info script]]]
    variable cache_dir {D:\FPGA_Competition\tmp\stage2a\S2A-T68\xc7z020_2_ooc_20261008_r02}
    variable python_executable {C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe}
    variable expected_commit {999238284157bed77cdb3a37e3e6eea52daeefc4}
    variable expected_tree {b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67}
    variable top_name {s2a_stage2a_core_ooc}
    variable started_epoch [clock seconds]
    variable resolved_part {}
    variable stage {preflight}
    variable report_failure_count 0
    variable latch_count -1
    variable generalized_latch_count -1
    variable is_latch_count -1
    variable ldce_count -1
    variable ldpe_count -1
    variable source_count 0
    variable synth_completed 0

    proc write_new_text {name text} {
        variable evidence_dir
        set path [file join $evidence_dir $name]
        set stream [open $path {WRONLY CREAT EXCL}]
        fconfigure $stream -encoding utf-8 -translation lf
        puts $stream $text
        close $stream
    }

    proc run {} {
        variable evidence_dir
        variable cache_dir
        variable python_executable
        variable expected_commit
        variable expected_tree
        variable top_name
        variable resolved_part
        variable stage
        variable report_failure_count
        variable latch_count
        variable generalized_latch_count
        variable is_latch_count
        variable ldce_count
        variable ldpe_count
        variable source_count
        variable synth_completed
        if {![file isdirectory $evidence_dir] || ![file isdirectory $cache_dir]} {
            error "已确认的证据或缓存目录不存在"
        }
        foreach name {utilization.rpt utilization_hierarchical.rpt timing_summary.rpt clocks.rpt worst_paths.rpt operating_conditions.rpt latch_cells.txt latch_check_summary.txt synthesis_summary.txt resolved_part_runtime.txt s2a_stage2a_core_ooc_post_synth.dcp run_result.txt} {
            if {[file exists [file join $evidence_dir $name]]} {
                error "本 RunId 已有输出，拒绝覆盖：[file join $evidence_dir $name]"
            }
        }
        if {![info exists ::s2a_target_part] || $::s2a_target_part eq {}} {
            error "主控必须先依据 get_parts 解析结果设置 ::s2a_target_part"
        }
        set part_objects [get_parts -quiet $::s2a_target_part]
        if {[llength $part_objects] != 1} {
            error "实际 get_parts 必须唯一，返回 [llength $part_objects] 项"
        }
        set part_object [lindex $part_objects 0]
        set resolved_part [get_property NAME $part_object]
        if {$resolved_part ne $::s2a_target_part || [get_property DEVICE $part_object] ne {xc7z020} || [get_property PACKAGE $part_object] ne {clg400} || [get_property SPEED $part_object] ne {-2}} {
            error "器件实际属性与主控解析或用户确认的 XC7Z020/CLG400/-2 不一致"
        }
        set binding [exec $python_executable -I -B [file join $evidence_dir prepare_sources.py] --verify-only --part $resolved_part]
        puts "SOURCE_BINDING_PRECHECK=$binding"
        set runtime_part "RESOLVED_PART=$resolved_part"
        foreach property {DEVICE PACKAGE SPEED TEMPERATURE_GRADE_LETTER LUT_ELEMENTS FLIPFLOPS BLOCK_RAMS DSP} {
            append runtime_part "\n$property=[get_property $property $part_object]"
        }
        write_new_text resolved_part_runtime.txt $runtime_part
        set_param general.maxThreads 2
        puts "CANDIDATE_COMMIT=$expected_commit"
        puts "CANDIDATE_TREE=$expected_tree"
        puts "TOP=$top_name"
        puts "PART_NAME=$resolved_part"
        puts "MAX_THREADS=[get_param general.maxThreads]"
        set rtl_names {
            s2a_network_descriptor_pkg.sv int8_maxpool_geometry.sv
            int8_maxpool_window.sv int8_route_query.sv int8_upsample_query.sv
            s2a_conv_tile_engine.sv s2a_maxpool_engine.sv s2a_route_engine.sv
            s2a_upsample_engine.sv s2a_network_backend.sv s2a_memory_master.sv
            s2a_runtime_shell.sv s2a_stage2a_core_ooc.sv s2a_control_csr.sv
        }
        set source_count [llength $rtl_names]
        if {$source_count != 14} { error "RTL 闭包数量必须为 14" }
        set stage {read_verilog}
        foreach name $rtl_names {
            set source [file join $cache_dir sources src $name]
            if {![file isfile $source]} { error "隔离 RTL 不存在：$source" }
            puts "RTL_SOURCE=$source"
            read_verilog -sv $source
        }
        set stage {synthesis}
        synth_design -top $top_name -part $resolved_part -mode out_of_context -flatten_hierarchy none
        set synth_completed 1
        set stage {operating_conditions}
        # 工业温度等级仅作为功耗/环境分析设置，不产生工业温度时序已通过的结论。
        set_operating_conditions -grade industrial
        set stage {reports}
        foreach command [list \
            [list report_operating_conditions -all -file [file join $evidence_dir operating_conditions.rpt]] \
            [list report_utilization -file [file join $evidence_dir utilization.rpt]] \
            [list report_utilization -hierarchical -hierarchical_min_primitive_count 0 -file [file join $evidence_dir utilization_hierarchical.rpt]] \
            [list report_timing_summary -report_unconstrained -file [file join $evidence_dir timing_summary.rpt]] \
            [list report_clocks -file [file join $evidence_dir clocks.rpt]] \
            [list report_timing -delay_type max -max_paths 20 -file [file join $evidence_dir worst_paths.rpt]]] {
            if {[catch {uplevel #0 $command} message]} {
                incr report_failure_count
                puts stderr "S2A_REPORT_FAILED command=$command message=$message"
            }
        }
        set stage {latch_check}
        # 广义分组按 AMD UG953 的 LATCH 属性核对，再并集可用的 IS_LATCH 和明确原语。
        set generalized_cells [get_cells -hierarchical -quiet -filter {PRIMITIVE_SUBGROUP == LATCH || PRIMITIVE_SUBGROUP == latch}]
        set generalized_latch_count [llength $generalized_cells]
        set class_properties [list_property -class cell]
        set is_latch_cells {}
        if {[lsearch -exact $class_properties IS_LATCH] >= 0} {
            set is_latch_cells [get_cells -hierarchical -quiet -filter {IS_LATCH == 1}]
            set is_latch_count [llength $is_latch_cells]
        }
        set ldce_cells [get_cells -hierarchical -quiet -filter {REF_NAME == LDCE}]
        set ldpe_cells [get_cells -hierarchical -quiet -filter {REF_NAME == LDPE}]
        set ldce_count [llength $ldce_cells]
        set ldpe_count [llength $ldpe_cells]
        set latch_cells [lsort -unique [concat $generalized_cells $is_latch_cells $ldce_cells $ldpe_cells]]
        set latch_count [llength $latch_cells]
        set latch_text {}
        foreach cell $latch_cells {
            append latch_text "[get_property NAME $cell]\t[get_property REF_NAME $cell]\t[get_property PRIMITIVE_SUBGROUP $cell]\n"
        }
        write_new_text latch_cells.txt [string trimright $latch_text "\n"]
        write_new_text latch_check_summary.txt "GENERALIZED_PRIMITIVE_SUBGROUP_LATCH_COUNT=$generalized_latch_count\nIS_LATCH_COUNT=$is_latch_count\nIS_LATCH_UNAVAILABLE_SENTINEL=-1\nLDCE_COUNT=$ldce_count\nLDPE_COUNT=$ldpe_count\nUNIQUE_LATCH_COUNT=$latch_count"
        set stage {checkpoint}
        write_checkpoint [file join $evidence_dir s2a_stage2a_core_ooc_post_synth.dcp]
        write_new_text synthesis_summary.txt "Top: $top_name\nPart: $resolved_part\nCandidate commit: $expected_commit\nCandidate tree: $expected_tree\nRTL source count: $source_count\nGeneralized and explicit unique latch count: $latch_count\nClock constraints: none; no target period is frozen; timing reports describe risk only.\nOperating grade: industrial; power/environment setting only; no industrial-temperature timing claim.\nMaximum Vivado threads: [get_param general.maxThreads]\nReport generation failure count: $report_failure_count"
        if {$report_failure_count > 0 || $latch_count > 0} {
            error "报告失败数=$report_failure_count，非预期锁存器数=$latch_count"
        }
        set stage {completed}
        return {SYNTHESIS_COMPLETED}
    }
}

set s2a_previous_directory [pwd]
cd $::s2a_xc2_ooc_r02::cache_dir
set s2a_ooc_code [catch {::s2a_xc2_ooc_r02::run} s2a_ooc_message s2a_ooc_options]
cd $s2a_previous_directory
set s2a_ooc_elapsed [expr {[clock seconds] - $::s2a_xc2_ooc_r02::started_epoch}]
set s2a_ooc_result "TCL_RETURN_CODE=$s2a_ooc_code\nSTATUS_MESSAGE=$s2a_ooc_message\nSTAGE=$::s2a_xc2_ooc_r02::stage\nPART=$::s2a_xc2_ooc_r02::resolved_part\nSTARTED_EPOCH=$::s2a_xc2_ooc_r02::started_epoch\nCOMPLETED_EPOCH=[clock seconds]\nELAPSED_SECONDS=$s2a_ooc_elapsed\nSYNTHESIS_COMPLETED=$::s2a_xc2_ooc_r02::synth_completed\nREPORT_FAILURE_COUNT=$::s2a_xc2_ooc_r02::report_failure_count\nLATCH_COUNT=$::s2a_xc2_ooc_r02::latch_count"
::s2a_xc2_ooc_r02::write_new_text run_result.txt $s2a_ooc_result
puts "S2A_OOC_RETURN_CODE=$s2a_ooc_code"
puts "S2A_OOC_ELAPSED_SECONDS=$s2a_ooc_elapsed"
if {$s2a_ooc_code != 0} {
    return -options $s2a_ooc_options $s2a_ooc_message
}
return $s2a_ooc_message
