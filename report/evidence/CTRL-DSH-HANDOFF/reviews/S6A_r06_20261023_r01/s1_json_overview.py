#!/usr/bin/env python3
# 只读检查脚本 1：JSON 结构 / time_anchors / M3 / 修订记录 / window_complete 上下文
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
B = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01\blobs"
p = B + r"\r06_docs_stage6_s6a_stage6_g0_behavior_v1.json"
raw = open(p, encoding="utf-8").read()
d = json.loads(raw)

print("TOPKEYS:", list(d.keys()))
print()
print("artifact_version:", d["artifact_version"], "| run_id:", d.get("run_id"))
print("status:", d.get("status"), "| review_status:", d.get("review_status"))
print()
print("=== revision ===")
print(json.dumps(d.get("revision"), ensure_ascii=False, indent=1))
print()
print("=== time_anchors ===")
print(json.dumps(d.get("time_anchors"), ensure_ascii=False, indent=1))
print()
print("=== transitions.M3 ===")
for t in d["transitions"]:
    if t.get("id") == "M3":
        print(json.dumps(t, ensure_ascii=False, indent=1))
print()
print("=== behavior_rows B07/B27 ===")
for r in d["behavior_rows"]:
    if r.get("id") in ("B07", "B27"):
        print(json.dumps(r, ensure_ascii=False, indent=1))
print()
print("=== window_complete 出现上下文（JSON 原文）===")
for m in re.finditer("window_complete", raw):
    s = max(0, m.start() - 420)
    print("CTX>>>", raw[s:m.start() + 260].replace("\n", " | "))
    print("---")