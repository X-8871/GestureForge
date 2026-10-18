set fh [open "D:/tmp/vivado_test/license_probe.txt" w]
puts $fh "VIVADO=[version -short]"
if {[info exists ::env(XILINXD_LICENSE_FILE)]} { puts $fh "XILINXD_LICENSE_FILE=$::env(XILINXD_LICENSE_FILE)" } else { puts $fh "XILINXD_LICENSE_FILE=<unset>" }
read_verilog D:/FPGA_Competition/src/counter.sv
if {[catch {synth_design -top counter -part xc7z020clg400-2 -mode out_of_context} err]} {
    puts $fh "SYNTH_FAIL: $err"
} else {
    puts $fh "SYNTH_OK cells=[llength [get_cells -hier]] nets=[llength [get_nets]]"
    puts $fh "PART=[get_property PART [current_design]]"
}
close $fh
puts "PROBE_DONE"
exit