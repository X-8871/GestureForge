#!/usr/bin/env python3
"""r06 → r07 无回归/无夸大 逐字段核对（只用 git 提交字节，免疫工作树漂移）。"""
import hashlib
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
W6 = r"D:\codex-worktrees\w6"
BASE = "04ea58e1"
HEAD = "bdcf896"
EV07 = "report/evidence/S6-A/s6a_g0_20261022_r07"
JSONP = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOCP = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"


def blob(rev, path):
    r = subprocess.run(["git", "-C", W6, "cat-file", "blob", f"{rev}:{path}"],
                       capture_output=True, check=False)
    if r.returncode != 0:
        return None
    return r.stdout


def jload(rev, path):
    raw = blob(rev, path)
    return json.loads(raw.decode("utf-8"))


print("=" * 30, "1) 24 项参数逐字段 r06 vs r07")
a = jload(BASE, JSONP)
b = jload(HEAD, JSONP)
pa = {p["id"]: p for p in a["parameters"]}
pb = {p["id"]: p for p in b["parameters"]}
print("参数个数 r06/r07:", len(pa), len(pb), "| ID 集合差:",
      sorted(set(pb) - set(pa)), sorted(set(pa) - set(pb)))
fields = sorted({k for p in list(pa.values()) + list(pb.values()) for k in p})
diff = 0
for pid in sorted(pa):
    for f in fields:
        if pa[pid].get(f) != pb[pid].get(f):
            diff += 1
            print("  DIFF", pid, f, repr(pa[pid].get(f)), "->", repr(pb[pid].get(f)))
print("字段差异数:", diff)
print("非 PENDING_APPROVAL 参数 r07:",
      [p["id"] for p in pb.values() if p.get("approval_status") != "PENDING_APPROVAL"])

print("=" * 30, "2) ID 集合")
for key in ("transitions", "hard_invariants", "behavior_rows", "open_decisions", "parameters"):
    sa = {i["id"] for i in a[key]}
    sb = {i["id"] for i in b[key]}
    print(f"  {key}: {len(sa)}->{len(sb)} 新增={sorted(sb-sa)} 删除={sorted(sa-sb)}")
print("  states:", a["states"], "->", b["states"])
print("  reachability.transitions:", sorted(a["reachability"]["transitions"]),
      "->", sorted(b["reachability"]["transitions"]))

print("=" * 30, "3) 顶层键增删")
ka, kb = set(a), set(b)
print("  新增:", sorted(kb - ka), "删除:", sorted(ka - kb))
print("  sub-keys of reachability.M4:", sorted(a["reachability"]["transitions"]["M4"]),
      "->", sorted(b["reachability"]["transitions"]["M4"]))
print("  sub-keys of U6-12:", sorted(next(i for i in a["open_decisions"] if i["id"] == "U6-12")),
      "->", sorted(next(i for i in b["open_decisions"] if i["id"] == "U6-12")))

print("=" * 30, "4) 样例集与 expected 键值差异")
ca = jload(BASE, "report/evidence/S6-A/s6a_g0_20261022_r06/hand_computed_cases.json")
cb = jload(HEAD, f"{EV07}/hand_computed_cases.json")
ida = {c["case_id"]: c for c in ca["cases"]}
idb = {c["case_id"]: c for c in cb["cases"]}
print("  版本:", ca.get("hand_cases_version"), "->", cb.get("hand_cases_version"))
print("  样例数:", len(ida), "->", len(idb), "新增:", sorted(set(idb) - set(ida)),
      "删除:", sorted(set(ida) - set(idb)))
for cid in sorted(set(ida) & set(idb)):
    ea, eb = ida[cid].get("expected", {}), idb[cid].get("expected", {})
    added = sorted(set(eb) - set(ea))
    removed = sorted(set(ea) - set(eb))
    changed = [k for k in set(ea) & set(eb) if ea[k] != eb[k]]
    if added or removed or changed:
        print(f"  {cid}: +{added} -{removed} 值变={[(k, ea[k], eb[k]) for k in changed]}")

print("=" * 30, "5) r06→r07 文件差异（name-status）")
print(subprocess.run(["git", "-C", W6, "diff", "--name-status", BASE, HEAD],
                     capture_output=True, text=True).stdout)
print(subprocess.run(["git", "-C", W6, "diff", "--name-status", "43f7995", HEAD,
                      "--", "report/evidence/S6-A", "docs/stage6", "verification", "src"],
                     capture_output=True, text=True).stdout)

print("=" * 30, "6) 清单双向核对（提交内）")
man = jload(HEAD, f"{EV07}/delivery_manifest.json")
files = man["files"]
actual = subprocess.run(["git", "-C", W6, "ls-tree", "-r", "--name-only", HEAD,
                         f"{EV07}/"], capture_output=True, text=True).stdout.split()
declared_run = [f["path"] for f in files if f["path"].startswith(EV07 + "/")]
extra = sorted(p for p in actual if p not in declared_run and not p.endswith("delivery_manifest.json"))
missing = sorted(p for p in declared_run if p not in actual)
print("  运行目录实际文件:", len(actual), "清单声明:", len(declared_run))
print("  声明但缺失:", missing)
print("  存在但未声明（manifest 自身不计）:", extra)
shakey = 0
for f in files:
    raw = blob(HEAD, f["path"])
    if raw is None:
        print("  !! 声明文件在提交内不存在:", f["path"])
        continue
    for cand in (raw, raw.replace(b"\r\n", b"\n"), raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")):
        if hashlib.sha256(cand).hexdigest() == f["sha256"]:
            break
    else:
        shakey += 1
        print("  !! 换行归一后仍不匹配声明哈希:", f["path"])
print("  哈希不符（含换行归一）:", shakey)

print("=" * 30, "7) hashes_sha256.txt 解析核对")
ht = blob(HEAD, f"{EV07}/hashes_sha256.txt").decode("utf-8")
lines = [ln for ln in ht.splitlines() if ln.strip()]
print("  条目数:", len(lines), "首行:", lines[0][:90])
bad = 0
for ln in lines:
    m = re.match(r"^([0-9a-f]{64})\s+\*?(.+)$", ln.strip())
    if not m:
        print("  !! 无法解析:", ln[:80])
        continue
    want, path = m.group(1), m.group(2).strip()
    raw = blob(HEAD, path)
    if raw is None:
        print("  !! 文件不存在:", path)
        bad += 1
        continue
    if hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() != want and \
       hashlib.sha256(raw).hexdigest() != want and \
       hashlib.sha256(raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest() != want:
        print("  !! 哈希不符:", path)
        bad += 1
print("  hashes_sha256.txt 不符:", bad)

print("=" * 30, "8) 版本令牌出现次数（r07 提交字节）")
paths = subprocess.run(["git", "-C", W6, "ls-tree", "-r", "--name-only", HEAD, EV07 + "/",
                        "docs/stage6/"], capture_output=True, text=True).stdout.split()
for token in ("S6A-G0-v1.6", "S6A-HC-v1.6"):
    hits = []
    for p in paths:
        raw = blob(HEAD, p)
        if raw and token.encode() in raw:
            hits.append(p)
    print(f"  {token}: {len(hits)} 个文件 -> {hits}")

print("=" * 30, "9) 自称已审查/已通过 扫描（r07 提交内的 S6-A 文件）")
CLAIMS = ["已审查", "已通过", "G0 已通过", "验收已通过", "已冻结数值", "已实测通过", "可以冻结"]
NEG = ("不宣称", "不构成", "不得", "禁止", "未", "不是", "并非", "不因", "不复评", "不代表")
for p in paths:
    raw = blob(HEAD, p)
    if raw is None:
        continue
    text = raw.decode("utf-8", "replace")
    for c in CLAIMS:
        start = 0
        while True:
            i = text.find(c, start)
            if i < 0:
                break
            ctx = text[max(0, i - 20):i]
            if not any(n in ctx for n in NEG):
                print(f"  !! {p}: …{ctx[-30:]}[{c}]…")
            start = i + len(c)
print("  扫描完成")