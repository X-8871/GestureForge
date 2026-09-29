set mode [lindex $::argv 0]
if {$mode eq ""} {
    set mode "run"
}
set source_xpr_sha [lindex $::argv 1]
set owner_marker [lindex $::argv 2]
set owner_token [lindex $::argv 3]
set source_manifest_path [lindex $::argv 4]
set source_manifest_sha256 [lindex $::argv 5]
if {$mode ni {dryrun run} || [llength $::argv] != 6} {
    puts stderr "FAIL T57 参数必须为 mode、XPR SHA、owner marker、owner token、compile-source manifest 和其 SHA-256"
    exit 2
}
if {![regexp {^[0-9a-fA-F]{64}$} $source_xpr_sha] ||
    ![regexp {^[0-9a-fA-F]{64}$} $source_manifest_sha256] || $owner_token eq ""} {
    puts stderr "FAIL T57 XPR/compile-source 哈希或隔离工程 owner token 格式不匹配"
    exit 2
}

set source_xpr {D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr}
set source_project_name AX7Z020_Gesture
set ::source_project_sha_expected $source_xpr_sha
set run_directory {D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt02}
set scratch_directory {D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt02\isolated_project}
set scratch_project_name s2a_t57_row21_isolated
set scratch_project_xpr [file join $scratch_directory s2a_t57_row21_isolated.xpr]
set scratch_sim_directory [file join $scratch_directory s2a_t57_row21_isolated.sim sim_s2a_t57_row21 behav xsim]
set no_wave_tcl {D:\FPGA_Competition\sim\s2a_t57_no_wave.tcl}
set xsim_tcl {D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt02\xsim_run.tcl}
set ::t57_compile_source_manifest {D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt02\compile_source_manifest.tsv}
set ::t57_compile_source_manifest_sha256 [string tolower $source_manifest_sha256]
set ::t57_xsim_tcl $xsim_tcl
set status_path [file join $run_directory stage_status.json]
set dryrun_status_path [file join $run_directory t57_dryrun_stage_status.json]
set error_path [file join $run_directory project_simulation_errors.log]
set simset sim_s2a_t57_row21
set top tb_s2a_conv_layer35_row21_all_channels
set part xa7z020clg400-1I
set ::t57_runtime_property_empty false
set ::t57_runtime_control CUSTOM_TCL_RUN_ALL
set ::t57_effective_debug_level UNVERIFIED
set ::t57_custom_tcl_executed false
set ::t57_simulate_log_complete false
set ::t57_finish_time_ns NA
set ::t57_elaborate_batch_path ""
set ::t57_simulate_batch_path ""
set ::t57_elaborate_command_signature ""
set ::t57_simulate_command_signature ""
set ::t57_elaborate_before_compile_batch_path ""
set ::t57_simulate_before_compile_batch_path ""
set ::t57_elaborate_after_compile_batch_path ""
set ::t57_simulate_after_compile_batch_path ""
set ::t57_elaborate_after_elaborate_batch_path ""
set ::t57_simulate_after_elaborate_batch_path ""
set ::t57_log_all_signals 0

proc t57_json_escape {value} {
    set backslash [format %c 92]
    set quote [format %c 34]
    set carriage_return [format %c 13]
    set line_feed [format %c 10]
    set escaped_backslash [format %c%c 92 92]
    set escaped_quote [format %c%c 92 34]
    set escaped_carriage_return [format %c%c 92 114]
    set escaped_line_feed [format %c%c 92 110]
    return [string map [list $backslash $escaped_backslash \
        $quote $escaped_quote $carriage_return $escaped_carriage_return \
        $line_feed $escaped_line_feed] $value]
}

proc t57_json_code {value} {
    if {$value eq "" || $value eq "NA"} {
        return "null"
    }
    return $value
}

proc t57_write_status {path state compile_code elaborate_code simulate_step_tcl_code wdb_value failure_message} {
    global scratch_directory scratch_project_xpr source_project_name source_xpr
    global ::source_project_sha_expected ::t57_runtime_property_empty ::t57_runtime_control
    global ::t57_effective_debug_level ::t57_custom_tcl_executed ::t57_simulate_log_complete
    global ::t57_finish_time_ns ::t57_elaborate_batch_path ::t57_simulate_batch_path ::t57_log_all_signals
    global ::t57_xsim_tcl
    global ::t57_compile_source_manifest ::t57_compile_source_manifest_sha256
    global ::t57_elaborate_command_signature ::t57_simulate_command_signature
    global ::t57_elaborate_before_compile_batch_path ::t57_simulate_before_compile_batch_path
    global ::t57_elaborate_after_compile_batch_path ::t57_simulate_after_compile_batch_path
    global ::t57_elaborate_after_elaborate_batch_path ::t57_simulate_after_elaborate_batch_path
    set project_name s2a_t57_row21_isolated
    set failure_json [t57_json_escape $failure_message]
    set output [open $path w]
    puts $output "{"
    puts $output "  \"schema\": \"GestureForge-S2A-T57-isolated-simulation-status-v5\"," 
    puts $output "  \"status\": \"$state\"," 
    puts $output "  \"data_verification_status\": \"DATA_VERIFICATION_PENDING\"," 
    puts $output "  \"data_verification_report\": null," 
    puts $output "  \"simulation_context\": \"ISOLATED_SCRATCH_PROJECT\","
    puts $output "  \"project_name\": \"$project_name\","
    puts $output "  \"project_directory\": \"[t57_json_escape $scratch_directory]\","
    puts $output "  \"project_xpr_path\": \"[t57_json_escape $scratch_project_xpr]\","
    puts $output "  \"source_project_name\": \"$source_project_name\","
    puts $output "  \"source_project_xpr_path\": \"[t57_json_escape $source_xpr]\","
    puts $output "  \"source_project_xpr_sha256\": \"$::source_project_sha_expected\","
    puts $output "  \"source_project_modified\": false,"
    puts $output "  \"simset\": \"sim_s2a_t57_row21\","
    puts $output "  \"top\": \"tb_s2a_conv_layer35_row21_all_channels\","
    puts $output "  \"runtime_property_empty\": [t57_json_code $::t57_runtime_property_empty],"
    puts $output "  \"runtime_control\": \"$::t57_runtime_control\","
    puts $output "  \"effective_debug_level\": \"$::t57_effective_debug_level\","
    puts $output "  \"custom_tcl_path\": \"[t57_json_escape $::t57_xsim_tcl]\"," 
    puts $output "  \"compile_source_manifest_path\": \"[t57_json_escape $::t57_compile_source_manifest]\"," 
    puts $output "  \"compile_source_manifest_sha256\": \"$::t57_compile_source_manifest_sha256\"," 
    puts $output "  \"custom_tcl_executed\": [t57_json_code $::t57_custom_tcl_executed],"
    puts $output "  \"simulate_log_complete\": [t57_json_code $::t57_simulate_log_complete],"
    puts $output "  \"finish_time_ns\": [t57_json_code $::t57_finish_time_ns],"
    puts $output "  \"elaborate_batch_path\": \"[t57_json_escape $::t57_elaborate_batch_path]\"," 
    puts $output "  \"simulate_batch_path\": \"[t57_json_escape $::t57_simulate_batch_path]\"," 
    puts $output "  \"elaborate_command_signature\": \"[t57_json_escape $::t57_elaborate_command_signature]\"," 
    puts $output "  \"simulate_command_signature\": \"[t57_json_escape $::t57_simulate_command_signature]\"," 
    puts $output "  \"elaborate_before_compile_batch_path\": \"[t57_json_escape $::t57_elaborate_before_compile_batch_path]\"," 
    puts $output "  \"simulate_before_compile_batch_path\": \"[t57_json_escape $::t57_simulate_before_compile_batch_path]\"," 
    puts $output "  \"elaborate_after_compile_batch_path\": \"[t57_json_escape $::t57_elaborate_after_compile_batch_path]\"," 
    puts $output "  \"simulate_after_compile_batch_path\": \"[t57_json_escape $::t57_simulate_after_compile_batch_path]\"," 
    puts $output "  \"elaborate_after_elaborate_batch_path\": \"[t57_json_escape $::t57_elaborate_after_elaborate_batch_path]\"," 
    puts $output "  \"simulate_after_elaborate_batch_path\": \"[t57_json_escape $::t57_simulate_after_elaborate_batch_path]\"," 
    puts $output "  \"log_all_signals\": $::t57_log_all_signals,"
    puts $output "  \"compile_exit_code\": [t57_json_code $compile_code],"
    puts $output "  \"elaboration_exit_code\": [t57_json_code $elaborate_code],"
    puts $output "  \"simulate_step_tcl_code\": [t57_json_code $simulate_step_tcl_code],"
    puts $output "  \"xsim_exit_code\": null,"
    puts $output "  \"xsim_exit_code_captured\": false,"
    puts $output "  \"xsim_exit_code_source\": null,"
    puts $output "  \"vivado_process_exit_code\": null,"
    puts $output "  \"simulate_log_path\": null,"
    puts $output "  \"simulate_log_source\": null,"
    puts $output "  \"simulate_log_sha256\": null,"
    puts $output "  \"wrapper_finalization\": null,"
    puts $output "  \"wdb_generated\": [t57_json_code $wdb_value],"
    puts $output "  \"failure\": \"$failure_json\""
    puts $output "}"
    close $output
}

proc t57_read_file {path} {
    if {![file isfile $path]} {
        error "T57 required file is missing: $path"
    }
    set input [open $path r]
    fconfigure $input -translation binary -encoding binary
    set value [read $input]
    close $input
    return $value
}

proc t57_sha256_file {path} {
    if {![file isfile $path] || [file type $path] ne "file"} {
        error "T57 hash input is missing: $path"
    }
    set output [exec -- certutil.exe -hashfile $path SHA256]
    set hashes [regexp -all -inline -nocase {[0-9a-f]{64}} $output]
    if {[llength $hashes] != 1} {
        error "certutil did not return one SHA-256 for $path"
    }
    return [string tolower [lindex $hashes 0]]
}

proc t57_verify_compile_sources {sources manifest_path} {
    global ::t57_compile_source_manifest_sha256
    if {[string equal -nocase [file normalize $manifest_path] \
            [file normalize {D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt02\compile_source_manifest.tsv}]] == 0} {
        error "compile-source manifest path is not the fixed run09 file"
    }
    if {![file isfile $manifest_path] || [file type $manifest_path] ne "file" ||
        [t57_sha256_file $manifest_path] ne $::t57_compile_source_manifest_sha256} {
        error "compile-source manifest SHA-256 mismatch"
    }
    set manifest [t57_read_file $manifest_path]
    set lines [split [string trimright $manifest "\r\n"] "\n"]
    if {[llength $lines] < 2 ||
        [string trimright [lindex $lines 0] "\r"] ne "GestureForge-S2A-T57-compile-source-manifest-v1"} {
        error "compile-source manifest header or records are missing"
    }
    set records [dict create]
    foreach line [lrange $lines 1 end] {
        set line [string trimright $line "\r"]
        if {$line eq ""} {
            continue
        }
        set fields [split $line "\t"]
        if {[llength $fields] != 3} {
            error "compile-source manifest row is malformed"
        }
        lassign $fields sha256 size path
        if {![regexp {^[0-9a-fA-F]{64}$} $sha256] ||
            ![string is integer -strict $size] || $size < 0} {
            error "compile-source manifest hash or size is malformed: $path"
        }
        set key [string tolower [file normalize $path]]
        if {[dict exists $records $key]} {
            error "compile-source manifest contains a duplicate path: $path"
        }
        dict set records $key [list [string tolower $sha256] $size $path]
    }
    if {[dict size $records] != [llength $sources]} {
        error "compile-source manifest count does not match the actual fileset"
    }
    set seen [dict create]
    foreach source $sources {
        set normalized [file normalize $source]
        set key [string tolower $normalized]
        if {![dict exists $records $key] || [dict exists $seen $key]} {
            error "actual compile source is not uniquely bound: $source"
        }
        lassign [dict get $records $key] expected_sha256 expected_size recorded_path
        if {![string equal -nocase [file normalize $recorded_path] $normalized] ||
            ![file isfile $normalized] || [file type $normalized] ne "file" ||
            [file size $normalized] != $expected_size} {
            error "actual compile source path or size changed: $source"
        }
        if {[t57_sha256_file $normalized] ne $expected_sha256} {
            error "actual compile source SHA-256 changed: $source"
        }
        dict set seen $key 1
    }
    if {[dict size $seen] != [dict size $records]} {
        error "actual compile-source list omitted a bound source"
    }
}

proc t57_copy_new {source destination} {
    if {![file isfile $source]} {
        error "T57 copy source is missing: $source"
    }
    if {[file exists $destination]} {
        error "拒绝覆盖已有 T57 运行证据：$destination"
    }
    file copy -- $source $destination
}

proc t57_command_signature {batch_text executable} {
    set executable_pattern [string map [list . {\.}] $executable]
    set pattern [format {^[ \t]*call[ \t]+%s(\.exe)?[ \t]+(.+)[ \t]*$} $executable_pattern]
    set commands {}
    foreach line [split $batch_text "\n"] {
        if {[regexp -nocase -- $pattern $line -> extension arguments]} {
            regsub -all {[ \t]+} [string trim $arguments] " " signature
            lappend commands $signature
        }
    }
    if {[llength $commands] != 1} {
        error "仿真脚本必须包含唯一实际 $executable 命令，实得 [llength $commands] 条"
    }
    return [lindex $commands 0]
}

proc t57_option_values {command option} {
    set pattern [format {(^|[ \t])%s[ \t]+(\x7b[^\x7d]*\x7d|"[^"]+"|[^ \t]+)} $option]
    set matches [regexp -all -inline -nocase -- $pattern $command]
    if {[expr {[llength $matches] % 3}] != 0} {
        error "无法解析仿真命令选项 $option：$command"
    }
    set values {}
    foreach {whole prefix value} $matches {
        set first [string index $value 0]
        set last [string index $value end]
        if {($first eq "{" && $last eq "}") || ($first eq "\"" && $last eq "\"")} {
            set value [string range $value 1 end-1]
        }
        lappend values $value
    }
    return $values
}

proc t57_record_snapshot_path {snapshot_stage executable path} {
    global ::t57_elaborate_before_compile_batch_path ::t57_simulate_before_compile_batch_path
    global ::t57_elaborate_after_compile_batch_path ::t57_simulate_after_compile_batch_path
    global ::t57_elaborate_after_elaborate_batch_path ::t57_simulate_after_elaborate_batch_path
    set kind [expr {$executable eq "xelab" ? "elaborate" : "simulate"}]
    set variable_name "::t57_${kind}_${snapshot_stage}_batch_path"
    set $variable_name [file normalize $path]
}

proc t57_capture_and_verify_scripts {snapshot_stage scratch_sim_directory run_directory custom_tcl simset top} {
    global ::t57_elaborate_batch_path ::t57_simulate_batch_path
    global ::t57_elaborate_command_signature ::t57_simulate_command_signature
    global ::t57_effective_debug_level
    set allowed_stages {before_compile after_compile after_elaborate}
    if {$snapshot_stage ni $allowed_stages} {
        error "未知的仿真脚本快照阶段：$snapshot_stage"
    }
    set elaborate_source [file join $scratch_sim_directory elaborate.bat]
    set simulate_source [file join $scratch_sim_directory simulate.bat]
    set elaborate_text [t57_read_file $elaborate_source]
    set simulate_text [t57_read_file $simulate_source]
    set elaborate_snapshot [file normalize [file join $run_directory "elaborate.$snapshot_stage.bat"]]
    set simulate_snapshot [file normalize [file join $run_directory "simulate.$snapshot_stage.bat"]]
    t57_copy_new $elaborate_source $elaborate_snapshot
    t57_copy_new $simulate_source $simulate_snapshot
    t57_record_snapshot_path $snapshot_stage elaborate $elaborate_snapshot
    t57_record_snapshot_path $snapshot_stage simulate $simulate_snapshot
    if {$snapshot_stage eq "after_elaborate"} {
        set ::t57_elaborate_batch_path $elaborate_snapshot
        set ::t57_simulate_batch_path $simulate_snapshot
    }

    set elaborate_command [t57_command_signature $elaborate_text xelab]
    set simulate_command [t57_command_signature $simulate_text xsim]
    if {$::t57_elaborate_command_signature eq ""} {
        set ::t57_elaborate_command_signature $elaborate_command
    } elseif {$elaborate_command ne $::t57_elaborate_command_signature} {
        error "xelab 命令签名在仿真阶段间改变：$snapshot_stage"
    }
    if {$::t57_simulate_command_signature eq ""} {
        set ::t57_simulate_command_signature $simulate_command
    } elseif {$simulate_command ne $::t57_simulate_command_signature} {
        error "xsim 命令签名在仿真阶段间改变：$snapshot_stage"
    }

    set debug_values [t57_option_values $elaborate_command --debug]
    set snapshot_values [t57_option_values $elaborate_command --snapshot]
    set top_token "xil_defaultlib.$top"
    if {[llength $debug_values] != 1 || [lindex $debug_values 0] ne "off" ||
        [llength $snapshot_values] != 1 || [lindex $snapshot_values 0] ne "${top}_behav" ||
        [regexp -all -- [format {(^|[ \t])%s([ \t]|$)} [string map [list . {\.}] $top_token]] $elaborate_command] != 1} {
        error "实际 xelab 命令未唯一绑定 --debug off、目标 snapshot 和 top：$elaborate_command"
    }

    set expected_key "Behavioral:${simset}:Functional:${top}"
    set key_values [t57_option_values $simulate_command -key]
    set tclbatch_values [t57_option_values $simulate_command -tclbatch]
    if {[regexp -all -nocase -- {(^|[ \t])-wdb([ \t=]|$)} $simulate_command] != 0} {
        error "实际 xsim 命令启用了 WDB：$simulate_command"
    }
    if {[string first "${top}_behav " $simulate_command] != 0 ||
        [llength $key_values] != 1 || [lindex $key_values 0] ne $expected_key ||
        [llength $tclbatch_values] != 1} {
        error "实际 xsim 命令未唯一绑定目标 snapshot/key/-tclbatch：$simulate_command"
    }
    set tclbatch_value [lindex $tclbatch_values 0]
    set backslash [format %c 92]
    set expected_tclbatch [string map [list $backslash /] [file normalize $custom_tcl]]
    if {[string first $backslash $tclbatch_value] >= 0 ||
        ![string equal -nocase $tclbatch_value $expected_tclbatch] ||
        ![file isfile $tclbatch_value] || [t57_read_file $tclbatch_value] ne [t57_read_file $custom_tcl]} {
        error "实际 xsim 命令的 -tclbatch 必须是 run09 custom Tcl 的正斜杠绝对路径：$tclbatch_value"
    }
    set ::t57_effective_debug_level off
    puts "T57_SCRIPT_SNAPSHOT_VERIFIED stage=$snapshot_stage elaborate=$elaborate_snapshot simulate=$simulate_snapshot debug=off tclbatch=$tclbatch_value"
}

proc t57_find_wdb {root} {
    set matches {}
    set pending [list $root]
    while {[llength $pending] > 0} {
        set directory [lindex $pending end]
        set pending [lrange $pending 0 end-1]
        foreach entry [glob -nocomplain -directory $directory *] {
            if {[file isdirectory $entry]} {
                lappend pending $entry
            } elseif {[string equal -nocase [file extension $entry] ".wdb"]} {
                lappend matches [file normalize $entry]
            }
        }
    }
    return $matches
}

proc t57_check_owned_scratch {scratch_directory owner_marker owner_token} {
    if {![file isfile $owner_marker]} {
        error "缺少隔离工程所有权标记：$owner_marker"
    }
    set handle [open $owner_marker r]
    set marker_content [split [string trim [read $handle]] "\n"]
    close $handle
    if {[lindex $marker_content 0] ne $owner_token ||
        [file normalize [lindex $marker_content 1]] ne [file normalize $scratch_directory]} {
        error "隔离工程所有权标记不匹配"
    }
    if {[file normalize $scratch_directory] ne [file normalize {D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt02\isolated_project}]} {
        error "隔离工程路径与固定安全路径不匹配"
    }
    if {![file isdirectory $scratch_directory]} {
        error "隔离工程目录尚未由本次运行创建"
    }
    if {[file exists [file join $scratch_directory s2a_t57_row21_isolated.xpr]]} {
        error "隔离工程路径中已存在 XPR"
    }
}

proc t57_main {mode source_xpr_sha owner_marker owner_token source_manifest_path source_manifest_sha256} {
    global source_xpr source_project_name run_directory scratch_directory
    global scratch_project_name scratch_project_xpr scratch_sim_directory no_wave_tcl xsim_tcl
    global status_path dryrun_status_path error_path simset top part
    global ::t57_runtime_property_empty ::t57_runtime_control ::t57_effective_debug_level
    global ::t57_custom_tcl_executed ::t57_simulate_log_complete ::t57_finish_time_ns
    global ::t57_elaborate_command_signature ::t57_simulate_command_signature

    set code 0
    set compile_code NA
    set elaborate_code NA
    set simulate_step_tcl_code NA
    set wdb_value NA
    set state SIMULATION_FLOW_RUNNING
    set status_output [expr {$mode eq "run" ? $status_path : $dryrun_status_path}]
    set failure_message ""

    try {
        if {![string equal -nocase [file normalize $source_manifest_path] \
                [file normalize $::t57_compile_source_manifest]] ||
            [string tolower $source_manifest_sha256] ne $::t57_compile_source_manifest_sha256} {
            error "compile-source manifest arguments do not match the fixed run09 binding"
        }
        if {![file isfile $source_xpr]} {
            error "绑定的源 XPR 不存在：$source_xpr"
        }
        if {![file isfile $no_wave_tcl] || ![file isfile $xsim_tcl]} {
            error "T57 no-wave 或 run09 XSim batch Tcl 缺失"
        }
        if {![file isdirectory $run_directory]} {
            error "T57 run09 目录不存在：$run_directory"
        }
        if {[file exists $scratch_directory] && [llength [glob -nocomplain -directory $scratch_directory *]] > 0} {
            error "隔离工程目录非空，拒绝覆盖：$scratch_directory"
        }
        if {[file exists $scratch_project_xpr]} {
            error "隔离工程 XPR 已存在：$scratch_project_xpr"
        }
        if {$mode eq "run"} {
            foreach path [list $status_path $error_path \
                          [file join $run_directory compile.log] \
                          [file join $run_directory elaborate.log] \
                          [file join $run_directory simulate.log] \
                          [file join $run_directory elaborate.before_compile.bat] \
                          [file join $run_directory simulate.before_compile.bat] \
                          [file join $run_directory elaborate.after_compile.bat] \
                          [file join $run_directory simulate.after_compile.bat] \
                          [file join $run_directory elaborate.after_elaborate.bat] \
                          [file join $run_directory simulate.after_elaborate.bat] \
                          [file join $run_directory observed_raw.bin] \
                          [file join $run_directory observed_output.bin]] {
                if {[file exists $path]} {
                    error "拒绝覆盖已有 T57 运行证据：$path"
                }
            }
        } elseif {[file exists $dryrun_status_path]} {
            error "拒绝覆盖已有 T57 dryrun 状态：$dryrun_status_path"
        }
        t57_check_owned_scratch $scratch_directory $owner_marker $owner_token

        puts "T57_SIMULATION_CONTEXT=isolated_scratch_project"
        puts "T57_SOURCE_PROJECT=$source_project_name"
        puts "T57_SOURCE_XPR=$source_xpr"
        puts "T57_SOURCE_XPR_SHA256=$source_xpr_sha"
        puts "T57_SCRATCH_PROJECT=$scratch_project_name"
        puts "T57_SCRATCH_PROJECT_XPR=$scratch_project_xpr"
        puts "T57_SCRATCH_DIRECTORY=$scratch_directory"

        create_project -part $part $scratch_project_name $scratch_directory
        set project [current_project]
        if {[get_property NAME $project] ne $scratch_project_name} {
            error "Vivado 创建的不是 T57 隔离工程"
        }
        if {[file normalize [get_property DIRECTORY $project]] ne [file normalize $scratch_directory]} {
            error "Vivado 隔离工程目录越界：[get_property DIRECTORY $project]"
        }
        if {[get_property PART $project] ne $part} {
            error "隔离工程器件型号不匹配：[get_property PART $project]"
        }
        if {[llength [get_filesets -quiet $simset]] != 0} {
            error "隔离工程内 T57 fileset 名称冲突：$simset"
        }
        create_fileset -simset $simset
        set fileset [get_filesets $simset]
        set sources [list \
            {D:\FPGA_Competition\src\int8_conv_tap_geometry.sv} \
            {D:\FPGA_Competition\src\int8_conv_weight_address.sv} \
            {D:\FPGA_Competition\src\int8_mac_accumulator.sv} \
            {D:\FPGA_Competition\src\s2a_conv_engine.sv} \
            {D:\FPGA_Competition\src\s2a_conv_layer35_channel_probe.sv} \
            {D:\FPGA_Competition\sim\tb_s2a_conv_layer35_row21_all_channels.sv}]
        t57_verify_compile_sources $sources $source_manifest_path
        foreach source $sources {
            if {![file isfile $source]} {
                error "绑定的 T57 源码缺失：$source"
            }
        }
        add_files -fileset $simset -norecurse $sources
        set actual_sources [get_files -of_objects $fileset]
        if {[llength $actual_sources] != [llength $sources]} {
            error "隔离工程源文件数量不匹配"
        }
        foreach expected $sources {
            set found 0
            foreach actual $actual_sources {
                if {[file normalize $actual] eq [file normalize $expected]} {
                    set found 1
                }
            }
            if {!$found} {
                error "隔离工程缺少绑定源文件：$expected"
            }
        }
        t57_verify_compile_sources $actual_sources $source_manifest_path
        set_property top $top $fileset
        current_fileset -simset $fileset
        set active_simset [current_fileset -simset]
        if {[get_property NAME $active_simset] ne $simset} {
            error "T57 fileset 未成为当前 active simulation set"
        }
        set ::t57_xsim_tcl $xsim_tcl
        source $no_wave_tcl
        if {[get_property top $fileset] ne $top} {
            error "隔离工程仿真 top 不匹配"
        }
        if {[get_property xsim.simulate.runtime $fileset] ne ""} {
            error "T57 simulation runtime 必须为空，由 run09 custom Tcl 控制"
        }
        set ::t57_runtime_property_empty true
        set ::t57_log_all_signals [get_property xsim.simulate.log_all_signals $fileset]
        if {$::t57_log_all_signals != 0} {
            error "T57 log_all_signals 未关闭"
        }
        update_compile_order -fileset $simset
        puts "T57_FILESET=$simset"
        puts "T57_ACTIVE_SIMSET=[get_property NAME $active_simset]"
        puts "T57_TOP=[get_property top $fileset]"
        puts "T57_SOURCES=$actual_sources"
        puts "T57_SCRATCH_PROJECT_XPR_CREATED=[file isfile $scratch_project_xpr]"

        if {$mode eq "dryrun"} {
            set state SIMULATION_FLOW_DRYRUN_PASS
            t57_write_status $status_output $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value ""
            puts "T57_ISOLATED_PROJECT_DRYRUN_PASS"
            return 0
        }

        t57_write_status $status_output $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value ""
        t57_verify_compile_sources [get_files -of_objects $fileset] $source_manifest_path
        set script_code [catch {launch_simulation -simset $simset -mode behavioral -scripts_only} script_message]
        if {$script_code != 0} {
            error "simulation script generation failed: $script_message"
        }
        t57_capture_and_verify_scripts before_compile $scratch_sim_directory $run_directory $xsim_tcl $simset $top

        t57_verify_compile_sources [get_files -of_objects $fileset] $source_manifest_path
        set compile_code [catch {launch_simulation -simset $simset -mode behavioral -step compile} compile_message]
        t57_copy_new [file join $scratch_sim_directory compile.log] [file join $run_directory compile.log]
        puts "T57_STAGE=compile exit_code=$compile_code"
        t57_capture_and_verify_scripts after_compile $scratch_sim_directory $run_directory $xsim_tcl $simset $top
        if {$compile_code != 0} {
            error "compile: $compile_message"
        }
        t57_write_status $status_output $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value ""

        set active_simset [current_fileset -simset]
        if {[get_property NAME $active_simset] ne $simset} {
            error "compile 后 active simulation set 被更改"
        }
        source $no_wave_tcl
        t57_verify_compile_sources [get_files -of_objects $fileset] $source_manifest_path
        set elaborate_code [catch {launch_simulation -simset $simset -mode behavioral -step elaborate} elaborate_message]
        t57_copy_new [file join $scratch_sim_directory elaborate.log] [file join $run_directory elaborate.log]
        puts "T57_STAGE=elaboration exit_code=$elaborate_code"
        t57_capture_and_verify_scripts after_elaborate $scratch_sim_directory $run_directory $xsim_tcl $simset $top
        if {$elaborate_code != 0} {
            error "elaboration: $elaborate_message"
        }
        t57_write_status $status_output $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value ""

        set active_simset [current_fileset -simset]
        if {[get_property NAME $active_simset] ne $simset} {
            error "elaboration 后 active simulation set 被更改"
        }
        source $no_wave_tcl
        t57_verify_compile_sources [get_files -of_objects $fileset] $source_manifest_path
        set simulate_step_tcl_code [catch {launch_simulation -simset $simset -mode behavioral -step simulate} xsim_message]
        t57_copy_new [file join $scratch_sim_directory simulate.log] [file join $run_directory simulate.log]
        puts "T57_STAGE=xsim launch_simulation_tcl_code=$simulate_step_tcl_code"
        if {$simulate_step_tcl_code != 0} {
            error "xsim: $xsim_message"
        }
        set simulate_text [t57_read_file [file join $run_directory simulate.log]]
        set custom_sentinel_count [regexp -all -- {T57_CUSTOM_TCL_SENTINEL=run09} $simulate_text]
        set pass_count [regexp -all -line -- {^PASS T57 outputs=} $simulate_text]
        set progress_count [regexp -all -line -- {^PROGRESS T57 outputs=[0-9]+/6656[ \t]*$} $simulate_text]
        if {$custom_sentinel_count != 1 || $pass_count != 1 || $progress_count != 256} {
            error "XSim transcript incomplete: custom=$custom_sentinel_count pass=$pass_count progress=$progress_count"
        }
        if {![regexp {\$finish called at time[ \t]*:[ \t]*([0-9]+)[ \t]+ns} $simulate_text -> finish_time] || $finish_time <= 1000} {
            error "XSim transcript 未证明 custom Tcl run all 到达非默认 $finish"
        }
        set ::t57_custom_tcl_executed true
        set ::t57_simulate_log_complete true
        set ::t57_finish_time_ns $finish_time
        set raw_output [file join $run_directory observed_raw.bin]
        set int8_output [file join $run_directory observed_output.bin]
        if {![file isfile $raw_output] || [file size $raw_output] != 26624 ||
            ![file isfile $int8_output] || [file size $int8_output] != 6656} {
            error "run09 observed 输出文件缺失或长度错误"
        }
        set wdb_files [t57_find_wdb $scratch_sim_directory]
        set wdb_value false
        if {[llength $wdb_files] != 0} {
            set wdb_value true
            error "隔离 no-wave 仿真生成 WDB：$wdb_files"
        }
        set state SIMULATION_FLOW_PASS
        t57_write_status $status_output $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value ""
        puts "T57_ISOLATED_PROJECT_SIMULATION_PASS finish_time_ns=$finish_time"
    } on error {message options} {
        set code 1
        set failure_message $message
        set state SIMULATION_FLOW_FAIL
        puts stderr "FAIL T57 isolated project: $message"
        if {$mode eq "run"} {
            if {[file exists $status_path]} {
                t57_write_status $status_path $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value $failure_message
            } else {
                catch {t57_write_status $status_path $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value $failure_message}
            }
            if {![file exists $error_path]} {
                catch {
                    set error_stream [open $error_path w]
                    puts $error_stream $failure_message
                    close $error_stream
                }
            }
        } else {
            catch {t57_write_status $dryrun_status_path $state $compile_code $elaborate_code $simulate_step_tcl_code $wdb_value $failure_message}
        }
    } finally {
        catch {close_project -quiet}
    }
    return $code
}

set exit_code [t57_main $mode $source_xpr_sha $owner_marker $owner_token \
    $source_manifest_path $source_manifest_sha256]
exit $exit_code
