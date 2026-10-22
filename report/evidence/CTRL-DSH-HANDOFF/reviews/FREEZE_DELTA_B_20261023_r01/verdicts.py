import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev, path):
    p=subprocess.run(["git","-C",w6,"show",f"{rev}:{path}"],capture_output=True)
    return None if p.returncode!=0 else p.stdout.decode("utf-8")
F="0725d9cf48aeed21d3ea445ef01575c16b68d950"; G="1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e"
files=[
 "report/evidence/S6-A/s6a_g0_20261022_r09_selfproof/export_selfproof.json",
 "report/evidence/S6-A/s6a_g0_20261022_r09_selfproof/transport_clone_selfproof.json",
 "report/evidence/S6-B/s6b_core_20261023_r04_selfproof/export_selfproof.json",
 "report/evidence/S6-B/s6b_core_20261023_r04_selfproof/transport_clone_selfproof.json",
 "report/evidence/S6-A/s6a_g0_20261022_r09/delivery_manifest.json",
 "report/evidence/S6-B/s6b_core_20261023_r04/delivery_manifest.json",
 "report/evidence/S6-B/s6b_core_20261023_r04/claim_verification.json",
 ".codex/STATE.md",
]
def verdicts(o, path=""):
    out=[]
    if isinstance(o,dict):
        for k,v in o.items():
            if k=="verdict" or "verdict" in k.lower() or k.endswith("_status"):
                if isinstance(v,str) and ("PROVEN" in v or v in ("PASS","FAIL")): out.append((path+"/"+k, v))
            out+=verdicts(v, path+"/"+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): out+=verdicts(v, path+f"[{i}]")
    return out
for rev,name in ((F,"F"),(G,"G")):
    print("="*70); print("### %s = %s ###"%(name,rev))
    for f in files:
        raw=show(rev,f)
        if raw is None: print("  [missing] %s"%f); continue
        if f.endswith(".json"):
            try: o=json.loads(raw)
            except Exception as e: print("  [parse-err] %s %s"%(f,e)); continue
            vs=verdicts(o)
            subj=[(s.get("label"),s.get("verdict"),s.get("subject")) for s in (o.get("subjects") or [])]
            print("  %s"%f)
            print("     top-level verdict: %r"%o.get("verdict"))
            for s in subj: print("     subject: label=%r verdict=%r subject=%r"%s)
            for p,v in vs: print("     field %s = %r"%(p,v))
        else:
            lines=[l for l in raw.splitlines() if "SELF_PROVEN" in l or "自证" in l or "1e2a66c" in l or "0725d9c" in l]
            print("  %s (text)"%f)
            for l in lines[:25]: print("     | %s"%l)
