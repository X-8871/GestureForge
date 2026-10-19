#!/usr/bin/env bash
# 阶段3 Git Bash 启动器：许可/器件探测（只读—极小内存设计，不烧录、不接板、不干预他方进程）
# 用法: bash s3_run_license_probe.sh <run_dir_name> <part>
set -u

RUN_NAME="${1:?需要 run 目录名}"
PART="${2:?需要 part}"

WT="D:/codex-worktrees/dbdf"
RUN_DIR="$WT/tmp/s3r06/$RUN_NAME"
VIVADO="D:/Xilinx/2026.1/Vivado/bin/vivado"

export XILINXD_LICENSE_FILE="D:/Xilinx_licenses/basic_only.lic"

echo "LAUNCHER=gitbash"
echo "WORKTREE=$WT"
echo "RUN_DIR=$RUN_DIR"
echo "PART=$PART"
echo "LICENSE_FILE=$XILINXD_LICENSE_FILE"

if [ ! -d "$WT" ]; then echo "FAIL=worktree_missing"; exit 3; fi
if [ ! -x "$VIVADO" ]; then echo "FAIL=vivado_missing"; exit 3; fi
if [ -e "$RUN_DIR" ]; then echo "FAIL=run_dir_exists"; exit 3; fi
mkdir -p "$RUN_DIR" || { echo "FAIL=mkdir"; exit 3; }

"$VIVADO" -mode batch \
  -source "$WT/scripts/s3_license_part_probe.tcl" \
  -log "$RUN_DIR/vivado.log" \
  -journal "$RUN_DIR/vivado.jou" \
  -tclargs "$RUN_DIR" "$PART"
rc=$?
echo "VIVADO_EXIT=$rc"
exit "$rc"