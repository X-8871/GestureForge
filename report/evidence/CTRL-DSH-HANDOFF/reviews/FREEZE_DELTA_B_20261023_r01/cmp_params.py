import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev, path):
    p=subprocess.run(["git","-C",w6,"show",f"{rev}:{path}"],capture_output=True)
    return None if p.returncode!=0 else p.stdout.decode("utf-8")
BASE="1839766883436f521383f5432446eb67a01ada56"; F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
path="docs/stage6/s6a_stage6_g0_behavior_v1.json"
a=json.loads(show(BASE,path)); b=json.loads(show(F,path))

print("### parameters ###")
pa,pb=a["parameters"],b["parameters"]
print("count BASE=%d F=%d"%(len(pa),len(pb)))
print("id set equal:", set(pa)==set(pb), "added:",sorted(set(pb)-set(pa)),"removed:",sorted(set(pa)-set(pb)))
diff=0
for k in sorted(set(pa)|set(pb)):
    va,vb=pa.get(k),pb.get(k)
    if va!=vb:
        diff+=1
        if isinstance(va,dict):
            keys=set(va)|set(vb)
            for kk in sorted(keys):
                if va.get(kk)!=vb.get(kk):
                    print("  FIELD-DIFF %s.%s: %r -> %r"%(k,kk,va.get(kk),vb.get(kk)))
        else:
            print("  DIFF %s: %r -> %r"%(k,va,vb))
print("parameters differing entries:",diff)
pend=[k for k,v in pb.items() if (v.get("value")== "PENDING_APPROVAL") or ("PENDING_APPROVAL" in json.dumps(v))]
print("entries containing PENDING_APPROVAL:",len(pend))
for k in sorted(pb):
    v=pb[k]
    val=v.get("value") if isinstance(v,dict) else v
    if val!="PENDING_APPROVAL": print("   NON-PENDING %s = %r"%(k,val))

print()
print("### ID sets ###")
for key in ["transitions","behavior_rows","predicates","states","actions"]:
    ga,gb=a.get(key),b.get(key)
    def ids(g):
        if isinstance(g,dict): return set(g.keys())
        if isinstance(g,list):
            return set(x.get("id") if isinstance(x,dict) else x for x in g)
        return set()
    ia,ib=ids(ga),ids(gb)
    print("%-14s BASE=%d F=%d equal=%s added=%s removed=%s"%(key,len(ia),len(ib),ia==ib,sorted(ib-ia),sorted(ia-ib)))

print()
print("### semantic diff of other containers ###")
skip={"parameters","revision","status_note","status_label","artifact_version","run_id","supersedes_run_id","parameter_notes","reachability","baseline"}
for k in sorted(a):
    if k in skip: continue
    if a[k]!=b[k]:
        print("  CHANGED container: %s"%k)
        if isinstance(a[k],dict) and isinstance(b[k],dict):
            for kk in sorted(set(a[k])|set(b[k])):
                if a[k].get(kk)!=b[k].get(kk): print("      sub-key %s changed"%kk)
