# bd_p2c.tcl —— P2c 候选 BD：preproc v2（源图基址 0x12000000）+ 2B 推理 + **preproc M_AXIS → AXI DMA S2MM → HP0**
#
# 与 P2b 的差异（只加"输出消费者"，不加别的功能）：
#   1) preproc 的 M_AXIS（8 bit，无 TKEEP）先经 s4d_axis8_to_axis64 打包成 64 bit（小端、TKEEP=0xFF、TLAST 透传）；
#   2) 打包后的流接 AXI DMA（仅 S2MM、非 SG 简单模式，MM 64 bit / STREAM 64 bit）；
#   3) AXI DMA 的 M_AXI_S2MM 经 smc_data 的第 3 个从口进 HP0；
#   4) AXI DMA 的 AXI-Lite 寄存器在 GP0 上分配 0x43C20000（range 0x10000），PS 侧写 DA/LENGTH 启动传输；
#   5) preproc 源图基址由 RTL 参数 SRC_BASE=0x12000000 固定（ABI raw_frame），不再读 DDR 0x0。
#
# 用法： vivado -mode batch -source bd_p2c.tcl            → 只建 BD + validate（约 2 分钟）
#        vivado -mode batch -source bd_p2c.tcl -tclargs build → 继续综合/实现/位流/XSA（约 20 分钟）
#
# 边界：本文件只生成**候选**位流；未上板、不改冻结件、不主张 G3/G4/G5。

set root "D:/tmp/lead/p2c_20261029_r01/src"
set out  "D:/tmp/lead/p2c_20261029_r01/out"
set do_build [expr {$argc > 0 && [lindex $argv 0] eq "build"}]
file mkdir $out
set part_name "xc7z020clg400-2"

create_project -force s4d_p2c $out/proj -part $part_name
set_property target_language Verilog [current_project]
set_property include_dirs "$root/rtl" [get_filesets sources_1]

# ---- RTL：preproc v2（SRC_BASE 版）+ 打包器 + 2B 推理核心（2B 源只读引用 w2b） ----
add_files -fileset sources_1 -norecurse "$root/rtl/s4d_coord_tables.svh"
foreach f [list \
    "$root/rtl/s4d_preproc_csr.sv" \
    "$root/rtl/s4d_preproc_engine_v2.sv" \
    "$root/rtl/s4d_axi4_rd_shim.sv" \
    "$root/rtl/s4d_preproc_out_axis.sv" \
    "$root/rtl/s4d_preproc_v2_wrap.sv" \
    "$root/rtl/s4d_axis8_to_axis64.sv" ] {
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

create_bd_design "s4d_p2c"

# ---- PS7：FCLK0 50 MHz、GP0、HP0(64bit) ----
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

# ---- PL 从设备 + 打包器 + DMA ----
create_bd_cell -type module -reference s4d_preproc_v2_wrap s4d_0
create_bd_cell -type module -reference s2b_inference_top infer_0
create_bd_cell -type module -reference s4d_axis8_to_axis64 pack_0
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_dma axi_dma_0
set_property -dict [list \
    CONFIG.c_include_sg {0} \
    CONFIG.c_sg_include_stscntrl_strm {0} \
    CONFIG.c_include_mm2s {0} \
    CONFIG.c_include_s2mm {1} \
    CONFIG.c_m_axi_s2mm_data_width {64} \
    CONFIG.c_s_axis_s2mm_tdata_width {64} \
    CONFIG.c_addr_width {32} \
] [get_bd_cells axi_dma_0]

# ---- 复位同步 ----
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_all
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]     [get_bd_pins rst_all/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_all/ext_reset_in]

# ---- 时钟 ----
foreach p [get_bd_pins -quiet {ps7_0/M_AXI_GP0_ACLK ps7_0/S_AXI_HP0_ACLK s4d_0/clk infer_0/clk pack_0/clk axi_dma_0/*aclk*}] {
    connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] $p
}

# ---- 控制面：GP0 → smartconnect_ctrl(1S/3M) → {preproc CSR, 2B CSR, DMA AXI-Lite} ----
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_ctrl
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {3}] [get_bd_cells smc_ctrl]
connect_bd_intf_net [get_bd_intf_pins ps7_0/M_AXI_GP0] [get_bd_intf_pins smc_ctrl/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M00_AXI] [get_bd_intf_pins s4d_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M01_AXI] [get_bd_intf_pins infer_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M02_AXI] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]

# ---- 数据面：HP0 ← smartconnect_data(3S/1M) ← {preproc 读, 2B 推理, DMA 写} ----
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_data
set_property -dict [list CONFIG.NUM_SI {3} CONFIG.NUM_MI {1}] [get_bd_cells smc_data]
connect_bd_intf_net [get_bd_intf_pins smc_data/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP0]
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXI_RD] [get_bd_intf_pins smc_data/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins infer_0/M_AXI] [get_bd_intf_pins smc_data/S01_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_dma_0/M_AXI_S2MM] [get_bd_intf_pins smc_data/S02_AXI]

# ---- 输出流：preproc M_AXIS(8b) → 打包器 → DMA S2MM(64b) ----
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXIS] [get_bd_intf_pins pack_0/S_AXIS]
connect_bd_intf_net [get_bd_intf_pins pack_0/M_AXIS] [get_bd_intf_pins axi_dma_0/S_AXIS_S2MM]

# ---- 复位 ----
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_ctrl/aclk]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_data/aclk]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins s4d_0/rstn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins infer_0/cold_resetn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins pack_0/rstn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins smc_ctrl/aresetn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins smc_data/aresetn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins axi_dma_0/axi_resetn]
set_property CONFIG.PROFILE_VISIBILITY_PROVEN {1} [get_bd_cells infer_0]

# ---- 地址（validate 之前） ----
assign_bd_address -offset 0x43C10000 -range 0x00000080 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins s4d_0/S_AXI]]
assign_bd_address -offset 0x43C00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins infer_0/S_AXI]]
assign_bd_address -offset 0x43C20000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins axi_dma_0/S_AXI_LITE]]
foreach ip {s4d_0/M_AXI_RD infer_0/M_AXI axi_dma_0/M_AXI_S2MM} {
    assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces $ip] [get_bd_addr_segs ps7_0/S_AXI_HP0/HP0_DDR_LOWOCM]
}

regenerate_bd_layout
validate_bd_design
save_bd_design
puts "==== P2C BD VALIDATED ===="
foreach seg [get_bd_addr_segs] {
    set off [get_property OFFSET $seg]
    if {$off ne ""} { puts "  [get_property NAME $seg]  offset=$off  range=[get_property RANGE $seg]" }
}
if {!$do_build} {
    puts "==== P2C VALIDATE_ONLY DONE（未综合） ===="
    exit 0
}

# ---- wrapper + 综合/实现 ----
generate_target all [get_files s4d_p2c.bd]
make_wrapper -files [get_files s4d_p2c.bd] -top -import
set_property top s4d_p2c_wrapper [get_filesets sources_1]
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
puts "P2C_SUMMARY WNS=$wns WHS=$whs"
set bits [glob -nocomplain "$out/proj/s4d_p2c.runs/impl_1/*.bit"]
puts "P2C_BITS=$bits"
if {[llength $bits] > 0} { file copy -force [lindex $bits 0] "$out/s4d_p2c.bit"; puts "P2C_BIT_OK" }
write_hw_platform -fixed -force -file "$out/s4d_p2c.xsa"
puts "P2C_XSA_OK"
puts "==== P2C DONE ===="