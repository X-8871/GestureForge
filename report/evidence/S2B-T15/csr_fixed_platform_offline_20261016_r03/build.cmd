@echo off
call "D:\Xilinx\2026.1\Vitis\bin\vitis.bat" -s "D:\FPGA_Competition\w2b\vitis\build_s2b_inference.py"
exit /b %errorlevel%
