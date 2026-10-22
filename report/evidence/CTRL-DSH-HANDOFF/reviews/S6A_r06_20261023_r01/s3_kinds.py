#!/usr/bin/env python3
# 只读检查脚本 3：列出全部样例的 recompute.kind 与关键输入；打印低 FPS 类样例全文
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01\blobs"
p = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06\hand_computed_cases.json"
d = json.load(open(p, encoding="utf-8"))
cases = d["cases"]
print("=== 样例 kind 一览 ===")
for c in cases:
    spec = c.get("recompute") or {}
    extra = {k: v for k, v in spec.items()
             if k in ("period_ms", "period_ns", "s01_ms", "s02_frames", "fps", "p02",
                      "t_total_ms", "frames_total")}
    print(f"{c['case_id']} | {spec.get('kind')} | {json.dumps(extra, ensure_ascii=False)}")
print()
print("=== HC-01..HC-06 全文 ===")
for c in cases:
    if c["case_id"] in [f"HC-0{i}" for i in range(1, 7)]:
        print("=" * 70)
        print(json.dumps(c, ensure_ascii=False, indent=1))
print()
print("=== derivation_note / hand_cases_version ===")
print(d.get("hand_cases_version"))
print(d.get("derivation_note"))
print(d.get("parameter_assumptions_unfrozen"))