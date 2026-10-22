#!/usr/bin/env python3
# 只读检查脚本 13：我的探针复刻 stdout vs 入库 probe_*_stdout.txt 逐字节
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
EV6 = ISO + r"\blobs\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"
MINE = ISO + r"\runs\probe"
names = ["baseline_no_injection", "m5_window_advance_removed", "empty_predicates_used",
         "b13_predicates_used_added", "undeclared_predicate_name",
         "suppressed_release_not_window_advancing", "case_timeout_frame_action",
         "case_span_wrong", "historical_model_check"]
same = diff = 0
for n in names:
    lib = os.path.join(EV6, f"probe_{n}_stdout.txt")
    mine = os.path.join(MINE, f"{n}_stdout.txt")
    a = open(lib, "rb").read() if os.path.exists(lib) else None
    b = open(mine, "rb").read() if os.path.exists(mine) else None
    eq = a == b
    same += eq
    diff += (not eq)
    print(f"{n}: 入库 {len(a) if a is not None else 'MISSING'}B | 我的 {len(b) if b is not None else 'MISSING'}B | 逐字节相同={eq}")
    if not eq and a and b:
        print("   入库:", a[:220])
        print("   我的:", b[:220])
print(f"相同 {same} / 不同 {diff}")

print()
print("=== 入库 probe_summary historical c7_detail ===")
import json
ps = json.load(open(EV6 + r"\probe_summary.json", encoding="utf-8"))
h = [r for r in ps["results"] if r["case_id"] == "historical_model_check"][0]
print(json.dumps(h, ensure_ascii=False, indent=1)[:1200])
print()
print("=== 入库 probe_summary 各例 verdict/injection ===")
for r in ps["results"]:
    print(f"  {r['case_id']:<42} exit={r['actual_exit']} verdict={r['verdict']} check={r['expected_check']}")
print()
print("=== 入库 selfcheck_c11_stdout.txt ===")
print(open(EV6 + r"\selfcheck_c11_stdout.txt", encoding="utf-8").read()[:600])