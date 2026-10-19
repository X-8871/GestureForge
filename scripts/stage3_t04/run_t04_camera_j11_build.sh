#!/usr/bin/env bash
# 阶段3 S3-T04 J11 变体启动器：官方 22_ov5640_single 的 CMOS1 改映射到 J11（A/B 验证用）
# 用法: bash run_t04_camera_j11_build.sh <run_name>
set -u

RUN_NAME="${1:?需要 run 目录名}"
WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/22_ov5640_single/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"
J11_XDC="$WT/board/stage3/hardware/an5642_j11.xdc"

export XILINXD_LICENSE_FILE="D:/Xilinx_licenses/basic_only.lic"

echo "LAUNCHER=gitbash"
echo "RUN_DIR=$RUN_DIR"
echo "VENDOR_IN=$VENDOR"
echo "J11_XDC=$J11_XDC"

TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
if [ "$TOP" != "D:/codex-worktrees/dbdf" ]; then echo "FAIL=worktree_selfcheck:$TOP"; exit 3; fi
if [ -e "$RUN_DIR" ]; then echo "FAIL=run_dir_exists"; exit 3; fi
[ -f "$J11_XDC" ] || { echo "FAIL=j11_xdc_missing"; exit 3; }
mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir"; exit 3; }

cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
cp "$J11_XDC" "$SRC_COPY/src/constraints/an5642.xdc" || { echo "FAIL=xdc_replace"; exit 3; }
echo "XDC_REPLACED_WITH_J11=1"

# 复核：替换后的约束文件必须含 J20/L17/M18/J14（J11 特有脚）
for pin in J20 L17 M18 J14; do
  if ! grep -q "$pin" "$SRC_COPY/src/constraints/an5642.xdc"; then echo "FAIL=j11_pin_not_found:$pin"; exit 3; fi
done
echo "J11_PINS_VERIFIED=1"

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

echo "VENDOR_CACHE_STATUS:"
git -C "$WT/tmp/stage3_reference/AX7020_2023.1" status --short | head -20
exit "$rc"