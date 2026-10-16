@echo off
call "D:\Xilinx\2026.1\Vitis\bin\vitis.bat" -s "D:\FPGA_Competition\w2b\vitis\build_s2b_inference.py"
set "VITIS_RC=%errorlevel%"
> "D:\FPGA_Competition\w2b\report\evidence\S2B-T15\candidate_t13_r02_offline_20261016_r02\native_exit_vitis.txt" echo %VITIS_RC%
exit /b %VITIS_RC%
