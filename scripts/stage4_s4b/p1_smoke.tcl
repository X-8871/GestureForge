# P1 smoke：分步断言（每步各自记录；失败即停并指出失败步）
# 用法：xsdb.bat <本文件>（或由驱动调用）
# 退出码：0=三步全过；11=步骤1 targets 失败；12=步骤2 选目标失败；13=步骤3 只读失败
# 说明：本脚本**只读**；不 halt/resume/stop 任何目标。

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

# ---------- 步骤 2：选目标（APU 优先；失败再按 #0 过滤） ----------
set selected {}
foreach filt {{name =~ "APU*"} {name =~ "*#0*"} {name =~ "*Cortex-A9*"}} {
    if {![catch {targets -set -filter $filt} err]} { set selected $filt; break }
}
if {$selected eq {}} {
    puts "P1_STEP2=FAIL 无法通过过滤选中目标：$err"
    exit 12
}
puts "P1_STEP2=OK filter=$selected"
if {[catch {puts "P1_INFO_TARGET=[info target]"} err]} {
    puts "P1_INFO_TARGET=ERR:$err"
}

# ---------- 步骤 3：一次只读（DevCfg STATUS，只读寄存器） ----------
if {[catch {set v [lindex [mrd 0xF8007014] 0]} err]} {
    puts "P1_STEP3=FAIL mrd:$err"
    disconnect
    exit 13
}
puts "P1_STEP3=OK"
puts "P1_DEVCGF_STATUS=$v"
puts "P1_RESULT=PASS"
disconnect
exit 0