@echo off
setlocal EnableExtensions DisableDelayedExpansion
"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe" -c "import hashlib,os,pathlib,sys,time; pathlib.Path(sys.argv[1]).write_text(hashlib.sha256(os.environ['XILINXD_LICENSE_FILE'].encode('utf-8')).hexdigest().upper(), encoding='ascii'); time.sleep(0.25)" "D:\FPGA_Competition\w2b\report\evidence\S2B-T17\direct_bitgen_fixture_rdi_verbose_redaction_20261015T231715Z_2241c8d0\child_license_env_sha256.receipt"
if /I "%RDI_VERBOSE%"=="True" echo XILINXD_LICENSE_FILE=%XILINXD_LICENSE_FILE%
echo CHILD_RDI_VERBOSE=%RDI_VERBOSE%
exit /b 0
