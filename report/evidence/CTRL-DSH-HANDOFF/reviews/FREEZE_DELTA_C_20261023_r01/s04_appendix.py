# 检查 1/4：入库附录与套件产物（在 w6 只读读取）
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import run

G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"
F4 = "6b8e5f2a23ce6f7dec41fc9992141b3423612081"


def show_json(rev, path, label=""):
    rc, out, err = run(["show", f"{rev}:{path}"])
    if rc != 0:
        print(f"[缺失] {rev[:8]}:{path}")
        return None
    try:
        return json.loads(out)
    except Exception as e:
        print(f"[非JSON] {path}: {e}")
        return None


for rev, tag in [(F4, "F4"), (G4, "G4")]:
    print(f"\n################ {tag} = {rev[:12]} ################")
    for pkg, rundir in [("s6a", "report/evidence/S6-A/s6a_g0_20261023_r10"),
                        ("s6b", "report/evidence/S6-B/s6b_core_20261023_r05")]:
        print(f"\n--- {pkg} / {rundir} ---")
        j = show_json(rev, f"{rundir}/claim_verification.json")
        if j:
            print(f"  verdict            = {j.get('verdict')}")
            print(f"  claims_declared    = {j.get('claims_declared')}")
            print(f"  claims_recorded    = {j.get('claims_recorded')}")
            print(f"  count_ok           = {j.get('count_ok')}")
            print(f"  readonly_violations= {j.get('readonly_violations')}")
            print(f"  generated_at_utc8  = {j.get('generated_at_utc8')}")
            print(f"  n(claims[])        = {len(j.get('claims') or [])}")
            for c in (j.get("claims") or []):
                print(f"     - {c['claim_id']:42s} exit={c['exit_code']!s:>5s} expect={c['expected_exit']!s:>5s} {c['verdict']}")
        t = show_json(rev, f"{rundir}/tool_self_tests.json")
        if t:
            print(f"  tool_self_tests: verdict={t.get('verdict')} cases={len(t.get('cases') or [])}")
            print(f"    keys={sorted(t.keys())}")
            for c in (t.get("cases") or []):
                extra = {k: c[k] for k in c if k not in ('case_id', 'verdict', 'command', 'exit_code', 'expect_exit', 'observable')}
                print(f"     - {c.get('case_id'):40s} exit={c.get('exit_code')!s:>6s} expect={c.get('expect_exit')!s:>6s} {c.get('verdict')}  {json.dumps(extra, ensure_ascii=False)[:120]}")
        d = show_json(rev, f"{rundir}/delivery_manifest.json")
        if d:
            print(f"  delivery_manifest: run_id={d.get('run_id')} source_commit={d.get('source_commit')}")
            checks = d.get("checks") or []
            for k in checks:
                print(f"     check: {str(k)[:150]}")
        l = show_json(rev, f"{rundir}/limitations_not_executed.json")
        if l:
            print(f"  limitations keys={sorted(l.keys())}")
            txt = json.dumps(l, ensure_ascii=False)
            for tok in ["F2", "amend", "可达", "tool_self_tests", "claim_verif", "20 分钟", "HEAD"]:
                if tok in txt:
                    print(f"     含 token '{tok}'")