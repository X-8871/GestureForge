#!/usr/bin/env bash
set -euo pipefail
export HOME="$(cygpath -u "$HOME")"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export TMPDIR="$(cygpath -u "$TMPDIR")"
export VERILATOR_ROOT='/d/FPGA_S2A_MSYS2_20261001/env/mingw64/share/verilator'
python_path='/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
verilator_path='/d/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/verilator_bin.exe'
printf "T66_ENV_MSYSTEM=%s\n" "$MSYSTEM"
printf "T66_ENV_MINGW_PREFIX=%s\n" "$MINGW_PREFIX"
printf "T66_ENV_HOME=%s\nT66_ENV_TMP=%s\nT66_ENV_TEMP=%s\nT66_ENV_TMPDIR=%s\n" "$HOME" "$TMP" "$TEMP" "$TMPDIR"
printf "T66_ENV_RESOLVED_UNAME=%s\nT66_ENV_RESOLVED_GXX=%s\nT66_ENV_RESOLVED_MAKE=%s\nT66_ENV_RESOLVED_PYTHON=%s\nT66_ENV_RESOLVED_VERILATOR=%s\n" "$(command -v uname)" "$(command -v g++)" "$(command -v make)" "$python_path" "$verilator_path"
uname -a
g++ --version
make --version
"$python_path" --version
"$verilator_path" --version
set +e
"$verilator_path" '--binary' '--timing' '-Wno-fatal' '-j' '1' '--threads' '1' '--top-module' 'tb_s2a_t66_candidate_blackbox' '--Mdir' '/d/FPGA_Competition/report/evidence/S2A-T66/candidate_blackbox_t66_mutex_full_b65ec36d72324aeda1bb08f1f467a8f7/build' '-MAKEFLAGS' "PYTHON3='/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'" '-CFLAGS' '-D_GLIBCXX_USE_CXX11_ABI=0' '/d/FPGA_Competition/src/s2a_network_descriptor_pkg.sv' '/d/FPGA_Competition/src/s2a_conv_tile_engine.sv' '/d/FPGA_Competition/sim/tb_s2a_t66_candidate_blackbox.sv'
verilator_exit=$?
set -e
printf "VERILATOR_EXIT_CODE=%s\\n" "$verilator_exit"
exit "$verilator_exit"
