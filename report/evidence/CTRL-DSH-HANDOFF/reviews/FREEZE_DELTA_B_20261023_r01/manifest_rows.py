import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev,p):
    r=subprocess.run(["git","-C",w6,"show",f"{rev}:{p}"],capture_output=True)
    return None if r.returncode!=0 else r.stdout.decode("utf-8")
F="0725d9cf48aeed21d3ea445ef01575c16b68d950"
for p in ["report/evidence/S6-A/s6a_g0_20261022_r09/delivery_manifest.json",
          "report/evidence/S6-B/s6b_core_20261023_r04/delivery_manifest.json"]:
    o=json.loads(show(F,p))
    print("### %s"%p)
    print("  top keys:", [k for k in o.keys()])
    for row in (o.get("check_statuses") or o.get("checks") or []):
        print("   - %-22s %s"%(row.get("status"), str(row.get("name"))[:100]))
    # 是否绑定 claim_verification / selfproof
    for it in o.get("files",[]):
        if "claim_verification" in it["path"] or "selfproof" in it["path"]:
            print("   FILE %s sha=%s"%(it["path"], it["sha256"][:16]))
    print()
