# probe_axi_pins.tcl —— 验证 IPI 是否能访问 AXI 接口内部子信号（用于 5 探针 ILA 方案）
create_project -in_memory -part xc7z020clg400-2
create_bd_design probe2

create_bd_cell -type ip -vlnv xilinx.com:ip:axi_vdma:6.3 vdma_probe
set_property -dict [list CONFIG.c_include_mm2s {0} CONFIG.c_include_s2mm {1} CONFIG.c_include_sg {0}] [get_bd_cells vdma_probe]

puts "P3R_AXI_SUBPIN1: [get_bd_pins -quiet vdma_probe/M_AXI_S2MM_awvalid]"
puts "P3R_AXI_SUBPIN2: [get_bd_pins -quiet -filter {NAME =~ *awvalid*} vdma_probe/*]"
puts "P3R_AXI_SUBPIN3: [get_bd_intf_pins -quiet vdma_probe/M_AXI_S2MM]"
puts "P3R_ALL_PINS_COUNT: [llength [get_bd_pins -quiet vdma_probe/*]]"

# 尝试给 ila（原生，非 system_ila）设置 5 个探针
create_bd_cell -type ip -vlnv xilinx.com:ip:ila:6.2 ila_probe
set r1 [catch {set_property -dict [list CONFIG.C_NUM_OF_PROBES {5} CONFIG.C_DATA_DEPTH {8192} CONFIG.C_TRIGIN_EN {false} CONFIG.C_EN_STRG_QUAL {false}] [get_bd_cells ila_probe]} e1]
puts "P3R_ILA5_SET: rc=$r1 $e1"
puts "P3R_ILA5_PINS: [get_bd_pins -quiet ila_probe/*]"
close_bd_design [current_bd_design]
puts "P3R_AXI_PROBE_DONE"