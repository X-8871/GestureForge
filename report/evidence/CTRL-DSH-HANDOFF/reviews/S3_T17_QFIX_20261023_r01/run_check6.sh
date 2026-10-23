#!/usr/bin/env bash
# 评审核查 6：交付态 record exit 0 复现 + 突变体 JSON 诊断 + 17 份口径 + 157 行普查
set +e
R=/d/FPGA_Competition/tmp/review/S3_T17_QFIX_20261023_r01
WT=/d/codex-worktrees/dbdf
OUT=$R/cmd
LOG=$OUT/exit_codes4.txt
: > "$LOG"
say() { echo "$*" | tee -a "$LOG"; }

REC=report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_record_stage3_delivered.json
CUR=$(git -C "$WT" rev-parse HEAD)

say "=== 1. record 规范键计数与非法键探测（只读） ==="
python -B -c "
import json,sys
d=json.load(open(r'D:/codex-worktrees/dbdf/$REC',encoding='utf-8'))
print('keys=',len(d)); print(sorted(d))
"
say "--- as-is 复跑（当前 HEAD=$CUR） ---"
python -B /d/FPGA_Competition/verification/handoff_check.py --worktree "$WT" --record "$WT/$REC" \
  > "$OUT/item4_handoff_asIs.txt" 2>&1
say "asIs rc=$?"
grep -E '^\[FAIL|^结论|^退出码' "$OUT/item4_handoff_asIs.txt" | tee -a "$LOG"

say "--- 把 base_commit 改为当前 HEAD 的副本（仅评审临时目录） ---"
python -B -c "
import json
p=r'D:/codex-worktrees/dbdf/$REC'
d=json.load(open(p,encoding='utf-8'))
d['base_commit']='$CUR'
json.dump(d,open(r'$R/cmd/record_head_updated.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('written')
"
python -B /d/FPGA_Competition/verification/handoff_check.py --worktree "$WT" \
  --record "$R/cmd/record_head_updated.json" > "$OUT/item4_handoff_headUpdated.txt" 2>&1
say "headUpdated rc=$?"
grep -E '^\[|^结论|^退出码' "$OUT/item4_handoff_headUpdated.txt" | tail -5 | tee -a "$LOG"

say "=== 2. 突变体 selftest 的 cli_regressions 诊断 ==="
python -B -c "
import json
for n in ('m1_arrow_keep_rc','m2_arrow_no_rc','b1_noreconf_selftest'):
    p=rf'$OUT/item2/{n}.json'
    try:
        d=json.load(open(p,encoding='utf-8'))
    except Exception as e:
        print(n,'ERR',e); continue
    print('---',n,d.get('conclusion'),d.get('exit_code'))
    for c in d.get('cli_regressions',[]):
        print('   ',c['name'],'exp',c['expected_exit_code'],'act',c['actual_exit_code'],'json',c['json_written'],'matched',c['matched'])
        print('     stdout_head=',repr(c['stdout_head'])[:180])
        print('     stderr_tail=',repr(c['stderr_tail'])[:220])
"

say "=== 3. f77f363 含箭头的已提交证据文件数（=误改口径） ==="
git -C "$WT" grep -l $'\u21d2' f77f363 -- report/evidence > "$OUT/ev_arrow_old.txt"
say "evidence_files_with_arrow@f77f363=$(wc -l < "$OUT/ev_arrow_old.txt")"
say "--- 逐文件 f77f363 vs 605f960 blob 是否相同 ---"
same=0; diff=0
while read -r f; do
  a=$(git -C "$WT" rev-parse "f77f363:$f" 2>/dev/null)
  b=$(git -C "$WT" rev-parse "605f960:$f" 2>/dev/null)
  if [ "$a" = "$b" ]; then same=$((same+1)); else diff=$((diff+1)); echo "DIFF $f" >> "$LOG"; fi
done < "$OUT/ev_arrow_old.txt"
say "byte_identical=$same  differing=$diff"

say "=== 4. 47 份副本中拼接语句的行号分布 ==="
find "$WT" -name 'cmos_8_16bit*.v' -not -path '*/.git/*' > "$OUT/cmos_dbdf.txt"
while read -r p; do
  ln=$(grep -n 'pdata_o <= {pdata_i_d0,pdata_i};' "$p" 2>/dev/null | head -1 | cut -d: -f1)
  total=$(wc -l < "$p")
  echo "$ln $total $p"
done < "$OUT/cmos_dbdf.txt" | sort -n | awk '{print "line="$1" total_lines="$2" "$3}' | tee -a "$LOG"
echo DONE >> "$LOG"