import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
W6 = Path(r"D:\codex-worktrees\w6")
doc = (W6 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8")
data = json.loads((W6 / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))
res = {"invariant_text_diff": [], "behavior_title_diff": [], "behavior_params_diff": [],
       "param_value_diff": [], "open_decision_diff": [], "doc_section3_events_diff": []}

# H 文本
sec2 = doc.split("## 2.")[1].split("## 3.")[0]
md_h = {}
for line in sec2.splitlines():
    m = re.match(r"- \*\*(H-\d+) [^*]+\*\*：(.+)$", line)
    if m:
        md_h[m.group(1)] = m.group(2).strip()
for h in data["hard_invariants"]:
    mt = md_h.get(h["id"])
    if mt is None:
        res["invariant_text_diff"].append({"id": h["id"], "issue": "MD 缺失"})
    elif re.sub(r"\s+", "", mt) != re.sub(r"\s+", "", h["rule"]):
        res["invariant_text_diff"].append({"id": h["id"], "md": mt, "json": h["rule"]})

# 行为表标题与参数（MD 行）
sec5 = doc.split("## 5.")[1].split("## 6.")[0]
md_b = {}
for line in sec5.splitlines():
    m = re.match(r"\| (B\d{2}) \| ([^|]+?) \|", line)
    if m:
        md_b[m.group(1)] = m.group(2).strip()
for b in data["behavior_rows"]:
    if md_b.get(b["id"]) != b["title"]:
        res["behavior_title_diff"].append({"id": b["id"], "md": md_b.get(b["id"]), "json": b["title"]})

# 参数值/单位/比较（MD §14 表）
sec14 = doc.split("## 14.")[1].split("## 15.")[0]
md_p = {}
for line in sec14.splitlines():
    m = re.match(r"\| `(T6-[A-Za-z0-9_]+)` \| [^|]+ \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", line)
    if m:
        md_p[m.group(1)] = {"unit": m.group(2).strip(), "comparison": m.group(3).strip(),
                            "draft_value": m.group(4).strip()}
for p in data["parameters"]:
    if p["id"] not in md_p:
        res["param_value_diff"].append({"id": p["id"], "issue": "MD §14 无此行"})
        continue
    mdv = md_p[p["id"]]["draft_value"]
    jv = p["draft_value"]
    # 只比较首个数/词，容忍“（草案）”“；样本…”等修饰
    def first_num(s):
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        return float(m.group(0)) if m else None
    if isinstance(jv, (int, float)) and first_num(mdv) != float(jv):
        res["param_value_diff"].append({"id": p["id"], "md": mdv, "json": jv})
    if p["id"] == "T6-A03" and not mdv.startswith("无草案值"):
        res["param_value_diff"].append({"id": "T6-A03", "md": mdv, "json": None})

# 未决项
sec16 = doc.split("## 16.")[1].split("## 17.")[0]
md_u = set(re.findall(r"\| (U6-\d{2}) \|", sec16))
json_u = {u["id"] for u in data["open_decisions"]}
res["open_decision_diff"] = {"md_only": sorted(md_u - json_u), "json_only": sorted(json_u - md_u)}

# 文档 §3 输入事件 vs JSON
sec3 = doc.split("## 3.")[1].split("## 4.")[0]
md_events = set(re.findall(r"`(E_[A-Z_]+)`", sec3))
json_events = set(data["event_classes"]["input_events"])
res["doc_section3_events_diff"] = {"doc_only": sorted(md_events - json_events),
                                   "json_only": sorted(json_events - md_events)}


def brief(x):
    if isinstance(x, dict):
        return {k: brief(v) for k, v in x.items()}
    return x

print(json.dumps(res, ensure_ascii=False, indent=2))
