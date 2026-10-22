import json, subprocess
w6=r"D:\codex-worktrees\w6"
def show(rev,p):
    r=subprocess.run(["git","-C",w6,"show",f"{rev}:{p}"],capture_output=True)
    return None if r.returncode!=0 else r.stdout.decode("utf-8")
G="1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e"
for p in ["report/evidence/S6-A/s6a_g0_20261022_r09/claim_verification.json",
          "report/evidence/S6-B/s6b_core_20261023_r04/claim_verification.json"]:
    o=json.loads(show(G,p))
    print("### %s"%p)
    print("  verdict=%r generated=%r"%(o.get("verdict"),o.get("generated_at")))
    for c in o.get("claims",[]):
        cid=c.get("claim_id"); print("   - %-28s exit=%s expect=%s verdict=%s"%(cid,c.get("exit_code"),c.get("expected_exit"),c.get("verdict")))
    print()
