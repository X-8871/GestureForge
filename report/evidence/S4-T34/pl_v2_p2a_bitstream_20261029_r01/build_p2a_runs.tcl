# build_p2a_runs.tcl —— P2a：project-mode 从 BD 到 bit/XSA（含 IP OOC synth）
# 前置：$root = 已 staging 的源码（planA 引擎 + 重命名后的 wrap），$out = 输出
set root "D:/tmp/lead/p2a_20261029_r01/src"
set out  "D:/tmp/lead/p2a_20261029_r01/out"
file mkdir $out
set ::env(S4D_BD_DIR) "$out/bd_runs"

# 1) BD 创建 + validate + 地址分配（bd tcl 内部 create_project）
source "$root/bd_preproc_v2.tcl"
puts "P2A_BD_OK"

# 2) 生成 BD 目标 + wrapper
generate_target all [get_files s4d_preproc_v2.bd]
make_wrapper -files [get_files s4d_preproc_v2.bd] -top
set wrap "$out/bd_runs/s4d_preproc_v2_bd/s4d_preproc_v2_bd.gen/sources_1/bd/s4d_preproc_v2/hdl/s4d_preproc_v2_wrapper.v"
if {![file exists $wrap]} { error "WRAPPER_NOT_FOUND $wrap" }
add_files -fileset sources_1 -norecurse $wrap
set_property top s4d_preproc_v2_wrapper [get_filesets sources_1]
update_compile_order -fileset sources_1
puts "P2A_WRAPPER_OK $wrap"

# 3) 时钟约束：PS7 FCLK0 由 IP 自动定义；显式加一条防止未约束（同名时 Vivado 会合并）
set xdc "$out/p2a_clocks.xdc"
set fd [open $xdc w]
puts $fd "# P2a：FCLK0 = 100 MHz（PS7 CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ=100 已自动定义；此约束用于兜底校验）"
puts $fd "create_clock -period 10.000 -name clk_fclk0 \[get_pins -hier -filter {NAME =~ *FCLK_CLK0}\]"
close $fd

# 4) 运行 synth / impl / bitstream
launch_runs synth_1 -jobs 2
wait_on_run synth_1
set st [get_property PROGRESS [get_runs synth_1]]
puts "P2A_SYNTH_PROGRESS=$st"
if {$st ne "100%"} { error "SYNTH_FAILED $st" }

set_property STEPS.WRITE_BITSTREAM.ARGS.BIN_FILE true [get_runs impl_1]
launch_runs impl_1 -to_step write_bitstream -jobs 2
wait_on_run impl_1
set st2 [get_property PROGRESS [get_runs impl_1]]
puts "P2A_IMPL_PROGRESS=$st2"
if {$st2 ne "100%"} { error "IMPL_FAILED $st2" }

# 5) 报告 + 产物
open_run impl_1
report_timing_summary -delay_type min_max -max_paths 10 -file "$out/timing_route.rpt"
report_utilization -file "$out/util_route.rpt"
report_clocks -file "$out/clocks_route.rpt"
set wns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1 -nworst 1]]
set whs [get_property SLACK [get_timing_paths -delay_type min -max_paths 1 -nworst 1]]
set luts  [llength [get_cells -hier -quiet -filter {PRIMITIVE_GROUP == LUT}]]
set ffs   [llength [get_cells -hier -quiet -filter {PRIMITIVE_GROUP == REGISTER}]]
set dsps  [llength [get_cells -hier -quiet -filter {REF_NAME =~ DSP48E1*}]]
set brams [llength [get_cells -hier -quiet -filter {REF_NAME =~ RAMB*}]]
set fd [open "$out/summary_p2a.txt" w]
puts $fd "top=s4d_preproc_v2_wrapper"
puts $fd "wns_ns=$wns"
puts $fd "whs_ns=$whs"
puts $fd "lut_cells=$luts"
puts $fd "ff_cells=$ffs"
puts $fd "dsp48=$dsps"
puts $fd "bram_primitive=$brams"
close $fd
puts "P2A_SUMMARY WNS=$wns WHS=$whs LUT=$luts FF=$ffs DSP=$dsps BRAM=$brams"

set bit [glob -nocomplain "$out/bd_runs/s4d_preproc_v2_bd/s4d_preproc_v2_bd.runs/impl_1/*.bit"]
puts "P2A_BIT_CANDIDATES=$bit"
if {[llength $bit] > 0} {
    file copy -force [lindex $bit 0] "$out/s4d_preproc_p2a.bit"
    puts "P2A_BIT_OK $out/s4d_preproc_p2a.bit"
}
write_hw_platform -fixed -force -file "$out/s4d_preproc_p2a.xsa"
puts "P2A_XSA_OK $out/s4d_preproc_p2a.xsa"
puts "==== P2A RUNS DONE ===="