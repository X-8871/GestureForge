# 静态复现 s6_g0_selfcheck.py C11 的 STATE 解析分支（第1163-1187行），不运行重型自证
import re, subprocess
from pathlib import Path
w6=Path(r"D:\codex-worktrees\w6")
G="1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e"; F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
def state_at(rev):
    p=subprocess.run(["git","-C",str(w6),"show",f"{rev}:.codex/STATE.md"],capture_output=True)
    return p.stdout.decode("utf-8")
ev_dir = w6/"report/evidence/S6-A/s6a_g0_20261022_r09"
for rev,name in ((F,"F"),(G,"G")):
    text=state_at(rev)
    declared_files=set(); declared_dirs=set()
    for line in text.splitlines():
        if "证据入口" not in line and "report/evidence" not in line: continue
        for token in re.findall(r"`([^`]+)`", line):
            if (re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*\.(json|md|txt|jsonl)", token)
                    and "/" not in token and "\\" not in token):
                declared_files.add(token)
            elif token.startswith("report/evidence/"):
                declared_dirs.add(token.rstrip("/"))
    miss_files=sorted(n for n in declared_files if not (ev_dir/n).is_file())
    miss_dirs=sorted(p for p in declared_dirs if not (w6/p).is_dir())
    print("### %s = %s"%(name,rev))
    print("  declared_files=%d declared_dirs=%d"%(len(declared_files),len(declared_dirs)))
    print("  missing_files=%s"%miss_files)
    print("  missing_dirs=%s"%miss_dirs)
    print("  C11 STATE 分支判定: %s"%("FAIL" if (miss_files or miss_dirs) else "PASS"))
    print()
