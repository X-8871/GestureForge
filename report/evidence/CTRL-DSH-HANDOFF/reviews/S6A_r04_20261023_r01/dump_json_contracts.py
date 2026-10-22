# -*- coding: utf-8 -*-
"""独立评审：转储被审 JSON 的关键契约片段到文本文件（只读）。"""
import json, os, io

ROOT = r"D:\codex-worktrees\w6"
J = os.path.join(ROOT, "docs", "stage6", "s6a_stage6_g0_behavior_v1.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json_dump.txt")

d = json.load(open(J, encoding="utf-8"))
w = io.StringIO()

def P(*a):
    w.write(" ".join(str(x) for x in a) + "\n")

P("=" * 30, "predicates", "=" * 30)
P(json.dumps(d["predicates"], ensure_ascii=False, indent=2))

P("=" * 30, "predicate_binding_policy", "=" * 30)
P(json.dumps(d["predicate_binding_policy"], ensure_ascii=False, indent=2))

P("=" * 30, "time_anchors", "=" * 30)
P(json.dumps(d["time_anchors"], ensure_ascii=False, indent=2))

P("=" * 30, "stable_latching", "=" * 30)
P(json.dumps(d["stable_latching"], ensure_ascii=False, indent=2))

P("=" * 30, "transitions", "=" * 30)
for t in d["transitions"]:
    P("-" * 60)
    P("id=", t["id"], "| from=", t["from"], "| to=", t["to"], "| priority=", t.get("priority"))
    P("  params=", t.get("params"))
    P("  predicates_used=", t.get("predicates_used", "<ABSENT>"))
    P("  condition=", t.get("condition"))

P("=" * 30, "behavior_rows", "=" * 30)
for b in d["behavior_rows"]:
    P("-" * 60)
    P("id=", b["id"], "|", b.get("title"))
    P("  params=", b.get("params"))
    P("  predicates_used=", b.get("predicates_used", "<ABSENT>"))
    P("  semantics_status=", b.get("semantics_status"))
    P("  condition=", b.get("condition"))

P("=" * 30, "parameters", "=" * 30)
for p in d["parameters"]:
    P(p["id"], "|", p.get("kind"), "|", p.get("unit"), "|", p.get("comparison"),
      "| draft=", p.get("draft_value"), "|", p.get("approval_status"))

P("=" * 30, "revision", "=" * 30)
P(json.dumps(d["revision"], ensure_ascii=False, indent=2))

P("=" * 30, "reachability", "=" * 30)
P(json.dumps(d["reachability"], ensure_ascii=False, indent=2))

P("=" * 30, "cooldown_policy", "=" * 30)
P(json.dumps(d["cooldown_policy"], ensure_ascii=False, indent=2))

P("=" * 30, "trigger_once_while_held", "=" * 30)
P(json.dumps(d["trigger_once_while_held"], ensure_ascii=False, indent=2))

P("=" * 30, "hard_invariants", "=" * 30)
for h in d["hard_invariants"]:
    P(h["id"], "::", h["rule"])

P("=" * 30, "parameter_notes", "=" * 30)
P(json.dumps(d["parameter_notes"], ensure_ascii=False, indent=2))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(w.getvalue())
print("wrote", OUT, len(w.getvalue()), "chars")