import re, hashlib, os, sys
sys.stdout.reconfigure(encoding='utf-8')
doc = open(r'D:\codex-worktrees\w6\docs\stage6\S6A_stage6_g0_behavior_spec_v1.md', encoding='utf-8').read()
sec = doc.split('**上游只读文件 SHA-256')[1].split('**阶段5 修订建议')[0]
pat = r'\|\s*`([^`]+)`[^|]*\|\s*`([0-9a-f]{64})`\s*\|'
rows = re.findall(pat, sec)
print('rows', len(rows))
for p, h in rows:
    cand = [os.path.join(r'D:\codex-worktrees\w6', p), os.path.join(r'D:\FPGA_Competition', p)]
    f = next((c for c in cand if os.path.isfile(c)), None)
    if not f:
        print('MISSING', p)
        continue
    a = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    print('OK   ' if a == h else 'DRIFT', p[-58:], a[:12], h[:12])
