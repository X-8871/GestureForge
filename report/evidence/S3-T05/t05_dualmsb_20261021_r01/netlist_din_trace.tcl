# =============================================================================
# S3-T05-PL3：在综合后网表里核对「重建位确实接到 FIFO din」
#
# 用法：
#   vivado -mode batch -source netlist_din_trace.tcl -log <log> -tclargs <synth_dcp>
#
# 原理：16 位重建字按卡面位表 B'[4]=B[3]（字 bit15）、G'[2]=G[3]（字 bit7）。
#   RTL 里 `din = {s_axis_tdata_dualmsb, s_axis_tlast, s_axis_tuser}`（18 位），
#   故 A=重建字 占 din[17:2]（din[i] = A[i-2]，i>=2），tlast=din[1]、tuser=din[0]。
#   因此重建位 A[15]、A[7] 落在 **din[17]、din[9]**；
#   参考位 A[14]=B[3] 落在 din[16]、A[8]=G[3] 落在 din[10]（基线实测已确认 din[15]<-tdata[13] 等）。
#   多数表决是 3 抽头：maj = (c0&c1)|(c0&c2)|(c1&c2)，其中 c1/c2 是新增的像素率延迟寄存器。
#   因此网表上应表现为：
#     * din[17]（B'[4]）的根驱动有 3 个（当前样本 + 2 个延迟样本），且其中包含 din[16]（B[3]）的根驱动；
#     * din[9]（G'[2]）同理，包含 din[10]（G[3]）的根驱动；
#     * 未重建的位仍被单个寄存器直接驱动。
#   打印成机器可读行，供构建报告解析；不修改任何网表。
#
# 输出格式（每行 ILA_DIN| 前缀）：
#   ILA_DIN|din_total=<N>
#   ILA_DIN|bit=<i> net=<net> depth1=<pin>(<ref>) depth2=<pin>(<ref>) roots=<pin>|<pin>|...
#   ILA_DIN|roots_of_din14=<...>  roots_of_din8=<...>
#   ILA_DIN|DONE=1
# =============================================================================

set DCP [lindex $argv 0]
if {$DCP eq ""} { puts "ILA_DIN|FAIL=usage_tclargs_synth_dcp"; exit 2 }
if {![file exists $DCP]} { puts "ILA_DIN|FAIL=dcp_missing:$DCP"; exit 2 }

proc dlog {m} { puts "ILA_DIN|$m"; flush stdout }

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

# 向上追溯最多 depth 层组合逻辑，收集"根驱动"（遇到非组合单元即停）
# 注意：下钻组合单元时必须取其**输入**管脚（取输出管脚只会回到它自己）。
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

dlog "DCP=$DCP"
open_checkpoint $DCP
dlog "TOPPART=[get_property PART [current_design]]"

set din_all [get_pins -hier -quiet -filter {NAME =~ "*xpm_fifo_async_inst/din*"}]
dlog "din_total=[llength $din_all] sample=[join [lrange $din_all 0 5] {|}]"
if {[llength $din_all] == 0} {
    dlog "FAIL=no_fifo_din_pins_found"
    exit 3
}

array set DIN {}
foreach p $din_all {
    if {[regexp {xpm_fifo_async_inst/din\[([0-9]+)\]$} $p -> idx]} { set DIN($idx) $p }
}
dlog "din_bits=[lsort -integer [array names DIN]]"

foreach idx {17 16 10 9 8 7 2} {
    if {![info exists DIN($idx)]} { dlog "bit=$idx MISSING"; continue }
    set p $DIN($idx)
    set nets [get_nets -quiet -of_objects $p]
    set n "<none>"
    if {[llength $nets] > 0} { set n [lindex $nets 0] }
    set ds [drivers_of_pin $p]
    set d1 "<none>"
    set ref1 "<none>"
    if {[llength $ds] > 0} {
        set d1 [lindex $ds 0]
        set ref1 [ref_of_pin $d1]
    }
    set d2 "<none>"
    set ref2 "<none>"
    if {[llength $ds] > 0} {
        set d1s [drivers_of_pin $d1]
        if {[llength $d1s] > 0} {
            set d2 [lindex $d1s 0]
            set ref2 [ref_of_pin $d2]
        }
    }
    set roots [roots_of_pin $p 4]
    set lutin {}
    if {[llength $ds] > 0} {
        set dc [get_cells -quiet -of_objects [lindex $ds 0]]
        if {[llength $dc] > 0} {
            set lutin [get_pins -quiet -of_objects [lindex $dc 0] -filter {DIRECTION == IN}]
        }
    }
    dlog "bit=$idx net=$n depth1=${d1}(${ref1}) depth2=${d2}(${ref2}) lut_inputs=[join $lutin {|}] roots=[join $roots {|}]"
    if {$idx == 16} { dlog "roots_of_din16_B3=[join $roots {|}]" }
    if {$idx == 10} { dlog "roots_of_din10_G3=[join $roots {|}]" }
}

dlog "DONE=1"
exit 0