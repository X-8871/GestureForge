# 检查 2：F -> F4 增量范围 + 行为表/24 参数逐字段比对
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g import show, run

F = "0725d9cf48aeed21d3ea445ef01575c16b68d950"
F4 = "6b8e5f2a23ce6f7dec41fc9992141b3423612081"
G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"
CHAIN = ["1e2a66c", "33b1fee", "8ecd92cb", "efb9f191", "6b8e5f2", "f5b749e"]
LABEL = {"1e2a66c": "G", "33b1fee": "F2", "8ecd92cb": "G2", "efb9f191": "F3",
         "6b8e5f2": "F4", "f5b749e": "G4"}

print("#### 每个中间提交改动的非证据文件（name-status）")
for c in CHAIN:
    rc, out, _ = run(["diff", "--name-status", c + "^", c])
    files = [l.split("\t") for l in out.strip().splitlines()]
    non_ev = [l for l in files if len(l) > 1 and not l[1].startswith("report/evidence/")]
    print(f"\n=== {LABEL[c]} {c} —— 共 {len(files)} 文件，其中非 report/evidence 的 {len(non_ev)} 个")
    for l in non_ev:
        print("   ", "\t".join(l))
    ev_dirs = sorted({"/".join(l[1].split("/")[:5]) for l in files if len(l) > 1 and l[1].startswith("report/evidence/")})
    print("    证据目录:", ev_dirs)

print("\n\n#### 累积 F -> F4: 非 report/evidence 文件")
rc, out, _ = run(["diff", "--name-status", F, F4])
files = [l.split("\t") for l in out.strip().splitlines()]
for l in files:
    if not l[1].startswith("report/evidence/"):
        print("   ", "\t".join(l))
print("  证据文件数 =", len([l for l in files if l[1].startswith("report/evidence/")]))
print("  总计 =", len(files))

# ---------- 行为表 JSON 深比对 ----------
BT = "docs/stage6/s6a_stage6_g0_behavior_v1.json"


def blob(rev, path):
    rc, out, err = run(["show", f"{rev}:{path}"])
    assert rc == 0, (rev, path, err)
    return out


def deepdiff(a, b, path=""):
    out = []
    if type(a) is not type(b):
        out.append((path, repr(a), repr(b)))
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((path + "/" + str(k), "<MISSING>", repr(b[k])))
            elif k not in b:
                out.append((path + "/" + str(k), repr(a[k]), "<MISSING>"))
            else:
                out += deepdiff(a[k], b[k], path + "/" + str(k))
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path + "/<len>", str(len(a)), str(len(b))))
        for i in range(min(len(a), len(b))):
            out += deepdiff(a[i], b[i], path + f"[{i}]")
    else:
        if a != b:
            out.append((path, repr(a), repr(b)))
    return out


ja = json.loads(blob(F, BT))
jb = json.loads(blob(F4, BT))
print("\n\n#### 行为表 F vs F4 深比对")
d = deepdiff(ja, jb)
print(f"差异条数 = {len(d)}")
for p, x, y in d:
    print(f"  {p}\n     F  = {x}\n     F4 = {y}")

# ---------- 24 参数 ----------
print("\n\n#### 24 参数逐字段")
pa = ja.get("parameters", ja)
for key in ["parameters"]:
    A = ja.get(key, [])
    B = jb.get(key, [])
    print(f"容器 '{key}': F n={len(A)}  F4 n={len(B)}")
    da = {p["id"]: p for p in A}
    db_ = {p["id"]: p for p in B}
    print("  ID 集合相等:", set(da) == set(db_))
    only_a = sorted(set(da) - set(db_)); only_b = sorted(set(db_) - set(da))
    print("  仅 F 有:", only_a, " 仅 F4 有:", only_b)
    ndiff = 0
    for pid in sorted(set(da) & set(db_)):
        dd = deepdiff(da[pid], db_[pid], "")
        if dd:
            ndiff += 1
            print(f"  [{pid}] 差异:")
            for p, x, y in dd:
                print(f"      {p}: F={x} F4={y}")
    print("  有差异的参数条数 =", ndiff)
    pend_a = sum(1 for p in A if p.get("approval_status") == "PENDING_APPROVAL")
    pend_b = sum(1 for p in B if p.get("approval_status") == "PENDING_APPROVAL")
    print(f"  PENDING_APPROVAL: F {pend_a}/{len(A)}   F4 {pend_b}/{len(B)}")
    nonpend = [(p["id"], p.get("approval_status")) for p in B if p.get("approval_status") != "PENDING_APPROVAL"]
    print("  F4 非 PENDING 项:", nonpend)

print("\n#### 各容器 ID 集合规模")
for k, v in jb.items():
    if isinstance(v, list):
        print(f"  {k:28s} list n={len(v)}")
    elif isinstance(v, dict):
        print(f"  {k:28s} dict n={len(v)}")