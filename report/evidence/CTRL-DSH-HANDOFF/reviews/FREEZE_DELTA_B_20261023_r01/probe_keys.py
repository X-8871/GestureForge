import json, subprocess, sys, hashlib
w6=r"D:\codex-worktrees\w6"
def show(rev, path):
    p=subprocess.run(["git","-C",w6,"show",f"{rev}:{path}"],capture_output=True)
    if p.returncode!=0: return None
    return p.stdout.decode("utf-8")
BASE="1839766883436f521383f5432446eb67a01ada56"
F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
path="docs/stage6/s6a_stage6_g0_behavior_v1.json"
a=json.loads(show(BASE,path)); b=json.loads(show(F,path))
print("BASE top-level keys:", len(a), sorted(a.keys()))
print("F    top-level keys:", len(b), sorted(b.keys()))
print("keys added:", sorted(set(b)-set(a)))
print("keys removed:", sorted(set(a)-set(b)))
# find params container
for k in a:
    if isinstance(a[k],dict) and k.lower() in ("parameters","params","thresholds","parameter_values"):
        print("PARAM CONTAINER:",k, len(a[k]))
