@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "_S15_ORIGINAL_CWD=%CD%"
pushd "%~dp0"
set "_S15_BATCH_CWD=%CD%"
for /l %%N in (1,1,20000) do @set "_S15_SPIN=%%N"
cd /d "%_S15_ORIGINAL_CWD%"
"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\direct_bitgen_fixture_cmd_cwd_identity_20261013_e95f4d6746484c82a7373f59a00a3466\initial_cwd_fixture_bin\short_child.py" "C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T17\direct_bitgen_fixture_cmd_cwd_identity_20261013_e95f4d6746484c82a7373f59a00a3466\initial_cwd_fixture_bin\short_child_receipt.json"
set "_S15_CHILD_EXIT=%errorlevel%"
popd
exit /b 37
