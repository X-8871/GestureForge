#!/usr/bin/env bash
# 评审核查 9：交集修正 + 「56 份」候选口径 + 主仓计数
set +e
R=/d/FPGA_Competition/tmp/review/S3_T17_QFIX_20261023_r01
WT=/d/codex-worktrees/dbdf
OUT=$R/cmd
LOG=$OUT/exit_codes6.txt
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

say "=== 修正交集：含箭头 且 在 F3 被改 的已提交证据文件 ==="
git -C "$WT" grep -l $'\u21d2' f77f363 -- report/evidence | sed 's/^f77f363://' | sort > "$OUT/arrows_ev.txt"
git -C "$WT" diff --name-only f77f363 605f960 -- report/evidence | sort > "$OUT/changed_ev.txt"
say "含箭头=$(wc -l < "$OUT/arrows_ev.txt")  被改=$(wc -l < "$OUT/changed_ev.txt")"
comm -12 "$OUT/arrows_ev.txt" "$OUT/changed_ev.txt" | tee -a "$LOG"
say "交集数=$(comm -12 "$OUT/arrows_ev.txt" "$OUT/changed_ev.txt" | wc -l)"
say "未被改的含箭头文件数=$(comm -23 "$OUT/arrows_ev.txt" "$OUT/changed_ev.txt" | wc -l)"

say "=== 「56 份」候选口径 ==="
find "$WT" -name 'cmos_8_16bit*.v' -not -path '*/.git/*' | wc -l | xargs echo "A dbdf *.v (excl .git):"
find "$WT" -name 'cmos_8_16bit*' -not -path '*/.git/*' | wc -l | xargs echo "B dbdf any ext (excl .git):"
find "$WT" -name 'cmos_8_16bit.v' -not -path '*/.git/*' | wc -l | xargs echo "C dbdf exact name:"
find "$WT" -name 'cmos_8_16bit*.v' | wc -l | xargs echo "D dbdf *.v incl .git:"
find /d/FPGA_Competition -name 'cmos_8_16bit*.v' -not -path '*/.git/*' 2>/dev/null | wc -l | xargs echo "E main tree *.v:"
find /d/FPGA -name 'cmos_8_16bit*.v' 2>/dev/null | wc -l | xargs echo "F D:/FPGA *.v:"
find "$WT" /d/FPGA_Competition -name 'cmos_8_16bit*.v' -not -path '*/.git/*' 2>/dev/null | sort -u | wc -l | xargs echo "G dbdf+main unique:"
find "$WT" /d/FPGA_Competition /d/FPGA -name 'cmos_8_16bit*.v' -not -path '*/.git/*' 2>/dev/null | sort -u | wc -l | xargs echo "H dbdf+main+FPGA unique:"

say "=== 主仓 S3-T17 证据目录里的 hw_authorization ==="
find /d/FPGA_Competition/report/evidence -name 'hw_authorization*.json' 2>/dev/null | head -10 | tee -a "$LOG"
say "主仓 report/evidence/S3-T17 列表:"
ls /d/FPGA_Competition/report/evidence/ 2>/dev/null | grep -i 'S3-T17' | tee -a "$LOG"
echo DONE >> "$LOG"