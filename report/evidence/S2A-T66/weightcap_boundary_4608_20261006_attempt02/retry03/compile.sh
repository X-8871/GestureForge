#!/usr/bin/env bash
set -uo pipefail
export HOME="$(cygpath -u "$HOME")"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export TMPDIR="$(cygpath -u "$TMPDIR")"
export VERILATOR_ROOT=/d/FPGA_S2A_MSYS2_20261001/env/mingw64/share/verilator
printf 'TMP=%s\nTEMP=%s\nTMPDIR=%s\nHOME=%s\n' "$TMP" "$TEMP" "$TMPDIR" "$HOME"
printf 'uname_path=%s\n' "$(command -v uname)"
printf 'gxx_path=%s\n' "$(command -v g++)"
printf 'verilator_path=%s\n' "$(command -v verilator_bin.exe)"
uname -a
g++ --version
set +e
printf 'int main(){}' | g++ -std=c++20 -fcoroutines -x c++ -c -o "$TMPDIR/gxx_temp_probe.o" -
gxx_probe_exit=$?
set -e
printf 'GXX_PROBE_EXIT=%s\n' "$gxx_probe_exit"
if [ "$gxx_probe_exit" -ne 0 ]; then exit "$gxx_probe_exit"; fi
verilator=/d/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/verilator_bin.exe
python_flag="PYTHON3='/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'"
set +e
"$verilator" --binary --timing -Wno-fatal -j 1 --threads 1 --top-module tb_s2a_weightcap_boundary --Mdir /d/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry03/build -MAKEFLAGS "$python_flag" -CFLAGS '-D_GLIBCXX_USE_CXX11_ABI=0' /d/FPGA_Competition/src/s2a_network_descriptor_pkg.sv /d/FPGA_Competition/src/s2a_conv_tile_engine.sv /d/FPGA_Competition/report/evidence/S2A-T66/weightcap_boundary_4608_20261006_attempt02/retry03/tb_s2a_weightcap_boundary.sv
verilator_exit=$?
set -e
printf 'VERILATOR_EXIT_CODE=%s\n' "$verilator_exit"
exit "$verilator_exit"