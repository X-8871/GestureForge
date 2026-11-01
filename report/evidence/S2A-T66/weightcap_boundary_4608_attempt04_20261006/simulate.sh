#!/usr/bin/env bash
set -uo pipefail
export HOME="$(cygpath -u "$HOME")"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export TMPDIR="$(cygpath -u "$TMPDIR")"
simulator=/d/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_attempt04_20261006/build/Vtb_s2a_weightcap_boundary.exe
printf 'simulator_path=%s\n' "$simulator"
set +e
"$simulator"
simulator_exit=$?
set -e
printf 'SIMULATOR_EXIT_CODE=%s\n' "$simulator_exit"
exit "$simulator_exit"
