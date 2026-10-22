import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev,p):
    r=subprocess.run(["git","-C",w6,"show",f"{rev}:{p}"],capture_output=True)
    return None if r.returncode!=0 else r.stdout.decode("utf-8")
G="1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e"
o=json.loads(show(G,"report/evidence/S6-B/s6b_core_20261023_r04/limitations_not_executed.json"))
def walk(x,path=""):
    if isinstance(x,dict):
        for k,v in x.items(): walk(v,path+"/"+k)
    elif isinstance(x,list):
        for i,v in enumerate(x): walk(v,path+f"[{i}]")
    elif isinstance(x,str):
        if any(t in x for t in ("新鲜","两步","fresh","20 分钟","BOTH","未建","替代")):
            print("  %s: %s"%(path,x[:300]))
walk(o)
print("--- top keys:", list(o.keys()))
