# 阶段3 许可/器件探测：验证 Vivado 2026.1 对现行器件 xc7z020clg400-2（XC7Z020-2CLG400I）的
# Synthesis / Implementation 许可链路。只跑极小的内存设计，不烧录、不接板、不写授权目录外文件。
# 用法: vivado -mode batch -source s3_license_part_probe.tcl -tclargs <outdir> <part>

set outdir [lindex $argv 0]
set part   [lindex $argv 1]
if {$outdir eq "" || $part eq ""} {
    puts "PROBE_FAIL=USAGE: -tclargs <outdir> <part>"
    exit 3
}
file mkdir $outdir

puts "PROBE_VIVADO_VERSION=[version -short]"
puts "PROBE_PART_REQUESTED=$part"
if {[info exists ::env(XILINXD_LICENSE_FILE)]} {
    puts "PROBE_LICENSE_ENV=$::env(XILINXD_LICENSE_FILE)"
} else {
    puts "PROBE_LICENSE_ENV=<unset>"
}

set vfile [file join $outdir probe_top.v]
set f [open $vfile w]
puts $f "module probe_top(input clk, input a, output reg b);"
puts $f "  reg \[7:0\] cnt = 8'd0;"
puts $f "  always @(posedge clk) begin"
puts $f "    cnt <= cnt + 8'd1;"
puts $f "    b <= a ^ cnt\[0\];"
puts $f "  end"
puts $f "endmodule"
close $f

read_verilog $vfile
synth_design -top probe_top -part $part
puts "PROBE_SYNTH_OK=1"

opt_design
puts "PROBE_OPT_OK=1"
place_design
puts "PROBE_PLACE_OK=1"
route_design
puts "PROBE_ROUTE_OK=1"

catch { set_property SEVERITY {Warning} [get_drc_checks NSTD-1] }
catch { set_property SEVERITY {Warning} [get_drc_checks UCIO-1] }
set bitfile [file join $outdir probe_top.bit]
write_bitstream -force $bitfile
puts "PROBE_BITSTREAM_EXISTS=[file exists $bitfile]"
puts "PROBE_ALL_DONE=1"
exit 0