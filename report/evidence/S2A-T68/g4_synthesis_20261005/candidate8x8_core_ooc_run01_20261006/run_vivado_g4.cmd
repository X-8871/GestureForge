@echo off
call "D:\Xilinx\2026.1\Vivado\bin\vivado.bat" -mode batch -source "D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\candidate8x8_core_ooc_run01_20261006\run_synthesis.tcl" -journal "D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\candidate8x8_core_ooc_run01_20261006\vivado.jou" -log "D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\candidate8x8_core_ooc_run01_20261006\vivado.log"
set "exitCode=%ERRORLEVEL%"
echo %exitCode% > "D:\FPGA_Competition\report\evidence\S2A-T68\g4_synthesis_20261005\candidate8x8_core_ooc_run01_20261006\launcher_exit_code.txt"
exit /b %exitCode%