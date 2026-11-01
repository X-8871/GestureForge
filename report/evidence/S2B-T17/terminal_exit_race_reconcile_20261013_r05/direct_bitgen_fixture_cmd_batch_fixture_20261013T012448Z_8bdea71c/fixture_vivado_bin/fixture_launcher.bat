@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "_RDI_CWD=%cd%"
pushd "%~dp0"
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\terminal_exit_race_reconcile_20261013_r05\direct_bitgen_fixture_cmd_batch_fixture_20261013T012448Z_8bdea71c\cwd_after_pushd.receipt" echo(%cd%
cd /d "%_RDI_CWD%"
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\terminal_exit_race_reconcile_20261013_r05\direct_bitgen_fixture_cmd_batch_fixture_20261013T012448Z_8bdea71c\cwd_after_restore.receipt" echo(%cd%
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\terminal_exit_race_reconcile_20261013_r05\direct_bitgen_fixture_cmd_batch_fixture_20261013T012448Z_8bdea71c\batch_args.receipt" echo(%*
"C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe" -c "import time; time.sleep(0.8)"
popd
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\terminal_exit_race_reconcile_20261013_r05\direct_bitgen_fixture_cmd_batch_fixture_20261013T012448Z_8bdea71c\cwd_after_popd.receipt" echo(%cd%
exit /b 37
