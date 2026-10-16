@echo off
call "D:\Xilinx\2026.1\Vivado\bin\xvlog.bat" --incr -L uvm -prj tb_s2b_control_csr_vlog.prj -log xvlog.log
set "NATIVE_RC=%errorlevel%"
> "D:\FPGA_Competition\w2b\tmp\2B\S2B-T11\control_r18_independent_20261016_r08\native_exit_compile.txt" echo %NATIVE_RC%
exit /b %NATIVE_RC%
