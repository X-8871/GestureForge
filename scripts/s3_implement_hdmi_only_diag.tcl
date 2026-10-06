# 阶段3离线 HDMI-only 综合与布局布线诊断；不生成 bitstream、XSA 或访问板卡。

set ::s3_script_path [info script]
set ::s3_repo_root [file dirname [file dirname $::s3_script_path]]
set ::s3_expected_commit fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327
set ::s3_source_relative course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project
set ::s3_expected_device xa7z020clg400-1I
set ::s3_synthesis_flow {Vivado Synthesis 2026}
set ::s3_guard_script_sha256 30031404FB7617B3B05CAA131099E201E2741A15134B302FA5EE5FB8AD1A6450
set ::s3_expected_board_xdc_sha256 D8FD1B1AD450BC44C25AECB0EF2AE3ECE67EB1F718B60D564EA5BBB803665058
set ::s3_classification DIAGNOSTIC_ONLY_NO_BITSTREAM_NO_BOARD_NO_TIMING_SIGNOFF

proc s3_read_utf8_secure {path} {
    set channel [open $path r]
    fconfigure $channel -encoding utf-8 -translation auto
    set value [read $channel]
    close $channel
    return $value
}

proc s3_write_utf8_secure {path value} {
    s3_secure_write_bytes $path [encoding convertto utf-8 $value] OpenExisting
}

proc s3_replace_utf8 {path value} {
    s3_secure_write_bytes $path [encoding convertto utf-8 $value] OpenExisting
}

proc s3_write_sentinel {path value} {
    s3_secure_write_bytes $path [encoding convertto utf-8 $value] OpenExisting
}

proc s3_read_binary {path} {
    set channel [open $path rb]
    fconfigure $channel -translation binary -encoding binary
    set value [read $channel]
    close $channel
    return $value
}

proc s3_secure_write_bytes {path bytes mode} {
    if {$mode ni {CreateNew OpenExisting}} {error "INVALID_SECURE_FILE_MODE: $mode"}
    if {![info exists ::s3_repo_root] || ![file isfile [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]]} {
        error "SECURE_FILE_HELPER_NOT_FOUND"
    }
    set helper [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]
    if {[info exists ::s3_state(output)] && $::s3_state(output) ne ""} {
        set secure_root $::s3_state(output)
    } else {
        set secure_root [file dirname $path]
    }
    set command [list powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $helper \
        -SecureHelper -SecurePath $path -SecureRoot $secure_root -SecureMode $mode]
    set encoded_bytes [binary encode base64 -maxlen 0 $bytes]
    if {[catch {set output [exec {*}$command << $encoded_bytes]} err]} {
        error "SECURE_FILE_WRITE_FAILED: $path; $err"
    }
    if {[string trim $output] ne "S3_SECURE_WRITE=PASS"} {
        error "SECURE_FILE_WRITE_BAD_RESULT: $path; $output"
    }
}

proc s3_secure_write_hash {path bytes root} {
    if {![info exists ::s3_repo_root] || ![file isfile [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]]} {
        error "SECURE_HASH_WRITE_HELPER_NOT_FOUND"
    }
    set helper [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]
    set command [list powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $helper \
        -SecureHelper -SecureHashOnWrite -SecurePath $path -SecureRoot $root -SecureMode OpenExisting]
    set encoded_bytes [binary encode base64 -maxlen 0 $bytes]
    if {[catch {set output [exec {*}$command << $encoded_bytes]} error_text]} {
        error "SECURE_HASH_WRITE_FAILED: $path; $error_text"
    }
    if {![regexp {^S3_SECURE_WRITE=PASS:([A-Fa-f0-9]{64})$} [string trim $output] -> digest]} {
        error "SECURE_HASH_WRITE_BAD_RESULT: $path; $output"
    }
    return [string toupper $digest]
}

proc s3_secure_read_utf8 {path root} {
    if {![info exists ::s3_repo_root] || ![file isfile [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]]} {
        error "SECURE_READ_HELPER_NOT_FOUND"
    }
    set helper [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]
    set command [list powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $helper \
        -SecureReadHelper -SecurePath $path -SecureRoot $root]
    if {[catch {set output [exec {*}$command 2>@1]} error_text]} {
        error "SECURE_READ_FAILED: $path; $error_text"
    }
    if {![regexp {^S3_SECURE_READ=([A-Fa-f0-9]{64}):([A-Za-z0-9+/]*={0,2})$} [string trim $output] -> digest encoded]} {
        error "SECURE_READ_BAD_RESULT: $path; $output"
    }
    set bytes [binary decode base64 $encoded]
    return [dict create sha256 [string toupper $digest] text [encoding convertfrom utf-8 $bytes]]
}

proc s3_expected_generated_clock_xdc_path {project} {
    return [file join $project s3_hdmi_only.gen sources_1 bd s3_hdmi_only ip \
        s3_hdmi_only_rgb2dvi_0_0 src rgb2dvi_clocks.xdc]
}

proc s3_wait_for_generated_clock_xdc_lease {path digest {timeout_ms 120000}} {
    if {![regexp {^[A-Fa-f0-9]{64}$} $digest]} {error "GENERATED_CLOCK_XDC_SHA256_FORMAT_INVALID"}
    set expected_path [s3_expected_generated_clock_xdc_path $::s3_state(project)]
    if {[s3_normalized_key $path] ne [s3_normalized_key $expected_path]} {
        error "GENERATED_CLOCK_XDC_PATH_NOT_EXACT_EXPECTED_PATH: $path"
    }
    set reports [file join $::s3_state(output) reports]
    set request_path [file join $reports generated_clock_xdc.lease_request]
    set ack_path [file join $reports generated_clock_xdc.lease_ack]
    set error_path [file join $reports generated_clock_xdc.lease_error]
    if {[s3_read_utf8_secure $request_path] ne "" || [s3_read_utf8_secure $ack_path] ne "" || [s3_read_utf8_secure $error_path] ne ""} {
        error "GENERATED_CLOCK_XDC_BROKER_CONTROL_NOT_EMPTY_AT_START"
    }
    set path_b64 [binary encode base64 -maxlen 0 [encoding convertto utf-8 $path]]
    set request_text "S3_GENERATED_CLOCK_LEASE=1\nPATH_B64=$path_b64\nSHA256=[string toupper $digest]\n"
    s3_write_utf8_secure $request_path $request_text
    set started [clock milliseconds]
    while {1} {
        set error_text [s3_read_utf8_secure $error_path]
        if {$error_text ne ""} {
            if {![string match "*\n" $error_text]} {after 100; continue}
            if {[regexp {(?m)^S3_GENERATED_CLOCK_LEASE=FAIL$} $error_text]} {
                error "GENERATED_CLOCK_XDC_BROKER_REJECTED: $error_text"
            }
            error "GENERATED_CLOCK_XDC_BROKER_ERROR_FORMAT_INVALID: $error_text"
        }
        set ack_text [s3_read_utf8_secure $ack_path]
        if {$ack_text ne ""} {
            if {![string match "*\n" $ack_text]} {after 100; continue}
            set ack_lines [split [string trimright $ack_text "\r\n"] "\n"]
            if {[llength $ack_lines] != 3 || [lindex $ack_lines 0] ne "S3_GENERATED_CLOCK_LEASE=READY" ||
                ![regexp {^PATH_B64=([A-Za-z0-9+/]*={0,2})$} [lindex $ack_lines 1] -> ack_path_b64] ||
                ![regexp {^SHA256=([A-Fa-f0-9]{64})$} [lindex $ack_lines 2] -> ack_digest]} {
                error "GENERATED_CLOCK_XDC_BROKER_ACK_FORMAT_INVALID: $ack_text"
            }
            set ack_path_decoded [encoding convertfrom utf-8 [binary decode base64 $ack_path_b64]]
            if {[s3_normalized_key $ack_path_decoded] ne [s3_normalized_key $path] ||
                [string toupper $ack_digest] ne [string toupper $digest]} {
                error "GENERATED_CLOCK_XDC_BROKER_ACK_MISMATCH"
            }
            return [dict create path $ack_path_decoded sha256 [string toupper $ack_digest]]
        }
        if {([clock milliseconds] - $started) >= $timeout_ms} {
            s3_secure_write_bytes $error_path [encoding convertto utf-8 "S3_GENERATED_CLOCK_LEASE=FAIL\nERROR=TCL_WAIT_TIMEOUT\n"] OpenExisting
            error "GENERATED_CLOCK_XDC_BROKER_ACK_TIMEOUT"
        }
        after 100
    }
}

proc s3_path_has_traversal {path} {
    set portable [string map [list "\\" "/"] $path]
    return [regexp {(^|/)\.\.?(/|$)} $portable]
}

proc s3_normalized_key {path} {
    set value [string map [list "\\" "/"] $path]
    while {[string first "//" $value] >= 0 && ![string match "//*" $value]} {
        set value [string map [list "//" "/"] $value]
    }
    return [string tolower [string trimright $value "/"]]
}

proc s3_output_is_repo_tmp_child {repo_root output_dir} {
    if {[file pathtype $output_dir] ne "absolute" || [s3_path_has_traversal $output_dir]} {return 0}
    set tmp_key [s3_normalized_key [file join $repo_root tmp]]
    set output_key [s3_normalized_key $output_dir]
    if {$output_key eq $tmp_key} {return 0}
    return [string match "${tmp_key}/*" $output_key]
}

proc s3_validate_arguments {vendor_root output_dir repo_root action} {
    if {[file pathtype $vendor_root] ne "absolute" || [s3_path_has_traversal $vendor_root]} {
        error "INVALID_VENDOR_ROOT_MUST_BE_ABSOLUTE_AND_TRAVERSAL_FREE"
    }
    if {![file isdirectory $vendor_root]} {error "VENDOR_ROOT_NOT_A_DIRECTORY"}
    if {![s3_output_is_repo_tmp_child $repo_root $output_dir]} {
        error "OUTPUT_MUST_BE_AN_ABSOLUTE_TRAVERSAL_FREE_CHILD_OF_REPOSITORY_TMP"
    }
    if {$action eq "prepare-only" && ![file isdirectory $output_dir]} {error "PRELEASED_OUTPUT_TREE_MISSING"}
    if {$action eq "run" && ![file isdirectory $output_dir]} {error "PREPARED_OUTPUT_DIRECTORY_MISSING"}
    return [list $vendor_root $output_dir]
}

proc s3_repo_root_from_vendor {vendor_root} {
    set repo_root $vendor_root
    for {set index 0} {$index < 3} {incr index} {set repo_root [file dirname $repo_root]}
    set expected_vendor [file join $repo_root tmp stage3_reference AX7020_2023.1]
    if {[s3_normalized_key $expected_vendor] ne [s3_normalized_key $vendor_root]} {
        error "VENDOR_ROOT_MUST_BE_REPOSITORY_TMP_STAGE3_REFERENCE_AX7020_2023_1"
    }
    return $repo_root
}

proc s3_audit_hdmi_xdc {text} {
    if {[regexp -nocase {set_output_delay} $text]} {
        error "UNEXPECTED_OUTPUT_DELAY_MUST_NOT_BE_INVENTED_OR_IMPORTED"
    }
    if {[regexp -nocase {create_(generated_)?clock} $text]} {
        error "BOARD_HDMI_XDC_MUST_NOT_CARRY_CLOCK_CONSTRAINTS"
    }
    if {[regexp -nocase {(^|\n)[ \t]*(read_xdc|source[ \t]+[^\r\n]*\.xdc)} $text]} {
        error "NESTED_XDC_LOAD_NOT_ALLOWED"
    }

    set ports {}
    set active_count 0
    foreach raw_line [split $text "\n"] {
        set line [string trim $raw_line " \t\r"]
        if {$line eq "" || [string index $line 0] eq "#"} {continue}
        if {![regexp {^set_property[ \t]+(PACKAGE_PIN|IOSTANDARD)[ \t]+[^ \t]+[ \t]+\[get_ports[ \t]+(.+)\]$} $line -> property port_token]} {
            error "UNEXPECTED_ACTIVE_XDC_COMMAND: $line"
        }
        set port [string trim $port_token "{} \t"]
        if {[regexp -nocase {camera|cmos|ov[0-9]{4}} $port]} {
            error "CAMERA_REFERENCE_IN_HDMI_ONLY_XDC: $port"
        }
        if {![regexp -nocase {^(TMDS_|hdmi_)} $port]} {
            error "NON_HDMI_PORT_IN_HDMI_XDC: $port"
        }
        lappend ports $port
        incr active_count
    }
    if {$active_count == 0} {error "EMPTY_HDMI_XDC"}
    return [lsort -unique $ports]
}

proc s3_remove_bad_clock_relation {text} {
    set needle {create_generated_clock -source [get_ports PixelClk] -multiply_by 5 [get_ports SerialClk]}
    set count 0
    set start 0
    set result ""
    while {1} {
        set index [string first $needle $text $start]
        if {$index < 0} {break}
        set line_start [string last "\n" $text [expr {$index - 1}]]
        set line_start [expr {$line_start + 1}]
        set line_end [string first "\n" $text $index]
        if {$line_end < 0} {set line_end [string length $text]}
        set line [string trim [string range $text $line_start [expr {$line_end - 1}]] " \t\r"]
        if {$line ne $needle} {error "CLOCK_RELATION_NOT_A_STANDALONE_LINE"}
        append result [string range $text $start [expr {$index - 1}]]
        set start [expr {$index + [string length $needle]}]
        incr count
    }
    append result [string range $text $start end]
    if {$count != 1} {error "EXPECTED_EXACTLY_ONE_KNOWN_BAD_CLOCK_RELATION_GOT_$count"}
    if {[string first {create_generated_clock} $result] >= 0} {
        error "UNEXPECTED_ADDITIONAL_GENERATED_CLOCK_CONSTRAINT"
    }
    return $result
}

proc s3_ps_quote {value} {
    return "'[string map [list "'" "''"] $value]'"
}

proc s3_sha256_read_mode {path} {
    if {![info exists ::s3_state(output)] || $::s3_state(output) eq ""} {return Read}
    set output_root $::s3_state(output)
    if {[file pathtype $output_root] ne "absolute" || [s3_path_has_traversal $output_root]} {return Read}
    if {[file pathtype $path] ne "absolute" || [s3_path_has_traversal $path]} {return Read}
    set output_key [s3_normalized_key $output_root]
    set path_key [s3_normalized_key $path]
    if {[string first "${output_key}/" $path_key] == 0} {return ReadWrite}
    return Read
}

proc s3_sha256_manifest {paths} {
    if {[llength $paths] == 0} {error "EMPTY_SHA256_INPUT_MANIFEST"}
    set quoted_read_paths {}
    set quoted_shared_read_paths {}
    foreach path $paths {
        if {[s3_sha256_read_mode $path] eq "ReadWrite"} {
            lappend quoted_shared_read_paths [s3_ps_quote $path]
        } else {
            lappend quoted_read_paths [s3_ps_quote $path]
        }
    }
    set powershell_script "\$ErrorActionPreference='Stop'; \$ProgressPreference='SilentlyContinue'; \$VerbosePreference='SilentlyContinue'; \$readPaths=@([join $quoted_read_paths ,]); \$sharedReadPaths=@([join $quoted_shared_read_paths ,]); function Write-S3Hash(\$p,\$share) { \$sha=\[Security.Cryptography.SHA256\]::Create(); \$stream=\[IO.File\]::Open(\$p,\[IO.FileMode\]::Open,\[IO.FileAccess\]::Read,\$share); try { \$h=\[BitConverter\]::ToString(\$sha.ComputeHash(\$stream)).Replace('-','') } finally { \$stream.Dispose(); \$sha.Dispose() }; Write-Output (\$h + \[char\]9 + \$p) }; foreach (\$p in \$readPaths) { Write-S3Hash \$p (\[IO.FileShare\]::Read) }; foreach (\$p in \$sharedReadPaths) { Write-S3Hash \$p (\[IO.FileShare\]::ReadWrite) }"
    set encoded [binary encode base64 -maxlen 0 [encoding convertto unicode $powershell_script]]
    set output [exec powershell.exe -NoLogo -NoProfile -NonInteractive -OutputFormat Text -EncodedCommand $encoded 2>@1]
    set hashes [dict create]
    foreach line [split [string trim $output "\r\n"] "\n"] {
        set line [string trimright $line "\r"]
        if {$line eq ""} {continue}
        if {![regexp {^([A-Fa-f0-9]{64})\t(.+)$} $line -> digest path]} {
            error "INVALID_SHA256_HELPER_OUTPUT: $line"
        }
        dict set hashes $path [string toupper $digest]
    }
    if {[dict size $hashes] != [llength $paths]} {
        error "SHA256_MANIFEST_CARDINALITY_MISMATCH"
    }
    return $hashes
}

proc s3_tree_sha256_manifest {root} {
    if {![info exists ::s3_state(output)] || $::s3_state(output) eq "" ||
        [s3_sha256_read_mode $root] ne "ReadWrite"} {
        error "TREE_SHA256_ROOT_OUTSIDE_VERIFIED_OUTPUT"
    }
    set helper [file join $::s3_repo_root scripts run_s3_implement_hdmi_only_diag.ps1]
    if {![file isfile $helper] || ![file isdirectory $root]} {error "SECURE_TREE_SHA256_HELPER_OR_ROOT_NOT_FOUND"}
    set command [list powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $helper \
        -SecureTreeHashHelper -SecureRoot $::s3_state(output) -SecureTreeRoot $root]
    if {[catch {set output [exec {*}$command 2>@1]} error_text]} {
        error "SECURE_TREE_SHA256_HELPER_FAILED: $error_text"
    }
    set hashes [dict create]
    set records 0
    foreach line [split [string trim $output "\r\n"] "\n"] {
        set line [string trimright $line "\r"]
        if {$line eq ""} {continue}
        if {![regexp {^S3_SECURE_TREE_SHA256=([A-Fa-f0-9]{64})\t(.+)$} $line -> digest relative]} {
            error "INVALID_SECURE_TREE_SHA256_HELPER_OUTPUT: $line"
        }
        if {[string first "\t" $relative] >= 0 || [string first "\r" $relative] >= 0 ||
            [string first "\n" $relative] >= 0 || [string first ":" $relative] >= 0 ||
            [string match {/*} $relative] || [regexp {(^|/)\.\.?(/|$)} $relative]} {
            error "INVALID_SECURE_TREE_RELATIVE_PATH: $relative"
        }
        if {[dict exists $hashes $relative]} {error "DUPLICATE_SECURE_TREE_RELATIVE_PATH: $relative"}
        dict set hashes $relative [string toupper $digest]
        incr records
    }
    if {$records == 0 || [dict size $hashes] != $records} {
        error "SECURE_TREE_SHA256_MANIFEST_CARDINALITY_MISMATCH"
    }
    return $hashes
}

proc s3_format_tree_sha256_manifest {root hashes} {
    set lines [list "ROOT=$root" "FILE_COUNT=[dict size $hashes]"]
    foreach relative [lsort [dict keys $hashes]] {
        lappend lines "[dict get $hashes $relative]  $relative"
    }
    return "[join $lines \n]\n"
}

proc s3_validate_tree_sha256_manifest {text expected_root} {
    if {[string length $text] < 1 || [string index $text end] ne "\n" || [string first "\r" $text] >= 0} {
        error "SECURE_TREE_MANIFEST_LINE_ENDING_INVALID"
    }
    set lines [split [string range $text 0 end-1] "\n"]
    if {[llength $lines] < 3 || ![string match "ROOT=*" [lindex $lines 0]]} {
        error "SECURE_TREE_MANIFEST_HEADER_INVALID"
    }
    set actual_root [string range [lindex $lines 0] 5 end]
    if {[s3_normalized_key $actual_root] ne [s3_normalized_key $expected_root]} {
        error "SECURE_TREE_MANIFEST_ROOT_MISMATCH"
    }
    if {![regexp {^FILE_COUNT=([1-9][0-9]*)$} [lindex $lines 1] -> declared_count]} {
        error "SECURE_TREE_MANIFEST_COUNT_INVALID"
    }
    if {$declared_count != [llength $lines] - 2} {error "SECURE_TREE_MANIFEST_CARDINALITY_MISMATCH"}
    set seen [dict create]
    foreach line [lrange $lines 2 end] {
        if {![regexp {^([A-Fa-f0-9]{64})  (.+)$} $line -> digest relative]} {
            error "SECURE_TREE_MANIFEST_RECORD_INVALID"
        }
        if {[string first "\\" $relative] >= 0 || [string first "\t" $relative] >= 0 ||
            [string first ":" $relative] >= 0 || [string match {/*} $relative] ||
            [string match {*/} $relative] || [string first "//" $relative] >= 0 ||
            [regexp {(^|/)\.\.?(/|$)} $relative]} {
            error "SECURE_TREE_MANIFEST_RELATIVE_PATH_INVALID: $relative"
        }
        if {[dict exists $seen $relative]} {error "SECURE_TREE_MANIFEST_DUPLICATE_PATH: $relative"}
        dict set seen $relative [string toupper $digest]
    }
    return $declared_count
}

proc s3_validate_preparation_result {text expected_run_id expected_metadata_tree_sha256} {
    if {[string first "S3_TCL_RESULT=PASS:PREPARED\n" $text] < 0 ||
        [string first "RUN_ID=$expected_run_id\n" $text] < 0} {
        error "PREPARATION_RESULT_OR_RUN_ID_MISMATCH"
    }
    if {![regexp -line {^METADATA_COUNT=([1-9][0-9]*)$} $text -> prepared_metadata_count]} {
        error "PREPARATION_METADATA_COPY_FILE_COUNT_MISSING_OR_INVALID"
    }
    if {![regexp -line {^METADATA_TREE_SHA256=([A-Fa-f0-9]{64})$} $text -> prepared_metadata_tree_sha256]} {
        error "PREPARATION_METADATA_TREE_SHA256_MISSING_OR_INVALID"
    }
    if {![regexp -nocase {^[A-F0-9]{64}$} $expected_metadata_tree_sha256] ||
        [string toupper $prepared_metadata_tree_sha256] ne [string toupper $expected_metadata_tree_sha256]} {
        error "PREPARED_METADATA_TREE_SHA256_MISMATCH"
    }
    return [list $prepared_metadata_count [string toupper $prepared_metadata_tree_sha256]]
}

proc s3_load_existing_guard {repo_root} {
    set validator [file join $repo_root scripts s3_validate_hdmi_only_bd.tcl]
    if {![file isfile $validator]} {error "EXISTING_PATH_GUARD_SCRIPT_MISSING"}
    set digest [dict get [s3_sha256_manifest [list $validator]] $validator]
    if {$digest ne $::s3_guard_script_sha256} {error "EXISTING_PATH_GUARD_SCRIPT_SHA256_MISMATCH"}

    set text [s3_read_utf8_secure $validator]
    set boundary {if {$argc < 2 || $argc > 4}}
    set index [string first $boundary $text]
    if {$index < 0} {error "PATH_GUARD_DEFINITION_BOUNDARY_NOT_FOUND"}
    set definitions [string range $text 0 [expr {$index - 1}]]
    if {[string first {proc s3_launch_secure_guardian} $definitions] < 0 ||
        [string first {proc s3_guard_status_dict} $definitions] < 0} {
        error "PATH_GUARD_PROCEDURES_NOT_FOUND_BEFORE_EXECUTABLE_BODY"
    }
    uplevel #0 $definitions
    return $validator
}

proc s3_replace_guard_body_once {body needle replacement label} {
    set first [string first $needle $body]
    if {$first < 0} {error "SECURE_GUARD_EXTENSION_ANCHOR_MISSING: $label"}
    if {[string first $needle $body [expr {$first + [string length $needle]}]] >= 0} {
        error "SECURE_GUARD_EXTENSION_ANCHOR_NOT_UNIQUE: $label"
    }
    return [string replace $body $first [expr {$first + [string length $needle] - 1}] $replacement]
}

proc s3_extend_guard_api {} {
    set body [info body s3_launch_secure_guardian]
    set body [s3_replace_guard_body_once $body \
        {if (ChildExists(GetDirectory(TmpFinal), OutputLeaf)) throw new IOException("OUTPUT_PATH_ALREADY_EXISTS");} \
        {bool outputExists = ChildExists(GetDirectory(TmpFinal), OutputLeaf);
        if ((phase == "run" && !outputExists) || (phase == "hdl_precreated" && !outputExists) || (phase == "hdl" && outputExists)) throw new IOException((phase == "run" || phase == "hdl_precreated") ? "PREPARED_OUTPUT_MISSING" : "OUTPUT_PATH_ALREADY_EXISTS");} \
        output-existence-gate]
    set body [s3_replace_guard_body_once $body \
        {OutputFinal = CreateDirectoryChild(TmpFinal, OutputLeaf);} \
        {string reportsPath = "", checkpointsPath = "", sentinelsPath = "", inputsPath = "";
        if (phase == "run") @L@
            OutputFinal = AcquireSubtree(TmpFinal, Join(TmpFinal, OutputLeaf));
            string runProjectPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "project"));
            string runMetadataPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "vendor_ip_metadata"));
            string runReportsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "reports"));
            string runCheckpointsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "checkpoints"));
            string runSentinelsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "sentinels"));
            string runInputsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "inputs"));
            return "RESULT=PASS_PATH_GUARD_RUN\nOUTPUT=" + OutputFinal + "\nPROJECT=" + runProjectPath + "\nMETADATA=" + runMetadataPath + "\nREPORTS=" + runReportsPath + "\nCHECKPOINTS=" + runCheckpointsPath + "\nSENTINELS=" + runSentinelsPath + "\nINPUTS=" + runInputsPath;
        @R@ else if (phase == "hdl_precreated") @L@
            OutputFinal = AcquireSubtree(TmpFinal, Join(TmpFinal, OutputLeaf));
            reportsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "reports"));
            checkpointsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "checkpoints"));
            sentinelsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "sentinels"));
            inputsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "inputs"));
        @R@ else @L@
        OutputFinal = CreateDirectoryChild(TmpFinal, OutputLeaf);
        if (phase == "hdl") @L@
            reportsPath = CreateDirectoryChild(OutputFinal, "reports");
            checkpointsPath = CreateDirectoryChild(OutputFinal, "checkpoints");
            sentinelsPath = CreateDirectoryChild(OutputFinal, "sentinels");
            inputsPath = CreateDirectoryChild(OutputFinal, "inputs");
        @R@ @R@} \
        guarded-child-create-and-run-open]
    set body [s3_replace_guard_body_once $body \
        {return "RESULT=PASS_PATH_GUARD_PREPARATION\nOUTPUT=" + OutputFinal + "\nPROJECT=" + project + "\nMETADATA=" + metadataPath + "\nMETADATA_COUNT=" + copied + "\nTARGET_FILES_WRITTEN=" + copied;} \
        {return "RESULT=PASS_PATH_GUARD_PREPARATION\nOUTPUT=" + OutputFinal + "\nPROJECT=" + project + "\nMETADATA=" + metadataPath + "\nMETADATA_COUNT=" + copied + "\nMETADATA_TREE_SHA256=" + MetadataTreeSha256(metadataPath, manifest) + "\nREPORTS=" + reportsPath + "\nCHECKPOINTS=" + checkpointsPath + "\nSENTINELS=" + sentinelsPath + "\nINPUTS=" + inputsPath + "\nTARGET_FILES_WRITTEN=" + copied;} \
        guarded-child-status]
    set body [s3_replace_guard_body_once $body \
        {private static int Count(string value, string expression) @L@ return System.Text.RegularExpressions.Regex.Matches(value, expression).Count; @R@} \
        {private static int Count(string value, string expression) @L@ return System.Text.RegularExpressions.Regex.Matches(value, expression).Count; @R@
    private static string HashMetadataFile(string path) @L@
        string full = Normalize(Path.GetFullPath(path));
        SafeFileHandle handle = CreateFileW(full, GenericRead | ReadAttributes, ShareRead | ShareWrite, IntPtr.Zero, OpenExisting, OpenReparse, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), "METADATA_HASH_OPEN_FAILED");
        try @L@
            AttributeTagInfo info = Info(handle);
            if ((info.Attributes & (AttrReparse | AttrDirectory)) != 0 || !String.Equals(FinalPath(handle), full, StringComparison.OrdinalIgnoreCase)) throw new IOException("METADATA_HASH_PATH_OR_TYPE_MISMATCH");
            byte[] digest;
            using (FileStream stream = new FileStream(handle, FileAccess.Read)) @L@
                handle = null;
                using (System.Security.Cryptography.SHA256 sha = System.Security.Cryptography.SHA256.Create()) digest = sha.ComputeHash(stream);
            @R@
            return BitConverter.ToString(digest).Replace("-", "");
        @R@ finally @L@ if (handle != null) handle.Dispose(); @R@
    @R@
    private static string MetadataTreeSha256(string metadataPath, string[] manifest) @L@
        string root = Normalize(Path.GetFullPath(metadataPath)).TrimEnd('\\');
        SortedDictionary<string, string> hashes = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (string entry in manifest) @L@
            string[] parts = entry.Replace('\\', '/').Split('/');
            if (parts.Length < 2 || parts[0] != "my_ip") throw new IOException("METADATA_HASH_SOURCE_PATH_INVALID");
            foreach (string part in parts) if (String.IsNullOrWhiteSpace(part) || part == "." || part == ".." || part.IndexOfAny(new char[] {'\\', '/', ':'}) >= 0) throw new IOException("METADATA_HASH_PATH_COMPONENT_INVALID");
            string relative = String.Join("/", parts, 1, parts.Length - 1);
            string full = root;
            for (int index = 1; index < parts.Length; index++) full = Join(full, parts[index]);
            if (!Under(root, full)) throw new IOException("METADATA_HASH_PATH_ESCAPED_ROOT");
            hashes.Add(relative, HashMetadataFile(full));
        @R@
        if (hashes.Count < 1 || hashes.Count != manifest.Length) throw new IOException("METADATA_HASH_CARDINALITY_MISMATCH");
        StringBuilder canonical = new StringBuilder();
        canonical.Append("FILE_COUNT=").Append(hashes.Count).Append('\n');
        foreach (KeyValuePair<string, string> entry in hashes) canonical.Append(entry.Value.ToUpperInvariant()).Append("  ").Append(entry.Key).Append('\n');
        using (System.Security.Cryptography.SHA256 sha = System.Security.Cryptography.SHA256.Create()) @L@
            return BitConverter.ToString(sha.ComputeHash(new UTF8Encoding(false).GetBytes(canonical.ToString()))).Replace("-", "");
        @R@
    @R@} \
        metadata-copy-snapshot-digest]
    set body [s3_replace_guard_body_once $body \
        {string project = CreateDirectoryChild(OutputFinal, "project"), metadataPath = "";} \
        {string project = phase == "hdl_precreated" ? AcquireSubtree(OutputFinal, Join(OutputFinal, "project")) : CreateDirectoryChild(OutputFinal, "project"), metadataPath = "";} \
        precreated-project-lease]
    set body [s3_replace_guard_body_once $body \
        {metadataPath = CreateDirectoryChild(OutputFinal, "vendor_ip_metadata");} \
        {metadataPath = phase == "hdl_precreated" ? AcquireSubtree(OutputFinal, Join(OutputFinal, "vendor_ip_metadata")) : CreateDirectoryChild(OutputFinal, "vendor_ip_metadata");} \
        precreated-metadata-lease]
    proc s3_launch_secure_guardian {vendor_root source_root output_dir mode phase} $body
}

proc s3_validate_guarded_children {guard_data expected_phase} {
    if {$expected_phase eq "prepare-only"} {
        set expected_result PASS_PATH_GUARD_PREPARATION
    } else {
        set expected_result PASS_PATH_GUARD_RUN
    }
    if {[dict get $guard_data RESULT] ne $expected_result} {error "UNEXPECTED_SECURE_GUARD_RESULT: [dict get $guard_data RESULT]"}
    set output [dict get $guard_data OUTPUT]
    foreach {key leaf} {PROJECT project METADATA vendor_ip_metadata REPORTS reports CHECKPOINTS checkpoints SENTINELS sentinels INPUTS inputs} {
        if {![dict exists $guard_data $key]} {error "SECURE_GUARD_MISSING_CHILD_PATH_$key"}
        set guarded_path [dict get $guard_data $key]
        set expected_path [file join $output $leaf]
        if {[s3_normalized_key $guarded_path] ne [s3_normalized_key $expected_path]} {
            error "SECURE_GUARD_CHILD_PATH_MISMATCH_$key: $guarded_path"
        }
        if {![file isdirectory $guarded_path]} {error "SECURE_GUARD_CHILD_NOT_DIRECTORY_$key: $guarded_path"}
    }
}

proc s3_guarded_output {vendor_root output_dir phase} {
    set source_root [file join $vendor_root {*}$::s3_source_relative]
    set validator [s3_load_existing_guard $::s3_repo_root]
    s3_extend_guard_api
    set guard_phase [expr {$phase eq "prepare-only" ? "hdl_precreated" : "run"}]
    set status [s3_launch_secure_guardian $vendor_root $source_root $output_dir azynq_metadata $guard_phase]
    set data [s3_guard_status_dict $status]
    s3_validate_guarded_children $data $phase
    if {![dict exists $data OUTPUT] || ![dict exists $data PROJECT] || ![dict exists $data METADATA]} {
        error "PATH_GUARD_RETURNED_INCOMPLETE_OUTPUT_PATHS"
    }
    return [dict create output [dict get $data OUTPUT] project [dict get $data PROJECT] metadata [dict get $data METADATA] validator $validator guard_data $data]
}

proc s3_collect_input_files {vendor_root validator} {
    set source_root [file join $vendor_root {*}$::s3_source_relative]
    set tracked [exec git -C $vendor_root ls-files -- "$::s3_source_relative/my_ip"]
    set files [list \
        [file join $source_root ps_config.tcl] \
        [file join $source_root pl_config.tcl] \
        [file join $source_root src constraints hdmi_out.xdc] \
        $validator \
        $::s3_script_path]
    foreach relative [split [string trim $tracked] "\n"] {
        set relative [string trim $relative "\r"]
        if {$relative eq ""} {continue}
        if {![string match "$::s3_source_relative/my_ip/*" $relative] || [s3_path_has_traversal $relative]} {
            error "UNEXPECTED_TRACKED_IP_INPUT_PATH: $relative"
        }
        lappend files [file join $vendor_root {*}[split $relative "/"]]
    }
    set unique [lsort -unique $files]
    foreach path $unique {
        if {![file isfile $path]} {error "MISSING_INPUT_FILE: $path"}
    }
    return $unique
}

proc s3_format_hash_manifest {hashes} {
    set lines {}
    foreach path [lsort [dict keys $hashes]] {lappend lines "[dict get $hashes $path]  $path"}
    return "[join $lines \n]\n"
}

proc s3_timestamp {} {
    return [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S %Z}]
}

proc s3_status_text {} {
    set lines [list \
        "CLASSIFICATION=$::s3_classification" \
        "RUN_ID=$::s3_state(run_id)" \
        "TCL_RESULT=$::s3_state(tcl_result)" \
        "UPDATED_LOCAL=$::s3_state(updated_local)" \
        "STAGE=$::s3_state(stage)" \
        "RESULT=$::s3_state(result)" \
        "ELAPSED_SECONDS=$::s3_state(elapsed_seconds)" \
        "VIVADO_VERSION=$::s3_state(vivado_version)" \
        "DEVICE=$::s3_expected_device" \
        "VENDOR_COMMIT_EXPECTED=$::s3_expected_commit" \
        "VENDOR_COMMIT_ACTUAL=$::s3_state(vendor_commit)" \
        "MAX_THREADS=$::s3_state(max_threads)" \
        "EXECUTION_TCL_PATH=$::s3_state(execution_tcl_path)" \
        "EXECUTION_TCL_SHA256=$::s3_state(execution_tcl_sha256)" \
        "METADATA_COPY_MANIFEST=$::s3_state(metadata_copy_manifest)" \
        "METADATA_COPY_FILE_COUNT=$::s3_state(metadata_copy_count)" \
        "METADATA_TREE_SHA256=$::s3_state(metadata_tree_sha256)" \
        "METADATA_COPY_MANIFEST_SHA256=$::s3_state(metadata_copy_manifest_sha256)" \
        "VIVADO_LOG=$::s3_state(vivado_log)" \
        "VIVADO_JOURNAL=$::s3_state(vivado_journal)" \
        "SYNTH_STATE=$::s3_state(synth_state)" \
        "SYNTHESIS_FLOW=$::s3_state(synthesis_flow)" \
        "SYNTH_RUN_STATUS=$::s3_state(synth_run_status)" \
        "SYNTH_PROGRESS=$::s3_state(synth_progress)" \
        "VERIFIED_HDMI_PORTS=$::s3_state(verified_hdmi_ports)" \
        "OPT_STATE=$::s3_state(opt_state)" \
        "PLACE_STATE=$::s3_state(place_state)" \
        "ROUTE_STATE=$::s3_state(route_state)" \
        "EXPECTED_RUNTIME=$::s3_state(expected_runtime)" \
        "MAX_RUNTIME=$::s3_state(max_runtime)" \
        "NO_PROGRESS_STOP=$::s3_state(no_progress_stop)" \
        "INPUT_SHA256_MANIFEST=$::s3_state(input_sha256_file)" \
        "BOARD_HDMI_XDC_SHA256=$::s3_state(board_xdc_sha256)" \
        "TIMING_REPORT=$::s3_state(timing_report)" \
        "CLOCK_REPORT=$::s3_state(clock_report)" \
        "DRC_REPORT=$::s3_state(drc_report)" \
        "BLACKBOXES_AFTER_SYNTH=$::s3_state(blackboxes_after_synth)" \
        "BLACKBOXES_AFTER_OPT=$::s3_state(blackboxes_after_opt)" \
        "OUTPUT_PORTS_WITHOUT_SET_OUTPUT_DELAY=$::s3_state(missing_output_delays)" \
        "CLOCK_MODEL_LIMITATION=$::s3_state(clock_model_limitation)" \
        "ERROR=$::s3_state(error)"]
    return "[join $lines \n]\n"
}

proc s3_persist_status {} {
    set ::s3_state(updated_local) [s3_timestamp]
    if {[info exists ::s3_state(started_ms)]} {
        set ::s3_state(elapsed_seconds) [expr {([clock milliseconds] - $::s3_state(started_ms)) / 1000}]
    }
    if {[info exists ::s3_state(output)] && $::s3_state(output) ne "" && [file isdirectory $::s3_state(output)]} {
        set path [file join $::s3_state(output) run_status.txt]
        if {![info exists ::s3_status_created] || !$::s3_status_created} {
            s3_secure_write_bytes $path [encoding convertto utf-8 [s3_status_text]] CreateNew
            set ::s3_status_created 1
        } else {
            s3_replace_utf8 $path [s3_status_text]
        }
    }
}

proc s3_emit_tcl_result {result_code} {
    puts "S3_TCL_RESULT=$result_code"
    flush stdout
}

proc s3_prepare_metadata_digest_line {run_id process_id file_count tree_sha256} {
    if {![regexp {^[A-Za-z0-9_-]{1,80}$} $run_id] ||
        ![string is integer -strict $process_id] || $process_id < 1 ||
        ![string is integer -strict $file_count] || $file_count < 1 ||
        ![regexp -nocase {^[A-F0-9]{64}$} $tree_sha256]} {
        error "PREPARE_METADATA_DIGEST_CHANNEL_ARGUMENTS_INVALID"
    }
    return "S3_PREP_METADATA_DIGEST=$run_id|$process_id|$file_count|[string toupper $tree_sha256]"
}

proc s3_open_named_pipe_with_retry {pipe_path access} {
    set started_ms [clock milliseconds]
    set last_error ""
    set last_error_code "UNKNOWN"
    while {1} {
        if {![catch {open $pipe_path $access} channel open_options]} {return $channel}
        set last_error $channel
        if {[dict exists $open_options -errorcode]} {set last_error_code [dict get $open_options -errorcode]}
        if {[clock milliseconds] - $started_ms >= 5000} {
            error "PREPARE_METADATA_PIPE_OPEN_TIMEOUT access=$access error=$last_error errorcode=$last_error_code"
        }
        after 50
    }
}

proc s3_emit_prepare_metadata_digest {pipe_name run_id file_count tree_sha256} {
    if {![regexp {^[A-Za-z0-9_]{1,80}$} $pipe_name]} {
        error "PREPARE_METADATA_DIGEST_PIPE_NAME_INVALID"
    }
    set line [s3_prepare_metadata_digest_line $run_id [pid] $file_count $tree_sha256]
    set pipe_path [format {\\.\pipe\%s} $pipe_name]
    set channel [s3_open_named_pipe_with_retry $pipe_path w]
    try {
        fconfigure $channel -encoding ascii -translation lf -buffering none
        after 250
        puts $channel $line
        flush $channel
    } finally {
        close $channel
    }
}

proc s3_validate_hdmi_ports_after_synth {expected_ports} {
    set actual_xdc_ports [lsort -unique $expected_ports]
    set resolved_ports {}
    foreach port $expected_ports {
        set matches [get_ports -quiet -filter "NAME == {$port}"]
        if {[llength $matches] != 1} {error "HDMI_PORT_NOT_UNIQUELY_RESOLVED_AFTER_SYNTH: $port COUNT=[llength $matches]"}
        set resolved_name [get_property NAME [lindex $matches 0]]
        if {$resolved_name ne $port} {error "HDMI_PORT_NAME_MISMATCH_AFTER_SYNTH: EXPECTED=$port ACTUAL=$resolved_name"}
        lappend resolved_ports $resolved_name
    }
    set resolved_ports [lsort -unique $resolved_ports]
    if {$resolved_ports ne $actual_xdc_ports || [llength $resolved_ports] != 11} {
        error "HDMI_PORT_EXACT_SET_MISMATCH_AFTER_SYNTH: EXPECTED=$actual_xdc_ports ACTUAL=$resolved_ports"
    }
    return $resolved_ports
}

proc s3_validate_synthesis_run_flow {actual_flow expected_flow} {
    if {$actual_flow ne $expected_flow} {
        error "SYNTHESIS_RUN_FLOW_MISMATCH: EXPECTED=$expected_flow ACTUAL=$actual_flow"
    }
    return $actual_flow
}

proc s3_validate_synthesis_completion {run_name run_count progress} {
    if {$run_name ne "synth_1"} {error "UNEXPECTED_SYNTHESIS_RUN_NAME: $run_name"}
    if {![string is integer -strict $run_count] || $run_count != 1} {
        error "EXPECTED_SINGLE_SYNTHESIS_RUN: NAME=$run_name COUNT=$run_count"
    }
    if {$progress ne "100%"} {error "SYNTHESIS_RUN_NOT_COMPLETE: NAME=$run_name PROGRESS=$progress"}
    return COMPLETE
}

proc s3_mark_synthesis_failure {} {
    if {[info exists ::s3_state(synth_state)] && $::s3_state(synth_state) eq "RUNNING"} {
        set ::s3_state(synth_state) FAILED
    }
    if {[info exists ::s3_state(synth_run_status)] &&
        [lsearch -exact {DISCOVERING CREATING READY LAUNCHING RUNNING} $::s3_state(synth_run_status)] >= 0} {
        set ::s3_state(synth_run_status) FAILED
    }
}

proc s3_expected_hdmi_ports {} {
    return [lsort -unique {TMDS_clk_n TMDS_clk_p {TMDS_data_n[0]} {TMDS_data_n[1]} {TMDS_data_n[2]} {TMDS_data_p[0]} {TMDS_data_p[1]} {TMDS_data_p[2]} hdmi_oen hdmi_ddc_scl_io hdmi_ddc_sda_io}]
}

proc s3_set_state {key value} {
    set ::s3_state($key) $value
    s3_persist_status
}

proc s3_stage_begin {name state_key} {
    set ::s3_state(stage) $name
    if {$state_key ne ""} {set ::s3_state($state_key) RUNNING}
    set ::s3_state(error) NONE
    s3_persist_status
}

proc s3_stage_complete {name state_key checkpoint} {
    if {$checkpoint ne ""} {write_checkpoint -force $checkpoint}
    if {$state_key ne ""} {set ::s3_state($state_key) COMPLETE}
    set ::s3_state(stage) "${name}_COMPLETE"
    set sentinel [file join $::s3_state(output) sentinels "${name}.complete"]
    s3_write_sentinel $sentinel "STAGE=$name\nCOMPLETED_LOCAL=[s3_timestamp]\n"
    s3_persist_status
}

proc s3_blackbox_names {} {
    set names {}
    foreach cell [get_cells -hier -quiet] {
        if {[catch {set blackbox [get_property IS_BLACKBOX $cell]}]} {continue}
        if {$blackbox} {lappend names [get_property NAME $cell]}
    }
    return [lsort -unique $names]
}

proc s3_all_output_ports {} {
    set names {}
    foreach port [get_ports -quiet -filter {DIRECTION == OUT}] {lappend names [get_property NAME $port]}
    return [lsort -dictionary -unique $names]
}

proc s3_exec_main {vendor_root output_dir action run_id expected_metadata_manifest_sha256 expected_metadata_tree_sha256 prepare_digest_pipe_name} {
    set ::s3_action $action
    set ::s3_status_created 1
    array set ::s3_state [list \
        output "" project "" run_id $run_id tcl_result NONE stage ARGUMENTS result STARTING error NONE \
        started_ms [clock milliseconds] elapsed_seconds 0 input_sha256_file NOT_READY board_xdc_sha256 NOT_READY \
        execution_tcl_path $::s3_script_path execution_tcl_sha256 NOT_READY metadata_copy_manifest NOT_READY \
        metadata_copy_count NOT_READY metadata_tree_sha256 NOT_READY metadata_copy_manifest_sha256 NOT_READY \
        vivado_log NOT_STARTED vivado_journal NOT_STARTED \
        timing_report NOT_STARTED clock_report NOT_STARTED drc_report NOT_STARTED \
        vivado_version UNKNOWN vendor_commit UNKNOWN max_threads UNKNOWN \
        synth_state NOT_STARTED opt_state NOT_STARTED place_state NOT_STARTED route_state NOT_STARTED \
        synthesis_flow $::s3_synthesis_flow synth_run_status NOT_CREATED synth_progress NOT_STARTED verified_hdmi_ports NOT_CHECKED \
        blackboxes_after_synth NOT_CHECKED blackboxes_after_opt NOT_CHECKED missing_output_delays NOT_CHECKED \
        expected_runtime {10-40 minutes} max_runtime {60 minutes total} no_progress_stop {15 minutes without log/stage progress} \
        clock_model_limitation {Static implementation uses generated default clock constraints; runtime axi_dynclk DRP reprogramming is not modeled.}]

    lassign [s3_validate_arguments $vendor_root $output_dir $::s3_repo_root $action] vendor_root output_dir
    if {$action eq "run"} {
        if {![regexp -nocase {^[A-F0-9]{64}$} $expected_metadata_manifest_sha256]} {
            error "EXPECTED_METADATA_MANIFEST_SHA256_INVALID"
        }
        if {![regexp -nocase {^[A-F0-9]{64}$} $expected_metadata_tree_sha256]} {
            error "EXPECTED_METADATA_TREE_SHA256_INVALID"
        }
        if {$prepare_digest_pipe_name ne ""} {error "RUN_PHASE_MUST_NOT_RECEIVE_PREPARE_DIGEST_PIPE"}
    } elseif {$expected_metadata_manifest_sha256 ne "" || $expected_metadata_tree_sha256 ne "" ||
              ![regexp {^[A-Za-z0-9_]{1,80}$} $prepare_digest_pipe_name]} {
        error "PREPARE_PHASE_MUST_NOT_RECEIVE_METADATA_SHA256_ARGUMENTS"
    }
    set guard [s3_guarded_output $vendor_root $output_dir $action]
    set ::s3_state(output) [dict get $guard output]
    set ::s3_state(project) [dict get $guard project]
    set guard_data [dict get $guard guard_data]
    set ::s3_state(vivado_log) [file join $::s3_state(output) vivado.log]
    set ::s3_state(vivado_journal) [file join $::s3_state(output) vivado.jou]
    if {$action eq "prepare-only"} {
        if {[file size [file join $::s3_state(output) prepare.result]] != 0} {error "PREPARATION_RESULT_NOT_EMPTY_AT_PREPARE_START"}
        set prepared_metadata_count [dict get $guard_data METADATA_COUNT]
        if {![string is integer -strict $prepared_metadata_count] || $prepared_metadata_count < 1} {
            error "GUARDED_METADATA_COPY_FILE_COUNT_INVALID"
        }
        set prepared_metadata_tree_sha256 [dict get $guard_data METADATA_TREE_SHA256]
        if {![regexp -nocase {^[A-F0-9]{64}$} $prepared_metadata_tree_sha256]} {
            error "GUARDED_METADATA_TREE_SHA256_INVALID"
        }
        set prepared_metadata_tree_sha256 [string toupper $prepared_metadata_tree_sha256]
    } else {
        set prepare_result [file join $::s3_state(output) prepare.result]
        if {![file isfile $prepare_result]} {error "PREPARATION_RESULT_MISSING"}
        set prepare_text [s3_read_utf8_secure $prepare_result]
        lassign [s3_validate_preparation_result $prepare_text $run_id $expected_metadata_tree_sha256] \
            prepared_metadata_count prepared_metadata_tree_sha256
    }
    set ::s3_state(metadata_tree_sha256) $prepared_metadata_tree_sha256
    s3_persist_status

    set source_root [file join $vendor_root {*}$::s3_source_relative]
    set board_xdc [file join $source_root src constraints hdmi_out.xdc]
    set xdc_text [s3_read_utf8_secure $board_xdc]
    set board_xdc_bytes [s3_read_binary $board_xdc]
    set xdc_ports [s3_audit_hdmi_xdc $xdc_text]
    set input_files [s3_collect_input_files $vendor_root [dict get $guard validator]]
    set input_hashes [s3_sha256_manifest $input_files]
    set ::s3_state(execution_tcl_sha256) [dict get $input_hashes $::s3_script_path]
    set observed_board_xdc_sha256 [dict get $input_hashes $board_xdc]
    if {$observed_board_xdc_sha256 ne $::s3_expected_board_xdc_sha256} {
        error "OFFICIAL_HDMI_BOARD_XDC_SHA256_MISMATCH"
    }
    set local_board_xdc [file join $::s3_state(output) inputs hdmi_out.xdc]
    if {$action eq "prepare-only"} {
        s3_secure_write_bytes $local_board_xdc $board_xdc_bytes OpenExisting
    }
    if {[dict get [s3_sha256_manifest [list $board_xdc $local_board_xdc]] $local_board_xdc] ne $observed_board_xdc_sha256} {
        error "COPIED_HDMI_XDC_SHA256_MISMATCH"
    }
    set ::s3_state(vendor_commit) [string trim [exec git -C $vendor_root rev-parse HEAD]]
    set ::s3_state(board_xdc_sha256) $observed_board_xdc_sha256
    if {$::s3_state(vendor_commit) ne $::s3_expected_commit} {error "VENDOR_COMMIT_MISMATCH"}
    s3_write_utf8_secure [file join $::s3_state(output) reports input_sha256.txt] [s3_format_hash_manifest $input_hashes]
    set xdc_line_count [llength [split [string trimright $xdc_text "\r\n"] "\n"]]
    s3_write_utf8_secure [file join $::s3_state(output) reports hdmi_xdc_audit.txt] \
        "SOURCE=$board_xdc\nSHA256=$observed_board_xdc_sha256\nLINE_COUNT=$xdc_line_count\nACTIVE_HDMI_PORTS=$xdc_ports\nCLOCK_CONSTRAINT_COUNT=0\nSET_OUTPUT_DELAY_COUNT=0\nSCOPE=HDMI_PINS_AND_IOSTANDARD_CANDIDATE_ONLY\nBOARD_REVISION_BINDING=UNVERIFIED_CANDIDATE_ONLY\n"
    set metadata_manifest_path [file join $::s3_state(output) reports metadata_copy_sha256.txt]
    if {$action eq "prepare-only"} {
        set ::s3_state(metadata_copy_count) $prepared_metadata_count
        set ::s3_state(metadata_copy_manifest_sha256) NOT_READY
    } else {
        if {![file isfile $metadata_manifest_path]} {error "METADATA_COPY_HASH_MANIFEST_MISSING"}
        set metadata_manifest [s3_read_utf8_secure $metadata_manifest_path]
        set observed_manifest_sha256 [dict get [s3_sha256_manifest [list $metadata_manifest_path]] $metadata_manifest_path]
        if {$observed_manifest_sha256 ne [string toupper $expected_metadata_manifest_sha256]} {
            error "METADATA_COPY_MANIFEST_SHA256_MISMATCH"
        }
        set observed_metadata_count [s3_validate_tree_sha256_manifest $metadata_manifest [dict get $guard metadata]]
        if {$observed_metadata_count != $prepared_metadata_count} {
            error "PREPARED_METADATA_COPY_FILE_COUNT_MISMATCH"
        }
        set ::s3_state(metadata_copy_count) $observed_metadata_count
        set ::s3_state(metadata_copy_manifest_sha256) $observed_manifest_sha256
    }
    set ::s3_state(metadata_copy_manifest) $metadata_manifest_path
    if {$action eq "prepare-only"} {
        set ::s3_state(stage) PREPARED_FOR_RUNNER
        set ::s3_state(result) PREPARED_FOR_CONTROLLED_RUNNER
        set ::s3_state(tcl_result) PASS:PREPARED
        s3_write_sentinel [file join $::s3_state(output) sentinels preflight.complete] "RUN_ID=$run_id\nCOMPLETED_LOCAL=[s3_timestamp]\n"
        s3_persist_status
        s3_write_sentinel [file join $::s3_state(output) prepare.result] "S3_TCL_RESULT=PASS:PREPARED\nRUN_ID=$run_id\nEXECUTION_TCL_SHA256=$::s3_state(execution_tcl_sha256)\nMETADATA_COUNT=$prepared_metadata_count\nMETADATA_TREE_SHA256=$prepared_metadata_tree_sha256\n"
        s3_emit_prepare_metadata_digest $prepare_digest_pipe_name $run_id $prepared_metadata_count $prepared_metadata_tree_sha256
        s3_emit_tcl_result PASS:PREPARED
        s3_persist_status
        puts [s3_status_text]
        return 0
    }

    set expected_hdmi_ports [s3_expected_hdmi_ports]
    if {$xdc_ports ne $expected_hdmi_ports} {
        error "OFFICIAL_BOARD_XDC_HDMI_PORT_SET_MISMATCH: EXPECTED=$expected_hdmi_ports ACTUAL=$xdc_ports"
    }

    set ::s3_state(vivado_version) [version -short]
    set_param general.maxThreads 1
    set ::s3_state(max_threads) [get_param general.maxThreads]
    if {$::s3_state(max_threads) ne "1"} {error "VIVADO_MAX_THREADS_NOT_ONE"}
    set part_matches [get_parts -quiet $::s3_expected_device]
    if {[llength $part_matches] != 1 || ![string equal -nocase [lindex $part_matches 0] $::s3_expected_device]} {
        error "EXACT_DEVICE_NOT_UNIQUE_OR_UNAVAILABLE"
    }
    set part_family [get_property FAMILY [lindex $part_matches 0]]
    if {$part_family ne "azynq"} {error "EXPECTED_AZYNQ_FAMILY_FOR_XA_DEVICE"}

    set ::s3_state(stage) STARTING_PROJECT
    s3_persist_status
    set_param general.maxThreads 1
    create_project s3_hdmi_only [dict get $guard project] -part [lindex $part_matches 0]
    set_property ip_repo_paths [list [dict get $guard metadata]] [current_project]
    update_ip_catalog
    create_bd_design s3_hdmi_only
    create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
    source -encoding utf-8 [file join $source_root ps_config.tcl]
    set_ps_config processing_system7_0
    source -encoding utf-8 [file join $source_root pl_config.tcl]

    set expected_cells [lsort -dictionary {axi_dynclk_0 axi_smc axi_vdma_0 processing_system7_0 ps7_0_axi_periph rgb2dvi_0 rst_ps7_0_100M rst_ps7_0_142M v_axi4s_vid_out_0 v_tc_0 xlconcat_0}]
    set cell_names {}
    foreach cell [get_bd_cells -quiet] {lappend cell_names [get_property NAME $cell]}
    set cell_names [lsort -dictionary $cell_names]
    if {$cell_names ne $expected_cells} {error "UNEXPECTED_HDMI_ONLY_BD_CELL_TOPOLOGY: $cell_names"}
    set intf_names {}
    foreach port [get_bd_intf_ports -quiet] {lappend intf_names [get_property NAME $port]}
    set intf_names [lsort -dictionary $intf_names]
    if {$intf_names ne [lsort -dictionary {DDR FIXED_IO TMDS hdmi_ddc}]} {error "UNEXPECTED_HDMI_BD_INTERFACE_PORTS: $intf_names"}
    set bd_ports {}
    foreach port [get_bd_ports -quiet] {lappend bd_ports [get_property NAME $port]}
    set bd_ports [lsort -dictionary $bd_ports]
    foreach required_port {hdmi_oen TMDS_clk_n TMDS_clk_p TMDS_data_n TMDS_data_p} {
        if {[lsearch -exact $bd_ports $required_port] < 0} {error "MISSING_HDMI_BD_PORT_$required_port"}
    }
    if {[regexp -nocase {camera|ov5640|cmos} [join $bd_ports " "]]} {error "CAMERA_PORT_FOUND_IN_HDMI_ONLY_BD"}
    set initial_constraints [get_files -quiet -of_objects [get_filesets constrs_1]]
    if {[llength $initial_constraints] != 0} {error "UNEXPECTED_PROJECT_XDC_BEFORE_EXPLICIT_HDMI_XDC"}
    validate_bd_design
    save_bd_design
    set bd_files [get_files -quiet */s3_hdmi_only.bd]
    if {[llength $bd_files] != 1} {error "EXPECTED_SINGLE_HDMI_ONLY_BD_FILE"}
    generate_target all $bd_files
    set wrapper_files [make_wrapper -files $bd_files -top]
    if {[llength $wrapper_files] == 0} {error "HDMI_BD_WRAPPER_NOT_GENERATED"}
    foreach wrapper $wrapper_files {if {![file isfile $wrapper]} {error "GENERATED_WRAPPER_MISSING: $wrapper"}}
    add_files -norecurse $wrapper_files
    set_property top s3_hdmi_only_wrapper [current_fileset]

    set clock_xdcs [glob -nocomplain -types f [file join [dict get $guard project] s3_hdmi_only.gen sources_1 bd s3_hdmi_only ip * src rgb2dvi_clocks.xdc]]
    if {[llength $clock_xdcs] != 1} {error "EXPECTED_ONE_GENERATED_RGB2DVI_CLOCK_XDC_GOT_[llength $clock_xdcs]"}
    set generated_clock_xdc [lindex $clock_xdcs 0]
    set project_key [s3_normalized_key [dict get $guard project]]
    set generated_key [s3_normalized_key $generated_clock_xdc]
    if {![string match "${project_key}/*" $generated_key]} {error "GENERATED_CLOCK_XDC_ESCAPES_ISOLATED_PROJECT"}
    set expected_generated_clock_xdc [s3_expected_generated_clock_xdc_path [dict get $guard project]]
    if {$generated_key ne [s3_normalized_key $expected_generated_clock_xdc]} {error "GENERATED_CLOCK_XDC_NOT_AT_EXACT_EXPECTED_PATH: $generated_clock_xdc"}
    set original_generated_clock_record [s3_secure_read_utf8 $generated_clock_xdc $::s3_state(output)]
    set original_generated_clock_xdc [dict get $original_generated_clock_record text]
    set corrected_generated_clock_xdc [s3_remove_bad_clock_relation $original_generated_clock_xdc]
    set generated_clock_written_sha256 [s3_secure_write_hash $generated_clock_xdc [encoding convertto utf-8 $corrected_generated_clock_xdc] $::s3_state(output)]
    set ::s3_state(stage) GENERATED_CLOCK_XDC_LEASE_BARRIER
    s3_persist_status
    set generated_clock_lease [s3_wait_for_generated_clock_xdc_lease $generated_clock_xdc $generated_clock_written_sha256]
    set ::s3_state(generated_clock_xdc_path) $generated_clock_xdc
    set ::s3_state(generated_clock_relation) REMOVED_FROM_ISOLATED_GENERATED_PROJECT_COPY_ONLY
    set ::s3_state(generated_clock_xdc_sha256_before) [dict get [s3_sha256_manifest [list [file join $source_root my_ip rgb2dvi_v1_3 src rgb2dvi_clocks.xdc]]] [file join $source_root my_ip rgb2dvi_v1_3 src rgb2dvi_clocks.xdc]]
    set ::s3_state(generated_clock_xdc_sha256_after) [dict get $generated_clock_lease sha256]
    if {$::s3_state(generated_clock_xdc_sha256_after) ne $generated_clock_written_sha256} {error "GENERATED_CLOCK_XDC_BROKER_SHA256_MISMATCH"}
    set observed_generated_clock_sha256 [dict get [s3_sha256_manifest [list $generated_clock_xdc]] $generated_clock_xdc]
    if {$observed_generated_clock_sha256 ne $::s3_state(generated_clock_xdc_sha256_after)} {error "GENERATED_CLOCK_XDC_CHANGED_DURING_LEASE_HANDOFF"}
    s3_write_utf8_secure [file join $::s3_state(output) reports clock_constraint_change.txt] \
        "OFFICIAL_SOURCE_XDC=[file join $source_root my_ip rgb2dvi_v1_3 src rgb2dvi_clocks.xdc]\nOFFICIAL_SOURCE_SHA256=$::s3_state(generated_clock_xdc_sha256_before)\nISOLATED_PROJECT_COPY=$generated_clock_xdc\nISOLATED_PROJECT_COPY_SHA256_AFTER=$::s3_state(generated_clock_xdc_sha256_after)\nCHANGE=Removed exactly the known PixelClk-to-SerialClk x5 generated-clock command from the project-local generated copy; vendor source unchanged.\n"

    add_files -fileset constrs_1 -norecurse $local_board_xdc
    set local_xdc_obj [get_files -quiet -of_objects [get_filesets constrs_1] $local_board_xdc]
    if {[llength $local_xdc_obj] != 1} {error "HDMI_XDC_NOT_PRESENT_IN_CONSTRAINT_SET"}
    set_property USED_IN_SYNTHESIS true $local_xdc_obj
    set_property USED_IN_IMPLEMENTATION true $local_xdc_obj

    set ::s3_state(stage) PROJECT_BD_COMPLETE
    set ::s3_state(bd_cell_count) [llength $cell_names]
    set ::s3_state(bd_cells) $cell_names
    set ::s3_state(bd_interfaces) $intf_names
    set ::s3_state(xdc_ports) $xdc_ports
    set ::s3_state(input_sha256_file) [file join $::s3_state(output) reports input_sha256.txt]

    set reports [file join $::s3_state(output) reports]
    set checkpoints [file join $::s3_state(output) checkpoints]
    set ::s3_state(stage) SYNTHESIS_RUN_SETUP
    set ::s3_state(synth_state) RUNNING
    set ::s3_state(synth_run_status) DISCOVERING
    set ::s3_state(synth_progress) NOT_STARTED
    s3_persist_status

    set synth_runs [get_runs -quiet synth_1]
    if {[llength $synth_runs] > 1} {error "DUPLICATE_SYNTHESIS_RUN_NAME: synth_1"}
    if {[llength $synth_runs] == 0} {
        set ::s3_state(synth_run_status) CREATING
        s3_persist_status
        create_run -constrset constrs_1 -part $::s3_expected_device -flow $::s3_synthesis_flow synth_1
        set synth_runs [get_runs -quiet synth_1]
    }
    if {[llength $synth_runs] != 1} {error "EXPECTED_SINGLE_SYNTHESIS_RUN_AFTER_SETUP: synth_1 COUNT=[llength $synth_runs]"}
    set synth_run [lindex $synth_runs 0]
    set synth_flow [get_property FLOW $synth_run]
    s3_validate_synthesis_run_flow $synth_flow $::s3_synthesis_flow
    set ::s3_state(synth_run_status) READY
    set ::s3_state(stage) SYNTHESIS_RUN_LAUNCH
    s3_persist_status

    set ::s3_state(synth_run_status) LAUNCHING
    s3_persist_status
    launch_runs -jobs 1 $synth_run
    set ::s3_state(synth_run_status) RUNNING
    set ::s3_state(stage) SYNTHESIS_RUN_WAIT
    s3_persist_status
    wait_on_run $synth_run

    set synth_runs [get_runs -quiet synth_1]
    set synth_progress NOT_AVAILABLE
    if {[llength $synth_runs] == 1} {set synth_progress [get_property PROGRESS [lindex $synth_runs 0]]}
    set ::s3_state(synth_progress) $synth_progress
    s3_validate_synthesis_completion synth_1 [llength $synth_runs] $synth_progress
    set ::s3_state(synth_run_status) [get_property STATUS [lindex $synth_runs 0]]
    set ::s3_state(stage) OPEN_SYNTHESIS_RUN
    s3_persist_status
    open_run -name s3_hdmi_only_synth [lindex $synth_runs 0]

    set ::s3_state(verified_hdmi_ports) [s3_validate_hdmi_ports_after_synth $expected_hdmi_ports]
    set ::s3_state(blackboxes_after_synth) [s3_blackbox_names]
    s3_stage_complete synth "synth_state" [file join $checkpoints synth.dcp]
    set ::s3_state(stage) SYNTHESIS_REPORTS
    s3_persist_status
    report_utilization -file [file join $reports synth_utilization.rpt]
    report_clocks -file [file join $reports synth_clocks.rpt]
    report_timing_summary -delay_type min_max -max_paths 50 -report_unconstrained -file [file join $reports synth_timing_summary.rpt]

    set ::s3_state(stage) OPT_DESIGN
    set ::s3_state(opt_state) RUNNING
    s3_persist_status
    opt_design
    set ::s3_state(blackboxes_after_opt) [s3_blackbox_names]
    if {[llength $::s3_state(blackboxes_after_opt)] != 0} {
        error "UNRESOLVED_BLACKBOXES_AFTER_OPT: $::s3_state(blackboxes_after_opt)"
    }
    s3_stage_complete opt "opt_state" [file join $checkpoints opt.dcp]

    set ::s3_state(stage) PLACE_DESIGN
    set ::s3_state(place_state) RUNNING
    s3_persist_status
    place_design
    s3_stage_complete place "place_state" [file join $checkpoints placed.dcp]
    set ::s3_state(stage) PLACE_REPORTS
    s3_persist_status
    report_utilization -file [file join $reports placed_utilization.rpt]
    report_timing_summary -delay_type min_max -max_paths 50 -report_unconstrained -file [file join $reports placed_timing_summary.rpt]

    set ::s3_state(stage) ROUTE_DESIGN
    set ::s3_state(route_state) RUNNING
    s3_persist_status
    route_design
    s3_stage_complete route "route_state" [file join $checkpoints routed.dcp]
    set ::s3_state(stage) ROUTED_REPORTS
    s3_persist_status
    report_timing_summary -delay_type min_max -max_paths 100 -report_unconstrained -file [file join $reports routed_timing_summary.rpt]
    report_clocks -file [file join $reports routed_clocks.rpt]
    report_clock_interaction -file [file join $reports routed_clock_interaction.rpt]
    check_timing -verbose -file [file join $reports routed_check_timing.rpt]
    report_drc -file [file join $reports routed_drc.rpt]
    set ::s3_state(missing_output_delays) [s3_all_output_ports]
    set ::s3_state(output_delay_constraint_count) 0
    set ::s3_state(timing_report) [file join $reports routed_timing_summary.rpt]
    set ::s3_state(clock_report) [file join $reports routed_clocks.rpt]
    set ::s3_state(drc_report) [file join $reports routed_drc.rpt]
    set ::s3_state(result) ROUTE_COMPLETED_DIAGNOSTIC_ONLY_TIMING_NOT_SIGNED_OFF
    set ::s3_state(tcl_result) PASS:ROUTE_COMPLETE
    s3_stage_complete final_reports "" ""
    set ::s3_state(stage) COMPLETE
    s3_persist_status
    s3_write_utf8_secure [file join $reports final_summary.txt] [s3_status_text]
    s3_emit_tcl_result PASS:ROUTE_COMPLETE
    puts [s3_status_text]
    return 0
}

proc s3_run_selftest {} {
    set failures {}
    set checks 0
    set synthetic_xdc "set_property PACKAGE_PIN N18 \[get_ports TMDS_clk_p\]\nset_property IOSTANDARD TMDS_33 \[get_ports TMDS_clk_p\]\nset_property PACKAGE_PIN V16 \[get_ports hdmi_oen\]\nset_property IOSTANDARD LVCMOS33 \[get_ports hdmi_oen\]"
    set xdc_text $synthetic_xdc
    if {[catch {set ports [s3_audit_hdmi_xdc $xdc_text]} err]} {
        lappend failures "valid HDMI pin XDC rejected: $err"
    } elseif {[llength $ports] != 2} {
        lappend failures "HDMI port audit returned unexpected set: $ports"
    }
    incr checks
    if {![catch {s3_audit_hdmi_xdc "set_property IOSTANDARD LVCMOS33 \[get_ports camera_clk\]"}]} {
        lappend failures "camera signal was not rejected"
    }
    incr checks
    if {![catch {s3_audit_hdmi_xdc "set_property PACKAGE_PIN P1 \[get_ports CMOS2_D9\]"}]} {
        lappend failures "CMOS camera port was not rejected"
    }
    incr checks
    if {![catch {s3_audit_hdmi_xdc "set_output_delay -clock pix 1.0 \[get_ports TMDS_clk_p\]"}]} {
        lappend failures "output delay was not rejected"
    }
    incr checks
    if {![s3_output_is_repo_tmp_child {C:/repo} {C:/repo/tmp/fresh_run}]} {
        lappend failures "fresh absolute output under repository tmp was rejected"
    }
    incr checks
    set bad_clock_xdc "# Clock constraints ###\ncreate_generated_clock -source \[get_ports PixelClk\] -multiply_by 5 \[get_ports SerialClk\]\n"
    if {[catch {set clean_clock_xdc [s3_remove_bad_clock_relation $bad_clock_xdc]}] || [string first {create_generated_clock} $clean_clock_xdc] >= 0} {
        lappend failures "known bad generated clock relation was not removed"
    }
    incr checks
    if {![catch {s3_remove_bad_clock_relation "# empty\n"}]} {
        lappend failures "missing clock relation did not fail closed"
    }
    incr checks
    if {[s3_output_is_repo_tmp_child {C:/repo} {C:/repo/tmp/x/../outside}]} {
        lappend failures "path traversal was not rejected"
    }
    incr checks
    if {[s3_output_is_repo_tmp_child {C:/repo} {C:/repo/out-of-scope}]} {
        lappend failures "output outside repository tmp was not rejected"
    }
    incr checks
    if {[string first "/.codex/" [s3_normalized_key {C:\Users\22061\.codex\worktrees\repo\tmp\run01}]] < 0} {
        lappend failures "path key normalization changed the literal hidden-directory component"
    }
    incr checks
    set synthetic_project_root {C:/repo/tmp/s3_route/project}
    set synthetic_clock_xdc [s3_expected_generated_clock_xdc_path $synthetic_project_root]
    set expected_synthetic_clock_xdc {C:/repo/tmp/s3_route/project/s3_hdmi_only.gen/sources_1/bd/s3_hdmi_only/ip/s3_hdmi_only_rgb2dvi_0_0/src/rgb2dvi_clocks.xdc}
    set expected_synthetic_clock_xdc_windows {C:\repo\tmp\s3_route\project\s3_hdmi_only.gen\sources_1\bd\s3_hdmi_only\ip\s3_hdmi_only_rgb2dvi_0_0\src\rgb2dvi_clocks.xdc}
    if {[s3_normalized_key $synthetic_clock_xdc] ne [s3_normalized_key $expected_synthetic_clock_xdc] ||
        [s3_normalized_key $expected_synthetic_clock_xdc] ne [s3_normalized_key $expected_synthetic_clock_xdc_windows]} {
        lappend failures "generated-clock XDC helper did not return the exact single-layer IP-instance path: $synthetic_clock_xdc"
    }
    incr checks
    if {[llength [s3_expected_hdmi_ports]] != 11} {
        lappend failures "fixed official HDMI port set must contain eleven unique ports"
    }
    incr checks
    if {[catch {set checked_flow [s3_validate_synthesis_run_flow {Vivado Synthesis 2026} $::s3_synthesis_flow]} flow_error] ||
        $checked_flow ne $::s3_synthesis_flow} {
        lappend failures "Vivado 2026.1 synthesis run flow was not accepted: $flow_error"
    }
    incr checks
    if {![catch {s3_validate_synthesis_run_flow {Vivado Implementation 2026} $::s3_synthesis_flow} flow_mismatch_error] ||
        [string first "SYNTHESIS_RUN_FLOW_MISMATCH:" $flow_mismatch_error] != 0} {
        lappend failures "unexpected synthesis flow did not fail closed"
    }
    incr checks
    if {[catch {set complete_state [s3_validate_synthesis_completion synth_1 1 100%]} completion_error] ||
        $complete_state ne "COMPLETE"} {
        lappend failures "successful synthesis run completion was rejected: $completion_error"
    }
    incr checks
    foreach {run_name run_count progress expected_error} {
        synth_2 1 100% UNEXPECTED_SYNTHESIS_RUN_NAME:
        synth_1 0 100% EXPECTED_SINGLE_SYNTHESIS_RUN:
        synth_1 2 100% EXPECTED_SINGLE_SYNTHESIS_RUN:
        synth_1 1 0% SYNTHESIS_RUN_NOT_COMPLETE:
        synth_1 1 NOT_AVAILABLE SYNTHESIS_RUN_NOT_COMPLETE:
    } {
        if {![catch {s3_validate_synthesis_completion $run_name $run_count $progress} completion_error] ||
            [string first $expected_error $completion_error] != 0} {
            lappend failures "synthesis completion guard missed $expected_error for $run_name/$run_count/$progress"
        }
    }
    incr checks
    set had_synth_state [info exists ::s3_state(synth_state)]
    set had_synth_run_status [info exists ::s3_state(synth_run_status)]
    if {$had_synth_state} {set saved_synth_state $::s3_state(synth_state)}
    if {$had_synth_run_status} {set saved_synth_run_status $::s3_state(synth_run_status)}
    set ::s3_state(synth_state) RUNNING
    set ::s3_state(synth_run_status) RUNNING
    s3_mark_synthesis_failure
    if {$::s3_state(synth_state) ne "FAILED" || $::s3_state(synth_run_status) ne "FAILED"} {
        lappend failures "active synthesis run state did not become FAILED on the guarded error path"
    }
    if {$had_synth_state} {set ::s3_state(synth_state) $saved_synth_state} else {unset ::s3_state(synth_state)}
    if {$had_synth_run_status} {set ::s3_state(synth_run_status) $saved_synth_run_status} else {unset ::s3_state(synth_run_status)}
    incr checks
    set synthesis_body [info body s3_exec_main]
    set synthesis_contract_markers {
        {set_property USED_IN_SYNTHESIS true $local_xdc_obj}
        {if {[llength $synth_runs] > 1}}
        {if {[llength $synth_runs] == 0}}
        {create_run -constrset constrs_1 -part $::s3_expected_device -flow $::s3_synthesis_flow synth_1}
        {get_property FLOW $synth_run}
        {launch_runs -jobs 1 $synth_run}
        {wait_on_run $synth_run}
        {get_property PROGRESS [lindex $synth_runs 0]}
        {s3_validate_synthesis_completion synth_1 [llength $synth_runs] $synth_progress}
        {open_run -name s3_hdmi_only_synth [lindex $synth_runs 0]}
        {s3_validate_hdmi_ports_after_synth $expected_hdmi_ports}
        {set ::s3_state(blackboxes_after_synth) [s3_blackbox_names]}
        {s3_stage_complete synth "synth_state" [file join $checkpoints synth.dcp]}
        {opt_design}
        {place_design}
        {route_design}
    }
    set prior_contract_position -1
    foreach marker $synthesis_contract_markers {
        set contract_position [string first $marker $synthesis_body]
        if {$contract_position <= $prior_contract_position} {
            lappend failures "project-mode synthesis/implementation contract is missing or out of order: $marker"
            break
        }
        set prior_contract_position $contract_position
    }
    if {[regexp -nocase {(?m)^[ \t]*synth_design([ \t]|$)} $synthesis_body]} {
        lappend failures "direct synth_design call remains inside the project-mode run procedure"
    }
    incr checks
    set synthetic_tree_manifest [format "ROOT=C:/repo/tmp/out/vendor_ip_metadata\nFILE_COUNT=2\n%s  axi_dynclk_v1_0/component.xml\n%s  rgb2dvi_v1_3/component.xml\n" \
        [string repeat A 64] [string repeat B 64]]
    if {[catch {set synthetic_tree_count [s3_validate_tree_sha256_manifest $synthetic_tree_manifest {C:/repo/tmp/out/vendor_ip_metadata}]}] ||
        $synthetic_tree_count != 2} {
        lappend failures "valid runner metadata tree manifest was rejected"
    }
    incr checks
    set bad_tree_manifest [string map [list "FILE_COUNT=2" "FILE_COUNT=3"] $synthetic_tree_manifest]
    if {![catch {s3_validate_tree_sha256_manifest $bad_tree_manifest {C:/repo/tmp/out/vendor_ip_metadata}}]} {
        lappend failures "metadata tree manifest cardinality mismatch was accepted"
    }
    incr checks
    set synthetic_prepare_result "S3_TCL_RESULT=PASS:PREPARED\nRUN_ID=selftest\nMETADATA_COUNT=2\nMETADATA_TREE_SHA256=[string repeat C 64]\n"
    if {[catch {set prepared_pair [s3_validate_preparation_result $synthetic_prepare_result selftest [string repeat C 64]]}] ||
        [lindex $prepared_pair 0] != 2 || [lindex $prepared_pair 1] ne [string repeat C 64]} {
        lappend failures "valid prepare-time metadata digest was rejected"
    }
    incr checks
    if {![catch {s3_validate_preparation_result $synthetic_prepare_result selftest [string repeat D 64]}]} {
        lappend failures "prepare-time metadata digest mismatch was accepted"
    }
    incr checks
    set bad_prepare_result [string map [list "METADATA_TREE_SHA256=[string repeat C 64]" ""] $synthetic_prepare_result]
    if {![catch {s3_validate_preparation_result $bad_prepare_result selftest [string repeat C 64]}]} {
        lappend failures "missing prepare-time metadata digest was accepted"
    }
    incr checks
    if {[catch {set synthetic_digest_line [s3_prepare_metadata_digest_line selftest 1234 2 [string repeat C 64]]} emit_error] ||
        $synthetic_digest_line ne "S3_PREP_METADATA_DIGEST=selftest|1234|2|[string repeat C 64]"} {
        lappend failures "valid trusted prepare digest payload was rejected: $emit_error"
    }
    incr checks
    if {![catch {s3_prepare_metadata_digest_line selftest 0 2 [string repeat C 64]}]} {
        lappend failures "invalid trusted prepare digest process ID was accepted"
    }
    incr checks
    if {![catch {s3_prepare_metadata_digest_line selftest 1234 0 [string repeat C 64]}]} {
        lappend failures "invalid trusted prepare digest file count was accepted"
    }
    incr checks
    set bad_tree_manifest [string map [list "axi_dynclk_v1_0/component.xml" "../outside.xml"] $synthetic_tree_manifest]
    if {![catch {s3_validate_tree_sha256_manifest $bad_tree_manifest {C:/repo/tmp/out/vendor_ip_metadata}}]} {
        lappend failures "metadata tree manifest traversal path was accepted"
    }
    incr checks
    if {![catch {s3_validate_tree_sha256_manifest $synthetic_tree_manifest {C:/repo/tmp/other}}]} {
        lappend failures "metadata tree manifest root mismatch was accepted"
    }
    incr checks
    set saved_output_exists [info exists ::s3_state(output)]
    if {$saved_output_exists} {set saved_output $::s3_state(output)}
    set ::s3_state(output) {C:/repo/tmp/out}
    if {[s3_sha256_read_mode {C:/repo/tmp/out/inputs/hdmi_out.xdc}] ne "ReadWrite" ||
        [s3_sha256_read_mode {C:/repo/tmp/outside/inputs/hdmi_out.xdc}] ne "Read" ||
        [s3_sha256_read_mode {C:/repo/tmp/out/../outside/inputs/hdmi_out.xdc}] ne "Read" ||
        [s3_sha256_read_mode {relative/inputs/hdmi_out.xdc}] ne "Read"} {
        lappend failures "SHA256 shared-read mode escaped the absolute output subtree"
    }
    set ::s3_state(output) {relative/tmp/out}
    if {[s3_sha256_read_mode {C:/repo/tmp/out/inputs/hdmi_out.xdc}] ne "Read"} {
        lappend failures "relative output root enabled shared-write hash reads"
    }
    if {$saved_output_exists} {set ::s3_state(output) $saved_output} else {unset ::s3_state(output)}
    incr checks
    if {[catch {s3_load_existing_guard .; s3_extend_guard_api} guard_error guard_options]} {
        lappend failures "verified path-guard API extension failed: $guard_error [dict get $guard_options -errorinfo]"
    } else {
        set expected_guard_metadata_digest [string repeat C 64]
        set synthetic_guard_status "RESULT=PASS_PATH_GUARD_PREPARATION\nMETADATA_TREE_SHA256=$expected_guard_metadata_digest\n"
        if {[catch {set parsed_guard_status [s3_guard_status_dict $synthetic_guard_status]} guard_status_error] ||
            [dict get $parsed_guard_status RESULT] ne "PASS_PATH_GUARD_PREPARATION" ||
            [dict get $parsed_guard_status METADATA_TREE_SHA256] ne $expected_guard_metadata_digest} {
            lappend failures "secure guard status rejected numeric digest key or changed its value: $guard_status_error"
        }
        incr checks
        if {![catch {s3_guard_status_dict "RESULT=PASS\nBAD-KEY=value\n"} bad_key_error] ||
            [string first "INVALID_GUARD_STATUS_LINE:" $bad_key_error] != 0} {
            lappend failures "secure guard status accepted a key containing a disallowed character"
        }
        incr checks
        if {![catch {s3_guard_status_dict "RESULT=PASS\nRESULT=FAIL\n"} duplicate_key_error] ||
            $duplicate_key_error ne "DUPLICATE_GUARD_STATUS_KEY: RESULT"} {
            lappend failures "secure guard status did not reject duplicate keys"
        }
        incr checks
        if {![catch {s3_guard_status_dict "METADATA_TREE_SHA256=$expected_guard_metadata_digest\n"} missing_result_error] ||
            $missing_result_error ne "GUARD_STATUS_MISSING_RESULT"} {
            lappend failures "secure guard status did not require RESULT"
        }
        incr checks
        set extended_guard_body [info body s3_launch_secure_guardian]
        foreach required_snippet {{phase == "run"} {phase == "hdl_precreated"} {string runProjectPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "project"));} {string runMetadataPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "vendor_ip_metadata"));} {string runReportsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "reports"));} {string runCheckpointsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "checkpoints"));} {string runSentinelsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "sentinels"));} {string runInputsPath = AcquireSubtree(OutputFinal, Join(OutputFinal, "inputs"));} {MetadataTreeSha256(metadataPath, manifest)} {METADATA_TREE_SHA256=} {AcquireSubtree(OutputFinal, Join(OutputFinal, "project"))} {AcquireSubtree(OutputFinal, Join(OutputFinal, "vendor_ip_metadata"))} {CreateDirectoryChild(OutputFinal, "reports")} {CreateDirectoryChild(OutputFinal, "checkpoints")} {CreateDirectoryChild(OutputFinal, "sentinels")} {CreateDirectoryChild(OutputFinal, "inputs")} {AcquireSubtree(OutputFinal, Join(OutputFinal, "reports"))} {AcquireSubtree(OutputFinal, Join(OutputFinal, "checkpoints"))} {AcquireSubtree(OutputFinal, Join(OutputFinal, "sentinels"))} {AcquireSubtree(OutputFinal, Join(OutputFinal, "inputs"))}} {
            if {[string first $required_snippet $extended_guard_body] < 0} {
                lappend failures "secure guard extension missing required operation: $required_snippet"
            }
        }
    }
    incr checks
    set secure_test_dir [file join $::s3_repo_root tmp "s3_t03_tcl_selftest_[pid]_[clock clicks]"]
    if {[file exists $secure_test_dir]} {
        lappend failures "secure-write selftest output collision: $secure_test_dir"
    } else {
        file mkdir $secure_test_dir
        set ::s3_state(output) $secure_test_dir
        set ::s3_state(project) [file join $secure_test_dir project]
        set owner_text "S3_T03_TCL_SELFTEST_[pid]_[clock clicks]"
        set owner_path [file join $secure_test_dir .s3_t03_selftest_owner]
        if {[catch {s3_secure_write_bytes $owner_path [encoding convertto utf-8 $owner_text] CreateNew} owner_error]} {
            lappend failures "secure-write selftest owner marker creation failed: $owner_error"
        }
        set secure_test_file [file join $secure_test_dir secure_leaf.txt]
        if {[catch {s3_secure_write_bytes $secure_test_file [encoding convertto utf-8 first] CreateNew} secure_create_error]} {
            lappend failures "secure CREATE_NEW helper failed: $secure_create_error"
        } elseif {[catch {s3_secure_write_bytes $secure_test_file [encoding convertto utf-8 second] OpenExisting} secure_update_error]} {
            lappend failures "secure OPEN_EXISTING helper failed: $secure_update_error"
        } elseif {[s3_read_utf8_secure $secure_test_file] ne "second"} {
            lappend failures "secure helper update content mismatch: [binary encode hex [s3_read_binary $secure_test_file]]"
        }
        incr checks
        if {![catch {s3_secure_write_bytes $secure_test_file [encoding convertto utf-8 conflict] CreateNew}]} {
            lappend failures "secure CREATE_NEW did not reject an existing leaf"
        }
        incr checks
        set control_dir [file join $secure_test_dir reports]
        file mkdir $control_dir
        if {[catch {
            set secure_read_record [s3_secure_read_utf8 $secure_test_file $secure_test_dir]
            set hash_manifest [s3_sha256_manifest [list $secure_test_file]]
            if {[dict get $hash_manifest $secure_test_file] ne [dict get $secure_read_record sha256]} {
                error "SHA256_MANIFEST_DIFFERS_FROM_SECURE_READ"
            }
        } hash_manifest_error]} {
            lappend failures "SHA256 manifest could not read an existing secure output: $hash_manifest_error"
        }
        incr checks
        foreach leaf {generated_clock_xdc.lease_request generated_clock_xdc.lease_ack generated_clock_xdc.lease_error} {
            if {[catch {s3_secure_write_bytes [file join $control_dir $leaf] [encoding convertto utf-8 ""] CreateNew} control_create_error]} {
                lappend failures "lease control leaf secure reservation failed: $leaf; $control_create_error"
            }
        }
        if {[catch {
            set control_tree_hashes [s3_tree_sha256_manifest $control_dir]
            set secure_error_read [s3_secure_read_utf8 [file join $control_dir generated_clock_xdc.lease_error] $secure_test_dir]
            if {[dict size $control_tree_hashes] != 3 ||
                [dict get $control_tree_hashes generated_clock_xdc.lease_error] ne [dict get $secure_error_read sha256]} {
                error "TREE_SHA256_MANIFEST_DIFFERS_FROM_SECURE_READ"
            }
        } tree_hash_error]} {
            lappend failures "tree SHA256 manifest could not hash secure output leaves: $tree_hash_error"
        }
        incr checks
        set control_read_failures {}
        foreach leaf {generated_clock_xdc.lease_request generated_clock_xdc.lease_ack generated_clock_xdc.lease_error} {
            set control_path [file join $control_dir $leaf]
            if {[catch {set control_text [s3_read_utf8_secure $control_path]} control_read_error]} {
                lappend control_read_failures "$leaf: $control_read_error"
            } elseif {$control_text ne ""} {
                lappend control_read_failures "$leaf: reserved control leaf was not empty"
            }
        }
        if {[llength $control_read_failures] != 0} {
            lappend failures "lease control leaves could not be read before broker wait: [join $control_read_failures {; }]"
        }
        incr checks
        set timeout_path [s3_expected_generated_clock_xdc_path $::s3_state(project)]
        set timeout_caught [catch {s3_wait_for_generated_clock_xdc_lease $timeout_path [string repeat A 64] 30} timeout_error timeout_options]
        if {!$timeout_caught || [string first "GENERATED_CLOCK_XDC_BROKER_ACK_TIMEOUT" $timeout_error] < 0} {
            set timeout_error_info [expr {$timeout_caught && [dict exists $timeout_options -errorinfo] ? [dict get $timeout_options -errorinfo] : "NO_ERROR_INFO"}]
            lappend failures "generated-clock broker Tcl wait timeout did not fail closed: $timeout_error; ERROR_INFO=$timeout_error_info"
        }
        set timeout_error_text [s3_read_utf8_secure [file join $control_dir generated_clock_xdc.lease_error]]
        if {[string first "ERROR=TCL_WAIT_TIMEOUT" $timeout_error_text] < 0} {
            lappend failures "generated-clock broker Tcl timeout error channel missing marker: $timeout_error_text"
        }
        set lease_reset_failures {}
        foreach leaf {generated_clock_xdc.lease_request generated_clock_xdc.lease_ack generated_clock_xdc.lease_error} {
            set control_path [file join $control_dir $leaf]
            if {[catch {s3_secure_write_bytes $control_path [encoding convertto utf-8 ""] OpenExisting} reset_error]} {
                lappend lease_reset_failures "$leaf write: $reset_error"
            } elseif {[catch {set reset_text [s3_read_utf8_secure $control_path]} read_reset_error]} {
                lappend lease_reset_failures "$leaf read: $read_reset_error"
            } elseif {$reset_text ne ""} {
                lappend lease_reset_failures "$leaf remained nonempty after reset"
            }
        }
        if {[llength $lease_reset_failures] != 0} {
            lappend failures "generated-clock broker test controls could not be securely reset: [join $lease_reset_failures {; }]"
        }
        incr checks
        incr checks
        if {[file exists $secure_test_dir]} {
            set cleanup_helper [file join $::s3_repo_root scripts s3_tcl_selftest_cleanup.ps1]
            set cleanup_output ""
            if {![file isfile $cleanup_helper]} {
                lappend failures "secure-write selftest cleanup helper is missing: $cleanup_helper"
            } elseif {[catch {set cleanup_output [exec powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -OutputFormat Text -File $cleanup_helper -Root $secure_test_dir -Boundary [file join $::s3_repo_root tmp] -OwnerText $owner_text 2>@1]} cleanup_error]} {
                lappend failures "secure-write selftest directory cleanup failed: $cleanup_error; OUTPUT=$cleanup_output"
            } elseif {[string first "SELFTEST_TMP_CLEANUP=PASS" $cleanup_output] < 0} {
                lappend failures "secure-write selftest cleanup returned unexpected marker: $cleanup_output"
            }
            if {![regexp {(?m)^(SELFTEST_EXTERNAL_SENTINEL=UNCHANGED;SHA256=[A-Fa-f0-9]{64})$} $cleanup_output -> sentinel_line]} {
                lappend failures "secure-write selftest external sentinel regression missing: $cleanup_output"
            } else {
                puts $sentinel_line
            }
        }
        if {[file exists $secure_test_dir]} {lappend failures "secure-write selftest directory remains after cleanup: $secure_test_dir"}
    }
    incr checks
    if {[llength $failures] != 0} {
        puts stderr "SELFTEST=FAIL"
        foreach failure $failures {puts stderr "SELFTEST_FAILURE=$failure"}
        s3_emit_tcl_result FAIL:SELFTEST
        return 1
    }
    puts "SELFTEST=PASS"
    puts "SELFTEST_CHECKS=$checks"
    s3_emit_tcl_result PASS:SELFTEST
    return 0
}

if {$argc == 1 && [lindex $argv 0] eq "--selftest"} {
    set selftest_status [s3_run_selftest]
    exit $selftest_status
}
if {$argc == 5 && [lindex $argv 0] eq "--selftest-launch-same-image-sibling"} {
    set sibling_pipe_name [lindex $argv 1]
    set sibling_log [lindex $argv 2]
    set sibling_journal [lindex $argv 3]
    set sibling_script [lindex $argv 4]
    if {![regexp {^[A-Za-z0-9_]{1,80}$} $sibling_pipe_name]} {
        puts stderr "SELFTEST_SAME_IMAGE_SIBLING=FAIL:PIPE_NAME_INVALID"
        exit 2
    }
    set sibling_command [list [info nameofexecutable] -mode batch -log $sibling_log -journal $sibling_journal \
        -source $sibling_script -tclargs --selftest-digest-pipe $sibling_pipe_name]
    puts "SELFTEST_SAME_IMAGE_SIBLING_EXE=[info nameofexecutable]"
    puts "SELFTEST_SAME_IMAGE_SIBLING_COMMAND=$sibling_command"
    if {[catch {exec {*}$sibling_command} sibling_error]} {
        puts stderr "SELFTEST_SAME_IMAGE_SIBLING_RESULT=$sibling_error"
    } else {
        puts "SELFTEST_SAME_IMAGE_SIBLING_RESULT=EXITED_ZERO"
    }
    exit 0
}
if {$argc == 2 && [lindex $argv 0] eq "--selftest-digest-pipe"} {
    if {[catch {s3_emit_prepare_metadata_digest [lindex $argv 1] SELFTEST_DIGEST_PIPE 1 [string repeat C 64]} selftest_pipe_error]} {
        puts stderr "SELFTEST_DIGEST_PIPE=FAIL:$selftest_pipe_error"
        s3_emit_tcl_result FAIL:SELFTEST_DIGEST_PIPE
        exit 1
    }
    puts "SELFTEST_DIGEST_PIPE=PASS"
    s3_emit_tcl_result PASS:SELFTEST_DIGEST_PIPE
    exit 0
}
if {$argc < 3 || $argc > 6} {
    puts stderr "用法：vivado -mode batch -source scripts/s3_implement_hdmi_only_diag.tcl -tclargs <固定官方源码根目录> <tmp下唯一输出目录> prepare-only <run-id> <摘要管道名>；run阶段使用 <run-id> <metadata manifest SHA-256> <prepare metadata tree SHA-256>"
    puts stderr "纯Tcl自测：xtclsh s3_implement_hdmi_only_diag.tcl --selftest"
    s3_emit_tcl_result FAIL:ARGUMENTS
    exit 2
}
set s3_vendor_root [lindex $argv 0]
set s3_output_dir [lindex $argv 1]
set s3_action [lindex $argv 2]
set s3_run_id [expr {$argc >= 4 ? [lindex $argv 3] : "S3T03_[pid]_[clock clicks]"}]
set s3_expected_metadata_manifest_sha256 [expr {$s3_action eq "run" && $argc == 6 ? [lindex $argv 4] : ""}]
set s3_expected_metadata_tree_sha256 [expr {$s3_action eq "run" && $argc == 6 ? [lindex $argv 5] : ""}]
set s3_prepare_digest_pipe_name [expr {$s3_action eq "prepare-only" && $argc == 5 ? [lindex $argv 4] : ""}]
if {$s3_action ni {run prepare-only}} {
    puts stderr "INVALID_ACTION: $s3_action"
    s3_emit_tcl_result FAIL:ARGUMENTS
    exit 2
}
if {($s3_action eq "run" && $argc != 6) || ($s3_action eq "prepare-only" && $argc != 5)} {
    puts stderr "INVALID_METADATA_MANIFEST_ARGUMENT_COUNT"
    s3_emit_tcl_result FAIL:ARGUMENTS
    exit 2
}
if {![regexp {^[A-Za-z0-9_-]{1,80}$} $s3_run_id]} {
    puts stderr "INVALID_RUN_ID"
    s3_emit_tcl_result FAIL:ARGUMENTS
    exit 2
}
if {[catch {
    set ::s3_repo_root [s3_repo_root_from_vendor $s3_vendor_root]
    set ::s3_script_path [file join $::s3_repo_root scripts [file tail [info script]]]
    if {![file isfile $::s3_script_path]} {error "SCRIPT_PATH_NOT_FOUND_FROM_FIXED_VENDOR_ROOT"}
} s3_location_error]} {
    puts stderr "S3_LOCATION_PREFLIGHT_FAILED: $s3_location_error"
    s3_emit_tcl_result FAIL:LOCATION_PREFLIGHT
    exit 2
}
if {[catch {s3_exec_main $s3_vendor_root $s3_output_dir $s3_action $s3_run_id $s3_expected_metadata_manifest_sha256 $s3_expected_metadata_tree_sha256 $s3_prepare_digest_pipe_name} s3_error s3_error_options]} {
    puts stderr "S3_DIAGNOSTIC_FAILED: $s3_error"
    if {[dict exists $s3_error_options -errorinfo]} {puts stderr [dict get $s3_error_options -errorinfo]}
    if {[info exists ::s3_state(output)] && $::s3_state(output) ne "" && [file isdirectory $::s3_state(output)]} {
        s3_mark_synthesis_failure
        set ::s3_state(result) FAILED
        set ::s3_state(error) $s3_error
        set ::s3_state(tcl_result) FAIL:IMPLEMENTATION_ERROR
        set ::s3_state(stage) FAILED_AT_$::s3_state(stage)
        catch {s3_persist_status}
        catch {s3_write_sentinel [file join $::s3_state(output) sentinels failed.sentinel] "FAILED_LOCAL=[s3_timestamp]\nERROR=$s3_error\n"}
        catch {s3_write_utf8_secure [file join $::s3_state(output) failure_details.txt] [dict get $s3_error_options -errorinfo]}
        catch {s3_write_sentinel [file join $::s3_state(output) failure.result] "S3_TCL_RESULT=FAIL:IMPLEMENTATION_ERROR\nRUN_ID=$s3_run_id\n"}
    }
    s3_emit_tcl_result FAIL:IMPLEMENTATION_ERROR
    exit 2
}
exit 0
