#!/usr/bin/env bash
# build_mvp_elf.sh —— 构建 MVP 推理 ELF（离线；不启动 Vivado/hw_server/xsdb）
# 产物：
#   build/s4d_ps_app_mvp.elf        —— core0 standalone（链接 0x00100000，单机自测用）
#   build/s4d_ps_app_mvp_core1.elf  —— core1（链接 0x02000000，与 core0 显示 ELF 并存的双核变体）
set -u
OUT=/d/tmp/lead/mvp_infer_20261031_r01
W=/d/codex-worktrees/w4
BD="D:/codex-worktrees/w4/tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r13/bundle_extract/bundle/workspace/ps7/export/ps7/sw/cpu0"
GCC="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-gcc.exe"
SZ="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-size.exe"
NM="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-nm.exe"
OD="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-objdump.exe"
LS="$W/tmp/4/S4-T34/ps_app_build/lscript_s4t34.ld"
LS1="$OUT/src/lscript_s4t34_core1.ld"
SRC="$OUT/src"
APP="$SRC/s4d_ps_app_mvp.c"
mkdir -p "$OUT/build" "$OUT/logs"
cd "$OUT" || exit 9

FLAGS="-DSDT -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -MMD -MP \
-specs=$BD/Xilinx.spec -I$BD/include -I$SRC -I$W/verification -I$W/vitis/stage4/ps \
-Wall -Wextra -O2 -g3 -std=gnu11 -ffunction-sections -fdata-sections -U__clang__"

: > logs/exit_codes_mvp.txt
rec() { echo "$1=$2" >> logs/exit_codes_mvp.txt; }

echo "== [1/5] compile app (S4D_FRAME_SRC_CAM=1) =="
"$GCC" $FLAGS -DS4D_FRAME_SRC_CAM=1 -DPREPROC_SRC=0 \
    -o build/mvp_app.o -c "$APP" 2> logs/compile_app_mvp.log
rec compile_app_mvp $?

echo "== [2/5] compile shared (sw_preproc + decode ref) =="
"$GCC" $FLAGS -o build/mvp_sw_preproc.o -c "$SRC/s4d_sw_preproc.c" 2> logs/compile_sw_preproc.log
rec compile_sw_preproc $?
"$GCC" $FLAGS -o build/mvp_decode.o -c "$SRC/s2a_ps_decode_nms_reference.c" 2> logs/compile_decode.log
rec compile_decode $?

echo "== [3/5] link core0 (0x00100000) =="
"$GCC" $FLAGS -Wl,-Map="build/s4d_ps_app_mvp.map",--cref,--gc-sections \
    build/mvp_app.o build/mvp_sw_preproc.o build/mvp_decode.o \
    -o "build/s4d_ps_app_mvp.elf" \
    -L"$BD/lib" -Wl,-T -Wl,"$LS" \
    -Wl,--start-group -lxilstandalone -lxiltimer -lxil -lgcc -lc -lm -Wl,--end-group \
    2> logs/link_core0.log
rec link_core0 $?

echo "== [4/5] link core1 (0x02000000) =="
"$GCC" $FLAGS -Wl,-Map="build/s4d_ps_app_mvp_core1.map",--cref,--gc-sections \
    build/mvp_app.o build/mvp_sw_preproc.o build/mvp_decode.o \
    -o "build/s4d_ps_app_mvp_core1.elf" \
    -L"$BD/lib" -Wl,-T -Wl,"$LS1" \
    -Wl,--start-group -lxilstandalone -lxiltimer -lxil -lgcc -lc -lm -Wl,--end-group \
    2> logs/link_core1.log
rec link_core1 $?

echo "== [5/5] size / nm / objdump / strings / sha =="
for T in s4d_ps_app_mvp s4d_ps_app_mvp_core1; do
    "$SZ" "build/$T.elf" > "build/$T.size.txt" 2>&1; rec size_$T $?
    "$NM" -S "build/$T.elf" > "build/$T.nm.txt" 2>&1; rec nm_$T $?
    "$OD" -d "build/$T.elf" > "build/$T.objdump.txt" 2>&1; rec objdump_$T $?
    strings "build/$T.elf" > "build/$T.strings.txt" 2>&1; rec strings_$T $?
    sha256sum "build/$T.elf" > "build/$T.sha256"
done

echo "---- EXIT CODES ----"
cat logs/exit_codes_mvp.txt
echo "---- SHA256 ----"
cat build/s4d_ps_app_mvp.sha256 build/s4d_ps_app_mvp_core1.sha256
echo "BUILD_MVP_DONE"