# 仅打开本次Run隔离inputs目录内的冻结DCP副本并写出固定bit文件。

set expected_part {xc7z020clg400-2}
set expected_dcp_name {s2b_inference_wrapper_postroute_physopt.dcp}
set expected_tcl_name {s15_frozen_dcp_bitgen.tcl}
set expected_bit_name {s2b_inference_wrapper_postroute_physopt.bit}
set expected_progress_name {tcl_progress.jsonl}

proc write_progress {channel event detail} {
    set utc [clock format [clock seconds] -gmt 1 -format %Y-%m-%dT%H:%M:%SZ]
    puts $channel "{\"event\":\"$event\",\"utc\":\"$utc\",\"detail\":\"$detail\"}"
    flush $channel
}

if {[llength $argv] != 4} {
    puts stderr "Expected arguments: run DCP copy, output bitstream, Tcl progress log, evidence root"
    exit 71
}

set dcp [lindex $argv 0]
set bitfile [lindex $argv 1]
set progress_file [lindex $argv 2]
set expected_evidence_root [file normalize [lindex $argv 3]]
set script_path [file normalize [info script]]
set inputs_dir [file dirname $script_path]
set run_dir [file normalize [file dirname $inputs_dir]]
set normalized_dcp [file normalize $dcp]
set normalized_expected_dcp [file normalize [file join $inputs_dir $expected_dcp_name]]
if {[file tail $inputs_dir] ne "inputs" ||
    [file tail $script_path] ne $expected_tcl_name ||
    [string equal $normalized_dcp $normalized_expected_dcp] != 1 ||
    [string equal [file dirname $run_dir] $expected_evidence_root] != 1 ||
    ![regexp {^direct_bitgen_[0-9]{8}T[0-9]{6}Z_[0-9a-f]{16}$} [file tail $run_dir]]} {
    puts stderr "拒绝使用Run隔离目录之外的DCP或Tcl脚本"
    exit 72
}

set bit_parent [file normalize [file dirname $bitfile]]
set progress_parent [file normalize [file dirname $progress_file]]
if {[string equal $bit_parent $run_dir] != 1 ||
    [string equal $progress_parent $run_dir] != 1 ||
    [file tail $bitfile] ne $expected_bit_name ||
    [file tail $progress_file] ne $expected_progress_name} {
    puts stderr "拒绝写入指定Run目录之外的输出"
    exit 73
}
if {[file exists $bitfile] || [file exists $progress_file]} {
    puts stderr "拒绝覆盖已有bitstream或Tcl progress文件"
    exit 74
}
if {[catch {open $progress_file {WRONLY CREAT EXCL}} progress_channel]} {
    puts stderr "无法以排他方式创建Tcl progress文件: $progress_channel"
    exit 75
}
fconfigure $progress_channel -buffering line -encoding utf-8 -translation lf

set command_status [catch {
    set actual_version [version -short]
    puts "DIRECT_BITGEN_VIVADO_VERSION $actual_version"
    if {![regexp {^[0-9]+(\.[0-9]+)*$} $actual_version]} {
        error "Vivado version command returned a non-numeric version"
    }
    write_progress $progress_channel "vivado_version" $actual_version
    if {$actual_version ne "2026.1"} {
        error "Vivado version mismatch: expected 2026.1, actual $actual_version"
    }

    write_progress $progress_channel "open_checkpoint_start" "run_frozen_dcp_copy"
    open_checkpoint $dcp
    set design [current_design]
    if {[llength $design] != 1} {
        error "open_checkpoint did not produce exactly one current design"
    }
    set actual_part [get_property PART $design]
    if {![regexp {^[A-Za-z0-9_-]+$} $actual_part]} {
        error "DCP PART property is malformed"
    }
    write_progress $progress_channel "checkpoint_opened" $actual_part
    if {$actual_part ne $expected_part} {
        error "DCP PART mismatch: expected $expected_part, actual $actual_part"
    }

    write_progress $progress_channel "write_bitstream_start" [file tail $bitfile]
    write_bitstream $bitfile
    if {![file exists $bitfile] || [file size $bitfile] <= 0} {
        error "write_bitstream returned without a non-empty bit file"
    }
    write_progress $progress_channel "write_bitstream_complete" [file size $bitfile]
} command_message command_options]

if {$command_status != 0} {
    write_progress $progress_channel "failed" "see_vivado_log"
    puts stderr "S15 frozen DCP bitgen failed: $command_message"
    close $progress_channel
    exit 1
}

close $progress_channel
exit 0
