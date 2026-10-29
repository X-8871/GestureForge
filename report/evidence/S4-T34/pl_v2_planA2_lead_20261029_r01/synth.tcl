# synth_p1_planA2.tcl —— planA2：我(lead)对 4 拍版做 planA 改动后的两轮综合
# 对象：D:/tmp/lead/planA2_20261029_r01/rtl（4 拍版 + (ONE24-dy_q) 前移到拍1 沿）
# 范围：仅 synth_design，top = s4d_preproc_engine_v2；不做 opt/place/route/bit。
set out_dir "[file normalize {D:/tmp/lead/planA2_20261029_r01/out}]"
file mkdir $out_dir
create_project -in_memory -part xc7z020clg400-2
set_property target_language Verilog [current_project]

set RTL "D:/tmp/lead/planA2_20261029_r01/rtl"
foreach f [list \
    "$RTL/s4d_preproc_csr.sv" \
    "$RTL/s4d_preproc_engine_v2.sv" \
    "$RTL/s4d_axi4_rd_shim.sv" \
    "$RTL/s4d_preproc_out_axis.sv" \
    "$RTL/s4d_preproc_v2_wrapper.sv" ] {
    read_verilog -sv $f
}

proc ram_histogram {tag} {
    set pats [list RAMB18* RAMB36* RAM32M* RAM64M* RAM32X* RAM64X* RAM128X* RAM256X* RAMD32* RAMD64* RAMS32* RAMS64*]
    set fd [open "$::out_dir/ramhist_$tag.txt" w]
    set total 0
    foreach p $pats {
        set n [llength [get_cells -hier -quiet -filter "REF_NAME =~ $p"]]
        if {$n > 0} { puts $fd "$p $n"; incr total $n }
    }
    puts $fd "TOTAL_BRAM_LUTRAM_PRIMITIVES $total"
    close $fd
}

proc run_one {period tag} {
    puts "==== SYNTH planA2 @ ${period} ns ($tag) ===="
    synth_design -top s4d_preproc_engine_v2 -part xc7z020clg400-2 \
                 -include_dirs $::RTL \
                 -flatten_hierarchy rebuilt
    create_clock -period $period -name clk [get_ports clk]
    report_utilization    -file "$::out_dir/util_$tag.rpt"
    report_timing_summary -delay_type min_max -max_paths 5 -file "$::out_dir/timing_$tag.rpt"
    report_timing -delay_type max -max_paths 10 -nworst 1 -file "$::out_dir/critical_$tag.rpt"
    ram_histogram $tag
    set wns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1 -nworst 1]]
    set whs [get_property SLACK [get_timing_paths -delay_type min -max_paths 1 -nworst 1]]
    set luts  [llength [get_cells -hier -filter {PRIMITIVE_GROUP == LUT}]]
    set ffs   [llength [get_cells -hier -filter {PRIMITIVE_GROUP == REGISTER}]]
    set dsps  [llength [get_cells -hier -filter {REF_NAME =~ DSP48E1*}]]
    set brams [llength [get_cells -hier -filter {REF_NAME =~ RAMB*}]]
    set lutmem [llength [get_cells -hier -filter {PRIMITIVE_SUBGROUP == LUT_MEMORY}]]
    set fd [open "$::out_dir/summary_$tag.txt" w]
    puts $fd "top=s4d_preproc_engine_v2"
    puts $fd "clock_period_ns=$period"
    puts $fd "wns_ns=$wns"
    puts $fd "whs_ns=$whs"
    puts $fd "lut_cells=$luts"
    puts $fd "ff_cells=$ffs"
    puts $fd "dsp48=$dsps"
    puts $fd "bram_primitive=$brams"
    puts $fd "lut_memory_primitive=$lutmem"
    close $fd
    puts "SUMMARY tag=$tag WNS=$wns WHS=$whs LUT=$luts FF=$ffs DSP=$dsps BRAM=$brams LUTRAM=$lutmem"
    close_design
}

run_one 10.000 100mhz
run_one 6.667  150mhz
puts "==== PLANA2 SYNTH DONE ===="