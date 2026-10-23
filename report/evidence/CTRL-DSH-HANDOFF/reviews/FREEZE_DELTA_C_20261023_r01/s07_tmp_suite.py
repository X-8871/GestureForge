import json, sys
p = r"D:\codex-worktrees\w6\tmp\6\tool_self_tests.json"
d = json.load(open(p, encoding="utf-8"))
print("verdict =", d["verdict"], " n =", len(d["cases"]))
for c in d["cases"]:
    print(f"  - {c['case_id']:40s} exit={str(c['exit_code']):>5s} {c['verdict']:12s} "
          f"{'SKIPPED' if c.get('skipped') else '':8s} {str(c.get('note'))[:110]}")
print("\nsample observable of one simulate case:")
for c in d["cases"]:
    if c["case_id"] == "empty_claim_list_must_fail":
        print(json.dumps(c, ensure_ascii=False, indent=2))