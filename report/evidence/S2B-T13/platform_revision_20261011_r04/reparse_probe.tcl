# 只读核验真实 junction 的 Windows reparse 属性补核，不执行任何 Vivado 命令。
source {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/vivado/s2b_inference_platform.tcl}
set base {C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/tmp/2B/S2B-T13/platform_revision_20261011_r04}
set bad_code [catch {::s2b_inference_platform::reject_reparse [list [file join $base junction_parent]]} bad_message]
set bad_ok [expr {$bad_code == 1 && [string match {*PATH_REPARSE_FAIL*} $bad_message]}]
puts "DIRECT_REPARSE_NEGATIVE PASS:$bad_ok CODE:$bad_code"
set good_code [catch {::s2b_inference_platform::reject_reparse [list [file join $base real_parent]]} good_message]
set good_ok [expr {$good_code == 0}]
puts "DIRECT_REPARSE_POSITIVE PASS:$good_ok CODE:$good_code"
exit [expr {$bad_ok && $good_ok ? 0 : 1}]
