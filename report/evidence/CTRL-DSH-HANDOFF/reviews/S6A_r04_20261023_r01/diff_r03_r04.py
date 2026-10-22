# -*- coding: utf-8 -*-
"""独立评审：r03(2ce290f) 与 r04(b20b670) 的参数/ID 集合逐字段差异。

用 git cat-file blob 二进制提取被审提交的字节（不经文本转换）。
"""
import json, subprocess, os, io

WT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
JREL = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOCREL = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"

def blob(rev, rel):
    p = subprocess.run(["git", "-C", WT, "cat-file", "blob", f"{rev}:{rel}"],
                       capture_output=True)
    assert p.returncode == 0, p.stderr
    return p.stdout

r03 = json.loads(blob("2ce290f", JREL).decode("utf-8"))
r04 = json.loads(blob("b20b670", JREL).decode("utf-8"))

w = io.StringIO()
def P(*a): w.write(" ".join(str(x) for x in a) + "\n")

P("### 参数逐字段比较（id, kind, unit, comparison, draft_value, approval_status, approval_owner）")
p3 = {p["id"]: p for p in r03["parameters"]}
p4 = {p["id"]: p for p in r04["parameters"]}
P(f"  r03 参数数={len(p3)}  r04 参数数={len(p4)}")
P(f"  ID 集合相同 = {set(p3) == set(p4)}；仅 r03 有 = {sorted(set(p3)-set(p4))}；仅 r04 有 = {sorted(set(p4)-set(p3))}")
fields = ["kind", "name_zh", "unit", "comparison", "draft_value", "draft_source",
          "approval_status", "approval_owner"]
diff = 0
for k in sorted(set(p3) & set(p4)):
    for f in fields:
        if p3[k].get(f) != p4[k].get(f):
            diff += 1
            P(f"  [差异] {k}.{f}: r03={p3[k].get(f)!r} -> r04={p4[k].get(f)!r}")
P(f"  逐字段差异总数 = {diff}")

P("")
P("### PENDING_APPROVAL 纪律")
for tag, dd in (("r03", r03), ("r04", r04)):
    badv = [p["id"] for p in dd["parameters"] if p.get("approval_status") != "PENDING_APPROVAL"]
    P(f"  {tag}: 非 PENDING_APPROVAL 的参数 = {badv}")

P("")
P("### ID 集合全等性（除声明新增）")
def ids(dd):
    return {
        "parameters": {x["id"] for x in dd["parameters"]},
        "transitions": {x["id"] for x in dd["transitions"]},
        "hard_invariants": {x["id"] for x in dd["hard_invariants"]},
        "behavior_rows": {x["id"] for x in dd["behavior_rows"]},
        "states": set(dd["states"]),
        "open_decisions": {x["id"] for x in dd["open_decisions"]},
        "event_classes_keys": set(dd["event_classes"].keys()),
        "actions_keys": set(dd["actions"].keys()),
        "top_keys": set(dd.keys()),
    }
i3, i4 = ids(r03), ids(r04)
for group in i3:
    only3 = sorted(i3[group] - i4[group])
    only4 = sorted(i4[group] - i3[group])
    flag = "全等" if not only3 and not only4 else "有差异"
    P(f"  {group}: {flag} | 仅r03={only3} | 仅r04={only4}")

P("")
P("### 行为行 / 迁移 条数与内容级 ID 顺序")
P(f"  behavior_rows r03={len(r03['behavior_rows'])} r04={len(r04['behavior_rows'])} 顺序相同 = "
  f"{[x['id'] for x in r03['behavior_rows']] == [x['id'] for x in r04['behavior_rows']]}")
P(f"  transitions   r03={len(r03['transitions'])} r04={len(r04['transitions'])} 顺序相同 = "
  f"{[x['id'] for x in r03['transitions']] == [x['id'] for x in r04['transitions']]}")
P(f"  states r03={r03['states']}")
P(f"  states r04={r04['states']}")

P("")
P("### 新增块（r04 声明新增）")
for k in ("stable_latching", "time_anchors", "predicate_binding_policy"):
    P(f"  {k}: 在 r03 存在={k in r03}  在 r04 存在={k in r04}")
P(f"  U6-16 在 r03={any(x['id']=='U6-16' for x in r03['open_decisions'])} "
  f"在 r04={any(x['id']=='U6-16' for x in r04['open_decisions'])}")

P("")
P("### 版本/身份字段")
for f in ("artifact_version", "run_id", "status", "supersedes_run_id", "schema_version"):
    P(f"  {f}: r03={r03.get(f)!r} -> r04={r04.get(f)!r}")

P("")
P("### 文档身份行")
d3 = blob("2ce290f", DOCREL).decode("utf-8")
d4 = blob("b20b670", DOCREL).decode("utf-8")
P(f"  r03 文档行数={len(d3.splitlines())} r04 文档行数={len(d4.splitlines())}")
for tok in ("matched_frames", "t_last_match", "t_submit+"):
    P(f"  '{tok}': r03 出现 {d3.count(tok)} 次 -> r04 出现 {d4.count(tok)} 次")
for tok in ("TARGET_CONTINUES", "WINDOW_MATCH", "t_last_target_continues"):
    P(f"  '{tok}': r03 {d3.count(tok)} -> r04 {d4.count(tok)}")

open(os.path.join(HERE, "r03_vs_r04.txt"), "w", encoding="utf-8").write(w.getvalue())
print("wrote r03_vs_r04.txt", len(w.getvalue()))