import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev,p):
    r=subprocess.run(["git","-C",w6,"show",f"{rev}:{p}"],capture_output=True)
    return None if r.returncode!=0 else r.stdout.decode("utf-8")
BASE="1839766883436f521383f5432446eb67a01ada56"; F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
print("### 1839766 版 claim_verify.py 是否也有同一处不可达 append ###")
src=show(BASE,"verification/claim_verify.py")
import ast
t=ast.parse(src)
mf=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name=="main"][0]
for n in ast.walk(mf):
    if isinstance(n,ast.If) and any(isinstance(s,ast.Return) for s in n.body):
        body=n.body; idx=[i for i,s in enumerate(body) if isinstance(s,ast.Return)]
        for i in idx:
            print("  BASE 1839766: if line %d, return 之后 %d 条语句 %s"%(n.lineno,len(body[i+1:]),[(type(x).__name__,x.lineno) for x in body[i+1:]]))
print()
print("### r09 claim_verification.json 全文 ###")
print(show(F,"report/evidence/S6-A/s6a_g0_20261022_r09/claim_verification.json"))
