# M3：候选区写-回读 + 恢复 + 逐字校验（严格限定 [0x12000000,0x12C08000)）
# 用法：xsdb.bat <本文件> <mode> <binfile>
#   mode=snapshot  只读整区到 <binfile>
#   mode=write     写确定性图案（仅候选区内）
#   mode=readback  整区回读到 <binfile>
#   mode=restore   用 <binfile>（快照）整区回写
# 退出码：0=成功；2=参数/区间断言失败；5=选目标失败；7=mrd/mwr 失败
# 修复（窗口1 后）：所有 mrd/mwr 前**先选目标**；区间断言不变。

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

# 修复点：先选目标
set sel ""
foreach filt {{name =~ "APU*"} {name =~ "*Cortex-A9*"} {name =~ "*#0*"}} {
    if {![catch {targets -set -filter $filt}]} { set sel $filt; break }
}
if {$sel eq ""} {
    puts "M3_SELECT=FAIL"
    disconnect
    exit 5
}
puts "M3_SELECT=OK filter=$sel"

if {$mode == "snapshot" || $mode == "readback"} {
    if {[catch {mrd -bin -file $binfile $BASE $WORDS} err]} {
        puts "M3_ERROR=mrd:$err"
        disconnect
        exit 7
    }
    puts "M3_DUMP=$binfile"
    puts "M3_RESULT=READ_OK"
} elseif {$mode == "write"} {
    # 确定性图案：分块 64 KiB，块首写 0x5A5A0000|chunk，其余 0xA5A5A5A5
    set chunk_words 16384
    set chunks [expr {($WORDS + $chunk_words - 1) / $chunk_words}]
    for {set c 0} {$c < $chunks} {incr c} {
        set addr [expr {$BASE + $c * $chunk_words * 4}]
        set remain [expr {$WORDS - $c * $chunk_words}]
        set n [expr {$remain < $chunk_words ? $remain : $chunk_words}]
        set marker [format "0x5A5A%04X" $c]
        if {[catch {
            mwr $addr $marker
            if {$n > 1} { mwr -pattern 0xA5A5A5A5 [expr {$addr + 4}] [expr {$n - 1}] }
        } err]} {
            puts "M3_ERROR=mwr:$err"
            disconnect
            exit 7
        }
    }
    puts "M3_CHUNKS=$chunks"
    puts "M3_RESULT=WRITE_OK"
} elseif {$mode == "restore"} {
    if {[catch {mwr -bin -file $binfile $BASE} err]} {
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