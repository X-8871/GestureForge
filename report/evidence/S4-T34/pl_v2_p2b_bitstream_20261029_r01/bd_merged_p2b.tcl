# bd_merged_p2b.tcl —— 4-D 合并 BD（P2b）：preproc v2 + 2B 推理核心，GP0/HP0 均走 smartconnect
# 与 2B 原 BD 的差别：**不用 axi_protocol_converter**，改用 smartconnect（AXI4-Lite 从口，P2a 已证可用）
# 目的：验证"PS→2B CSR 读挂死是旧转换器导致"的假设，并得到真正的 4-D 位流。
set root "D:/tmp/lead/p2b_20261029_r01/src"
set out  "D:/tmp/lead/p2b_20261029_r01/out"
file mkdir $out
set part_name "xc7z020clg400-2"

create_project -force s4d_p2b $out/proj -part $part_name
set_property target_language Verilog [current_project]
set_property include_dirs "$root/rtl" [get_filesets sources_1]

# ---- RTL：preproc v2（planA）+ 2B 推理核心（只读引用 w2b 源） ----
add_files -fileset sources_1 -norecurse "$root/rtl/s4d_coord_tables.svh"
foreach f [list \
    "$root/rtl/s4d_preproc_csr.sv" \
    "$root/rtl/s4d_preproc_engine_v2.sv" \
    "$root/rtl/s4d_axi4_rd_shim.sv" \
    "$root/rtl/s4d_preproc_out_axis.sv" \
    "$root/rtl/s4d_preproc_v2_wrap.sv" ] {
    read_verilog -sv $f
}
set W2B "D:/FPGA_Competition/w2b"
foreach rel [list \
    src/s2a_network_descriptor_pkg.sv src/s2b_maxpool_geometry.sv src/int8_maxpool_window.sv \
    src/s2b_route_query.sv src/int8_upsample_query.sv src/s2b_conv_tile_engine.sv \
    src/s2b_maxpool_engine.sv src/s2b_route_engine.sv src/s2b_upsample_engine.sv \
    src/s2b_network_backend.sv src/s2a_memory_master.sv src/s2a_runtime_shell.sv \
    src/s2b_stage2b_core.sv src/s2a_control_csr.sv src/s2b_request_guard.sv \
    src/s2b_hp0_word_adapter.sv src/s2b_control_csr.sv src/s2b_inference_top.sv ] {
    read_verilog -sv "$W2B/$rel"
}
set_property top s4d_preproc_v2_wrap [get_filesets sources_1]
update_compile_order -fileset sources_1

create_bd_design "s4d_p2b"

# ---- PS7：100 MHz、GP0、HP0(64bit) ----
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7 ps7_0
set_property -dict [list \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {50} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64} \
    CONFIG.PCW_USE_S_AXI_HP1 {0} \
] [get_bd_cells ps7_0]
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/FIXED_IO]

# ---- 两个 PL 从设备 ----
create_bd_cell -type module -reference s4d_preproc_v2_wrap s4d_0
create_bd_cell -type module -reference s2b_inference_top infer_0

# ---- 复位同步 ----
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_all
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]     [get_bd_pins rst_all/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_all/ext_reset_in]

# ---- 时钟 ----
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins ps7_0/M_AXI_GP0_ACLK]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins ps7_0/S_AXI_HP0_ACLK]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins s4d_0/clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins infer_0/clk]

# ---- 控制面：GP0 → smartconnect_ctrl(1S/2M) → {s4d CSR, infer CSR} ----
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_ctrl
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {2}] [get_bd_cells smc_ctrl]
connect_bd_intf_net [get_bd_intf_pins ps7_0/M_AXI_GP0] [get_bd_intf_pins smc_ctrl/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M00_AXI] [get_bd_intf_pins s4d_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M01_AXI] [get_bd_intf_pins infer_0/S_AXI]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_ctrl/aclk]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins smc_ctrl/aresetn]

# ---- 数据面：HP0 ← smartconnect_data(1S/2M) ← {preproc M_AXI_RD, infer M_AXI} ----
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_data
set_property -dict [list CONFIG.NUM_SI {2} CONFIG.NUM_MI {1}] [get_bd_cells smc_data]
connect_bd_intf_net [get_bd_intf_pins smc_data/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP0]
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXI_RD] [get_bd_intf_pins smc_data/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins infer_0/M_AXI] [get_bd_intf_pins smc_data/S01_AXI]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_data/aclk]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins smc_data/aresetn]

# ---- 复位 ----
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins s4d_0/rstn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins infer_0/cold_resetn]
# s2b_inference_top 的可见性参数（来自 2B BD）
set_property CONFIG.PROFILE_VISIBILITY_PROVEN {1} [get_bd_cells infer_0]

# ---- 地址（validate 之前） ----
assign_bd_address -offset 0x43C10000 -range 0x00000080 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins s4d_0/S_AXI]]
assign_bd_address -offset 0x43C00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins infer_0/S_AXI]]
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces s4d_0/M_AXI_RD] [get_bd_addr_segs ps7_0/S_AXI_HP0/HP0_DDR_LOWOCM]
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces infer_0/M_AXI] [get_bd_addr_segs ps7_0/S_AXI_HP0/HP0_DDR_LOWOCM]

regenerate_bd_layout
validate_bd_design
save_bd_design
puts "==== P2B BD VALIDATED ===="
foreach seg [get_bd_addr_segs] {
    set off [get_property OFFSET $seg]
    if {$off ne ""} { puts "  [get_property NAME $seg]  offset=$off  range=[get_property RANGE $seg]" }
}

# ---- wrapper + 运行 ----
generate_target all [get_files s4d_p2b.bd]
make_wrapper -files [get_files s4d_p2b.bd] -top -import
set_property top s4d_p2b_wrapper [get_filesets sources_1]
update_compile_order -fileset sources_1
launch_runs synth_1 -jobs 2
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} { error "SYNTH_FAILED" }
set_property STEPS.WRITE_BITSTREAM.ARGS.BIN_FILE true [get_runs impl_1]
launch_runs impl_1 -to_step write_bitstream -jobs 2
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} { error "IMPL_FAILED" }
open_run impl_1
report_timing_summary -delay_type min_max -max_paths 10 -file "$out/timing_route.rpt"
report_utilization -file "$out/util_route.rpt"
set wns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1 -nworst 1]]
set whs [get_property SLACK [get_timing_paths -delay_type min -max_paths 1 -nworst 1]]
puts "P2B_SUMMARY WNS=$wns WHS=$whs"
set bits [glob -nocomplain "$out/proj/s4d_p2b.runs/impl_1/*.bit"]
puts "P2B_BITS=$bits"
if {[llength $bits] > 0} { file copy -force [lindex $bits 0] "$out/s4d_p2b.bit"; puts "P2B_BIT_OK" }
write_hw_platform -fixed -force -file "$out/s4d_p2b.xsa"
puts "P2B_XSA_OK"
puts "==== P2B DONE ===="