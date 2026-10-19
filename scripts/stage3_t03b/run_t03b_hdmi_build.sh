#!/usr/bin/env bash
# 阶段3 S3-T03b Git Bash 启动器：官方 14_vdma_hdmi_out 在 xc7z020clg400-2 上重建到比特流
# 用法: bash run_t03b_hdmi_build.sh <run_name>
set -u

RUN_NAME="${1:?需要 run 目录名}"
WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"
VENDOR="$WT/tmp/stage3_reference/AX7020_2023.1/course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project"
SRC_COPY="$RUN_DIR/vendor_src"

export XILINXD_LICENSE_FILE="D:/Xilinx_licenses/basic_only.lic"

echo "LAUNCHER=gitbash"
echo "RUN_DIR=$RUN_DIR"
echo "VENDOR_IN=$VENDOR"
echo "LICENSE_FILE=$XILINXD_LICENSE_FILE"

# 硬性自检：工作树必须正确
TOP="$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null)"
if [ "$TOP" != "D:/codex-worktrees/dbdf" ]; then echo "FAIL=worktree_selfcheck:$TOP"; exit 3; fi
if [ -e "$RUN_DIR" ]; then echo "FAIL=run_dir_exists"; exit 3; fi
mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir"; exit 3; }

# 只读引用：先把官方 auto_create_project 复制成本轮私有副本（不改厂商原件）
cp -r "$VENDOR" "$SRC_COPY" || { echo "FAIL=vendor_copy"; exit 3; }
echo "VENDOR_COPY=$SRC_COPY"

"$VIVADO" -mode batch \
  -source "$WT/scripts/stage3_t03b/build_t03b_hdmi.tcl" \
  -log "$RUN_DIR/vivado.log" \
  -journal "$RUN_DIR/vivado.jou" \
  -tclargs "$RUN_DIR" "$SRC_COPY"
rc=$?
echo "VIVADO_EXIT=$rc"

if [ -f "$RUN_DIR/project/vdma_hdmi_out.runs/impl_1/design_1_wrapper.bit" ]; then
  sha256sum "$RUN_DIR/project/vdma_hdmi_out.runs/impl_1/design_1_wrapper.bit" || true
fi
[ -f "$RUN_DIR/design_1_wrapper.xsa" ] && sha256sum "$RUN_DIR/design_1_wrapper.xsa" || true

# 官方缓存必须保持干净（只读引用核对）
echo "VENDOR_CACHE_STATUS:"
git -C "$WT/tmp/stage3_reference/AX7020_2023.1" status --short | head -20
exit "$rc"