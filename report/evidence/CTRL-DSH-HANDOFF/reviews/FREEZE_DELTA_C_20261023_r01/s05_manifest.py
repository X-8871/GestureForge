# 检查 5：r10/r05 附录与清单的机器声明（只读）
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import run

F = "0725d9cf48aeed21d3ea445ef01575c16b68d950"
G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"

runs = {
    "r10@G4": (G4, "report/evidence/S6-A/s6a_g0_20261023_r10"),
    "r09@F":  (F,  "report/evidence/S6-A/s6a_g0_20261022_r09"),
    "r05@G4": (G4, "report/evidence/S6-B/s6b_core_20261023_r05"),
    "r04@F":  (F,  "report/evidence/S6-B/s6b_core_20261023_r04"),
}


def get(rev, path):
    rc, out, err = run(["show", f"{rev}:{path}"])
    return (out if rc == 0 else None)


print("################ 交付清单 check 明细对比 ################")
for label, (rev, d) in runs.items():
    print(f"\n=== {label} / {d}/delivery_manifest.json ===")
    t = get(rev, f"{d}/delivery_manifest.json")
    if not t:
        print("  [缺失]")
        continue
    j = json.loads(t)
    print(f"  run_id={j.get('run_id')} source_commit={str(j.get('source_commit'))[:12]} generated={j.get('generated_at_utc8')}")
    for c in (j.get("checks") or []):
        print(f"   - status={c.get('status'):8s} exit={str(c.get('exit_code')):>6s} name={str(c.get('name'))[:80]}")
        if c.get("status") not in ("PASS",) or c.get("exit_code") not in (0,):
            print(f"       reason={str(c.get('reason'))[:160]}")

print("\n################ fix_record.md（r10）################")
t = get(G4, "report/evidence/S6-A/s6a_g0_20261023_r10/fix_record.md")
print(t)

print("\n################ r10 limitations_not_executed.json ################")
t = get(G4, "report/evidence/S6-A/s6a_g0_20261023_r10/limitations_not_executed.json")
print(json.dumps(json.loads(t), ensure_ascii=False, indent=2))

print("\n################ r10 fresh_selfcheck_pair.json ################")
t = get(G4, "report/evidence/S6-A/s6a_g0_20261023_r10/fresh_selfcheck_pair.json")
print(json.dumps(json.loads(t), ensure_ascii=False, indent=2))

print("\n################ r05 s6b_fresh_evidence_pair.json ################")
t = get(G4, "report/evidence/S6-B/s6b_core_20261023_r05/s6b_fresh_evidence_pair.json")
print(json.dumps(json.loads(t), ensure_ascii=False, indent=2))