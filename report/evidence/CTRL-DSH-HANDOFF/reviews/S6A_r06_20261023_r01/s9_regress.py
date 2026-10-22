#!/usr/bin/env python3
# 只读检查脚本 9：r05 vs r06 无回归比对（参数/ID/键/版本）+ 声明纪律 + 漂移
import json, os, hashlib, subprocess, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
B = ISO + r"\blobs"
ROOT = r"D:\codex-worktrees\w6"
EV6 = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"
EV5 = B + r"\r05\report\evidence\S6-A\s6a_g0_20261022_r05"

j5 = json.load(open(B + r"\r05_docs_stage6_s6a_stage6_g0_behavior_v1.json", encoding="utf-8"))
j6 = json.load(open(B + r"\r06_docs_stage6_s6a_stage6_g0_behavior_v1.json", encoding="utf-8"))
print("=== 1. 参数（24 项）逐字段 ===")
p5 = {x["id"]: x for x in j5["parameters"]}
p6 = {x["id"]: x for x in j6["parameters"]}
print("数量:", len(p5), "->", len(p6), "| 集合相同:", set(p5) == set(p6))
diff = 0
for pid in sorted(set(p5) | set(p6)):
    a, b = p5.get(pid), p6.get(pid)
    if a != b:
        diff += 1
        ka = set(a or {}) ^ set(b or {})
        print("  DIFF", pid, "字段差异:", sorted(ka))
        for k in sorted(set(a or {}) & set(b or {})):
            if a[k] != b[k]:
                print(f"    {k}: {a[k]!r} -> {b[k]!r}")
print("参数逐字段差异数:", diff)
pend5 = [x["id"] for x in j5["parameters"] if x["approval_status"] != "PENDING_APPROVAL"]
pend6 = [x["id"] for x in j6["parameters"] if x["approval_status"] != "PENDING_APPROVAL"]
print("非 PENDING_APPROVAL: r05 =", pend5, "| r06 =", pend6)
print()
print("=== 2. ID 集合 ===")
for blk in ("transitions", "hard_invariants", "behavior_rows", "open_decisions", "parameters"):
    a = [x["id"] for x in j5[blk]]
    b = [x["id"] for x in j6[blk]]
    print(f"{blk}: {len(a)} -> {len(b)} | 新增={sorted(set(b)-set(a))} 删除={sorted(set(a)-set(b))}")
print("states:", len(j5["states"]), "->", len(j6["states"]), "| 新增=", sorted(set(j6["states"])-set(j5["states"])))
print()
print("=== 3. 顶层键 ===")
print("新增:", sorted(set(j6) - set(j5)), "| 删除:", sorted(set(j5) - set(j6)))
print()
print("=== 4. JSON 全量键路径差异（含新增/删除/改值）===")


def paths(o, pre=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(paths(v, f"{pre}.{k}"))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(paths(v, f"{pre}[{i}]"))
    else:
        out[pre] = o
    return out


a, b = paths(j5), paths(j6)
added = sorted(set(b) - set(a))
removed = sorted(set(a) - set(b))
changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
print(f"新增键 {len(added)} / 删除键 {len(removed)} / 改值键 {len(changed)}")
for k in added:
    print("  +", k, "=", repr(b[k])[:120])
for k in removed:
    print("  -", k, "=", repr(a[k])[:120])
print("  -- 改值（排除纯索引位移）--")
for k in changed:
    if any(k.endswith(s) for s in ("run_id", "supersedes_run_id", "artifact_version", "review_source",
                                   "review_verdict", "retained_from_r05", "retained_from_r04")):
        pass
    print("  ~", k, ":", repr(a[k])[:90], "->", repr(b[k])[:90])
print()
print("=== 5. artifact_version 一致性 ===")
tokens = {}
tokens["JSON artifact_version"] = j6["artifact_version"]
tokens["JSON revision.retained_from_r05.artifact_version"] = j6["revision"]["retained_from_r05"]["artifact_version"]
doc6 = open(B + r"\r06_docs_stage6_S6A_stage6_g0_behavior_spec_v1.md", encoding="utf-8").read()
tokens["doc 出现 v1.5 次数"] = doc6.count("v1.5")
tokens["doc 出现 v1.4 次数"] = doc6.count("v1.4")
tokens["doc 含 S6A-G0-v1.5 完整令牌"] = "S6A-G0-v1.5" in doc6
state6 = open(B + r"\r06_.codex_STATE.md", encoding="utf-8").read()
tokens["STATE 出现 v1.5 次数"] = state6.count("v1.5")
tokens["STATE 含 r06"] = "r06" in state6
for f in sorted(os.listdir(EV6)):
    if f.endswith((".json", ".md", ".txt")):
        t = open(os.path.join(EV6, f), encoding="utf-8", errors="replace").read()
        if "v1.5" in t:
            tokens[f"evidence:{f}"] = t.count("v1.5")
for k, v in tokens.items():
    print(f"  {k}: {v}")
print()
print("=== 6. 声明但缺失 / 未声明但存在 ===")
man = json.load(open(EV6 + r"\delivery_manifest.json", encoding="utf-8"))
print("manifest.evidence_dir =", man.get("evidence_dir"))
actual = sorted(os.path.relpath(os.path.join(dp, f), EV6).replace("\\", "/")
                for dp, _, fs in os.walk(EV6) for f in fs)
decl_run = set()
ext = []
for item in man["files"]:
    p = item["path"].replace("\\", "/")
    pre = "report/evidence/S6-A/s6a_g0_20261022_r06/"
    if p.startswith(pre):
        decl_run.add(p[len(pre):])
    else:
        ext.append(p)
print("运行目录实际文件:", len(actual), "| manifest 运行目录条目:", len(decl_run), "| 外部绑定:", len(ext))
print("声明但缺失:", sorted(decl_run - set(actual)))
print("存在但未声明:", sorted(set(actual) - decl_run))
print("外部绑定:", ext)
miss = [p for p in ext if not os.path.isfile(os.path.join(ROOT, p.replace("/", "\\")))]
print("外部绑定缺失:", miss)
print()
print("=== 7. 文档 §18 点名文件存在性 ===")
names = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_.\-]*\.(?:json|md|txt))`", doc6))
missing = sorted(n for n in names if not os.path.isfile(os.path.join(EV6, n)))
print("§18 点名文件名:", len(names), "| 证据目录缺失:", missing)
print()
print("=== 8. 自称『已审查/已通过』扫描（r06 证据 + 文档 + STATE）===")
PAT = re.compile(r"已审查|已通过|审查通过|G0 通过|G0 已通过|验收通过|冻结(?!前)")
for label, text in (("doc", doc6), ("STATE", state6)):
    for m in PAT.finditer(text):
        s = max(0, m.start() - 70)
        print(f"  [{label}] ...{text[s:m.end()+70].strip()}...")
for f in sorted(os.listdir(EV6)):
    if not f.endswith((".json", ".md", ".txt")):
        continue
    t = open(os.path.join(EV6, f), encoding="utf-8", errors="replace").read()
    for m in PAT.finditer(t):
        s = max(0, m.start() - 70)
        print(f"  [{f}] ...{t[s:m.end()+70].strip()}...")