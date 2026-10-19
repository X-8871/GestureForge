#!/usr/bin/env bash
# 阶段3 S3-T04 J11+CMOS2 变体启动器：把单通道设计接到模块的 CMOS2 通道（J11 上）
# 用法: bash run_t04_camera_j11_cmos2_build.sh <run_name>
set -u

RUN_NAME="${1:?需要 run 目录名}"
WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
XDC_IN="$WT/board/stage3/hardware/an5642_j11_cmos2.xdc"

export XILINXD_LICENSE_FILE="D:/Xilinx_licenses/basic_only.lic"

echo "LAUNCHER=gitbash"
echo "RUN_DIR=$RUN_DIR"
echo "XDC_IN=$XDC_IN"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
if [ "$TOP" != "D:/codex-worktrees/dbdf" ]; then echo "FAIL=worktree_selfcheck:$TOP"; exit 3; fi
if [ -e "$RUN_DIR" ]; then echo "FAIL=run_dir_exists"; exit 3; fi
[ -f "$XDC_IN" ] || { echo "FAIL=xdc_missing"; exit 3; }
mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir"; exit 3; }

cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
cp "$XDC_IN" "$SRC_COPY/src/constraints/an5642.xdc" || { echo "FAIL=xdc_replace"; exit 3; }
echo "XDC_REPLACED_WITH_J11_CMOS2=1"

for pin in F17 F16 F19 L19 K19; do
  if ! grep -q "$pin" "$SRC_COPY/src/constraints/an5642.xdc"; then echo "FAIL=pin_not_found:$pin"; exit 3; fi
done
echo "CMOS2_PINS_VERIFIED=1"

"$VIVADO" -mode batch \
  -source "$WT/scripts/stage3_t04/build_t04_camera.tcl" \
  -log "$RUN_DIR/vivado.log" \
  -journal "$RUN_DIR/vivado.jou" \
  -tclargs "$RUN_DIR" "$SRC_COPY"
rc=$?
echo "VIVADO_EXIT=$rc"

if [ -f "$RUN_DIR/project/ov5640_single.runs/impl_1/design_1_wrapper.bit" ]; then
  sha256sum "$RUN_DIR/project/ov5640_single.runs/impl_1/design_1_wrapper.bit" || true
fi
[ -f "$RUN_DIR/design_1_wrapper.xsa" ] && sha256sum "$RUN_DIR/design_1_wrapper.xsa" || true
exit "$rc"