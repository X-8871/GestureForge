@echo off
setlocal EnableExtensions DisableDelayedExpansion
"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import hashlib,os,pathlib,sys,time; pathlib.Path(sys.argv[1]).write_text(hashlib.sha256(os.environ['XILINXD_LICENSE_FILE'].encode('utf-8')).hexdigest().upper(), encoding='ascii'); time.sleep(0.25)" "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\review_v2_cmd_launcher_20261013_01\direct_bitgen_fixture_rdi_verbose_redaction_20261012T233730Z_4e8a008b\child_license_env_sha256.receipt"
if /I "%RDI_VERBOSE%"=="True" echo XILINXD_LICENSE_FILE=%XILINXD_LICENSE_FILE%
echo CHILD_RDI_VERBOSE=%RDI_VERBOSE%
exit /b 0
