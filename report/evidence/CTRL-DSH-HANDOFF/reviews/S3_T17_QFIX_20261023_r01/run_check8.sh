#!/usr/bin/env bash
# 评审核查 8：m2 突变体手工复跑（看是否有 UnicodeEncodeError/被捕获）+ sha1 比对法核验 + STATE 箭头精确计数
set +e
R=/d/FPGA_Competition/tmp/review/S3_T17_QFIX_20261023_r01
C=$R/clonet
WT=/d/codex-worktrees/dbdf
OUT=$R/cmd
LOG=$OUT/exit_codes5.txt
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

cd "$C" || exit 9
ARCH=report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/bars_raw_frame_full.bin

say "=== m2 突变体（⇒ 恢复 + 去 reconfigure）手工跑：归档帧 ==="
PYTHONIOENCODING=gbk python -B "$R/mutations/analyze_arrow_no_rc.py" --frame "$ARCH" \
  --json-out "$R/mutations/m2_manual.json" > "$R/mutations/m2_manual.stdout.txt" 2>&1
say "m2_manual_archived rc=$?"
say "m2_manual_json=$([ -f "$R/mutations/m2_manual.json" ] && echo landed || echo MISSING)"
say "SUMMARY_PRINT_FAILED 出现次数=$(grep -c 'SUMMARY_PRINT_FAILED' "$R/mutations/m2_manual.stdout.txt")"
say "UnicodeEncodeError 出现次数=$(grep -c 'UnicodeEncodeError' "$R/mutations/m2_manual.stdout.txt")"
grep -n 'SUMMARY_PRINT_FAILED\|UnicodeEncodeError\|JSON_OUT' "$R/mutations/m2_manual.stdout.txt" | head -6 | tee -a "$LOG"
say "--- 若被捕获，随后应看到 traceback 行 ---"
grep -n 'Traceback\|line .*, in main' "$R/mutations/m2_manual.stdout.txt" | head -4 | tee -a "$LOG"

say "=== m2 突变体：只修一路帧 ==="
PYTHONIOENCODING=gbk python -B "$R/mutations/analyze_arrow_no_rc.py" \
  --frame "$R/selftest_fixtures/fixture_C_blue_only.bin" --json-out "$R/mutations/m2_manual_partial.json" \
  > "$R/mutations/m2_manual_partial.stdout.txt" 2>&1
say "m2_manual_partial rc=$?"
say "partial_json=$([ -f "$R/mutations/m2_manual_partial.json" ] && echo landed || echo MISSING)"
say "partial_SUMMARY_PRINT_FAILED=$(grep -c 'SUMMARY_PRINT_FAILED' "$R/mutations/m2_manual_partial.stdout.txt")"

say "=== 旧版（f77f363）同样命令的对照 ==="
say "old_archived_rc_recorded=1（见 item2/a2，无 JSON）"

say "=== sha1 比对法核验（含已知改动的 4 个证据文件） ==="
for f in report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/README.md \
         report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.json \
         report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/t17_judgement_table.md \
         report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/README.md \
         report/evidence/S3-T05/t05_sw_v9_20261021_r01/README.md; do
  a=$(git -C "$WT" rev-parse "f77f363:$f" 2>&1)
  b=$(git -C "$WT" rev-parse "605f960:$f" 2>&1)
  say "$(basename "$f") in $(dirname "$f")"
  say "   old=[$a]"
  say "   new=[$b]"
done
say "--- 权威改动清单 report/evidence ---"
git -C "$WT" diff --name-only f77f363 605f960 -- report/evidence | tee -a "$LOG"
say "--- 其中在 f77f363 含箭头的文件 ---"
git -C "$WT" grep -l $'\u21d2' f77f363 -- report/evidence > "$OUT/ev_arrow_old.txt"
git -C "$WT" diff --name-only f77f363 605f960 -- report/evidence > "$OUT/ev_changed.txt"
comm -12 <(sort "$OUT/ev_arrow_old.txt") <(sort "$OUT/ev_changed.txt") | tee -a "$LOG"
say "58 份中改动数=$(comm -12 <(sort "$OUT/ev_arrow_old.txt") <(sort "$OUT/ev_changed.txt") | wc -l)"

say "=== .codex/STATE.md 箭头精确计数 ==="
say "f77f363=$(git -C "$WT" show f77f363:.codex/STATE.md | grep -c $'\u21d2')"
say "605f960=$(git -C "$WT" show 605f960:.codex/STATE.md | grep -c $'\u21d2')"
say "worktree=$(grep -c $'\u21d2' "$WT/.codex/STATE.md")"
echo DONE >> "$LOG"