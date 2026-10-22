#!/usr/bin/env python3
# 只读检查脚本 12：样例逐例差异（r05→r06）/ builder 常量 / limitations / coverage
import json, os, subprocess, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
B = ISO + r"\blobs"
EV6 = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"
EV5 = B + r"\r05\report\evidence\S6-A\s6a_g0_20261022_r05"

c5 = json.load(open(EV5 + r"\hand_computed_cases.json", encoding="utf-8"))
c6 = json.load(open(EV6 + r"\hand_computed_cases.json", encoding="utf-8"))
i5 = {c["case_id"]: c for c in c5["cases"]}
i6 = {c["case_id"]: c for c in c6["cases"]}
print("=== 样例 ID 集合 ===")
print("r05:", len(i5), "r06:", len(i6), "| 新增:", sorted(set(i6) - set(i5)), "| 删除:", sorted(set(i5) - set(i6)))
print()
print("=== 逐例差异 ===")
for cid in sorted(set(i5) | set(i6)):
    a, b = i5.get(cid), i6.get(cid)
    if a == b:
        continue
    if a is None or b is None:
        print(cid, "新增" if a is None else "删除")
        continue
    ek = (sorted(set((a.get("expected") or {})) ^ set((b.get("expected") or {}))),
          sorted(k for k in set(a.get("expected") or {}) & set(b.get("expected") or {})
                 if a["expected"][k] != b["expected"][k]))
    rk = (sorted(set(a.get("recompute") or {}) ^ set(b.get("recompute") or {})),)
    print(f"{cid}: expected 键增删={ek[0]} 值变={ek[1]} | recompute 键增删={rk[0]}")
    print(f"   主题变: {a.get('topic') != b.get('topic')} | 推导变: {a.get('derivation') != b.get('derivation')}")
print()
print("hand_cases_version:", c5.get("hand_cases_version"), "->", c6.get("hand_cases_version"))
print("parameter_assumptions_unfrozen 相同:", c5.get("parameter_assumptions_unfrozen") == c6.get("parameter_assumptions_unfrozen"))
print()
print("=== builder 中可能残留的旧常量 ===")
bld = open(B + r"\r06_verification_s6a_build_evidence.py", encoding="utf-8").read()
for pat in ("source_commit 为修订基线", "8 个注入", "C7 捕获 N-r04-04", "v1.4", "r05 的表述", "b20b670"):
    for m in re.finditer(re.escape(pat), bld):
        s = max(0, m.start() - 120)
        print(f"  [{pat}] ...{bld[s:m.end()+120].strip()}...")
        break
print()
print("=== manifest.limitations[0] 与 source_commit ===")
m6 = json.load(open(EV6 + r"\delivery_manifest.json", encoding="utf-8"))
m5 = json.load(open(EV5 + r"\delivery_manifest.json", encoding="utf-8"))
print("r06 source_commit:", m6["source_commit"])
print("r06 limitations[0]:", m6["limitations"][0])
print("r05 source_commit:", m5["source_commit"])
print("r05 limitations[0]:", m5["limitations"][0])
print()
print("=== limitations_not_executed.json（r06）===")
lim = json.load(open(EV6 + r"\limitations_not_executed.json", encoding="utf-8"))
print(json.dumps(lim, ensure_ascii=False, indent=1)[:4000])
print()
print("=== coverage_matrix.json（r06）非 items 部分 ===")
cov = json.load(open(EV6 + r"\coverage_matrix.json", encoding="utf-8"))
print(json.dumps({k: v for k, v in cov.items() if k != "items"}, ensure_ascii=False, indent=1)[:2500])
print("items 条数:", len(cov.get("items", [])))