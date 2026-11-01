# ============================================================================
# bd_p3r_b6.tcl -- P3r **build6** = build5 + I2C0 两项对齐阶段3
#   改动（仅 2 项）：PCW_I2C_PERIPHERAL_FREQMHZ 111.111115 -> 127.777779
#                   PCW_I2C_RESET_SELECT <Select> -> Share reset pin
#   其余保持 build5：DDR 1GiB(MT41J256M16)、UART0/1、cmos_rst 默认 1、I2C0 EMIO、引脚 F16/F19
#   产物 out/build6/；策略 Performance_ExplorePostRoutePhysOpt、jobs=1
# ============================================================================
# ============================================================================
# bd_p3r_b5.tcl -- P3r **build5** = build4 + PS7 DDR 512MiB -> 1GiB
#   唯一差异：PS7 DDR 参数照抄阶段3（MT41J256M16 RE-125 / 16bit / 4096Mbit / HIGHADDR=0x3FFFFFFF）
#   UART0/1、I2C0-EMIO、cmos_rst 默认 1 均保持 build4；产物 out/build5/
# ============================================================================
# ============================================================================
# bd_p3r_b4.tcl -- P3r **build4**：修 PS7 UART 时钟缺失 + cmos_rst 默认值
#   相对 build3 的差异（仅 BD 参数，无 RTL / 无引脚改动）：
#     1) PS7 补 UART1(MIO48..49,115200) + UART0(MIO46..47,115200)
#        => APER_CLK_CTRL(0xF800012C) bit20(UART0)=1、bit21(UART1)=1
#     2) cmos_rst GPIO C_DOUT_DEFAULT: 0 -> 0x1（复位后默认释放）
#     3) PCW_I2C_RESET_ENABLE: 0 -> 1（与阶段3 对齐）
#   impl 策略沿用 Performance_ExplorePostRoutePhysOpt，jobs=1（避开已知 MCP 插件端口冲突）
#   产物：out/build4/
# ============================================================================
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
set out  "D:/tmp/lead/p3r_camera_20261031_r01/out/build6"
set base "D:/tmp/lead/p3r_camera_20261031_r01"
set do_build [expr {$argc > 0 && [lindex $argv 0] eq "build"}]
file mkdir $out
set part_name "xc7z020clg400-2"

create_project -force s4d_p3r_r01 $out/proj -part $part_name
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
read_verilog "$base/rtl/top_p3r.v"
puts "==== P3Q DISPLAY RTL ADDED ===="

# ---- P3r：相机 IP 厂商仓库（只读引用，不复制、不修改）----
set cam_repo "D:/codex-worktrees/dbdf/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project/my_ip"
if {![file isdirectory $cam_repo]} { error "P3R_ABORT: cam_repo 不存在: $cam_repo" }
set_property ip_repo_paths $cam_repo [current_project]
update_ip_catalog -quiet
puts "P3R_IP_REPO=$cam_repo"
foreach ipn {www.alinx.com.cn:user:alinx_ov5640:5.4} {
    puts "P3R_IP_FOUND=$ipn -> [llength [get_ipdefs -quiet $ipn]]"
}
create_bd_design "s4d_p3r"

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
    CONFIG.PCW_EN_I2C0 {1} \
    CONFIG.PCW_EN_EMIO_I2C0 {1} \
    CONFIG.PCW_I2C0_I2C0_IO {EMIO} \
    CONFIG.PCW_I2C0_PERIPHERAL_ENABLE {1} \
    CONFIG.PCW_I2C0_RESET_ENABLE {0} \
    CONFIG.PCW_I2C_PERIPHERAL_FREQMHZ {127.777779} \
    CONFIG.PCW_I2C_RESET_ENABLE {1} \
    CONFIG.PCW_I2C_RESET_SELECT {Share reset pin} \
    CONFIG.PCW_EN_UART1 {1} \
    CONFIG.PCW_UART1_UART1_IO {MIO 48 .. 49} \
    CONFIG.PCW_UART1_BAUD_RATE {115200} \
    CONFIG.PCW_UART1_PERIPHERAL_ENABLE {1} \
    CONFIG.PCW_EN_EMIO_UART1 {0} \
    CONFIG.PCW_EN_MODEM_UART1 {0} \
    CONFIG.PCW_P2F_UART1_INTR {0} \
    CONFIG.PCW_EN_UART0 {1} \
    CONFIG.PCW_UART0_UART0_IO {MIO 46 .. 47} \
    CONFIG.PCW_UART0_BAUD_RATE {115200} \
    CONFIG.PCW_UART0_PERIPHERAL_ENABLE {1} \
    CONFIG.PCW_EN_EMIO_UART0 {0} \
    CONFIG.PCW_EN_MODEM_UART0 {0} \
    CONFIG.PCW_P2F_UART0_INTR {0} \
] [get_bd_cells ps7_0]

# ============================================================================
# build5：DDR 512MiB -> 1GiB 修正
#   根因：P2d 继承的 PS7 用 MT41J128M8/8bit/1024Mbit => DDR 窗口 0x1FFFFFFF(512MiB)
#         帧存 A/B(0x20000000/0x20384000)、结果块(0x20800000) 越界 => AXI 解码错误 => 数据中止
#   做法：PARTNO 等用户级参数 + 板级/封装延迟 逐项照抄阶段3 冻结 XSA（不估算），
#         显式设 PCW_DDR_RAM_HIGHADDR=0x3FFFFFFF；派生量(容量/位宽/行数/FAW/RC)由 PARTNO 自动决定
# ============================================================================
set_property -dict [list \
    CONFIG.PCW_UIPARAM_DDR_ENABLE {1} \
    CONFIG.PCW_UIPARAM_DDR_PARTNO {MT41J256M16 RE-125} \
    CONFIG.PCW_UIPARAM_DDR_BUS_WIDTH {32 Bit} \
    CONFIG.PCW_UIPARAM_DDR_SPEED_BIN {DDR3_1066F} \
    CONFIG.PCW_UIPARAM_DDR_MEMORY_TYPE {DDR 3} \
    CONFIG.PCW_UIPARAM_DDR_FREQ_MHZ {533.333333} \
    CONFIG.PCW_UIPARAM_DDR_HIGH_TEMP {Normal (0-85)} \
    CONFIG.PCW_UIPARAM_DDR_ECC {Disabled} \
    CONFIG.PCW_UIPARAM_DDR_CL {7} \
    CONFIG.PCW_UIPARAM_DDR_CWL {6} \
    CONFIG.PCW_UIPARAM_DDR_BL {8} \
    CONFIG.PCW_UIPARAM_DDR_AL {0} \
    CONFIG.PCW_UIPARAM_DDR_T_RCD {7} \
    CONFIG.PCW_UIPARAM_DDR_T_RP {7} \
    CONFIG.PCW_UIPARAM_DDR_T_RAS_MIN {35.0} \
    CONFIG.PCW_UIPARAM_DDR_TRAIN_DATA_EYE {1} \
    CONFIG.PCW_UIPARAM_DDR_TRAIN_READ_GATE {1} \
    CONFIG.PCW_UIPARAM_DDR_TRAIN_WRITE_LEVEL {1} \
    CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY0 {0.080} \
    CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY1 {0.063} \
    CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY2 {0.057} \
    CONFIG.PCW_PACKAGE_DDR_BOARD_DELAY3 {0.068} \
    CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_0 {-0.047} \
    CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_1 {-0.025} \
    CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_2 {-0.006} \
    CONFIG.PCW_PACKAGE_DDR_DQS_TO_CLK_DELAY_3 {-0.017} \
    CONFIG.PCW_UIPARAM_DDR_CLOCK_0_PACKAGE_LENGTH {54.563} \
    CONFIG.PCW_UIPARAM_DDR_CLOCK_1_PACKAGE_LENGTH {54.563} \
    CONFIG.PCW_UIPARAM_DDR_CLOCK_2_PACKAGE_LENGTH {54.563} \
    CONFIG.PCW_UIPARAM_DDR_CLOCK_3_PACKAGE_LENGTH {54.563} \
    CONFIG.PCW_UIPARAM_DDR_DQS_0_PACKAGE_LENGTH {101.239} \
    CONFIG.PCW_UIPARAM_DDR_DQS_1_PACKAGE_LENGTH {79.5025} \
    CONFIG.PCW_UIPARAM_DDR_DQS_2_PACKAGE_LENGTH {60.536} \
    CONFIG.PCW_UIPARAM_DDR_DQS_3_PACKAGE_LENGTH {71.7715} \
    CONFIG.PCW_UIPARAM_DDR_DQ_0_PACKAGE_LENGTH {104.5365} \
    CONFIG.PCW_UIPARAM_DDR_DQ_1_PACKAGE_LENGTH {70.676} \
    CONFIG.PCW_UIPARAM_DDR_DQ_2_PACKAGE_LENGTH {59.1615} \
    CONFIG.PCW_UIPARAM_DDR_DQ_3_PACKAGE_LENGTH {81.319} \
    CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY0 {0.25} \
    CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY1 {0.25} \
    CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY2 {0.25} \
    CONFIG.PCW_UIPARAM_DDR_BOARD_DELAY3 {0.25} \
    CONFIG.PCW_UIPARAM_DDR_CLOCK_0_PROPOGATION_DELAY {160} \
    CONFIG.PCW_UIPARAM_DDR_DQS_0_PROPOGATION_DELAY {160} \
    CONFIG.PCW_UIPARAM_DDR_DQ_0_PROPOGATION_DELAY {160} \
    CONFIG.PCW_USE_DDR_BYPASS {0} \
    CONFIG.PCW_DDR_RAM_BASEADDR {0x00100000} \
    CONFIG.PCW_DDR_RAM_HIGHADDR {0x3FFFFFFF}
] [get_bd_cells ps7_0]
foreach kn {CONFIG.PCW_UIPARAM_DDR_PARTNO CONFIG.PCW_UIPARAM_DDR_DEVICE_CAPACITY CONFIG.PCW_UIPARAM_DDR_DRAM_WIDTH CONFIG.PCW_UIPARAM_DDR_ROW_ADDR_COUNT CONFIG.PCW_DDR_RAM_HIGHADDR} {
    puts "P3R5_CHECK $kn = [get_property $kn [get_bd_cells ps7_0]]"
}

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
# （P3r）显示 MM2S 不再直连 pc_hp2，改为与采集 S2MM 一起经 smc_vis 合并，见下方采集段
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


# ============================================================================
# P3r 新增：**相机采集通路**（DVP -> alinx_ov5640 -> AXIS16(RGB565) -> subset(24bit RGB888) -> VDMA S2MM -> HP2）
#   依据：阶段3 冻结 XSA 1f5b138e… 内 .hwh 的 axi_vdma_1 / axis_subset_converter_0 参数（逐项照抄）
#   SCCB：PS7 I2C0 经 EMIO 出 PL（SDA=F16 / SCL=F19），沿用阶段3 驱动
#   PCLK->ACLK 跨域在 alinx_ov5640 IP 内部（BUFFER_DEPTH=4096），无需额外异步 FIFO
# ============================================================================
# 相机采集 IP（厂商打包 IP，DEBUG_OV5640=false 关闭内嵌 ILA，避免 >5 probe 许可限制）
create_bd_cell -type ip -vlnv www.alinx.com.cn:user:alinx_ov5640:5.4 alinx_ov5640_0
set_property -dict [list CONFIG.DEBUG_OV5640 {false} CONFIG.BUFFER_DEPTH {4096}] [get_bd_cells alinx_ov5640_0]

# RGB565(16b) -> RGB888(24b) 展开（与阶段3 逐字相同的 TDATA_REMAP；DDR 内存序 B,G,R）
create_bd_cell -type ip -vlnv xilinx.com:ip:axis_subset_converter:1.1 axis_subset_converter_0
set_property -dict [list \
    CONFIG.M_HAS_TKEEP {1} \
    CONFIG.M_HAS_TLAST {1} \
    CONFIG.M_TDATA_NUM_BYTES {3} \
    CONFIG.M_TUSER_WIDTH {1} \
    CONFIG.S_HAS_TKEEP {1} \
    CONFIG.S_HAS_TLAST {1} \
    CONFIG.S_TDATA_NUM_BYTES {2} \
    CONFIG.S_TUSER_WIDTH {1} \
    CONFIG.TDATA_REMAP {tdata[4:0],3'b000,tdata[10:5],2'b00,tdata[15:11],3'b000} \
    CONFIG.TKEEP_REMAP {1'b1,tkeep[1:0]} \
    CONFIG.TLAST_REMAP {tlast[0]} \
    CONFIG.TUSER_REMAP {tuser[0:0]} \
] [get_bd_cells axis_subset_converter_0]

# 采集 VDMA（S2MM，非 SG；参数逐项照抄阶段3 冻结 XSA 的 axi_vdma_1）
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vdma:6.3 axi_vdma_1
set_property -dict [list \
    CONFIG.c_include_sg {0} \
    CONFIG.c_include_mm2s {0} \
    CONFIG.c_include_s2mm {1} \
    CONFIG.c_include_s2mm_dre {1} \
    CONFIG.c_m_axi_s2mm_data_width {64} \
    CONFIG.c_num_fstores {1} \
    CONFIG.c_use_s2mm_fsync {2} \
    CONFIG.c_s2mm_genlock_mode {0} \
    CONFIG.c_s2mm_linebuffer_depth {4096} \
    CONFIG.c_s2mm_max_burst_length {128} \
] [get_bd_cells axi_vdma_1]

# 显示 MM2S + 采集 S2MM 合并到 HP2（2S/1M），复用已有 pc_hp2(AXI4->AXI3)
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_vis
set_property -dict [list CONFIG.NUM_SI {2} CONFIG.NUM_MI {1}] [get_bd_cells smc_vis]
connect_bd_intf_net [get_bd_intf_pins vdma_0/M_AXI_MM2S]      [get_bd_intf_pins smc_vis/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_vdma_1/M_AXI_S2MM]  [get_bd_intf_pins smc_vis/S01_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_vis/M00_AXI]        [get_bd_intf_pins pc_hp2/S_AXI]
connect_bd_intf_net [get_bd_intf_pins pc_hp2/M_AXI]           [get_bd_intf_pins ps7_0/S_AXI_HP2]

# 相机轴流链路
connect_bd_intf_net [get_bd_intf_pins alinx_ov5640_0/m_axis_video]      [get_bd_intf_pins axis_subset_converter_0/S_AXIS]
connect_bd_intf_net [get_bd_intf_pins axis_subset_converter_0/M_AXIS] [get_bd_intf_pins axi_vdma_1/S_AXIS_S2MM]

# 相机复位（GPIO 输出 1bit -> cmos_rstn，阶段3 同地址 0x41200000）
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio cmos_rst
set_property -dict [list \
    CONFIG.C_GPIO_WIDTH {1} \
    CONFIG.C_ALL_OUTPUTS {1} \
    CONFIG.C_GPIO2_WIDTH {1} \
    CONFIG.C_IS_DUAL {0} \
    CONFIG.C_DOUT_DEFAULT {0x00000001} \
] [get_bd_cells cmos_rst]
puts "P3R4_CMOS_RST_DOUT_DEFAULT=[get_property CONFIG.C_DOUT_DEFAULT [get_bd_cells cmos_rst]]"

# 相机状态/帧计数 GPIO（双通道输入：ch1=采集帧数, ch2=VDMA S2MM 当前帧指针）
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio gpio_cam
set_property -dict [list \
    CONFIG.C_GPIO_WIDTH {32} \
    CONFIG.C_ALL_INPUTS {1} \
    CONFIG.C_IS_DUAL {1} \
    CONFIG.C_GPIO2_WIDTH {32} \
    CONFIG.C_ALL_INPUTS_2 {1} \
] [get_bd_cells gpio_cam]

# ---- DVP / SCCB / 状态 外部端口 ----
create_bd_port -dir I -from 9 -to 0 cmos1_d
create_bd_port -dir I cmos1_href
create_bd_port -dir I cmos1_vsync
create_bd_port -dir I -type clk -freq_hz 84000000 cmos1_pclk
connect_bd_net [get_bd_ports cmos1_d]     [get_bd_pins alinx_ov5640_0/cmos_d]
connect_bd_net [get_bd_ports cmos1_href]  [get_bd_pins alinx_ov5640_0/cmos_href]
connect_bd_net [get_bd_ports cmos1_vsync] [get_bd_pins alinx_ov5640_0/cmos_vsync]
connect_bd_net [get_bd_ports cmos1_pclk]  [get_bd_pins alinx_ov5640_0/cmos_pclk]

# SCCB：PS7 I2C0(EMIO) -> 外部 IIC 端口（沿用阶段3 的 PS I2C 软件路径）
set cam_i2c [create_bd_intf_port -mode Master -vlnv xilinx.com:interface:iic_rtl:1.0 cmos1_i2c]
connect_bd_intf_net [get_bd_intf_ports cmos1_i2c] [get_bd_intf_pins ps7_0/IIC_0]

create_bd_port -dir O cmos_rstn
connect_bd_net [get_bd_ports cmos_rstn] [get_bd_pins cmos_rst/gpio_io_o]

# 采集帧数（RTL 计数 AO/ tuser=SOF）与 VDMA 帧指针 -> GPIO
create_bd_port -dir O -type clk -freq_hz 100000000 clk_100
connect_bd_net [get_bd_ports clk_100] [get_bd_pins ps7_0/FCLK_CLK1]
create_bd_port -dir O cam_sof
connect_bd_net [get_bd_ports cam_sof] [get_bd_pins axis_subset_converter_0/m_axis_tuser]
create_bd_port -dir O -from 4 -to 0 cam_frmptr
connect_bd_net [get_bd_ports cam_frmptr] [get_bd_pins axi_vdma_1/s2mm_frame_ptr_out]
create_bd_port -dir I -from 31 -to 0 cam_sof_cnt
create_bd_port -dir I -from 31 -to 0 cam_frmptr32
connect_bd_net [get_bd_ports cam_sof_cnt]   [get_bd_pins gpio_cam/gpio_io_i]
connect_bd_net [get_bd_ports cam_frmptr32]  [get_bd_pins gpio_cam/gpio2_io_i]

# ---- 采集域时钟（与显示数据面同为 FCLK1=100 MHz）----
foreach p [get_bd_pins -quiet {alinx_ov5640_0/m_axis_video_aclk axis_subset_converter_0/aclk \
        axi_vdma_1/m_axi_s2mm_aclk axi_vdma_1/s_axis_s2mm_aclk smc_vis/aclk}] {
    connect_bd_net [get_bd_pins ps7_0/FCLK_CLK1] $p
}
# 控制面（AXI-Lite）留在 FCLK0=50 MHz，与 smc_ctrl 同域
foreach p [get_bd_pins -quiet {axi_vdma_1/s_axi_lite_aclk cmos_rst/s_axi_aclk gpio_cam/s_axi_aclk}] {
    connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] $p
}
# 复位
connect_bd_net [get_bd_pins rst_100/peripheral_aresetn] [get_bd_pins alinx_ov5640_0/m_axis_video_aresetn]
connect_bd_net [get_bd_pins rst_100/peripheral_aresetn] [get_bd_pins smc_vis/aresetn]
# subset converter 的 aresetn 在阶段3 用常量 1（AXIS 无状态）
create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant const_1
connect_bd_net [get_bd_pins const_1/dout] [get_bd_pins axis_subset_converter_0/aresetn]

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
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {8}] [get_bd_cells smc_ctrl]
connect_bd_intf_net [get_bd_intf_pins ps7_0/M_AXI_GP0] [get_bd_intf_pins smc_ctrl/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M00_AXI] [get_bd_intf_pins s4d_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M01_AXI] [get_bd_intf_pins infer_0/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M02_AXI] [get_bd_intf_pins axi_dma_0/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M03_AXI] [get_bd_intf_pins vdma_0/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M04_AXI] [get_bd_intf_pins gpio_uf/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M05_AXI] [get_bd_intf_pins axi_vdma_1/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M06_AXI] [get_bd_intf_pins gpio_cam/S_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M07_AXI] [get_bd_intf_pins cmos_rst/S_AXI]

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
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins axi_vdma_1/axi_resetn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins cmos_rst/s_axi_aresetn]
connect_bd_net [get_bd_pins rst_all/peripheral_aresetn] [get_bd_pins gpio_cam/s_axi_aresetn]
connect_bd_net [get_bd_pins rst_100/peripheral_aresetn] [get_bd_pins pc_hp2/aresetn]
set_property CONFIG.PROFILE_VISIBILITY_PROVEN {1} [get_bd_cells infer_0]

# ---- 地址（validate 之前） ----
assign_bd_address -offset 0x43C10000 -range 0x00000080 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins s4d_0/S_AXI]]
assign_bd_address -offset 0x43C00000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins infer_0/S_AXI]]
assign_bd_address -offset 0x43C20000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins axi_dma_0/S_AXI_LITE]]
# P3r 相机采集地址（不与既有 43C0/1/2/4/5 冲突）
assign_bd_address -offset 0x43C60000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins axi_vdma_1/S_AXI_LITE]]
assign_bd_address -offset 0x43C70000 -range 0x00001000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins gpio_cam/S_AXI]]
assign_bd_address -offset 0x41200000 -range 0x00010000 -target_address_space [get_bd_addr_spaces ps7_0/Data] [get_bd_addr_segs -of_objects [get_bd_intf_pins cmos_rst/S_AXI]]
assign_bd_address -offset 0x00000000 -range 0x40000000 -target_address_space [get_bd_addr_spaces -of_objects [get_bd_intf_pins axi_vdma_1/M_AXI_S2MM]] [get_bd_addr_segs ps7_0/S_AXI_HP2/HP2_DDR_LOWOCM]
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
generate_target all [get_files s4d_p3r.bd]
make_wrapper -files [get_files s4d_p3r.bd] -top -import
set_property top top_p3r [get_filesets sources_1]
read_xdc "$base/p3r.xdc"
read_xdc "$base/p3r_cdc.xdc"
update_compile_order -fileset sources_1
launch_runs synth_1 -jobs 1
wait_on_run synth_1
if {[get_property PROGRESS [get_runs synth_1]] ne "100%"} { error "SYNTH_FAILED" }
set_property STEPS.WRITE_BITSTREAM.ARGS.BIN_FILE true [get_runs impl_1]
set_property strategy Performance_ExplorePostRoutePhysOpt [get_runs impl_1]
puts "P3R4_IMPL_STRATEGY=[get_property strategy [get_runs impl_1]]"
launch_runs impl_1 -to_step write_bitstream -jobs 1
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} { error "IMPL_FAILED" }
open_run impl_1
report_timing_summary -delay_type min_max -max_paths 10 -file "$out/timing_route.rpt"
report_utilization -file "$out/util_route.rpt"
set wns [get_property SLACK [get_timing_paths -delay_type max -max_paths 1 -nworst 1]]
set whs [get_property SLACK [get_timing_paths -delay_type min -max_paths 1 -nworst 1]]
puts "P3Q_SUMMARY WNS=$wns WHS=$whs"
set bits [glob -nocomplain "$out/proj/s4d_p3r_r01.runs/impl_1/*.bit"]
puts "P3Q_BITS=$bits"
if {[llength $bits] > 0} { file copy -force [lindex $bits 0] "$out/s4d_p3r_r01.bit"; puts "P3Q_BIT_OK" }
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

write_hw_platform -fixed -force -file "$out/s4d_p3r_r01.xsa"
puts "P3Q_XSA_OK"
puts "==== P3Q DONE ===="