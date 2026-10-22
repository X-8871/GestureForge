"""Reviewer 侧独立核验：predicates.used_by <-> 每项 predicates_used 双向一致。"""
import json
import re
import sys

WORKTREE = r"D:\codex-worktrees\w6"
P = WORKTREE + r"\docs\stage6\s6a_stage6_g0_behavior_v1.json"

d = json.load(open(P, encoding="utf-8"))
preds = d["predicates"]
items = {}
for t in d["transitions"]:
    items[t["id"]] = ("transition", t)
for b in d["behavior_rows"]:
    items[b["id"]] = ("behavior_row", b)

# 从 used_by 文本抽取 ID（形如 "M3 ..." / "B09 ..." / "§12 ..."）
forward = {}
for name in ("TARGET_CONTINUES", "WINDOW_MATCH"):
    s = set()
    for entry in preds[name]["used_by"]:
        m = re.match(r"^\s*(M\d+|B\d{2})\b", str(entry))
        if m:
            s.add(m.group(1))
    forward[name] = s

reverse = {}
for iid, (kind, obj) in items.items():
    for name in obj.get("predicates_used") or []:
        reverse.setdefault(name, set()).add(iid)

print("== forward (used_by) ==")
for k, v in forward.items():
    print(f"{k}: {sorted(v)}")
print("== reverse (item.predicates_used) ==")
for k, v in reverse.items():
    print(f"{k}: {sorted(v)}")

bad = False
for name in ("TARGET_CONTINUES", "WINDOW_MATCH"):
    f = forward[name]
    r = reverse.get(name, set())
    only_f = sorted(f - r)
    only_r = sorted(r - f)
    print(f"\n[{name}] 仅 used_by 有: {only_f}")
    print(f"[{name}] 仅 predicates_used 有: {only_r}")
    if only_f or only_r:
        bad = True
        for iid in only_f:
            obj = items[iid][1]
            print(f"   -> {iid} 的 predicates_used={obj.get('predicates_used')} 但 used_by 未登记它")

print("\n双向一致:" , "NO" if bad else "YES")

# 逐项打印哪些条目条件文本里出现谓词名但未声明 predicates_used
print("\n== 条件/输出提及谓词名但 predicates_used 为空 ==")
for iid, (kind, obj) in items.items():
    text = str(obj.get("condition", "")) + " " + str(obj.get("output", ""))
    hit = [n for n in ("TARGET_CONTINUES", "WINDOW_MATCH") if n in text]
    declared = obj.get("predicates_used") or []
    if hit and sorted(set(hit)) != sorted(set(declared)):
        print(f"{iid} ({kind}) text提及={hit} declared={declared}")
