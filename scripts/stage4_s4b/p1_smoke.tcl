# P1 smoke：分步断言（每步各自记录；失败即停并指出失败步）
# 用法：xsdb.bat <本文件>（由驱动调用）
# 退出码：0=三步全过；11=步骤1 targets 失败；12=步骤2 选目标失败；13=步骤3 只读失败
# 只读脚本；不 halt/resume/stop 任何目标。
# 修订（窗口2 后）：选目标用 `*Cortex-A9*` 过滤到**核**；删除无效的 `info target`；寄存器读取用 `mrd -value`。

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]

# ---------- 步骤 1：connect + 枚举 targets ----------
if {[catch {connect -url $url} err]} {
    puts "P1_STEP1=FAIL connect:$err"
    exit 11
}
puts "P1_XSDB_VERSION=[version]"
if {[catch {set all [targets]} err]} {
    puts "P1_STEP1=FAIL targets:$err"
    exit 11
}
puts "P1_STEP1=OK"
puts "P1_TARGET_COUNT=[llength $all]"
set idx 0
foreach t $all {
    puts "P1_TARGET[$idx]=$t"
    incr idx
}

# ---------- 步骤 2：选目标（必须是处理器核；`APU*` 是集群，不能用于 rst/寄存器操作） ----------
set selected {}
foreach filt {{name =~ "*Cortex-A9*#0*"} {name =~ "*#0*"}} {
    if {![catch {targets -set -filter $filt} err]} { set selected $filt; break }
}
if {$selected eq {}} {
    puts "P1_STEP2=FAIL 无法选中处理器核：$err"
    exit 12
}
puts "P1_STEP2=OK filter=$selected"

# ---------- 步骤 3：一次只读（DevCfg STATUS，只读）；用 -value 取 Tcl 列表 ----------
if {[catch {set words [mrd -value 0xF8007014]} err]} {
    puts "P1_STEP3=FAIL mrd:$err"
    disconnect
    exit 13
}
set devcfg [lindex $words 0]
puts "P1_STEP3=OK"
puts "P1_DEVCGF_STATUS=$devcfg"
puts "P1_RESULT=PASS"
disconnect
exit 0