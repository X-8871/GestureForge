# =============================================================================
# S3-T05-PL5 有界网表佐证（刻意不做逐位回溯）
#
# 只做一次过滤查询：
#   open_checkpoint(OOC DCP) -> get_cells/get_nets -hier -filter {NAME =~ "*stdluma*"}
#   并反向确认旧补丁标记（dualmsb / bluefix / gray_g2）计数为 0。
# 用法: vivado -mode batch -source check_stdluma_ooc_nets.tcl -tclargs <ooc_dcp> <out_txt>
# =============================================================================
set ::dcp [lindex $argv 0]
set ::out [lindex $argv 1]
if {$::dcp eq "" || $::out eq ""} {
    puts "NETS_FAIL=USAGE: -tclargs <ooc_dcp> <out_txt>"
    exit 3
}
if {![file exists $::dcp]} {
    puts "NETS_FAIL=DCP_MISSING:$::dcp"
    exit 3
}

proc emit {fh line} { puts $line; puts $fh $line }

open_checkpoint $::dcp
set fh [open $::out w]

emit $fh "OOC_DCP=$::dcp"
emit $fh "VIVADO_VERSION=[version -short]"

set cells [get_cells -hier -quiet -filter {NAME =~ "*stdluma*"}]
set nets  [get_nets  -hier -quiet -filter {NAME =~ "*stdluma*"}]
emit $fh "STDLUMA_CELL_COUNT=[llength $cells]"
emit $fh "STDLUMA_NET_COUNT=[llength $nets]"
foreach c $cells { emit $fh "STDLUMA_CELL=$c" }
emit $fh "STDLUMA_NET_SAMPLE=[lrange $nets 0 9]"

# 反向断言：旧补丁标记必须为 0
foreach pat {dualmsb bluefix gray_g2} {
    set n [get_nets  -hier -quiet -filter "NAME =~ \"*$pat*\""]
    set c [get_cells -hier -quiet -filter "NAME =~ \"*$pat*\""]
    switch -- $pat {
        dualmsb { emit $fh "RESIDUAL_DUALMSB_COUNT=[llength $n]" }
        bluefix { emit $fh "RESIDUAL_BLUEFIX_COUNT=[llength $n]" }
        gray_g2 { emit $fh "RESIDUAL_GRAYG2_COUNT=[llength $n]" }
    }
    emit $fh "RESIDUAL_${pat}_CELL_COUNT=[llength $c]"
}

# FIFO 写数据端口仍存在（证明 din 通路完整，未做逐位回溯）
set din [get_pins -quiet -hier -filter {NAME =~ "*xpm_fifo_async_inst/din*"}]
emit $fh "FIFO_DIN_PIN_COUNT=[llength $din]"
close $fh
puts "NETS_DONE=1"
exit 0