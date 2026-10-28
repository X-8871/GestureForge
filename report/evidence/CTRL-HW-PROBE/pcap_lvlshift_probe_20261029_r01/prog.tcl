open_hw_manager
connect_hw_server -url localhost:3121
open_hw_target
current_hw_device [lindex [get_hw_devices xc7z020*] 0]
set_property PROGRAM.FILE {D:/FPGA_Competition/w2b/report/evidence/S2B-T19/visibility1_csr_fixed_20261016_r04/artifacts/s2b_inference.bit} [current_hw_device]
program_hw_devices [current_hw_device]
refresh_hw_device -update_hw_probes false [current_hw_device]
puts "PROGRAM_DONE"
close_hw_target
disconnect_hw_server
close_hw_manager
