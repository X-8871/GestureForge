# post_p3c_checks.tcl —— P3c 事后两项核验（一次 Vivado 调用完成）
#  A) BD 接口时钟域自证：打印关键 AXI 接口的 FREQ_HZ / CLK_DOMAIN
#     （证明 VDMA lite=50 / MM=100 / 流=74.21875、HP2=100、smc_vid=100）
#  B) 路由后补加异步时钟组并重算时序（XDC 里的组构建期因 12-4739 未生效）
set base "D:/tmp/lead/p3c_video_20261030_r01"
set out  "$base/out"
set fp [open "$out/post_checks.log" w]
proc P {fh msg} { puts $msg; puts $fh $msg; flush $fh }

# ---------------- A) BD 接口时钟域 ----------------
open_project "$out/proj/s4d_p3c_r01.xpr"
open_bd_design [get_files s4d_p3c.bd]
P $fp "==== A) BD 关键接口时钟域（FREQ_HZ / CLK_DOMAIN）===="
foreach ip {
    vdma_0/S_AXI_LITE
    smc_ctrl/M04_AXI
    vdma_0/M_AXI_MM2S
    smc_vid/S00_AXI
    smc_vid/M00_AXI
    ps7_0/S_AXI_HP2
    vdma_0/M_AXIS_MM2S
    vidout_0/video_in
    vtc_0/ctrl
    ps7_0/M_AXI_GP0
} {
    set pin [get_bd_intf_pins -quiet $ip]
    if {[llength $pin] == 0} { P $fp "  $ip : <not found>"; continue }
    set fq "<none>"; set cd "<none>"
    catch {set fq [get_property CONFIG.FREQ_HZ $pin]}
    catch {set cd [get_property CONFIG.CLK_DOMAIN $pin]}
    P $fp "  [format %-28s $ip] FREQ_HZ=$fq  CLK_DOMAIN=$cd"
}
# VDMA 的异步模式参数
foreach ipn {vdma_0} {
    foreach pn {CONFIG.c_prmry_is_aclk_async CONFIG.c_num_fstores CONFIG.c_m_axi_mm2s_data_width CONFIG.c_m_axis_mm2s_tdata_width} {
        set v "<none>"; catch {set v [get_property [string map {{CONFIG.} {CONFIG.}} $pn] [get_bd_cells $ipn]]}
        P $fp "  $ipn $pn = $v"
    }
}
close_bd_design

# ---------------- B) 路由后补加异步时钟组 ----------------
open_checkpoint "$out/proj/s4d_p3c_r01.runs/impl_1/top_p3c_routed.dcp"
P $fp "==== B) 路由后时钟组复算 ===="
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
report_clock_utilization -file "$out/clk_util_post_clkgrp.rpt"

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
close $fp
puts "==== POST_CHECKS P3C DONE ===="
exit 0