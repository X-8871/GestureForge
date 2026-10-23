#!/usr/bin/env bash
# 评审核查脚本 3：突变诊断 + 箭头普查（限定范围）+ reflog + cmos 普查 + 行号
set +e
R=/d/FPGA_Competition/tmp/review/S3_T17_QFIX_20261023_r01
C=$R/clonet
OUT=$R/cmd
LOG=$OUT/exit_codes3.txt
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

say "=== A. 突变体内容诊断 ==="
for f in "$R/mutations/analyze_arrow_keep_rc.py" "$R/mutations/analyze_arrow_no_rc.py"; do
  say "--- $f"
  say "arrow_count=$(grep -c $'\u21d2' "$f")"
  say "reconfigure_lines=$(grep -n '_force_utf8_streams' "$f" | tr '\n' '|')"
  say "reason_line=$(grep -n 'WHITE_BIT_NOT_SET' "$f" | head -1)"
done
say "--- mutations dir listing"; ls -l "$R/mutations" >> "$LOG" 2>&1

say "=== B. 直接手跑 m2 突变体（PYTHONIOENCODING=gbk，归档帧） ==="
cd "$C"
PYTHONIOENCODING=gbk python -B "$R/mutations/analyze_arrow_no_rc.py" \
  --frame report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/bars_raw_frame_full.bin \
  --json-out "$R/mutations/manual_m2.json" > "$R/mutations/manual_m2.stdout.txt" 2>&1
say "manual_m2 rc=$?"
say "manual_m2_json_landed=$([ -f "$R/mutations/manual_m2.json" ] && echo yes || echo no)"
tail -3 "$R/mutations/manual_m2.stdout.txt" | tee -a "$LOG"

say "=== C. 箭头普查（限定 report/evidence + .codex + scripts） ==="
for rev in f77f363 605f960; do
  git grep -c $'\u21d2' "$rev" -- report/evidence .codex scripts > "$OUT/arrows_$rev.txt"
  echo "$rev files_with_arrow=$(wc -l < "$OUT/arrows_$rev.txt")" >> "$LOG"
done
sed 's/^[0-9a-f]*://' "$OUT/arrows_f77f363.txt" | sort > "$OUT/arrows_old.txt"
sed 's/^[0-9a-f]*://' "$OUT/arrows_605f960.txt" | sort > "$OUT/arrows_new.txt"
say "--- 旧有箭头但新无（箭头被删的文件） ---"
comm -23 "$OUT/arrows_old.txt" "$OUT/arrows_new.txt" | tee -a "$LOG"
say "--- 新增箭头（新有旧无） ---"
comm -13 "$OUT/arrows_old.txt" "$OUT/arrows_new.txt" | tee -a "$LOG"
say "--- 计数不同的文件 ---"
join -j 2 <(sed 's/^[0-9a-f]*://' "$OUT/arrows_f77f363.txt" | sort -k1,1) \
          <(sed 's/^[0-9a-f]*://' "$OUT/arrows_605f960.txt" | sort -k1,1) \
  | awk '$2!=$3 {print "DELTA", $1, "old="$2, "new="$3}' | tee -a "$LOG"
say "--- 被点名的两个历史证据是否仍有箭头 ---"
say "handoff_check_claim.json @605f960: $(git show 605f960:report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_check_claim.json 2>/dev/null | grep -c $'\u21d2')"
say "fix_record @605f960: $(git show 605f960:report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/fix_record.md 2>/dev/null | grep -c $'\u21d2')"
say "--- 上述两文件 f77f363 vs 605f960 blob 是否逐字节相同 ---"
for f in report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_check_claim.json \
         report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/fix_record.md; do
  a=$(git rev-parse "f77f363:$f" 2>/dev/null); b=$(git rev-parse "605f960:$f" 2>/dev/null)
  say "$f  old=$a new=$b  same=$([ "$a" = "$b" ] && echo YES || echo NO)"
done
say "--- 全部已提交证据中箭头被删的文件数（report/evidence 范围） ---"
comm -23 "$OUT/arrows_old.txt" "$OUT/arrows_new.txt" | grep '^report/evidence' | wc -l | tee -a "$LOG"

say "=== D. reflog（在 dbdf，不是克隆） ==="
git -C /d/codex-worktrees/dbdf reflog show codex/stage3-video | head -8 | tee -a "$LOG"
say "--- 图形 ---"
git -C /d/codex-worktrees/dbdf log --graph --oneline -5 | cat | tee -a "$LOG"
say "--- 祖先关系 ---"
git -C /d/codex-worktrees/dbdf merge-base --is-ancestor f77f363 605f960 && say "f77f363 -> 605f960 ancestor=YES"
git -C /d/codex-worktrees/dbdf merge-base --is-ancestor 605f960 975f3a5 && say "605f960 -> 975f3a5 ancestor=YES"

say "=== E. cmos_8_16bit* 普查 ==="
find /d/codex-worktrees/dbdf -name 'cmos_8_16bit*.v' -not -path '*/.git/*' > "$OUT/cmos_dbdf.txt"
say "dbdf_total=$(wc -l < "$OUT/cmos_dbdf.txt")"
awk -F/ '{print $5"/"$6}' "$OUT/cmos_dbdf.txt" | sort | uniq -c | sort -rn | head -20 | tee -a "$LOG"
find /d/FPGA_Competition -maxdepth 6 -name 'cmos_8_16bit*.v' -not -path '*/.git/*' > "$OUT/cmos_main.txt"
say "main_total=$(wc -l < "$OUT/cmos_main.txt")"
find /d/FPGA -name 'cmos_8_16bit*.v' 2>/dev/null > "$OUT/cmos_fpga.txt"
say "D_FPGA_total=$(wc -l < "$OUT/cmos_fpga.txt")"
say "dbdf+main+D_FPGA=$(cat "$OUT/cmos_dbdf.txt" "$OUT/cmos_main.txt" "$OUT/cmos_fpga.txt" | sort -u | wc -l)"
say "--- 含拼接语句的比例 ---"
say "dbdf contains=$(grep -rl 'pdata_o <= {pdata_i_d0,pdata_i};' $(cat "$OUT/cmos_dbdf.txt") 2>/dev/null | wc -l)"

say "=== F. 厂商参考文件行号 ==="
say "blob_bytes=$(wc -c < "$OUT/item3/ref_head.blob")"
say "blob_lines=$(wc -l < "$OUT/item3/ref_head.blob")"
say "pattern_line=$(grep -n 'pdata_o <= {pdata_i_d0,pdata_i};' "$OUT/item3/ref_head.blob" | cut -d: -f1)"
say "line157=[$(sed -n '157p' "$OUT/item3/ref_head.blob")]"
say "line156=[$(sed -n '156p' "$OUT/item3/ref_head.blob")]"
say "line158=[$(sed -n '158p' "$OUT/item3/ref_head.blob")]"
say "--- CRLF 计数（blob 与 dbdf 工作区） ---"
say "blob_crlf=$(grep -c $'\r' "$OUT/item3/ref_head.blob")"
say "dbdf_wt_crlf=$(grep -c $'\r' /d/codex-worktrees/dbdf/report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v)"
say "worktree_lines=$(wc -l < /d/codex-worktrees/dbdf/report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v)"
say "worktree_pattern_line=$(grep -n 'pdata_o <= {pdata_i_d0,pdata_i};' /d/codex-worktrees/dbdf/report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v | cut -d: -f1)"
echo DONE >> "$LOG"