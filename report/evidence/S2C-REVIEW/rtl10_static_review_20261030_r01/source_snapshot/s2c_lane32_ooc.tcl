# S2C候选离线综合入口；只生成隔离的资源、时序与检查点，不连接硬件。
# 启动器须以全新隔离工作目录为cwd，并把-log/-journal写到该工作目录。
# 调用：vivado -mode batch -log 隔离日志 -journal 隔离日志 -source 本文件 -tclargs 精确仓库绝对路径 新报告目录绝对路径。
proc s2c_lane32_ooc_main {} {
    global argv
    if {[llength $argv] != 2} {error "需要仓库目录和全新输出目录两个参数"}
    lassign $argv repo_root output_dir
    # 加载复用函数前，逐组件验证仓库与平台脚本，不执行来自未核路径的Tcl。
    set bootstrap [file join $repo_root vivado/s2b_inference_platform.tcl]
    if {[file pathtype $repo_root] ne "absolute" ||
        [regexp {(^|[/\\])\.{1,2}([/\\]|$)} $repo_root] ||
        [regexp {[/\\]{2}} $repo_root]} {error "仓库路径不是精确绝对路径"}
    set parts [file split $bootstrap]
    set current [lindex $parts 0]
    set bootstrap_components [list $current]
    foreach component [lrange $parts 1 end] {
        if {![file isdirectory $current] ||
            [lsearch -exact [glob -nocomplain -directory $current -tails -- * .*] $component] < 0} {
            error "加载前精确路径核验失败:$bootstrap"
        }
        set current [file join $current $component]
        lappend bootstrap_components $current
        file lstat $current entry
        if {$entry(type) eq "link"} {error "加载前路径含链接:$current"}
    }
    if {![file isfile $bootstrap] || ![file isdirectory $repo_root]} {error "加载前目标类型错误"}
    if {$::tcl_platform(platform) eq "windows"} {
        # 尚未加载公共函数，用固定只读.NET查询补上Tcl无法可靠识别的junction检查。
        set encoded [binary encode base64 -maxlen 0 [encoding convertto utf-8 [join $bootstrap_components \n]]]
        set probe [string map [list @PATHS@ $encoded] {
            $ErrorActionPreference='Stop'
            $paths=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('@PATHS@')).Split([char]10)
            foreach($path in $paths) {
                if (([IO.File]::GetAttributes($path) -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw 'BOOTSTRAP_REPARSE_FAIL'
                }
            }
        }]
        exec powershell.exe -NoProfile -NonInteractive -Command $probe
    }
    source $bootstrap
    set checked_repo [::s2b_inference_platform::exact_existing $repo_root directory]
    set checked_output [::s2b_inference_platform::new_directory $output_dir]
    ::s2b_inference_platform::reject_reparse [concat $checked_repo $checked_output]
    foreach relative $::s2b_inference_platform::rtl_sources {
        ::s2b_inference_platform::exact_existing [file join $repo_root $relative] file
    }
    set_param general.maxThreads 2
    file mkdir $output_dir
    cd $output_dir
    create_project -in_memory -part xc7z020clg400-2
    foreach relative $::s2b_inference_platform::rtl_sources {
        read_verilog -sv [file join $repo_root $relative]
    }
    set constraints [file join $output_dir clock_100mhz.xdc]
    set handle [open $constraints {WRONLY CREAT EXCL}]
    fconfigure $handle -encoding utf-8
    puts $handle {create_clock -name s2c_clk -period 10.000 [get_ports clk]}
    close $handle
    read_xdc $constraints
    synth_design -top s2b_inference_top -part xc7z020clg400-2 -mode out_of_context \
        -generic CONV_OUTPUT_LANES=32 -generic ENABLE_BULK=1 -generic PROFILE_VISIBILITY_PROVEN=0
    if {[llength [get_clocks s2c_clk]] != 1 ||
        [get_property PERIOD [get_clocks s2c_clk]] != 10.0} {
        error "100MHz时钟约束未生效"
    }
    report_utilization -file [file join $output_dir utilization.rpt]
    report_utilization -hierarchical -file [file join $output_dir utilization_hierarchical.rpt]
    report_timing_summary -delay_type min_max -check_timing_verbose -report_unconstrained \
        -max_paths 10 -file [file join $output_dir timing_summary.rpt]
    report_methodology -file [file join $output_dir methodology.rpt]
    write_checkpoint [file join $output_dir lane32_bulk_post_synth.dcp]
    # 综合完成不代表时序合格，外部需分别解析WNS/TNS/WHS/THS及资源是否超限。
    puts "S2C_LANE32_OOC:COMPLETED_REPORTS_NOT_ACCEPTANCE"
    puts "LIMITATION:仅OOC时钟约束；接口输入输出延迟未给定，须报告未约束路径；无实现或板级结论"
}
if {[catch {s2c_lane32_ooc_main} message options]} {
    puts stderr "S2C_LANE32_OOC:FAIL $message"
    puts stderr [dict get $options -errorinfo]
    exit 1
}
exit 0
