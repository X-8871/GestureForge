set ::env(TEMP) {D:\codex-worktrees\w4\tmp\4\S4B-PL-PREPROC-NUMERIC-01\numeric_20261023_r04\process_tmp}
set ::env(TMP) $::env(TEMP)
set ::env(TMPDIR) $::env(TEMP)
cd [file dirname [info script]]

proc write_exit_code {path status options} {
    set code 0
    set error_code {}
    if {$status != 0} {
        if {[dict exists $options -errorcode]} {
            set error_code [dict get $options -errorcode]
        }
        if {[llength $error_code] >= 3 && [lindex $error_code 0] eq "CHILDSTATUS"} {
            set code [lindex $error_code 2]
        } else {
            set code -1
        }
    }
    set stream [open $path w]
    puts $stream $code
    close $stream
    return $code
}

set status [catch {
    exec xvlog -sv \
        {D:\codex-worktrees\w4\src\s4b_preproc_fp64.sv} \
        {D:\codex-worktrees\w4\src\s4b_preproc_pixel.sv} \
        {D:\codex-worktrees\w4\sim\tb_s4b_preproc_pixel.sv} \
        > xvlog_stdout.txt 2> xvlog_stderr.txt
} message options]
set code [write_exit_code xvlog_exit_code.txt $status $options]
puts "XVLOG_EXIT_CODE=$code"
if {$status != 0} { error "xvlog failed: $message" }

set status [catch {
    exec xelab work.tb_s4b_preproc_pixel -s tb_s4b_preproc_pixel \
        > xelab_stdout.txt 2> xelab_stderr.txt
} message options]
set code [write_exit_code xelab_exit_code.txt $status $options]
puts "XELAB_EXIT_CODE=$code"
if {$status != 0} { error "xelab failed: $message" }

set status [catch {
    exec xsim tb_s4b_preproc_pixel -R \
        > xsim_stdout.txt 2> xsim_stderr.txt
} message options]
set code [write_exit_code xsim_exit_code.txt $status $options]
puts "XSIM_EXIT_CODE=$code"
if {$status != 0} { error "xsim failed: $message" }

set stream [open xsim_complete.txt w]
puts $stream "XSIM_STAGES_PASS"
close $stream
puts "XSIM_STAGES_PASS"
