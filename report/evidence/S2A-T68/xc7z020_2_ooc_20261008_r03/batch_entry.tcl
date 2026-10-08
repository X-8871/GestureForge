# 主控以独立 Vivado batch 进程启动本入口；专用参数防止误用于共享会话。
if {![info exists ::argc] || $::argc != 1 || [lindex $::argv 0] ne {--isolated-batch-r03}} {
    error "必须由独立batch启动并传入--isolated-batch-r03；未获该参数时不退出当前会话"
}
if {[namespace exists ::s2a_xc2_batch_r03]} {
    error "本RunId入口已调用过，拒绝覆盖或重复运行"
}
namespace eval ::s2a_xc2_batch_r03 {
    variable evidence_dir [file dirname [file normalize [info script]]]
    variable cache_dir {D:\FPGA_Competition\tmp\stage2a\S2A-T68\xc7z020_2_ooc_20261008_r03}
    variable stage {batch_preflight}
    variable tier {}
    variable resolved_part {}
    variable started_epoch [clock seconds]

    proc write_new_text {name text} {
        variable evidence_dir
        set stream [open [file join $evidence_dir $name] {WRONLY CREAT EXCL}]
        fconfigure $stream -encoding utf-8 -translation lf
        puts $stream $text
        close $stream
    }

    proc json_string {value} {
        # 器件和版本属性转义后生成UTF-8 JSON，不记录任何许可文件或主机标识。
        set escaped [string map [list "\\" "\\\\" "\"" "\\\"" "\n" "\\n" "\r" "\\r" "\t" "\\t"] $value]
        return "\"$escaped\""
    }

    proc run {} {
        variable evidence_dir
        variable cache_dir
        variable stage
        variable tier
        variable resolved_part
        if {![file isdirectory $evidence_dir] || ![file isdirectory $cache_dir]} {
            error "本RunId精确证据/缓存目录不存在"
        }
        foreach name {batch_preflight.txt batch_result.txt target_resolution.json target_resolution.txt run_result.txt resolved_part_runtime.txt utilization.rpt utilization_hierarchical.rpt timing_summary.rpt clocks.rpt worst_paths.rpt operating_conditions.rpt latch_check_summary.txt latch_cells.txt synthesis_summary.txt s2a_stage2a_core_ooc_post_synth.dcp} {
            if {[file exists [file join $evidence_dir $name]]} {
                error "拒绝覆盖本RunId既有输出：[file join $evidence_dir $name]"
            }
        }
        set tier [get_vivado_tier]
        set vivado_version [version -short]
        write_new_text batch_preflight.txt "VIVADO_VERSION=$vivado_version\nVIVADO_TIER=$tier\nREQUIRED_TIER=BASIC\nENTRY_MODE=isolated_batch_r03"
        puts "S2A_BATCH_ACTUAL_TIER=$tier"
        if {$tier ne {BASIC}} {
            error "实际Vivado tier不是BASIC，不调用本RunId综合：$tier"
        }
        set stage {part_resolution}
        set candidates [get_parts -quiet {xc7z020clg400*}]
        set matched {}
        foreach item $candidates {
            if {[get_property DEVICE $item] eq {xc7z020} && [get_property PACKAGE $item] eq {clg400} && [get_property SPEED $item] eq {-2}} {
                lappend matched $item
            }
        }
        if {[llength $matched] != 1} {
            error "实际XC7Z020/CLG400/-2器件解析须唯一，返回[llength $matched]项"
        }
        set object [lindex $matched 0]
        set resolved_part [get_property NAME $object]
        set temperature_letter [get_property TEMPERATURE_GRADE_LETTER $object]
        set resolution [format {{
  "schema": "s2a-xc2-target-resolution-v1",
  "run_id": "xc7z020_2_ooc_20261008_r03",
  "requested_marking": "XC7Z020-2CLG400I",
  "resolved_part": %s,
  "match_count": 1,
  "queried_candidate_count": %d,
  "device": "xc7z020",
  "package": "clg400",
  "speed": "-2",
  "temperature_grade_letter": %s,
  "vivado_tier": %s,
  "vivado_version": %s,
  "temperature_timing_claim": false
}} [json_string $resolved_part] [llength $candidates] [json_string $temperature_letter] [json_string $tier] [json_string $vivado_version]]
        write_new_text target_resolution.json $resolution
        write_new_text target_resolution.txt "VIVADO_VERSION=$vivado_version\nVIVADO_TIER=$tier\nREQUESTED_MARKING=XC7Z020-2CLG400I\nQUERY_PATTERN=xc7z020clg400*\nQUERY_CANDIDATE_COUNT=[llength $candidates]\nMATCH_COUNT=1\nRESOLVED_PART=$resolved_part\nDEVICE=[get_property DEVICE $object]\nPACKAGE=[get_property PACKAGE $object]\nSPEED=[get_property SPEED $object]\nTEMPERATURE_GRADE_LETTER=$temperature_letter\nTEMPERATURE_TIMING_CLAIM=0"
        puts "S2A_BATCH_ACTUAL_PART=$resolved_part"
        set ::s2a_target_part $resolved_part
        set stage {ooc_source}
        source -encoding utf-8 [file join $evidence_dir run_synthesis.tcl]
        set stage {completed}
        return {BATCH_OOC_COMPLETED}
    }
}

set s2a_batch_previous_directory [pwd]
set s2a_batch_code [catch {
    cd $::s2a_xc2_batch_r03::cache_dir
    ::s2a_xc2_batch_r03::run
} s2a_batch_message s2a_batch_options]
cd $s2a_batch_previous_directory
set s2a_batch_elapsed [expr {[clock seconds] - $::s2a_xc2_batch_r03::started_epoch}]
set s2a_batch_record "BATCH_TCL_RETURN_CODE=$s2a_batch_code\nSTATUS_MESSAGE=$s2a_batch_message\nSTAGE=$::s2a_xc2_batch_r03::stage\nVIVADO_TIER=$::s2a_xc2_batch_r03::tier\nPART=$::s2a_xc2_batch_r03::resolved_part\nSTARTED_EPOCH=$::s2a_xc2_batch_r03::started_epoch\nCOMPLETED_EPOCH=[clock seconds]\nELAPSED_SECONDS=$s2a_batch_elapsed"
if {[catch {::s2a_xc2_batch_r03::write_new_text batch_result.txt $s2a_batch_record} s2a_batch_record_error]} {
    puts stderr "S2A_BATCH_RECORD_FAILED=$s2a_batch_record_error"
    set s2a_batch_code 1
}
puts "S2A_BATCH_RETURN_CODE=$s2a_batch_code"
puts "S2A_BATCH_ELAPSED_SECONDS=$s2a_batch_elapsed"
if {$s2a_batch_code != 0} {
    puts stderr "S2A_BATCH_FAILED=$s2a_batch_message"
    exit 1
}
exit 0
