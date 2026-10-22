import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev, path):
    p=subprocess.run(["git","-C",w6,"show",f"{rev}:{path}"],capture_output=True)
    return None if p.returncode!=0 else p.stdout.decode("utf-8")
BASE="1839766883436f521383f5432446eb67a01ada56"; F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
path="docs/stage6/s6a_stage6_g0_behavior_v1.json"
a=json.loads(show(BASE,path)); b=json.loads(show(F,path))

print("### 24 项参数逐字段比对 (BASE 1839766 -> F) ###")
pa={x["id"]:x for x in a["parameters"]}; pb={x["id"]:x for x in b["parameters"]}
print("count BASE=%d F=%d"%(len(pa),len(pb)))
print("ID set equal:", set(pa)==set(pb), "| added:",sorted(set(pb)-set(pa)),"| removed:",sorted(set(pa)-set(pb)))
ndiff=0
for k in sorted(set(pa)|set(pb)):
    va,vb=pa.get(k,{}),pb.get(k,{})
    for kk in sorted(set(va)|set(vb)):
        if va.get(kk)!=vb.get(kk):
            ndiff+=1; print("  FIELD-DIFF %s.%s: %r -> %r"%(k,kk,va.get(kk),vb.get(kk)))
print("TOTAL parameter field differences:", ndiff)
nonpend=[(k,v.get("approval_status"),v.get("draft_value")) for k,v in sorted(pb.items()) if v.get("approval_status")!="PENDING_APPROVAL"]
print("F 非 PENDING_APPROVAL 项数:",len(nonpend), nonpend)
print("F PENDING_APPROVAL 项数:",sum(1 for v in pb.values() if v.get("approval_status")=="PENDING_APPROVAL"))
print("BASE PENDING_APPROVAL 项数:",sum(1 for v in pa.values() if v.get("approval_status")=="PENDING_APPROVAL"))

print()
print("### ID 集合比对 ###")
def ids(g):
    if isinstance(g,dict): return set(g.keys())
    if isinstance(g,list): return set(x.get("id") if isinstance(x,dict) else x for x in g)
    return set()
for key in ["transitions","behavior_rows","predicates","states","actions","open_decisions","hard_invariants"]:
    ia,ib=ids(a.get(key)),ids(b.get(key))
    tag="OK" if ia==ib else "**DIFF**"
    print("%-16s BASE=%3d F=%3d %s added=%s removed=%s"%(key,len(ia),len(ib),tag,sorted(ib-ia),sorted(ia-ib)))

print()
print("### 其余容器语义变化 ###")
skip={"parameters","revision","status_note","status_label","artifact_version","run_id","supersedes_run_id","parameter_notes","reachability","baseline"}
for k in sorted(a):
    if k in skip: continue
    if a[k]!=b[k]:
        print("  CHANGED: %s"%k)
        if isinstance(a[k],dict) and isinstance(b[k],dict):
            for kk in sorted(set(a[k])|set(b[k])):
                if a[k].get(kk)!=b[k].get(kk): print("      sub-key: %s"%kk)
        elif isinstance(a[k],list) and isinstance(b[k],list):
            print("      len %d -> %d"%(len(a[k]),len(b[k])))
