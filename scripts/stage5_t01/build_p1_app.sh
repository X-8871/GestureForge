#!/usr/bin/env bash
# S5-T01 P1 构建：把阶段3 应用源码复制到本树 tmp，插入最小补丁 + 生成用例头，构建 A9 ELF。
# 只读使用 dbdf（不修改其任何文件）；不跑 Vivado；不接触板卡。
# 用法: bash scripts/stage5_t01/build_p1_app.sh [EXEC名]
set -u

EXEC="${1:-s5t01_overlay.elf}"
EXTRA_CFLAGS="${2:-}"
W5="/d/codex-worktrees/w5"
WT="/d/codex-worktrees/dbdf"
SRC="$WT/tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app"
BSP="$SRC/empty_application_bsp"          # 直接复用既有 BSP（不复制、不重建）
STAGE="$W5/tmp/5/S5-T01/p1_app/build"
TOOL1="/d/Xilinx/2026.1/Vitis/gnu/aarch32/nt/gcc-arm-none-eabi/bin"
TOOL2="/d/Xilinx/2026.1/Vitis/gnuwin/bin"

[ -d "$SRC" ] || { echo "FAIL=src_missing $SRC"; exit 3; }
[ -f "$BSP/ps7_cortexa9_0/lib/libxil.a" ] || { echo "FAIL=bsp_missing"; exit 3; }
export PATH="$PATH:$TOOL1:$TOOL2"   # 追加而非前置：避免 Xilinx gnuwin 的 cp.exe 抢占 Git Bash 的 cp
command -v arm-none-eabi-gcc >/dev/null || { echo "FAIL=gcc_not_in_path"; exit 3; }
command -v make >/dev/null || { echo "FAIL=make_not_in_path"; exit 3; }

rm -rf "$STAGE"; mkdir -p "$STAGE"
# 复制应用源码（不含 BSP/对象文件），保持相对目录结构
for item in Makefile Makefile.app lscript.ld Xilinx.spec display_demo.c display_demo.h vdma.c vdma.h ov5640.c ov5640.h; do
  cp -p "$SRC/$item" "$STAGE/" || { echo "FAIL=copy_$item"; exit 3; }
done
cp -rp "$SRC/display_ctrl" "$SRC/dynclk" "$SRC/i2c" "$STAGE/" || { echo "FAIL=copy_dirs"; exit 3; }

# 生成用例头 + 复制叠框模块 + 打最小补丁
python -B "$W5/scripts/stage5_t01/gen_overlay_cases.py" --emit-c "$STAGE/s5_overlay_cases.h" || { echo "FAIL=gen_header"; exit 3; }
cp -p "$W5/scripts/stage5_t01/p1_app/s5_overlay.c" "$STAGE/" || { echo "FAIL=copy_overlay"; exit 3; }
# S5-T02：板上动态映射核心（可选 -DS5_DYNAMIC_MAP=1；Makefile 自动发现顶层 *.c）
cp -p "$W5/scripts/stage5_t01/p1_app/s5_dynamic_map.c" "$STAGE/" || { echo "FAIL=copy_dynmap_c"; exit 3; }
cp -p "$W5/scripts/stage5_t01/p1_app/s5_dynamic_map.h" "$STAGE/" || { echo "FAIL=copy_dynmap_h"; exit 3; }
python -B "$W5/scripts/stage5_t01/apply_p1_patch.py" "$STAGE/display_demo.c" || { echo "FAIL=patch"; exit 3; }
grep -c "s5_overlay_loop(" "$STAGE/display_demo.c" | sed "s/^/PATCH_CALLS=/"

# S5-T02：动态映射核心使用 floor/fmin/fmax（libm）。**仅当**开启该开关时才补 -lm，
# 以保证默认构建逐字节不变（dbdf 原件只读，改的是本树拷贝）。
case "$EXTRA_CFLAGS" in
  *S5_DYNAMIC_MAP=1*)
    python - "$STAGE/Makefile.app" <<'PY' || { echo "FAIL=libm_patch"; exit 3; }
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
old = "-Wl,--start-group,-lxil,-lgcc,-lc,--end-group"
assert s.count(old) == 1, "LN_FLAGS 锚点不唯一"
s = s.replace(old, "-Wl,--start-group,-lxil,-lgcc,-lc,-lm,--end-group")
p.write_text(s, encoding="utf-8", newline="\n")
print("S5DYN_LIBM=added")
PY
    ;;
esac

# 构建
cd "$STAGE" || exit 3
echo "BUILD_DIR=$STAGE"
make -f Makefile.app EXEC="$EXEC" BSP_DIR="$BSP" OPT_FLAGS="-O2 -c $EXTRA_CFLAGS" > build.log 2>&1
RC=$?
tail -6 build.log
echo "MAKE_EXIT=$RC"
if [ "$RC" -ne 0 ] || [ ! -f "$EXEC" ]; then
  echo "FAIL=build"
  grep -nE "error|Error|undefined" build.log | head -20
  exit 1
fi
sha256sum "$EXEC" | tee elf_sha256.txt
ls -l "$EXEC" | awk "{print \"ELF_BYTES=\" \$5}"
echo "BUILD_OK=$EXEC"