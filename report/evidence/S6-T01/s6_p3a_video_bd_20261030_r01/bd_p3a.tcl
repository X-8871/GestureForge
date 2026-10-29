# bd_p3a.tcl —— 阶段6 P3a：视频输出通路 BD（纯输出，无叠加、无 TMDS）
#
# 基线：P2d 合并体（PS7 + smc_ctrl(1S/3M) + 2B 推理核直连 HP0 + preproc + 打包器 + AXI DMA/HP1）
# 本脚本在其上追加一条**纯视频输出通路**（G0 冻结，2026-10-30）：
#   PS7 追加 FCLK1=100 MHz、S_AXI_HP2(64b)、fabric IRQ(1 bit)
#     -> clk_wiz: 100 MHz 入，clk_out1=74.25 MHz(像素) / clk_out2=371.25 MHz(串行/预留)
#     -> v_tc 6.2: 1280x720p60 时序(占 0x43C30000)，generation-only，AXI4-Lite 使能
#     -> axi_vdma 6.3: 只开 MM2S、非 SG、MM 64b / 流侧 32b(RGBA 承载 RGB888)，M_AXI_MM2S -> HP2
#     -> v_axi4s_vid_out 4.0: 32b 流 -> vid_io_out 原生 32b(RGBA)，xlslice 裁到 vid_data[23:0]
#     -> 视频相关 AXI-Lite(VDMA 0x43C40000) 挂在 smc_ctrl 上，smc_ctrl 由 1S/3M 扩到 1S/5M
#
# 时钟域：
#   50 MHz(FCLK0)  : 控制面 / 原 P2d 全部逻辑 / VDMA 的 s_axi_lite_aclk 与 m_axi_mm2s_aclk
#   100 MHz(FCLK1) : clk_wiz 参考输入
#   74.21875 MHz   : 像素域（v_tc clk、vid_out aclk、VDMA m_axis_mm2s_aclk），由 rst_pix 单独复位
#
# 用法：
#   vivado -mode batch -source bd_p3a.tcl                    -> 建 BD + validate + save（约 3 分钟）
#   vivado -mode batch -source bd_p3a.tcl -tclargs gen        -> 追加 generate_target + wrapper（仍不综合）
#   vivado -mode batch -source bd_p3a.tcl -tclargs build      -> synth+impl（本任务不执行）
#
# 边界：本脚本不做综合/实现/上板；不改 P2d 目录与厂商原件；不 git 提交。

set root "D:/tmp/lead/p2c_20261029_r02/src"
set w2b  "D:/FPGA_Competition/w2b"
set base "D:/tmp/lead/p3a_video_20261030_r01"
set out  "$base/out"
set mode "validate"
set do_wrapper 0
set do_build 0
if {$argc > 0} {
    set mode [lindex $argv 0]
    if {$mode eq "gen"}   { set do_wrapper 1 }
    if {$mode eq "build"} { set do_wrapper 1 ; set do_build 1 }
}
file mkdir $out
set part_name "xc7z020clg400-2"

puts "==== P3A MODE=$mode ===="
create_project -force s4d_p3a_r01 $out/proj -part $part_name
set_property target_language Verilog [current_project]
set_property include_dirs "$root/rtl" [get_filesets sources_1]

# ============================================================
# 1) RTL（与 P2d 完全一致，只为 module reference 提供定义）
# ============================================================
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
foreach rel [list \
    src/s2a_network_descriptor_pkg.sv src/s2b_maxpool_geometry.sv src/int8_maxpool_window.sv \
    src/s2b_route_query.sv src/int8_upsample_query.sv src/s2b_conv_tile_engine.sv \
    src/s2b_maxpool_engine.sv src/s2b_route_engine.sv src/s2b_upsample_engine.sv \
    src/s2b_network_backend.sv src/s2a_memory_master.sv src/s2a_runtime_shell.sv \
    src/s2b_stage2b_core.sv src/s2a_control_csr.sv src/s2b_request_guard.sv \
    src/s2b_hp0_word_adapter.sv src/s2b_control_csr.sv src/s2b_inference_top.sv ] {
    read_verilog -sv "$w2b/$rel"
}
set_property top s4d_preproc_v2_wrap [get_filesets sources_1]
update_compile_order -fileset sources_1

create_bd_design "s4d_p3a"

# ============================================================
# 2) PS7：FCLK0=50 / FCLK1=100、GP0、HP0/HP1/HP2 各 64b、fabric IRQ 1 bit
# ============================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7 ps7_0
set_property -dict [list \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {50} \
    CONFIG.PCW_FPGA1_PERIPHERAL_FREQMHZ {100} \
    CONFIG.PCW_EN_CLK0_PORT {1} \
    CONFIG.PCW_EN_CLK1_PORT {1} \
    CONFIG.PCW_CLK0_FREQ {50000000} \
    CONFIG.PCW_CLK1_FREQ {100000000} \
    CONFIG.PCW_USE_CR_FABRIC {1} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64} \
    CONFIG.PCW_USE_S_AXI_HP1 {1} \
    CONFIG.PCW_S_AXI_HP1_DATA_WIDTH {64} \
    CONFIG.PCW_USE_S_AXI_HP2 {1} \
    CONFIG.PCW_S_AXI_HP2_DATA_WIDTH {64} \
    CONFIG.PCW_USE_FABRIC_INTERRUPT {1} \
    CONFIG.PCW_IRQ_F2P_INTR {1} \
] [get_bd_cells ps7_0]
# 2026.1 实测：FCLK_CLK1 端口的真实门控是 (PCW_EN_CLK1_PORT==1 && PCW_USE_CR_FABRIC==1)，
# 频率由 PCW_CLK1_FREQ(H, 单位 Hz) 决定；PCW_FPGA1_PERIPHERAL_FREQMHZ 只是 MHz 镜像。
# 仅设 PCW_FPGA1_PERIPHERAL_FREQMHZ 不会生成 FCLK_CLK1 引脚（默认 EN_CLK1_PORT=0）。
set fclk1_act [get_property CONFIG.PCW_ACT_FPGA1_PERIPHERAL_FREQMHZ [get_bd_cells ps7_0]]
puts "P3A_FCLK0_ACT=[get_property CONFIG.PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ [get_bd_cells ps7_0]] MHz"
puts "P3A_FCLK1_ENABLE=[get_property CONFIG.PCW_FPGA_FCLK1_ENABLE [get_bd_cells ps7_0]]"
puts "P3A_FCLK1_ACT=$fclk1_act MHz"
if {[expr {abs(double($fclk1_act) - 100.0)}] > 0.01} {
    error "P3A_ABORT: FCLK1 actual $fclk1_act MHz != 100 MHz (PS7 FCLK config not applied)"
}
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/FIXED_IO]

# ============================================================
# 3) 原 P2d 逻辑：preproc / 2B 推理核 / 打包器 / AXI DMA（功能与地址均不变）
# ============================================================
create_bd_cell -type module -reference s4d_preproc_v2_wrap s4d_0
set_property -dict [list CONFIG.SRC_BASE {32'h12000000}] [get_bd_cells s4d_0]
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

# ============================================================
# 4) 视频输出通路（本阶段新增）
# ============================================================
# 4.1 像素时钟 / 串行时钟：100 MHz 参考，厂商已验证 MMCM 原始参数
create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0
set_property -dict [list \
    CONFIG.PRIM_SOURCE {Single_ended_clock_capable_pin} \
    CONFIG.PRIM_IN_FREQ {100.000} \
    CONFIG.CLKOUT1_USED {true} \
    CONFIG.CLKOUT2_USED {true} \
    CONFIG.NUM_OUT_CLKS {2} \
    CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {74.25} \
    CONFIG.CLKOUT2_REQUESTED_OUT_FREQ {371.25} \
    CONFIG.CLKOUT1_DRIVES {BUFG} \
    CONFIG.CLKOUT2_DRIVES {BUFG} \
    CONFIG.USE_LOCKED {true} \
    CONFIG.USE_RESET {true} \
    CONFIG.OVERRIDE_MMCM {true} \
    CONFIG.MMCM_CLKIN1_PERIOD {10.000} \
    CONFIG.MMCM_DIVCLK_DIVIDE {8} \
    CONFIG.MMCM_CLKFBOUT_MULT_F {59.375} \
    CONFIG.MMCM_CLKOUT0_DIVIDE_F {10.000} \
    CONFIG.MMCM_CLKOUT1_DIVIDE {2} \
] [get_bd_cells clk_wiz_0]

# 4.2 VTC：1280x720p60，generation-only（detection 关闭，减少悬空输入）
create_bd_cell -type ip -vlnv xilinx.com:ip:v_tc vtc_0
set_property -dict [list \
    CONFIG.VIDEO_MODE {720p} \
    CONFIG.HAS_AXI4_LITE {true} \
    CONFIG.HAS_INTC_IF {false} \
    CONFIG.enable_generation {true} \
    CONFIG.enable_detection {false} \
    CONFIG.GEN_VIDEO_FORMAT {RGB} \
    CONFIG.GEN_INTERLACED {false} \
    CONFIG.GEN_FIELDID_EN {false} \
    CONFIG.GEN_HACTIVE_SIZE {1280} \
    CONFIG.GEN_HFRAME_SIZE {1650} \
    CONFIG.GEN_HSYNC_START {1390} \
    CONFIG.GEN_HSYNC_END {1430} \
    CONFIG.GEN_VACTIVE_SIZE {720} \
    CONFIG.GEN_F0_VFRAME_SIZE {750} \
    CONFIG.GEN_F0_VSYNC_VSTART {724} \
    CONFIG.GEN_F0_VSYNC_VEND {729} \
    CONFIG.GEN_F1_VFRAME_SIZE {750} \
    CONFIG.GEN_F1_VSYNC_VSTART {724} \
    CONFIG.GEN_F1_VSYNC_VEND {729} \
    CONFIG.GEN_HSYNC_POLARITY {High} \
    CONFIG.GEN_VSYNC_POLARITY {High} \
    CONFIG.GEN_AVIDEO_POLARITY {High} \
    CONFIG.GEN_HBLANK_POLARITY {High} \
    CONFIG.GEN_VBLANK_POLARITY {High} \
    CONFIG.max_clocks_per_line {4096} \
    CONFIG.max_lines_per_frame {4096} \
] [get_bd_cells vtc_0]

# 4.3 VDMA：只开 MM2S、非 SG；MM 侧 64b，流侧 32b（RGBA 承载 RGB888）
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vdma vdma_0
set_property -dict [list \
    CONFIG.c_include_sg {0} \
    CONFIG.c_include_mm2s {1} \
    CONFIG.c_include_s2mm {0} \
    CONFIG.c_m_axi_mm2s_data_width {64} \
    CONFIG.c_m_axis_mm2s_tdata_width {32} \
    CONFIG.c_addr_width {32} \
    CONFIG.c_use_fsync {0} \
] [get_bd_cells vdma_0]
# c_sg_length_width：2026.1 的 axi_vdma 6.3 在 c_include_sg=0 时不暴露该参数
# （实测 set_property 触发 CRITICAL WARNING [BD 41-1276] Parameter does not exist），故不设置；
# 非 SG 简单模式下传输长度由 DA/LENGTH 寄存器直接给出，不需要 SG 长度位宽。记录于报告。

# 4.4 AXI4-Stream -> Video Out：输入 RGBA(4 分量 x8b = 32b)，slave 模式跟 VTC 时序
create_bd_cell -type ip -vlnv xilinx.com:ip:v_axi4s_vid_out vidout_0
set_property -dict [list \
    CONFIG.C_S_AXIS_VIDEO_FORMAT {6} \
    CONFIG.C_PIXELS_PER_CLOCK {1} \
    CONFIG.C_S_AXIS_VIDEO_DATA_WIDTH {8} \
    CONFIG.C_NATIVE_COMPONENT_WIDTH {8} \
    CONFIG.C_HAS_ASYNC_CLK {0} \
    CONFIG.C_VTG_MASTER_SLAVE {0} \
    CONFIG.C_ADDR_WIDTH {10} \
    CONFIG.C_HYSTERESIS_LEVEL {12} \
] [get_bd_cells vidout_0]

# 4.5 32b 原生视频 -> 24b（砍掉 alpha 字节），得到 vid_data[23:0]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 vid_slice
set_property -dict [list \
    CONFIG.DIN_WIDTH {32} \
    CONFIG.DIN_FROM {23} \
    CONFIG.DIN_TO {0} \
    CONFIG.DOUT_WIDTH {24} \
] [get_bd_cells vid_slice]

# ============================================================
# 5) 复位与常量
# ============================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_all
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]     [get_bd_pins rst_all/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_all/ext_reset_in]

# 像素域复位：与 rst_all 同源，但同步到像素时钟（IPI 常规做法，异步断言/同步释放）
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_pix
connect_bd_net [get_bd_pins clk_wiz_0/clk_out1]  [get_bd_pins rst_pix/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_pix/ext_reset_in]

create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant const_1
set_property -dict [list CONFIG.CONST_WIDTH {1} CONFIG.CONST_VAL {1}] [get_bd_cells const_1]
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant const_0
set_property -dict [list CONFIG.CONST_WIDTH {1} CONFIG.CONST_VAL {0}] [get_bd_cells const_0]

# ============================================================
# 6) 时钟网络
# ============================================================
# 50 MHz：控制面 + 原 P2d 全部 + VDMA 的 AXI-Lite / AXI-MM
foreach p [get_bd_pins -quiet {ps7_0/M_AXI_GP0_ACLK ps7_0/S_AXI_HP0_ACLK ps7_0/S_AXI_HP1_ACLK ps7_0/S_AXI_HP2_ACLK \
        s4d_0/clk infer_0/clk pack_0/clk axi_dma_0/*aclk* smc_ctrl/aclk smc_data/aclk \
        vtc_0/s_axi_aclk vdma_0/s_axi_lite_aclk vdma_0/m_axi_mm2s_aclk}] {
    connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] $p
}
# 100 MHz：clk_wiz 参考
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK1] [get_bd_pins clk_wiz_0/clk_in1]
# 74.21875 MHz 像素域
foreach p [get_bd_pins -quiet {vtc_0/clk vidout_0/aclk vdma_0/m_axis_mm2s_aclk}] {
    connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] $p
}
# clk_wiz 复位（高有效）用 50 MHz 域的 peripheral_reset
connect_bd_net [get_bd_pins rst_all/peripheral_reset] [get_bd_pins clk_wiz_0/reset]

# ============================================================
# 7) 控制面：GP0 -> smc_ctrl(1S/5M) -> {2B CSR, preproc CSR, DMA, VTC, VDMA}
# ============================================================
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_ctrl
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {5}] [get_bd_cells smc_ctrl]
connect_bd_intf_net [get_bd_intf_pins ps7_0/M_AXI_GP0] [get_bd_intf_pins smc_ctrl/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M00_AXI] [get_bd_intf_pins s4d_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M01_AXI] [get_bd_intf_pins infer_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M02_AXI] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M03_AXI] [get_bd_intf_pins vtc_0/ctrl]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M04_AXI] [get_bd_intf_pins vdma_0/S_AXI_LITE]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_ctrl/aclk]

# ============================================================
# 8) 数据面
# ============================================================
# 原 P2d：2B 推理核直连 HP0；preproc 读 + DMA 写经 smc_data(2S/1M) -> HP1
connect_bd_intf_net [get_bd_intf_pins infer_0/M_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP0]
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_data
set_property -dict [list CONFIG.NUM_SI {2} CONFIG.NUM_MI {1}] [get_bd_cells smc_data]
connect_bd_intf_net [get_bd_intf_pins smc_data/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP1]
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXI_RD] [get_bd_intf_pins smc_data/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_dma_0/M_AXI_S2MM] [get_bd_intf_pins smc_data/S01_AXI]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_data/aclk]

# 新增：VDMA 读端口单独占 HP2（不与 HP0/HP1 混）。
# VDMA 的 M_AXI_MM2S 是 AXI4，PS7 的 S_AXI_HP 是 AXI3，必须经 smartconnect 做协议转换
# （HP0/HP1 同理，P2d 已由 smc_data 承担）。
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_vid
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] [get_bd_cells smc_vid]
connect_bd_intf_net [get_bd_intf_pins vdma_0/M_AXI_MM2S] [get_bd_intf_pins smc_vid/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_vid/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP2]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins smc_vid/aclk]

# 原 P2d 输出流：preproc M_AXIS(8b) -> 打包器 -> DMA S2MM(64b)
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXIS] [get_bd_intf_pins pack_0/S_AXIS]
connect_bd_intf_net [get_bd_intf_pins pack_0/M_AXIS] [get_bd_intf_pins axi_dma_0/S_AXIS_S2MM]

# 新增视频流：VDMA MM2S(32b) -> vid_out(32b RGBA) ；VTC 时序 -> vid_out(slave)
connect_bd_intf_net [get_bd_intf_pins vdma_0/M_AXIS_MM2S] [get_bd_intf_pins vidout_0/video_in]
connect_bd_intf_net [get_bd_intf_pins vtc_0/vtiming_out]  [get_bd_intf_pins vidout_0/vtiming_in]

# ============================================================
# 9) 复位网络
# ============================================================
foreach p [get_bd_pins -quiet {s4d_0/rstn infer_0/cold_resetn pack_0/rstn smc_ctrl/aresetn smc_data/aresetn smc_vid/aresetn \
        axi_dma_0/axi_resetn vtc_0/s_axi_aresetn vdma_0/axi_resetn}] {
    connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] $p
}
connect_bd_net [get_bd_pins rst_pix/peripheral_aresetn] [get_bd_pins vtc_0/resetn]
connect_bd_net [get_bd_pins rst_pix/peripheral_aresetn] [get_bd_pins vidout_0/aresetn]

# ============================================================
# 10) 常量 / 使能 / 时序握手
# ============================================================
connect_bd_net [get_bd_pins const_1/dout] [get_bd_pins vtc_0/clken]
connect_bd_net [get_bd_pins const_1/dout] [get_bd_pins vtc_0/s_axi_aclken]
connect_bd_net [get_bd_pins const_1/dout] [get_bd_pins vidout_0/aclken]
connect_bd_net [get_bd_pins const_1/dout] [get_bd_pins vidout_0/vid_io_out_ce]
connect_bd_net [get_bd_pins const_0/dout] [get_bd_pins vtc_0/fsync_in]
connect_bd_net [get_bd_pins const_0/dout] [get_bd_pins vtc_0/sof_state]
connect_bd_net [get_bd_pins const_0/dout] [get_bd_pins vidout_0/fid]
# slave 模式下由 vid_out 产生 vtg_ce 去驱动 VTC 的 gen_clken
connect_bd_net [get_bd_pins vidout_0/vtg_ce] [get_bd_pins vtc_0/gen_clken]

# 视频数据：32b 原生 -> 24b（丢 alpha）
connect_bd_net [get_bd_pins vidout_0/vid_data] [get_bd_pins vid_slice/Din]

# VDMA MM2S 中断 -> PS7 IRQ_F2P[0]
if {[catch {connect_bd_net [get_bd_pins vdma_0/mm2s_introut] [get_bd_pins ps7_0/IRQ_F2P]} e]} {
    puts "IRQ_F2P direct connect failed, retry [0]: $e"
    connect_bd_net [get_bd_pins vdma_0/mm2s_introut] [get_bd_pins "ps7_0/IRQ_F2P\[0\]"]
}

# ============================================================
# 11) BD 端口（本阶段只引出，不接 TMDS）
# ============================================================
create_bd_port -dir O -type clk pixel_clk
connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_ports pixel_clk]
create_bd_port -dir O vid_hsync
connect_bd_net [get_bd_pins vidout_0/vid_hsync] [get_bd_ports vid_hsync]
create_bd_port -dir O vid_vsync
connect_bd_net [get_bd_pins vidout_0/vid_vsync] [get_bd_ports vid_vsync]
create_bd_port -dir O vid_de
connect_bd_net [get_bd_pins vidout_0/vid_active_video] [get_bd_ports vid_de]
create_bd_port -dir O -from 23 -to 0 vid_data
connect_bd_net [get_bd_pins vid_slice/Dout] [get_bd_ports vid_data]

set_property CONFIG.PROFILE_VISIBILITY_PROVEN {1} [get_bd_cells infer_0]

# ============================================================
# 12) 地址分配（每段 64K，互不重叠；0x43C00000 起连续 5 段）
# ============================================================
assign_bd_address -offset 0x43C10000 -range 0x00000080 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins s4d_0/S_AXI]]
assign_bd_address -offset 0x43C00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins infer_0/S_AXI]]
assign_bd_address -offset 0x43C20000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins axi_dma_0/S_AXI_LITE]]
assign_bd_address -offset 0x43C30000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins vtc_0/ctrl]]
assign_bd_address -offset 0x43C40000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins vdma_0/S_AXI_LITE]]
# 主端 DDR 段
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces -of_objects [get_bd_intf_pins infer_0/M_AXI]] [get_bd_addr_segs ps7_0/S_AXI_HP0/HP0_DDR_LOWOCM]
foreach ip {s4d_0/M_AXI_RD axi_dma_0/M_AXI_S2MM} {
    assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces -of_objects [get_bd_intf_pins $ip]] [get_bd_addr_segs ps7_0/S_AXI_HP1/HP1_DDR_LOWOCM]
}
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces -of_objects [get_bd_intf_pins vdma_0/M_AXI_MM2S]] [get_bd_addr_segs ps7_0/S_AXI_HP2/HP2_DDR_LOWOCM]

# ============================================================
# 13) 布局 / 校验 / 保存
# ============================================================
regenerate_bd_layout
set verr_txt ""
if {[catch {validate_bd_design} verr_txt]} {
    puts "==== VALIDATE THREW: $verr_txt ===="
}
puts "==== P3A BD VALIDATE DONE ===="

# 校验结论说明：Vivado 2026.1 的 get_msg 不返回历史消息（实测 ERROR/CRITICAL/WARNING 全返回 0，
# 但同一运行实际打印了 14 条 WARNING），故本脚本不自行统计，避免给出假的"0 error"。
# validate 结论以本次 console / -log 中 '^ERROR' 与 '^CRITICAL WARNING' 行的计数为准（见 P3A_BD_REPORT.md）。
puts "P3A_VALIDATE_DONE (verdict = count of ^ERROR / ^CRITICAL WARNING lines in this run's log)"
save_bd_design

# ---------- 关键事实读回（写报告用） ----------
set dfp [open "$out/p3a_bd_facts.txt" w]
proc F {fh msg} { puts $msg; puts $fh $msg; flush $fh }

F $dfp "---- clk_wiz_0 ----"
set mult [get_property CONFIG.MMCM_CLKFBOUT_MULT_F  [get_bd_cells clk_wiz_0]]
set ddiv [get_property CONFIG.MMCM_DIVCLK_DIVIDE    [get_bd_cells clk_wiz_0]]
set d0   [get_property CONFIG.MMCM_CLKOUT0_DIVIDE_F [get_bd_cells clk_wiz_0]]
set d1   [get_property CONFIG.MMCM_CLKOUT1_DIVIDE   [get_bd_cells clk_wiz_0]]
set fin  [get_property CONFIG.PRIM_IN_FREQ          [get_bd_cells clk_wiz_0]]
set fvco [expr {double($fin) * double($mult) / double($ddiv)}]
F $dfp "  PRIM_IN_FREQ=$fin MHz  DIVCLK=$ddiv  MULT=$mult  CLKOUT0_DIV_F=$d0  CLKOUT1_DIV=$d1"
F $dfp "  OVERRIDE_MMCM=[get_property CONFIG.OVERRIDE_MMCM [get_bd_cells clk_wiz_0]]"
F $dfp "  VCO=$fvco MHz  clk_out1=[expr {$fvco/double($d0)}] MHz  clk_out2=[expr {$fvco/double($d1)}] MHz"
F $dfp "  CLKOUT1_JITTER=[get_property CONFIG.CLKOUT1_JITTER [get_bd_cells clk_wiz_0]] ps  CLKOUT2_JITTER=[get_property CONFIG.CLKOUT2_JITTER [get_bd_cells clk_wiz_0]] ps"

F $dfp "---- v_tc (vtc_0) ----"
foreach p {VIDEO_MODE VID_PPC GEN_HACTIVE_SIZE GEN_HFRAME_SIZE GEN_HSYNC_START GEN_HSYNC_END \
           GEN_VACTIVE_SIZE GEN_F0_VFRAME_SIZE GEN_F0_VSYNC_VSTART GEN_F0_VSYNC_VEND \
           GEN_HSYNC_POLARITY GEN_VSYNC_POLARITY GEN_AVIDEO_POLARITY \
           HAS_AXI4_LITE enable_generation enable_detection} {
    if {[catch {get_property CONFIG.$p [get_bd_cells vtc_0]} v]} { set v "<none>" }
    F $dfp "  $p = $v"
}

F $dfp "---- axi_vdma (vdma_0) ----"
foreach p {c_include_sg c_include_mm2s c_include_s2mm c_m_axi_mm2s_data_width \
           c_m_axis_mm2s_tdata_width c_addr_width c_use_fsync c_single_interface} {
    if {[catch {get_property CONFIG.$p [get_bd_cells vdma_0]} v]} { set v "<none>" }
    F $dfp "  $p = $v"
}

F $dfp "---- v_axi4s_vid_out (vidout_0) ----"
foreach p {C_S_AXIS_VIDEO_FORMAT C_PIXELS_PER_CLOCK C_S_AXIS_VIDEO_DATA_WIDTH \
           C_NATIVE_COMPONENT_WIDTH C_HAS_ASYNC_CLK C_VTG_MASTER_SLAVE C_ADDR_WIDTH C_HYSTERESIS_LEVEL} {
    if {[catch {get_property CONFIG.$p [get_bd_cells vidout_0]} v]} { set v "<none>" }
    F $dfp "  $p = $v"
}

F $dfp "---- BD PORTS ----"
foreach port [get_bd_ports] {
    set l 0 ; set r 0
    catch {set l [get_property LEFT  $port]}
    catch {set r [get_property RIGHT $port]}
    F $dfp "  [get_property NAME $port]  dir=[get_property DIR $port]  type=[get_property TYPE $port]  bits=\[$l:$r\]"
}

F $dfp "---- VIDEO AXIS WIDTH (TDATA_NUM_BYTES) ----"
foreach ipin {vdma_0/M_AXIS_MM2S vidout_0/video_in vtc_0/vtiming_out vidout_0/vtiming_in} {
    set pin [get_bd_intf_pins $ipin]
    set nb "<none>"
    catch {set nb [get_property CONFIG.TDATA_NUM_BYTES $pin]}
    set t  "<none>"
    catch {set t [get_property CONFIG.TDATA_NUM_BYTES $pin]}
    F $dfp "  $ipin  TYPE=[get_property TYPE $pin]  TDATA_NUM_BYTES=$nb"
}

F $dfp "---- ADDR SEGS ----"
foreach seg [get_bd_addr_segs] {
    set off [get_property OFFSET $seg]
    if {$off ne ""} {
        F $dfp "  [get_property NAME $seg]  offset=$off  range=[get_property RANGE $seg]"
    }
}
close $dfp
puts "==== P3A BD FACTS WRITTEN $out/p3a_bd_facts.txt ===="

# BD 文件副本：out/ 与任务根目录各一份（根目录为交付要求位置）
if {[file exists "$out/proj/s4d_p3a_r01.srcs/sources_1/bd/s4d_p3a/s4d_p3a.bd"]} {
    file copy -force "$out/proj/s4d_p3a_r01.srcs/sources_1/bd/s4d_p3a/s4d_p3a.bd" "$out/bd_p3a.bd"
    file copy -force "$out/proj/s4d_p3a_r01.srcs/sources_1/bd/s4d_p3a/s4d_p3a.bd" "$base/bd_p3a.bd"
    puts "==== BD_COPY_OK ===="
}
catch {write_bd_tcl -force "$out/bd_p3a_generated.tcl"}
puts "==== BD_TCL_EXPORT_DONE ===="

if {!$do_wrapper} {
    puts "==== P3A VALIDATE_ONLY DONE (no synthesis, no wrapper) ===="
    exit 0
}

# ============================================================
# 14) gen/build：生成产物 + wrapper（仍不做综合，除非 build）
# ============================================================
generate_target all [get_files s4d_p3a.bd]
make_wrapper -files [get_files s4d_p3a.bd] -top -import
set_property top s4d_p3a_wrapper [get_filesets sources_1]
update_compile_order -fileset sources_1
puts "==== P3A WRAPPER OK ===="
if {!$do_build} {
    puts "==== P3A GEN DONE (no synthesis) ===="
    exit 0
}

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
write_hw_platform -fixed -force -file "$out/s4d_p3a_r01.xsa"
puts "==== P3A BUILD DONE ===="