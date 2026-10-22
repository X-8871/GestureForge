#!/usr/bin/env python3
# 只读检查脚本 2：打印 r06 样例 HC-28..HC-31 全文 + 样例键集合
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01\blobs"
p = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06\hand_computed_cases.json"
d = json.load(open(p, encoding="utf-8"))
print("顶层键:", list(d.keys()))
cases = d["cases"]
print("样例总数:", len(cases))
print("样例 id:", [c["case_id"] for c in cases])
print()
for c in cases:
    if c["case_id"] in ("HC-28", "HC-29", "HC-30", "HC-31"):
        print("=" * 70)
        print(json.dumps(c, ensure_ascii=False, indent=1))
print()
print("=== 各样例 expected 键 ===")
for c in cases:
    print(c["case_id"], "|", c.get("kind"), "|", sorted((c.get("expected") or {}).keys()))