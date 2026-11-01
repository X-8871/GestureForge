# probe_ila.tcl —— 探测 system_ila 在 IPI 中的监视引脚命名（不建工程产物，仅内存 BD）
create_project -in_memory -part xc7z020clg400-2
create_bd_design probe_bd

create_bd_cell -type ip -vlnv xilinx.com:ip:system_ila:1.1 ila_probe
puts "P3R_ILA_DEFAULT_INTFPINS: [get_bd_intf_pins -quiet ila_probe/*]"
puts "P3R_ILA_DEFAULT_PINS: [get_bd_pins -quiet ila_probe/*]"

set r1 [catch {set_property -dict [list CONFIG.C_NUM_MONITOR_SLOTS {2}] [get_bd_cells ila_probe]} e1]
puts "P3R_ILA_SLOTS_SET: rc=$r1 $e1"

set r2 [catch {set_property -dict [list \
    CONFIG.C_SLOT_0_INTF_TYPE {xilinx.com:interface:aximm_rtl:1.0} \
    CONFIG.C_SLOT_1_INTF_TYPE {xilinx.com:interface:axis_rtl:1.0} \
] [get_bd_cells ila_probe]} e2]
puts "P3R_ILA_TYPE_SET: rc=$r2 $e2"

puts "P3R_ILA_INTFPINS: [get_bd_intf_pins -quiet ila_probe/*]"
puts "P3R_ILA_PINS: [get_bd_pins -quiet ila_probe/*]"
puts "P3R_ILA_SLOT0_PROP: [get_property -quiet CONFIG.C_SLOT_0_INTF_TYPE [get_bd_cells ila_probe]]"
puts "P3R_ILA_SLOT1_PROP: [get_property -quiet CONFIG.C_SLOT_1_INTF_TYPE [get_bd_cells ila_probe]]"
puts "P3R_ILA_DATA_DEPTH: [get_property -quiet CONFIG.C_DATA_DEPTH [get_bd_cells ila_probe]]"
close_bd_design [current_bd_design]
puts "P3R_ILA_PROBE_DONE"