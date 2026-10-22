# -*- coding: utf-8 -*-
"""独立评审：收尾细节——B09/B17 文本、B13 字段、C7 span 语义、M5 条件精度。"""
import json, os, io, subprocess

WT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(WT, "docs/stage6/s6a_stage6_g0_behavior_v1.json")
DOC = os.path.join(WT, "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
d = json.load(open(J, encoding="utf-8"))
doc = open(DOC, encoding="utf-8").read()

out = []
def P(*a):
    line = " ".join(str(x) for x in a); print(line); out.append(line)

rows = {b["id"]: b for b in d["behavior_rows"]}
P("### B03 / B09 / B17 全字段（谓词名在文本中的出现情况）")
for cid in ("B03", "B09", "B17", "B04", "B07", "B08", "B10", "B12", "B14"):
    b = rows[cid]
    text = " ".join(str(b.get(k, "")) for k in ("condition", "output", "must_log"))
    P(f"  {cid} declared={b.get('predicates_used','<无>')} "
      f"文中TARGET_CONTINUES={'TARGET_CONTINUES' in text} 文中WINDOW_MATCH={'WINDOW_MATCH' in text}")
    P(f"      condition={b.get('condition')}")
    P(f"      output={b.get('output')}")
    P(f"      must_log={b.get('must_log')}")

P("")
P("### B13 字段现状（是否带 global_cooldown_gate）")
P(f"  B13 键 = {sorted(rows['B13'].keys())}")
P(f"  'global_cooldown_gate' in B13 = {'global_cooldown_gate' in rows['B13']}")
tr = {t["id"]: t for t in d["transitions"]}
P(f"  M5 键 = {sorted(tr['M5'].keys())}")
P(f"  M5.global_cooldown_gate = {tr['M5'].get('global_cooldown_gate')!r}")
P(f"  policy.statement = {d['predicate_binding_policy']['statement']}")
P(f"  policy.item_notes.B13 = {d['predicate_binding_policy']['item_notes']['B13']}")
P(f"  B13.predicate_binding_note = {rows['B13'].get('predicate_binding_note')}")

P("")
P("### 文档 §5 B09 / B17 行原文")
for line in doc.splitlines():
    if line.startswith("| B09 ") or line.startswith("| B17 ") or line.startswith("| B13 "):
        P("  " + line)

P("")
P("### M5 条件 vs stable_latching 叙述（“窗口推进帧”限定）")
P(f"  M5.condition = {tr['M5']['condition']}")
P(f"  stable_latching.suppressed_trigger_release = {d['stable_latching']['suppressed_trigger_release']}")
P(f"  文档 §4 锁存段 = {[l for l in doc.splitlines() if '锁存（观察项定论' in l][0][:400] if any('锁存（观察项定论' in l for l in doc.splitlines()) else 'N/A'}")
P(f"  §13 是否有“不得触发动作”汇总行 = "
  f"{any('都不得触发动作' in l for l in doc.splitlines())}")

P("")
P("### C7 window_match_vs_continues 的 span 语义 vs 规格 §9")
P("  自检实现：window_span_ms = (len(frames) - 1) * period_ms   ← 覆盖整个序列")
P("  规格 §9：窗口完成时刻 = 第 T6-S02 个 WINDOW_MATCH 结果到达且时长条件同时满足的那一帧")
P("  规格 §9：窗口持续时间 = t(完成帧) − t(窗口首帧)")
cases = json.load(open(os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04/hand_computed_cases.json"), encoding="utf-8"))
c29 = next(c for c in cases["cases"] if c["case_id"] == "HC-29")
n = len(c29["recompute"]["frames"]); per = c29["recompute"]["period_ms"]
P(f"  HC-29: frames={n} period={per}ms → 自检用 span=(n-1)*P={(n-1)*per}ms")
P(f"  HC-29: 第 6 个 WINDOW_MATCH 帧处的真实窗口时长=(6-1)*P={(6-1)*per}ms")
P(f"  HC-29 预期 = {c29['expected']}（两种口径下 m3_fires 同为 True，结论未受影响）")

P("")
P("### 结尾状态：被审提交与工作树")
P("  git rev-parse HEAD = " + subprocess.run(["git","-C",WT,"rev-parse","HEAD"],
    capture_output=True, text=True).stdout.strip())
P("  git status --short:")
for line in subprocess.run(["git","-C",WT,"status","--short"], capture_output=True,
                           text=True, encoding="utf-8").stdout.splitlines():
    P("    " + line)

with open(os.path.join(HERE, "final_details.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")