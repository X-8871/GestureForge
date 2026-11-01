connect -url tcp:127.0.0.1:3121
targets -set -filter {name =~ "*Cortex-A9*#0*"}
if {[catch {stop} e]} { puts "STOP_ERR $e" } else { puts STOP_OK }
if {[catch {loadhw -hw D:/tmp/lead/p3r_camera_20261031_r01/out/build10b2/s4d_p3r_r01.xsa -mem-ranges {0x00000000 0x7FFFFFFF}} e]} { puts "LH_ERR $e" } else { puts LH_OK }
if {[catch {puts "CR [mrd -value 0x43C60030]"} e]} { puts "CR_ERR $e" }
if {[catch {puts "SR [mrd -value 0x43C60034]"} e]} { puts "SR_ERR $e" }
if {[catch {puts "CURDESC [mrd -value 0x43C60038]"} e]} { puts "CURDESC_ERR $e" }
if {[catch {puts "S2MM_VSIZE_50 [mrd -value 0x43C60050]"} e]} { puts "S2MM_VSIZE_50_ERR $e" }
if {[catch {puts "S2MM_HSIZE_54 [mrd -value 0x43C60054]"} e]} { puts "S2MM_HSIZE_54_ERR $e" }
if {[catch {puts "S2MM_FRMDLY_58 [mrd -value 0x43C60058]"} e]} { puts "S2MM_FRMDLY_58_ERR $e" }
if {[catch {puts "S2MM_STRIDE_5C [mrd -value 0x43C6005C]"} e]} { puts "S2MM_STRIDE_5C_ERR $e" }
if {[catch {puts "VSIZE_A0 [mrd -value 0x43C600A0]"} e]} { puts "VSIZE_A0_ERR $e" }
if {[catch {puts "HSIZE_A4 [mrd -value 0x43C600A4]"} e]} { puts "HSIZE_A4_ERR $e" }
if {[catch {puts "STRIDE_A8 [mrd -value 0x43C600A8]"} e]} { puts "STRIDE_A8_ERR $e" }
if {[catch {puts "FRMPTR_AC [mrd -value 0x43C600AC]"} e]} { puts "FRMPTR_AC_ERR $e" }
if {[catch {puts "FRMSTORE_B0 [mrd -value 0x43C600B0]"} e]} { puts "FRMSTORE_B0_ERR $e" }
if {[catch {puts "FRMPTR_STS_B4 [mrd -value 0x43C600B4]"} e]} { puts "FRMPTR_STS_B4_ERR $e" }
disconnect
exit
