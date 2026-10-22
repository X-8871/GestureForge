import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev, path):
    p=subprocess.run(["git","-C",w6,"show",f"{rev}:{path}"],capture_output=True)
    return None if p.returncode!=0 else p.stdout.decode("utf-8")
BASE="1839766883436f521383f5432446eb67a01ada56"; F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
path="docs/stage6/s6a_stage6_g0_behavior_v1.json"
a=json.loads(show(BASE,path)); b=json.loads(show(F,path))
ta={x["id"]:x for x in a["transitions"]}; tb={x["id"]:x for x in b["transitions"]}
for k in sorted(ta):
    va,vb=ta[k],tb[k]
    for kk in sorted(set(va)|set(vb)):
        if va.get(kk)!=vb.get(kk):
            print("transitions[%s].%s:\n   BASE=%r\n   F   =%r"%(k,kk,va.get(kk),vb.get(kk)))
