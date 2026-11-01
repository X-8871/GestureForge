@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "_RDI_CWD=%cd%"
pushd "%~dp0"
> "D:\FPGA_Competition\w2b\report\evidence\S2B-T17\direct_bitgen_fixture_cmd_batch_fixture_20261015T193839Z_3688ab90\cwd_after_pushd.receipt" echo(%cd%
cd /d "%_RDI_CWD%"
> "D:\FPGA_Competition\w2b\report\evidence\S2B-T17\direct_bitgen_fixture_cmd_batch_fixture_20261015T193839Z_3688ab90\cwd_after_restore.receipt" echo(%cd%
> "D:\FPGA_Competition\w2b\report\evidence\S2B-T17\direct_bitgen_fixture_cmd_batch_fixture_20261015T193839Z_3688ab90\batch_args.receipt" echo(%*
"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe" -c "import time; time.sleep(0.8)"
popd
> "D:\FPGA_Competition\w2b\report\evidence\S2B-T17\direct_bitgen_fixture_cmd_batch_fixture_20261015T193839Z_3688ab90\cwd_after_popd.receipt" echo(%cd%
exit /b 37
