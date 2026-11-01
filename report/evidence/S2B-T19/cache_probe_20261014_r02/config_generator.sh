#!/usr/bin/env bash
cd /c/Users/22061/.codex/worktrees/96a3/FPGA_Competition
py=/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
script=tmp/2B/S2B-T19/board_prepare_20261013_r01/prepare_visibility_config_pa.py
receipt=C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/report/evidence/S2B-T17/implemented_export_independent_20261014_r01/runtime_compatibility_receipt_r02.json
receipt_local=report/evidence/S2B-T17/implemented_export_independent_20261014_r01/runtime_compatibility_receipt_r02.json
uart=C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/tmp/2B/S2B-T19/board_run_20261014_r02/uart_identity.json
server=C:/Users/22061/.codex/worktrees/96a3/FPGA_Competition/tmp/2B/S2B-T19/board_run_20261014_r02/hw_server_identity.json
out=tmp/2B/S2B-T19/board_run_20261014_r02/config_generate_attempt_r04.stdout.log
err=tmp/2B/S2B-T19/board_run_20261014_r02/config_generate_attempt_r04.stderr.log
config=tmp/2B/S2B-T19/board_prepare_20261013_r01/visibility_config_cache_probe_20261014_r03.json
test -f "$receipt_local" && test ! -e "$out" && test ! -e "$err" && test ! -e "$config" || exit 90
receipt_sha=$(sha256sum "$receipt_local" | cut -d" " -f1)
"$py" -B "$script" generate --compat-receipt "$receipt" --compat-receipt-sha256 "$receipt_sha" --source-commit 7c14ec0a0c8205dabdb4ddb541140ccf20c9c9d9 --uart-identity "$uart" --owned-server-identity "$server" --run-id cache_probe_20261014_r02 --cpu-seed 722665479 --dap-seed 722665480 --response-timeout-seconds 30 --output-name visibility_config_cache_probe_20261014_r03.json >"$out" 2>"$err"
rc=$?
printf 'exit=%s receipt_sha256=%s\nstdout:\n' "$rc" "$receipt_sha"
cat "$out"
printf 'stderr:\n'
cat "$err"
exit "$rc"
