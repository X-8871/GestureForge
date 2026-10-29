#!/usr/bin/env bash
# 编译"探针版"长跑应用：首次 CSR 访问前打印 SLCR（判定 PL 无时钟/无响应）
# 工具链与 flags 逐字复用 w4/tmp/4/S4-T34/ps_app_build/build_v2.log（longrunK 构建）
set -u
W=/d/codex-worktrees/w4
B=/d/tmp/lead/probe_app_20261029_r01
BUNDLE="$W/tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r13/bundle_extract/bundle/workspace/ps7/export/ps7/sw/cpu0"
GCC="$BUNDLE/../../../.." # 占位，下面直接用绝对 gcc
GCC="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-gcc.exe"
SZ="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-size.exe"
NM="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-nm.exe"
BD="D:/codex-worktrees/w4/tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r13/bundle_extract/bundle/workspace/ps7/export/ps7/sw/cpu0"
FLAGS="-DSDT -DPREPROC_SRC=0 -DS4D_LONGRUN_SELFCHECK=1 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -MMD -MP -specs=$BD/Xilinx.spec -I$BD/include -ID:/codex-worktrees/w4/verification -ID:/codex-worktrees/w4/vitis/stage4/ps -Wall -Wextra -O2 -g3 -std=gnu11 -ffunction-sections -fdata-sections -U__clang__"

mkdir -p "$B"
cd "$B" || exit 9

echo "== compile app =="
"$GCC" $FLAGS -o "$B/s4d_ps_app_sw0_probe.o" -c "D:/codex-worktrees/w4/vitis/stage4/ps/s4d_ps_app.c" 2> "$B/compile_app.log"
rc_c=$?
echo "compile_app_exit=$rc_c"
[ $rc_c -eq 0 ] || { tail -20 "$B/compile_app.log"; exit 1; }

echo "== compile sw preproc (unchanged source) =="
"$GCC" $FLAGS -o "$B/s4d_sw_preproc.o" -c "D:/codex-worktrees/w4/vitis/stage4/ps/s4d_sw_preproc.c" 2> "$B/compile_pre.log"
rc_p=$?
echo "compile_pre_exit=$rc_p"
[ $rc_p -eq 0 ] || { tail -20 "$B/compile_pre.log"; exit 1; }

echo "== link =="
"$GCC" $FLAGS -Wl,-Map="$B/s4d_ps_app_sw0_longrunP.map",--cref,--gc-sections \
  "$B/s4d_ps_app_sw0_probe.o" \
  "$W/tmp/4/S4-T34/ps_app_build/s2a_ps_decode_nms_reference.o" \
  "$B/s4d_sw_preproc.o" \
  -o "$B/s4d_ps_app_sw0_longrunP.elf" \
  -L"$BD/lib" -Wl,-T -Wl,"$W/tmp/4/S4-T34/ps_app_build/lscript_s4t34.ld" \
  -Wl,--start-group -lxilstandalone -lxiltimer -lxil -lgcc -lc -lm -Wl,--end-group 2> "$B/link.log"
rc_l=$?
echo "link_exit=$rc_l"
[ $rc_l -eq 0 ] || { tail -20 "$B/link.log"; exit 1; }

"$SZ" --format=berkeley "$B/s4d_ps_app_sw0_longrunP.elf" > "$B/size.txt" 2>&1
rc_s=$?
"$NM" -C "$B/s4d_ps_app_sw0_longrunP.elf" > "$B/nm.txt" 2>&1
echo "size_exit=$rc_s"
grep -c "LONGRUN PROBE" "$B/nm.txt" >/dev/null 2>&1
strings "$B/s4d_ps_app_sw0_longrunP.elf" 2>/dev/null | grep -c "LONGRUN PROBE" > "$B/probe_str_count.txt"
echo "probe_string_occurrences=$(cat "$B/probe_str_count.txt")"
sha256sum "$B/s4d_ps_app_sw0_longrunP.elf" | cut -c1-64 > "$B/elf.sha256"
echo "ELF_SHA=$(cat "$B/elf.sha256")"
echo "---- PROBE_APP_BUILD_RC=$((rc_c+rc_p+rc_l)) ----"