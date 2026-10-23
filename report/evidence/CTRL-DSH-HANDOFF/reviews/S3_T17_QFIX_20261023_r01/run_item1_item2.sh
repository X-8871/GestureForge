#!/usr/bin/env bash
# S3-T17 快修复审（task-19）：item1（R-1/R-2 真关闭）+ item2（判别力反例）
# 全部命令：不设 PYTHONUTF8；stdout 重定向到文件；记录真实退出码。
set +e
R=/d/FPGA_Competition/tmp/review/S3_T17_QFIX_20261023_r01
C=$R/clonet
OUT=$R/cmd
FIX=$R/selftest_fixtures
OLD=$R/oldf77f363
NOCFG=$R/noreconf
mkdir -p "$OUT/item1" "$OUT/item2" "$FIX" "$OLD" "$NOCFG"
: > "$OUT/exit_codes.txt"
cd "$C" || exit 9

ARCH_REL=report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/bars_raw_frame_full.bin
ARCH=$C/$ARCH_REL
FIXC=$FIX/fixture_C_blue_only.bin

log() { echo "$*" | tee -a "$OUT/exit_codes.txt"; }

echo "=== env diagnostic (stdout redirected => see pipe encoding) ===" > "$OUT/env.txt"
python -V >> "$OUT/env.txt" 2>&1
python -c "import sys,locale;print('stdout.encoding=',sys.stdout.encoding);print('preferred=',locale.getpreferredencoding(False))" >> "$OUT/env.txt" 2>&1
echo "PYTHONUTF8=[${PYTHONUTF8:-<unset>}] PYTHONIOENCODING=[${PYTHONIOENCODING:-<unset>}]" >> "$OUT/env.txt"
cat "$OUT/env.txt"

# ---------------- item 1-1: runner preflight（README 命令） ----------------
cd "$C"
bash scripts/stage3_t17/run_t17_color_retest.sh preflight --run-id t17_qfix_review_preflight_r01 > "$OUT/item1/01_runner_preflight.stdout.txt" 2>&1
log "01_runner_preflight rc=$?"
tail -3 "$OUT/item1/01_runner_preflight.stdout.txt"

# ---------------- item 1-2: analyze --selftest ----------------
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --selftest --repo-root "$C" --fixture-dir "$FIX" --json-out "$OUT/item1/02_selftest.json" > "$OUT/item1/02_selftest.stdout.txt" 2>&1
log "02_analyze_selftest rc=$?"
tail -12 "$OUT/item1/02_selftest.stdout.txt"

# ---------------- item 1-3: analyze --frame 归档缺陷整帧 ----------------
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame "$ARCH" --json-out "$OUT/item1/03_archived.json" > "$OUT/item1/03_archived.stdout.txt" 2>&1
log "03_analyze_archived rc=$?"
tail -3 "$OUT/item1/03_archived.stdout.txt"

# ---------------- item 1-4: analyze --frame 只修一路 ----------------
python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame "$FIXC" --json-out "$OUT/item1/04_partial.json" > "$OUT/item1/04_partial.stdout.txt" 2>&1
log "04_analyze_partial_blue_only rc=$?"
tail -3 "$OUT/item1/04_partial.stdout.txt"

# ---------------- item 1-5: check_t17_preflight.py ----------------
python -B scripts/stage3_t17/check_t17_preflight.py --worktree "$C" --json-out "$OUT/item1/05_check_preflight.json" > "$OUT/item1/05_check_preflight.stdout.txt" 2>&1
log "05_check_t17_preflight rc=$?"
tail -4 "$OUT/item1/05_check_preflight.stdout.txt"

# ---------------- item 1-6: verify_t17_blob_identity.py ----------------
python -B scripts/stage3_t17/verify_t17_blob_identity.py --repo-root "$C" --commit HEAD --json-out "$OUT/item1/06_blob_identity.json" > "$OUT/item1/06_blob_identity.stdout.txt" 2>&1
log "06_verify_blob_identity rc=$?"
cat "$OUT/item1/06_blob_identity.stdout.txt"

# ---------------- item 1-7: handoff_check --record（交付态 record，当前 HEAD=975f3a5） ----------------
python -B /d/FPGA_Competition/verification/handoff_check.py --worktree /d/codex-worktrees/dbdf \
  --record /d/codex-worktrees/dbdf/report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_record_stage3_delivered.json \
  --json > "$OUT/item1/07_handoff_dbdf_asIs.stdout.txt" 2>&1
log "07_handoff_record_asIs rc=$?"
grep -E '^\[|结论|退出码' "$OUT/item1/07_handoff_dbdf_asIs.stdout.txt" | tail -6

# ---------------- item 1-8: PYTHONIOENCODING=gbk 关键两条（R-1/R-2 路径） ----------------
PYTHONIOENCODING=gbk python -B scripts/stage3_t17/verify_t17_blob_identity.py --repo-root "$C" --commit HEAD --json-out "$OUT/item1/08a_gbk_blob.json" > "$OUT/item1/08a_gbk_blob.stdout.txt" 2>&1
log "08a_gbk_verify_blob_identity rc=$?"
PYTHONIOENCODING=gbk python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame "$ARCH" --json-out "$OUT/item1/08b_gbk_archived.json" > "$OUT/item1/08b_gbk_archived.stdout.txt" 2>&1
log "08b_gbk_analyze_archived rc=$?"
PYTHONIOENCODING=gbk python -B scripts/stage3_t17/analyze_t17_bit_integrity.py --frame "$FIXC" --json-out "$OUT/item1/08c_gbk_partial.json" > "$OUT/item1/08c_gbk_partial.stdout.txt" 2>&1
log "08c_gbk_analyze_partial rc=$?"

# ---------------- item 2-a: f77f363 旧版两工具 ----------------
cd "$C"
git show f77f363:scripts/stage3_t17/analyze_t17_bit_integrity.py > "$OLD/analyze_old.py"
git show f77f363:scripts/stage3_t17/verify_t17_blob_identity.py > "$OLD/verify_old.py"
echo "old_script_md5=$(md5sum "$OLD"/analyze_old.py "$OLD"/verify_old.py | tr '\n' ' ')" >> "$OUT/exit_codes.txt"
python -B "$OLD/verify_old.py" --repo-root "$C" --commit HEAD --json-out "$OUT/item2/a1_old_blob.json" > "$OUT/item2/a1_old_blob.stdout.txt" 2>&1
log "a1_old_verify_blob rc=$?"
python -B "$OLD/analyze_old.py" --frame "$ARCH" --json-out "$OUT/item2/a2_old_archived.json" > "$OUT/item2/a2_old_archived.stdout.txt" 2>&1
log "a2_old_analyze_archived rc=$?"
python -B "$OLD/analyze_old.py" --frame "$FIXC" --json-out "$OUT/item2/a3_old_partial.json" > "$OUT/item2/a3_old_partial.stdout.txt" 2>&1
log "a3_old_analyze_partial rc=$?"
echo "--- old json landed? ---" >> "$OUT/exit_codes.txt"
for f in "$OUT/item2/a1_old_blob.json" "$OUT/item2/a2_old_archived.json" "$OUT/item2/a3_old_partial.json"; do
  if [ -f "$f" ]; then echo "EXISTS $f" >> "$OUT/exit_codes.txt"; else echo "MISSING $f" >> "$OUT/exit_codes.txt"; fi
done
echo "--- old stderr tails ---" >> "$OUT/exit_codes.txt"
tail -4 "$OUT/item2/a1_old_blob.stdout.txt" >> "$OUT/exit_codes.txt"
tail -4 "$OUT/item2/a2_old_archived.stdout.txt" >> "$OUT/exit_codes.txt"
tail -4 "$OUT/item2/a3_old_partial.stdout.txt" >> "$OUT/exit_codes.txt"

# ---------------- item 2-b: F3 版去掉 reconfigure 调用的副本 -> --selftest 必须 FAIL ----------------
python - "$C/scripts/stage3_t17/analyze_t17_bit_integrity.py" "$NOCFG/analyze_noreconf.py" <<'PY'
import sys, io
src = open(sys.argv[1], encoding="utf-8").read()
lines = src.split("\n")
kept = [ln for ln in lines if ln.strip() != "_force_utf8_streams()"]
assert len(kept) == len(lines) - 1, "expected exactly one call line"
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(kept))
print("removed_lines=1")
PY
grep -n "_force_utf8_streams" "$NOCFG/analyze_noreconf.py" >> "$OUT/exit_codes.txt"
mkdir -p "$R/noreconf_fixtures"
python -B "$NOCFG/analyze_noreconf.py" --selftest --repo-root "$C" --fixture-dir "$R/noreconf_fixtures" --json-out "$OUT/item2/b1_noreconf_selftest.json" > "$OUT/item2/b1_noreconf_selftest.stdout.txt" 2>&1
log "b1_noreconf_selftest rc=$?"
tail -12 "$OUT/item2/b1_noreconf_selftest.stdout.txt"

echo "=== DONE ===" >> "$OUT/exit_codes.txt"
cat "$OUT/exit_codes.txt"