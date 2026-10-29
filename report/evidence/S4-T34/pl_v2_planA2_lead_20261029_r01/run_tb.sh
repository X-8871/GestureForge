#!/usr/bin/env bash
# planA2 TB equivalence: 3 TBs against my patched RTL (D:\tmp\lead\planA2_20261029_r01\rtl)
set -u
XV=/d/Xilinx/2026.1/Vivado/bin
SRC=/d/tmp/lead/planA2_20261029_r01/rtl
TBS=/d/wb-out/task1/tb
WORK=/d/tmp/lead/planA2_20261029_r01/tb
mkdir -p "$WORK/golden"
cp /d/wb-out-r3/p0_rerun/golden/*.bin "$WORK/golden/" 2>/dev/null
: > "$WORK/results.tsv"
rc=0

run_one () {
  local d=$1 top=$2; shift 2
  mkdir -p "$WORK/$d"; cd "$WORK/$d" || return 9
  local srcs=()
  for f in "$@"; do
    case "$f" in tb_*) srcs+=("$TBS/$f");; *) srcs+=("$SRC/$f");; esac
  done
  "$XV/xvlog.bat" -sv -i "$SRC" "${srcs[@]}" > xvlog.log 2>&1; local v=$?
  "$XV/xelab.bat" -debug off "$top" -s sim > xelab.log 2>&1; local e=$?
  timeout 3600 "$XV/xsim.bat" sim -runall > xsim.log 2>&1; local r=$?
  local line fnv
  line=$(grep -a '^RESULT' xsim.log | tail -1)
  fnv=$(grep -a 'FNV1a64' xsim.log | tail -1)
  local verdict=FAIL
  case "$line" in
    *pass=1*mismatch=0*)
      if [ -z "$fnv" ]; then
        verdict=EQUIV_NOFNV
      else
        local d1 g1
        d1=$(echo "$fnv" | grep -o 'dut=[0-9a-fA-Fx]*' | head -1 | cut -d= -f2)
        g1=$(echo "$fnv" | grep -o 'gold=[0-9a-fA-Fx]*' | head -1 | cut -d= -f2)
        if [ -n "$d1" ] && [ "$d1" = "$g1" ]; then verdict=EQUIV; fi
      fi ;;
  esac
  printf '%s\txvlog=%s\txelab=%s\txsim=%s\t%s\t%s\n' "$d" "$v" "$e" "$r" "$verdict" "$line" >> "$WORK/results.tsv"
  printf '%-18s xvlog=%d xelab=%d xsim=%d -> %-11s | %s\n  %s\n' "$d" "$v" "$e" "$r" "$verdict" "$line" "$fnv"
  [ "$verdict" = EQUIV ] || [ "$verdict" = EQUIV_NOFNV ] || rc=1
}

run_one work_engine_v2 tb_s4d_preproc_engine_v2 s4d_preproc_engine_v2.sv tb_s4d_preproc_engine_v2.sv || rc=1
run_one work_v2_axi   tb_s4d_preproc_v2_axi     s4d_preproc_engine_v2.sv s4d_axi4_rd_shim.sv tb_s4d_preproc_v2_axi.sv || rc=1
run_one work_v2_axis  tb_s4d_preproc_v2_axis    s4d_preproc_engine_v2.sv s4d_preproc_out_axis.sv tb_s4d_preproc_v2_axis.sv || rc=1

echo "---- PLANA2_TB_RC=$rc ----"
exit $rc