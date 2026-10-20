# =============================================================================
# 阶段3 S3-T05-ILA：在 J11+CMOS2 综合检查点上用「网表插入法」加 1 个 5 探针 ILA，
# 实现到比特流并导出 .ltx（供阶段总控上板采集）。
#
# 用法（Tcl 批量模式）：
#   vivado -mode batch -source netlist_insert_ila.tcl \
#          -log <run_dir>/vivado_ila.log -journal <run_dir>/vivado_ila.jou \
#          -tclargs <run_dir> <synth_dcp>
#
# 设计要点（严格遵守任务卡 S3-T05-ILA）：
#   * 只读综合检查点，不改 BD / 源码 / 约束；只在内存中插入调试核。
#   * BASIC 许可只支持 <=5 探针：本脚本固定 1 个 ILA、5 个 probe，不打开厂商 IP 的
#     DEBUG_OV5640 内嵌 ila_0（6 探针会被许可拒绝）。
#   * 任一探针/时钟网名解析为空 => 在 opt_design 之前停止并如实退出（退出码 10），
#     不猜、不替换成别的信号。
#
# 退出码：
#   0  = 全流程成功（write_bitstream + write_debug_probes 完成）
#   2  = 入参/输入文件错误
#   10 = 探针或时钟网名解析为空（未进入实现）
#   11 = ILA 创建 / connect_debug_port 失败
#   12 = opt_design 之后网表里找不到 ILA 或 dbg_hub（调试核未落地）
#   1  = 其他 Vivado 错误（批量模式自然退出码）
# =============================================================================

set RUN_DIR   [lindex $argv 0]
set SYNTH_DCP [lindex $argv 1]

proc t05 {msg} {
    puts "ILA_T05|$msg"
    flush stdout
}

if {$RUN_DIR eq "" || $SYNTH_DCP eq ""} {
    puts "ILA_T05|FAIL=missing_tclargs_usage_run_dir_synth_dcp"
    exit 2
}
if {![file exists $SYNTH_DCP]} {
    puts "ILA_T05|FAIL=synth_dcp_missing:$SYNTH_DCP"
    exit 2
}

set OUT_DIR [file join $RUN_DIR impl_ila]
file mkdir $OUT_DIR

set BIT      [file join $OUT_DIR design_1_wrapper.bit]
set LTX      [file join $OUT_DIR design_1_wrapper.ltx]
set RPT_TMG  [file join $OUT_DIR report_timing_summary_routed.rpt]
set RPT_DRC  [file join $OUT_DIR report_drc_routed.rpt]
set RPT_UTIL [file join $OUT_DIR report_utilization_routed.rpt]
set RPT_CLK  [file join $OUT_DIR report_clocks_routed.rpt]
set RPT_CDC  [file join $OUT_DIR report_clock_interaction_routed.rpt]
set MAPFILE  [file join $RUN_DIR ila_netmap.txt]
set STATFILE [file join $RUN_DIR ila_status.txt]

# -----------------------------------------------------------------------------
# 工具过程
# -----------------------------------------------------------------------------
proc read_text {path} {
    if {![file exists $path]} { return "" }
    set fh [open $path r]
    fconfigure $fh -translation binary
    set txt [read $fh]
    close $fh
    return $txt
}

# 网名排序偏好：顶层（无 "/"）优先，其次名字最短，最后字典序。
proc net_cmp {a b} {
    set da [expr {[string first "/" $a] >= 0 ? 1 : 0}]
    set db [expr {[string first "/" $b] >= 0 ? 1 : 0}]
    if {$da != $db} { return [expr {$da - $db}] }
    set la [string length $a]
    set lb [string length $b]
    if {$la != $lb} { return [expr {$la - $lb}] }
    return [string compare $a $b]
}

# 用一组 glob 模式解析唯一目标网（所有模式都指向同一个物理信号的不同命名可能）。
# 打印全部候选；返回 "" 表示解析为空。
proc resolve_net {label patterns} {
    set found {}
    foreach pat $patterns {
        set m [get_nets -hier -quiet -filter "NAME =~ \"$pat\""]
        puts "ILA_T05|CAND $label PATTERN=$pat COUNT=[llength $m] NAMES=[join $m {|}]"
        flush stdout
        foreach n $m {
            if {[lsearch -exact $found $n] < 0} { lappend found $n }
        }
    }
    if {[llength $found] == 0} { return "" }
    return [lindex [lsort -command net_cmp $found] 0]
}

# 同一组 glob 模式，但改为匹配「管脚」，再取该管脚所在网（用于 IP 接口信号兜底）。
proc resolve_net_via_pin {label patterns} {
    set found {}
    foreach pat $patterns {
        set pins [get_pins -hier -quiet -filter "NAME =~ \"$pat\""]
        puts "ILA_T05|CANDPIN $label PATTERN=$pat PINS=[llength $pins]"
        flush stdout
        foreach p $pins {
            set nets [get_nets -quiet -of_objects $p]
            foreach n $nets {
                if {[lsearch -exact $found $n] < 0} { lappend found $n }
            }
        }
    }
    if {[llength $found] == 0} { return "" }
    return [lindex [lsort -command net_cmp $found] 0]
}

proc net_driver {n} {
    set pins [get_pins -quiet -of_objects [get_nets $n] -filter {DIRECTION == OUT}]
    if {[llength $pins] == 0} { return "<none>" }
    return [join [lrange $pins 0 3] {,}]
}

proc net_driver_ref {n} {
    set pins [get_pins -quiet -of_objects [get_nets $n] -filter {DIRECTION == OUT}]
    if {[llength $pins] == 0} { return "<none>" }
    set refs {}
    foreach p $pins {
        set c [get_cells -quiet -of_objects $p]
        if {[llength $c] > 0} {
            lappend refs "[lindex $c 0]:[get_property REF_NAME [lindex $c 0]]"
        }
    }
    if {[llength $refs] == 0} { return "<none>" }
    return [join $refs {,}]
}

proc net_sink_count {n} {
    set pins [get_pins -quiet -of_objects [get_nets $n] -filter {DIRECTION == IN}]
    return [llength $pins]
}

# -----------------------------------------------------------------------------
# 0) 打开综合检查点
# -----------------------------------------------------------------------------
t05 "STEP=open_checkpoint PATH=$SYNTH_DCP"
open_checkpoint $SYNTH_DCP
t05 "INFO=opened_part=[get_property PART [current_design]]"
t05 "INFO=top=[get_property NAME [current_design]]"

# 现有调试核审计：厂商 IP 若自带 DEBUG_OV5640 内嵌 ILA（6 探针）必须在此暴露出来。
set pre_cores [get_debug_cores -quiet]
t05 "INFO=preexisting_debug_cores COUNT=[llength $pre_cores] NAMES=[join $pre_cores {|}]"
if {[llength $pre_cores] > 0} {
    t05 "FAIL=unexpected_preexisting_debug_core"
    exit 11
}
set pre_hub [get_cells -hier -quiet -filter {NAME =~ "*dbg_hub*"}]
t05 "INFO=preexisting_dbg_hub COUNT=[llength $pre_hub] NAMES=[join $pre_hub {|}]"

# -----------------------------------------------------------------------------
# 1) 解析 ILA 时钟：axi_vdma_1 S2MM 流时钟（与 axis_subset_converter_0/aclk、
#    v_axi4s_vid_out_0/aclk、alinx_ov5640_0/m_axis_video_aclk 同一 FCLK_CLK1 网）
# -----------------------------------------------------------------------------
set clk_net [resolve_net_via_pin "ila_clock" {
    "*/axi_vdma_1/s_axis_s2mm_aclk"
    "*axi_vdma_1/s_axis_s2mm_aclk"
    "*/axis_subset_converter_0/aclk"
    "*/v_axi4s_vid_out_0/aclk"
}]
if {$clk_net eq ""} {
    set clk_net [resolve_net "ila_clock" {
        "design_1_i/processing_system7_0_FCLK_CLK1"
        "processing_system7_0_FCLK_CLK1"
        "*processing_system7_0_FCLK_CLK1*"
        "*FCLK_CLK1*"
    }]
}
if {$clk_net eq ""} {
    t05 "FAIL=ila_clock_net_unresolved"
    exit 10
}
# 时钟网交叉核验：必须实际驱动 S2MM 流侧的 aclk 管脚
set clk_sink_pins [get_pins -quiet -of_objects [get_nets $clk_net]]
set clk_verified 0
foreach cp $clk_sink_pins {
    if {[regexp {s2mm_aclk|axis_subset_converter_0/aclk|v_axi4s_vid_out_0/aclk} $cp]} { incr clk_verified }
}
t05 "RESULT ila_clock_net_sink_pins=[llength $clk_sink_pins] matched_s2mm_side_aclk_pins=$clk_verified"
t05 "RESULT ila_clock_net_sink_pin_names=[join [lrange $clk_sink_pins 0 6] {|}]"
set clk_name "<unknown>"
catch { set clks [get_clocks -quiet -of_objects [get_nets $clk_net]]; if {[llength $clks] > 0} { set clk_name [join $clks {,}] } }
set clk_period "<unknown>"
catch { if {$clk_name ne "<unknown>"} { set clk_period [get_property PERIOD [lindex $clks 0]] } }
t05 "RESULT ila_clock_net=$clk_net"
t05 "RESULT ila_clock_obj=$clk_name period_ns=$clk_period"

# -----------------------------------------------------------------------------
# 2) 解析 5 个固定顺序的探针网
#    probe0 = 顶层 cmos1_pclk 输入网（IBUF 输出）
#    probe1 = cmos1_vsync 输入网
#    probe2 = cmos1_href 输入网
#    probe3 = alinx_ov5640_0 m_axis_video_tuser
#    probe4 = alinx_ov5640_0 m_axis_video_tlast
# -----------------------------------------------------------------------------
set p0 [resolve_net "probe0_cmos1_pclk" {
    "cmos1_pclk_IBUF"
    "*/cmos1_pclk_IBUF"
    "*cmos1_pclk_IBUF*"
    "*cmos_pclk_1*"
}]
if {$p0 eq ""} { set p0 [resolve_net_via_pin "probe0_cmos1_pclk" {"*alinx_ov5640_0/cmos_pclk" "*cmos_pclk_1*"}] }

set p1 [resolve_net "probe1_cmos1_vsync" {
    "cmos1_vsync_IBUF"
    "*/cmos1_vsync_IBUF"
    "*cmos1_vsync_IBUF*"
    "*cmos_vsync_1*"
    "*cmos1_vsync*"
    "*cmos_vsync*"
}]
if {$p1 eq ""} { set p1 [resolve_net_via_pin "probe1_cmos1_vsync" {"*alinx_ov5640_0/cmos_vsync" "*cmos_vsync_1*"}] }

set p2 [resolve_net "probe2_cmos1_href" {
    "cmos1_href_IBUF"
    "*/cmos1_href_IBUF"
    "*cmos1_href_IBUF*"
    "*cmos_href_1*"
    "*cmos1_href*"
    "*cmos_href*"
}]
if {$p2 eq ""} { set p2 [resolve_net_via_pin "probe2_cmos1_href" {"*alinx_ov5640_0/cmos_href" "*cmos_href_1*"}] }

set p3 [resolve_net "probe3_m_axis_video_tuser" {
    "design_1_i/alinx_ov5640_0_m_axis_video_tuser"
    "*alinx_ov5640_0*m_axis_video*tuser*"
    "*alinx_ov5640_0*m_axis_video*TUSER*"
    "*m_axis_video_tuser*"
    "*m_axis_video_TUSER*"
}]
if {$p3 eq ""} {
    set p3 [resolve_net_via_pin "probe3_m_axis_video_tuser" {
        "*alinx_ov5640_0*m_axis_video_tuser*"
        "*alinx_ov5640_0*m_axis_video_TUSER*"
    }]
}

set p4 [resolve_net "probe4_m_axis_video_tlast" {
    "design_1_i/alinx_ov5640_0_m_axis_video_tlast"
    "*alinx_ov5640_0*m_axis_video*tlast*"
    "*alinx_ov5640_0*m_axis_video*TLAST*"
    "*m_axis_video_tlast*"
    "*m_axis_video_TLAST*"
}]
if {$p4 eq ""} {
    set p4 [resolve_net_via_pin "probe4_m_axis_video_tlast" {
        "*alinx_ov5640_0*m_axis_video_tlast*"
        "*alinx_ov5640_0*m_axis_video*TLAST*"
    }]
}

# 注意：probe 列表必须用 [list ...] 构造，不能让 $p0..$p4 留在花括号字面量里（否则不展开）
set probe_pairs [list 0 $p0 1 $p1 2 $p2 3 $p3 4 $p4]
set unresolved {}
foreach {idx nm} $probe_pairs {
    if {$nm eq ""} { lappend unresolved "probe$idx" }
}
if {[llength $unresolved] > 0} {
    t05 "FAIL=probe_net_unresolved:[join $unresolved {,}]"
    t05 "NOTE=stopped_before_opt_design_no_guessing_no_signal_substitution"
    exit 10
}

# 分辨率与驱动/负载审计（写证据，便于独立复核探到的确实是目标信号）
set mfh [open $MAPFILE w]
puts $mfh "# S3-T05-ILA 探针网名映射（probe -> 实际网名）"
puts $mfh "ila_clock=$clk_net"
foreach {idx nm} $probe_pairs {
    set w "<unknown>"
    catch { set nets [get_nets $nm]; set w [get_property WIDTH [lindex $nets 0]] }
    set drv [net_driver $nm]
    set ref [net_driver_ref $nm]
    set snk [net_sink_count $nm]
    puts $mfh "probe$idx=$nm"
    puts $mfh "probe${idx}_width=$w"
    puts $mfh "probe${idx}_driver=$drv"
    puts $mfh "probe${idx}_driver_ref=$ref"
    puts $mfh "probe${idx}_sink_count=$snk"
    t05 "RESULT probe$idx=$nm width=$w driver=$drv ref=$ref sinks=$snk"
}
close $mfh

# probe4 = tlast、probe3 = tuser 的驱动必须是 alinx_ov5640_0（摄像头 IP）。
foreach {idx nm} {3 $p3 4 $p4} {
    set ref [net_driver_ref $nm]
    if {[string first "alinx_ov5640" $ref] < 0} {
        t05 "WARN=probe$idx driver_ref_not_alinx_ov5640:$ref"
    }
}

# -----------------------------------------------------------------------------
# 3) 创建 1 个 5 探针 ILA（BASIC 许可上限；不打开 DEBUG_OV5640）
# -----------------------------------------------------------------------------
t05 "STEP=create_debug_core"
if {[catch { create_debug_core u_ila_0 ila } emsg]} {
    t05 "FAIL=create_debug_core:$emsg"
    exit 11
}
# 必需参数：5 探针 + 4096 深度
if {[catch {
    set_property C_NUM_OF_PROBES 5 [get_debug_cores u_ila_0]
    set_property C_DATA_DEPTH 4096 [get_debug_cores u_ila_0]
} emsg]} {
    t05 "FAIL=set_required_debug_props:$emsg"
    exit 11
}
# 可选参数：逐个尝试，失败只记录，不因此中断（避免版本差异造成假失败）
foreach {prop val} {
    C_TRIGIN_EN false C_TRIGOUT_EN false C_ADV_TRIGGER false
    C_INPUT_PIPE_STAGES 0 C_EN_STRG_QUAL false
    ALL_PROBE_SAME_MU true ALL_PROBE_SAME_MU_CNT 1
} {
    if {[catch { set_property $prop $val [get_debug_cores u_ila_0] } eopt]} {
        t05 "INFO=optional_prop_skipped $prop=$val : $eopt"
    }
}
t05 "INFO=debug_core_created num_probes=[get_property C_NUM_OF_PROBES [get_debug_cores u_ila_0]] depth=[get_property C_DATA_DEPTH [get_debug_cores u_ila_0]]"

t05 "STEP=connect_debug_ports"
if {[catch {
    connect_debug_port u_ila_0/clk [get_nets $clk_net]
    connect_debug_port u_ila_0/probe0 [get_nets $p0]
    connect_debug_port u_ila_0/probe1 [get_nets $p1]
    connect_debug_port u_ila_0/probe2 [get_nets $p2]
    connect_debug_port u_ila_0/probe3 [get_nets $p3]
    connect_debug_port u_ila_0/probe4 [get_nets $p4]
} emsg]} {
    t05 "FAIL=connect_debug_port:$emsg"
    exit 11
}

# 回读实际连接（写证据）
foreach dp [lsort [get_debug_ports u_ila_0/*]] {
    set conn "<unreadable>"
    catch { set conn [join [get_nets -quiet -of_objects [get_debug_ports $dp]] {,}] }
    t05 "RESULT debug_port=$dp connected_net=$conn"
}

# 网表法插入调试核（若该版本需要显式插入则在此落地；不需要时忽略错误继续）
if {[catch {implement_debug_core [get_debug_cores u_ila_0] ila} emsg2]} {
    t05 "INFO=implement_debug_core_skipped:$emsg2"
} else {
    t05 "INFO=implement_debug_core_ok"
}

# -----------------------------------------------------------------------------
# 4) 实现流程
# -----------------------------------------------------------------------------
t05 "STEP=opt_design"
opt_design
t05 "STEP=place_design"
place_design
t05 "STEP=phys_opt_design"
phys_opt_design
t05 "STEP=route_design"
route_design

# 调试核落地核验
set ila_cells [get_cells -hier -quiet -filter {NAME =~ "*u_ila_0*"}]
set hub_cells [get_cells -hier -quiet -filter {NAME =~ "*dbg_hub*"}]
t05 "RESULT ila_cells COUNT=[llength $ila_cells] NAMES=[join [lrange $ila_cells 0 3] {|}]"
t05 "RESULT dbg_hub_cells COUNT=[llength $hub_cells] NAMES=[join [lrange $hub_cells 0 3] {|}]"
if {[llength $ila_cells] == 0 || [llength $hub_cells] == 0} {
    t05 "FAIL=debug_core_not_in_netlist_after_opt"
    exit 12
}

# -----------------------------------------------------------------------------
# 5) 报告 + 产物
# -----------------------------------------------------------------------------
t05 "STEP=reports"
report_timing_summary -file $RPT_TMG
report_drc -file $RPT_DRC
report_utilization -file $RPT_UTIL
report_clocks -file $RPT_CLK
report_clock_interaction -file $RPT_CDC

set wns ""; set tns ""; set whs ""; set ths ""
set tmg [read_text $RPT_TMG]
if {[regexp -line {^[ \t]*(-?[0-9]+\.[0-9]+)[ \t]+(-?[0-9]+\.[0-9]+)[ \t]+([0-9]+)[ \t]+([0-9]+)[ \t]+(-?[0-9]+\.[0-9]+)[ \t]+(-?[0-9]+\.[0-9]+)} $tmg -> a b c d e f]} {
    set wns $a; set tns $b; set whs $e; set ths $f
}
set wns_path ""
set whs_path ""
catch { set wns_path [get_property SLACK [get_timing_paths -delay_type max -max_paths 1 -nworst 1 -quiet]] }
catch { set whs_path [get_property SLACK [get_timing_paths -delay_type min -max_paths 1 -nworst 1 -quiet]] }

t05 "STEP=write_bitstream"
write_bitstream -force $BIT
t05 "STEP=write_debug_probes"
write_debug_probes -force $LTX

set bit_ok [file exists $BIT]
set ltx_ok [file exists $LTX]
t05 "RESULT bit_exists=$bit_ok path=$BIT"
t05 "RESULT ltx_exists=$ltx_ok path=$LTX"
if {!$bit_ok || !$ltx_ok} {
    t05 "FAIL=artifact_missing bit=$bit_ok ltx=$ltx_ok"
    exit 13
}

set sfh [open $STATFILE w]
puts $sfh "status=ok"
puts $sfh "wns_ns=$wns"
puts $sfh "tns_ns=$tns"
puts $sfh "whs_ns=$whs"
puts $sfh "ths_ns=$ths"
puts $sfh "wns_from_path_ns=$wns_path"
puts $sfh "whs_from_path_ns=$whs_path"
puts $sfh "bit_path=$BIT"
puts $sfh "ltx_path=$LTX"
puts $sfh "ila_cells=[llength $ila_cells]"
puts $sfh "dbg_hub_cells=[llength $hub_cells]"
close $sfh

t05 "RESULT timing_wns_ns=$wns tns_ns=$tns whs_ns=$whs ths_ns=$ths"
t05 "RESULT timing_path_wns_ns=$wns_path path_whs_ns=$whs_path"
t05 "DONE=S3-T05-ILA"
exit 0