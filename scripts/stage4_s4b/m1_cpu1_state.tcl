# M1：CPU1 保持停止（**只读**；绝不 halt/resume/stop 任何目标）
# 用法：xsdb.bat <本文件>
# 退出码：0=CPU1 确定性 halted（两次采样 PC 不变）；3=未找到 CPU1；4=CPU1 非 halted/PC 推进；5=选目标或读取失败
# 修订（窗口2 后）：删除无效 `info target`；用 `*#1*` 定位 CPU1 核。

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url

# 先选 CPU0 核建立有效句柄（`APU*` 为集群，不可用于寄存器操作）
if {[catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}} err]} {
    puts "M1_SELECT=FAIL $err"
    disconnect
    exit 5
}
puts "M1_SELECT=OK"

# 定位 CPU1 核
set cpu1sel ""
foreach filt {{name =~ "*#1*"} {name =~ "*MPCore #1*"}} {
    if {![catch {targets -set -filter $filt}]} { set cpu1sel $filt; break }
}
if {$cpu1sel eq ""} {
    puts "M1_CPU1_TARGET=NOT_FOUND"
    disconnect
    exit 3
}
puts "M1_CPU1_SELECT=$cpu1sel"

# 两次采样（间隔 ≥2.5 s），判定 halted 且 PC 不推进
if {[catch {set st1 [state]; set pc1 [rrd pc]} err]} {
    puts "M1_READ=FAIL $err"
    disconnect
    exit 5
}
puts "M1_CPU1_STATE=$st1"
puts "M1_CPU1_PC_1=$pc1"
after 2500
if {[catch {set st2 [state]; set pc2 [rrd pc]} err]} {
    puts "M1_READ2=FAIL $err"
    disconnect
    exit 5
}
puts "M1_CPU1_STATE_2=$st2"
puts "M1_CPU1_PC_2=$pc2"
set stable [expr {$pc1 == $pc2}]
puts "M1_CPU1_PC_STABLE=[expr {$stable ? 1 : 0}]"
disconnect

set halted [expr {[string match -nocase "*halt*" $st1] || [string match -nocase "*stop*" $st1]}]
if {$halted && $stable} {
    puts "M1_RESULT=PASS"
    exit 0
}
if {!$halted} {
    puts "M1_RESULT=FAIL_NOT_HALTED state=$st1"
    exit 4
}
puts "M1_RESULT=FAIL_PC_MOVED pc1=$pc1 pc2=$pc2"
exit 4