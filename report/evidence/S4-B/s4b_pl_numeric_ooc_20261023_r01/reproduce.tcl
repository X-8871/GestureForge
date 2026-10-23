set_param general.maxThreads 2
read_verilog -sv {D:/codex-worktrees/w4/src/s4b_preproc_fp64.sv}
read_verilog -sv {D:/codex-worktrees/w4/src/s4b_preproc_pixel.sv}
get_parts xc7z020clg400-2
synth_design -top s4b_preproc_pixel -part xc7z020clg400-2 -mode out_of_context
create_clock -name preproc_clk -period 20.000 [get_ports clk]
set_input_delay -clock preproc_clk 0.000 [get_ports -filter {DIRECTION == IN && NAME != clk}]
set_output_delay -clock preproc_clk 0.000 [all_outputs]
write_checkpoint {numeric_synth.dcp}
write_xdc {numeric_post_synth.xdc}
report_utilization -file {utilization.rpt}
report_timing_summary -delay_type min_max -report_unconstrained -file {timing_summary.rpt}
report_timing -delay_type max -max_paths 10 -file {timing_paths.rpt}
dict create tool_version [version -short] part [get_property PART [current_design]] sequential_cells [llength [get_cells -hierarchical -filter {IS_SEQUENTIAL}]] internal_max_slack [get_property SLACK [get_timing_paths -from [all_registers] -to [all_registers] -delay_type max -max_paths 1]] internal_min_slack [get_property SLACK [get_timing_paths -from [all_registers] -to [all_registers] -delay_type min -max_paths 1]]
