@echo off
set "TEMP=D:\tmp"
set "TMP=D:\tmp"
set "PATH=D:\Xilinx\2026.1\Vivado\bin;%PATH%"
if not exist D:\tmp\vivado_test\simrun mkdir D:\tmp\vivado_test\simrun
cd /d D:\tmp\vivado_test\simrun
echo === xvlog ===
call xvlog.bat -sv D:/FPGA_Competition/src/counter.sv D:/FPGA_Competition/sim/tb_counter.sv
echo XVLOG_EXIT=%ERRORLEVEL%
echo === xelab ===
call xelab.bat tb_counter -debug typical -s tb_counter_sim
echo XELAB_EXIT=%ERRORLEVEL%
echo === xsim ===
call xsim.bat tb_counter_sim -runall
echo XSIM_EXIT=%ERRORLEVEL%
exit /b 0