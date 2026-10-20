# =============================================================================
# 阶段3 S3-T05-ILA「BD 内实例化 ILA」路线
#
# 背景：网表插入路线已被 BASIC 许可直接否决
#   ERROR: [Vivado 12-29205] 'create_debug_core' tcl command is not supported.
#       Your current selected license is BASIC.
# 故改为在 BD 里实例化 xilinx.com:ip:ila IP（不调用 create_debug_core）。
# BASIC 许可下 ILA IP 本身可 create_ip/generate_target（precheck 实测 RC=0）。
#
# 模式：
#   precheck <scratch_dir>
#       只探测 ILA IP 在当前许可下是否可实例化/生成（不建 RunId）。
#   bdaudit <scratch_dir> <vendor_dir>
#       只建 BD 并接 ILA，核对 AXI-Stream 接口成员网是否被 ILA 显式连接破坏；
#       不综合、不实现，用于在消耗 RunId 之前判定连法是否安全。
#   build <run_dir> <vendor_src> <xdc>
#       完整流程：BD + ILA -> wrapper -> synth -> impl -> bitstream -> ltx，
#       并在综合后按网表核验 TUSER/TLAST 网上同时存在三个端点
#       （摄像头 IP、axis_subset_converter_0、ila_cam）；缺一即 FAIL，不产位流。
#
# 约束：
#   * 厂商 IP 的 CONFIG.DEBUG_OV5640 必须保持 false（打开会内嵌 6 探针 ila_0）
#   * 只允许 1 个 ILA、5 个探针
#   * BD 对象先解析后连接；解析为空即停止并如实报告，不猜、不换成别的信号
#   * 不烧录、不连硬件、不提交 Git
#
# 退出码：
#   0  成功
#   2  入参/输入错误
#   11 ILA IP 创建失败（含许可拒绝）
#   12 BD/网表对象解析为空或连接被破坏
#   13 BD 校验/包装/综合/实现/产物未完成
#   20 precheck 判定 ILA IP 在当前许可下不可用
#   21 实现完成但网表内没有自动插入的 dbg_hub（ILA 无法经 JTAG 访问）
# =============================================================================

set MODE [lindex $argv 0]
if {$MODE eq ""} { puts "ILA_BD|FAIL=missing_mode"; exit 2 }

proc bdlog {msg} { puts "ILA_BD|$msg"; flush stdout }

proc ver_int {vlnv} {
    set v [lindex [split $vlnv ":"] end]
    set n 0
    foreach p [split $v "."] { set n [expr {$n * 100 + $p}] }
    return $n
}

proc read_text {path} {
    if {![file exists $path]} { return "" }
    set fh [open $path r]
    fconfigure $fh -translation binary
    set txt [read $fh]
    close $fh
    return $txt
}

# 在指定 BD 单元的所有管脚里按 glob 找唯一目标管脚；0 个或多个都视为解析失败（不猜）
proc bd_cell_pin_unique {cell pattern label} {
    set ps [get_bd_pins -quiet -of_objects [get_bd_cells $cell] -filter "NAME =~ \"*$pattern*\""]
    bdlog "CANDPIN $label CELL=$cell PAT=*$pattern* N=[llength $ps] NAMES=[join $ps {|}]"
    if {[llength $ps] != 1} { return "" }
    return [lindex $ps 0]
}

proc pins_label {objs} { return [join $objs {|}] }

proc has_sub {txt sub} { return [expr {[string first $sub $txt] >= 0}] }

# =============================================================================
# 共用：建工程 + BD + 关闭厂商 ILA + 实例化 ILA + 连时钟与 5 探针 + 连接核验
# 成功返回 1；任何解析/连接问题则打印 FAIL 并 exit（不猜、不替代信号）
# =============================================================================
proc build_bd_with_ila {vendor_dir proj_dir} {
    file mkdir $proj_dir
    create_project -force ov5640_single $proj_dir -part xc7z020clg400-2
    bdlog "PROJECT_PART=[get_property PART [current_project]]"

    set_property ip_repo_paths [file join $vendor_dir my_ip] [current_project]
    update_ip_catalog -quiet

    create_bd_design design_1
    create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
    source [file join $vendor_dir ps_config.tcl]
    set_ps_config processing_system7_0
    source [file join $vendor_dir pl_config.tcl]

    # 厂商 OV5640 IP 内嵌 ILA 必须关闭（DEBUG_OV5640=false）
    if {[llength [get_bd_cells -quiet alinx_ov5640_0]] == 0} { bdlog "FAIL=OV5640_CELL_NOT_FOUND"; exit 13 }
    set_property -dict [list CONFIG.DEBUG_OV5640 {false}] [get_bd_cells alinx_ov5640_0]
    bdlog "DEBUG_OV5640=[get_property CONFIG.DEBUG_OV5640 [get_bd_cells alinx_ov5640_0]]"

    # ---- ILA IP 实例化 ----
    set ila_defs {}
    foreach d [get_ipdefs -all -quiet {xilinx.com:ip:ila:*}] {
        if {[regexp {^xilinx\.com:ip:ila:[0-9.]+$} $d]} { lappend ila_defs $d }
    }
    bdlog "ILA_IPDEFS=[join $ila_defs {|}]"
    if {[llength $ila_defs] == 0} { bdlog "FAIL=ila_ipdef_not_found_in_catalog"; exit 11 }
    set ila_vlnv [lindex $ila_defs 0]
    foreach d $ila_defs { if {[ver_int $d] > [ver_int $ila_vlnv]} { set ila_vlnv $d } }
    bdlog "ILA_VLNV_SELECTED=$ila_vlnv"

    if {[catch { create_bd_cell -type ip -vlnv $ila_vlnv ila_cam } emsg]} {
        bdlog "FAIL=create_bd_cell_ila:$emsg"
        exit 11
    }
    if {[catch {
        set_property -dict [list \
            CONFIG.C_NUM_OF_PROBES {5} \
            CONFIG.C_DATA_DEPTH {4096} \
            CONFIG.C_EN_STRG_QUAL {1} \
        ] [get_bd_cells ila_cam]
    } emsg]} {
        bdlog "FAIL=set_ila_config:$emsg"
        exit 11
    }
    foreach {prop val} {
        CONFIG.C_ADV_TRIGGER {false} CONFIG.C_TRIGIN_EN {false} CONFIG.C_TRIGOUT_EN {false}
        CONFIG.C_INPUT_PIPE_STAGES {0}
    } {
        if {[catch { set_property $prop $val [get_bd_cells ila_cam] } eopt]} {
            bdlog "INFO=optional_ila_prop_skipped $prop=$val : $eopt"
        }
    }
    bdlog "ILA_NUM_PROBES=[get_property CONFIG.C_NUM_OF_PROBES [get_bd_cells ila_cam]] DEPTH=[get_property CONFIG.C_DATA_DEPTH [get_bd_cells ila_cam]]"

    # ---- ILA 时钟：与 axi_vdma_1/s_axis_s2mm_aclk 同一 FCLK ----
    set clk_pin [get_bd_pins -quiet axi_vdma_1/s_axis_s2mm_aclk]
    if {[llength $clk_pin] == 0} { bdlog "FAIL=bd_clk_pin_unresolved"; exit 12 }
    set clk_net [get_bd_nets -quiet -of_objects $clk_pin]
    bdlog "RESULT ila_clock_pin=$clk_pin"
    bdlog "RESULT ila_clock_net=$clk_net"
    if {[llength $clk_net] == 0} { bdlog "FAIL=bd_clk_net_unresolved"; exit 12 }
    if {[catch { connect_bd_net [get_bd_pins ila_cam/clk] $clk_pin } emsg]} {
        bdlog "FAIL=connect_ila_clk:$emsg"; exit 12
    }

    # ---- 5 个探针目标对象 ----
    set p0 [bd_cell_pin_unique alinx_ov5640_0 cmos_pclk        probe0_cmos1_pclk]
    set p1 [bd_cell_pin_unique alinx_ov5640_0 cmos_vsync       probe1_cmos1_vsync]
    set p2 [bd_cell_pin_unique alinx_ov5640_0 cmos_href        probe2_cmos1_href]
    set p3 [bd_cell_pin_unique alinx_ov5640_0 m_axis_video_tuser probe3_m_axis_video_tuser]
    set p4 [bd_cell_pin_unique alinx_ov5640_0 m_axis_video_tlast probe4_m_axis_video_tlast]

    set port0 [get_bd_ports -quiet cmos1_pclk]
    set port1 [get_bd_ports -quiet cmos1_vsync]
    set port2 [get_bd_ports -quiet cmos1_href]
    bdlog "RESULT bd_port_cmos1_pclk=$port0"
    bdlog "RESULT bd_port_cmos1_vsync=$port1"
    bdlog "RESULT bd_port_cmos1_href=$port2"

    set probe_pairs [list 0 $p0 1 $p1 2 $p2 3 $p3 4 $p4]
    set unresolved {}
    foreach {idx p} $probe_pairs { if {$p eq ""} { lappend unresolved "probe$idx" } }
    if {[llength $unresolved] > 0} {
        bdlog "FAIL=bd_probe_object_unresolved:[join $unresolved {,}]"
        bdlog "NOTE=stopped_before_connect_no_guessing_no_signal_substitution"
        exit 12
    }

    # ---- 解析 AXI-Stream 消费端成员管脚（TUSER/TLAST），必须唯一 ----
    set cons_tu [get_bd_pins -quiet -of_objects [get_bd_intf_pins axis_subset_converter_0/S_AXIS] -filter {NAME =~ "*s_axis_tuser*"}]
    set cons_tl [get_bd_pins -quiet -of_objects [get_bd_intf_pins axis_subset_converter_0/S_AXIS] -filter {NAME =~ "*s_axis_tlast*"}]
    bdlog "RESULT consumer_tuser_pins N=[llength $cons_tu] NAMES=[pins_label $cons_tu]"
    bdlog "RESULT consumer_tlast_pins N=[llength $cons_tl] NAMES=[pins_label $cons_tl]"
    if {[llength $cons_tu] != 1 || [llength $cons_tl] != 1} {
        bdlog "FAIL=consumer_tuser_or_tlast_member_pin_unresolved"
        exit 12
    }

    # ---- 连接 ----
    # probe0..2：摄像头 IP 的 DVP 输入管脚（与外部端口同一 BD 网）。
    # probe3/4：只覆盖生产者管脚会让接口消费端悬空，因此显式把
    #   「摄像头 IP 生产者 + ILA 探针 + axis_subset_converter_0 消费者」
    #   三点连到同一个标量网，电学上保证 TUSER/TLAST 仍然到达 VDMA 侧。
    foreach {idx p} [list 0 $p0 1 $p1 2 $p2] {
        if {[catch { connect_bd_net [get_bd_pins ila_cam/probe$idx] $p } emsg]} {
            bdlog "FAIL=connect_probe$idx:$emsg"; exit 12
        }
    }
    if {[catch { connect_bd_net [get_bd_pins ila_cam/probe3] $p3 $cons_tu } emsg]} {
        bdlog "FAIL=connect_probe3:$emsg"; exit 12
    }
    if {[catch { connect_bd_net [get_bd_pins ila_cam/probe4] $p4 $cons_tl } emsg]} {
        bdlog "FAIL=connect_probe4:$emsg"; exit 12
    }

    # ---- 连接后回读：每个探针所在 BD 网及其成员 ----
    set mfh [open [file join [file dirname $proj_dir] _ila_connect_audit.txt] w]
    puts $mfh "# S3-T05-ILA BD 路线：ILA 探针/时钟 -> BD 对象与 BD 网络映射"
    puts $mfh "ila_clock_pin=$clk_pin"
    puts $mfh "ila_clock_net=$clk_net"
    foreach {idx p} $probe_pairs {
        set n [get_bd_nets -quiet -of_objects [get_bd_pins ila_cam/probe$idx]]
        set objs [get_bd_pins -quiet -of_objects $n]
        set ports [get_bd_ports -quiet -of_objects $n]
        puts $mfh "probe${idx}_target_pin=$p"
        puts $mfh "probe${idx}_bd_net=$n"
        puts $mfh "probe${idx}_net_pins=[pins_label $objs]"
        puts $mfh "probe${idx}_net_ports=[pins_label $ports]"
        bdlog "RESULT probe$idx target_pin=$p bd_net=$n net_ports=[pins_label $ports] net_pins=[pins_label $objs]"
    }

    # ---- 核验 A：probe0..2 与外部端口同网 ----
    foreach {idx port_} [list 0 $port0 1 $port1 2 $port2] {
        set n [get_bd_nets -quiet -of_objects [get_bd_pins ila_cam/probe$idx]]
        set same [get_bd_ports -quiet -of_objects $n]
        if {[lsearch -exact $same $port_] < 0} {
            bdlog "FAIL=probe${idx}_not_on_same_bd_net_as_port:$port_"
            exit 12
        }
    }
    bdlog "INFO=probe0_2_share_bd_net_with_external_ports=1"

    # ---- 核验 B（关键）：TUSER/TLAST 标量网必须同时含三点
    #      摄像头 IP 生产者、axis_subset_converter_0 消费者、ila_cam 探针。
    #      任一缺失即说明 ILA 接入把 AXI-Stream 通路拆开，必须停止（不产位流）。
    foreach {sig idx} {tuser 3 tlast 4} {
        set n [get_bd_nets -quiet -of_objects [get_bd_pins ila_cam/probe$idx]]
        set objs [get_bd_pins -quiet -of_objects $n]
        set s [pins_label $objs]
        bdlog "RESULT ${sig}_net=$n pins=$s"
        if {[llength $n] == 0 || ![has_sub $s "alinx_ov5640_0"] \
            || ![has_sub $s "axis_subset_converter_0"] || ![has_sub $s "ila_cam"]} {
            bdlog "FAIL=${sig}_net_missing_endpoint_camera_or_converter_or_ila"
            exit 12
        }
        bdlog "INFO=${sig}_three_endpoints_on_one_bd_net=1"
    }
    close $mfh

    regenerate_bd_layout
    set bd_valid [validate_bd_design]
    bdlog "BD_VALIDATED=$bd_valid"
    save_bd_design
    return 1
}

# =============================================================================
# 模式：precheck
# =============================================================================
if {$MODE eq "precheck"} {
    bdlog "MODE=precheck"
    bdlog "VIVADO=[version -short]"
    if {[info exists ::env(XILINXD_LICENSE_FILE)]} {
        bdlog "LICENSE_ENV=$::env(XILINXD_LICENSE_FILE)"
    } else {
        bdlog "LICENSE_ENV=<unset>"
    }
    create_project -in_memory -part xc7z020clg400-2
    if {[catch { create_ip -name ila -vendor xilinx.com -library ip -module_name ila_precheck } emsg]} {
        bdlog "CREATE_IP_RC=1 MSG=$emsg"
        bdlog "PRECHECK_STATUS=blocked_at_create_ip"
        exit 20
    }
    bdlog "CREATE_IP_RC=0 MSG=$emsg"
    if {[catch { generate_target all [get_ips ila_precheck] } emsg2]} {
        bdlog "GENERATE_TARGET_RC=1 MSG=$emsg2"
        bdlog "PRECHECK_STATUS=blocked_at_generate_target"
        exit 20
    }
    bdlog "GENERATE_TARGET_RC=0 MSG=$emsg2"
    # 清理副作用：-in_memory 工程会把 IP 落到进程 CWD 的 .srcs/ 与 .gen/
    foreach side {".srcs" ".gen"} {
        if {[file isdirectory "$side/sources_1/ip/ila_precheck"]} {
            if {[llength [glob -nocomplain "$side/sources_1/ip/*"]] == 1} {
                file delete -force $side
                bdlog "PRECHECK_CLEANUP=removed_$side"
            } else {
                bdlog "PRECHECK_CLEANUP=left_${side}_shared"
            }
        }
    }
    bdlog "PRECHECK_STATUS=ok_ila_ip_usable"
    exit 0
}

# =============================================================================
# 模式：bdaudit（只建 BD 并核对连接，不综合、不实现）
# =============================================================================
if {$MODE eq "bdaudit"} {
    set SCRATCH    [lindex $argv 1]
    set VENDOR_DIR [lindex $argv 2]
    if {$SCRATCH eq "" || $VENDOR_DIR eq ""} { bdlog "FAIL=usage_bdaudit_scratch_vendor"; exit 2 }
    if {![file isdirectory $VENDOR_DIR]} { bdlog "FAIL=vendor_missing:$VENDOR_DIR"; exit 2 }
    bdlog "MODE=bdaudit"
    bdlog "SCRATCH=$SCRATCH"
    bdlog "VENDOR_DIR=$VENDOR_DIR"
    set SCRATCH [file join $SCRATCH proj]
    build_bd_with_ila $VENDOR_DIR $SCRATCH
    bdlog "AUDIT_STATUS=bd_connect_audit_passed"
    exit 0
}

if {$MODE ne "build"} { bdlog "FAIL=unknown_mode:$MODE"; exit 2 }

# =============================================================================
# 模式：build
# =============================================================================
set RUN_DIR  [lindex $argv 1]
set VENDOR   [lindex $argv 2]
set XDC_IN   [lindex $argv 3]
if {$RUN_DIR eq "" || $VENDOR eq "" || $XDC_IN eq ""} { bdlog "FAIL=usage_build_run_dir_vendor_src_xdc"; exit 2 }
if {![file isdirectory $VENDOR]} { bdlog "FAIL=vendor_src_missing:$VENDOR"; exit 2 }
if {![file exists $XDC_IN]} { bdlog "FAIL=xdc_missing:$XDC_IN"; exit 2 }

set ::proj_name "ov5640_single"
set ::bd_name "design_1"
set ::proj_dir [file join $RUN_DIR project]
set OUT_DIR [file join $RUN_DIR impl_ila]
file mkdir $OUT_DIR
set MAPFILE  [file join $RUN_DIR ila_bd_netmap.txt]
set STATFILE [file join $RUN_DIR ila_bd_status.txt]
set RPT_TMG  [file join $OUT_DIR report_timing_summary_routed.rpt]
set RPT_DRC  [file join $OUT_DIR report_drc_routed.rpt]
set RPT_UTIL [file join $OUT_DIR report_utilization_routed.rpt]
set RPT_CLK  [file join $OUT_DIR report_clocks_routed.rpt]

bdlog "MODE=build"
bdlog "RUN_DIR=$RUN_DIR"
bdlog "VENDOR_SRC=$VENDOR"
bdlog "VIVADO=[version -short]"

build_bd_with_ila $VENDOR $::proj_dir

# bdaudit 版审计文件（写在 project 同级目录）搬到 RunId 根，便于证据留存
set pre_audit [file join $RUN_DIR _ila_connect_audit.txt]
if {[file exists $pre_audit]} { file copy -force $pre_audit $MAPFILE }

# ---- wrapper + 约束 ----
set bd_file [get_files ${::bd_name}.bd]
make_wrapper -files $bd_file -top
set wrapper_files [glob -nocomplain [file join $::proj_dir ${::proj_name}.gen sources_1 bd ${::bd_name} hdl *.v]]
if {[llength $wrapper_files] == 0} { bdlog "FAIL=WRAPPER_NOT_FOUND"; exit 13 }
add_files -norecurse $wrapper_files
set ::wrapper_name "${::bd_name}_wrapper"
set_property top $::wrapper_name [current_fileset]
update_compile_order -fileset sources_1
bdlog "TOP=[get_property top [current_fileset]]"

add_files -fileset constrs_1 -norecurse $XDC_IN
bdlog "XDC_ADDED=[llength [get_files -of [get_filesets constrs_1]]]"

# ---- 综合 ----
bdlog "STEP=synth"
launch_runs synth_1 -jobs 3
if {[catch {wait_on_run synth_1} we]} { bdlog "SYNTH_WAIT_WARN=$we" }
set synth_status [get_property STATUS [get_runs synth_1]]
set synth_progress [get_property PROGRESS [get_runs synth_1]]
bdlog "SYNTH_STATUS=$synth_status"
bdlog "SYNTH_PROGRESS=$synth_progress"
for {set attempt 1} {$attempt <= 2} {incr attempt} {
    if {[string match "*Complete*" $synth_status] && $synth_progress eq "100%"} { break }
    set failed [get_runs -quiet -filter {PROGRESS != "100%"}]
    bdlog "SYNTH_RETRY_${attempt}_FAILED_RUNS=[llength $failed]"
    if {[llength $failed] == 0} { break }
    reset_run $failed
    launch_runs synth_1 -jobs 3
    if {[catch {wait_on_run synth_1} we2]} { bdlog "SYNTH_RETRY_WAIT_WARN=$we2" }
    set synth_status [get_property STATUS [get_runs synth_1]]
    set synth_progress [get_property PROGRESS [get_runs synth_1]]
    bdlog "SYNTH_RETRY_${attempt}_STATUS=$synth_status"
}
if {![string match "*Complete*" $synth_status] || $synth_progress ne "100%"} {
    bdlog "FAIL=SYNTH_NOT_COMPLETE:$synth_status:$synth_progress"
    exit 13
}

# ---- 综合后权威核验：TUSER/TLAST 网上必须同时有摄像头 IP、subset converter、ila_cam ----
open_run synth_1 -name synth_1
bdlog "SYNTH_ILA_CELLS=[llength [get_cells -hier -quiet -filter {NAME =~ \"*ila_cam*\"}]]"
report_utilization -file [file join $OUT_DIR report_utilization_synth.rpt]

foreach {sig pat_up pat_lo} {tuser m_axis_video_TUSER m_axis_video_tuser
                             tlast m_axis_video_TLAST m_axis_video_tlast} {
    set nets [lsort -unique [concat \
        [get_nets -hier -quiet -filter "NAME =~ \"*$pat_up*\""] \
        [get_nets -hier -quiet -filter "NAME =~ \"*$pat_lo*\""]]]
    bdlog "RESULT synth_${sig}_nets N=[llength $nets] NAMES=[pins_label $nets]"
    set found 0
    foreach n $nets {
        set ps [get_pins -quiet -of_objects [get_nets $n]]
        set s [pins_label $ps]
        if {[has_sub $s "alinx_ov5640_0"] && [has_sub $s "axis_subset_converter_0"] && [has_sub $s "ila_cam"]} {
            set found 1
            bdlog "RESULT synth_${sig}_verified_net=$n pins=$s"
        }
    }
    if {!$found} {
        bdlog "FAIL=synth_${sig}_net_missing_endpoint_camera_or_converter_or_ila"
        foreach n $nets {
            bdlog "DETAIL synth_${sig}_net=$n pins=[pins_label [get_pins -quiet -of_objects [get_nets $n]]]"
        }
        exit 12
    }
}
close_design

# ---- 实现 ----
bdlog "STEP=impl"
launch_runs impl_1 -to_step write_bitstream -jobs 3
if {[catch {wait_on_run impl_1} we3]} { bdlog "IMPL_WAIT_WARN=$we3" }
set impl_status [get_property STATUS [get_runs impl_1]]
set impl_progress [get_property PROGRESS [get_runs impl_1]]
bdlog "IMPL_STATUS=$impl_status"
bdlog "IMPL_PROGRESS=$impl_progress"
if {![string match "*Complete*" $impl_status] || $impl_progress ne "100%"} {
    bdlog "FAIL=IMPL_NOT_COMPLETE:$impl_status:$impl_progress"
    exit 13
}

open_run impl_1
set ila_cells [get_cells -hier -quiet -filter {NAME =~ "*ila_cam*"}]
set hub_cells [get_cells -hier -quiet -filter {NAME =~ "*dbg_hub*"}]
bdlog "RESULT impl_ila_cells COUNT=[llength $ila_cells] NAMES=[pins_label [lrange $ila_cells 0 3]]"
bdlog "RESULT impl_dbg_hub_cells COUNT=[llength $hub_cells] NAMES=[pins_label [lrange $hub_cells 0 3]]"

report_timing_summary -delay_type min_max -report_unconstrained -check_timing_verbose -max_paths 10 -file $RPT_TMG
report_drc -file $RPT_DRC
report_utilization -file $RPT_UTIL
report_clocks -file $RPT_CLK
bdlog "TIMING_WNS=[get_property STATS.WNS [get_runs impl_1]]"
bdlog "TIMING_TNS=[get_property STATS.TNS [get_runs impl_1]]"
bdlog "TIMING_WHS=[get_property STATS.WHS [get_runs impl_1]]"
bdlog "TIMING_THS=[get_property STATS.THS [get_runs impl_1]]"

set bit_src [file join $::proj_dir ${::proj_name}.runs impl_1 ${::bd_name}_wrapper.bit]
set ltx_run [file join $::proj_dir ${::proj_name}.runs impl_1 ${::bd_name}_wrapper.ltx]
bdlog "BIT_IN_RUN=$bit_src EXISTS=[file exists $bit_src]"
bdlog "LTX_IN_RUN=$ltx_run EXISTS=[file exists $ltx_run]"

set ltx_out [file join $OUT_DIR design_1_wrapper.ltx]
set bit_out [file join $OUT_DIR design_1_wrapper.bit]
if {[catch { write_debug_probes -force $ltx_out } eltx]} {
    bdlog "WARN=write_debug_probes:$eltx"
    if {[file exists $ltx_run]} { file copy -force $ltx_run $ltx_out }
}
if {[file exists $bit_src]} { file copy -force $bit_src $bit_out }

set wns ""; set tns ""; set whs ""; set ths ""
set tmg [read_text $RPT_TMG]
if {[regexp -line {^[ \t]*(-?[0-9]+\.[0-9]+)[ \t]+(-?[0-9]+\.[0-9]+)[ \t]+([0-9]+)[ \t]+([0-9]+)[ \t]+(-?[0-9]+\.[0-9]+)[ \t]+(-?[0-9]+\.[0-9]+)} $tmg -> a b c d e f]} {
    set wns $a; set tns $b; set whs $e; set ths $f
}

set sfh [open $STATFILE w]
puts $sfh "wns_ns=$wns"
puts $sfh "tns_ns=$tns"
puts $sfh "whs_ns=$whs"
puts $sfh "ths_ns=$ths"
puts $sfh "impl_ila_cells=[llength $ila_cells]"
puts $sfh "impl_dbg_hub_cells=[llength $hub_cells]"
puts $sfh "bit_run_path=$bit_src"
puts $sfh "ltx_run_path=$ltx_run"
puts $sfh "bit_out_path=$bit_out"
puts $sfh "ltx_out_path=$ltx_out"
puts $sfh "bit_exists=[file exists $bit_out]"
puts $sfh "ltx_exists=[file exists $ltx_out]"
close $sfh

bdlog "RESULT timing_wns_ns=$wns tns_ns=$tns whs_ns=$whs ths_ns=$ths"
bdlog "RESULT bit_out_exists=[file exists $bit_out] ltx_out_exists=[file exists $ltx_out]"
if {![file exists $bit_out] || ![file exists $ltx_out]} {
    bdlog "FAIL=artifact_missing bit=[file exists $bit_out] ltx=[file exists $ltx_out]"
    exit 13
}
if {[llength $hub_cells] == 0} {
    bdlog "FAIL=dbg_hub_missing_ila_not_accessible_over_jtag"
    exit 21
}
bdlog "DONE=S3-T05-ILA-BD"
exit 0