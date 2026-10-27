# M2：无其他 DDR consumer（**只读**；不写任何寄存器）
# 用法：xsdb.bat <本文件>
# 判定依据（构造性证明，**不是**总线测量）：无第二调试客户端 + PL 是否已配置（DevCfg STATUS@0xF8007014）
#                                    + CPU0/CPU1 状态如实记录
# 退出码：0=只读完成（由驱动按阈值判定）；5=选目标/读取失败
# 修复（窗口1 后）：mrd 前**先选目标**；targets 按结构化元素解析。

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url

set sel ""
foreach filt {{name =~ "APU*"} {name =~ "*Cortex-A9*"} {name =~ "*#0*"}} {
    if {![catch {targets -set -filter $filt}]} { set sel $filt; break }
}
if {$sel eq ""} {
    puts "M2_SELECT=FAIL"
    disconnect
    exit 5
}
puts "M2_SELECT=OK filter=$sel"

set idx 0
foreach t [targets] {
    puts "M2_TARGET[$idx]=$t"
    incr idx
}

# 只读 DevCfg 寄存器（PL 配置状态由 STATUS 位判定，原始字一并记录以便复核）
set read_fail 0
foreach {name addr} {M2_DEVCGF_CTRL 0xF8007000 M2_DEVCGF_INT_STS 0xF800700C M2_DEVCGF_STATUS 0xF8007014} {
    if {[catch {set v [lindex [mrd $addr] 0]} err]} {
        puts "$name=READ_ERROR:$err"
        set read_fail 1
    } else {
        puts "$name=$v"
    }
}

# CPU 状态（只读）
set idx 0
foreach t [targets] {
    if {[string match "*Cortex-A9*" $t] || [string match "*#*" $t]} {
        set esc [string map {"\"" "\\\""} $t]
        if {![catch {targets -set -filter "name =~ \"$esc\""}]} {
            if {![catch {set s [state]}]} { puts "M2_CPU_STATE[$idx]=$t|$s" }
        }
        incr idx
    }
}

disconnect
if {$read_fail} {
    puts "M2_RESULT=READ_FAILED"
    exit 5
}
puts "M2_RESULT=READ_ONLY_DONE"
exit 0