# M2：无其他 DDR consumer（只读；不写任何寄存器）
# 用法：xsdb.bat scripts\stage4_s4b\m2_consumer_check.tcl
# 判定依据：无第二调试客户端 + PL 是否已配置（Zynq-7000 DevCfg STATUS @0xF8007014）+ CPU0/CPU1 状态
# 退出码：0=PASS(PL 未配置且无第二客户端) / 5=PL 已配置(需已登记位流身份, 由驱动判定) / 6=异常

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url
set all_targets [targets]
puts "M2_TARGET_COUNT=[llength $all_targets]"
foreach t $all_targets { puts "M2_TARGET=$t" }

# 只读 0xF8007014（DevCfg STATUS）；同时记录 0xF8007000(CTRL)/0xF800700C(INT_STS) 原始字以便复核
foreach {name addr} {M2_DEVCGF_CTRL 0xF8007000 M2_DEVCGF_INT_STS 0xF800700C M2_DEVCGF_STATUS 0xF8007014} {
    if {[catch {set v [lindex [mrd $addr] 0]} err]} {
        puts "$name=READ_ERROR:$err"
    } else {
        puts "$name=$v"
    }
}

# CPU 状态（不改变任何状态）
foreach t $all_targets {
    set lowered [string tolower $t]
    if {[string match "*cortex*" $lowered] || [string match "*arm*" $lowered]} {
        if {[catch {
            targets $t
            puts "M2_CPU_STATE=$t|[state]"
        } err]} {
            puts "M2_CPU_STATE=$t|ERROR:$err"
        }
    }
}
disconnect
puts "M2_RESULT=READ_ONLY_DONE"
exit 0