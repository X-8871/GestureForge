# =============================================================================
# S3-T05-PL4：在综合后网表里核对「新 16 位字的三个通道位确实来自绿通道 G'」
#
# 用法：
#   vivado -mode batch -source netlist_din_trace_gray.tcl -log <log> -tclargs <synth_dcp>
#
# 背景：PL 端中性灰度把整个字换成 { G'[5:1], G'[5:0], G'[5:1] }，其中
#   G' = { tdata[10], tdata[9], tdata[8], maj3(tdata[8]), tdata[6], tdata[5] }
#   maj3 = (c0&c1)|(c0&c2)|(c1&c2)，c1/c2 是 2 个新增像素率延迟寄存器。
# 位映射（word[i]，din[i+2]，因为 din = {word, tlast, tuser}）：
#   word15..11 = G'[5:1] = t10, t9, t8, maj, t6
#   word10..5  = G'[5:0] = t10, t9, t8, maj, t6, t5
#   word4..0   = G'[5:1] = t10, t9, t8, maj, t6
# 因此**所有** word 位的根驱动都应落在允许集合内：
#   { cmos_d_16bit_d1_reg[5]/Q, [6]/Q, [8]/Q, [9]/Q, [10]/Q, gray_g2_d1_reg/Q, gray_g2_d2_reg/Q }
# 绝不应出现 R 字段的 reg[0..4]、B 字段的 reg[11..15]，或已死的 G[2] 原寄存器 reg[7]。
#
# 本脚本回溯 din[0..17] 每一位的驱动（下钻 LUT 输入，不看 LUT 输出自身）并打印机器可读行；
# 不修改任何网表。
#
# 输出格式（每行 ILA_GRAY| 前缀）：
#   ILA_GRAY|din_total=<N>
#   ILA_GRAY|bit=<i> net=<net> depth1=<pin>(<ref>) lut_inputs=<pin>|<pin>... roots=<pin>|<pin>...
#   ILA_GRAY|DONE=1
# =============================================================================

set DCP [lindex $argv 0]
if {$DCP eq ""} { puts "ILA_GRAY|FAIL=usage_tclargs_synth_dcp"; exit 2 }
if {![file exists $DCP]} { puts "ILA_GRAY|FAIL=dcp_missing:$DCP"; exit 2 }

proc glog {m} { puts "ILA_GRAY|$m"; flush stdout }

proc ref_of_pin {p} {
    set c [get_cells -quiet -of_objects $p]
    if {[llength $c] == 0} { return "<none>" }
    return [get_property REF_NAME [lindex $c 0]]
}

proc drivers_of_pin {p} {
    set nets [get_nets -quiet -of_objects $p]
    if {[llength $nets] == 0} { return {} }
    set outs {}
    foreach n $nets {
        foreach o [get_pins -quiet -of_objects [get_nets $n] -filter {DIRECTION == OUT}] {
            lappend outs $o
        }
    }
    return $outs
}

# 向上追溯最多 depth 层组合逻辑，收集"根驱动"（遇到时序单元即停）。
# 关键：下钻组合单元时必须取其**输入**管脚（取输出管脚只会回到它自己）。
proc roots_of_pin {p depth} {
    set ds [drivers_of_pin $p]
    if {[llength $ds] == 0} { return [list $p] }
    if {$depth <= 0} { return [lsort -unique $ds] }
    set roots {}
    foreach d $ds {
        set ref [ref_of_pin $d]
        if {[string match "LUT*" $ref] || [string match "MUXF*" $ref]} {
            set c [get_cells -quiet -of_objects $d]
            set ins {}
            if {[llength $c] > 0} {
                foreach ip [get_pins -quiet -of_objects [lindex $c 0] -filter {DIRECTION == IN}] { lappend ins $ip }
            }
            if {[llength $ins] == 0} {
                lappend roots $d
            } else {
                foreach ip $ins {
                    foreach r [roots_of_pin $ip [expr {$depth - 1}]] { lappend roots $r }
                }
            }
        } else {
            lappend roots $d
        }
    }
    return [lsort -unique $roots]
}

glog "DCP=$DCP"
open_checkpoint $DCP
glog "TOPPART=[get_property PART [current_design]]"

set din_all [get_pins -hier -quiet -filter {NAME =~ "*xpm_fifo_async_inst/din*"}]
glog "din_total=[llength $din_all] sample=[join [lrange $din_all 0 5] {|}]"
if {[llength $din_all] == 0} {
    glog "FAIL=no_fifo_din_pins_found"
    exit 3
}

array set DIN {}
foreach p $din_all {
    if {[regexp {xpm_fifo_async_inst/din\[([0-9]+)\]$} $p -> idx]} { set DIN($idx) $p }
}
glog "din_bits=[lsort -integer [array names DIN]]"

foreach idx [lsort -integer [array names DIN]] {
    set p $DIN($idx)
    set nets [get_nets -quiet -of_objects $p]
    set n "<none>"
    if {[llength $nets] > 0} { set n [lindex $nets 0] }
    set ds [drivers_of_pin $p]
    set d1 "<none>"; set ref1 "<none>"
    if {[llength $ds] > 0} { set d1 [lindex $ds 0]; set ref1 [ref_of_pin $d1] }
    set roots [roots_of_pin $p 4]
    set lutin {}
    if {[llength $ds] > 0} {
        set dc [get_cells -quiet -of_objects [lindex $ds 0]]
        if {[llength $dc] > 0} {
            set lutin [get_pins -quiet -of_objects [lindex $dc 0] -filter {DIRECTION == IN}]
        }
    }
    glog "bit=$idx net=$n depth1=${d1}(${ref1}) lut_inputs=[join $lutin {|}] roots=[join $roots {|}]"
}

glog "DONE=1"
exit 0