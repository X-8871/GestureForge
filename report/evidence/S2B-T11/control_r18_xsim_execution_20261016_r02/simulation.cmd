@echo off
call "D:\Xilinx\2026.1\Vivado\bin\xsim.bat" tb_s2b_control_csr_behav -key {Behavioral:sim_1:Functional:tb_s2b_control_csr} -tclbatch tb_s2b_control_csr.tcl -log simulate.log
set "NATIVE_RC=%errorlevel%"
> "D:\FPGA_Competition\w2b\tmp\2B\S2B-T11\control_r18_xsim_execution_20261016_r02\native_exit_simulation.txt" echo %NATIVE_RC%
exit /b %NATIVE_RC%
