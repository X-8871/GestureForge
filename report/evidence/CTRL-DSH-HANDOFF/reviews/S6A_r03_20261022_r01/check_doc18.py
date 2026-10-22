import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')
doc = open(r'D:\codex-worktrees\w6\docs\stage6\S6A_stage6_g0_behavior_spec_v1.md', encoding='utf-8').read()
sec = doc.split('## 18.')[1]
names = set(re.findall(r'`([A-Za-z0-9_.\-]+\.(?:json|md|txt))`', sec))
root = r'D:\codex-worktrees\w6\report\evidence\S6-A\s6a_g0_20261022_r03'
missing = [n for n in sorted(names) if not os.path.isfile(os.path.join(root, n))]
print('declared in section 18:', len(names))
print('missing:', missing)
print('declared:', sorted(names))
