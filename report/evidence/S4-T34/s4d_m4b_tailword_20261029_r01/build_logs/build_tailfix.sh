#!/usr/bin/env bash
# build_tailfix.sh —— 在 rebuild_timeout_20261029_r01 之后重建三个 ELF 的**新目录**副本。
# 触发原因（2026-10-29，S4-T34 / task-2 定位）：M4-b 自检在 2B 基线上报
#   diff13=2 first13=5068，根因是宿主侧 head13 参考按字粒度只预置 5,070//4=1,267 字
#   = 5,068 B（run_window_b_driver.py:355 'HEAD13_BYTES // 4'），尾 2 字节
#   （byte 5,068/5,069）从未写入 0x12000000，比较时读到的仍是候选区快照旧值
#   （0x12000000+5,068 = 0xFF 0x8F，见 s4d_m4b_baseline_2b_20261029_r03/W4_dump.bin）。
# 本轮应用侧改动仅为**尾字 lane 取证**（M4B TAIL13 行 + RESULT 诊断字段），
# 不改比较范围（仍逐字节 5,070 B，符合 2A-T01 规格）、不改 pass 判据。
# 只写本目录与 w4 应用源；不碰原 build/ 目录、不碰板卡、不跑 Vivado、不 git。
set -u
B="D:/tmp/lead/tailfix_20261029_r01"
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

echo "== 输入源码哈希（只读记录） =="
sha256sum "$APP" "$PRE" "$DEC" "$LS" | tee logs/input_sha256.txt

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
echo "BUILD_TAILFIX_DONE"