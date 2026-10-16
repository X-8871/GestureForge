@echo off
call "D:\Xilinx\2026.1\Vivado\bin\xelab.bat" --incr --debug typical --mt off -L xil_defaultlib -L uvm -L unisims_ver -L unimacro_ver -L secureip --snapshot tb_s2b_control_csr_behav xil_defaultlib.tb_s2b_control_csr -log elaborate.log
set "NATIVE_RC=%errorlevel%"
> "D:\FPGA_Competition\w2b\tmp\2B\S2B-T11\control_r18_xsim_epoch_zero_clock_20261016_r06\native_exit_elaborate.txt" echo %NATIVE_RC%
exit /b %NATIVE_RC%
