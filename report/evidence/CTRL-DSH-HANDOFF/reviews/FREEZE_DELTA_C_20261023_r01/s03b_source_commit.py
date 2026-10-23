# 检查 3c-fix：source_commit / subject 可达性（用完整哈希）
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import run

FULL = {"F": "0725d9cf48aeed21d3ea445ef01575c16b68d950",
        "G": "1e2a66c904b15ed7e8a01206c3c2fe4a43dc760e",
        "F2": "33b1fee30af1974560fa0b94bf6c6662d3e5d1e0",
        "G2": "8ecd92cb35a34c29fc9570d5fcbed955f2063fd8",
        "F3a": "66f45dd47056261720f55abc7d661bafd8714970",   # 被 amend 掉的旧 F3
        "F3": "efb9f191c67fff307366f9552059ba7a5720b477",
        "F4": "6b8e5f2a23ce6f7dec41fc9992141b3423612081",
        "G4": "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"}

rc, out, _ = run(["rev-list", "HEAD"])
reach = set(out.split())

print("#### 可达性（自 HEAD=G4）")
for k, c in FULL.items():
    rc2, o2, _ = run(["cat-file", "-t", c])
    print(f"  {k:4s} {c}  objtype={o2.strip() or 'MISSING'}  reachable={c in reach}")

PATHS = [
    "report/evidence/S6-A/s6a_g0_20261023_r10/delivery_manifest.json",
    "report/evidence/S6-A/s6a_g0_20261023_r10/inputs_manifest.json",
    "report/evidence/S6-A/s6a_g0_20261023_r10/selfcheck_result.json",
    "report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/export_selfproof.json",
    "report/evidence/S6-A/s6a_g0_20261023_r10_selfproof/transport_clone_selfproof.json",
    "report/evidence/S6-B/s6b_core_20261023_r05/delivery_manifest.json",
    "report/evidence/S6-B/s6b_core_20261023_r05/inputs_manifest.json",
    "report/evidence/S6-B/s6b_core_20261023_r05_selfproof/export_selfproof.json",
    "report/evidence/S6-B/s6b_core_20261023_r05_selfproof/transport_clone_selfproof.json",
]

KEYS = ("source_commit", "commit", "commit_hash", "delivery_commit", "subject_commit",
        "source_commit_resolvable", "subjects", "verdict", "run_id")


def walk(obj, path="", acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in KEYS:
                acc.append((path + "/" + k, v))
            walk(v, path + "/" + str(k), acc)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, path + f"[{i}]", acc)
    return acc


for rev in ["F2", "G2", "F3a", "F3", "F4", "G4"]:
    print(f"\n========== {rev} ({FULL[rev][:12]}) ==========")
    for p in PATHS:
        rc2, out2, err2 = run(["show", f"{FULL[rev]}:{p}"])
        if rc2 != 0:
            print(f"  [缺失] {p}")
            continue
        try:
            j = json.loads(out2)
        except Exception as e:
            print(f"  [非 JSON] {p}: {e}")
            continue
        print(f"  {p}")
        for k, v in walk(j):
            s = json.dumps(v, ensure_ascii=False)
            if len(s) > 160:
                s = s[:160] + "..."
            print(f"      {k} = {s}")
            if "commit" in k and isinstance(v, str) and len(v) >= 7:
                rc3, o3, _ = run(["rev-parse", "--verify", "--quiet", v + "^{commit}"])
                if rc3 != 0:
                    print(f"          -> UNRESOLVABLE(!)")
                else:
                    print(f"          -> {'reachable' if o3.strip() in reach else 'UNREACHABLE(!)'}")
            if k.endswith("subjects") and isinstance(v, list):
                for s_item in v:
                    for part in (s_item if isinstance(s_item, list) else [s_item]):
                        if isinstance(part, str) and len(part) >= 7 and any(ch in part for ch in "0123456789abcdef"):
                            tok = part.split()[0] if " " in part else (part[:40] if len(part) >= 40 else None)
                            if tok and len(tok) >= 7:
                                rc3, o3, _ = run(["rev-parse", "--verify", "--quiet", tok + "^{commit}"])
                                st = "UNRESOLVABLE(!)" if rc3 != 0 else ("reachable" if o3.strip() in reach else "UNREACHABLE(!)")
                                print(f"          subject-token {tok[:12]} -> {st}")