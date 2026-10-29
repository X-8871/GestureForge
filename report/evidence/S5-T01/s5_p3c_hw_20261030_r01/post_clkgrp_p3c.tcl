# post_clkgrp_p3c.tcl —— P3c：在已路由 DCP 上补加"异步时钟组"并重算时序
#
# 背景：构建时 XDC 里的 set_clock_groups 会因"用户 XDC 早于 IP/BD 时钟约束被读取"
# 而取到空集合（Vivado 12-4739）；P3b 已实测 PROCESSING_ORDER {LATE} 也修不好。
# 本脚本在路由后（设计已 link、时钟齐全）施加同样的分组，给出修正后的时序数字。
# 仅做分析，不改动已发布的位流。
set base "D:/tmp/lead/p3c_video_20261030_r01"
set out  "$base/out"
set fp [open "$out/post_clkgrp.log" w]
proc P {fh msg} { puts $msg; puts $fh $msg; flush $fh }

open_checkpoint "$out/proj/s4d_p3c_r01.runs/impl_1/top_p3c_routed.dcp"
P $fp "design=[get_property NAME [current_design]]"

set g0 [get_clocks -quiet -include_generated_clocks clk_fpga_0]
set g1 [get_clocks -quiet -include_generated_clocks clk_fpga_1]
set gp [get_clocks -quiet -include_generated_clocks clk_out*_s4d_p3c_clk_wiz_0_0]
P $fp "P3C_POST_CLOCKS: g0={$g0} | g1={$g1} | gp={$gp}"

set args {}
foreach g [list $g0 $g1 $gp] {
    if {[llength $g] > 0} { lappend args -group $g }
}
if {[llength $args] >= 4} {
    if {[catch {eval set_clock_groups -asynchronous $args} e]} {
        P $fp "P3C_POST_CLKGRP=FAILED_APPLY: $e"
    } else {
        P $fp "P3C_POST_CLKGRP=APPLIED"
    }
} else {
    P $fp "P3C_POST_CLKGRP=FAILED (组数不足: [llength $args])"
}

update_timing -full
report_clocks            -file "$out/clocks_post_clkgrp.rpt"
report_timing_summary    -delay_type min_max -max_paths 10 -file "$out/timing_post_clkgrp.rpt"
report_clock_interaction -delay_type min_max -file "$out/clk_interaction_post_clkgrp.rpt"

set wns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1 -nworst 1]]
set whs [get_property SLACK [get_timing_paths -delay_type min -max_paths 1 -nworst 1]]
P $fp "P3C_POST_WNS=$wns"
P $fp "P3C_POST_WHS=$whs"

set tfh [open "$out/timing_post_clkgrp.rpt" r]
set tlines [split [read $tfh] "\n"]
close $tfh
for {set i 0} {$i < [llength $tlines]} {incr i} {
    if {[string match "*WNS(ns)*" [lindex $tlines $i]]} {
        P $fp "P3C_POST_TS_VAL: [string trim [lindex $tlines [expr {$i+2}]]]"
        break
    }
}

# 时钟域归属实证：列出每个时钟的负载数，证明 100 MHz 域确实承载了 VDMA/HP2
catch {report_clock_utilization -file "$out/clk_util_post_clkgrp.rpt"}
close $fp
puts "==== POST_CLKGRP P3C DONE ===="
exit 0