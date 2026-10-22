import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev, path):
    p=subprocess.run(["git","-C",w6,"show",f"{rev}:{path}"],capture_output=True)
    return None if p.returncode!=0 else p.stdout.decode("utf-8")
BASE="1839766883436f521383f5432446eb67a01ada56"; F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
path="docs/stage6/s6a_stage6_g0_behavior_v1.json"
a=json.loads(show(BASE,path)); b=json.loads(show(F,path))
pa,pb=a["parameters"],b["parameters"]
print("type:",type(pa).__name__,len(pa),type(pb).__name__,len(pb))
print("sample entry:",json.dumps(pa[0],ensure_ascii=False))
