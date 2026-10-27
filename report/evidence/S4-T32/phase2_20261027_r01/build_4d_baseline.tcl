# S4-T32 Phase 2 基线构建：用 2B 冻结 BD + RTL 闭包，在 w4 tmp 内独立重建平台并跑综合/实现/bitstream。
# 只在 tmp 内工作，不写 w2b。所有失败以 error 终止（真实退出码由 vivado 返回）。

set root "D:/codex-worktrees/w4/tmp/4/S4-T32/build_r01"
set part "xc7z020clg400-2"
set log [open [file join $root build.log] a]
proc note {msg} {
    global log
    puts $msg
    puts $log $msg
    flush $log
}

note "== S4-T32 Phase2 baseline build start: [clock format [clock seconds] -format {%Y-%m-%dT%H:%M:%S}] =="
if {[llength [get_parts $part]] != 1} { error "PART_NOT_EXACT:$part" }
note "PART: $part"
note "VIVADO: [version -short]"

# 1) 工程
create_project s4d_baseline [file join $root prj] -part $part -force
set_property target_language Verilog [current_project]

# 2) RTL 闭包（先加 RTL，BD 的 module_ref 才能解析）
set rtl [glob -nocomplain [file join $root rtl *.sv]]
if {[llength $rtl] == 0} { error "RTL_MISSING" }
foreach f $rtl { add_files -norecurse $f }
note "RTL_FILES: [llength $rtl]"

# 3) 冻结 BD
set bdfile [file join $root bd s2b_inference.bd]
if {![file isfile $bdfile]} { error "BD_MISSING" }
add_files -norecurse $bdfile
set bd [get_files -quiet s2b_inference.bd]
if {[llength $bd] != 1} { error "BD_OBJECT_FAIL" }
open_bd_design $bd
validate_bd_design -force
save_bd_design
note "BD_VALIDATE: OK"

# 4) 包装 + 顶层
generate_target all $bd
make_wrapper -files $bd -top -import
set wrapper [get_files -quiet */s2b_inference_wrapper.v]
if {[llength $wrapper] != 1} { error "WRAPPER_FAIL" }
set_property top s2b_inference_wrapper [current_fileset]
update_compile_order -fileset sources_1
note "TOP: s2b_inference_wrapper"

# 5) 50 MHz 约束（FCLK_CLK0 由 PS 提供）
set xdc [file join $root constr s4d_50mhz.xdc]
file mkdir [file dirname $xdc]
set fh [open $xdc w]
puts $fh {create_clock -period 20.000 -name clk_fclk0_50mhz [get_pins -hierarchical -filter {NAME =~ */FCLK_CLK0}]}
close $fh
add_files -fileset constrs_1 -norecurse $xdc
note "XDC: $xdc"

# 6) 综合
launch_runs synth_1 -jobs 4
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} {
    note "SYNTH_PROGRESS: [get_property PROGRESS [get_runs synth_1]]"
    error "SYNTH_FAIL"
}
open_run synth_1
set rd [file join $root reports]
file mkdir $rd
report_utilization -file [file join $rd utilization_synth.rpt]
report_timing_summary -file [file join $rd timing_synth.rpt]
note "SYNTH: OK"

# 7) 实现 + 位流
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {
    note "IMPL_PROGRESS: [get_property PROGRESS [get_runs impl_1]]"
    error "IMPL_FAIL"
}
open_run impl_1
report_utilization -file [file join $rd utilization_impl.rpt]
report_timing_summary -file [file join $rd timing_impl.rpt]
note "IMPL: OK"
note "== BUILD DONE =="
close $log
exit 0