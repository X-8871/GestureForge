#!/usr/bin/env bash
# item2 补充突变试验 + item3(N-1) + item5 初步核查
set +e
R=/d/FPGA_Competition/tmp/review/S3_T17_QFIX_20261023_r01
C=$R/clonet
OUT=$R/cmd
MUT=$R/mutations
mkdir -p "$MUT" "$OUT/item3" "$OUT/item5"
: > "$OUT/exit_codes2.txt"
log() { echo "$*" | tee -a "$OUT/exit_codes2.txt"; }

# 突变 m1：F3 版恢复 U+21D2（保留 reconfigure）
python - "$C/scripts/stage3_t17/analyze_t17_bit_integrity.py" "$MUT/analyze_arrow_keep_rc.py" "$MUT/analyze_arrow_no_rc.py" <<'PY'
import sys
src = open(sys.argv[1], encoding="utf-8").read()
print("orig_arrow_count=", src.count("\u21d2"))
arrowed = src.replace("缺位）", "缺位\uff09")  # no-op guard
# 在 not_discriminated 的 reason 中恢复 U+21D2
needle = "=>(图文无损" if "=>(图文无损" in src else None
import re
m = re.search(r'"WHITE_BIT_NOT_SET[^"]*"', src)
print("reason_literal=", m.group(0) if m else None)
assert m, "reason literal not found"
new_literal = m.group(0).replace("=>", "\u21d2")
m1 = src.replace(m.group(0), new_literal, 1)
assert m1.count("\u21d2") == src.count("\u21d2") + 1
lines = m1.split("\n")
m2 = "\n".join(ln for ln in lines if ln.strip() != "_force_utf8_streams()")
assert len(m2.split("\n")) == len(lines) - 1
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(m1)   # 保留 reconfigure
open(sys.argv[3], "w", encoding="utf-8", newline="\n").write(m2)   # 去掉 reconfigure
print("mutants_written arrows:", m1.count("\u21d2"), m2.count("\u21d2"))
PY

python -B "$MUT/analyze_arrow_keep_rc.py" --selftest --repo-root "$C" --fixture-dir "$MUT/fx_keep" --json-out "$OUT/item2/m1_arrow_keep_rc.json" > "$OUT/item2/m1_arrow_keep_rc.stdout.txt" 2>&1
log "m1_arrow_keep_rc_selftest rc=$?"
python -B "$MUT/analyze_arrow_no_rc.py" --selftest --repo-root "$C" --fixture-dir "$MUT/fx_norc" --json-out "$OUT/item2/m2_arrow_no_rc.json" > "$OUT/item2/m2_arrow_no_rc.stdout.txt" 2>&1
log "m2_arrow_no_rc_selftest rc=$?"

# ---------------- item3 N-1 ----------------
REF_REL=report/evidence/S3-T05/t05_github_ref_20261020_r01/cmos_8_16bit_ref.v
cd "$C"
echo "=== ref existence (clone worktree) ===" >> "$OUT/exit_codes2.txt"
ls -l "$C/$REF_REL" >> "$OUT/exit_codes2.txt" 2>&1
echo "=== blob content sha256/size at HEAD and f77f363 (clone) ===" >> "$OUT/exit_codes2.txt"
git cat-file blob HEAD:$REF_REL > "$OUT/item3/ref_head.blob"
git cat-file blob f77f363:$REF_REL > "$OUT/item3/ref_f77f363.blob"
sha256sum "$OUT/item3/ref_head.blob" "$OUT/item3/ref_f77f363.blob" >> "$OUT/exit_codes2.txt"
wc -c "$OUT/item3/ref_head.blob" >> "$OUT/exit_codes2.txt"
echo "=== line 157 of the blob ===" >> "$OUT/exit_codes2.txt"
sed -n '157p' "$OUT/item3/ref_head.blob" | tee -a "$OUT/exit_codes2.txt" | cat -A | head -2 >> "$OUT/exit_codes2.txt"
echo "=== occurrence count of the pattern inside the ref file ===" >> "$OUT/exit_codes2.txt"
grep -c 'pdata_o <= {pdata_i_d0,pdata_i};' "$OUT/item3/ref_head.blob" >> "$OUT/exit_codes2.txt"
echo "=== disk census: cmos_8_16bit*.v under dbdf (excl .git) ===" >> "$OUT/exit_codes2.txt"
find /d/codex-worktrees/dbdf -name 'cmos_8_16bit*.v' -not -path '*/.git/*' | wc -l >> "$OUT/exit_codes2.txt"
find /d/codex-worktrees/dbdf -name 'cmos_8_16bit*.v' -not -path '*/.git/*' > "$OUT/item3/census_dbdf.txt"
echo "=== disk census: under D:/FPGA_Competition (excl .git) ===" >> "$OUT/exit_codes2.txt"
find /d/FPGA_Competition -name 'cmos_8_16bit*.v' -not -path '*/.git/*' > "$OUT/item3/census_main.txt"
wc -l < "$OUT/item3/census_main.txt" >> "$OUT/exit_codes2.txt"
echo "=== census: exact-name cmos_8_16bit.v under dbdf ===" >> "$OUT/exit_codes2.txt"
find /d/codex-worktrees/dbdf -name 'cmos_8_16bit.v' -not -path '*/.git/*' | wc -l >> "$OUT/exit_codes2.txt"
echo "=== of those, how many contain the pattern ===" >> "$OUT/exit_codes2.txt"
grep -rl 'pdata_o <= {pdata_i_d0,pdata_i};' $(find /d/codex-worktrees/dbdf -name 'cmos_8_16bit*.v' -not -path '*/.git/*') 2>/dev/null | wc -l >> "$OUT/exit_codes2.txt"

# ---------------- item5 初步：改动文件与箭头计数 ----------------
echo "=== changed files f77f363..605f960 ===" >> "$OUT/exit_codes2.txt"
git diff --name-status f77f363 605f960 >> "$OUT/exit_codes2.txt"
echo "=== arrow counts per changed file (f77f363 / 605f960) ===" >> "$OUT/exit_codes2.txt"
for f in $(git diff --name-only f77f363 605f960); do
  a=$(git show f77f363:"$f" 2>/dev/null | grep -c $'\u21d2')
  b=$(git show 605f960:"$f" 2>/dev/null | grep -c $'\u21d2')
  if [ "$a" != "$b" ]; then echo "ARROW_DELTA $f  old=$a new=$b" >> "$OUT/exit_codes2.txt"; fi
done
echo "=== reflog ===" >> "$OUT/exit_codes2.txt"
git reflog show codex/stage3-video | head -6 >> "$OUT/exit_codes2.txt"
echo "=== F3/G4 file-name intersection ===" >> "$OUT/exit_codes2.txt"
git diff --name-only f77f363 605f960 | sort > "$OUT/item5/f3.txt"
git diff --name-only 605f960 975f3a5 | sort > "$OUT/item5/g4.txt"
comm -12 "$OUT/item5/f3.txt" "$OUT/item5/g4.txt" >> "$OUT/exit_codes2.txt"
echo "=== scripts under review identical F3 vs HEAD? ===" >> "$OUT/exit_codes2.txt"
git diff --name-only 605f960 975f3a5 -- scripts/ | wc -l >> "$OUT/exit_codes2.txt"
echo "=== hw artifacts ===" >> "$OUT/exit_codes2.txt"
find /d/codex-worktrees/dbdf -name 'hw_authorization.json' -not -path '*/.git/*' >> "$OUT/exit_codes2.txt" 2>&1
echo "hw_auth_count=$(find /d/codex-worktrees/dbdf -name 'hw_authorization.json' -not -path '*/.git/*' | wc -l)" >> "$OUT/exit_codes2.txt"
cat "$OUT/exit_codes2.txt"