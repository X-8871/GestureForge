# bd_s4d_preproc_v2.tcl —— 4-D 预处理 v2 的 BD 集成（控制面 + 数据面），只到 validate
#
# 结构：
#   PS7 (FCLK0=100MHz, M_AXI_GP0, S_AXI_HP0)
#     ├─ M_AXI_GP0 → smc_ctrl(1S/1M) → s4d_0/S_AXI      @ 0x43C10000  (AXI4-Lite, 控制)
#     └─ S_AXI_HP0 ← smc_data(1S/1M) ← s4d_0/M_AXI_RD                (AXI4 读, 64bit 数据面)
#   复位：FCLK_RESET0_N → proc_sys_reset → peripheral_aresetn（同步后再分发）
#
# 不做什么：不综合、不实现、不出 bit/XSA；不写 w4/w5 树内文件。
# 运行：vivado -mode batch -nojournal -source bd_s4d_preproc_v2.tcl -log bd_v2/vivado_bd.log

set part_name "xc7z020clg400-2"
set root      "[file normalize {D:/tmp/lead/p2a_20261029_r01/src}]"
set bd_dir    "$root/bd_v2"
if {[info exists ::env(S4D_BD_DIR)]} { set bd_dir $::env(S4D_BD_DIR) }
file mkdir $bd_dir

create_project -force s4d_preproc_v2_bd $bd_dir/s4d_preproc_v2_bd -part $part_name
set_property target_language Verilog [current_project]

# `include "s4d_coord_tables.svh"：该 .svh 必须显式 add_files 进工程（Vivado 要求），
# 否则 module reference 报 filemgmt 56-591
set_property include_dirs "$root/rtl" [get_filesets sources_1]
add_files -fileset sources_1 -norecurse "$root/rtl/s4d_coord_tables.svh"
foreach f [list \
    "$root/rtl/s4d_preproc_csr.sv" \
    "$root/rtl/s4d_preproc_engine_v2.sv" \
    "$root/rtl/s4d_axi4_rd_shim.sv" \
    "$root/rtl/s4d_preproc_out_axis.sv" \
    "$root/rtl/s4d_preproc_v2_wrap.sv" ] {
    read_verilog -sv $f
}
set_property top s4d_preproc_v2_wrap [get_filesets sources_1]
update_compile_order -fileset sources_1

create_bd_design "s4d_preproc_v2"

# ---------------- PS7：100 MHz + GP0 + HP0 ----------------
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7 ps7_0
set_property -dict [list \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
    CONFIG.PCW_USE_S_AXI_HP0 {1} \
    CONFIG.PCW_S_AXI_HP0_DATA_WIDTH {64} \
    CONFIG.PCW_USE_S_AXI_HP1 {0} \
    CONFIG.PCW_USE_S_AXI_HP2 {0} \
    CONFIG.PCW_USE_S_AXI_HP3 {0} \
] [get_bd_cells ps7_0]

make_bd_intf_pins_external [get_bd_intf_pins ps7_0/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7_0/FIXED_IO]

# ---------------- 预处理 v2 ----------------
create_bd_cell -type module -reference s4d_preproc_v2_wrap s4d_0

# ---------------- 复位同步 ----------------
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset rst_s4d
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]     [get_bd_pins rst_s4d/slowest_sync_clk]
connect_bd_net [get_bd_pins ps7_0/FCLK_RESET0_N] [get_bd_pins rst_s4d/ext_reset_in]

# ---------------- 时钟 ----------------
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins ps7_0/M_AXI_GP0_ACLK]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins ps7_0/S_AXI_HP0_ACLK]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0] [get_bd_pins s4d_0/clk]

connect_bd_net [get_bd_pins rst_s4d/peripheral_aresetn] [get_bd_pins s4d_0/rstn]

# ---------------- 控制面：GP0 → S_AXI ----------------
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_ctrl
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] [get_bd_cells smc_ctrl]
connect_bd_intf_net [get_bd_intf_pins ps7_0/M_AXI_GP0] [get_bd_intf_pins smc_ctrl/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_ctrl/M00_AXI] [get_bd_intf_pins s4d_0/S_AXI]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]            [get_bd_pins smc_ctrl/aclk]
connect_bd_net [get_bd_pins rst_s4d/peripheral_aresetn] [get_bd_pins smc_ctrl/aresetn]

# ---------------- 数据面：M_AXI_RD → HP0 ----------------
create_bd_cell -type ip -vlnv xilinx.com:ip:smartconnect smc_data
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] [get_bd_cells smc_data]
connect_bd_intf_net [get_bd_intf_pins s4d_0/M_AXI_RD] [get_bd_intf_pins smc_data/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins smc_data/M00_AXI] [get_bd_intf_pins ps7_0/S_AXI_HP0]
connect_bd_net [get_bd_pins ps7_0/FCLK_CLK0]            [get_bd_pins smc_data/aclk]
connect_bd_net [get_bd_pins rst_s4d/peripheral_aresetn] [get_bd_pins smc_data/aresetn]

# ---------------- 输出流（P2a：内部悬空） ----------------
# P2a 目标 = 验证 PS<->PL 通路与 CSR（长跑根因），不验证输出流。
# 若外引 M_AXIS + 随流时钟，会产生 13 个无引脚约束的顶层端口 -> bitgen DRC NSTD-1/UCIO-1 失败。
# 故本版将 M_AXIS 保持内部悬空；输出流的消费（VDMA/显示）属合并部署（P2b/W-C）。
puts "==== P2A: M_AXIS left internal (output stream not routed to top in this build) ===="

# ---------------- 地址分配（必须在 validate 之前，否则报 BD 41-1356/41-2909） ----------------
set seg_ctrl [get_bd_addr_segs -of_objects [get_bd_intf_pins s4d_0/S_AXI]]
puts "==== CONTROL SEGMENTS: $seg_ctrl ===="
assign_bd_address -offset 0x43C10000 -range 128 \
    -target_address_space [get_bd_addr_spaces ps7_0/Data] $seg_ctrl -force

set spaces [get_bd_addr_spaces -of_objects [get_bd_cells s4d_0]]
puts "==== S4D MASTER SPACES: $spaces ===="
if {[llength $spaces] == 0} { error "wrapper has no master address space; check M_AXI_RD inference" }
set hp_segs [get_bd_addr_segs -of_objects [get_bd_intf_pins ps7_0/S_AXI_HP0]]
puts "==== HP0 SEGMENTS: $hp_segs ===="
assign_bd_address -offset 0x00000000 -range 512M \
    -target_address_space [get_bd_addr_spaces s4d_0/M_AXI_RD] $hp_segs -force


regenerate_bd_layout
validate_bd_design
save_bd_design

puts "==== FINAL ADDRESS MAP ===="
foreach seg [get_bd_addr_segs] {
    set off [get_property OFFSET $seg]
    if {$off ne ""} { puts "  [get_property NAME $seg]  offset=$off  range=[get_property RANGE $seg]" }
}
write_bd_tcl -force "$bd_dir/s4d_preproc_v2_bd.tcl"
puts "==== BD V2 VALIDATED & SAVED ===="
