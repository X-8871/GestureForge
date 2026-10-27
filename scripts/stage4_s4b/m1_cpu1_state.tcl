# M1：CPU1 保持停止（**只读**；本脚本绝不 halt/resume/stop 任何目标）
# 用法：xsdb.bat <本文件>
# 退出码：0=CPU1 确定性 halted（两次采样 PC 不变）；3=未找到 CPU1；4=CPU1 非 halted/PC 推进；5=选目标或读取失败
# 修复（窗口1 后）：所有读取前**先选目标**；targets 按结构化元素解析，不按行切分。

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url

# 步骤 A：选 APU 复合目标，保证后续 rrd/rrd pc 有有效句柄
set sel ""
foreach filt {{name =~ "APU*"} {name =~ "*Cortex-A9*"} {name =~ "*#0*"}} {
    if {![catch {targets -set -filter $filt}]} { set sel $filt; break }
}
if {$sel eq ""} {
    puts "M1_SELECT=FAIL"
    disconnect
    exit 5
}
puts "M1_SELECT=OK filter=$sel"
puts "M1_APU_INFO=[info target]"

# 步骤 B：定位 CPU1（先按 #1 过滤；失败则遍历 targets 元素）
set cpu1sel ""
if {![catch {targets -set -filter {name =~ "*#1*"}}]} {
    set cpu1sel {name =~ "*#1*"}
} else {
    foreach t [targets] {
        if {[string match "*#1*" $t]} {
            set esc [string map {"\"" "\\\""} $t]
            if {![catch {targets -set -filter "name =~ \"$esc\""}]} { set cpu1sel "name =~ \"$esc\""; break }
        }
    }
}
if {$cpu1sel eq ""} {
    puts "M1_CPU1_TARGET=NOT_FOUND"
    disconnect
    exit 3
}
puts "M1_CPU1_SELECT=$cpu1sel"
puts "M1_CPU1_TARGET=[info target]"

# 步骤 C：两次采样（间隔 ≥2 s），判定 halted 且 PC 不推进
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