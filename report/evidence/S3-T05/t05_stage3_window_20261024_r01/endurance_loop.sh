#!/usr/bin/env bash
# 阶段3 板级窗口（2026-10-24）耐久循环：每 300 s 一次「只读探测 + 活写标记」，共 7 轮（≈37 分钟）。
# 不写任何寄存器；每轮记录时间戳与 xsdb 真实退出码。用法: bash endurance_loop.sh
set -u
WT=/d/codex-worktrees/dbdf
LOGDIR="${1:?需要日志目录}"
OUT="$LOGDIR/endurance_probes.txt"
: > "$OUT"
echo "ENDURANCE_START=$(date '+%Y-%m-%d %H:%M:%S')" >> "$OUT"
for i in 1 2 3 4 5 6 7; do
  echo "=== probe_$i t=$(date '+%Y-%m-%d %H:%M:%S') ===" >> "$OUT"
  bash "$WT/scripts/stage3_t03b/run_xsdb.sh" "$WT/scripts/stage3_t05/jtag_liveness_marker.tcl" >> "$OUT" 2>&1
  echo "PROBE_${i}_EXIT=$?" >> "$OUT"
  bash "$WT/scripts/stage3_t03b/run_xsdb.sh" "$WT/scripts/stage3_t05/jtag_read_safe.tcl" >> "$OUT" 2>&1
  echo "READ_${i}_EXIT=$?" >> "$OUT"
  if [ "$i" -lt 7 ]; then sleep 300; fi
done
echo "ENDURANCE_DONE=$(date '+%Y-%m-%d %H:%M:%S')" >> "$OUT"
echo "ENDURANCE_ALL_DONE=1" >> "$OUT"