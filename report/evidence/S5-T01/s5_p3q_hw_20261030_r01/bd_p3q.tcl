# bd_p3q.tcl -- 阶段5（HDMI 显示链）/ 任务 S5-T01 / **P3q：计算集成体 + 显示链**
#
# RunId: s5_p3q_build_20261030_r01
#
# ============================================================================
# P3q = **P2d 计算集成体（完全不动）** + **P3n/P3p 显示链（并到 HP2）**
#
# 保留 P2d 全部现状（严格）：
#   - 2B 推理核 M_AXI **直连 S_AXI_HP0**（不经 SmartConnect，P2b 实测慢 1.82x 的教训）
#   - preproc 读 + AXI DMA 写 经 smc_data(2S/1M) -> S_AXI_HP1
#   - 既有地址：2B CSR 0x43C00000、preproc 0x43C10000（range 0x80）、AXI DMA 0x43C20000
#   - FCLK0=50 MHz、打包器 8->64b、DMA 23-bit 长度
#
# 新增（显示路径）：
#   - VDMA(MM2S-only / 非 SG / 2 frame store / 具备 fsync 能力) -> axi_protocol_converter(AXI4->AXI3)
#     -> S_AXI_HP2；**删除 VTC 与 v_axi4s_vid_out**（P3g/P3h 已证明它们不出时序）
#   - 地址：VDMA AXI-Lite **0x43C40000**、underflow GPIO **0x43C50000**
#     （GPIO 双通道：ch1=本帧欠载像素数 @+0x00，ch2=累计 @+0x08）
#   - smc_ctrl 由 1S/3M 扩为 **1S/5M**（M03=VDMA Lite、M04=GPIO；M00~M02 原样）
#   - 时钟：VDMA MM/HP2/转换器 = **FCLK1 100 MHz**；VDMA Lite = FCLK0 50 MHz（与 smc_ctrl 同域）；
#           流侧 = pixel_clk（RTL 内 MMCM 原语产生，74.21875 MHz）；新增 rst_100
#   - RTL：MMCME2_ADV(50->74.21875/371.09375)+locked、自写 axis_to_video(720p60 全正极性)、rgb2dvi_wrap
#   - TMDS 引脚 N18/V20/T20/N20（_n 由工具推断）、hdmi_oen=V16=1、sys_clk=U18
#
# 风险（如实记录，不优化掩盖）：
#   P2d 数据面（HP0/HP1）与显示（HP2）并发时 DDR 带宽需复测；若 2B 推理 47,287 ms 因显示并发变慢，
#   在本报告"未验证项"里如实记录。
#
# 边界：不上板、不烧 QSPI、不 git；不改 P2d/P3a/P3b/P3c/P3d/P3e/P3f/P3g/P3h/P3k/P3m/P3n/P3p 目录。
# ============================================================================

set root "D:/tmp/lead/p2c_20261029_r02/src"
set out  "D:/tmp/lead/p3q_video_20261030_r01/out"
set base "D:/tmp/lead/p3q_video_20261030_r01"
set do_build [expr {$argc > 0 && [lindex $argv 0] eq "build"}]
file mkdir $out
set part_name "xc7z020clg400-2"

create_project -force s4d_p3q_r01 $out/proj -part $part_name
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

# ---- P3q 显示链 RTL：厂商 rgb2dvi（7 个 VHDL，逐字节复制）+ 固定 generic 薄封装 + 自写时序/顶层 ----
foreach f {DVI_Constants SyncAsync SyncAsyncReset ClockGen TMDS_Encoder OutputSERDES rgb2dvi} {
    read_vhdl "$base/src/rgb2dvi/$f.vhd"
}
read_vhdl    "$base/rtl/rgb2dvi_wrap.vhd"
read_verilog "$base/rtl/axis_to_video.v"
read_verilog "$base/rtl/top_p3q.v"
puts "==== P3Q DISPLAY RTL ADDED ===="

create_bd_design "s4d_p3q"

# ---- PS7：FCLK0 50 MHz、GP0、HP0/HP1 各 64bit（2B 用 HP0，preproc+DMA 用 HP1） ----
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7 ps7_0
set_property -dict [list \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {50} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64} \
    CONFIG.PCW_USE_S_AXI_HP1 {1} \
    CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {64} \
    CONFIG.PCW_FPGA1_PERIPHERAL_FREQMHZ {100} \
    CONFIG.PCW_EN_CLK1_PORT {1} \
    CONFIG.PCW_CLK1_FREQ {100000000} \
    CONFIG.PCW_USE_CR_FABRIC {1} \
    CONFIG.PCW_USE_S_AXI_HP2 {1} \
    CONFIG.PCW_S_AXI_HP2_DATA_WIDTH {64} \
] [get_bd_cells ps7_0]
# P3q：显示数据面用 FCLK1=100 MHz（P3n/P3p 实证的有效配置）
set fclk1_act [get_property CONFIG.PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ [get_bd_cells ps7_0]]
puts "P3Q_FCLK1_ACT=$fclk1_act MHz"
if {[expr {abs(double($fclk1_act) - 100.0)}] > 0.01} {
    error "P3Q_ABORT: FCLK1 actual $fclk1_act MHz != 100 MHz"
}
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/FIXED_IO]

# ---- PL 从设备 + 打包器 + DMA ----
create_bd_cell -type module -reference s4d_preproc_v2_wrap s4d_0
# P2c：源图基址由 RTL 参数给出（默认 0 = 与冻结 TB 基线一致），此处覆盖为 ABI raw_frame
set_property -dict [list CONFIG.SRC_BASE {32'h12000000}] [get_bd_cells s4d_0]
puts "P3Q_SRC_BASE_BD=[get_property CONFIG.SRC_BASE [get_bd_cells s4d_0]]"
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
    CONFIG.c_sg_length_width {23} \
    CONFIG.c_addr_width {32} \
] [get_bd_cells axi_dma_0]


# ============================================================================
# P3q 新增：**显示路径**（沿用 P3n/P3p 已验证结构，并到 HP2）
#   VDMA(MM2S-only/非SG/2 frame store/fsync 能力) -> 协议转换器(AXI4->AXI3) -> S_AXI_HP2
#   控制面：VDMA AXI-Lite @0x43C40000、underflow GPIO @0x43C50000（挂在 smc_ctrl 上）
#   时钟：VDMA MM/HP2/转换器 = FCLK1(100 MHz)；VDMA Lite = FCLK0(50)；流侧 = pixel_clk(RTL MMCM)
# ============================================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vdma vdma_0
set_property -dict [list \
    CONFIG.c_include_sg {0} \
    CONFIG.c_include_mm2s {1} \
    CONFIG.c_include_s2mm {0} \
    CONFIG.c_m_axi_mm2s_data_width {64} \
    CONFIG.c_m_axis_mm2s_tdata_width {32} \
    CONFIG.c_addr_width {32} \
    CONFIG.c_num_fstores {2} \
    CONFIG.c_use_fsync {1} \
    CONFIG.c_use_mm2s_fsync {1} \
] [get_bd_cells vdma_0]

# 显示数据面：AXI4(VDMA MM) -> AXI3(PS7 HP) 最小协议转换器（P3f/P3n 已验证）
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_protocol_converter pc_hp2
set_property -dict [list \
    CONFIG.SI_PROTOCOL {AXI4} \
    CONFIG.MI_PROTOCOL {AXI3} \
    CONFIG.READ_WRITE_MODE {READ_ONLY} \
    CONFIG.DATA_WIDTH {64} \
    CONFIG.ADDR_WIDTH {32} \
] [get_bd_cells pc_hp2]
connect_bd_intf_net [get_bd_intf_pins vdma_0/M_AXI_MM2S] [get_bd_intf_pins pc_hp2/S_AXI]
connect_bd_intf_net [get_bd_intf_pins pc_hp2/M_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP2]

# underflow 双通道只读 GPIO（ch1=本帧欠载像素数 @+0x00，ch2=累计 @+0x04）
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio gpio_uf
set_property -dict [list \
    CONFIG.C_GPIO_WIDTH {32} \
    CONFIG.C_ALL_INPUTS {1} \
    CONFIG.C_IS_DUAL {1} \
    CONFIG.C_GPIO2_WIDTH {32} \
    CONFIG.C_ALL_INPUTS_2 {1} \
] [get_bd_cells gpio_uf]

# 100 MHz 域复位（显示数据面）
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_100
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK1]     [get_bd_pins rst_100/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_100/ext_reset_in]

# 外部端口（给 RTL 的 axis_to_video / MMCM / 诊断计数）
create_bd_port -dir I -type clk -freq_hz 74218750 pixel_clk
connect_bd_net [get_bd_ports pixel_clk] [get_bd_pins vdma_0/m_axis_mm2s_aclk]

create_bd_port -dir O -type clk -freq_hz 50000000 clk_50
connect_bd_net [get_bd_ports clk_50] [get_bd_pins ps7_0/FCLK_CLK0]

create_bd_port -dir O -from 31 -to 0 m_axis_tdata
create_bd_port -dir O              m_axis_tvalid
create_bd_port -dir O              m_axis_tlast
create_bd_port -dir I              m_axis_tready
connect_bd_net [get_bd_ports m_axis_tdata]  [get_bd_pins vdma_0/m_axis_mm2s_tdata]
connect_bd_net [get_bd_ports m_axis_tvalid] [get_bd_pins vdma_0/m_axis_mm2s_tvalid]
connect_bd_net [get_bd_ports m_axis_tlast]  [get_bd_pins vdma_0/m_axis_mm2s_tlast]
connect_bd_net [get_bd_ports m_axis_tready] [get_bd_pins vdma_0/m_axis_mm2s_tready]

# ★ VDMA frame sync：显示侧 vsync（RTL 的 axis_to_video.vs）
create_bd_port -dir I mm2s_fsync
connect_bd_net [get_bd_ports mm2s_fsync] [get_bd_pins vdma_0/mm2s_fsync]

create_bd_port -dir I -from 31 -to 0 uf_frame
create_bd_port -dir I -from 31 -to 0 uf_total
connect_bd_net [get_bd_ports uf_frame] [get_bd_pins gpio_uf/gpio_io_i]
connect_bd_net [get_bd_ports uf_total] [get_bd_pins gpio_uf/gpio2_io_i]

# ---- 复位同步 ----
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_all
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]     [get_bd_pins rst_all/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_all/ext_reset_in]

# ---- 时钟 ----
foreach p [get_bd_pins -quiet {ps7_0/M_AXI_GP0_ACLK ps7_0/S_AXI_HP0_ACLK ps7_0/S_AXI_HP1_ACLK s4d_0/clk infer_0/clk pack_0/clk axi_dma_0/*aclk* \
        vdma_0/s_axi_lite_aclk gpio_uf/s_axi_aclk}] {
    connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] $p
}
# P3q 显示数据面：100 MHz（VDMA MM 侧 / HP2 / 协议转换器同域）
foreach p [get_bd_pins -quiet {ps7_0/S_AXI_HP2_ACLK pc_hp2/aclk vdma_0/m_axi_mm2s_aclk}] {
    connect_bd_net [get_bd_pins ps7_0/FCLK_CLK1] $p
}

# ---- 控制面：GP0 → smartconnect_ctrl(1S/3M) → {preproc CSR, 2B CSR, DMA AXI-Lite} ----
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_ctrl
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {5}] [get_bd_cells smc_ctrl]
connect_bd_intf_net [get_bd_intf_pins ps7_0/M_AXI_GP0] [get_bd_intf_pins smc_ctrl/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M00_AXI] [get_bd_intf_pins s4d_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M01_AXI] [get_bd_intf_pins infer_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M02_AXI] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M03_AXI] [get_bd_intf_pins vdma_0/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M04_AXI] [get_bd_intf_pins gpio_uf/S_AXI]

# ---- 数据面（方向 A）：2B 推理核 **直连 HP0**；preproc 读 + DMA 写 经 smc_data(2S/1M) → HP1 ----
connect_bd_intf_net [get_bd_intf_pins infer_0/M_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP0]
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_data
set_property -dict [list CONFIG.NUM_SI {2} CONFIG.NUM_MI {1}] [get_bd_cells smc_data]
connect_bd_intf_net [get_bd_intf_pins smc_data/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP1]
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXI_RD] [get_bd_intf_pins smc_data/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_dma_0/M_AXI_S2MM] [get_bd_intf_pins smc_data/S01_AXI]

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
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins vdma_0/axi_resetn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins gpio_uf/s_axi_aresetn]
connect_bd_net [get_bd_pins rst_100/peripheral_aresetn] [get_bd_pins pc_hp2/aresetn]
set_property CONFIG.PROFILE_VISIBILITY_PROVEN {1} [get_bd_cells infer_0]

# ---- 地址（validate 之前） ----
assign_bd_address -offset 0x43C10000 -range 0x00000080 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins s4d_0/S_AXI]]
assign_bd_address -offset 0x43C00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins infer_0/S_AXI]]
assign_bd_address -offset 0x43C20000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins axi_dma_0/S_AXI_LITE]]
# P3q 显示链地址（与 P2d 既有 43C00000/1/2 不冲突）
assign_bd_address -offset 0x43C40000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins vdma_0/S_AXI_LITE]]
assign_bd_address -offset 0x43C50000 -range 0x00001000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins gpio_uf/S_AXI]]
# VDMA 读帧：HP2 的 DDR 段
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces -of_objects [get_bd_intf_pins vdma_0/M_AXI_MM2S]] [get_bd_addr_segs ps7_0/S_AXI_HP2/HP2_DDR_LOWOCM]
# 2B 推理核：直连 HP0 的 DDR 段
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces infer_0/M_AXI] [get_bd_addr_segs ps7_0/S_AXI_HP0/HP0_DDR_LOWOCM]
# preproc 读 / DMA 写：HP1 的 DDR 段（同一块 DDR，只是物理端口不同）
foreach ip {s4d_0/M_AXI_RD axi_dma_0/M_AXI_S2MM} {
    assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces $ip] [get_bd_addr_segs ps7_0/S_AXI_HP1/HP1_DDR_LOWOCM]
}

regenerate_bd_layout
validate_bd_design
save_bd_design
puts "==== P3Q BD VALIDATED ===="
foreach seg [get_bd_addr_segs] {
    set off [get_property OFFSET $seg]
    if {$off ne ""} { puts "  [get_property NAME $seg]  offset=$off  range=[get_property RANGE $seg]" }
}
if {!$do_build} {
    puts "==== P3Q VALIDATE_ONLY DONE（未综合） ===="
    exit 0
}

# ---- wrapper + 综合/实现 ----
generate_target all [get_files s4d_p3q.bd]
make_wrapper -files [get_files s4d_p3q.bd] -top -import
set_property top top_p3q [get_filesets sources_1]
read_xdc "$base/p3q.xdc"
read_xdc "$base/p3q_cdc.xdc"
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
puts "P3Q_SUMMARY WNS=$wns WHS=$whs"
set bits [glob -nocomplain "$out/proj/s4d_p3q_r01.runs/impl_1/*.bit"]
puts "P3Q_BITS=$bits"
if {[llength $bits] > 0} { file copy -force [lindex $bits 0] "$out/s4d_p3q_r01.bit"; puts "P3Q_BIT_OK" }
report_drc               -file "$out/drc_route.rpt"
report_io                -file "$out/io_route.rpt"
report_clocks            -file "$out/clocks_route.rpt"
report_clock_utilization -file "$out/clk_util_route.rpt"

set f2 [open "$out/drc_route.rpt" r]
foreach ln [split [read $f2] "\n"] {
    if {[string match "*Checks found*" $ln]} { puts "P3Q_DRC: [string trim $ln]" }
}
close $f2
foreach pn {sys_clk TMDS_clk_p TMDS_clk_n TMDS_data_p[0] TMDS_data_n[0] TMDS_data_p[1] TMDS_data_n[1] TMDS_data_p[2] TMDS_data_n[2] hdmi_oen} {
    set pt [get_ports -quiet $pn]
    if {[llength $pt] == 0} { continue }
    set loc "<none>"; set io "<none>"
    catch {set loc [get_property PACKAGE_PIN $pt]}
    catch {set io  [get_property IOSTANDARD  $pt]}
    puts "P3Q_PIN [format %-16s $pn] PACKAGE_PIN=$loc IOSTANDARD=$io"
}
foreach ck [get_clocks -quiet -include_generated_clocks] {
    set per ""; catch {set per [get_property PERIOD $ck]}
    puts "P3Q_CLOCK [get_property NAME $ck] PERIOD=$per"
}

write_hw_platform -fixed -force -file "$out/s4d_p3q_r01.xsa"
puts "P3Q_XSA_OK"
puts "==== P3Q DONE ===="