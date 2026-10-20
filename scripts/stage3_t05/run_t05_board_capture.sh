#!/usr/bin/env bash
# S3-T05 板测一键运行：后台抓 UART → JTAG 下载(bit+PS初始化+ELF) → 等 UART 收完 → 只读探测并 halt/con 读 DDR。
# 只做易失性下载（PS_RESET/FPGA_PROGRAM/PS7_INIT/DOW/RUN）；不烧 QSPI、不改接线。
# 用法: bash run_t05_board_capture.sh <run_dir> <elf> <tag> [uart_seconds]
#   run_dir 例: D:/codex-worktrees/dbdf/tmp/s3r06/t04_camera_j11cmos2_20261020_r01
#   tag 例: diag5
set -u

RUN_DIR="${1:?需要 run_dir}"
ELF="${2:?需要 ELF}"
TAG="${3:?需要 tag}"
UART_SECS="${4:-60}"

WT="D:/codex-worktrees/dbdf"
LOG_DIR="$RUN_DIR/t05_${TAG}"
mkdir -p "$LOG_DIR" || { echo "FAIL=mkdir"; exit 3; }
echo "T05_RUN_DIR=$RUN_DIR"
echo "T05_ELF=$ELF"
echo "T05_TAG=$TAG"
echo "T05_UART_SECS=$UART_SECS"
echo "T05_LOG_DIR=$LOG_DIR"

# 1) 后台抓串口（只读 COM4）
python "$WT/scripts/stage3_t03b/read_uart.py" COM4 "$UART_SECS" "$LOG_DIR/uart_${TAG}.log" \
  > "$LOG_DIR/uart_${TAG}.stdout" 2>&1 &
UART_PID=$!
echo "T05_UART_PID=$UART_PID"
sleep 2

# 2) JTAG 下载（含 PS_RESET → FPGA_PROGRAM → PS7_INIT → DOW → RUN）
bash "$WT/scripts/stage3_t03b/run_jtag_download_t03.sh" "$RUN_DIR" "$ELF" "" "t05_${TAG}_download" \
  | tee "$LOG_DIR/download_${TAG}.log"
DL_RC=${PIPESTATUS[0]}
echo "T05_DOWNLOAD_EXIT=$DL_RC"

# 3) 等串口抓完
wait "$UART_PID"
UART_RC=$?
echo "T05_UART_EXIT=$UART_RC"

# 4) 安全只读探测（halt → mrd → con），独立于应用的 cache 视角
bash "$WT/scripts/stage3_t03b/run_xsdb.sh" "$WT/scripts/stage3_t05/jtag_read_safe.tcl" \
  | tee "$LOG_DIR/read_safe_${TAG}.log"
echo "T05_READ_EXIT=${PIPESTATUS[0]}"

sha256sum "$ELF" > "$LOG_DIR/input_hashes.txt" 2>/dev/null || true
echo "T05_ALL_DONE=1"
exit "$DL_RC"