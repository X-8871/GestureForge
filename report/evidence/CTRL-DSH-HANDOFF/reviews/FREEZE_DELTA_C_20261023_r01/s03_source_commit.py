# 检查 3c：source_commit 可达性与 amend 偏离
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import run, show

FULL = {}
for k, s in {"F": "0725d9cf", "G": "1e2a66c", "F2": "33b1fee", "G2": "8ecd92cb",
             "F3": "efb9f191", "F4": "6b8e5f2", "G4": "f5b749e"}.items():
    rc, o, _ = run(["rev-parse", s])
    FULL[k] = o.strip()

rc, out, _ = run(["rev-list", "HEAD"])
reach = set(out.split())
print("#### 可达性（自 HEAD=G4）")
for k, c in FULL.items():
    print(f"  {k:3s} {c} reachable={c in reach}")

rc, out, _ = run(["rev-list", "--all"])
allreach = set(out.split())
print("\n#### 可达性（自 --all）")
for k, c in FULL.items():
    print(f"  {k:3s} reachable_all={c in allreach}")

REVS = ["F2", "G2", "F3", "F4", "G4"]
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
    "report/evidence/S6-A/s6a_g0_20261022_r09_selfproof/transport_clone_selfproof.json",
    "report/evidence/S6-B/s6b_core_20261023_r04_selfproof/transport_clone_selfproof.json",
]

def find_commits(obj, path="", acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("source_commit", "commit", "commit_hash", "delivery_commit", "subject_commit") and isinstance(v, str):
                acc.append((path + "/" + k, v))
            else:
                find_commits(v, path + "/" + str(k), acc)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_commits(v, path + f"[{i}]", acc)
    return acc

for rev in REVS:
    print(f"\n===== {rev} ({FULL[rev][:12]}) =====")
    for p in PATHS:
        rc, out, err = run(["show", f"{rev}:{p}"])
        if rc != 0:
            continue
        try:
            j = json.loads(out)
        except Exception as e:
            print(f"  {p}: JSON 解析失败 {e}")
            continue
        hits = find_commits(j)
        h2 = []
        for k, v in hits:
            h2.append((k, v))
        print(f"  {p}")
        for k, v in h2:
            # 判断该引用是否可达
            rc2, o2, _ = run(["rev-parse", "--verify", "--quiet", v + "^{commit}"])
            if rc2 != 0:
                st = "UNRESOLVABLE(!)"
            else:
                st = "reachable" if o2.strip() in reach else "UNREACHABLE(!)"
            print(f"      {k} = {v[:40]}  -> {st}")

print("\n#### reflog --all（含 amend 痕迹）")
show(["reflog", "--all", "--date=iso", "-40"])
print("\n#### reflog refs/heads/stage6-interact-prep")
show(["log", "-g", "--date=iso", "--format=%gd %H %gs", "stage6-interact-prep"])