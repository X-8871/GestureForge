# M2：无其他 DDR consumer（**只读**；不写任何寄存器）
# 用法：xsdb.bat <本文件>
# 判定依据（构造性证明，**不是**总线测量）：无第二调试客户端 + PL 是否已配置（DevCfg STATUS）
#                                    + CPU0/CPU1 状态如实记录
# 退出码：0=只读完成（驱动按阈值判定）；5=选目标/读取失败
# 修订（窗口2 后）：寄存器读取改 `mrd -value`（返回 Tcl 列表，免文本解析）；选目标用 `*Cortex-A9*`。

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url

if {[catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}} err]} {
    puts "M2_SELECT=FAIL $err"
    disconnect
    exit 5
}
puts "M2_SELECT=OK"
set idx 0
foreach t [targets] { puts "M2_TARGET[$idx]=$t"; incr idx }

set read_fail 0
foreach {name addr} {M2_DEVCGF_CTRL 0xF8007000 M2_DEVCGF_INT_STS 0xF800700C M2_DEVCGF_STATUS 0xF8007014} {
    if {[catch {set words [mrd -value $addr]} err]} {
        puts "$name=READ_ERROR:$err"
        set read_fail 1
    } else {
        puts "$name=[lindex $words 0]"
    }
}

# CPU 状态（只读；逐个核过滤后读取 state）
set idx 0
foreach filt {{name =~ "*#0*"} {name =~ "*#1*"}} {
    if {![catch {targets -set -filter $filt}] && ![catch {set s [state]}]} {
        puts "M2_CPU_STATE[$idx]=$filt|$s"
    }
    incr idx
}

disconnect
if {$read_fail} {
    puts "M2_RESULT=READ_FAILED"
    exit 5
}
puts "M2_RESULT=READ_ONLY_DONE"
exit 0