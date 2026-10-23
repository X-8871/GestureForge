#!/usr/bin/env bash
# S3-T17 阶段3 色彩复测一键执行器（新摄像头到货后：DVP 位完整性 + 真彩通路）。
#
# 阶段：
#   preflight                     离线前置检查（工作树/锁/重型进程/冻结产物哈希/硬件门禁）
#   judge [--frame f | <row文件...>]  离线判定（调用 analyze_t17_bit_integrity.py）
#   link                          只读 JTAG 链路确认（陷阱：用 llength [targets]/jtag targets）
#   baseline                      无补偿基线（bit 7cb33068 + v9_read）→ 只读回读 → 安全转储 → 判定
#   bars                          内部彩条（v12 写 0x503D=0x80，仅易失）→ 安全转储 → 恢复 → 判定
#   all                           preflight → link → baseline → bars → 汇总
#
# 硬件阶段的前置条件（两者同时成立，否则退出码 3，绝不动板）：
#   ① --allow-hardware 显式开关  ② report/evidence/S3-T17/hw_authorization.json 中
#      wong_go 与 codex_hw_release 同时为 true（Wong 开工信号 + 硬件窗口书面让出/时间窗）。
#
# 硬边界：只写本工作树；只做易失 JTAG；不烧 QSPI；不改接线；一次只跑一个重型任务；
#         自起的 hw_server 用完即终止，运行前已存在的他人会话一律不动。
#
# 退出码（评审 N-5 补齐 exit 4）：
#   0  该阶段成功（preflight 的 OFFLINE_GO 也是 0）
#   1  all 的 preflight 失败（T17_ABORT=PREFLIGHT_FAILED）
#   2  用法错误（未知阶段/缺参数）或**运行位置护栏拒绝**（cwd ≠ WT，T17_GUARD_CWD_MISMATCH=1，未创建任何文件）；judge 阶段会把判定器退出码原样传播（0/1/2/3）
#   3  硬件门禁未放行（T17_HW_BLOCKED=…）或目标目录已存在（T17_REFUSE=EXISTS）
#   4  extract_addr_stride 取不到 ADDR_S2MM/STRIDE_S2MM（T17_ADDR_STRIDE_MISSING=1）—— 禁止用旧地址转储
#
# 前提（评审 N-4）：本仓库 core.autocrlf=true；按工作区口径复核哈希/自证须
#   `git -c core.autocrlf=false clone`（详见 scripts/stage3_t17/README.md）。
# 前置 HEAD 判据（评审 B-3）：HEAD 只需是**声明基线或其后代**（可用 --baseline-commit / T17_BASELINE_COMMIT 覆盖）。
#
# 用法示例（**必须在工作树内运行**：先 `cd D:/codex-worktrees/dbdf`；在克隆内跑须 `--wt <该克隆>` 或 `T17_WT=<该克隆>`，否则 exit 2 拒绝）：
#   cd D:/codex-worktrees/dbdf
#   bash scripts/stage3_t17/run_t17_color_retest.sh preflight
#   bash scripts/stage3_t17/run_t17_color_retest.sh judge --frame <某帧.bin>
#   bash scripts/stage3_t17/run_t17_color_retest.sh all --run-id t17_color_retest_20261023_r01 --allow-hardware
set -u

# 工作树：默认 dbdf；可用 env `T17_WT` 或 `--wt <路径>` 覆盖。
# **护栏（评审 Q-A）**：cwd 必须与 WT 指向同一目录，否则**拒绝运行（exit 2）且不创建任何文件**——
# 因为 WT 决定全部写入位置（evidence/tmp/脚本/ELF），从克隆调用而 WT 仍指向 dbdf 会**静默写坏 dbdf 证据**。
WT="${T17_WT:-D:/codex-worktrees/dbdf}"
PHASE="${1:?用法: run_t17_color_retest.sh <preflight|judge|link|baseline|bars|all> [选项]}"
shift || true

RUN_ID="t17_color_retest_20261023_r01"
ALLOW_HW=0
WANT_FRAME=0
JUDGE_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --wt) WT="${2:?--wt 需要工作树路径}"; shift 2 ;;
    --run-id) RUN_ID="${2:?--run-id 需要值}"; shift 2 ;;
    --allow-hardware) ALLOW_HW=1; shift ;;
    --frame) WANT_FRAME=1; JUDGE_ARGS+=("--frame" "${2:?--frame 需要路径}"); shift 2 ;;
    --rows) shift; while [ $# -gt 0 ] && [[ "$1" != --* ]]; do JUDGE_ARGS+=("$1"); shift; done ;;
    *) JUDGE_ARGS+=("$1"); shift ;;
  esac
done

PY="python"
# ---------- 运行位置护栏（评审 Q-A；必须在任何 mkdir/写文件之前）----------
# 归一化目录：优先 `pwd -W`（Git Bash 下给出 D:/... 形式），失败回退 `pwd`；大小写不敏感比较。
norm_dir() { ( cd "$1" >/dev/null 2>&1 && { pwd -W 2>/dev/null || pwd; } ) || return 1; }
WT_NORM="$(norm_dir "$WT")" || {
  echo "T17_GUARD=WT_NOT_FOUND path=$WT"
  echo "T17_RUN_ABORTED=1（未创建任何文件）"
  exit 2
}
if [ ! -d "$WT/.git" ] && [ ! -f "$WT/.git" ]; then
  echo "T17_GUARD=WT_NOT_A_GIT_WORKTREE path=$WT_NORM"
  echo "T17_RUN_ABORTED=1（未创建任何文件）"
  exit 2
fi
CWD_NORM="$(norm_dir .)" || {
  echo "T17_GUARD=CWD_UNRESOLVED"
  echo "T17_RUN_ABORTED=1（未创建任何文件）"
  exit 2
}
if [ "$(printf '%s' "$CWD_NORM" | tr 'A-Z' 'a-z')" != "$(printf '%s' "$WT_NORM" | tr 'A-Z' 'a-z')" ]; then
  echo "T17_GUARD_CWD_MISMATCH=1"
  echo "T17_CWD=$CWD_NORM"
  echo "T17_WT=$WT_NORM"
  echo "T17_RUN_FROM_WORKTREE_REQUIRED=1（先 cd $WT_NORM 再执行，或显式 --wt <该工作树>／T17_WT=<该工作树>）"
  echo "T17_RUN_ABORTED=1（未创建任何文件）"
  exit 2
fi
echo "T17_GUARD_CWD_OK=1 WT=$WT_NORM"
export PYTHONUTF8=1
export XILINXD_LICENSE_FILE="D:/Xilinx_licenses/basic_only.lic"
EVID="$WT/report/evidence/S3-T17/$RUN_ID"
TMP="$WT/tmp/3/S3-T17/$RUN_ID"
ANALYZER="$WT/scripts/stage3_t17/analyze_t17_bit_integrity.py"
PREFLIGHT="$WT/scripts/stage3_t17/check_t17_preflight.py"
DUMP_TCL="$WT/scripts/stage3_t17/jtag_t17_dump_rows.tcl"
LINK_TCL="$WT/scripts/stage3_t17/jtag_t17_link_check.tcl"
XSDB_LAUNCHER="$WT/scripts/stage3_t03b/run_xsdb.sh"
CAPTURE="$WT/scripts/stage3_t05/run_t05_board_capture.sh"

BASE_BIT="$WT/tmp/s3r06/t04_sof_fix_20261020_r01/project/ov5640_single.runs/impl_1/design_1_wrapper.bit"
ELF_V9="$WT/tmp/s3r06/t04_j11cmos2_elf_v9/elf_build/app/an5642_j11cmos2_v9_read.elf"
ELF_V10="$WT/tmp/s3r06/t04_j11cmos2_elf_v10/elf_build/app/an5642_j11cmos2_v10_read.elf"
ELF_V12="$WT/tmp/s3r06/t04_j11cmos2_elf_v12/elf_build/app/an5642_j11cmos2_v12_bars_freeze.elf"

mkdir -p "$EVID" "$TMP"
LOG="$EVID/run_log.txt"
say() { echo "$@" | tee -a "$LOG"; }

# ---------- 硬件门禁 ----------
require_hw() {
  if [ "$ALLOW_HW" != "1" ]; then
    say "T17_HW_BLOCKED=MISSING_ALLOW_HARDWARE_FLAG（需显式 --allow-hardware）"
    exit 3
  fi
  local auth="$WT/report/evidence/S3-T17/hw_authorization.json"
  if [ ! -f "$auth" ]; then
    say "T17_HW_BLOCKED=NO_HW_AUTHORIZATION_FILE（$auth）"
    exit 3
  fi
  "$PY" - "$auth" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
ok = bool(d.get("wong_go")) and bool(d.get("codex_hw_release"))
print("T17_HW_AUTHORIZATION=%s wong_go=%s codex_hw_release=%s"
      % ("CONFIRMED" if ok else "INCOMPLETE", d.get("wong_go"), d.get("codex_hw_release")))
print("T17_HW_AUTHORIZATION_DECLARED_BY=%s" % d.get("declared_by"))
print("T17_HW_AUTHORIZATION_REFS=%s" % d.get("references"))
sys.exit(0 if ok else 3)
PYEOF
  local rc=$?
  [ "$rc" -eq 0 ] || { say "T17_HW_BLOCKED=HW_AUTHORIZATION_INCOMPLETE"; exit 3; }
  say "T17_HW_GATE=OPEN"
}

# ---------- hw_server 快照/清理（只终止本次新起的） ----------
hw_pids() {
  tasklist //FI "IMAGENAME eq hw_server.exe" //FO CSV //NH 2>/dev/null \
    | awk -F'","' '{gsub(/"/,"",$2); if ($2 ~ /^[0-9]+$/) print $2}' | sort -u
}
HW_BEFORE="$(hw_pids || true)"
cleanup_hw() {
  local after new
  after="$(hw_pids || true)"
  new="$(comm -13 <(echo "$HW_BEFORE") <(echo "$after") 2>/dev/null || true)"
  if [ -n "$new" ]; then
    for pid in $new; do
      say "T17_HW_SERVER_KILL_SELF_STARTED=$pid"
      taskkill //PID "$pid" //F >/dev/null 2>&1 || say "T17_HW_SERVER_KILL_FAIL=$pid"
    done
  else
    say "T17_HW_SERVER_NO_NEW_PROCESS=1"
  fi
  if [ -n "$HW_BEFORE" ]; then
    say "T17_HW_SERVER_PREEXISTING_NOT_TOUCHED=$(echo $HW_BEFORE | tr '\n' ',')"
  fi
}

refuse_existing() { [ -e "$1" ] && { say "T17_REFUSE=EXISTS:$1"; exit 3; }; return 0; }

# 从只读回读日志里取当前帧地址/stride（不得硬编码旧地址）
extract_addr_stride() {
  local log="$1"
  ADDR_HEX="$(grep -oiE 'ADDR_S2MM=(0x[0-9a-f]+)' "$log" | tail -1 | cut -d= -f2)"
  local stride_hex
  stride_hex="$(grep -oiE 'STRIDE_S2MM=(0x[0-9a-f]+)' "$log" | tail -1 | cut -d= -f2)"
  if [ -z "$ADDR_HEX" ] || [ -z "$stride_hex" ]; then
    say "T17_ADDR_STRIDE_MISSING=1（日志 $log 未含 ADDR_S2MM/STRIDE_S2MM；禁止用旧地址转储）"
    exit 4
  fi
  STRIDE_DEC=$((stride_hex))
  say "T17_FRAME_ADDR=$ADDR_HEX"
  say "T17_STRIDE_BYTES=$STRIDE_DEC ($stride_hex)"
}

judge_rows() {
  local tag="$1"; shift
  "$PY" -B "$ANALYZER" --rows "$@" --json-out "$EVID/judge_${tag}.json" 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  say "T17_JUDGE_${tag}_EXIT=$rc"
  return "$rc"
}

phase_preflight() {
  say "== phase preflight（离线）=="
  "$PY" -B "$PREFLIGHT" --worktree "$WT" \
    --json-out "$EVID/preflight.json" 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  say "T17_PREFLIGHT_EXIT=$rc"
  return "$rc"
}

phase_link() {
  say "== phase link（只读 JTAG 链路确认）=="
  require_hw
  refuse_existing "$TMP/link"
  mkdir -p "$TMP/link"
  bash "$XSDB_LAUNCHER" "$LINK_TCL" 2>&1 | tee -a "$LOG" | tee "$TMP/link/link_check.log"
  local rc=${PIPESTATUS[0]}
  say "T17_LINK_EXIT=$rc"
  cleanup_hw
  return "$rc"
}

phase_baseline() {
  say "== phase baseline（无补偿基线 + v9_read；真彩/位完整性复测专用）=="
  require_hw
  refuse_existing "$TMP/baseline"
  mkdir -p "$TMP/baseline"
  bash "$CAPTURE" "$TMP/baseline" "$ELF_V9" baseline 90 2>&1 | tee -a "$LOG"
  say "T17_BASELINE_CAPTURE_EXIT=${PIPESTATUS[0]}"
  extract_addr_stride "$TMP/baseline/t05_baseline/read_safe_baseline.log"
  local dumpdir="$TMP/baseline/dump_rows"
  mkdir -p "$dumpdir"
  local extra=(); [ "$WANT_FRAME" = "1" ] && extra=(--frame)
  bash "$XSDB_LAUNCHER" "$DUMP_TCL" "$dumpdir" "$ADDR_HEX" "$STRIDE_DEC" 200 360 500 "${extra[@]+"${extra[@]}"}" 2>&1 | tee -a "$LOG"
  say "T17_BASELINE_DUMP_EXIT=${PIPESTATUS[0]}"
  cleanup_hw
  judge_rows baseline "$dumpdir/row_y200.bin" "$dumpdir/row_y360.bin" "$dumpdir/row_y500.bin"
  local rc=$?
  say "T17_BASELINE_JUDGE_EXIT=$rc"
  return "$rc"
}

phase_bars() {
  say "== phase bars（传感器内部彩条 0x503D=0x80，仅易失）=="
  require_hw
  refuse_existing "$TMP/bars"
  mkdir -p "$TMP/bars"
  # ① 写入前必须能回读原值；本工具自身回读 before/after（S3_DIAG12_BARS=...）
  bash "$CAPTURE" "$TMP/bars" "$ELF_V12" bars 90 2>&1 | tee -a "$LOG"
  say "T17_BARS_CAPTURE_EXIT=${PIPESTATUS[0]}"
  extract_addr_stride "$TMP/bars/t05_bars/read_safe_bars.log"
  local dumpdir="$TMP/bars/dump_rows"
  mkdir -p "$dumpdir"
  bash "$XSDB_LAUNCHER" "$DUMP_TCL" "$dumpdir" "$ADDR_HEX" "$STRIDE_DEC" 200 360 500 --frame 2>&1 | tee -a "$LOG"
  say "T17_BARS_DUMP_EXIT=${PIPESTATUS[0]}"
  cp -f "$dumpdir/frame_full.bin" "$EVID/bars_raw_frame_full.bin" 2>/dev/null || say "T17_BARS_FRAME_COPY_MISSING=1"
  cleanup_hw
  judge_rows bars "$dumpdir/row_y200.bin" "$dumpdir/row_y360.bin" "$dumpdir/row_y500.bin"
  local bars_rc=$?
  say "T17_BARS_JUDGE_EXIT=$bars_rc"

  # ② 恢复普通输出：v10_read 的 init 表把 0x503D 写回 0x00；必须回读确认
  say "== phase bars/restore（恢复 0x503D=0x00 并回读）=="
  refuse_existing "$TMP/restore"
  mkdir -p "$TMP/restore"
  bash "$CAPTURE" "$TMP/restore" "$ELF_V10" restore 60 2>&1 | tee -a "$LOG"
  say "T17_RESTORE_CAPTURE_EXIT=${PIPESTATUS[0]}"
  cleanup_hw
  if grep -qE '503D=(0x)?0*0?([^0-9a-f]|$)' "$TMP/restore/t05_restore/uart_restore.log" 2>/dev/null; then
    say "T17_RESTORE_503D_ZERO=1"
  else
    say "T17_RESTORE_503D_ZERO=UNCONFIRMED（人工核对 uart_restore.log 的 S3_DIAG5_SENS 行）"
  fi
  return "$bars_rc"
}

phase_judge() {
  say "== phase judge（离线判定）=="
  if [ "${#JUDGE_ARGS[@]}" -eq 0 ]; then
    say "T17_JUDGE_USAGE=需要 --frame <帧> 或 <row_y*.bin>..."; exit 2
  fi
  "$PY" -B "$ANALYZER" "${JUDGE_ARGS[@]}" --json-out "$EVID/judge_manual.json" 2>&1 | tee -a "$LOG"
  local rc=${PIPESTATUS[0]}
  say "T17_JUDGE_MANUAL_EXIT=$rc"
  exit "$rc"
}

case "$PHASE" in
  preflight) phase_preflight ;;
  judge) phase_judge ;;
  link) phase_link ;;
  baseline) phase_baseline ;;
  bars) phase_bars ;;
  all)
    say "T17_START=$PHASE run_id=$RUN_ID"
    phase_preflight || { say "T17_ABORT=PREFLIGHT_FAILED"; exit 1; }
    if [ "$ALLOW_HW" != "1" ]; then
      say "T17_ALL_OFFLINE_ONLY=1（未给 --allow-hardware，硬件阶段不执行）"
      say "T17_ALL_DONE_OFFLINE=1"
      exit 0
    fi
    require_hw
    phase_link || say "T17_LINK_NONZERO=1"
    phase_baseline || say "T17_BASELINE_NONZERO=1"
    phase_bars || say "T17_BARS_NONZERO=1"
    cleanup_hw
    say "T17_ALL_DONE=1（硬件流程结束后板上比流以恢复为准；彩条为易失）"
    ;;
  *) say "T17_USAGE=未知阶段 $PHASE"; exit 2 ;;
esac