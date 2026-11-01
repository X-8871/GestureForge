# M3：候选区写-回读 + 恢复 + 逐字校验（严格限定 [0x12000000,0x12C08000)）
# 用法：xsdb.bat <本文件> <mode> <binfile>
#   mode=snapshot  只读整区到 <binfile>
#   mode=write     写确定性图案（仅候选区内）
#   mode=readback  整区回读到 <binfile>
#   mode=restore   用 <binfile>（快照）整区回写
# 退出码：0=成功；2=参数/区间断言失败；5=选目标失败；7=mrd/mwr 失败
# 修订（窗口2 后）：选目标用 `*Cortex-A9*`（核，非 APU 集群）；整区读写继续用 `-file`（二进制）。

set BASE 0x12000000
set END  0x12C08000
set BYTES 12615680
set WORDS [expr {$BYTES / 4}]

if {$argc < 2} {
    puts "M3_USAGE=<snapshot|write|readback|restore> <binfile>"
    exit 2
}
set mode [lindex $argv 0]
set binfile [lindex $argv 1]
if {$BASE != 301989888 || $END != 314605568 || $BYTES != 12615680} {
    puts "M3_RANGE_ASSERT=FAIL"
    exit 2
}
puts "M3_MODE=$mode"
puts "M3_BINFILE=$binfile"
puts "M3_BASE=$BASE"
puts "M3_END_EXCLUSIVE=$END"
puts "M3_BYTES=$BYTES"
puts "M3_WORDS=$WORDS"

set url [expr {[info exists env(S4_HW_URL)] ? $env(S4_HW_URL) : "tcp:127.0.0.1:3121"}]
connect -url $url

if {[catch {targets -set -filter {name =~ "*Cortex-A9*#0*"}} err]} {
    puts "M3_SELECT=FAIL $err"
    disconnect
    exit 5
}
puts "M3_SELECT=OK"

if {$mode == "snapshot" || $mode == "readback"} {
    if {[catch {mrd -bin -file $binfile $BASE $WORDS} err]} {
        puts "M3_ERROR=mrd:$err"
        disconnect
        exit 7
    }
    puts "M3_DUMP=$binfile"
    puts "M3_RESULT=READ_OK"
} elseif {$mode == "write"} {
    # 修订（窗口5 后）：xsdb 2026.1 的 mwr **无 -pattern 选项**；改为写入由驱动预生成的图案文件
    # （图案文件自带每块标记字 + 0xA5A5A5A5 填充），一次性整区写入。
    if {[catch {mwr -bin -file $binfile $BASE $WORDS} err]} {
        puts "M3_ERROR=mwr:$err"
        disconnect
        exit 7
    }
    puts "M3_RESULT=WRITE_OK"
} elseif {$mode == "restore"} {
    # 修订（窗口5 后）：`mwr -bin -file` 必须显式给出字数，否则报 wrong # of args。
    if {[catch {mwr -bin -file $binfile $BASE $WORDS} err]} {
        puts "M3_ERROR=mwr:$err"
        disconnect
        exit 7
    }
    puts "M3_RESULT=RESTORE_OK"
} else {
    puts "M3_ERROR=unknown_mode:$mode"
    disconnect
    exit 2
}
disconnect
exit 0