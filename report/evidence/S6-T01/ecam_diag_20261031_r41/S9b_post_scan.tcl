connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
if {[catch {stop} e]} { puts "STOP_ERR $e" } else { puts STOP_OK }
if {[catch {loadhw -hw D:/tmp/lead/p3r_camera_20261031_r01/out/build10b2/s4d_p3r_r01.xsa -mem-ranges {0x00000000 0x7FFFFFFF}} e]} { puts "LH_ERR $e" } else { puts LH_OK }
if {[catch {puts "PCV [rrd pc]"} e]} { puts "PC_ERR $e" }
if {[catch {puts "CPSRV [rrd cpsr]"} e]} { puts "CPSR_ERR $e" }
if {[catch {puts "CAM_CR [mrd -value 0x43C60030]"} e]} { puts "CAM_CR_ERR $e" }
if {[catch {puts "CAM_SR [mrd -value 0x43C60034]"} e]} { puts "CAM_SR_ERR $e" }
if {[catch {puts "VSIZE [mrd -value 0x43C600A0]"} e]} { puts "VSIZE_ERR $e" }
if {[catch {puts "HSIZE [mrd -value 0x43C600A4]"} e]} { puts "HSIZE_ERR $e" }
if {[catch {puts "STRIDE [mrd -value 0x43C600A8]"} e]} { puts "STRIDE_ERR $e" }
if {[catch {puts "FRMPTR [mrd -value 0x43C600AC]"} e]} { puts "FRMPTR_ERR $e" }
if {[catch {puts "GPIO_CAM [mrd -value 0x43C70000]"} e]} { puts "GPIO_CAM_ERR $e" }
if {[catch {puts "S2MM_A [mrd -value 0x43CB0000]"} e]} { puts "S2MM_A_ERR $e" }
if {[catch {puts "S2MM_A2 [mrd -value 0x43CB0008]"} e]} { puts "S2MM_A2_ERR $e" }
if {[catch {puts "S2MM_B [mrd -value 0x43CC0000]"} e]} { puts "S2MM_B_ERR $e" }
if {[catch {puts "S2MM_B2 [mrd -value 0x43CC0008]"} e]} { puts "S2MM_B2_ERR $e" }
if {[catch {puts "RAW_head_00 [mrd -value 0x12000000]"} e]} { puts "RAW_head_00_ERR $e" }
if {[catch {puts "RAW_head_01 [mrd -value 0x12000004]"} e]} { puts "RAW_head_01_ERR $e" }
if {[catch {puts "RAW_head_02 [mrd -value 0x12000008]"} e]} { puts "RAW_head_02_ERR $e" }
if {[catch {puts "RAW_head_03 [mrd -value 0x1200000C]"} e]} { puts "RAW_head_03_ERR $e" }
if {[catch {puts "RAW_head_04 [mrd -value 0x12000010]"} e]} { puts "RAW_head_04_ERR $e" }
if {[catch {puts "RAW_head_05 [mrd -value 0x12000014]"} e]} { puts "RAW_head_05_ERR $e" }
if {[catch {puts "RAW_head_06 [mrd -value 0x12000018]"} e]} { puts "RAW_head_06_ERR $e" }
if {[catch {puts "RAW_head_07 [mrd -value 0x1200001C]"} e]} { puts "RAW_head_07_ERR $e" }
if {[catch {puts "RAW_head_08 [mrd -value 0x12000020]"} e]} { puts "RAW_head_08_ERR $e" }
if {[catch {puts "RAW_head_09 [mrd -value 0x12000024]"} e]} { puts "RAW_head_09_ERR $e" }
if {[catch {puts "RAW_head_10 [mrd -value 0x12000028]"} e]} { puts "RAW_head_10_ERR $e" }
if {[catch {puts "RAW_head_11 [mrd -value 0x1200002C]"} e]} { puts "RAW_head_11_ERR $e" }
if {[catch {puts "RAW_head_12 [mrd -value 0x12000030]"} e]} { puts "RAW_head_12_ERR $e" }
if {[catch {puts "RAW_head_13 [mrd -value 0x12000034]"} e]} { puts "RAW_head_13_ERR $e" }
if {[catch {puts "RAW_head_14 [mrd -value 0x12000038]"} e]} { puts "RAW_head_14_ERR $e" }
if {[catch {puts "RAW_head_15 [mrd -value 0x1200003C]"} e]} { puts "RAW_head_15_ERR $e" }
if {[catch {puts "RAW_mid_00 [mrd -value 0x12151800]"} e]} { puts "RAW_mid_00_ERR $e" }
if {[catch {puts "RAW_mid_01 [mrd -value 0x12151804]"} e]} { puts "RAW_mid_01_ERR $e" }
if {[catch {puts "RAW_mid_02 [mrd -value 0x12151808]"} e]} { puts "RAW_mid_02_ERR $e" }
if {[catch {puts "RAW_mid_03 [mrd -value 0x1215180C]"} e]} { puts "RAW_mid_03_ERR $e" }
if {[catch {puts "RAW_mid_04 [mrd -value 0x12151810]"} e]} { puts "RAW_mid_04_ERR $e" }
if {[catch {puts "RAW_mid_05 [mrd -value 0x12151814]"} e]} { puts "RAW_mid_05_ERR $e" }
if {[catch {puts "RAW_mid_06 [mrd -value 0x12151818]"} e]} { puts "RAW_mid_06_ERR $e" }
if {[catch {puts "RAW_mid_07 [mrd -value 0x1215181C]"} e]} { puts "RAW_mid_07_ERR $e" }
if {[catch {puts "RAW_mid_08 [mrd -value 0x12151820]"} e]} { puts "RAW_mid_08_ERR $e" }
if {[catch {puts "RAW_mid_09 [mrd -value 0x12151824]"} e]} { puts "RAW_mid_09_ERR $e" }
if {[catch {puts "RAW_mid_10 [mrd -value 0x12151828]"} e]} { puts "RAW_mid_10_ERR $e" }
if {[catch {puts "RAW_mid_11 [mrd -value 0x1215182C]"} e]} { puts "RAW_mid_11_ERR $e" }
if {[catch {puts "RAW_mid_12 [mrd -value 0x12151830]"} e]} { puts "RAW_mid_12_ERR $e" }
if {[catch {puts "RAW_mid_13 [mrd -value 0x12151834]"} e]} { puts "RAW_mid_13_ERR $e" }
if {[catch {puts "RAW_mid_14 [mrd -value 0x12151838]"} e]} { puts "RAW_mid_14_ERR $e" }
if {[catch {puts "RAW_mid_15 [mrd -value 0x1215183C]"} e]} { puts "RAW_mid_15_ERR $e" }
if {[catch {puts "RAW_last_00 [mrd -value 0x122A2100]"} e]} { puts "RAW_last_00_ERR $e" }
if {[catch {puts "RAW_last_01 [mrd -value 0x122A2104]"} e]} { puts "RAW_last_01_ERR $e" }
if {[catch {puts "RAW_last_02 [mrd -value 0x122A2108]"} e]} { puts "RAW_last_02_ERR $e" }
if {[catch {puts "RAW_last_03 [mrd -value 0x122A210C]"} e]} { puts "RAW_last_03_ERR $e" }
if {[catch {puts "RAW_last_04 [mrd -value 0x122A2110]"} e]} { puts "RAW_last_04_ERR $e" }
if {[catch {puts "RAW_last_05 [mrd -value 0x122A2114]"} e]} { puts "RAW_last_05_ERR $e" }
if {[catch {puts "RAW_last_06 [mrd -value 0x122A2118]"} e]} { puts "RAW_last_06_ERR $e" }
if {[catch {puts "RAW_last_07 [mrd -value 0x122A211C]"} e]} { puts "RAW_last_07_ERR $e" }
if {[catch {puts "RAW_last_08 [mrd -value 0x122A2120]"} e]} { puts "RAW_last_08_ERR $e" }
if {[catch {puts "RAW_last_09 [mrd -value 0x122A2124]"} e]} { puts "RAW_last_09_ERR $e" }
if {[catch {puts "RAW_last_10 [mrd -value 0x122A2128]"} e]} { puts "RAW_last_10_ERR $e" }
if {[catch {puts "RAW_last_11 [mrd -value 0x122A212C]"} e]} { puts "RAW_last_11_ERR $e" }
if {[catch {puts "RAW_last_12 [mrd -value 0x122A2130]"} e]} { puts "RAW_last_12_ERR $e" }
if {[catch {puts "RAW_last_13 [mrd -value 0x122A2134]"} e]} { puts "RAW_last_13_ERR $e" }
if {[catch {puts "RAW_last_14 [mrd -value 0x122A2138]"} e]} { puts "RAW_last_14_ERR $e" }
if {[catch {puts "RAW_last_15 [mrd -value 0x122A213C]"} e]} { puts "RAW_last_15_ERR $e" }
disconnect
exit
