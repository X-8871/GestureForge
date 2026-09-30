@echo off
setlocal EnableExtensions
set TEMP=D:\FPGA_Competition\report\evidence\S2A-T64\temp
set TMP=%TEMP%
cd /d D:\FPGA_Competition\report\evidence\S2A-T64\sim_run07
if errorlevel 1 (echo CHDIR_FAIL > status.txt & exit /b 90)
call "D:\Xilinx\2026.1\Vivado\bin\xvlog.bat" -sv -work xil_defaultlib "D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv" "D:\FPGA_Competition\src\int8_conv_tap_geometry.sv" "D:\FPGA_Competition\src\int8_conv_weight_address.sv" "D:\FPGA_Competition\src\int8_mac_accumulator.sv" "D:\FPGA_Competition\src\int8_maxpool_geometry.sv" "D:\FPGA_Competition\src\int8_maxpool_window.sv" "D:\FPGA_Competition\src\int8_route_query.sv" "D:\FPGA_Competition\src\int8_upsample_query.sv" "D:\FPGA_Competition\src\s2a_conv_engine.sv" "D:\FPGA_Competition\src\s2a_maxpool_engine.sv" "D:\FPGA_Competition\src\s2a_route_engine.sv" "D:\FPGA_Competition\src\s2a_upsample_engine.sv" "D:\FPGA_Competition\src\s2a_control_csr.sv" "D:\FPGA_Competition\src\s2a_network_backend.sv" "D:\FPGA_Competition\sim\tb_s2a_network_backend_csr_deadline.sv" > xvlog_console.txt 2>&1
if errorlevel 1 (echo XVLOG_EXIT_FAIL > status.txt & exit /b 91)
if not exist xvlog.log (echo XVLOG_LOG_MISSING > status.txt & exit /b 91)
findstr /i /c:"ERROR:" /c:"FATAL:" xvlog.log >nul
if not errorlevel 1 (echo XVLOG_LOG_FAIL > status.txt & exit /b 91)
call "D:\Xilinx\2026.1\Vivado\bin\xelab.bat" -mt off -debug typical xil_defaultlib.tb_s2a_network_backend_csr_deadline -s s2a_t64_deadline_snapshot > xelab_console.txt 2>&1
if errorlevel 1 (echo XELAB_EXIT_FAIL > status.txt & exit /b 92)
if not exist xelab.log (echo XELAB_LOG_MISSING > status.txt & exit /b 92)
findstr /i /c:"ERROR:" /c:"FATAL:" xelab.log >nul
if not errorlevel 1 (echo XELAB_LOG_FAIL > status.txt & exit /b 92)
if not exist xsim.dir\s2a_t64_deadline_snapshot\xsimk.exe (echo SNAPSHOT_MISSING > status.txt & exit /b 92)
call "D:\Xilinx\2026.1\Vivado\bin\xsim.bat" s2a_t64_deadline_snapshot -R > xsim_console.txt 2>&1
if errorlevel 1 (echo XSIM_EXIT_FAIL > status.txt & exit /b 93)
if not exist xsim.log (echo XSIM_LOG_MISSING > status.txt & exit /b 93)
findstr /i /c:"ERROR:" /c:"FATAL:" xsim.log >nul
if not errorlevel 1 (echo XSIM_LOG_FAIL > status.txt & exit /b 93)
findstr /i /c:"PASS: backend/CSR deadline" xsim.log >nul
if errorlevel 1 (echo PASS_MARKER_MISSING > status.txt & exit /b 94)
echo PASS > status.txt
exit /b 0