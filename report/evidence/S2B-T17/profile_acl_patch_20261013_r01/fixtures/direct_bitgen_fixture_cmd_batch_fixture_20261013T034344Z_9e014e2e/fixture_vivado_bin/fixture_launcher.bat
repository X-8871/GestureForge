@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "_RDI_CWD=%cd%"
pushd "%~dp0"
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\profile_acl_patch_20261013_r01\fixtures\direct_bitgen_fixture_cmd_batch_fixture_20261013T034344Z_9e014e2e\cwd_after_pushd.receipt" echo(%cd%
cd /d "%_RDI_CWD%"
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\profile_acl_patch_20261013_r01\fixtures\direct_bitgen_fixture_cmd_batch_fixture_20261013T034344Z_9e014e2e\cwd_after_restore.receipt" echo(%cd%
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\profile_acl_patch_20261013_r01\fixtures\direct_bitgen_fixture_cmd_batch_fixture_20261013T034344Z_9e014e2e\batch_args.receipt" echo(%*
"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import time; time.sleep(0.8)"
popd
> "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\profile_acl_patch_20261013_r01\fixtures\direct_bitgen_fixture_cmd_batch_fixture_20261013T034344Z_9e014e2e\cwd_after_popd.receipt" echo(%cd%
exit /b 37
