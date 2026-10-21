# 阶段3安全转储的命令替身测试；不加载 XSDB，不连接板卡。
# 用法：tclsh test_dump_display_channels.tcl <工作树内已存在的临时目录>

set root [lindex $argv 0]
if {$root eq "" || ![file isdirectory $root]} { error "需要已有临时目录" }
set script [file join [file dirname [info script]] jtag_dump_display_channels.tcl]
set ::events {}
set ::mode ""

proc mock {command args} {
    lappend ::events $command
    if {$command eq "stop" && $::mode eq "halt_fail"} { error "模拟暂停失败" }
    if {$command eq "mrd" && $::mode eq "read_fail"} { error "模拟读取失败" }
    if {$command eq "con" && $::mode eq "resume_fail"} { error "模拟恢复失败" }
    if {$command eq "exit"} { return -code error -errorcode [list DUMP_EXIT [lindex $args 0]] "脚本结束" }
    return "0"
}

foreach mode {normal halt_fail read_fail resume_fail} {
    set out [file join $root $mode]
    if {[file exists $out]} { error "拒绝覆盖测试目录：$out" }
    file mkdir $out
    set ::events {}
    set ::mode $mode
    set child [interp create]
    foreach command {connect targets stop mrd con disconnect exit} {
        interp alias $child $command {} mock $command
    }
    interp alias $child after {} list
    interp alias $child puts {} list
    $child eval [list set argv [list $out]]
    catch {$child eval [list source $script]} result options
    interp delete $child
    set expected [expr {$mode eq "normal" ? 0 : 2}]
    if {![dict exists $options -errorcode] || [dict get $options -errorcode] ne [list DUMP_EXIT $expected]} {
        error "退出码不符：$mode $result $options"
    }
    set reads [llength [lsearch -all -exact $::events mrd]]
    set resumes [llength [lsearch -all -exact $::events con]]
    if {$mode eq "halt_fail" && ($reads != 0 || $resumes != 0)} { error "暂停失败后仍读内存或恢复" }
    if {$mode eq "normal" && $reads != 10} { error "正常路径未执行7寄存器及3行转储" }
    if {$mode ne "halt_fail" && $resumes != 1} { error "成功暂停后没有唯一恢复尝试" }
    if {[lindex $::events end-1] ne "disconnect"} { error "未断开连接" }
    puts "DUMP_MOCK_PASS=$mode reads=$reads resume_attempts=$resumes exit=$expected"
}
puts "DUMP_MOCK_ALL_PASS=4"
