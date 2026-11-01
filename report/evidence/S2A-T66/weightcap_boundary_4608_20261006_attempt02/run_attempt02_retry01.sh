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
printf 'int main(){}' | g++ -std=c++20 -fcoroutines -x c++ -c -o "$TMPDIR/gxx_temp_probe.o" -
printf 'gxx_coroutines_probe=PASS output=%s/gxx_temp_probe.o\n' "$TMPDIR"
runner_win_path="$(cygpath -w /d/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/run_weightcap_boundary.ps1)"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "$runner_win_path"