# 只检查器件和厂商例程所需 IP；不执行厂商脚本、综合、实现或实物操作。
proc s3_probe {vendor_root} {
    if {[file pathtype $vendor_root] ne "absolute" || ![file isdirectory $vendor_root]} {
        error "厂商仓库必须是存在的绝对目录"
    }
    set source_root [file join $vendor_root course_s2_vitis 22_ov5640_single Vivado auto_create_project]
    set templates {}
    foreach name {create_project.tcl pl_config.tcl} {
        set path [file join $source_root $name]
        if {![file isfile $path]} {error "缺少模板：$path"}
        set channel [open $path r]
        fconfigure $channel -encoding utf-8
        lappend templates [read $channel]
        close $channel
    }
    set ip_root [file join $source_root my_ip]
    if {![file isdirectory $ip_root]} {error "缺少厂商 IP 目录"}
    puts "VIVADO=[version -short]"
    set parts [get_parts -quiet xa7z020clg400-1*]
    set selected {}
    foreach part $parts {
        if {[string equal -nocase $part xa7z020clg400-1I]} {lappend selected $part}
    }
    puts "PART_CANDIDATES=$parts"
    if {[llength $selected] != 1} {error "未找到唯一 XA7Z020/CLG400/-1I；禁止回退 XC 或 -2"}
    set part [lindex $selected 0]
    puts "EXACT_PART=$part"
    create_project -in_memory s3_catalog_probe -part $part
    set_property ip_repo_paths [list $ip_root] [current_project]
    update_ip_catalog
    set required {}
    foreach template $templates {
        foreach line [split $template \n] {
            if {[regexp {^\s*#} $line]} {continue}
            if {[regexp {create_bd_cell\s+-type\s+ip\s+-vlnv\s+([A-Za-z0-9_.:-]+)} $line -> vlnv]} {
                lappend required $vlnv
            }
        }
    }
    set required [lsort -unique $required]
    if {[llength $required] == 0} {error "模板未识别到 IP 依赖，不能判为通过"}
    puts "REQUIRED_COUNT=[llength $required]"
    set missing {}
    foreach vlnv $required {
        if {[llength [get_ipdefs -all -quiet $vlnv]] == 0} {
            lappend missing $vlnv
            puts "MISSING=$vlnv"
            set family [join [lrange [split $vlnv :] 0 2] :]
            puts "ALTERNATIVES_ONLY=[get_ipdefs -all -quiet ${family}:*]"
        } else {
            puts "FOUND=$vlnv"
        }
    }
    close_project
    if {[llength $missing] != 0} {error "缺少 [llength $missing] 项精确版本 IP；需要迁移，不能直接执行原模板"}
    return PASS_TOOL_CATALOG_ONLY
}

# 报告必须是新文件；保护既有证据，失败也写出终态。
if {$argc != 2} {puts stderr "用法：-tclargs 厂商仓库绝对目录 新报告绝对路径"; exit 2}
set vendor_root [lindex $argv 0]
set report_path [lindex $argv 1]
if {[file pathtype $report_path] ne "absolute" || ![file isdirectory [file dirname $report_path]] || [file exists $report_path]} {
    puts stderr "报告父目录必须存在且目标文件不得存在"
    exit 2
}
set failed [catch {s3_probe $vendor_root} result]
set report [open $report_path {WRONLY CREAT EXCL}]
fconfigure $report -encoding utf-8 -translation lf
puts $report "VIVADO=[version -short]"
puts $report "VENDOR_ROOT=$vendor_root"
puts $report "FAILED=$failed"
puts $report "RESULT=$result"
puts $report "SCOPE=CATALOG_ONLY_NO_BD_NO_SYNTHESIS_NO_HARDWARE"
close $report
puts "RESULT=$result"
if {$failed} {exit 2}
exit 0
