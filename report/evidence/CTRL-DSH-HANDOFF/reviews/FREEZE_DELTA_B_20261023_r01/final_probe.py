import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev,p):
    r=subprocess.run(["git","-C",w6,"show",f"{rev}:{p}"],capture_output=True)
    return None if r.returncode!=0 else r.stdout.decode("utf-8")
F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
for p in ["report/evidence/S6-A/s6a_g0_20261022_r09/claim_verification.json",
          "report/evidence/S6-B/s6b_core_20261023_r04/claim_verification.json"]:
    o=json.loads(show(F,p))
    print("%s"%p)
    print("   generated_at_utc8=%r claims=%d verdict=%r"%(o.get("generated_at_utc8"),len(o.get("claims",[])),o.get("verdict")))
    print("   reproduce=%r"%o.get("reproduce"))
print()
print("### 冻结的 claim_verify.py 期望 claim 集（静态） ###")
import ast
src=show(F,"verification/claim_verify.py")
t=ast.parse(src)
for fn in ("s6a_claims","s6b_claims"):
    f=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==fn][0]
    ids=[e.value for r in f.body if isinstance(r,ast.Return) for e in r.value.elts
         if isinstance(e,ast.Dict) for k,v in zip(e.keys,e.values) if isinstance(k,ast.Constant) and k.value=="id"]
    print("  %s -> %s"%(fn,ids))
