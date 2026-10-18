@echo off
set "XILINXD_LICENSE_FILE=D:\Xilinx_licenses\basic_only.lic"
set "TEMP=D:\tmp"
set "TMP=D:\tmp"
cd /d D:\tmp\vivado_test
call "D:\Xilinx\2026.1\Vivado\bin\vivado.bat" -mode batch -nojournal -nolog -source license_probe.tcl > probe_out.txt 2>&1
exit /b %ERRORLEVEL%