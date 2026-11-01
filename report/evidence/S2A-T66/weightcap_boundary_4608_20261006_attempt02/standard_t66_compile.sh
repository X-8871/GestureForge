#!/usr/bin/env bash
set -euo pipefail
export HOME="$(cygpath -u "$HOME")"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export TMPDIR="$(cygpath -u "$TMPDIR")"
printf 'TMP=%s\nTEMP=%s\nTMPDIR=%s\nHOME=%s\n' "$TMP" "$TEMP" "$TMPDIR" "$HOME"
printf 'uname_path=%s\n' "$(command -v uname)"
printf 'gxx_path=%s\n' "$(command -v g++)"
uname -a
g++ --version
pwsh_path=/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe
runner_path="$(cygpath -w /d/FPGA_Competition/verification/run_s2a_t66_candidate_blackbox.ps1)"
printf 'powershell7_path=%s\nrunner_path=%s\n' "$pwsh_path" "$runner_path"
"$pwsh_path" -NoLogo -NoProfile -File "$runner_path" -CompileOnly