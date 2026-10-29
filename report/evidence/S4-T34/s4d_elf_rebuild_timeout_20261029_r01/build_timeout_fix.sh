#!/usr/bin/env bash
# build_timeout_fix.sh —— 用**当前源码**（S4D_NET_TIMEOUT_CYCLES=0xFFFFFFFF）重建
# chainA / chainB / m4b 三个变体。原因（2026-10-29 21:3x 定位）：
#   旧 ELF（2026-10-28 构建）里超时字面量是 0x40000000 = 2^30 周期
#   ⇒ 50 MHz 下 21.47 s，短于 2B 单帧实测 47.3 s ⇒ 内核必然 TIMEOUT(error=5)。
#   实测链条证据：chain-lite A 在 21,474 ms 正好落 error=5。
# 只写本目录；不碰 w4 源码、不碰板卡。
set -u
B="D:/tmp/lead/rebuild_timeout_20261029_r01"
W="D:/codex-worktrees/w4"
BD="$W/tmp/4/S4-B-REAL-01/s4b_ps_tensor_20261023_r13/bundle_extract/bundle/workspace/ps7/export/ps7/sw/cpu0"
GCC="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-gcc.exe"
NM="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-nm.exe"
SZ="D:/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin/arm-none-eabi-size.exe"
LS="$W/tmp/4/S4-T34/ps_app_build/lscript_s4t34.ld"
APP="$W/vitis/stage4/ps/s4d_ps_app.c"
PRE="$W/vitis/stage4/ps/s4d_sw_preproc.c"
DEC="$W/verification/s2a_ps_decode_nms_reference.c"
COMMON="-DSDT -DPREPROC_SRC=0 -mcpu=cortex-a9 -mfpu=vfpv3 -mfloat-abi=hard -MMD -MP \
-specs=$BD/Xilinx.spec -I$BD/include -I$W/verification -I$W/vitis/stage4/ps \
-Wall -Wextra -O2 -g3 -std=gnu11 -ffunction-sections -fdata-sections -U__clang__"

mkdir -p "$B/build" "$B/logs"
cd "$B" || exit 9
: > logs/exit_codes.txt
rec() { echo "$1=$2" >> logs/exit_codes.txt; }

echo "== 共用对象（preproc/decode，与变体无关） =="
"$GCC" $COMMON -o build/s4d_sw_preproc.o -c "$PRE" 2> logs/pre.log; rec preproc $?
"$GCC" $COMMON -o build/s2a_ps_decode_nms_reference.o -c "$DEC" 2> logs/decode.log; rec decode $?

build_variant() {
  tag="$1"; flags="$2"
  echo "== $tag =="
  "$GCC" $COMMON $flags -o "build/s4d_ps_app_sw0_$tag.o" -c "$APP" 2> "logs/app_$tag.log"; rec "compile_$tag" $?
  "$GCC" $COMMON $flags -Wl,-Map="build/s4d_ps_app_sw0_$tag.map",--cref,--gc-sections \
      "build/s4d_ps_app_sw0_$tag.o" build/s2a_ps_decode_nms_reference.o build/s4d_sw_preproc.o \
      -o "build/s4d_ps_app_sw0_$tag.elf" \
      -L"$BD/lib" -Wl,-T -Wl,"$LS" \
      -Wl,--start-group -lxilstandalone -lxiltimer -lxil -lgcc -lc -lm -Wl,--end-group 2> "logs/link_$tag.log"; rec "link_$tag" $?
  "$SZ" --format=berkeley "build/s4d_ps_app_sw0_$tag.elf" > "build/s4d_ps_app_sw0_$tag.size.txt" 2>&1; rec "size_$tag" $?
  "$NM" -C "build/s4d_ps_app_sw0_$tag.elf" > "build/s4d_ps_app_sw0_$tag.nm.txt" 2>&1; rec "nm_$tag" $?
  sha256sum "build/s4d_ps_app_sw0_$tag.elf" | cut -c1-64 > "build/s4d_ps_app_sw0_$tag.sha256"
  echo "$tag SHA=$(cat build/s4d_ps_app_sw0_$tag.sha256)"
}

build_variant chainA "-DS4D_CHAIN_SELFCHECK=1"
build_variant chainB "-DS4D_CHAINB_SELFCHECK=1"
build_variant m4b    "-DS4D_M4B_SELFCHECK=1"

echo "---- EXIT CODES ----"
cat logs/exit_codes.txt
echo "BUILD_TIMEOUT_FIX_DONE"